from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class LeadStatus(str, Enum):
    """Statut d'un lead"""
    NEW = "new"
    CONTACTED = "contacted"
    QUALIFIED = "qualified"
    CONVERTED = "converted"
    ARCHIVED = "archived"


class LeadQuality(str, Enum):
    """Classification qualité du lead"""
    HOT = "hot"      # > 70 points - Urgent, budget confirmé
    WARM = "warm"    # 40-70 points - Intéressé, à qualifier
    COLD = "cold"    # < 40 points - Faible priorité


class LeadType(str, Enum):
    """Type de travaux"""
    RENOVATION = "renovation"
    CONSTRUCTION = "construction"
    REPARATION = "reparation"
    INSTALLATION = "installation"
    ENTRETIEN = "entretien"
    AUTRE = "autre"


class LeadSource(str, Enum):
    """Source du lead"""
    LEBONCOIN = "leboncoin"
    SELOGER = "seloger"
    MEILLEURSAGENTS = "meilleursagents"
    DATAGOUV_PERMIS = "datagouv_permis"
    TWITTER = "twitter"
    MANUAL = "manual"


class Localisation(BaseModel):
    """Localisation d'un lead"""
    adresse: Optional[str] = None
    code_postal: Optional[str] = None
    ville: str
    region: Optional[str] = None
    departement: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class Contact(BaseModel):
    """Informations de contact"""
    nom: Optional[str] = None
    email: Optional[str] = None
    telephone: Optional[str] = None
    societe: Optional[str] = None


class Lead(BaseModel):
    """Modèle principal d'un lead"""
    id: str = Field(..., description="Identifiant unique du lead")
    source: LeadSource = Field(..., description="Source d'origine")
    type_travaux: LeadType = Field(..., description="Type de travaux")
    sous_type: Optional[str] = Field(None, description="Sous-catégorie (ex: 'plomberie', 'toiture')")
    
    # Localisation
    localisation: Localisation
    
    # Contact
    contact: Optional[Contact] = None
    
    # Détails du projet
    description: Optional[str] = None
    budget_estime: Optional[float] = Field(None, description="Budget estimé en euros")
    surface_m2: Optional[float] = None
    urgence: Optional[str] = Field(None, description="Niveau d'urgence déclaré")
    date_souhaitee: Optional[datetime] = None
    
    # Scoring
    score: int = Field(default=0, ge=0, le=100, description="Score de pertinence 0-100")
    qualite: LeadQuality = Field(default=LeadQuality.COLD)
    
    # Statut et métadonnées
    status: LeadStatus = Field(default=LeadStatus.NEW)
    url_source: Optional[str] = None
    raw_data: Optional[dict] = None  # Données brutes de la source
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    scraped_at: datetime = Field(default_factory=datetime.utcnow)


class LeadFilter(BaseModel):
    """Filtres pour la recherche de leads"""
    secteur: Optional[str] = Field(None, description="Secteur d'activité")
    region: Optional[str] = None
    departement: Optional[str] = None
    ville: Optional[str] = None
    code_postal: Optional[str] = None
    
    type_travaux: Optional[LeadType] = None
    qualite: Optional[LeadQuality] = None
    status: Optional[LeadStatus] = None
    source: Optional[LeadSource] = None
    
    budget_min: Optional[float] = None
    budget_max: Optional[float] = None
    
    score_min: Optional[int] = Field(None, ge=0, le=100)
    score_max: Optional[int] = Field(None, ge=0, le=100)
    
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    
    limit: int = Field(default=50, ge=1, le=500)
    offset: int = Field(default=0, ge=0)


class LeadSearchRequest(BaseModel):
    """Requête de recherche de leads"""
    query: Optional[str] = None
    filtres: LeadFilter = Field(default_factory=LeadFilter)


class LeadListResponse(BaseModel):
    """Réponse liste de leads"""
    total: int
    limit: int
    offset: int
    leads: List[Lead]


class LeadScoreFactors(BaseModel):
    """Facteurs de scoring détaillés"""
    type_travaux_score: int = Field(..., ge=0, le=100)
    budget_score: int = Field(..., ge=0, le=100)
    urgence_score: int = Field(..., ge=0, le=100)
    localisation_score: int = Field(..., ge=0, le=100)
    contact_score: int = Field(..., ge=0, le=100)
    total_score: int = Field(..., ge=0, le=100)
