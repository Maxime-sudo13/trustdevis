import logging
from datetime import datetime
from typing import Optional

from models import (
    Subscription, 
    SubscriptionStatus, 
    Invoice, 
    InvoiceStatus
)
from stripe_integration import stripe_integration, stripe_subscription_to_model, stripe_invoice_to_model

logger = logging.getLogger(__name__)


class WebhookHandler:
    """Gestionnaire des événements webhook Stripe"""
    
    def __init__(self):
        # Stockage en mémoire (à remplacer par une vraie base de données)
        self.subscriptions: dict[str, Subscription] = {}
        self.invoices: dict[str, Invoice] = {}
        self.users_subscriptions: dict[str, str] = {}  # user_id -> subscription_id
    
    def handle_event(self, event: dict) -> dict:
        """
        Gère un événement webhook Stripe.
        
        Args:
            event: Événement Stripe
            
        Returns:
            Résultat du traitement
        """
        event_type = event.get("type")
        event_data = event.get("data", {}).get("object", {})
        
        logger.info(f"Traitement événement webhook: {event_type}")
        
        handlers = {
            "checkout.session.completed": self._handle_checkout_completed,
            "invoice.paid": self._handle_invoice_paid,
            "invoice.payment_failed": self._handle_invoice_payment_failed,
            "customer.subscription.updated": self._handle_subscription_updated,
            "customer.subscription.deleted": self._handle_subscription_deleted,
            "customer.subscription.created": self._handle_subscription_created,
        }
        
        handler = handlers.get(event_type)
        if handler:
            try:
                result = handler(event_data)
                return {
                    "status": "success",
                    "event_type": event_type,
                    "result": result
                }
            except Exception as e:
                logger.error(f"Erreur traitement {event_type}: {e}")
                return {
                    "status": "error",
                    "event_type": event_type,
                    "error": str(e)
                }
        else:
            logger.info(f"Événement non géré: {event_type}")
            return {
                "status": "ignored",
                "event_type": event_type
            }
    
    def _handle_checkout_completed(self, session: dict) -> dict:
        """
        Gère l'événement checkout.session.completed.
        Crée l'abonnement après paiement réussi.
        """
        metadata = session.get("metadata", {})
        user_id = metadata.get("user_id")
        plan_id = metadata.get("plan_id")
        
        subscription_id = session.get("subscription")
        customer_id = session.get("customer")
        
        logger.info(f"Checkout complété pour user {user_id}, plan {plan_id}")
        
        # Créer l'abonnement local
        subscription = Subscription(
            id=f"sub_{subscription_id}",
            user_id=user_id,
            plan_id=plan_id,
            stripe_subscription_id=subscription_id,
            stripe_customer_id=customer_id,
            status=SubscriptionStatus.ACTIVE,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        # Sauvegarder
        self.subscriptions[subscription.id] = subscription
        self.users_subscriptions[user_id] = subscription.id
        
        logger.info(f"Abonnement créé: {subscription.id}")
        
        return {
            "action": "subscription_created",
            "subscription_id": subscription.id,
            "user_id": user_id,
            "plan_id": plan_id
        }
    
    def _handle_invoice_paid(self, invoice: dict) -> dict:
        """
        Gère l'événement invoice.paid.
        Crée ou met à jour la facture.
        """
        subscription_id = invoice.get("subscription")
        customer_id = invoice.get("customer")
        
        # Trouver l'abonnement local
        local_sub_id = None
        user_id = None
        for sub in self.subscriptions.values():
            if sub.stripe_subscription_id == subscription_id:
                local_sub_id = sub.id
                user_id = sub.user_id
                break
        
        if not user_id:
            # Essayer de trouver via les métadonnées
            user_id = invoice.get("metadata", {}).get("user_id", "unknown")
        
        # Créer la facture
        invoice_model = stripe_invoice_to_model(invoice, user_id, local_sub_id)
        invoice_model.status = InvoiceStatus.PAID
        
        self.invoices[invoice_model.id] = invoice_model
        
        logger.info(f"Facture payée: {invoice_model.id}")
        
        return {
            "action": "invoice_paid",
            "invoice_id": invoice_model.id,
            "amount_euros": invoice_model.amount_due_euros
        }
    
    def _handle_invoice_payment_failed(self, invoice: dict) -> dict:
        """
        Gère l'événement invoice.payment_failed.
        Marque la facture comme échouée.
        """
        subscription_id = invoice.get("subscription")
        
        # Trouver l'abonnement local
        local_sub_id = None
        user_id = None
        for sub in self.subscriptions.values():
            if sub.stripe_subscription_id == subscription_id:
                local_sub_id = sub.id
                user_id = sub.user_id
                break
        
        if not user_id:
            user_id = invoice.get("metadata", {}).get("user_id", "unknown")
        
        # Créer la facture échouée
        invoice_model = stripe_invoice_to_model(invoice, user_id, local_sub_id)
        
        self.invoices[invoice_model.id] = invoice_model
        
        # Mettre à jour le statut de l'abonnement si nécessaire
        if local_sub_id and local_sub_id in self.subscriptions:
            self.subscriptions[local_sub_id].status = SubscriptionStatus.PAST_DUE
        
        logger.warning(f"Paiement échoué pour facture: {invoice_model.id}")
        
        return {
            "action": "payment_failed",
            "invoice_id": invoice_model.id,
            "next_payment_attempt": invoice.get("next_payment_attempt")
        }
    
    def _handle_subscription_updated(self, stripe_sub: dict) -> dict:
        """
        Gère l'événement customer.subscription.updated.
        Met à jour l'abonnement local.
        """
        stripe_sub_id = stripe_sub.get("id")
        
        # Trouver l'abonnement local
        local_sub = None
        for sub in self.subscriptions.values():
            if sub.stripe_subscription_id == stripe_sub_id:
                local_sub = sub
                break
        
        if local_sub:
            # Mettre à jour
            local_sub.status = SubscriptionStatus(stripe_sub.get("status", "incomplete"))
            local_sub.cancel_at_period_end = stripe_sub.get("cancel_at_period_end", False)
            local_sub.current_period_start = datetime.fromtimestamp(stripe_sub.get("current_period_start")) if stripe_sub.get("current_period_start") else None
            local_sub.current_period_end = datetime.fromtimestamp(stripe_sub.get("current_period_end")) if stripe_sub.get("current_period_end") else None
            local_sub.updated_at = datetime.utcnow()
            
            if stripe_sub.get("canceled_at"):
                local_sub.canceled_at = datetime.fromtimestamp(stripe_sub.get("canceled_at"))
            
            logger.info(f"Abonnement mis à jour: {local_sub.id}")
            
            return {
                "action": "subscription_updated",
                "subscription_id": local_sub.id,
                "status": local_sub.status.value
            }
        
        return {
            "action": "subscription_not_found",
            "stripe_subscription_id": stripe_sub_id
        }
    
    def _handle_subscription_deleted(self, stripe_sub: dict) -> dict:
        """
        Gère l'événement customer.subscription.deleted.
        Marque l'abonnement comme annulé.
        """
        stripe_sub_id = stripe_sub.get("id")
        
        # Trouver l'abonnement local
        local_sub = None
        for sub in self.subscriptions.values():
            if sub.stripe_subscription_id == stripe_sub_id:
                local_sub = sub
                break
        
        if local_sub:
            local_sub.status = SubscriptionStatus.CANCELED
            local_sub.canceled_at = datetime.utcnow()
            local_sub.updated_at = datetime.utcnow()
            
            logger.info(f"Abonnement supprimé: {local_sub.id}")
            
            return {
                "action": "subscription_canceled",
                "subscription_id": local_sub.id,
                "user_id": local_sub.user_id
            }
        
        return {
            "action": "subscription_not_found",
            "stripe_subscription_id": stripe_sub_id
        }
    
    def _handle_subscription_created(self, stripe_sub: dict) -> dict:
        """
        Gère l'événement customer.subscription.created.
        """
        stripe_sub_id = stripe_sub.get("id")
        metadata = stripe_sub.get("metadata", {})
        user_id = metadata.get("user_id", "unknown")
        plan_id = metadata.get("plan_id", "unknown")
        
        logger.info(f"Nouvel abonnement Stripe créé: {stripe_sub_id}")
        
        return {
            "action": "subscription_created_stripe",
            "stripe_subscription_id": stripe_sub_id,
            "user_id": user_id,
            "plan_id": plan_id
        }
    
    # Méthodes utilitaires pour récupérer les données
    
    def get_subscription(self, subscription_id: str) -> Optional[Subscription]:
        """Récupère un abonnement par ID"""
        return self.subscriptions.get(subscription_id)
    
    def get_user_subscription(self, user_id: str) -> Optional[Subscription]:
        """Récupère l'abonnement d'un utilisateur"""
        sub_id = self.users_subscriptions.get(user_id)
        if sub_id:
            return self.subscriptions.get(sub_id)
        return None
    
    def get_user_invoices(self, user_id: str) -> list[Invoice]:
        """Récupère les factures d'un utilisateur"""
        return [inv for inv in self.invoices.values() if inv.user_id == user_id]
    
    def cancel_subscription(
        self, 
        subscription_id: str, 
        user_id: str,
        immediate: bool = False
    ) -> Optional[Subscription]:
        """
        Annule un abonnement.
        
        Args:
            subscription_id: ID de l'abonnement
            user_id: ID de l'utilisateur (pour vérification)
            immediate: Annulation immédiate ou à la fin de la période
            
        Returns:
            Abonnement mis à jour ou None
        """
        subscription = self.subscriptions.get(subscription_id)
        
        if not subscription:
            logger.error(f"Abonnement non trouvé: {subscription_id}")
            return None
        
        if subscription.user_id != user_id:
            logger.error(f"User {user_id} n'est pas propriétaire de {subscription_id}")
            return None
        
        try:
            # Annuler via Stripe
            stripe_integration.cancel_subscription(
                subscription.stripe_subscription_id,
                immediate=immediate
            )
            
            # Mettre à jour localement
            if immediate:
                subscription.status = SubscriptionStatus.CANCELED
                subscription.canceled_at = datetime.utcnow()
            else:
                subscription.cancel_at_period_end = True
            
            subscription.updated_at = datetime.utcnow()
            
            logger.info(f"Abonnement {subscription_id} annulé (immediate={immediate})")
            
            return subscription
            
        except Exception as e:
            logger.error(f"Erreur annulation abonnement {subscription_id}: {e}")
            return None


# Instance singleton
webhook_handler = WebhookHandler()
