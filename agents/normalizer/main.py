"""
Service FastAPI - Agent Normalizer TrustDevis
=============================================
Endpoint POST /normalize pour classifier les lignes de devis
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uvicorn

from normalizer import normalize_lines, batch_normalize
from categories import ALL_CATEGORIES, get_categories_by_sector


app = FastAPI(
    title="TrustDevis Normalizer",
    description="Service de classification des lignes de devis",
    version="1.0.0"
)


class NormalizeRequest(BaseModel):
    """Requête de normalisation"""
    lines: List[str]
    sector: Optional[str] = None  # 'building', 'mechanic', ou None (auto)


class NormalizedLine(BaseModel):
    """Ligne normalisée"""
    orig_line: str
    category: str
    unit: str
    qty: Optional[float]
    normalized_desc: str
    confidence: float
    category_name: str


class NormalizeResponse(BaseModel):
    """Réponse de normalisation"""
    results: List[NormalizedLine]
    stats: Dict[str, Any]


class CategoriesResponse(BaseModel):
    """Réponse liste des catégories"""
    categories: Dict[str, Dict]
    count: int


@app.get("/")
async def root():
    """Health check"""
    return {
        "service": "TrustDevis Normalizer",
        "status": "ok",
        "version": "1.0.0"
    }


@app.get("/health")
async def health():
    """Health check détaillé"""
    return {
        "status": "healthy",
        "categories_loaded": len(ALL_CATEGORIES),
        "sectors": ["building", "mechanic"]
    }


@app.post("/normalize", response_model=NormalizeResponse)
async def normalize(request: NormalizeRequest):
    """
    Normalise une liste de lignes de devis
    
    - **lines**: Liste de lignes brutes OCR
    - **sector**: Secteur optionnel ('building' ou 'mechanic')
    
    Retourne les lignes classifiées avec catégorie, unité et confiance
    """
    if not request.lines:
        raise HTTPException(status_code=400, detail="Aucune ligne fournie")
    
    try:
        result = batch_normalize(request.lines, request.sector)
        
        # Conversion en modèles Pydantic
        normalized_lines = [
            NormalizedLine(
                orig_line=r["orig_line"],
                category=r["category"],
                unit=r["unit"],
                qty=r["qty"],
                normalized_desc=r["normalized_desc"],
                confidence=r["confidence"],
                category_name=r["category_name"]
            )
            for r in result["results"]
        ]
        
        return NormalizeResponse(
            results=normalized_lines,
            stats=result["stats"]
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur de normalisation: {str(e)}")


@app.get("/categories", response_model=CategoriesResponse)
async def list_categories(sector: Optional[str] = None):
    """
    Liste toutes les catégories disponibles
    
    - **sector**: Filtre par secteur ('building' ou 'mechanic')
    """
    categories = get_categories_by_sector(sector) if sector else ALL_CATEGORIES
    
    return CategoriesResponse(
        categories=categories,
        count=len(categories)
    )


@app.get("/categories/{category_id}")
async def get_category(category_id: str):
    """Détail d'une catégorie spécifique"""
    if category_id not in ALL_CATEGORIES:
        raise HTTPException(status_code=404, detail="Catégorie non trouvée")
    
    return {
        "id": category_id,
        **ALL_CATEGORIES[category_id]
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
