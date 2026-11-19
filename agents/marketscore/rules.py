"""
TrustDevis MarketScore - Règles métier par secteur
"""
from enum import Enum
from typing import Dict, Any


class Secteur(str, Enum):
    BATIMENT = "batiment"
    MECANIQUE = "mecanique"
    ELECTRICITE = "electricite"
    PLOMBERIE = "plomberie"
    GENERIQUE = "generique"


class RiskLevel(str, Enum):
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"


# Seuils de risque par secteur (delta % au-delà duquel on déclenche un niveau de risque)
SEUILS_RISQUE: Dict[Secteur, Dict[str, float]] = {
    Secteur.BATIMENT: {
        "moderate": 0.25,  # > 25% = moderate
        "high": 0.40,      # > 40% = high
    },
    Secteur.MECANIQUE: {
        "moderate": 0.20,  # > 20% = moderate
        "high": 0.35,      # > 35% = high
    },
    Secteur.ELECTRICITE: {
        "moderate": 0.25,
        "high": 0.40,
    },
    Secteur.PLOMBERIE: {
        "moderate": 0.25,
        "high": 0.40,
    },
    Secteur.GENERIQUE: {
        "moderate": 0.25,
        "high": 0.40,
    },
}

# Pondérations par catégorie de ligne (importance relative dans le calcul du score)
PONDERATIONS_CATEGORIE: Dict[str, float] = {
    "main_oeuvre": 0.35,
    "materiaux": 0.25,
    "pieces": 0.25,
    "deplacement": 0.10,
    "diagnostic": 0.05,
    "autre": 0.10,
}

# Score minimum pour éviter la revue humaine
SCORE_MIN_CONFIDENCE = 60

# Seuil de delta global pour alerte automatique
DELTA_GLOBAL_ALERTE = 0.30  # 30%


def get_seuil_risque(secteur: Secteur, delta_pct: float) -> RiskLevel:
    """
    Détermine le niveau de risque basé sur le secteur et le delta %.
    """
    seuils = SEUILS_RISQUE.get(secteur, SEUILS_RISQUE[Secteur.GENERIQUE])
    
    if delta_pct > seuils["high"]:
        return RiskLevel.HIGH
    elif delta_pct > seuils["moderate"]:
        return RiskLevel.MODERATE
    return RiskLevel.LOW


def get_ponderation_categorie(categorie: str) -> float:
    """
    Retourne la pondération pour une catégorie donnée.
    """
    return PONDERATIONS_CATEGORIE.get(categorie.lower(), PONDERATIONS_CATEGORIE["autre"])


def requires_human_review(score: int, risk_level: RiskLevel, delta_pct: float) -> bool:
    """
    Détermine si une revue humaine est nécessaire.
    """
    if score < SCORE_MIN_CONFIDENCE:
        return True
    if risk_level == RiskLevel.HIGH:
        return True
    if delta_pct > DELTA_GLOBAL_ALERTE:
        return True
    return False


def get_secteur_from_string(secteur_str: str) -> Secteur:
    """
    Convertit une string en enum Secteur.
    """
    mapping = {
        "batiment": Secteur.BATIMENT,
        "construction": Secteur.BATIMENT,
        "renovation": Secteur.BATIMENT,
        "mecanique": Secteur.MECANIQUE,
        "garage": Secteur.MECANIQUE,
        "auto": Secteur.MECANIQUE,
        "electricite": Secteur.ELECTRICITE,
        "plomberie": Secteur.PLOMBERIE,
    }
    return mapping.get(secteur_str.lower(), Secteur.GENERIQUE)
