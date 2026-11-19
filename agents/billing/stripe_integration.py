import os
import logging
from datetime import datetime
from typing import Optional

import stripe

from models import (
    Subscription, 
    SubscriptionStatus, 
    Invoice, 
    InvoiceStatus,
    Plan
)
from plans import get_plan, get_plan_by_stripe_price

logger = logging.getLogger(__name__)

# Configuration Stripe
stripe.api_key = os.environ.get("STRIPE_SECRET_KEY", "")


class StripeError(Exception):
    """Exception personnalisée pour les erreurs Stripe"""
    pass


class StripeIntegration:
    """Classe d'intégration avec Stripe"""
    
    def __init__(self):
        self.api_key = os.environ.get("STRIPE_SECRET_KEY", "")
        if not self.api_key:
            logger.warning("STRIPE_SECRET_KEY non configurée")
        stripe.api_key = self.api_key
    
    def create_checkout_session(
        self,
        user_id: str,
        plan: Plan,
        success_url: str,
        cancel_url: str,
        customer_email: Optional[str] = None
    ) -> dict:
        """
        Crée une session de checkout Stripe.
        
        Args:
            user_id: ID de l'utilisateur
            plan: Plan choisi
            success_url: URL de redirection après succès
            cancel_url: URL de redirection après annulation
            customer_email: Email du client (optionnel)
            
        Returns:
            Session Stripe créée
            
        Raises:
            StripeError: Si la création échoue
        """
        try:
            # Préparer les métadonnées
            metadata = {
                "user_id": user_id,
                "plan_id": plan.id,
                "plan_tier": plan.tier.value
            }
            
            # Construire les paramètres de la session
            session_params = {
                "payment_method_types": ["card"],
                "line_items": [{
                    "price_data": {
                        "currency": plan.currency,
                        "product_data": {
                            "name": f"TrustDevis {plan.name}",
                            "description": plan.description,
                        },
                        "unit_amount": plan.price_cents,
                        "recurring": {
                            "interval": plan.interval
                        }
                    },
                    "quantity": 1,
                }],
                "mode": "subscription",
                "success_url": success_url,
                "cancel_url": cancel_url,
                "metadata": metadata,
                "subscription_data": {
                    "metadata": metadata
                }
            }
            
            # Ajouter l'email si fourni
            if customer_email:
                session_params["customer_email"] = customer_email
            
            # Créer la session
            session = stripe.checkout.Session.create(**session_params)
            
            logger.info(f"Session checkout créée: {session.id} pour user {user_id}")
            return session
            
        except stripe.error.StripeError as e:
            logger.error(f"Erreur Stripe création checkout: {e}")
            raise StripeError(f"Erreur création checkout: {str(e)}")
    
    def get_subscription(self, stripe_subscription_id: str) -> dict:
        """
        Récupère un abonnement Stripe.
        
        Args:
            stripe_subscription_id: ID de l'abonnement Stripe
            
        Returns:
            Abonnement Stripe
            
        Raises:
            StripeError: Si la récupération échoue
        """
        try:
            subscription = stripe.Subscription.retrieve(stripe_subscription_id)
            return subscription
        except stripe.error.StripeError as e:
            logger.error(f"Erreur récupération subscription {stripe_subscription_id}: {e}")
            raise StripeError(f"Erreur récupération subscription: {str(e)}")
    
    def cancel_subscription(
        self, 
        stripe_subscription_id: str, 
        immediate: bool = False
    ) -> dict:
        """
        Annule un abonnement Stripe.
        
        Args:
            stripe_subscription_id: ID de l'abonnement Stripe
            immediate: Si True, annule immédiatement. Sinon, à la fin de la période.
            
        Returns:
            Abonnement Stripe mis à jour
            
        Raises:
            StripeError: Si l'annulation échoue
        """
        try:
            if immediate:
                # Annulation immédiate
                subscription = stripe.Subscription.delete(stripe_subscription_id)
                logger.info(f"Subscription {stripe_subscription_id} annulée immédiatement")
            else:
                # Annulation à la fin de la période
                subscription = stripe.Subscription.modify(
                    stripe_subscription_id,
                    cancel_at_period_end=True
                )
                logger.info(f"Subscription {stripe_subscription_id} annulée à la fin de période")
            
            return subscription
            
        except stripe.error.StripeError as e:
            logger.error(f"Erreur annulation subscription {stripe_subscription_id}: {e}")
            raise StripeError(f"Erreur annulation subscription: {str(e)}")
    
    def get_customer_invoices(self, stripe_customer_id: str, limit: int = 10) -> list:
        """
        Récupère les factures d'un client.
        
        Args:
            stripe_customer_id: ID du client Stripe
            limit: Nombre maximum de factures
            
        Returns:
            Liste des factures Stripe
            
        Raises:
            StripeError: Si la récupération échoue
        """
        try:
            invoices = stripe.Invoice.list(
                customer=stripe_customer_id,
                limit=limit
            )
            return invoices.data
        except stripe.error.StripeError as e:
            logger.error(f"Erreur récupération factures client {stripe_customer_id}: {e}")
            raise StripeError(f"Erreur récupération factures: {str(e)}")
    
    def construct_webhook_event(
        self, 
        payload: bytes, 
        sig_header: str,
        webhook_secret: str
    ) -> stripe.Event:
        """
        Construit un événement webhook Stripe.
        
        Args:
            payload: Corps de la requête
            sig_header: Header Stripe-Signature
            webhook_secret: Secret du webhook
            
        Returns:
            Événement Stripe
            
        Raises:
            StripeError: Si la vérification échoue
        """
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, webhook_secret
            )
            return event
        except stripe.error.SignatureVerificationError as e:
            logger.error(f"Erreur vérification signature webhook: {e}")
            raise StripeError("Signature webhook invalide")
        except Exception as e:
            logger.error(f"Erreur construction événement webhook: {e}")
            raise StripeError(f"Erreur webhook: {str(e)}")
    
    def create_customer_portal_session(
        self,
        stripe_customer_id: str,
        return_url: str
    ) -> dict:
        """
        Crée une session de portail client Stripe.
        
        Args:
            stripe_customer_id: ID du client Stripe
            return_url: URL de retour après gestion
            
        Returns:
            Session du portail client
            
        Raises:
            StripeError: Si la création échoue
        """
        try:
            session = stripe.billing_portal.Session.create(
                customer=stripe_customer_id,
                return_url=return_url
            )
            return session
        except stripe.error.StripeError as e:
            logger.error(f"Erreur création portail client: {e}")
            raise StripeError(f"Erreur création portail: {str(e)}")
    
    def create_product_and_price(self, plan: Plan) -> tuple[str, str]:
        """
        Crée un produit et un prix dans Stripe pour un plan.
        À utiliser pour l'initialisation des plans.
        
        Args:
            plan: Plan à créer
            
        Returns:
            Tuple (product_id, price_id)
            
        Raises:
            StripeError: Si la création échoue
        """
        try:
            # Créer le produit
            product = stripe.Product.create(
                name=f"TrustDevis {plan.name}",
                description=plan.description,
                metadata={
                    "plan_id": plan.id,
                    "plan_tier": plan.tier.value,
                    "analysis_limit": str(plan.analysis_limit)
                }
            )
            
            # Créer le prix
            price = stripe.Price.create(
                product=product.id,
                unit_amount=plan.price_cents,
                currency=plan.currency,
                recurring={"interval": plan.interval}
            )
            
            logger.info(f"Produit et prix créés pour {plan.name}: {product.id}, {price.id}")
            return product.id, price.id
            
        except stripe.error.StripeError as e:
            logger.error(f"Erreur création produit/prix pour {plan.name}: {e}")
            raise StripeError(f"Erreur création produit: {str(e)}")


# Instance singleton
stripe_integration = StripeIntegration()


# Fonctions utilitaires

def stripe_subscription_to_model(
    stripe_sub: dict,
    user_id: str,
    plan_id: str
) -> Subscription:
    """
    Convertit un abonnement Stripe en modèle Subscription.
    
    Args:
        stripe_sub: Abonnement Stripe
        user_id: ID de l'utilisateur
        plan_id: ID du plan
        
    Returns:
        Modèle Subscription
    """
    return Subscription(
        id=f"sub_{stripe_sub.id}",
        user_id=user_id,
        plan_id=plan_id,
        stripe_subscription_id=stripe_sub.id,
        stripe_customer_id=stripe_sub.get("customer"),
        status=SubscriptionStatus(stripe_sub.status),
        current_period_start=datetime.fromtimestamp(stripe_sub.current_period_start) if stripe_sub.current_period_start else None,
        current_period_end=datetime.fromtimestamp(stripe_sub.current_period_end) if stripe_sub.current_period_end else None,
        cancel_at_period_end=stripe_sub.cancel_at_period_end,
        canceled_at=datetime.fromtimestamp(stripe_sub.canceled_at) if stripe_sub.canceled_at else None
    )


def stripe_invoice_to_model(
    stripe_invoice: dict,
    user_id: str,
    subscription_id: Optional[str] = None
) -> Invoice:
    """
    Convertit une facture Stripe en modèle Invoice.
    
    Args:
        stripe_invoice: Facture Stripe
        user_id: ID de l'utilisateur
        subscription_id: ID de l'abonnement local
        
    Returns:
        Modèle Invoice
    """
    return Invoice(
        id=f"inv_{stripe_invoice.id}",
        user_id=user_id,
        subscription_id=subscription_id,
        stripe_invoice_id=stripe_invoice.id,
        stripe_payment_intent_id=stripe_invoice.get("payment_intent"),
        amount_due_cents=stripe_invoice.amount_due,
        amount_paid_cents=stripe_invoice.amount_paid,
        currency=stripe_invoice.currency,
        status=InvoiceStatus(stripe_invoice.status),
        description=stripe_invoice.get("description") or stripe_invoice.get("lines", {}).get("data", [{}])[0].get("description"),
        pdf_url=stripe_invoice.get("invoice_pdf"),
        hosted_invoice_url=stripe_invoice.get("hosted_invoice_url"),
        period_start=datetime.fromtimestamp(stripe_invoice.period_start) if stripe_invoice.period_start else None,
        period_end=datetime.fromtimestamp(stripe_invoice.period_end) if stripe_invoice.period_end else None,
        paid_at=datetime.fromtimestamp(stripe_invoice.status_transitions.paid_at) if stripe_invoice.status_transitions and stripe_invoice.status_transitions.paid_at else None
    )
