from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Literal
from datetime import datetime
from enum import Enum


class WorkType(str, Enum):
    """Types de travaux supportés"""
    PLOMBERIE = "plomberie"
    ELECTRICITE = "electricite"
    PEINTURE = "peinture"
    MACONNERIE = "maconnerie"
    MENUISERIE = "menuiserie"
    CHAUFFAGE = "chauffage"
    PLOTRERIE = "platerie"
    CARRELAGE = "carrelage"
    PARQUET = "parquet"
    TOITURE = "toiture"
    ISOLATION = "isolation"
    MENUISERIE_EXTERIEURE = "menuiserie_exterieure"
    RENOVATION_COMPLETE = "renovation_complete"


class MaterialLevel(str, Enum):
    """Niveaux de matériaux"""
    ECONOMIQUE = "economique"
    STANDARD = "standard"
    PREMIUM = "premium"
    ECO = "eco"


class UrgencyLevel(str, Enum):
    """Niveaux d'urgence"""
    STANDARD = "standard"
    EXPRESS = "express"
    URGENT = "urgent"


class QuoteLevel(str, Enum):
    """Niveaux de devis générés"""
    ECONOMIQUE = "economique"
    STANDARD = "standard"
    PREMIUM = "premium"


class WorkDescription(BaseModel):
    """Description des travaux par le client"""
    work_type: WorkType = Field(..., description="Type de travaux")
    description: str = Field(..., min_length=10, description="Description détaillée des travaux")
    surface_m2: Optional[float] = Field(None, ge=0, description="Surface en m² si applicable")
    dimensions: Optional[str] = Field(None, description="Dimensions spécifiques (L x l x H)")
    material_preference: MaterialLevel = Field(default=MaterialLevel.STANDARD, description="Niveau de matériaux souhaité")
    postal_code: str = Field(..., min_length=5, max_length=5, description="Code postal")
    city: Optional[str] = Field(None, description="Ville")
    urgency: UrgencyLevel = Field(default=UrgencyLevel.STANDARD, description="Niveau d'urgence")
    budget_indicative: Optional[float] = Field(None, ge=0, description="Budget indicatif du client")
    existing_issues: Optional[str] = Field(None, description="Problèmes existants mentionnés")
    access_constraints: Optional[str] = Field(None, description="Contraintes d'accès")
    desired_start_date: Optional[datetime] = Field(None, description="Date souhaitée de début")


class CostBreakdown(BaseModel):
    """Détail des coûts"""
    labor_cost: float = Field(..., ge=0, description="Coût main d'œuvre HT")
    materials_cost: float = Field(..., ge=0, description="Coût matériaux HT")
    equipment_cost: float = Field(default=0, ge=0, description="Coût équipement HT")
    disposal_cost: float = Field(default=0, ge=0, description="Coût évacuation/déchets HT")
    transport_cost: float = Field(default=0, ge=0, description="Frais de déplacement HT")
    subtotal_ht: float = Field(..., ge=0, description="Sous-total HT")
    vat_rate: float = Field(default=20.0, description="Taux de TVA")
    vat_amount: float = Field(..., ge=0, description="Montant TVA")
    total_ttc: float = Field(..., ge=0, description="Total TTC")


class TimelineEstimate(BaseModel):
    """Estimation de la durée"""
    days_min: int = Field(..., ge=0, description="Durée minimale en jours")
    days_max: int = Field(..., ge=0, description="Durée maximale en jours")
    working_hours_per_day: int = Field(default=8, description="Heures de travail par jour")
    total_hours_estimate: int = Field(..., ge=0, description="Estimation totale en heures")


class QuoteVariant(BaseModel):
    """Variante de devis (économique, standard, premium)"""
    level: QuoteLevel = Field(..., description="Niveau du devis")
    title: str = Field(..., description="Titre de la variante")
    description: str = Field(..., description="Description de ce niveau")
    materials_quality: str = Field(..., description="Qualité des matériaux")
    cost_breakdown: CostBreakdown = Field(..., description="Détail des coûts")
    timeline: TimelineEstimate = Field(..., description="Durée estimée")
    warranty_years: int = Field(..., ge=0, description="Garantie en années")
    included_services: List[str] = Field(default_factory=list, description="Services inclus")
    excluded_services: List[str] = Field(default_factory=list, description="Services exclus")


class QuoteComparison(BaseModel):
    """Comparaison entre les 3 devis"""
    price_difference_economy_to_standard: float = Field(..., description="Différence prix éco → standard")
    price_difference_standard_to_premium: float = Field(..., description="Différence prix standard → premium")
    savings_economy_vs_premium: float = Field(..., description="Économie éco vs premium")
    quality_score_economy: int = Field(..., ge=0, le=100, description="Score qualité économique")
    quality_score_standard: int = Field(..., ge=0, le=100, description="Score qualité standard")
    quality_score_premium: int = Field(..., ge=0, le=100, description="Score qualité premium")
    value_for_money_recommendation: QuoteLevel = Field(..., description="Recommandation meilleur rapport qualité/prix")
    explanation: str = Field(..., description="Explication de la recommandation")


class PriceDistribution(BaseModel):
    """Répartition des prix pour graphique"""
    labels: List[str] = Field(..., description="Labels des segments")
    values: List[float] = Field(..., description="Valeurs des segments")
    colors: List[str] = Field(..., description="Couleurs pour le graphique")


class GeneratedQuote(BaseModel):
    """Devis généré complet"""
    id: str = Field(..., description="Identifiant unique du devis")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Date de création")
    work_description: WorkDescription = Field(..., description="Description initiale")
    variants: Dict[QuoteLevel, QuoteVariant] = Field(..., description="Les 3 variantes de devis")
    comparison: QuoteComparison = Field(..., description="Analyse comparative")
    price_distribution: Dict[QuoteLevel, PriceDistribution] = Field(..., description="Répartition des prix")
    artisan_profiles: Dict[QuoteLevel, str] = Field(..., description="Profil type d'artisan pour chaque niveau")
    recommendations: List[str] = Field(default_factory=list, description="Recommandations personnalisées")
    next_steps: List[str] = Field(default_factory=list, description="Prochaines étapes suggérées")


class QuoteRequest(BaseModel):
    """Requête de génération de devis"""
    work_description: WorkDescription = Field(..., description="Description des travaux")
    email: Optional[str] = Field(None, description="Email pour envoi du devis")
    phone: Optional[str] = Field(None, description="Téléphone pour contact")
    receive_by_email: bool = Field(default=False, description="Envoyer par email")
    contact_artisans: bool = Field(default=False, description="Être mis en relation")


class QuoteResponse(BaseModel):
    """Réponse de génération de devis"""
    success: bool = Field(..., description="Succès de la génération")
    quote: Optional[GeneratedQuote] = Field(None, description="Devis généré")
    message: str = Field(..., description="Message de retour")
    estimated_accuracy: int = Field(..., ge=0, le=100, description="Fiabilité estimée du devis")


class EmailRequest(BaseModel):
    """Requête d'envoi par email"""
    quote_id: str = Field(..., description="ID du devis")
    email: str = Field(..., description="Adresse email destinataire")
    include_comparison: bool = Field(default=True, description="Inclure le comparatif")
    include_artisan_contacts: bool = Field(default=False, description="Inclure contacts artisans")


class EmailResponse(BaseModel):
    """Réponse d'envoi email"""
    success: bool = Field(..., description="Succès de l'envoi")
    message: str = Field(..., description="Message de retour")
    sent_at: Optional[datetime] = Field(None, description="Date d'envoi")


class ArtisanContactRequest(BaseModel):
    """Requête de mise en relation avec artisans"""
    quote_id: str = Field(..., description="ID du devis")
    preferred_levels: List[QuoteLevel] = Field(default_factory=lambda: [QuoteLevel.STANDARD], description="Niveaux préférés")
    contact_name: str = Field(..., description="Nom du contact")
    contact_email: str = Field(..., description="Email de contact")
    contact_phone: str = Field(..., description="Téléphone de contact")
    preferred_contact_method: Literal["email", "phone", "both"] = Field(default="email", description="Méthode de contact préférée")
    availability: Optional[str] = Field(None, description="Disponibilités")
    additional_notes: Optional[str] = Field(None, description="Notes additionnelles")


class ArtisanContactResponse(BaseModel):
    """Réponse de mise en relation"""
    success: bool = Field(..., description="Succès de la demande")
    message: str = Field(..., description="Message de retour")
    request_id: Optional[str] = Field(None, description="ID de la demande")
    estimated_response_time: str = Field(..., description="Délai estimé de réponse")


class QuoteStorage(BaseModel):
    """Stockage des devis en mémoire (temporaire)"""
    quotes: Dict[str, GeneratedQuote] = Field(default_factory=dict)
    
    def add_quote(self, quote: GeneratedQuote) -> None:
        self.quotes[quote.id] = quote
    
    def get_quote(self, quote_id: str) -> Optional[GeneratedQuote]:
        return self.quotes.get(quote_id)
    
    def delete_quote(self, quote_id: str) -> bool:
        if quote_id in self.quotes:
            del self.quotes[quote_id]
            return True
        return False
