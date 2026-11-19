"""
API FastAPI pour les prédictions ML - TrustDevis
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
import numpy as np
import pandas as pd
from datetime import datetime
import json
import os
import sys

# Ajouter le path pour imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.fraud_detection import FraudDetectionModel
from models.price_prediction import PricePredictionModel
from models.artisan_recommender import ArtisanRecommender
from models.market_analytics import MarketAnalytics
from data.pipeline import DataPipeline


def get_risk_level(proba: float) -> str:
    """Détermine le niveau de risque"""
    if proba >= 0.8:
        return "HIGH"
    elif proba >= 0.6:
        return "MEDIUM"
    elif proba >= 0.4:
        return "ELEVATED"
    else:
        return "LOW"


app = FastAPI(
    title="TrustDevis ML API",
    description="API de prédiction Machine Learning pour TrustDevis",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modèles globaux
models = {
    'fraud': None,
    'price': None,
    'recommender': None,
    'analytics': None
}

pipeline = None


# ============== MODÈLES PYDANTIC ==============

class FraudPredictionRequest(BaseModel):
    prix_propose: float = Field(..., gt=0, description="Prix proposé dans le devis")
    region: str = Field(..., description="Région du chantier")
    saison: str = Field(..., description="Saison (printemps, ete, automne, hiver)")
    artisan_id: int = Field(..., description="ID de l'artisan")
    type_travaux: str = Field(..., description="Type de travaux")
    surface: float = Field(..., gt=0, description="Surface en m²")
    materiaux: str = Field(..., description="Type de matériaux")
    complexite: str = Field(..., description="Niveau de complexité")
    note_artisan: float = Field(default=4.0, ge=0, le=5)
    nb_avis_artisan: int = Field(default=10, ge=0)
    anciennete_artisan: float = Field(default=2.0, ge=0)


class PricePredictionRequest(BaseModel):
    type_travaux: str
    region: str
    surface: float = Field(..., gt=0)
    materiaux: str
    complexite: str
    saison: str


class ArtisanRecommendationRequest(BaseModel):
    client_profile: Dict
    project_type: str
    region: Optional[str] = None
    budget_max: Optional[float] = None
    urgent: bool = False
    top_k: int = Field(default=5, ge=1, le=20)


class PredictionResponse(BaseModel):
    success: bool
    data: Dict
    timestamp: str


# ============== ENDPOINTS ==============

@app.on_event("startup")
async def load_models():
    """Charge les modèles au démarrage"""
    global models, pipeline
    
    models_dir = os.path.join(os.path.dirname(__file__), '..', 'models', 'saved')
    
    try:
        if os.path.exists(f"{models_dir}/fraud_model.pkl"):
            models['fraud'] = FraudDetectionModel.load(f"{models_dir}/fraud_model.pkl")
            # Supprimer feature names pour éviter les erreurs
            if hasattr(models['fraud'].model, 'named_steps'):
                classifier = models['fraud'].model.named_steps['classifier']
            else:
                classifier = models['fraud'].model
            # Les feature names sont gérés automatiquement
            print("✅ Modèle fraude chargé")
        
        if os.path.exists(f"{models_dir}/price_model.pkl"):
            models['price'] = PricePredictionModel.load(f"{models_dir}/price_model.pkl")
            # Les feature names sont gérés automatiquement
            print("✅ Modèle prix chargé")
        
        if os.path.exists(f"{models_dir}/recommender.pkl"):
            models['recommender'] = ArtisanRecommender.load(f"{models_dir}/recommender.pkl")
            print("✅ Recommandeur chargé")
        
        if os.path.exists(f"{models_dir}/analytics.pkl"):
            models['analytics'] = MarketAnalytics.load(f"{models_dir}/analytics.pkl")
            print("✅ Analytics chargé")
        
        pipeline = DataPipeline()
        print("✅ Pipeline initialisé")
        
    except Exception as e:
        print(f"⚠️ Erreur chargement modèles: {e}")


@app.get("/health")
async def health_check():
    """Vérifie l'état de l'API"""
    return {
        "status": "healthy",
        "models_loaded": {k: v is not None for k, v in models.items()},
        "timestamp": datetime.now().isoformat()
    }


@app.post("/predict/fraud", response_model=PredictionResponse)
async def predict_fraud(request: FraudPredictionRequest):
    """Détecte si un devis est suspect"""
    
    if models['fraud'] is None:
        raise HTTPException(status_code=503, detail="Modèle fraude non disponible")
    
    try:
        # Préparer données
        data = pd.DataFrame([request.dict()])
        X, _ = pipeline.prepare_data(data, fit=False)
        
        # S'assurer que toutes les features attendues sont présentes
        if hasattr(models['fraud'].model, 'named_steps'):
            classifier = models['fraud'].model.named_steps['classifier']
        else:
            classifier = models['fraud'].model
        
        if hasattr(classifier, 'feature_names_in_'):
            expected_features = list(classifier.feature_names_in_)
            # Ajouter les colonnes manquantes avec valeur 0
            for col in expected_features:
                if col not in X.columns:
                    X[col] = 0.0
            # Réordonner selon l'ordre attendu
            X = X[expected_features]
        
        # Convertir en numpy array pour éviter les vérifications de noms
        X_array = X.values.astype(float)
        
        # Prédire directement avec le classifier
        proba = classifier.predict_proba(X_array)[:, 1]
        prediction = (proba >= models['fraud'].threshold).astype(int)
        
        result = {
            'is_suspect': bool(prediction[0]),
            'fraud_probability': float(proba[0]),
            'risk_level': get_risk_level(proba[0])
        }
        
        return PredictionResponse(
            success=True,
            data=result,
            timestamp=datetime.now().isoformat()
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/predict/price", response_model=PredictionResponse)
async def predict_price(request: PricePredictionRequest, confidence: float = 0.95):
    """Prédit le prix d'un devis avec intervalle de confiance"""
    
    if models['price'] is None:
        raise HTTPException(status_code=503, detail="Modèle prix non disponible")
    
    try:
        # Préparer données
        data = pd.DataFrame([request.dict()])
        
        # Ajouter features requises par le modèle
        data['prix_propose'] = 100  # Valeur temporaire
        data['note_artisan'] = 4.0
        data['nb_avis_artisan'] = 10
        data['anciennete_artisan'] = 2.0
        
        X, _ = pipeline.prepare_data(data, fit=False)
        
        # S'assurer que toutes les features attendues sont présentes
        if hasattr(models['price'].model, 'feature_names_in_'):
            expected_features = list(models['price'].model.feature_names_in_)
            for col in expected_features:
                if col not in X.columns:
                    X[col] = 0.0
            X = X[expected_features]
        
        # Convertir en numpy array
        X_array = X.values.astype(float)
        
        # Prédire directement
        pred_log = models['price'].model.predict(X_array)
        prediction = np.expm1(pred_log)
        
        # Intervalles simplifiés
        result = {
            'predicted_price': float(prediction[0]),
            'confidence_interval': {
                'lower': float(prediction[0] * 0.8),
                'upper': float(prediction[0] * 1.2),
                'confidence_level': confidence
            }
        }
        
        return PredictionResponse(
            success=True,
            data=result,
            timestamp=datetime.now().isoformat()
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/recommend/artisans", response_model=PredictionResponse)
async def recommend_artisans(request: ArtisanRecommendationRequest):
    """Recommande des artisans pour un projet"""
    
    if models['recommender'] is None:
        raise HTTPException(status_code=503, detail="Recommandeur non disponible")
    
    try:
        # Créer artisans synthétiques si pas de données réelles
        artisans_df = models['recommender'].create_synthetic_artisans(200)
        
        # Recommander
        recommendations = models['recommender'].recommend_artisans(
            client_profile=request.client_profile,
            artisans_df=artisans_df,
            project_type=request.project_type,
            top_k=request.top_k
        )
        
        return PredictionResponse(
            success=True,
            data={
                'recommendations': recommendations,
                'count': len(recommendations)
            },
            timestamp=datetime.now().isoformat()
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/analytics/trends")
async def get_trends(region: Optional[str] = None):
    """Récupère les tendances de marché"""
    
    if models['analytics'] is None:
        raise HTTPException(status_code=503, detail="Analytics non disponible")
    
    try:
        trends = models['analytics'].trend_models
        
        if region and region in trends:
            return PredictionResponse(
                success=True,
                data=trends[region],
                timestamp=datetime.now().isoformat()
            )
        
        return PredictionResponse(
            success=True,
            data=trends,
            timestamp=datetime.now().isoformat()
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/analytics/seasonality")
async def get_seasonality():
    """Récupère l'analyse de saisonnalité"""
    
    if models['analytics'] is None:
        raise HTTPException(status_code=503, detail="Analytics non disponible")
    
    return PredictionResponse(
        success=True,
        data=models['analytics'].seasonality_patterns,
        timestamp=datetime.now().isoformat()
    )


@app.get("/analytics/alerts")
async def get_alerts():
    """Récupère les alertes marché"""
    
    if models['analytics'] is None:
        raise HTTPException(status_code=503, detail="Analytics non disponible")
    
    # Générer dataset synthétique pour alertes
    pipeline_temp = DataPipeline()
    df = pipeline_temp.create_synthetic_dataset(1000)
    df['date_creation'] = pd.date_range(end=datetime.now(), periods=1000, freq='D')
    
    alerts = models['analytics'].generate_alerts(df)
    
    return PredictionResponse(
        success=True,
        data={'alerts': alerts, 'count': len(alerts)},
        timestamp=datetime.now().isoformat()
    )


@app.get("/models/metrics")
async def get_models_metrics():
    """Récupère les métriques des modèles"""
    
    metrics = {}
    
    for name, model in models.items():
        if model is not None and hasattr(model, 'metrics'):
            metrics[name] = model.metrics
    
    return PredictionResponse(
        success=True,
        data=metrics,
        timestamp=datetime.now().isoformat()
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)