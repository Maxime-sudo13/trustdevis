"""
Service FastAPI - Agent LeadFinder TrustDevis
API de détection et scoring de leads travaux/garagistes
"""

import os
import uuid
from typing import List, Optional, Dict
from datetime import datetime
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from models import (
    Lead, LeadFilter, LeadSearchRequest, LeadListResponse,
    LeadSource, LeadType, LeadQuality, LeadStatus,
    LeadScoreFactors
)
from scorer import LeadScorer
from sources import SourceManager


# Stockage en mémoire (remplacer par DB en production)
leads_db: Dict[str, Lead] = {}
source_manager: Optional[SourceManager] = None
scorer: Optional[LeadScorer] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestion du cycle de vie de l'application"""
    global source_manager, scorer
    
    # Startup
    print("🚀 Démarrage LeadFinder Service...")
    source_manager = SourceManager()
    scorer = LeadScorer()
    print(f"✅ Service prêt - {len(leads_db)} leads en mémoire")
    
    yield
    
    # Shutdown
    print("🛑 Arrêt du service...")
    if source_manager:
        await source_manager.close_all()


app = FastAPI(
    title="TrustDevis LeadFinder API",
    description="Service de détection et scoring de leads travaux",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # À restreindre en production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# ENDPOINTS API
# ============================================================================

@app.get("/")
async def root():
    """Point de contrôle santé"""
    return {
        "service": "TrustDevis LeadFinder",
        "version": "1.0.0",
        "status": "ok",
        "leads_count": len(leads_db)
    }


@app.get("/health")
async def health_check():
    """Health check détaillé"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "leads_total": len(leads_db),
        "sources_available": list(LeadSource),
        "scorer_ready": scorer is not None
    }


# ----------------------------------------------------------------------------
# Endpoints Leads
# ----------------------------------------------------------------------------

@app.post("/leads/search", response_model=LeadListResponse)
async def search_leads(request: LeadSearchRequest):
    """
    Recherche de leads selon critères.
    
    Cette endpoint permet de:
    - Chercher dans la base existante
    - Déclencher une recherche sur les sources externes
    """
    results = []
    
    # Filtrage sur la base existante
    for lead in leads_db.values():
        if _matches_filter(lead, request.filtres):
            results.append(lead)
    
    # Tri par score décroissant
    results.sort(key=lambda x: x.score, reverse=True)
    
    # Pagination
    total = len(results)
    offset = request.filtres.offset
    limit = request.filtres.limit
    paginated = results[offset:offset + limit]
    
    return LeadListResponse(
        total=total,
        limit=limit,
        offset=offset,
        leads=paginated
    )


@app.get("/leads", response_model=LeadListResponse)
async def list_leads(
    secteur: Optional[str] = None,
    region: Optional[str] = None,
    departement: Optional[str] = None,
    ville: Optional[str] = None,
    type_travaux: Optional[LeadType] = None,
    qualite: Optional[LeadQuality] = None,
    status: Optional[LeadStatus] = None,
    source: Optional[LeadSource] = None,
    budget_min: Optional[float] = None,
    budget_max: Optional[float] = None,
    score_min: Optional[int] = Query(None, ge=0, le=100),
    score_max: Optional[int] = Query(None, ge=0, le=100),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0)
):
    """
    Liste les leads avec filtres via query params.
    """
    filtres = LeadFilter(
        secteur=secteur,
        region=region,
        departement=departement,
        ville=ville,
        type_travaux=type_travaux,
        qualite=qualite,
        status=status,
        source=source,
        budget_min=budget_min,
        budget_max=budget_max,
        score_min=score_min,
        score_max=score_max,
        limit=limit,
        offset=offset
    )
    
    results = []
    for lead in leads_db.values():
        if _matches_filter(lead, filtres):
            results.append(lead)
    
    # Tri par score décroissant
    results.sort(key=lambda x: x.score, reverse=True)
    
    total = len(results)
    paginated = results[offset:offset + limit]
    
    return LeadListResponse(
        total=total,
        limit=limit,
        offset=offset,
        leads=paginated
    )


@app.get("/leads/{lead_id}", response_model=Lead)
async def get_lead(lead_id: str):
    """
    Récupère le détail d'un lead spécifique.
    """
    if lead_id not in leads_db:
        raise HTTPException(status_code=404, detail="Lead non trouvé")
    return leads_db[lead_id]


@app.post("/leads/{lead_id}/score")
async def rescore_lead(lead_id: str):
    """
    Recalcule le score d'un lead.
    """
    if lead_id not in leads_db:
        raise HTTPException(status_code=404, detail="Lead non trouvé")
    
    lead = leads_db[lead_id]
    scorer.update_lead_score(lead)
    
    return {
        "lead_id": lead_id,
        "new_score": lead.score,
        "new_quality": lead.qualite.value
    }


@app.get("/leads/{lead_id}/score-details", response_model=LeadScoreFactors)
async def get_score_details(lead_id: str):
    """
    Récupère le détail du scoring d'un lead.
    """
    if lead_id not in leads_db:
        raise HTTPException(status_code=404, detail="Lead non trouvé")
    
    lead = leads_db[lead_id]
    _, _, factors = scorer.score_lead(lead)
    return factors


# ----------------------------------------------------------------------------
# Endpoints Sources
# ----------------------------------------------------------------------------

@app.post("/sources/search")
async def search_sources(
    background_tasks: BackgroundTasks,
    sources: Optional[List[LeadSource]] = None,
    location: Optional[str] = None,
    code_postal: Optional[str] = None,
    departement: Optional[str] = None
):
    """
    Déclenche une recherche sur les sources externes.
    
    Cette opération peut être longue - s'exécute en arrière-plan.
    """
    # Pour l'instant, recherche synchrone
    results = await source_manager.search_all(
        sources=sources,
        location=location,
        code_postal=code_postal,
        departement=departement
    )
    
    # Score et sauvegarde des nouveaux leads
    new_leads_count = 0
    for source, leads in results.items():
        for lead in leads:
            if lead.id not in leads_db:
                scorer.update_lead_score(lead)
                leads_db[lead.id] = lead
                new_leads_count += 1
    
    return {
        "message": "Recherche terminée",
        "sources_searched": list(results.keys()),
        "new_leads_found": new_leads_count,
        "total_leads": len(leads_db)
    }


@app.get("/sources")
async def list_sources():
    """Liste les sources disponibles"""
    return {
        "sources": [
            {
                "id": source.value,
                "name": source.name,
                "status": "active" if source in source_manager.connectors else "inactive"
            }
            for source in LeadSource
        ]
    }


# ----------------------------------------------------------------------------
# Endpoints Admin (création manuelle, debug)
# ----------------------------------------------------------------------------

@app.post("/leads", response_model=Lead)
async def create_lead(lead: Lead):
    """
    Crée un lead manuellement (pour tests ou ajout manuel).
    """
    if not lead.id:
        lead.id = str(uuid.uuid4())[:12]
    
    # Score automatique
    scorer.update_lead_score(lead)
    
    leads_db[lead.id] = lead
    return lead


@app.delete("/leads/{lead_id}")
async def delete_lead(lead_id: str):
    """Supprime un lead"""
    if lead_id not in leads_db:
        raise HTTPException(status_code=404, detail="Lead non trouvé")
    
    del leads_db[lead_id]
    return {"message": "Lead supprimé", "lead_id": lead_id}


@app.get("/stats")
async def get_stats():
    """Statistiques des leads"""
    stats = {
        "total": len(leads_db),
        "by_quality": {"hot": 0, "warm": 0, "cold": 0},
        "by_source": {},
        "by_type": {},
        "by_status": {}
    }
    
    for lead in leads_db.values():
        stats["by_quality"][lead.qualite.value] += 1
        stats["by_source"][lead.source.value] = stats["by_source"].get(lead.source.value, 0) + 1
        stats["by_type"][lead.type_travaux.value] = stats["by_type"].get(lead.type_travaux.value, 0) + 1
        stats["by_status"][lead.status.value] = stats["by_status"].get(lead.status.value, 0) + 1
    
    return stats


# ============================================================================
# Fonctions utilitaires
# ============================================================================

def _matches_filter(lead: Lead, filtres: LeadFilter) -> bool:
    """Vérifie si un lead correspond aux filtres"""
    
    if filtres.secteur and filtres.secteur.lower() not in str(lead.sous_type or "").lower():
        return False
    
    if filtres.region and lead.localisation.region != filtres.region:
        return False
    
    if filtres.departement and lead.localisation.departement != filtres.departement:
        return False
    
    if filtres.ville and lead.localisation.ville != filtres.ville:
        return False
    
    if filtres.code_postal and lead.localisation.code_postal != filtres.code_postal:
        return False
    
    if filtres.type_travaux and lead.type_travaux != filtres.type_travaux:
        return False
    
    if filtres.qualite and lead.qualite != filtres.qualite:
        return False
    
    if filtres.status and lead.status != filtres.status:
        return False
    
    if filtres.source and lead.source != filtres.source:
        return False
    
    if filtres.budget_min and (lead.budget_estime is None or lead.budget_estime < filtres.budget_min):
        return False
    
    if filtres.budget_max and (lead.budget_estime is None or lead.budget_estime > filtres.budget_max):
        return False
    
    if filtres.score_min is not None and lead.score < filtres.score_min:
        return False
    
    if filtres.score_max is not None and lead.score > filtres.score_max:
        return False
    
    if filtres.date_from and lead.created_at < filtres.date_from:
        return False
    
    if filtres.date_to and lead.created_at > filtres.date_to:
        return False
    
    return True


# ============================================================================
# Point d'entrée
# ============================================================================

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    host = os.getenv("HOST", "0.0.0.0")
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=os.getenv("DEBUG", "false").lower() == "true"
    )
