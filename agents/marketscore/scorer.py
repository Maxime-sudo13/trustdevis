"""
TrustDevis MarketScore - Algorithme de scoring
"""
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass
from rules import (
    get_seuil_risque, 
    get_ponderation_categorie, 
    requires_human_review,
    get_secteur_from_string,
    RiskLevel,
    Secteur
)


@dataclass
class LigneScore:
    """Résultat du scoring d'une ligne de devis."""
    categorie: str
    description: str
    montant_devis: float
    mediane_marche: float
    delta_pct: float
    delta_abs: float
    ponderation: float
    score_ligne: float


@dataclass
class ScoreResult:
    """Résultat complet du scoring."""
    score: int
    delta_pct: float
    delta_moyen_pondere: float
    risk_level: str
    lignes_detail: List[LigneScore]
    total_devis: float
    total_marche: float
    requires_human_review: bool


def calculer_delta_ligne(montant_devis: float, mediane_marche: float) -> Tuple[float, float]:
    """
    Calcule le delta en % et en valeur absolue.
    
    Returns:
        (delta_pct, delta_abs)
    """
    if mediane_marche == 0:
        return 0.0, 0.0
    
    delta_abs = montant_devis - mediane_marche
    delta_pct = delta_abs / mediane_marche
    
    return delta_pct, delta_abs


def calculer_score_ligne(delta_pct: float, ponderation: float) -> float:
    """
    Calcule le score d'une ligne individuelle (0-100).
    
    Plus le delta est faible, plus le score est élevé.
    """
    # Pénalité non linéaire pour les écarts importants
    if delta_pct <= 0:
        # Sous-tarification = score parfait (100)
        return 100.0
    elif delta_pct <= 0.10:
        # Écart 0-10% : pénalité légère
        return 100 - (delta_pct * 100 * 0.5)
    elif delta_pct <= 0.25:
        # Écart 10-25% : pénalité modérée
        return 95 - ((delta_pct - 0.10) * 100 * 1.5)
    else:
        # Écart > 25% : pénalité sévère
        return 75 - ((delta_pct - 0.25) * 100 * 2)


def scorer_devis(
    lignes_devis: List[Dict[str, Any]],
    market_stats: Dict[str, Any],
    secteur_str: str
) -> ScoreResult:
    """
    Algorithme principal de scoring d'un devis.
    
    Args:
        lignes_devis: Liste des lignes du devis
        market_stats: Statistiques du marché régional
        secteur_str: Secteur d'activité
    
    Returns:
        ScoreResult avec tous les détails de calcul
    """
    secteur = get_secteur_from_string(secteur_str)
    lignes_scores: List[LigneScore] = []
    
    total_devis = 0.0
    total_pondere_delta = 0.0
    total_poids = 0.0
    
    for ligne in lignes_devis:
        categorie = ligne.get("categorie", "autre").lower()
        description = ligne.get("description", "")
        montant = float(ligne.get("montant", 0))
        
        # Récupérer la médiane du marché pour cette catégorie
        mediane = 0.0
        if "medianes" in market_stats and categorie in market_stats["medianes"]:
            mediane_data = market_stats["medianes"][categorie]
            if isinstance(mediane_data, dict):
                mediane = float(mediane_data.get("median", 0))
            else:
                mediane = float(mediane_data)
        
        # Calculs
        delta_pct, delta_abs = calculer_delta_ligne(montant, mediane)
        ponderation = get_ponderation_categorie(categorie)
        score_ligne = max(0, min(100, calculer_score_ligne(delta_pct, ponderation)))
        
        ligne_score = LigneScore(
            categorie=categorie,
            description=description,
            montant_devis=montant,
            mediane_marche=mediane,
            delta_pct=delta_pct,
            delta_abs=delta_abs,
            ponderation=ponderation,
            score_ligne=score_ligne
        )
        lignes_scores.append(ligne_score)
        
        # Agrégation pondérée
        total_devis += montant
        total_pondere_delta += abs(delta_pct) * ponderation
        total_poids += ponderation
    
    # Calcul du delta moyen pondéré
    delta_moyen_pondere = total_pondere_delta / total_poids if total_poids > 0 else 0.0
    
    # Calcul du delta global en %
    total_marche = sum(ls.mediane_marche for ls in lignes_scores)
    delta_global_pct = (total_devis - total_marche) / total_marche if total_marche > 0 else 0.0
    
    # Calcul du score global (0-100)
    # Basé sur le delta moyen pondéré avec une formule de décroissance
    if delta_moyen_pondere <= 0.05:
        score_global = 95 - (delta_moyen_pondere * 100)
    elif delta_moyen_pondere <= 0.15:
        score_global = 90 - ((delta_moyen_pondere - 0.05) * 200)
    elif delta_moyen_pondere <= 0.25:
        score_global = 70 - ((delta_moyen_pondere - 0.15) * 300)
    else:
        score_global = max(0, 40 - ((delta_moyen_pondere - 0.25) * 100))
    
    score_global = int(round(max(0, min(100, score_global))))
    
    # Détermination du niveau de risque
    # On prend le max entre le delta global et le delta moyen pondéré
    max_delta = max(abs(delta_global_pct), delta_moyen_pondere)
    risk_level = get_seuil_risque(secteur, max_delta)
    
    # Détermination si revue humaine nécessaire
    need_review = requires_human_review(score_global, risk_level, abs(delta_global_pct))
    
    return ScoreResult(
        score=score_global,
        delta_pct=round(delta_global_pct * 100, 2),
        delta_moyen_pondere=round(delta_moyen_pondere * 100, 2),
        risk_level=risk_level.value,
        lignes_detail=lignes_scores,
        total_devis=round(total_devis, 2),
        total_marche=round(total_marche, 2),
        requires_human_review=need_review
    )
