"""
Tests unitaires pour les modèles TrustDevis ML
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
import numpy as np
import pandas as pd
from data.pipeline import DataPipeline
from models.fraud_detection import FraudDetectionModel
from models.price_prediction import PricePredictionModel
from models.artisan_recommender import ArtisanRecommender
from models.market_analytics import MarketAnalytics


class TestDataPipeline(unittest.TestCase):
    """Tests du pipeline de données"""
    
    def setUp(self):
        self.pipeline = DataPipeline()
    
    def test_synthetic_dataset_creation(self):
        """Test création dataset synthétique"""
        df = self.pipeline.create_synthetic_dataset(n_samples=100)
        
        self.assertEqual(len(df), 100)
        self.assertIn('is_fraud', df.columns)
        self.assertIn('prix_propose', df.columns)
        self.assertTrue(df['prix_propose'].min() > 0)
    
    def test_feature_engineering(self):
        """Test création de features"""
        df = self.pipeline.create_synthetic_dataset(n_samples=50)
        df_engineered = self.pipeline.engineer_features(df)
        
        self.assertIn('prix_par_m2', df_engineered.columns)
        self.assertIn('log_prix', df_engineered.columns)
        self.assertIn('score_reputation', df_engineered.columns)


class TestFraudDetection(unittest.TestCase):
    """Tests du modèle de fraude"""
    
    def setUp(self):
        self.model = FraudDetectionModel()
        self.pipeline = DataPipeline()
        self.df = self.pipeline.create_synthetic_dataset(n_samples=500)
    
    def test_model_training(self):
        """Test entraînement modèle"""
        X, y = self.pipeline.prepare_data(self.df, target_col='is_fraud', fit=True)
        
        metrics = self.model.train(X, y, validation_split=0.3)
        
        self.assertIn('auc_roc', metrics)
        self.assertIn('f1_score', metrics)
        self.assertGreater(metrics['auc_roc'], 0.5)  # Meilleur que aléatoire
    
    def test_prediction(self):
        """Test prédiction"""
        X, y = self.pipeline.prepare_data(self.df, target_col='is_fraud', fit=True)
        self.model.train(X, y, validation_split=0.3)
        
        result = self.model.predict(X.iloc[:1])
        
        self.assertIn('is_suspect', result)
        self.assertIn('fraud_probability', result)
        self.assertIn('risk_level', result)
        self.assertTrue(0 <= result['fraud_probability'] <= 1)


class TestPricePrediction(unittest.TestCase):
    """Tests du modèle de prix"""
    
    def setUp(self):
        self.model = PricePredictionModel()
        self.pipeline = DataPipeline()
        self.df = self.pipeline.create_synthetic_dataset(n_samples=500)
    
    def test_model_training(self):
        """Test entraînement modèle prix"""
        X, _ = self.pipeline.prepare_data(self.df, fit=True)
        y = self.df['prix_reference'].values
        
        metrics = self.model.train(X, y, validation_split=0.3)
        
        self.assertIn('mae', metrics)
        self.assertIn('r2', metrics)
        self.assertGreater(metrics['r2'], 0)  # R2 positif
    
    def test_prediction_with_interval(self):
        """Test prédiction avec intervalle"""
        X, _ = self.pipeline.prepare_data(self.df, fit=True)
        y = self.df['prix_reference'].values
        self.model.train(X, y, validation_split=0.3)
        
        result = self.model.predict(X.iloc[:1], confidence=0.95)
        
        self.assertIn('predicted_price', result)
        self.assertIn('confidence_interval', result)
        self.assertLess(
            result['confidence_interval']['lower'],
            result['confidence_interval']['upper']
        )


class TestArtisanRecommender(unittest.TestCase):
    """Tests du recommandeur d'artisans"""
    
    def setUp(self):
        self.recommender = ArtisanRecommender()
    
    def test_artisan_scoring(self):
        """Test calcul des scores"""
        artisans_df = self.recommender.create_synthetic_artisans(50)
        scored_df = self.recommender.calculate_artisan_score(artisans_df)
        
        self.assertIn('score_global', scored_df.columns)
        self.assertTrue(all(0 <= scored_df['score_global']) <= 100)
    
    def test_recommendations(self):
        """Test génération de recommandations"""
        artisans_df = self.recommender.create_synthetic_artisans(100)
        
        client_profile = {
            'budget_max': 80,
            'urgent': False,
            'priorite': 'qualite'
        }
        
        recommendations = self.recommender.recommend_artisans(
            client_profile=client_profile,
            artisans_df=artisans_df,
            project_type='toiture',
            top_k=5
        )
        
        self.assertEqual(len(recommendations), 5)
        self.assertIn('score_global', recommendations[0])
        self.assertIn('pourquoi', recommendations[0])


class TestMarketAnalytics(unittest.TestCase):
    """Tests de l'analytics marché"""
    
    def setUp(self):
        self.analytics = MarketAnalytics()
        self.pipeline = DataPipeline()
        self.df = self.pipeline.create_synthetic_dataset(n_samples=1000)
        self.df['date_creation'] = pd.date_range(end='2024-01-01', periods=1000, freq='D')
    
    def test_seasonality_analysis(self):
        """Test analyse saisonnalité"""
        seasonality = self.analytics.analyze_seasonality(
            self.df, date_col='date_creation', price_col='prix_propose', region_col='region'
        )
        
        self.assertIn('global', seasonality)
    
    def test_anomaly_detection(self):
        """Test détection anomalies"""
        anomalies = self.analytics.detect_anomalies(
            self.df, date_col='date_creation', price_col='prix_propose'
        )
        
        self.assertIsInstance(anomalies, list)


def run_tests():
    """Exécute tous les tests"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestDataPipeline))
    suite.addTests(loader.loadTestsFromTestCase(TestFraudDetection))
    suite.addTests(loader.loadTestsFromTestCase(TestPricePrediction))
    suite.addTests(loader.loadTestsFromTestCase(TestArtisanRecommender))
    suite.addTests(loader.loadTestsFromTestCase(TestMarketAnalytics))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)