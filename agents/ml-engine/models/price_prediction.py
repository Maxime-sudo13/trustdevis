"""
Modèle de prédiction de prix - TrustDevis
Régression avec intervalles de confiance
"""

import numpy as np
import pandas as pd
from typing import Dict, Tuple, Optional
import xgboost as xgb
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import joblib
from datetime import datetime
from scipy import stats


class PricePredictionModel:
    """Modèle de prédiction de prix avec intervalles de confiance"""
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.model = None
        self.quantile_models = {}
        self.confidence_level = self.config.get('confidence_level', 0.95)
        self.metrics = {}
        self.residual_std = None
        
    def build_model(self, objective: str = 'reg:squarederror') -> xgb.XGBRegressor:
        """Construit le modèle de régression"""
        model = xgb.XGBRegressor(
            n_estimators=300,
            max_depth=8,
            learning_rate=0.05,
            subsample=0.8,
            colsample_bytree=0.8,
            objective=objective,
            random_state=42,
            n_jobs=-1
        )
        return model
    
    def train(self, X: pd.DataFrame, y: np.ndarray,
              validation_split: float = 0.2) -> Dict:
        """Entraîne le modèle de prédiction de prix"""
        
        # Log transform pour stabilité
        y_log = np.log1p(y)
        
        # Split
        X_train, X_val, y_train_log, y_val_log = train_test_split(
            X, y_log, test_size=validation_split, random_state=42
        )
        y_train = np.expm1(y_train_log)
        y_val = np.expm1(y_val_log)
        
        print(f"📊 Entraînement prix: {len(X_train)} échantillons")
        print(f"   Prix moyen: {y.mean():.0f}€")
        print(f"   Prix médian: {np.median(y):.0f}€")
        
        # Modèle principal (médiane)
        self.model = self.build_model('reg:squarederror')
        self.model.fit(X_train, y_train_log)
        
        # Prédictions validation
        y_pred_log = self.model.predict(X_val)
        y_pred = np.expm1(y_pred_log)
        
        # Calculer résidus pour intervalles
        residuals = y_val - y_pred
        self.residual_std = np.std(residuals)
        
        # Entraîner modèles quantiles pour intervalles
        print("   Entraînement modèles quantiles...")
        alphas = [0.05, 0.25, 0.75, 0.95]  # Pour intervalles 90% et 50%
        
        for alpha in alphas:
            # Utiliser reg:quantileerror avec paramètre quantile_alpha
            quantile_model = xgb.XGBRegressor(
                n_estimators=300,
                max_depth=8,
                learning_rate=0.05,
                subsample=0.8,
                colsample_bytree=0.8,
                objective='reg:quantileerror',
                quantile_alpha=alpha,
                random_state=42,
                n_jobs=-1
            )
            quantile_model.fit(X_train, y_train_log)
            self.quantile_models[alpha] = quantile_model
        
        # Métriques
        self.metrics = {
            'mae': mean_absolute_error(y_val, y_pred),
            'rmse': np.sqrt(mean_squared_error(y_val, y_pred)),
            'r2': r2_score(y_val, y_pred),
            'mape': np.mean(np.abs((y_val - y_pred) / y_val)) * 100,
            'residual_std': self.residual_std,
            'training_date': datetime.now().isoformat()
        }
        
        print(f"\n✅ Modèle prix entraîné!")
        print(f"   MAE: {self.metrics['mae']:.0f}€")
        print(f"   RMSE: {self.metrics['rmse']:.0f}€")
        print(f"   R²: {self.metrics['r2']:.3f}")
        print(f"   MAPE: {self.metrics['mape']:.1f}%")
        
        return self.metrics
    
    def predict(self, X: pd.DataFrame, 
                confidence: float = 0.95) -> Dict:
        """Prédit le prix avec intervalle de confiance"""
        if self.model is None:
            raise ValueError("Modèle non entraîné")
        
        # Convertir en numpy array
        X_array = X.values
        
        # Prédiction point
        pred_log = self.model.predict(X_array)
        prediction = np.expm1(pred_log)
        
        # Intervalles via modèles quantiles
        if confidence == 0.95:
            lower_alpha, upper_alpha = 0.025, 0.975
        elif confidence == 0.90:
            lower_alpha, upper_alpha = 0.05, 0.95
        elif confidence == 0.80:
            lower_alpha, upper_alpha = 0.10, 0.90
        else:
            lower_alpha, upper_alpha = 0.025, 0.975
        
        if lower_alpha in self.quantile_models and upper_alpha in self.quantile_models:
            lower_log = self.quantile_models[lower_alpha].predict(X_array)
            upper_log = self.quantile_models[upper_alpha].predict(X_array)
            lower = np.expm1(lower_log)
            upper = np.expm1(upper_log)
        else:
            # Fallback: utiliser résidus
            z_score = stats.norm.ppf((1 + confidence) / 2)
            margin = z_score * self.residual_std
            lower = prediction - margin
            upper = prediction + margin
        
        # Calculer fiabilité de la prédiction
        interval_width = (upper - lower) / prediction
        reliability = max(0, 1 - interval_width.mean())
        
        result = {
            'predicted_price': float(prediction[0]) if len(prediction) == 1 else prediction.tolist(),
            'confidence_interval': {
                'lower': float(lower[0]) if len(lower) == 1 else lower.tolist(),
                'upper': float(upper[0]) if len(upper) == 1 else upper.tolist(),
                'confidence_level': confidence
            },
            'reliability_score': float(reliability),
            'expected_range': f"{lower[0]:.0f}€ - {upper[0]:.0f}€" if len(prediction) == 1 else None
        }
        
        return result
    
    def get_price_range_by_region(self, X: pd.DataFrame, 
                                   regions: pd.Series) -> Dict:
        """Analyse des prix par région"""
        predictions = self.predict(X)['predicted_price']
        
        df_result = pd.DataFrame({
            'region': regions,
            'predicted_price': predictions if isinstance(predictions, list) else [predictions]
        })
        
        return df_result.groupby('region')['predicted_price'].agg(['mean', 'median', 'std']).to_dict()
    
    def cross_validate(self, X: pd.DataFrame, y: np.ndarray, cv: int = 5) -> Dict:
        """Validation croisée"""
        y_log = np.log1p(y)
        model = self.build_model()
        
        cv_scores = cross_val_score(model, X, y_log, cv=cv, scoring='neg_mean_absolute_error')
        
        return {
            'cv_mae_mean': -cv_scores.mean(),
            'cv_mae_std': cv_scores.std(),
            'cv_scores': (-cv_scores).tolist()
        }
    
    def save(self, path: str):
        """Sauvegarde le modèle"""
        # XGBoost stocke les feature names - on les ignore lors de la prédiction
        
        model_data = {
            'model': self.model,
            'quantile_models': self.quantile_models,
            'metrics': self.metrics,
            'residual_std': self.residual_std,
            'config': self.config
        }
        joblib.dump(model_data, path)
        print(f"💾 Modèle prix sauvegardé: {path}")
    
    @classmethod
    def load(cls, path: str):
        """Charge le modèle"""
        model_data = joblib.load(path)
        
        instance = cls(model_data['config'])
        instance.model = model_data['model']
        instance.quantile_models = model_data['quantile_models']
        instance.metrics = model_data['metrics']
        instance.residual_std = model_data['residual_std']
        
        return instance