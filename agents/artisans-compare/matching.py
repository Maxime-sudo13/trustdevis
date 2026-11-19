"""
Algorithme de matching client/artisan
"""

from typing import List, Optional
from models import Artisan, ArtisanMatch
from database import search_artisans


def match_artisans(
    project_type: str,
    location: str,
    budget: Optional[float] = None,
    urgency: str = "normal",
    limit: int = 3
) -> List[ArtisanMatch]:
    """
    Trouver les meilleurs artisans pour un projet
    """
    # Rechercher les artisans par spécialité et localisation
    candidates = search_artisans(
        specialty=project_type,
        location=location,
        min_rating=4.0,
        available=True if urgency == "urgent" else None,
        limit=20
    )
    
    matches = []
    for artisan in candidates:
        score, reasons = calculate_match_score(artisan, project_type, budget, urgency)
        
        # Estimer la fourchette de prix
        price_range = estimate_price_range(artisan, project_type)
        
        matches.append(ArtisanMatch(
            artisan=artisan,
            match_score=score,
            match_reasons=reasons,
            estimated_quote_range=price_range,
            availability=artisan.next_available_date or "Sur demande"
        ))
    
    # Trier par score et retourner les meilleurs
    matches.sort(key=lambda x: x.match_score, reverse=True)
    return matches[:limit]


def calculate_match_score(
    artisan: Artisan,
    project_type: str,
    budget: Optional[float],
    urgency: str
) -> tuple[float, List[str]]:
    """
    Calculer le score de matching et les raisons
    """
    score = 0.0
    reasons = []
    
    # Score de note (max 30 points)
    rating_score = artisan.rating * 6
    score += rating_score
    if artisan.rating >= 4.7:
        reasons.append(f"Excellente réputation ({artisan.rating}/5)")
    elif artisan.rating >= 4.5:
        reasons.append(f"Bonne réputation ({artisan.rating}/5)")
    
    # Score de transparence (max 25 points)
    transparency_score = artisan.transparency_score * 0.25
    score += transparency_score
    if artisan.transparency_score >= 90:
        reasons.append("Excellente transparence des prix")
    elif artisan.transparency_score >= 80:
        reasons.append("Bonne transparence des prix")
    
    # Nombre d'avis (max 15 points)
    review_score = min(artisan.review_count / 20, 15)
    score += review_score
    if artisan.review_count >= 100:
        reasons.append(f"{artisan.review_count} avis clients")
    
    # Badges (max 15 points)
    badge_score = len(artisan.badges) * 2
    score += badge_score
    if any(b.value == "trustdevis_verified" for b in artisan.badges):
        reasons.append("Vérifié TrustDevis")
    if any(b.value == "quality_gold" for b in artisan.badges):
        reasons.append("Badge Qualité Or")
    
    # Adéquation budget (max 15 points)
    if budget and artisan.average_daily_rate:
        # Estimer le projet à 3 jours de travail
        estimated_cost = artisan.average_daily_rate * 3
        budget_diff = abs(estimated_cost - budget) / budget
        if budget_diff < 0.2:
            score += 15
            reasons.append("Budget aligné avec vos attentes")
        elif budget_diff < 0.4:
            score += 8
    
    # Disponibilité urgente
    if urgency == "urgent" and artisan.available:
        score += 5
        reasons.append("Disponible rapidement")
    
    return round(score, 1), reasons


def estimate_price_range(artisan: Artisan, project_type: str) -> Optional[tuple[float, float]]:
    """
    Estimer une fourchette de prix selon le type de projet
    """
    if not artisan.average_daily_rate:
        return None
    
    # Durées estimées par type de projet (en jours)
    duration_map = {
        "plomberie": (0.5, 2),
        "electricite": (1, 3),
        "maconnerie": (2, 5),
        "peinture": (2, 4),
        "menuiserie": (1, 4),
        "couverture": (1, 5),
        "chauffage": (1, 3),
        "carrelage": (2, 5),
        "jardinage": (1, 3),
        "renovation": (5, 15)
    }
    
    duration = duration_map.get(project_type, (1, 3))
    
    min_price = artisan.average_daily_rate * duration[0]
    max_price = artisan.average_daily_rate * duration[1]
    
    return (min_price, max_price)


def calculate_transparency_score(artisan: Artisan) -> int:
    """
    Calculer le score de transparence TrustDevis
    """
    score = 50  # Base
    
    # +20 si TrustDevis vérifié
    if any(b.value == "trustdevis_verified" for b in artisan.badges):
        score += 20
    
    # +10 si tarifs publics (average_daily_rate renseigné)
    if artisan.average_daily_rate:
        score += 10
    
    # +10 si min_project_amount renseigné
    if artisan.min_project_amount:
        score += 10
    
    # +10 si certifications
    if any(b.value == "certified" for b in artisan.badges):
        score += 10
    
    # Bonus selon la note
    if artisan.rating >= 4.8:
        score += 10
    elif artisan.rating >= 4.5:
        score += 5
    
    return min(score, 100)
