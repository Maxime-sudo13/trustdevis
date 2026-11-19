"""
Module de comparaison d'artisans
"""

from typing import List, Dict, Any, Optional
from models import Artisan, ComparisonResult, ComparisonMetric, Review
from database import get_reviews


def compare_artisans(
    artisans: List[Artisan],
    project_type: str,
    budget_reference: Optional[float] = None
) -> ComparisonResult:
    """
    Comparer 2 ou 3 artisans et générer un tableau comparatif
    """
    if len(artisans) < 2:
        raise ValueError("Au moins 2 artisans sont nécessaires pour une comparaison")
    
    # Construire les métriques de comparaison
    metrics = build_comparison_metrics(artisans)
    
    # Comparer les prix
    price_comparison = compare_prices(artisans, budget_reference)
    
    # Comparer les notes
    rating_comparison = compare_ratings(artisans)
    
    # Résumé des badges
    badges_summary = {a.id: a.badges for a in artisans}
    
    # Récupérer les avis récents
    recent_reviews = {}
    for artisan in artisans:
        recent_reviews[artisan.id] = get_reviews(artisan.id, limit=3)
    
    # Déterminer la recommandation
    recommended_id, reason = determine_recommendation(artisans, metrics, budget_reference)
    
    # Calculer le prix moyen du marché
    market_average = calculate_market_average(project_type)
    
    return ComparisonResult(
        artisans=artisans,
        project_type=project_type,
        budget_reference=budget_reference,
        metrics=metrics,
        price_comparison=price_comparison,
        market_average=market_average,
        rating_comparison=rating_comparison,
        badges_summary=badges_summary,
        recommended_artisan_id=recommended_id,
        recommendation_reason=reason,
        recent_reviews=recent_reviews
    )


def build_comparison_metrics(artisans: List[Artisan]) -> List[ComparisonMetric]:
    """
    Construire les métriques de comparaison
    """
    metrics = []
    
    # Note globale
    best_rating = max(artisans, key=lambda a: a.rating)
    metrics.append(ComparisonMetric(
        label="Note globale",
        artisan_values={a.id: f"{a.rating}/5 ({a.review_count} avis)" for a in artisans},
        best_artisan_id=best_rating.id,
        unit="étoiles"
    ))
    
    # Score de transparence
    best_transparency = max(artisans, key=lambda a: a.transparency_score)
    metrics.append(ComparisonMetric(
        label="Score de transparence TrustDevis",
        artisan_values={a.id: f"{a.transparency_score}%" for a in artisans},
        best_artisan_id=best_transparency.id,
        unit="%"
    ))
    
    # Tarif journalier
    tjm_values = {}
    best_tjm_id = None
    best_tjm = float('inf')
    for a in artisans:
        if a.average_daily_rate:
            tjm_values[a.id] = f"{a.average_daily_rate:.0f} €"
            if a.average_daily_rate < best_tjm:
                best_tjm = a.average_daily_rate
                best_tjm_id = a.id
        else:
            tjm_values[a.id] = "Sur devis"
    
    metrics.append(ComparisonMetric(
        label="Tarif journalier moyen",
        artisan_values=tjm_values,
        best_artisan_id=best_tjm_id,
        unit="€/jour"
    ))
    
    # Disponibilité
    avail_values = {}
    earliest_id = None
    earliest_date = None
    for a in artisans:
        if a.next_available_date:
            avail_values[a.id] = a.next_available_date
            if earliest_date is None or a.next_available_date < earliest_date:
                earliest_date = a.next_available_date
                earliest_id = a.id
        else:
            avail_values[a.id] = "Sur demande"
    
    metrics.append(ComparisonMetric(
        label="Prochaine disponibilité",
        artisan_values=avail_values,
        best_artisan_id=earliest_id
    ))
    
    # Nombre de badges
    best_badges = max(artisans, key=lambda a: len(a.badges))
    metrics.append(ComparisonMetric(
        label="Badges TrustDevis",
        artisan_values={a.id: f"{len(a.badges)} badge(s)" for a in artisans},
        best_artisan_id=best_badges.id
    ))
    
    # Montant minimum
    min_values = {}
    lowest_min_id = None
    lowest_min = float('inf')
    for a in artisans:
        if a.min_project_amount:
            min_values[a.id] = f"{a.min_project_amount:.0f} €"
            if a.min_project_amount < lowest_min:
                lowest_min = a.min_project_amount
                lowest_min_id = a.id
        else:
            min_values[a.id] = "Non spécifié"
    
    metrics.append(ComparisonMetric(
        label="Montant minimum de projet",
        artisan_values=min_values,
        best_artisan_id=lowest_min_id,
        unit="€"
    ))
    
    return metrics


def compare_prices(artisans: List[Artisan], budget: Optional[float]) -> Dict[str, Any]:
    """
    Comparer les prix des artisans
    """
    result = {
        "daily_rates": {},
        "min_projects": {},
        "budget_alignment": {}
    }
    
    for a in artisans:
        result["daily_rates"][a.id] = a.average_daily_rate
        result["min_projects"][a.id] = a.min_project_amount
        
        if budget and a.average_daily_rate:
            # Estimer un projet à 3 jours
            estimated = a.average_daily_rate * 3
            diff_pct = ((estimated - budget) / budget) * 100
            result["budget_alignment"][a.id] = {
                "estimated_total": estimated,
                "difference_percent": round(diff_pct, 1),
                "alignment": "below" if diff_pct < -10 else "above" if diff_pct > 10 else "aligned"
            }
        else:
            result["budget_alignment"][a.id] = None
    
    return result


def compare_ratings(artisans: List[Artisan]) -> Dict[str, Any]:
    """
    Comparer les notes détaillées
    """
    return {
        "global_rating": {a.id: a.rating for a in artisans},
        "review_count": {a.id: a.review_count for a in artisans},
        "rating_distribution": {
            a.id: {
                "5_stars": int(a.review_count * 0.6),
                "4_stars": int(a.review_count * 0.25),
                "3_stars": int(a.review_count * 0.1),
                "2_stars": int(a.review_count * 0.03),
                "1_star": int(a.review_count * 0.02)
            } for a in artisans
        }
    }


def determine_recommendation(
    artisans: List[Artisan],
    metrics: List[ComparisonMetric],
    budget: Optional[float]
) -> tuple[Optional[str], str]:
    """
    Déterminer l'artisan recommandé
    """
    scores = {a.id: 0 for a in artisans}
    
    # Points pour chaque métrique où l'artisan est meilleur
    for metric in metrics:
        if metric.best_artisan_id:
            scores[metric.best_artisan_id] += 1
    
    # Bonus pour transparence élevée
    for a in artisans:
        if a.transparency_score >= 90:
            scores[a.id] += 2
    
    # Bonus pour note élevée
    for a in artisans:
        if a.rating >= 4.8:
            scores[a.id] += 1
    
    # Trouver le meilleur
    best_id = max(scores, key=scores.get)
    best_artisan = next(a for a in artisans if a.id == best_id)
    
    # Construire la raison
    reasons = []
    if best_artisan.transparency_score >= 90:
        reasons.append("excellente transparence")
    if best_artisan.rating >= 4.7:
        reasons.append("très bonne réputation")
    if any(b.value == "trustdevis_verified" for b in best_artisan.badges):
        reasons.append("vérifié TrustDevis")
    
    if reasons:
        reason = f"Recommandé pour son {', '.join(reasons)}"
    else:
        reason = "Recommandé selon nos critères de sélection"
    
    return best_id, reason


def calculate_market_average(project_type: str) -> Optional[float]:
    """
    Calculer le prix moyen du marché pour un type de projet
    """
    # Tarifs moyens par jour selon le type de travail
    market_rates = {
        "plomberie": 420,
        "electricite": 400,
        "maconnerie": 380,
        "peinture": 350,
        "menuiserie": 390,
        "couverture": 450,
        "chauffage": 480,
        "carrelage": 360,
        "jardinage": 320,
        "renovation": 400
    }
    
    return market_rates.get(project_type)
