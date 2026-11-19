from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Tuple
from enum import Enum


class WorkCategory(str, Enum):
    """Catégories de travaux"""
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


class PricingZone(str, Enum):
    """Zones tarifaires basées sur le code postal"""
    RURAL = "rural"
    SMALL_CITY = "small_city"  # < 50k habitants
    MEDIUM_CITY = "medium_city"  # 50k - 200k
    LARGE_CITY = "large_city"  # 200k - 1M
    PARIS_REGION = "paris_region"  # IDF


class LaborRate(BaseModel):
    """Taux horaire main d'œuvre par zone et niveau"""
    zone: PricingZone = Field(..., description="Zone géographique")
    economy_rate: float = Field(..., ge=0, description="Taux économique €/h")
    standard_rate: float = Field(..., ge=0, description="Taux standard €/h")
    premium_rate: float = Field(..., ge=0, description="Taux premium €/h")


class MaterialPrice(BaseModel):
    """Prix d'un matériau"""
    name: str = Field(..., description="Nom du matériau")
    unit: str = Field(..., description="Unité (m², ml, u, etc.)")
    economy_price: float = Field(..., ge=0, description="Prix économique")
    standard_price: float = Field(..., ge=0, description="Prix standard")
    premium_price: float = Field(..., ge=0, description="Prix premium")
    eco_price: Optional[float] = Field(None, ge=0, description="Prix écologique")
    description: Optional[str] = Field(None, description="Description")


class WorkItemPricing(BaseModel):
    """Tarification d'une prestation type"""
    code: str = Field(..., description="Code prestation")
    name: str = Field(..., description="Nom de la prestation")
    category: WorkCategory = Field(..., description="Catégorie")
    unit: str = Field(..., description="Unité")
    
    # Temps de travail estimé (heures par unité)
    labor_hours_economy: float = Field(..., ge=0, description="Heures niveau économique")
    labor_hours_standard: float = Field(..., ge=0, description="Heures niveau standard")
    labor_hours_premium: float = Field(..., ge=0, description="Heures niveau premium")
    
    # Matériaux requis par unité
    materials_needed: List[Tuple[str, float]] = Field(default_factory=list, description="[(material_code, quantity_per_unit)]")
    
    # Coûts fixes additionnels
    fixed_costs_economy: float = Field(default=0, ge=0, description="Coûts fixes économique")
    fixed_costs_standard: float = Field(default=0, ge=0, description="Coûts fixes standard")
    fixed_costs_premium: float = Field(default=0, ge=0, description="Coûts fixes premium")
    
    description: str = Field(..., description="Description détaillée")
    prerequisites: List[str] = Field(default_factory=list, description="Prérequis")


class PricingAdjustment(BaseModel):
    """Ajustements de prix selon contexte"""
    urgency_multiplier: Dict[str, float] = Field(default_factory=dict, description="Multiplicateur urgence")
    difficulty_multiplier: Dict[str, float] = Field(default_factory=dict, description="Multiplicateur difficulté")
    access_constraint_multiplier: Dict[str, float] = Field(default_factory=dict, description="Multiplicateur accès")
    surface_volume_discount: Dict[str, float] = Field(default_factory=dict, description="Remise volume")


class RegionalCoefficient(BaseModel):
    """Coefficients régionaux"""
    zone: PricingZone = Field(..., description="Zone")
    labor_coefficient: float = Field(default=1.0, description="Coefficient main d'œuvre")
    material_coefficient: float = Field(default=1.0, description="Coefficient matériaux")
    transport_coefficient: float = Field(default=1.0, description="Coefficient transport")


class PricingConfig(BaseModel):
    """Configuration complète du pricing"""
    vat_rate_standard: float = Field(default=20.0, description="Taux TVA standard")
    vat_rate_reduced: float = Field(default=10.0, description="Taux TVA réduit (travaux)")
    vat_rate_eco: float = Field(default=5.5, description="Taux TVA éco-énergie")
    
    minimum_quote_amount: float = Field(default=150.0, description="Montant minimum devis")
    
    warranty_years_economy: int = Field(default=1, description="Garantie économique")
    warranty_years_standard: int = Field(default=2, description="Garantie standard")
    warranty_years_premium: int = Field(default=10, description="Garantie premium")
    
    transport_base_cost: float = Field(default=30.0, description="Frais déplacement base")
    transport_per_km: float = Field(default=0.8, description="Frais déplacement/km")
    disposal_cost_per_m3: float = Field(default=85.0, description="Coût évacuation m³")
