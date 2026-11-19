import os
import logging
from datetime import datetime
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request, Header
from fastapi.responses import JSONResponse

from models import (
    SubscribeRequest, SubscribeResponse,
    CancelRequest, CancelResponse,
    InvoiceListResponse,
    PlansResponse, WebhookResponse,
    HealthResponse, Subscription
)
from plans import get_all_plans, get_plan
from stripe_integration import stripe_integration, StripeError
from webhook_handlers import webhook_handler

# Configuration logging
logging.basicConfig(
    level=getattr(logging, os.environ.get("LOG_LEVEL", "INFO").upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestionnaire de cycle de vie de l'application"""
    logger.info("🚀 Démarrage du service Billing TrustDevis")
    
    # Vérifier la configuration Stripe
    if not os.environ.get("STRIPE_SECRET_KEY"):
        logger.warning("⚠️ STRIPE_SECRET_KEY non configurée - le service fonctionnera en mode dégradé")
    
    yield
    
    logger.info("🛑 Arrêt du service Billing TrustDevis")


# Création de l'application FastAPI
app = FastAPI(
    title="TrustDevis Billing API",
    description="API de gestion des abonnements et paiements via Stripe",
    version="1.0.0",
    lifespan=lifespan
)


# ==========================================
# Endpoints Health & Info
# ==========================================

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check du service"""
    return HealthResponse(
        status="healthy",
        service="trustdevis-billing"
    )


@app.get("/")
async def root():
    """Page d'accueil"""
    return {
        "service": "TrustDevis Billing API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }


# ==========================================
# Endpoints Plans
# ==========================================

@app.get("/billing/plans", response_model=PlansResponse)
async def list_plans():
    """
    Liste tous les plans d'abonnement disponibles.
    
    Returns:
        Liste des plans avec leurs caractéristiques
    """
    plans = get_all_plans()
    return PlansResponse(plans=plans)


# ==========================================
# Endpoints Souscriptions
# ==========================================

@app.post("/billing/subscribe", response_model=SubscribeResponse)
async def subscribe(request: SubscribeRequest):
    """
    Crée un nouvel abonnement.
    
    Crée une session de checkout Stripe et retourne l'URL
    pour rediriger l'utilisateur vers le paiement.
    
    Args:
        request: Informations de souscription
        
    Returns:
        URL de checkout et IDs de session/abonnement
    """
    logger.info(f"Demande d'abonnement: user={request.user_id}, plan={request.plan_id}")
    
    # Vérifier le plan
    plan = get_plan(request.plan_id)
    if not plan:
        raise HTTPException(status_code=400, detail=f"Plan inconnu: {request.plan_id}")
    
    try:
        # Créer la session de checkout
        session = stripe_integration.create_checkout_session(
            user_id=request.user_id,
            plan=plan,
            success_url=request.success_url,
            cancel_url=request.cancel_url,
            customer_email=request.customer_email
        )
        
        # Générer un ID d'abonnement local
        subscription_id = f"sub_pending_{session.id}"
        
        return SubscribeResponse(
            checkout_url=session.url,
            session_id=session.id,
            subscription_id=subscription_id
        )
        
    except StripeError as e:
        logger.error(f"Erreur Stripe lors de la souscription: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Erreur inattendue lors de la souscription: {e}")
        raise HTTPException(status_code=500, detail="Erreur interne")


@app.post("/billing/cancel", response_model=CancelResponse)
async def cancel_subscription(request: CancelRequest):
    """
    Annule un abonnement existant.
    
    Args:
        request: Informations d'annulation
        
    Returns:
        Confirmation de l'annulation
    """
    logger.info(f"Demande d'annulation: subscription={request.subscription_id}, user={request.user_id}")
    
    try:
        subscription = webhook_handler.cancel_subscription(
            subscription_id=request.subscription_id,
            user_id=request.user_id,
            immediate=request.immediate
        )
        
        if not subscription:
            raise HTTPException(
                status_code=404, 
                detail="Abonnement non trouvé ou accès non autorisé"
            )
        
        message = (
            "Abonnement annulé immédiatement" 
            if request.immediate 
            else "Abonnement annulé (fin de période en cours)"
        )
        
        return CancelResponse(
            success=True,
            message=message,
            subscription=subscription
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de l'annulation: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de l'annulation")


# ==========================================
# Endpoints Factures
# ==========================================

@app.get("/billing/invoice", response_model=InvoiceListResponse)
async def list_invoices(user_id: str):
    """
    Liste les factures d'un utilisateur.
    
    Args:
        user_id: ID de l'utilisateur
        
    Returns:
        Liste des factures
    """
    logger.info(f"Récupération des factures pour user={user_id}")
    
    invoices = webhook_handler.get_user_invoices(user_id)
    
    return InvoiceListResponse(
        user_id=user_id,
        invoices=invoices,
        total=len(invoices)
    )


# ==========================================
# Endpoints Webhook Stripe
# ==========================================

@app.post("/billing/webhook", response_model=WebhookResponse)
async def stripe_webhook(
    request: Request,
    stripe_signature: str = Header(None, alias="Stripe-Signature")
):
    """
    Endpoint webhook pour recevoir les événements Stripe.
    
    Gère automatiquement:
    - checkout.session.completed
    - invoice.paid
    - invoice.payment_failed
    - customer.subscription.updated
    - customer.subscription.deleted
    
    Args:
        request: Requête webhook
        stripe_signature: Signature Stripe pour vérification
        
    Returns:
        Confirmation de traitement
    """
    webhook_secret = os.environ.get("STRIPE_WEBHOOK_SECRET")
    
    if not webhook_secret:
        logger.error("STRIPE_WEBHOOK_SECRET non configuré")
        raise HTTPException(status_code=500, detail="Configuration webhook manquante")
    
    if not stripe_signature:
        logger.error("Signature Stripe manquante")
        raise HTTPException(status_code=400, detail="Signature manquante")
    
    # Lire le payload
    payload = await request.body()
    
    try:
        # Vérifier et construire l'événement
        event = stripe_integration.construct_webhook_event(
            payload=payload,
            sig_header=stripe_signature,
            webhook_secret=webhook_secret
        )
        
        # Traiter l'événement
        result = webhook_handler.handle_event(event)
        
        return WebhookResponse(
            status=result.get("status", "processed"),
            event_type=result.get("event_type"),
            message=result.get("action")
        )
        
    except StripeError as e:
        logger.error(f"Erreur webhook Stripe: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Erreur traitement webhook: {e}")
        raise HTTPException(status_code=500, detail="Erreur interne")


# ==========================================
# Endpoints Utilitaires (pour debug/admin)
# ==========================================

@app.get("/billing/subscription/{subscription_id}")
async def get_subscription(subscription_id: str):
    """
    Récupère les détails d'un abonnement.
    
    Args:
        subscription_id: ID de l'abonnement
        
    Returns:
        Détails de l'abonnement
    """
    subscription = webhook_handler.get_subscription(subscription_id)
    
    if not subscription:
        raise HTTPException(status_code=404, detail="Abonnement non trouvé")
    
    return subscription


@app.get("/billing/user/{user_id}/subscription")
async def get_user_subscription(user_id: str):
    """
    Récupère l'abonnement actif d'un utilisateur.
    
    Args:
        user_id: ID de l'utilisateur
        
    Returns:
        Abonnement de l'utilisateur ou 404
    """
    subscription = webhook_handler.get_user_subscription(user_id)
    
    if not subscription:
        raise HTTPException(status_code=404, detail="Aucun abonnement trouvé pour cet utilisateur")
    
    return subscription


# ==========================================
# Gestion des erreurs
# ==========================================

@app.exception_handler(StripeError)
async def stripe_error_handler(request: Request, exc: StripeError):
    """Gestionnaire d'erreurs Stripe"""
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc)}
    )


if __name__ == "__main__":
    import uvicorn
    
    port = int(os.environ.get("API_PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
