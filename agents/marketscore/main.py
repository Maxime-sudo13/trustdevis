"""
TrustDevis MarketScore - Service FastAPI
Endpoint principal : POST /score
"""
import os
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from contextlib import asynccontextmanager

from scorer import scorer_devis, ScoreResult
from llm_integration import LLMIntegration
from rules import RiskLevel


# ==================== MODÈLES PYDANTIC ====================

class LigneDevis(BaseModel):
    """Une ligne de devis."""
    categorie: str = Field(..., description="Catégorie: main_oeuvre, materiaux, pieces, deplacement, diagnostic, autre")
    description: str = Field(..., description="Description de la prestation")
    montant: float = Field(..., ge=0, description="Montant en euros")
    quantite: Optional[float] = Field(default=1, ge=0)
    unite: Optional[str] = Field(default="forfait")


class MedianeMarche(BaseModel):
    """Statistiques de marché pour une catégorie."""
    median: float
    q1: Optional[float] = None
    q3: Optional[float] = None
    count: Optional[int] = None


class MarketStats(BaseModel):
    """Statistiques du marché régional."""
    region: str = Field(..., description="Code région")
    medianes: Dict[str, MedianeMarche] = Field(default_factory=dict)
    date_mise_a_jour: Optional[str] = None


class HistoriqueItem(BaseModel):
    """Élément d'historique de devis."""
    date: str
    secteur: str
    score: int
    delta_pct: float


class ScoreRequest(BaseModel):
    """Requête de scoring."""
    devis: Dict[str, Any] = Field(..., description="Informations du devis")
    market_stats: MarketStats = Field(..., description="Statistiques du marché")
    historique: List[HistoriqueItem] = Field(default_factory=list)
    
    class Config:
        json_schema_extra = {
            "example": {
                "devis": {
                    "secteur": "batiment",
                    "lignes": [
                        {"categorie": "main_oeuvre", "description": "Pose carrelage", "montant": 1500},
                        {"categorie": "materiaux", "description": "Carrelage premium", "montant": 800}
                    ]
                },
                "market_stats": {
                    "region": "IDF",
                    "medianes": {
                        "main_oeuvre": {"median": 1200, "q1": 1000, "q3": 1400},
                        "materiaux": {"median": 700, "q1": 600, "q3": 800}
                    }
                },
                "historique": []
            }
        }


class ConfidenceSource(BaseModel):
    """Source de confiance pour le score."""
    name: str
    weight: float = Field(..., ge=0, le=1)


class ScoreResponse(BaseModel):
    """Réponse de scoring - FORMAT JSON EXACT."""
    score: int = Field(..., ge=0, le=100, description="Score de confiance 0-100")
    delta_pct: float = Field(..., description="Delta global en % par rapport au marché")
    risk_level: str = Field(..., pattern="^(low|moderate|high)$")
    justification: List[str] = Field(..., description="Justifications ligne par ligne")
    actions_for_client: List[str] = Field(..., description="Actions recommandées")
    confidence_sources: List[ConfidenceSource] = Field(..., description="Sources de confiance")
    requires_human_review: bool = Field(..., description="Nécessite une revue humaine")
    
    class Config:
        json_schema_extra = {
            "example": {
                "score": 75,
                "delta_pct": 15.2,
                "risk_level": "low",
                "justification": [
                    "main_oeuvre: Probabilité de sur-tarification de 25% par rapport à la médiane régionale"
                ],
                "actions_for_client": [
                    "1. Demander un détail des heures de main d'œuvre"
                ],
                "confidence_sources": [
                    {"name": "marché régional", "weight": 0.6}
                ],
                "requires_human_review": False
            }
        }


# ==================== APPLICATION FASTAPI ====================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestion du cycle de vie de l'application."""
    # Startup
    app.state.llm = None
    try:
        app.state.llm = LLMIntegration()
    except ValueError:
        # Mode sans LLM (fallback local)
        pass
    yield
    # Shutdown
    pass


app = FastAPI(
    title="TrustDevis MarketScore",
    description="Service de scoring de devis par comparaison au marché",
    version="1.0.0",
    lifespan=lifespan
)


# ==================== ENDPOINTS ====================

@app.get("/health")
async def health_check():
    """Health check du service."""
    return {
        "status": "healthy",
        "service": "marketscore",
        "llm_available": app.state.llm is not None
    }


@app.post("/score", response_model=ScoreResponse)
async def score_devis(request: ScoreRequest):
    """
    Calcule le score de confiance d'un devis.
    
    Compare le devis aux statistiques du marché régional et génère :
    - Un score de confiance (0-100)
    - Un niveau de risque (low/moderate/high)
    - Des justifications factuelles
    - Des actions recommandées
    """
    try:
        # Extraction des données
        devis_data = request.devis
        secteur = devis_data.get("secteur", "generique")
        lignes = devis_data.get("lignes", [])
        
        if not lignes:
            raise HTTPException(status_code=400, detail="Aucune ligne dans le devis")
        
        # Conversion des market_stats en dict
        market_stats_dict = {
            "region": request.market_stats.region,
            "medianes": {
                k: v.model_dump() if hasattr(v, 'model_dump') else v 
                for k, v in request.market_stats.medianes.items()
            }
        }
        
        # === ÉTAPE 1: Scoring algorithmique ===
        score_result = scorer_devis(lignes, market_stats_dict, secteur)
        
        # === ÉTAPE 2: Génération des justifications via LLM (ou fallback) ===
        justification = []
        actions = []
        
        if app.state.llm:
            try:
                justification = await app.state.llm.generate_justification(
                    lignes_detail=score_result.lignes_detail,
                    score=score_result.score,
                    delta_pct=score_result.delta_pct,
                    risk_level=score_result.risk_level,
                    secteur=secteur
                )
                actions = await app.state.llm.generate_actions(
                    lignes_detail=score_result.lignes_detail,
                    score=score_result.score,
                    risk_level=score_result.risk_level,
                    secteur=secteur
                )
            except Exception:
                # Fallback sur la génération locale
                pass
        
        # Si LLM indisponible ou en erreur, utiliser le fallback
        if not justification:
            from llm_integration import LLMIntegration
            llm_fallback = LLMIntegration(api_key="dummy")  # Pour accès aux méthodes fallback
            justification = llm_fallback._generate_fallback_justifications(score_result.lignes_detail)
            actions = llm_fallback._generate_fallback_actions(score_result.risk_level, score_result.score)
        
        # === ÉTAPE 3: Construction des sources de confiance ===
        confidence_sources = [
            ConfidenceSource(name="marché régional", weight=0.5),
            ConfidenceSource(name="historique devis", weight=0.2),
            ConfidenceSource(name="analyse algorithmique", weight=0.3)
        ]
        
        # Ajuster les poids selon la qualité des données
        if request.market_stats.medianes:
            confidence_sources[0].weight = min(0.7, 0.3 + len(request.market_stats.medianes) * 0.1)
        
        if request.historique:
            confidence_sources[1].weight = min(0.3, len(request.historique) * 0.05)
        
        # Normaliser les poids
        total_weight = sum(s.weight for s in confidence_sources)
        for source in confidence_sources:
            source.weight = round(source.weight / total_weight, 2)
        
        # === ÉTAPE 4: Construction de la réponse ===
        response = ScoreResponse(
            score=score_result.score,
            delta_pct=score_result.delta_pct,
            risk_level=score_result.risk_level,
            justification=justification,
            actions_for_client=actions,
            confidence_sources=confidence_sources,
            requires_human_review=score_result.requires_human_review
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur de scoring: {str(e)}")


@app.post("/score/simple")
async def score_simple(devis: Dict[str, Any], market_stats: Dict[str, Any]):
    """
    Version simplifiée du scoring pour tests rapides.
    """
    try:
        secteur = devis.get("secteur", "generique")
        lignes = devis.get("lignes", [])
        
        score_result = scorer_devis(lignes, market_stats, secteur)
        
        return {
            "score": score_result.score,
            "delta_pct": score_result.delta_pct,
            "risk_level": score_result.risk_level,
            "requires_human_review": score_result.requires_human_review,
            "total_devis": score_result.total_devis,
            "total_marche": score_result.total_marche
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== POINT D'ENTRÉE ====================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
