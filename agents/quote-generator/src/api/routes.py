"""
Routes API FastAPI
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Optional

from src.models.quote import (
    QuoteRequest, QuoteResponse, EmailRequest, EmailResponse,
    ArtisanContactRequest, ArtisanContactResponse, GeneratedQuote
)
from src.services.quote_generator import QuoteGenerator
from src.services.email_service import EmailService
from src.services.comparison import QuoteComparisonService


router = APIRouter(prefix="/quote", tags=["quotes"])

# Services singletons
quote_generator = QuoteGenerator()
email_service = EmailService()
comparison_service = QuoteComparisonService()


@router.post("/generate", response_model=QuoteResponse)
async def generate_quote(request: QuoteRequest) -> QuoteResponse:
    """
    Génère un devis avec 3 variantes (économique, standard, premium)
    à partir de la description des travaux du client.
    """
    response = quote_generator.generate_quote(request)
    
    if not response.success:
        raise HTTPException(status_code=400, detail=response.message)
    
    return response


@router.get("/{quote_id}")
async def get_quote(quote_id: str) -> dict:
    """
    Récupère un devis généré par son ID.
    """
    quote = quote_generator.get_quote(quote_id)
    
    if not quote:
        raise HTTPException(status_code=404, detail="Devis non trouvé")
    
    return {
        "success": True,
        "quote": quote.model_dump()
    }


@router.post("/send-email", response_model=EmailResponse)
async def send_quote_email(request: EmailRequest) -> EmailResponse:
    """
    Envoie le devis par email au client.
    """
    quote = quote_generator.get_quote(request.quote_id)
    
    if not quote:
        raise HTTPException(status_code=404, detail="Devis non trouvé")
    
    return email_service.send_quote_email(request, quote)


@router.post("/contact-artisans")
async def contact_artisans(request: ArtisanContactRequest) -> dict:
    """
    Demande de mise en relation avec des artisans.
    """
    quote = quote_generator.get_quote(request.quote_id)
    
    if not quote:
        raise HTTPException(status_code=404, detail="Devis non trouvé")
    
    # Simuler la demande de contact
    return {
        "success": True,
        "message": f"Demande de contact enregistrée pour {request.contact_name}",
        "request_id": f"REQ-{request.quote_id}",
        "estimated_response_time": "24 à 48 heures ouvrées",
        "details": {
            "quote_id": request.quote_id,
            "levels_requested": [level.value for level in request.preferred_levels],
            "contact_method": request.preferred_contact_method
        }
    }


@router.get("/{quote_id}/comparison")
async def get_comparison(quote_id: str) -> dict:
    """
    Récupère le tableau comparatif des 3 devis.
    """
    quote = quote_generator.get_quote(quote_id)
    
    if not quote:
        raise HTTPException(status_code=404, detail="Devis non trouvé")
    
    return {
        "success": True,
        "comparison_table": comparison_service.generate_comparison_table(quote),
        "explanations": comparison_service.explain_differences(quote),
        "recommendation": comparison_service.get_personalized_recommendation(quote)
    }


@router.get("/{quote_id}/distribution")
async def get_price_distribution(quote_id: str) -> dict:
    """
    Récupère la répartition des prix pour graphiques.
    """
    quote = quote_generator.get_quote(quote_id)
    
    if not quote:
        raise HTTPException(status_code=404, detail="Devis non trouvé")
    
    return {
        "success": True,
        "distributions": {
            level.value: dist.model_dump() 
            for level, dist in quote.price_distribution.items()
        }
    }


@router.post("/{quote_id}/analyze")
async def analyze_received_quote(
    quote_id: str,
    received_amount: float,
    details: Optional[str] = None
) -> dict:
    """
    Analyse un devis reçu par rapport à notre estimation.
    """
    analysis = quote_generator.analyze_existing_quote(quote_id, received_amount, details)
    
    if "error" in analysis:
        raise HTTPException(status_code=404, detail=analysis["error"])
    
    return {
        "success": True,
        "analysis": analysis
    }


@router.get("/work-types/list")
async def list_work_types() -> dict:
    """
    Liste les types de travaux supportés.
    """
    from src.models.quote import WorkType
    
    return {
        "success": True,
        "work_types": [
            {"value": wt.value, "label": wt.value.replace("_", " ").title()}
            for wt in WorkType
        ]
    }


@router.get("/material-levels/list")
async def list_material_levels() -> dict:
    """
    Liste les niveaux de matériaux disponibles.
    """
    from src.models.quote import MaterialLevel
    
    return {
        "success": True,
        "material_levels": [
            {"value": ml.value, "label": ml.value.replace("_", " ").title()}
            for ml in MaterialLevel
        ]
    }
