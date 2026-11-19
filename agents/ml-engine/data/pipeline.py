"""
Pipeline de données pour TrustDevis ML
Gestion des features, preprocessing et transformations
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
import joblib
from datetime import datetime
import json


class DataPipeline:
    """Pipeline de données pour préparation des features"""
    
    def __init__(self, config_path: str = "config/config.json"):
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        
        self.preprocessor = None
        self.feature_names = None
        
    def create_synthetic_dataset(self, n_samples: int = 5000, seed: int = 42) -> pd.DataFrame:
        """Crée un dataset synthétique pour l'entraînement initial"""
        np.random.seed(seed)
        
        # Types de travaux
        types_travaux = ['toiture', 'peinture', 'electricite', 'plomberie', 
                        'chauffage', 'isolation', 'menuiserie', 'maconnerie']
        
        # Régions
        regions = ['IDF', 'PACA', 'ARA', 'OCC', 'NAQ', 'BRE', 'PDL', 'HDF', 
                   'GES', 'BFC', 'NOR', 'CVL', 'IDF']
        
        # Saisons
        saisons = ['printemps', 'ete', 'automne', 'hiver']
        
        # Matériaux
        materiaux = ['standard', 'premium', 'economique', 'ecologique']
        
        # Complexité
        complexites = ['simple', 'moyenne', 'complexe', 'tres_complexe']
        
        data = {
            'devis_id': range(n_samples),
            'type_travaux': np.random.choice(types_travaux, n_samples),
            'region': np.random.choice(regions, n_samples),
            'saison': np.random.choice(saisons, n_samples),
            'surface': np.random.lognormal(4, 0.8, n_samples),
            'materiaux': np.random.choice(materiaux, n_samples),
            'complexite': np.random.choice(complexites, n_samples),
            'artisan_id': np.random.randint(1000, 9999, n_samples),
            'anciennete_artisan': np.random.exponential(5, n_samples).clip(0, 30),
            'note_artisan': np.random.beta(7, 2, n_samples) * 5,
            'nb_avis_artisan': np.random.lognormal(3, 1, n_samples).astype(int),
        }
        
        df = pd.DataFrame(data)
        
        # Générer prix de référence basé sur features
        df['prix_reference'] = (
            df['surface'] * 
            np.where(df['type_travaux'] == 'toiture', 150,
                    np.where(df['type_travaux'] == 'electricite', 80,
                            np.where(df['type_travaux'] == 'plomberie', 100, 60))) *
            np.where(df['materiaux'] == 'premium', 1.5,
                    np.where(df['materiaux'] == 'economique', 0.7, 1.0)) *
            np.where(df['complexite'] == 'complexe', 1.4,
                    np.where(df['complexite'] == 'tres_complexe', 1.8, 1.0)) *
            np.where(df['region'] == 'IDF', 1.3,
                    np.where(df['region'] == 'PACA', 1.2, 1.0))
        )
        
        # Ajouter bruit
        df['prix_reference'] *= np.random.lognormal(0, 0.15, n_samples)
        
        # Générer prix proposé (avec anomalies pour fraude)
        fraud_rate = 0.08
        is_fraud = np.random.random(n_samples) < fraud_rate
        
        df['prix_propose'] = df['prix_reference'].copy()
        df.loc[is_fraud, 'prix_propose'] *= np.random.uniform(1.5, 3.0, is_fraud.sum())
        df.loc[~is_fraud, 'prix_propose'] *= np.random.lognormal(0, 0.1, (~is_fraud).sum())
        
        df['is_fraud'] = is_fraud.astype(int)
        
        # Features additionnelles - RETIRÉES car causent des problèmes avec XGBoost
        # df['ecart_prix_pct'] = ((df['prix_propose'] - df['prix_reference']) / df['prix_reference'] * 100)
        # df['delai_reponse_heures'] = np.random.exponential(24, n_samples).clip(1, 168)
        df['nb_devis_similaires'] = np.random.poisson(3, n_samples)
        
        return df
    
    def add_default_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Ajoute les features manquantes avec des valeurs par défaut"""
        df = df.copy()
        
        # Calculer ecart_prix_pct si possible, sinon valeur par défaut
        if 'ecart_prix_pct' not in df.columns:
            if 'prix_reference' in df.columns:
                df['ecart_prix_pct'] = ((df['prix_propose'] - df['prix_reference']) / df['prix_reference'] * 100)
            else:
                df['ecart_prix_pct'] = 0.0
        
        if 'delai_reponse_heures' not in df.columns:
            df['delai_reponse_heures'] = 24.0
        if 'nb_devis_similaires' not in df.columns:
            df['nb_devis_similaires'] = 3
        
        return df
    
    def engineer_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Crée des features avancées"""
        df = df.copy()
        
        # Features temporelles
        if 'date_creation' in df.columns:
            df['date_creation'] = pd.to_datetime(df['date_creation'])
            df['mois'] = df['date_creation'].dt.month
            df['jour_semaine'] = df['date_creation'].dt.dayofweek
            df['est_weekend'] = (df['jour_semaine'] >= 5).astype(int)
        
        # Features prix
        df['prix_par_m2'] = df['prix_propose'] / df['surface']
        df['log_prix'] = np.log1p(df['prix_propose'])
        
        # Features artisan
        df['score_reputation'] = (
            df['note_artisan'] * np.log1p(df['nb_avis_artisan']) * 
            np.log1p(df['anciennete_artisan']) / 10
        )
        
        # Features catégorielles encodées
        df['complexite_score'] = df['complexite'].map({
            'simple': 1, 'moyenne': 2, 'complexe': 3, 'tres_complexe': 4
        })
        
        df['materiaux_score'] = df['materiaux'].map({
            'economique': 1, 'standard': 2, 'ecologique': 2, 'premium': 3
        })
        
        # Interactions
        df['surface_complexite'] = df['surface'] * df['complexite_score']
        df['region_saison'] = df['region'] + '_' + df['saison']
        
        return df
    
    def build_preprocessor(self, numeric_features: List[str], 
                          categorical_features: List[str]) -> ColumnTransformer:
        """Construit le preprocessor sklearn"""
        numeric_transformer = Pipeline(steps=[
            ('scaler', StandardScaler())
        ])
        
        categorical_transformer = Pipeline(steps=[
            ('encoder', LabelEncoder())
        ])
        
        preprocessor = ColumnTransformer(
            transformers=[
                ('num', numeric_transformer, numeric_features),
                ('cat', categorical_transformer, categorical_features)
            ])
        
        return preprocessor
    
    def prepare_data(self, df: pd.DataFrame, target_col: Optional[str] = None,
                     fit: bool = True) -> Tuple[np.ndarray, Optional[np.ndarray]]:
        """Prépare les données pour l'entraînement"""
        df = self.engineer_features(df)
        df = self.add_default_features(df)
        
        # Définir toutes les features (doivent correspondre exactement au modèle)
        # Retirer ecart_prix_pct et delai_reponse_heures qui causent des problèmes
        numeric_features = ['surface', 'prix_propose', 'prix_par_m2', 'log_prix',
                           'anciennete_artisan', 'note_artisan', 'nb_avis_artisan',
                           'score_reputation', 'complexite_score', 'materiaux_score',
                           'surface_complexite']
        
        categorical_features = ['type_travaux', 'region', 'saison', 'materiaux']
        
        # Encoder catégories
        for col in categorical_features:
            if col in df.columns:
                le = LabelEncoder()
                df[col] = le.fit_transform(df[col].astype(str))
        
        # Sélectionner features disponibles
        available_features = [f for f in numeric_features + categorical_features 
                             if f in df.columns]
        
        X = df[available_features].fillna(0)
        
        if target_col and target_col in df.columns:
            y = df[target_col].values
        else:
            y = None
        
        return X, y
    
    def save(self, path: str):
        """Sauvegarde le pipeline"""
        joblib.dump(self, path)
    
    @classmethod
    def load(cls, path: str):
        """Charge le pipeline"""
        return joblib.load(path)