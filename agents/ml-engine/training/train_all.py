"""
Script d'entraînement complet - TrustDevis ML
Entraîne tous les modèles et sauvegarde
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

import numpy as np
import pandas as pd
from datetime import datetime
import json
import joblib

from data.pipeline import DataPipeline
from models.fraud_detection import FraudDetectionModel
from models.price_prediction import PricePredictionModel
from models.artisan_recommender import ArtisanRecommender
from models.market_analytics import MarketAnalytics


def train_fraud_model(df: pd.DataFrame, pipeline: DataPipeline) -> FraudDetectionModel:
    """Entraîne le modèle de détection de fraude"""
    print("\n" + "="*50)
    print("🛡️  ENTRAÎNEMENT: Détection de Fraude")
    print("="*50)
    
    # Préparer données
    X, y = pipeline.prepare_data(df, target_col='is_fraud', fit=True)
    
    # Entraîner
    model = FraudDetectionModel()
    metrics = model.train(X, y)
    
    # Validation croisée
    cv_results = model.cross_validate(X, y)
    print(f"\n📊 Validation croisée:")
    print(f"   AUC moyen: {cv_results['cv_auc_mean']:.3f} (+/- {cv_results['cv_auc_std']*2:.3f})")
    
    return model


def train_price_model(df: pd.DataFrame, pipeline: DataPipeline) -> PricePredictionModel:
    """Entraîne le modèle de prédiction de prix"""
    print("\n" + "="*50)
    print("💰 ENTRAÎNEMENT: Prédiction de Prix")
    print("="*50)
    
    # Préparer données
    X, _ = pipeline.prepare_data(df, fit=False)
    y = df['prix_reference'].values
    
    # Entraîner
    model = PricePredictionModel()
    metrics = model.train(X, y)
    
    # Validation croisée
    cv_results = model.cross_validate(X, y)
    print(f"\n📊 Validation croisée:")
    print(f"   MAE moyen: {cv_results['cv_mae_mean']:.0f}€ (+/- {cv_results['cv_mae_std']*2:.0f}€)")
    
    # Test prédiction
    sample_pred = model.predict(X.iloc[:1])
    print(f"\n📝 Exemple prédiction:")
    print(f"   Prix prédit: {sample_pred['predicted_price']:.0f}€")
    print(f"   Intervalle 95%: {sample_pred['confidence_interval']['lower']:.0f}€ - {sample_pred['confidence_interval']['upper']:.0f}€")
    
    return model


def train_recommender() -> ArtisanRecommender:
    """Entraîne le système de recommandation"""
    print("\n" + "="*50)
    print("⭐ ENTRAÎNEMENT: Recommandation Artisans")
    print("="*50)
    
    recommender = ArtisanRecommender()
    
    # Créer artisans synthétiques
    artisans_df = recommender.create_synthetic_artisans(500)
    print(f"📊 Dataset: {len(artisans_df)} artisans synthétiques")
    
    # Calculer scores
    artisans_scored = recommender.calculate_artisan_score(artisans_df)
    
    print(f"\n📈 Distribution des scores:")
    print(f"   Moyenne: {artisans_scored['score_global'].mean():.1f}")
    print(f"   Médiane: {artisans_scored['score_global'].median():.1f}")
    print(f"   Top 10%: {artisans_scored['score_global'].quantile(0.9):.1f}")
    
    # Test recommandation
    client_profile = {
        'budget_max': 80,
        'urgent': True,
        'priorite': 'qualite'
    }
    
    recommendations = recommender.recommend_artisans(
        client_profile=client_profile,
        artisans_df=artisans_df,
        project_type='toiture',
        top_k=3
    )
    
    print(f"\n📝 Exemple recommandation (toiture, urgent):")
    for i, rec in enumerate(recommendations[:3], 1):
        print(f"   {i}. {rec['nom']} - Score: {rec['score_global']}/100 - {rec['pourquoi']}")
    
    return recommender


def train_analytics(df: pd.DataFrame) -> MarketAnalytics:
    """Entraîne l'analytics de marché"""
    print("\n" + "="*50)
    print("📈 ENTRAÎNEMENT: Analytics Marché")
    print("="*50)
    
    analytics = MarketAnalytics()
    
    # Ajouter dates
    df['date_creation'] = pd.date_range(end=datetime.now(), periods=len(df), freq='D')
    
    # Analyser saisonnalité
    print("\n🌤️  Analyse saisonnalité...")
    seasonality = analytics.analyze_seasonality(
        df, date_col='date_creation', price_col='prix_propose', region_col='region'
    )
    
    if 'global' in seasonality:
        print(f"   Saison la plus chère: {max(seasonality['global']['mean'], key=seasonality['global']['mean'].get)}")
    
    # Forecast tendances
    print("\n📉 Forecast tendances...")
    trends = analytics.forecast_trends(
        df, date_col='date_creation', price_col='prix_propose', region_col='region'
    )
    
    print(f"   Régions analysées: {len(trends)}")
    for region, trend in list(trends.items())[:3]:
        print(f"   - {region}: tendance {trend['trend_direction']}")
    
    # Détecter anomalies
    print("\n⚠️  Détection anomalies...")
    anomalies = analytics.detect_anomalies(df, date_col='date_creation', price_col='prix_propose')
    print(f"   Anomalies détectées: {len(anomalies)}")
    
    if anomalies:
        print(f"   Plus gros écart: {anomalies[0]['deviation_pct']:.1f}% en {anomalies[0]['region']}")
    
    return analytics


def main():
    """Pipeline d'entraînement complet"""
    print("\n" + "🚀"*25)
    print("  TRUSTDEVIS ML - PIPELINE D'ENTRAÎNEMENT")
    print("🚀"*25 + "\n")
    
    start_time = datetime.now()
    
    # Créer dossier pour modèles
    models_dir = os.path.join(os.path.dirname(__file__), '..', 'models', 'saved')
    os.makedirs(models_dir, exist_ok=True)
    
    # Initialiser pipeline et créer données
    print("📦 Génération du dataset synthétique...")
    pipeline = DataPipeline()
    df = pipeline.create_synthetic_dataset(n_samples=10000, seed=42)
    print(f"   ✓ {len(df)} devis générés")
    print(f"   ✓ Taux de fraude: {df['is_fraud'].mean()*100:.1f}%")
    print(f"   ✓ Prix moyen: {df['prix_propose'].mean():.0f}€")
    
    # Entraîner tous les modèles
    models = {}
    
    # 1. Fraude
    models['fraud'] = train_fraud_model(df, pipeline)
    models['fraud'].save(f"{models_dir}/fraud_model.pkl")
    
    # 2. Prix
    models['price'] = train_price_model(df, pipeline)
    models['price'].save(f"{models_dir}/price_model.pkl")
    
    # 3. Recommandation
    models['recommender'] = train_recommender()
    models['recommender'].save(f"{models_dir}/recommender.pkl")
    
    # 4. Analytics
    models['analytics'] = train_analytics(df)
    models['analytics'].save(f"{models_dir}/analytics.pkl")
    
    # Sauvegarder pipeline
    pipeline.save(f"{models_dir}/pipeline.pkl")
    
    # Résumé
    duration = (datetime.now() - start_time).total_seconds()
    
    print("\n" + "="*50)
    print("✅ ENTRAÎNEMENT TERMINÉ")
    print("="*50)
    print(f"\n⏱️  Durée: {duration:.1f}s")
    print(f"📁 Modèles sauvegardés dans: {models_dir}")
    print("\n📊 Résumé des modèles:")
    
    for name, model in models.items():
        if hasattr(model, 'metrics') and model.metrics:
            print(f"   • {name}: OK")
    
    print("\n🚀 API prête à démarrer:")
    print(f"   cd /root/.openclaw/workspace/trustdevis/agents/ml-engine")
    print(f"   uvicorn api.main:app --host 0.0.0.0 --port 8000")
    
    # Sauvegarder rapport
    report = {
        'training_date': datetime.now().isoformat(),
        'duration_seconds': duration,
        'dataset_size': len(df),
        'fraud_rate': float(df['is_fraud'].mean()),
        'models': {name: {'trained': True} for name in models.keys()}
    }
    
    with open(f"{models_dir}/training_report.json", 'w') as f:
        json.dump(report, f, indent=2)
    
    return models


if __name__ == "__main__":
    main()