from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session

from database import (
    get_db, init_db, get_region, get_prices_by_category_region,
    add_price, get_categories, get_regions, get_global_stats
)
from calculator import PricingCalculator
from seed_data import main as seed_main

app = FastAPI(
    title="TrustDevis Pricing Engine",
    description="Service de calcul des prix médians du marché par catégorie et région",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============== MODÈLES Pydantic ==============

class PriceIngestRequest(BaseModel):
    category: str = Field(..., description="Catégorie du service (ex: peinture, freins)")
    region_code: str = Field(..., description="Code région (ex: IDF, PACA)")
    price: float = Field(..., gt=0, description="Prix du service")
    unit: str = Field(..., description="Unité: m², heure, forfait, unite")
    source: Optional[str] = Field(None, description="Source du prix (artisan_X, dataset_Y)")


class PriceIngestResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None


class PricingStatsResponse(BaseModel):
    category: str
    region_code: str
    region_name: str
    unit: str
    count: int
    median: float
    percentile_25: float
    percentile_75: float
    percentile_90: float
    min: float
    max: float
    labor_coefficient: float
    median_adjusted: Optional[float] = None


class GlobalStatsResponse(BaseModel):
    total_prices: int
    total_categories: int
    total_regions: int
    last_update: Optional[str]
    categories: Dict[str, int]
    regions: Dict[str, int]


class QuoteEvaluationRequest(BaseModel):
    quote_price: float = Field(..., gt=0, description="Prix du devis à évaluer")
    category: str = Field(..., description="Catégorie du service")
    region_code: str = Field(..., description="Code région")


class QuoteEvaluationResponse(BaseModel):
    category: str
    region_code: str
    market_stats: Dict[str, Any]
    evaluation: Dict[str, Any]
    recommendation: str


# ============== ENDPOINTS ==============

@app.on_event("startup")
async def startup_event():
    """Initialise la base de données au démarrage"""
    init_db()
    seed_main()


@app.get("/")
async def root():
    """Endpoint racine"""
    return {
        "service": "TrustDevis Pricing Engine",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": [
            "GET /pricing/{category}/{region_code}",
            "POST /pricing/ingest",
            "GET /pricing/stats",
            "POST /pricing/evaluate"
        ]
    }


@app.get("/pricing/{category}/{region_code}", response_model=PricingStatsResponse)
async def get_pricing_stats(
    category: str,
    region_code: str,
    db: Session = Depends(get_db)
):
    """
    Retourne les statistiques de prix pour une catégorie et une région.
    
    - **category**: Catégorie de service (peinture, plomberie, freins...)
    - **region_code**: Code région (IDF, PACA, ARA, NAQ...)
    """
    # Récupère la région
    region = get_region(db, region_code)
    if not region:
        raise HTTPException(status_code=404, detail=f"Région '{region_code}' non trouvée")
    
    # Récupère les prix
    prices = get_prices_by_category_region(db, category, region_code)
    if not prices:
        raise HTTPException(
            status_code=404, 
            detail=f"Aucune donnée pour la catégorie '{category}' en région '{region_code}'"
        )
    
    price_values = [p.price for p in prices]
    unit = prices[0].unit  # On prend l'unité du premier prix
    
    # Calcule les statistiques
    calculator = PricingCalculator()
    stats = calculator.get_price_range_for_category(price_values, region)
    
    return PricingStatsResponse(
        category=category,
        region_code=region_code.upper(),
        region_name=region.name,
        unit=unit,
        count=stats["count"],
        median=stats["median"],
        percentile_25=stats["percentile_25"],
        percentile_75=stats["percentile_75"],
        percentile_90=stats["percentile_90"],
        min=stats["min"],
        max=stats["max"],
        labor_coefficient=region.labor_coefficient,
        median_adjusted=stats.get("median_adjusted")
    )


@app.post("/pricing/ingest", response_model=PriceIngestResponse)
async def ingest_price(request: PriceIngestRequest, db: Session = Depends(get_db)):
    """
    Ajoute un nouveau prix au dataset.
    
    Permet d'enrichir la base de données avec de nouveaux prix du marché.
    """
    try:
        # Vérifie que la région existe
        region = get_region(db, request.region_code)
        if not region:
            return PriceIngestResponse(
                success=False,
                message=f"Région '{request.region_code}' non trouvée. Codes valides: IDF, PACA, ARA, NAQ, OCC, HDF, BRE, PDL, NOR, GES, CVL, BFC"
            )
        
        # Ajoute le prix
        new_price = add_price(
            db=db,
            category=request.category,
            region_code=request.region_code,
            price=request.price,
            unit=request.unit,
            source=request.source or "api_ingest"
        )
        
        return PriceIngestResponse(
            success=True,
            message="Prix ajouté avec succès",
            data={
                "id": new_price.id,
                "category": new_price.category,
                "region_code": new_price.region_code,
                "price": new_price.price,
                "unit": new_price.unit,
                "created_at": new_price.created_at.isoformat()
            }
        )
        
    except Exception as e:
        return PriceIngestResponse(
            success=False,
            message=f"Erreur lors de l'ajout: {str(e)}"
        )


@app.get("/pricing/stats", response_model=GlobalStatsResponse)
async def get_global_statistics(db: Session = Depends(get_db)):
    """
    Retourne les statistiques globales de la base de données.
    
    Inclut le nombre total de prix, de catégories, de régions,
    ainsi que la répartition par catégorie et par région.
    """
    stats = get_global_stats(db)
    return GlobalStatsResponse(**stats)


@app.post("/pricing/evaluate", response_model=QuoteEvaluationResponse)
async def evaluate_quote(request: QuoteEvaluationRequest, db: Session = Depends(get_db)):
    """
    Évalue un devis par rapport au marché.
    
    Compare un prix soumis avec le prix médian du marché pour la même
    catégorie et région, et fournit une recommandation.
    """
    calculator = PricingCalculator()
    result = calculator.evaluate_quote(
        quote_price=request.quote_price,
        category=request.category,
        region_code=request.region_code,
        db=db
    )
    
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    
    return QuoteEvaluationResponse(**result)


@app.get("/categories")
async def list_categories(db: Session = Depends(get_db)):
    """Liste toutes les catégories disponibles"""
    categories = get_categories(db)
    return {"categories": categories}


@app.get("/regions")
async def list_regions(db: Session = Depends(get_db)):
    """Liste toutes les régions avec leurs coefficients"""
    regions = get_regions(db)
    return {
        "regions": [
            {
                "code": r.code,
                "name": r.name,
                "labor_coefficient": r.labor_coefficient
            }
            for r in regions
        ]
    }


# ============== POINT D'ENTRÉE ==============

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
