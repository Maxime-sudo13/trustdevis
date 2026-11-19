"""
Modèles de données pour le service Artisans Compare
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class Badge(str, Enum):
    TRUSTDEVIS_VERIFIED = "trustdevis_verified"
    TRANSPARENCY_EXCELLENT = "transparency_excellent"
    QUALITY_GOLD = "quality_gold"
    PUNCTUALITY = "punctuality"
    RESPONSIVE = "responsive"
    INSURED = "insured"
    CERTIFIED = "certified"


class Artisan(BaseModel):
    """Modèle d'un artisan"""
    id: str
    name: str
    company_name: Optional[str] = None
    specialty: str
    sub_specialties: List[str] = []
    
    # Localisation
    city: str
    postal_code: str
    region: str
    service_radius_km: int = 30
    
    # Contact
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    
    # Notes et avis
    rating: float = Field(ge=0, le=5, default=0)
    review_count: int = 0
    
    # Badges TrustDevis
    badges: List[Badge] = []
    
    # Score de transparence (0-100)
    transparency_score: int = Field(ge=0, le=100, default=0)
    
    # Disponibilité
    available: bool = True
    next_available_date: Optional[str] = None
    
    # Tarifs indicatifs
    average_daily_rate: Optional[float] = None  # TJM
    min_project_amount: Optional[float] = None
    
    # Métadonnées
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        from_attributes = True


class Certification(BaseModel):
    """Certification professionnelle"""
    name: str
    organization: str
    valid_until: Optional[str] = None
    verified: bool = False


class Insurance(BaseModel):
    """Assurance"""
    type: str
    provider: str
    coverage_amount: Optional[float] = None
    valid_until: Optional[str] = None
    verified: bool = False


class QuoteHistory(BaseModel):
    """Historique des devis analysés pour cet artisan"""
    quote_id: str
    project_type: str
    amount: float
    analyzed_at: datetime
    market_position: str  # "below_market", "market_rate", "above_market"
    transparency_rating: int  # 0-100


class ArtisanProfile(Artisan):
    """Profil complet d'un artisan"""
    description: Optional[str] = None
    year_established: Optional[int] = None
    team_size: Optional[int] = None
    
    # Certifications et assurances
    certifications: List[Certification] = []
    insurances: List[Insurance] = []
    
    # Historique TrustDevis
    quotes_analyzed: List[QuoteHistory] = []
    
    # Avis clients
    reviews: List["Review"] = []
    
    # Statistiques
    completed_projects: int = 0
    response_time_hours: float = 24
    quote_acceptance_rate: float = 0.5
    
    # Photos
    logo_url: Optional[str] = None
    work_photos: List[str] = []


class Review(BaseModel):
    """Avis client"""
    id: str
    artisan_id: str
    client_name: str
    rating: float = Field(ge=0, le=5)
    title: Optional[str] = None
    comment: str
    project_type: str
    project_amount: Optional[float] = None
    verified: bool = False  # Avis vérifié (projet confirmé)
    created_at: datetime = Field(default_factory=datetime.now)
    
    # Sous-notes
    quality_rating: Optional[float] = Field(ge=0, le=5, default=None)
    punctuality_rating: Optional[float] = Field(ge=0, le=5, default=None)
    communication_rating: Optional[float] = Field(ge=0, le=5, default=None)
    value_rating: Optional[float] = Field(ge=0, le=5, default=None)


class ArtisanMatchRequest(BaseModel):
    """Requête de matching client/artisan"""
    project_type: str
    location: str
    budget: Optional[float] = None
    urgency: str = "normal"  # "urgent", "normal", "planned"
    artisan_ids: List[str] = []  # Pour comparaison
    description: Optional[str] = None


class ArtisanMatch(BaseModel):
    """Résultat de matching"""
    artisan: Artisan
    match_score: float = Field(ge=0, le=100)
    match_reasons: List[str]
    estimated_quote_range: Optional[tuple[float, float]] = None
    availability: str


class ComparisonMetric(BaseModel):
    """Métrique de comparaison"""
    label: str
    artisan_values: Dict[str, Any]  # artisan_id -> value
    best_artisan_id: Optional[str] = None
    unit: Optional[str] = None


class ComparisonResult(BaseModel):
    """Résultat de comparaison de 3 artisans"""
    artisans: List[Artisan]
    project_type: str
    budget_reference: Optional[float] = None
    
    # Tableau comparatif
    metrics: List[ComparisonMetric]
    
    # Prix
    price_comparison: Dict[str, Any]
    market_average: Optional[float] = None
    
    # Notes
    rating_comparison: Dict[str, Any]
    
    # Badges
    badges_summary: Dict[str, List[Badge]]
    
    # Recommandation
    recommended_artisan_id: Optional[str] = None
    recommendation_reason: str
    
    # Avis récents
    recent_reviews: Dict[str, List[Review]]  # artisan_id -> reviews
    
    created_at: datetime = Field(default_factory=datetime.now)
