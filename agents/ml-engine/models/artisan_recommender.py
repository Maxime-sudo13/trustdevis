"""
Système de scoring et recommandation artisans - TrustDevis
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import cosine_similarity
import joblib
from datetime import datetime


class ArtisanRecommender:
    """Système de recommandation et scoring des artisans"""
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.scoring_model = None
        self.artisan_profiles = None
        self.feature_cols = None
        
    def calculate_artisan_score(self, df_artisans: pd.DataFrame) -> pd.DataFrame:
        """Calcule le score global d'un artisan"""
        df = df_artisans.copy()
        
        # Composantes du score
        df['score_qualite'] = (
            df['note_moyenne'] / 5 * 0.4 +
            np.log1p(df['nb_avis']) / np.log1p(df['nb_avis'].max()) * 0.3 +
            np.clip(df['taux_completion'], 0, 1) * 0.3
        ) * 100
        
        df['score_experience'] = (
            np.clip(df['anciennete'] / 10, 0, 1) * 0.5 +
            np.log1p(df['nb_chantiers']) / np.log1p(df['nb_chantiers'].max()) * 0.5
        ) * 100
        
        df['score_reactivite'] = (
            (1 - np.clip(df['delai_moyen_reponse'] / 48, 0, 1)) * 0.6 +
            np.clip(df['taux_acceptation'], 0, 1) * 0.4
        ) * 100
        
        df['score_certification'] = (
            df['certification_qualibat'] * 0.3 +
            df['certification_rge'] * 0.3 +
            df['assurance_decennale'] * 0.2 +
            df['garantie'] * 0.2
        ) * 100
        
        # Score global pondéré
        df['score_global'] = (
            df['score_qualite'] * 0.35 +
            df['score_experience'] * 0.25 +
            df['score_reactivite'] * 0.25 +
            df['score_certification'] * 0.15
        )
        
        # Normaliser sur 100
        df['score_global'] = np.clip(df['score_global'], 0, 100)
        
        return df
    
    def train_satisfaction_model(self, X: pd.DataFrame, y: np.ndarray) -> Dict:
        """Entraîne le modèle de prédiction de satisfaction"""
        
        print(f"📊 Entraînement modèle satisfaction: {len(X)} échantillons")
        
        self.feature_cols = X.columns.tolist()
        
        self.scoring_model = RandomForestRegressor(
            n_estimators=200,
            max_depth=10,
            random_state=42,
            n_jobs=-1
        )
        
        self.scoring_model.fit(X, y)
        
        # Importance des features
        importance = dict(zip(X.columns, self.scoring_model.feature_importances_))
        
        metrics = {
            'r2': self.scoring_model.score(X, y),
            'feature_importance': importance,
            'training_date': datetime.now().isoformat()
        }
        
        print(f"✅ Modèle satisfaction entraîné - R²: {metrics['r2']:.3f}")
        
        return metrics
    
    def recommend_artisans(self, 
                          client_profile: Dict,
                          artisans_df: pd.DataFrame,
                          project_type: str,
                          top_k: int = 5) -> List[Dict]:
        """Recommande les meilleurs artisans pour un projet"""
        
        # Filtrer par type de travaux
        matching_artisans = artisans_df[
            artisans_df['specialites'].str.contains(project_type, na=False)
        ].copy()
        
        if len(matching_artisans) == 0:
            return []
        
        # Calculer scores
        matching_artisans = self.calculate_artisan_score(matching_artisans)
        
        # Matching score basé sur le profil client
        matching_artisans['matching_score'] = self._calculate_matching_score(
            client_profile, matching_artisans
        )
        
        # Score final combiné
        matching_artisans['score_final'] = (
            matching_artisans['score_global'] * 0.6 +
            matching_artisans['matching_score'] * 0.4
        )
        
        # Trier et retourner top_k
        top_artisans = matching_artisans.nlargest(top_k, 'score_final')
        
        recommendations = []
        for _, artisan in top_artisans.iterrows():
            recommendations.append({
                'artisan_id': artisan['artisan_id'],
                'nom': artisan['nom'],
                'score_global': round(artisan['score_global'], 1),
                'score_matching': round(artisan['matching_score'], 1),
                'note_moyenne': round(artisan['note_moyenne'], 1),
                'nb_avis': int(artisan['nb_avis']),
                'specialites': artisan['specialites'],
                'tarif_horaire': artisan.get('tarif_horaire', None),
                'delai_moyen': artisan.get('delai_moyen_reponse', None),
                'certifications': self._get_certifications(artisan),
                'pourquoi': self._generate_explanation(artisan, client_profile)
            })
        
        return recommendations
    
    def _calculate_matching_score(self, client_profile: Dict, 
                                   artisans_df: pd.DataFrame) -> pd.Series:
        """Calcule le score de matching client-artisan"""
        scores = pd.Series(50, index=artisans_df.index)  # Base 50
        
        # Budget
        if 'budget_max' in client_profile:
            budget_ok = artisans_df['tarif_horaire'] <= client_profile['budget_max'] * 1.2
            scores += budget_ok * 20
        
        # Urgence
        if client_profile.get('urgent', False):
            urgent_ok = artisans_df['delai_moyen_reponse'] <= 24
            scores += urgent_ok * 15
        
        # Préférence qualité vs prix
        if client_profile.get('priorite') == 'qualite':
            scores += (artisans_df['note_moyenne'] / 5) * 15
        elif client_profile.get('priorite') == 'prix':
            scores += (1 - artisans_df['tarif_horaire'] / artisans_df['tarif_horaire'].max()) * 15
        
        # Proximité (si coordonnées disponibles)
        if 'latitude' in client_profile and 'longitude' in client_profile:
            distances = np.sqrt(
                (artisans_df['latitude'] - client_profile['latitude'])**2 +
                (artisans_df['longitude'] - client_profile['longitude'])**2
            )
            scores += (1 - np.clip(distances / distances.max(), 0, 1)) * 10
        
        return scores
    
    def _get_certifications(self, artisan: pd.Series) -> List[str]:
        """Liste les certifications d'un artisan"""
        certs = []
        if artisan.get('certification_qualibat'):
            certs.append('Qualibat')
        if artisan.get('certification_rge'):
            certs.append('RGE')
        if artisan.get('assurance_decennale'):
            certs.append('Assurance décennale')
        if artisan.get('garantie'):
            certs.append('Garantie')
        return certs
    
    def _generate_explanation(self, artisan: pd.Series, 
                               client_profile: Dict) -> str:
        """Génère une explication personnalisée"""
        reasons = []
        
        if artisan['note_moyenne'] >= 4.5:
            reasons.append("excellente réputation")
        if artisan['nb_avis'] >= 50:
            reasons.append("très expérimenté")
        if artisan.get('delai_moyen_reponse', 48) <= 12:
            reasons.append("très réactif")
        if client_profile.get('urgent') and artisan.get('delai_moyen_reponse', 48) <= 24:
            reasons.append("disponible rapidement")
        if artisan.get('certification_rge') and client_profile.get('eco_concern'):
            reasons.append("certifié RGE")
        
        if reasons:
            return f"Recommandé pour : {', '.join(reasons[:3])}"
        return "Bon matching avec votre profil"
    
    def predict_satisfaction(self, artisan_features: pd.DataFrame) -> Dict:
        """Prédit la satisfaction client pour un artisan"""
        if self.scoring_model is None:
            raise ValueError("Modèle non entraîné")
        
        prediction = self.scoring_model.predict(artisan_features)
        
        return {
            'predicted_satisfaction': float(prediction[0]) if len(prediction) == 1 else prediction.tolist(),
            'confidence': 'high' if hasattr(self.scoring_model, 'score') and self.scoring_model.score > 0.7 else 'medium'
        }
    
    def create_synthetic_artisans(self, n: int = 500) -> pd.DataFrame:
        """Crée des données synthétiques d'artisans"""
        np.random.seed(42)
        
        specialites_list = [
            'toiture', 'peinture', 'electricite', 'plomberie',
            'chauffage', 'isolation', 'menuiserie', 'maconnerie'
        ]
        
        data = {
            'artisan_id': range(1000, 1000 + n),
            'nom': [f"Artisan {i}" for i in range(n)],
            'specialites': [', '.join(np.random.choice(specialites_list, 
                                                      np.random.randint(1, 4), 
                                                      replace=False)) 
                           for _ in range(n)],
            'note_moyenne': np.clip(np.random.normal(4.2, 0.6, n), 1, 5),
            'nb_avis': np.random.lognormal(3, 1.2, n).astype(int),
            'anciennete': np.random.exponential(5, n).clip(0.5, 30),
            'nb_chantiers': np.random.lognormal(4, 1, n).astype(int),
            'taux_completion': np.clip(np.random.beta(8, 2, n), 0.5, 1),
            'delai_moyen_reponse': np.random.exponential(12, n).clip(1, 72),
            'taux_acceptation': np.clip(np.random.beta(7, 3, n), 0.3, 1),
            'tarif_horaire': np.random.lognormal(3.5, 0.3, n),
            'certification_qualibat': np.random.random(n) < 0.3,
            'certification_rge': np.random.random(n) < 0.25,
            'assurance_decennale': np.random.random(n) < 0.9,
            'garantie': np.random.random(n) < 0.7,
            'latitude': np.random.uniform(43, 49, n),
            'longitude': np.random.uniform(-1, 6, n),
        }
        
        return pd.DataFrame(data)
    
    def save(self, path: str):
        """Sauvegarde le modèle"""
        model_data = {
            'scoring_model': self.scoring_model,
            'feature_cols': self.feature_cols,
            'config': self.config
        }
        joblib.dump(model_data, path)
        print(f"💾 Recommandeur sauvegardé: {path}")
    
    @classmethod
    def load(cls, path: str):
        """Charge le modèle"""
        model_data = joblib.load(path)
        
        instance = cls(model_data['config'])
        instance.scoring_model = model_data['scoring_model']
        instance.feature_cols = model_data['feature_cols']
        
        return instance