from datetime import datetime
from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field


class SubscriptionStatus(str, Enum):
    """Statuts possibles d'un abonnement"""
    ACTIVE = "active"
    CANCELED = "canceled"
    INCOMPLETE = "incomplete"
    INCOMPLETE_EXPIRED = "incomplete_expired"
    PAST_DUE = "past_due"
    TRIALING = "trialing"
    UNPAID = "unpaid"
    PAUSED = "paused"


class PlanTier(str, Enum):
    """Niveaux de plans disponibles"""
    STARTER = "starter"
    PRO = "pro"
    ENTERPRISE = "enterprise"


class Plan(BaseModel):
    """Modèle d'un plan tarifaire"""
    id: str
    name: str
    tier: PlanTier
    price_cents: int
    price_euros: float
    currency: str = "eur"
    interval: str = "month"
    description: str
    features: List[str]
    analysis_limit: int
    stripe_price_id: Optional[str] = None
    stripe_product_id: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "pro",
                "name": "PRO",
                "tier": "pro",
                "price_cents": 7900,
                "price_euros": 79.0,
                "currency": "eur",
                "interval": "month",
                "description": "Pour les professionnels",
                "features": ["200 analyses/mois", "Support prioritaire", "API access"],
                "analysis_limit": 200
            }
        }


class Subscription(BaseModel):
    """Modèle d'un abonnement"""
    id: str = Field(..., description="ID de l'abonnement")
    user_id: str = Field(..., description="ID de l'utilisateur")
    plan_id: str = Field(..., description="ID du plan")
    stripe_subscription_id: Optional[str] = Field(None, description="ID Stripe de l'abonnement")
    stripe_customer_id: Optional[str] = Field(None, description="ID Stripe du client")
    status: SubscriptionStatus = SubscriptionStatus.INCOMPLETE
    current_period_start: Optional[datetime] = None
    current_period_end: Optional[datetime] = None
    cancel_at_period_end: bool = False
    canceled_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "sub_123",
                "user_id": "user_456",
                "plan_id": "pro",
                "stripe_subscription_id": "sub_stripe_xxx",
                "stripe_customer_id": "cus_stripe_xxx",
                "status": "active",
                "cancel_at_period_end": False,
                "created_at": "2025-01-01T00:00:00"
            }
        }


class InvoiceStatus(str, Enum):
    """Statuts possibles d'une facture"""
    DRAFT = "draft"
    OPEN = "open"
    PAID = "paid"
    UNCOLLECTIBLE = "uncollectible"
    VOID = "void"


class Invoice(BaseModel):
    """Modèle d'une facture"""
    id: str
    user_id: str
    subscription_id: Optional[str] = None
    stripe_invoice_id: Optional[str] = None
    stripe_payment_intent_id: Optional[str] = None
    amount_due_cents: int
    amount_paid_cents: int
    currency: str = "eur"
    status: InvoiceStatus
    description: Optional[str] = None
    pdf_url: Optional[str] = None
    hosted_invoice_url: Optional[str] = None
    period_start: Optional[datetime] = None
    period_end: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    paid_at: Optional[datetime] = None
    
    @property
    def amount_due_euros(self) -> float:
        return self.amount_due_cents / 100
    
    @property
    def amount_paid_euros(self) -> float:
        return self.amount_paid_cents / 100
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "inv_123",
                "user_id": "user_456",
                "amount_due_cents": 7900,
                "amount_paid_cents": 7900,
                "currency": "eur",
                "status": "paid",
                "description": "Abonnement PRO - Janvier 2025"
            }
        }


# Modèles de requête/réponse

class SubscribeRequest(BaseModel):
    """Requête de création d'abonnement"""
    user_id: str = Field(..., description="ID de l'utilisateur")
    plan_id: str = Field(..., description="ID du plan (starter, pro, enterprise)")
    success_url: str = Field(..., description="URL de redirection après succès")
    cancel_url: str = Field(..., description="URL de redirection après annulation")
    customer_email: Optional[str] = Field(None, description="Email du client (optionnel)")


class SubscribeResponse(BaseModel):
    """Réponse de création d'abonnement"""
    checkout_url: str = Field(..., description="URL du checkout Stripe")
    session_id: str = Field(..., description="ID de la session Stripe")
    subscription_id: str = Field(..., description="ID de l'abonnement local")


class CancelRequest(BaseModel):
    """Requête d'annulation d'abonnement"""
    subscription_id: str = Field(..., description="ID de l'abonnement")
    user_id: str = Field(..., description="ID de l'utilisateur")
    immediate: bool = Field(False, description="Annuler immédiatement ou à la fin de la période")


class CancelResponse(BaseModel):
    """Réponse d'annulation d'abonnement"""
    success: bool
    message: str
    subscription: Optional[Subscription] = None


class InvoiceListResponse(BaseModel):
    """Réponse de liste des factures"""
    user_id: str
    invoices: List[Invoice]
    total: int


class PlansResponse(BaseModel):
    """Réponse de liste des plans"""
    plans: List[Plan]


class WebhookResponse(BaseModel):
    """Réponse de webhook"""
    status: str
    event_type: Optional[str] = None
    message: Optional[str] = None


class HealthResponse(BaseModel):
    """Réponse health check"""
    status: str
    service: str
    version: str = "1.0.0"
    timestamp: datetime = Field(default_factory=datetime.utcnow)
