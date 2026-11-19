"""
Artisans Compare Service - TrustDevis
Service de comparaison d'artisans (concurrence Travaux.com)
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
import uvicorn
import random

from models import Artisan, ArtisanProfile, Review, ComparisonResult, ArtisanMatchRequest
from database import init_db, get_artisans, get_artisan_by_id, search_artisans, get_reviews
from matching import match_artisans, calculate_transparency_score
from comparison import compare_artisans

app = FastAPI(
    title="TrustDevis Artisans Compare",
    description="Service de comparaison d'artisans",
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

# ============ API ENDPOINTS ============

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "artisans-compare"}


@app.get("/artisans/search", response_model=List[Artisan])
def search_artisans_endpoint(
    q: Optional[str] = Query(None, description="Terme de recherche"),
    specialty: Optional[str] = Query(None, description="Spécialité"),
    location: Optional[str] = Query(None, description="Localisation"),
    min_rating: Optional[float] = Query(None, ge=0, le=5, description="Note minimum"),
    available: Optional[bool] = Query(None, description="Disponible maintenant"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """
    Rechercher des artisans selon critères
    """
    results = search_artisans(
        query=q,
        specialty=specialty,
        location=location,
        min_rating=min_rating,
        available=available,
        limit=limit,
        offset=offset
    )
    return results


@app.get("/artisans/{artisan_id}", response_model=ArtisanProfile)
def get_artisan_details(artisan_id: str):
    """
    Obtenir les détails complets d'un artisan
    """
    artisan = get_artisan_by_id(artisan_id)
    if not artisan:
        raise HTTPException(status_code=404, detail="Artisan non trouvé")
    
    reviews = get_reviews(artisan_id)
    
    return ArtisanProfile(
        **artisan.dict(),
        reviews=reviews,
        completed_projects=random.randint(50, 500),
        response_time_hours=random.randint(1, 48),
        quote_acceptance_rate=random.uniform(0.3, 0.9)
    )


@app.post("/artisans/compare")
def compare_artisans_endpoint(request: ArtisanMatchRequest):
    """
    Comparer jusqu'à 3 artisans pour un projet
    """
    if len(request.artisan_ids) < 2 or len(request.artisan_ids) > 3:
        raise HTTPException(
            status_code=400, 
            detail="Veuillez sélectionner 2 ou 3 artisans à comparer"
        )
    
    artisans = []
    for aid in request.artisan_ids:
        artisan = get_artisan_by_id(aid)
        if not artisan:
            raise HTTPException(status_code=404, detail=f"Artisan {aid} non trouvé")
        artisans.append(artisan)
    
    comparison = compare_artisans(artisans, request.project_type, request.budget)
    return comparison


@app.get("/artisans/{artisan_id}/reviews", response_model=List[Review])
def get_artisan_reviews(
    artisan_id: str,
    limit: int = Query(10, ge=1, le=50),
    offset: int = Query(0, ge=0)
):
    """
    Obtenir les avis clients d'un artisan
    """
    artisan = get_artisan_by_id(artisan_id)
    if not artisan:
        raise HTTPException(status_code=404, detail="Artisan non trouvé")
    
    return get_reviews(artisan_id, limit=limit, offset=offset)


@app.post("/artisans/match")
def match_artisans_endpoint(request: ArtisanMatchRequest):
    """
    Trouver les meilleurs artisans pour un projet
    """
    matches = match_artisans(
        project_type=request.project_type,
        location=request.location,
        budget=request.budget,
        urgency=request.urgency,
        limit=3
    )
    
    return {
        "matches": matches,
        "project_type": request.project_type,
        "location": request.location,
        "recommendation_reason": "Basé sur la proximité, les avis clients et l'expertise"
    }


@app.get("/specialties")
def get_specialties():
    """
    Liste des spécialités disponibles
    """
    return {
        "specialties": [
            {"id": "plomberie", "name": "Plomberie", "icon": "🚿"},
            {"id": "electricite", "name": "Électricité", "icon": "⚡"},
            {"id": "maconnerie", "name": "Maçonnerie", "icon": "🧱"},
            {"id": "peinture", "name": "Peinture", "icon": "🎨"},
            {"id": "menuiserie", "name": "Menuiserie", "icon": "🪚"},
            {"id": "couverture", "name": "Couverture/Toiture", "icon": "🏠"},
            {"id": "chauffage", "name": "Chauffage/Climatisation", "icon": "🔥"},
            {"id": "carrelage", "name": "Carrelage", "icon": "⬜"},
            {"id": "jardinage", "name": "Jardinage/Paysagisme", "icon": "🌳"},
            {"id": "renovation", "name": "Rénovation générale", "icon": "🔨"},
        ]
    }


@app.get("/badges")
def get_badges_info():
    """
    Informations sur les badges TrustDevis
    """
    return {
        "badges": [
            {
                "id": "trustdevis_verified",
                "name": "TrustDevis Vérifié",
                "description": "Artisan vérifié par TrustDevis",
                "icon": "✅"
            },
            {
                "id": "transparency_excellent",
                "name": "Excellence Transparence",
                "description": "Score de transparence > 90%",
                "icon": "🔍"
            },
            {
                "id": "quality_gold",
                "name": "Qualité Or",
                "description": "Note moyenne > 4.7 sur 5",
                "icon": "⭐"
            },
            {
                "id": "punctuality",
                "name": "Respect des Délais",
                "description": "Respect des délais constaté",
                "icon": "⏱️"
            },
            {
                "id": "responsive",
                "name": "Réactif",
                "description": "Répond en moins de 2h en moyenne",
                "icon": "⚡"
            },
            {
                "id": "insured",
                "name": "Assuré",
                "description": "Assurance responsabilité civile à jour",
                "icon": "🛡️"
            },
            {
                "id": "certified",
                "name": "Certifié",
                "description": "Certifications professionnelles",
                "icon": "📜"
            }
        ]
    }


# ============ LANDING PAGE INTEGRATION ============

@app.get("/landing/recommended")
def get_recommended_artisans(
    project_type: Optional[str] = None,
    location: Optional[str] = None
):
    """
    Artisans recommandés pour la landing page
    """
    artisans = search_artisans(
        specialty=project_type,
        location=location,
        min_rating=4.0,
        limit=6
    )
    
    return {
        "title": "Artisans de confiance près de chez vous",
        "subtitle": "Vérifiés et notés par la communauté TrustDevis",
        "artisans": artisans,
        "cta": {
            "text": "Voir tous les artisans",
            "link": "/artisans"
        }
    }


@app.get("/landing/after-analysis")
def get_artisans_after_analysis(
    quote_id: str,
    project_type: str,
    detected_price: float
):
    """
    Artisans recommandés après analyse de devis
    """
    artisans = match_artisans(
        project_type=project_type,
        budget=detected_price,
        limit=3
    )
    
    return {
        "title": "Artisans recommandés pour votre projet",
        "context": {
            "quote_analyzed": quote_id,
            "project_type": project_type,
            "price_detected": detected_price
        },
        "artisans": artisans,
        "comparison_cta": {
            "text": "Comparer ces artisans",
            "action": "compare"
        }
    }


# ============ MAIN ============

if __name__ == "__main__":
    init_db()
    uvicorn.run(app, host="0.0.0.0", port=8010)
