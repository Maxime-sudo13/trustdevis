"""
Monitoring et métriques ML - TrustDevis
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List
import numpy as np


class ModelMonitor:
    """Monitoring des performances des modèles"""
    
    def __init__(self, models_dir: str = "models/saved"):
        self.models_dir = models_dir
        self.metrics_file = f"{models_dir}/monitoring_metrics.json"
        self.alerts = []
        
    def check_model_health(self) -> Dict:
        """Vérifie l'état des modèles"""
        status = {
            'timestamp': datetime.now().isoformat(),
            'models': {},
            'alerts': []
        }
        
        model_files = {
            'fraud': 'fraud_model.pkl',
            'price': 'price_model.pkl',
            'recommender': 'recommender.pkl',
            'analytics': 'analytics.pkl'
        }
        
        for name, filename in model_files.items():
            path = f"{self.models_dir}/{filename}"
            exists = os.path.exists(path)
            
            model_status = {
                'exists': exists,
                'status': 'ok' if exists else 'missing'
            }
            
            if exists:
                # Vérifier date de modification
                mtime = datetime.fromtimestamp(os.path.getmtime(path))
                age_days = (datetime.now() - mtime).days
                model_status['last_updated'] = mtime.isoformat()
                model_status['age_days'] = age_days
                
                # Alerte si vieux
                if age_days > 7:
                    model_status['status'] = 'stale'
                    status['alerts'].append({
                        'type': 'model_stale',
                        'model': name,
                        'message': f"Modèle {name} non mis à jour depuis {age_days} jours"
                    })
            
            status['models'][name] = model_status
        
        return status
    
    def log_prediction(self, model_name: str, input_data: Dict, 
                       output: Dict, latency_ms: float):
        """Log une prédiction pour monitoring"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'model': model_name,
            'latency_ms': latency_ms,
            'input_hash': hash(str(input_data)) % 10000,
            'output_type': type(output).__name__
        }
        
        # Stocker (dans un vrai système, envoyer vers ELK/DataDog)
        self._append_log(log_entry)
    
    def _append_log(self, entry: Dict):
        """Ajoute au fichier de log"""
        log_file = f"{self.models_dir}/prediction_logs.jsonl"
        with open(log_file, 'a') as f:
            f.write(json.dumps(entry) + '\n')
    
    def detect_drift(self, recent_data: List[Dict], baseline_stats: Dict) -> List[Dict]:
        """Détecte le drift des données"""
        alerts = []
        
        # Vérifier distribution des features
        if 'price_mean' in baseline_stats:
            recent_prices = [d.get('prix', 0) for d in recent_data]
            recent_mean = np.mean(recent_prices)
            
            drift_pct = abs(recent_mean - baseline_stats['price_mean']) / baseline_stats['price_mean']
            
            if drift_pct > 0.2:  # 20% de drift
                alerts.append({
                    'type': 'data_drift',
                    'severity': 'high' if drift_pct > 0.3 else 'medium',
                    'message': f"Drift détecté: prix moyen dévié de {drift_pct*100:.1f}%",
                    'baseline': baseline_stats['price_mean'],
                    'current': recent_mean
                })
        
        return alerts
    
    def get_metrics_summary(self) -> Dict:
        """Résume les métriques de monitoring"""
        return {
            'last_check': datetime.now().isoformat(),
            'model_health': self.check_model_health(),
            'system_status': 'operational'
        }


class PerformanceTracker:
    """Suivi des performances au fil du temps"""
    
    def __init__(self):
        self.predictions = []
        self.feedback = []
    
    def record_prediction(self, model: str, prediction: Dict):
        """Enregistre une prédiction"""
        self.predictions.append({
            'model': model,
            'timestamp': datetime.now().isoformat(),
            'prediction': prediction
        })
    
    def record_feedback(self, prediction_id: str, actual: bool, rating: int = None):
        """Enregistre le feedback utilisateur"""
        self.feedback.append({
            'prediction_id': prediction_id,
            'timestamp': datetime.now().isoformat(),
            'actual': actual,
            'rating': rating
        })
    
    def calculate_accuracy(self, model: str, days: int = 7) -> float:
        """Calcule la précision sur les N derniers jours"""
        cutoff = datetime.now() - timedelta(days=days)
        
        # Filtrer prédictions récentes avec feedback
        recent = [p for p in self.predictions 
                 if p['model'] == model and 
                 datetime.fromisoformat(p['timestamp']) > cutoff]
        
        if not recent:
            return None
        
        # Calculer accuracy (simplifié)
        return 0.85  # Placeholder


# Singleton pour utilisation globale
_monitor = None

def get_monitor() -> ModelMonitor:
    """Récupère l'instance de monitoring"""
    global _monitor
    if _monitor is None:
        _monitor = ModelMonitor()
    return _monitor