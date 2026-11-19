"""
Analyse prédictive marché - TrustDevis
Tendances, saisonnalité, alertes anomalies
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from scipy import stats
import joblib
import json


class MarketAnalytics:
    """Analyse prédictive du marché des travaux"""
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.trend_models = {}
        self.seasonality_patterns = {}
        self.baseline_stats = {}
        
    def analyze_seasonality(self, df: pd.DataFrame, 
                           date_col: str = 'date',
                           price_col: str = 'prix',
                           region_col: str = 'region') -> Dict:
        """Analyse la saisonnalité des travaux"""
        
        df = df.copy()
        df[date_col] = pd.to_datetime(df[date_col])
        df['mois'] = df[date_col].dt.month
        df['saison'] = df['mois'].map({
            12: 'hiver', 1: 'hiver', 2: 'hiver',
            3: 'printemps', 4: 'printemps', 5: 'printemps',
            6: 'ete', 7: 'ete', 8: 'ete',
            9: 'automne', 10: 'automne', 11: 'automne'
        })
        
        results = {}
        
        # Global
        global_seasonal = df.groupby('saison')[price_col].agg(['mean', 'median', 'count'])
        results['global'] = global_seasonal.to_dict()
        
        # Par région
        for region in df[region_col].unique():
            region_df = df[df[region_col] == region]
            seasonal = region_df.groupby('saison')[price_col].agg(['mean', 'median', 'count'])
            results[region] = seasonal.to_dict()
        
        # Par type de travaux
        if 'type_travaux' in df.columns:
            results['by_work_type'] = {}
            for work_type in df['type_travaux'].unique():
                work_df = df[df['type_travaux'] == work_type]
                seasonal = work_df.groupby('saison')[price_col].agg(['mean', 'median'])
                results['by_work_type'][work_type] = seasonal.to_dict()
        
        self.seasonality_patterns = results
        return results
    
    def forecast_trends(self, df: pd.DataFrame,
                       date_col: str = 'date',
                       price_col: str = 'prix',
                       region_col: str = 'region',
                       forecast_days: int = 90) -> Dict:
        """Prédit les tendances de prix"""
        
        df = df.copy()
        df[date_col] = pd.to_datetime(df[date_col])
        
        results = {}
        
        # Agréger par mois
        df['year_month'] = df[date_col].dt.to_period('M')
        
        for region in df[region_col].unique():
            region_df = df[df[region_col] == region]
            monthly = region_df.groupby('year_month')[price_col].mean().reset_index()
            monthly['year_month'] = monthly['year_month'].dt.to_timestamp()
            
            if len(monthly) < 6:
                continue
            
            # Créer features temporelles
            monthly['days'] = (monthly['year_month'] - monthly['year_month'].min()).dt.days
            monthly['month_num'] = monthly['year_month'].dt.month
            
            # Features polynomial pour capturer tendance
            X = monthly[['days']].values
            y = monthly[price_col].values
            
            # Régression linéaire simple
            model = LinearRegression()
            model.fit(X, y)
            
            # Forecast
            last_day = monthly['days'].max()
            future_days = np.arange(last_day + 30, last_day + forecast_days + 30, 30)
            future_prices = model.predict(future_days.reshape(-1, 1))
            
            # Intervalles de confiance
            residuals = y - model.predict(X)
            std_residuals = np.std(residuals)
            
            results[region] = {
                'current_avg_price': float(y[-1]),
                'trend_slope': float(model.coef_[0]),
                'trend_direction': 'up' if model.coef_[0] > 0.1 else 'down' if model.coef_[0] < -0.1 else 'stable',
                'forecast': [
                    {
                        'date': (monthly['year_month'].max() + timedelta(days=int(d - last_day))).strftime('%Y-%m'),
                        'predicted_price': float(p),
                        'lower_bound': float(p - 1.96 * std_residuals),
                        'upper_bound': float(p + 1.96 * std_residuals)
                    }
                    for d, p in zip(future_days, future_prices)
                ],
                'confidence_score': max(0, 1 - std_residuals / np.mean(y))
            }
            
            self.trend_models[region] = model
        
        return results
    
    def detect_anomalies(self, df: pd.DataFrame,
                        date_col: str = 'date',
                        price_col: str = 'prix',
                        region_col: str = 'region',
                        threshold: float = 2.5) -> List[Dict]:
        """Détecte les anomalies de marché"""
        
        df = df.copy()
        df[date_col] = pd.to_datetime(df[date_col])
        df['week'] = df[date_col].dt.to_period('W')
        
        anomalies = []
        
        for region in df[region_col].unique():
            region_df = df[df[region_col] == region]
            weekly = region_df.groupby('week')[price_col].agg(['mean', 'std', 'count']).reset_index()
            
            if len(weekly) < 4:
                continue
            
            # Calculer moyenne mobile et écart-type
            weekly['rolling_mean'] = weekly['mean'].rolling(window=4, min_periods=2).mean()
            weekly['rolling_std'] = weekly['mean'].rolling(window=4, min_periods=2).std()
            
            # Z-score
            weekly['z_score'] = (weekly['mean'] - weekly['rolling_mean']) / (weekly['rolling_std'] + 1e-8)
            
            # Détecter anomalies
            anomaly_mask = np.abs(weekly['z_score']) > threshold
            
            for _, row in weekly[anomaly_mask].iterrows():
                anomalies.append({
                    'region': region,
                    'week': str(row['week']),
                    'avg_price': float(row['mean']),
                    'expected_price': float(row['rolling_mean']),
                    'deviation_pct': float((row['mean'] - row['rolling_mean']) / row['rolling_mean'] * 100),
                    'severity': 'high' if abs(row['z_score']) > 3.5 else 'medium',
                    'type': 'spike' if row['z_score'] > 0 else 'drop'
                })
        
        # Trier par sévérité
        anomalies.sort(key=lambda x: abs(x['deviation_pct']), reverse=True)
        
        return anomalies[:20]  # Top 20 anomalies
    
    def calculate_market_indicators(self, df: pd.DataFrame,
                                    date_col: str = 'date',
                                    price_col: str = 'prix') -> Dict:
        """Calcule les indicateurs de marché"""
        
        df = df.copy()
        df[date_col] = pd.to_datetime(df[date_col])
        
        # Prix actuel vs historique
        current_month = df[df[date_col] >= df[date_col].max() - timedelta(days=30)]
        previous_month = df[
            (df[date_col] >= df[date_col].max() - timedelta(days=60)) &
            (df[date_col] < df[date_col].max() - timedelta(days=30))
        ]
        
        current_avg = current_month[price_col].mean()
        previous_avg = previous_month[price_col].mean() if len(previous_month) > 0 else current_avg
        
        indicators = {
            'current_avg_price': float(current_avg),
            'price_change_pct': float((current_avg - previous_avg) / previous_avg * 100) if previous_avg > 0 else 0,
            'price_volatility': float(df[price_col].std() / df[price_col].mean()),
            'market_activity': len(current_month),
            'price_range': {
                'p10': float(df[price_col].quantile(0.1)),
                'p25': float(df[price_col].quantile(0.25)),
                'p50': float(df[price_col].median()),
                'p75': float(df[price_col].quantile(0.75)),
                'p90': float(df[price_col].quantile(0.9))
            }
        }
        
        self.baseline_stats = indicators
        return indicators
    
    def generate_alerts(self, df: pd.DataFrame) -> List[Dict]:
        """Génère des alertes basées sur l'analyse"""
        
        alerts = []
        
        # Anomalies de prix
        anomalies = self.detect_anomalies(df)
        for anomaly in anomalies[:5]:
            alerts.append({
                'type': 'price_anomaly',
                'severity': anomaly['severity'],
                'message': f"Anomalie détectée en {anomaly['region']}: {anomaly['type']} de {abs(anomaly['deviation_pct']):.1f}%",
                'details': anomaly,
                'timestamp': datetime.now().isoformat()
            })
        
        # Tendances régionales
        trends = self.forecast_trends(df)
        for region, trend in trends.items():
            if trend['trend_direction'] == 'up' and trend['trend_slope'] > 1:
                alerts.append({
                    'type': 'rising_prices',
                    'severity': 'medium',
                    'message': f"Hausse des prix détectée en {region}: +{trend['trend_slope']:.2f}€/jour",
                    'region': region,
                    'timestamp': datetime.now().isoformat()
                })
        
        return alerts
    
    def get_insights(self, df: pd.DataFrame) -> Dict:
        """Génère des insights complets sur le marché"""
        
        return {
            'seasonality': self.analyze_seasonality(df),
            'trends': self.forecast_trends(df),
            'anomalies': self.detect_anomalies(df),
            'indicators': self.calculate_market_indicators(df),
            'alerts': self.generate_alerts(df),
            'generated_at': datetime.now().isoformat()
        }
    
    def save(self, path: str):
        """Sauvegarde l'analytics"""
        data = {
            'trend_models': self.trend_models,
            'seasonality_patterns': self.seasonality_patterns,
            'baseline_stats': self.baseline_stats,
            'config': self.config
        }
        joblib.dump(data, path)
        print(f"💾 Analytics sauvegardés: {path}")
    
    @classmethod
    def load(cls, path: str):
        """Charge l'analytics"""
        data = joblib.load(path)
        
        instance = cls(data['config'])
        instance.trend_models = data['trend_models']
        instance.seasonality_patterns = data['seasonality_patterns']
        instance.baseline_stats = data['baseline_stats']
        
        return instance