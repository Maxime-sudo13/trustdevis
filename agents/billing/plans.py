from models import Plan, PlanTier


# Configuration des plans TrustDevis
PLANS = {
    PlanTier.STARTER: Plan(
        id="starter",
        name="STARTER",
        tier=PlanTier.STARTER,
        price_cents=2900,
        price_euros=29.0,
        currency="eur",
        interval="month",
        description="Parfait pour démarrer et tester la plateforme",
        features=[
            "50 analyses de devis par mois",
            "Support par email",
            "Rapports PDF basiques",
            "Accès tableau de bord"
        ],
        analysis_limit=50,
        stripe_price_id=None,  # À configurer avec vos IDs Stripe
        stripe_product_id=None
    ),
    PlanTier.PRO: Plan(
        id="pro",
        name="PRO",
        tier=PlanTier.PRO,
        price_cents=7900,
        price_euros=79.0,
        currency="eur",
        interval="month",
        description="Pour les professionnels qui veulent plus de puissance",
        features=[
            "200 analyses de devis par mois",
            "Support prioritaire (email + chat)",
            "Rapports PDF avancés",
            "Accès API",
            "Intégrations tierces",
            "Historique illimité"
        ],
        analysis_limit=200,
        stripe_price_id=None,
        stripe_product_id=None
    ),
    PlanTier.ENTERPRISE: Plan(
        id="enterprise",
        name="ENTERPRISE",
        tier=PlanTier.ENTERPRISE,
        price_cents=14900,
        price_euros=149.0,
        currency="eur",
        interval="month",
        description="Solution complète pour les grandes structures",
        features=[
            "Analyses de devis illimitées",
            "Support dédié 24/7",
            "Rapports personnalisés",
            "Accès API + Webhooks",
            "Intégrations sur mesure",
            "Multi-utilisateurs",
            "SLA garanti",
            "Formation incluse"
        ],
        analysis_limit=-1,  # -1 = illimité
        stripe_price_id=None,
        stripe_product_id=None
    )
}


def get_plan(plan_id: str) -> Plan | None:
    """
    Récupère un plan par son ID.
    
    Args:
        plan_id: ID du plan (starter, pro, enterprise)
        
    Returns:
        Plan ou None si non trouvé
    """
    plan_id_lower = plan_id.lower()
    for tier, plan in PLANS.items():
        if plan.id == plan_id_lower or tier.value == plan_id_lower:
            return plan
    return None


def get_all_plans() -> list[Plan]:
    """
    Récupère tous les plans disponibles.
    
    Returns:
        Liste des plans
    """
    return list(PLANS.values())


def get_plan_by_stripe_price(stripe_price_id: str) -> Plan | None:
    """
    Récupère un plan par son ID de prix Stripe.
    
    Args:
        stripe_price_id: ID du prix Stripe
        
    Returns:
        Plan ou None si non trouvé
    """
    for plan in PLANS.values():
        if plan.stripe_price_id == stripe_price_id:
            return plan
    return None


def update_plan_stripe_ids(plan_id: str, price_id: str, product_id: str) -> None:
    """
    Met à jour les IDs Stripe d'un plan.
    À appeler après création des produits/prix dans Stripe.
    
    Args:
        plan_id: ID du plan
        price_id: ID du prix Stripe
        product_id: ID du produit Stripe
    """
    plan = get_plan(plan_id)
    if plan:
        plan.stripe_price_id = price_id
        plan.stripe_product_id = product_id


# Helper pour afficher les prix
def format_price_euros(cents: int) -> str:
    """Formate un prix en cents en euros avec symbole €"""
    return f"{cents / 100:.2f}€"


# Détails des plans pour l'affichage
PLAN_DETAILS = {
    "starter": {
        "display_name": "STARTER",
        "price_display": "29€/mois",
        "highlight": False,
        "badge": None
    },
    "pro": {
        "display_name": "PRO",
        "price_display": "79€/mois",
        "highlight": True,
        "badge": "Populaire"
    },
    "enterprise": {
        "display_name": "ENTERPRISE",
        "price_display": "149€/mois",
        "highlight": False,
        "badge": "Tout inclus"
    }
}
