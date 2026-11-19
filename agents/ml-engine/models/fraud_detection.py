"""
Modèle de détection de fraude - TrustDevis
Utilise XGBoost avec features avancées
"""

import numpy as np
import pandas as pd
from typing import Dict, Tuple, Optional
import xgboost as xgb
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.metrics import (classification_report, roc_auc_score, precision_recall_curve,
                            f1_score, confusion_matrix, average_precision_score)
from imblearn.over_sampling import SMOTE
from imblearn.pipeline import Pipeline as ImbPipeline
import joblib
import json
from datetime import datetime
import shap


class FraudDetectionModel:
    """Modèle de détection d'anomalies sur les devis"""
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.model = None
        self.threshold = self.config.get('threshold', 0.7)
        self.feature_importance = None
        self.shap_explainer = None
        self.metrics = {}
        
    def build_model(self, use_smote: bool = True) -> ImbPipeline:
        """Construit le pipeline du modèle"""
        # XGBoost avec hyperparamètres optimisés
        xgb_clf = xgb.XGBClassifier(
            n_estimators=200,
            max_depth=6,
            learning_rate=0.1,
            subsample=0.8,
            colsample_bytree=0.8,
            scale_pos_weight=10,  # Poids pour classe déséquilibrée
            eval_metric='logloss',
            random_state=42,
            n_jobs=-1
        )
        
        if use_smote:
            # Pipeline avec SMOTE pour équilibrage
            pipeline = ImbPipeline([
                ('smote', SMOTE(random_state=42, k_neighbors=5)),
                ('classifier', xgb_clf)
            ])
        else:
            pipeline = xgb_clf
            
        return pipeline
    
    def train(self, X: pd.DataFrame, y: np.ndarray, 
              validation_split: float = 0.2) -> Dict:
        """Entraîne le modèle de détection de fraude"""
        
        # Split données
        X_train, X_val, y_train, y_val = train_test_split(
            X, y, test_size=validation_split, random_state=42, stratify=y
        )
        
        print(f"📊 Entraînement: {len(X_train)} échantillons")
        print(f"   Fraude: {y_train.sum()} ({y_train.mean()*100:.1f}%)")
        print(f"   Validation: {len(X_val)} échantillons")
        
        # Construire et entraîner
        self.model = self.build_model(use_smote=True)
        self.model.fit(X_train, y_train)
        
        # Prédictions
        y_pred_proba = self.model.predict_proba(X_val)[:, 1]
        
        # Trouver meilleur threshold
        precision, recall, thresholds = precision_recall_curve(y_val, y_pred_proba)
        f1_scores = 2 * (precision * recall) / (precision + recall + 1e-8)
        best_idx = np.argmax(f1_scores)
        self.threshold = thresholds[best_idx] if best_idx < len(thresholds) else 0.5
        
        y_pred = (y_pred_proba >= self.threshold).astype(int)
        
        # Métriques
        self.metrics = {
            'auc_roc': roc_auc_score(y_val, y_pred_proba),
            'average_precision': average_precision_score(y_val, y_pred_proba),
            'f1_score': f1_score(y_val, y_pred),
            'precision': precision[best_idx],
            'recall': recall[best_idx],
            'threshold': self.threshold,
            'confusion_matrix': confusion_matrix(y_val, y_pred).tolist(),
            'training_date': datetime.now().isoformat()
        }
        
        print(f"\n✅ Modèle entraîné!")
        print(f"   AUC-ROC: {self.metrics['auc_roc']:.3f}")
        print(f"   F1-Score: {self.metrics['f1_score']:.3f}")
        print(f"   Precision: {self.metrics['precision']:.3f}")
        print(f"   Recall: {self.metrics['recall']:.3f}")
        print(f"   Threshold optimal: {self.threshold:.3f}")
        
        # Feature importance
        if hasattr(self.model, 'named_steps'):
            classifier = self.model.named_steps['classifier']
        else:
            classifier = self.model
            
        self.feature_importance = dict(zip(
            X.columns,
            classifier.feature_importances_
        ))
        
        # SHAP explainer
        try:
            self.shap_explainer = shap.TreeExplainer(classifier)
        except:
            pass
        
        return self.metrics
    
    def predict(self, X: pd.DataFrame, return_proba: bool = True) -> Dict:
        """Prédit si un devis est suspect"""
        if self.model is None:
            raise ValueError("Modèle non entraîné")
        
        # Convertir en numpy array sans noms de colonnes
        X_array = X.values
        
        # Utiliser le classifier interne directement
        if hasattr(self.model, 'named_steps'):
            classifier = self.model.named_steps['classifier']
            proba = classifier.predict_proba(X_array)[:, 1]
        else:
            proba = self.model.predict_proba(X_array)[:, 1]
        prediction = (proba >= self.threshold).astype(int)
        
        # Calculer score de confiance (distance au threshold)
        confidence = 1 - np.abs(proba - self.threshold) / max(self.threshold, 1 - self.threshold)
        
        result = {
            'is_suspect': bool(prediction[0]) if len(prediction) == 1 else prediction.tolist(),
            'fraud_probability': float(proba[0]) if len(proba) == 1 else proba.tolist(),
            'confidence_score': float(confidence[0]) if len(confidence) == 1 else confidence.tolist(),
            'risk_level': self._get_risk_level(proba[0]) if len(proba) == 1 else [self._get_risk_level(p) for p in proba]
        }
        
        # SHAP values pour explicabilité
        if self.shap_explainer is not None and len(X) == 1:
            shap_values = self.shap_explainer.shap_values(X)
            result['explanation'] = self._explain_prediction(X, shap_values)
        
        return result
    
    def _get_risk_level(self, proba: float) -> str:
        """Détermine le niveau de risque"""
        if proba >= 0.8:
            return "HIGH"
        elif proba >= 0.6:
            return "MEDIUM"
        elif proba >= 0.4:
            return "ELEVATED"
        else:
            return "LOW"
    
    def _explain_prediction(self, X: pd.DataFrame, shap_values) -> Dict:
        """Génère une explication du résultat"""
        feature_names = X.columns.tolist()
        
        if isinstance(shap_values, list):
            shap_values = shap_values[1]  # Classe positive
        
        # Top features contribuant à la prédiction
        contributions = list(zip(feature_names, shap_values[0]))
        contributions.sort(key=lambda x: abs(x[1]), reverse=True)
        
        top_positive = [(f, float(v)) for f, v in contributions if v > 0][:3]
        top_negative = [(f, float(v)) for f, v in contributions if v < 0][:3]
        
        return {
            'top_risk_factors': top_positive,
            'top_mitigating_factors': top_negative
        }
    
    def cross_validate(self, X: pd.DataFrame, y: np.ndarray, cv: int = 5) -> Dict:
        """Validation croisée"""
        model = self.build_model(use_smote=True)
        
        cv_scores = cross_val_score(model, X, y, cv=StratifiedKFold(cv, shuffle=True, random_state=42),
                                    scoring='roc_auc')
        
        return {
            'cv_auc_mean': cv_scores.mean(),
            'cv_auc_std': cv_scores.std(),
            'cv_scores': cv_scores.tolist()
        }
    
    def save(self, path: str):
        """Sauvegarde le modèle"""
        # Désactiver la validation des feature names
        if hasattr(self.model, 'named_steps'):
            classifier = self.model.named_steps['classifier']
        else:
            classifier = self.model
        
        # XGBoost stocke les feature names mais on ne peut pas les supprimer
        # On va les ignorer lors de la prédiction
        
        model_data = {
            'model': self.model,
            'threshold': self.threshold,
            'metrics': self.metrics,
            'feature_importance': self.feature_importance,
            'config': self.config
        }
        joblib.dump(model_data, path)
        print(f"💾 Modèle sauvegardé: {path}")
    
    @classmethod
    def load(cls, path: str):
        """Charge le modèle"""
        model_data = joblib.load(path)
        
        instance = cls(model_data['config'])
        instance.model = model_data['model']
        instance.threshold = model_data['threshold']
        instance.metrics = model_data['metrics']
        instance.feature_importance = model_data['feature_importance']
        
        return instance