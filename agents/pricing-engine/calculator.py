import numpy as np
from typing import List, Dict, Any, Optional
from database import Price, Region, Session


class PricingCalculator:
    """Calculateur de prix médians et percentiles"""
    
    @staticmethod
    def calculate_median(prices: List[float]) -> Optional[float]:
        """Calcule la médiane d'une liste de prix"""
        if not prices:
            return None
        return float(np.median(np.array(prices)))
    
    @staticmethod
    def calculate_percentiles(prices: List[float], percentiles: List[int] = [25, 75, 90]) -> Dict[str, float]:
        """Calcule les percentiles demandés"""
        if not prices:
            return {}
        
        prices_array = np.array(prices)
        result = {}
        for p in percentiles:
            result[f"percentile_{p}"] = float(np.percentile(prices_array, p))
        return result
    
    @staticmethod
    def calculate_all_stats(prices: List[float]) -> Dict[str, Any]:
        """Calcule toutes les statistiques (médiane, percentiles, min, max, etc.)"""
        if not prices:
            return None
        
        prices_array = np.array(prices)
        
        return {
            "count": len(prices),
            "median": float(np.median(prices_array)),
            "percentile_25": float(np.percentile(prices_array, 25)),
            "percentile_75": float(np.percentile(prices_array, 75)),
            "percentile_90": float(np.percentile(prices_array, 90)),
            "min": float(np.min(prices_array)),
            "max": float(np.max(prices_array)),
            "mean": float(np.mean(prices_array)),
            "std": float(np.std(prices_array))
        }
    
    @staticmethod
    def apply_labor_coefficient(base_price: float, coefficient: float) -> float:
        """Applique le coefficient main d'œuvre régional"""
        return round(base_price * coefficient, 2)
    
    @staticmethod
    def calculate_price_delta(submitted_price: float, market_median: float) -> Dict[str, Any]:
        """
        Calcule le delta entre un prix soumis et le prix médian du marché
        
        Returns:
            - delta_amount: Différence en euros
            - delta_percent: Différence en pourcentage
            - status: 'below_market', 'at_market', 'above_market'
        """
        delta_amount = round(submitted_price - market_median, 2)
        delta_percent = round((delta_amount / market_median) * 100, 2) if market_median != 0 else 0
        
        # Détermine le statut
        if delta_percent < -10:
            status = "significantly_below_market"
        elif delta_percent < -5:
            status = "below_market"
        elif delta_percent <= 5:
            status = "at_market"
        elif delta_percent <= 10:
            status = "above_market"
        else:
            status = "significantly_above_market"
        
        return {
            "submitted_price": submitted_price,
            "market_median": market_median,
            "delta_amount": delta_amount,
            "delta_percent": delta_percent,
            "status": status
        }
    
    @staticmethod
    def get_price_range_for_category(
        prices: List[float], 
        region: Region = None
    ) -> Dict[str, Any]:
        """
        Retourne la fourchette de prix pour une catégorie
        Prend en compte le coefficient main d'œuvre régional
        """
        stats = PricingCalculator.calculate_all_stats(prices)
        
        if not stats:
            return None
        
        # Applique le coefficient main d'œuvre si fourni
        if region and region.labor_coefficient != 1.0:
            coeff = region.labor_coefficient
            stats["labor_coefficient_applied"] = coeff
            stats["median_adjusted"] = round(stats["median"] * coeff, 2)
            stats["percentile_25_adjusted"] = round(stats["percentile_25"] * coeff, 2)
            stats["percentile_75_adjusted"] = round(stats["percentile_75"] * coeff, 2)
        
        return stats
    
    @staticmethod
    def evaluate_quote(
        quote_price: float,
        category: str,
        region_code: str,
        db: Session
    ) -> Dict[str, Any]:
        """
        Évalue un devis par rapport au marché
        
        Returns:
            - market_stats: Statistiques du marché
            - evaluation: Évaluation du prix soumis
            - recommendation: Recommandation
        """
        from database import get_prices_by_category_region, get_region
        
        # Récupère les prix du marché
        prices = get_prices_by_category_region(db, category, region_code)
        price_values = [p.price for p in prices]
        
        if not price_values:
            return {
                "error": f"Aucune donnée de marché pour {category} en {region_code}",
                "market_stats": None,
                "evaluation": None
            }
        
        # Récupère la région pour le coefficient
        region = get_region(db, region_code)
        
        # Calcule les stats du marché
        market_stats = PricingCalculator.get_price_range_for_category(price_values, region)
        market_median = market_stats["median"]
        
        # Évalue le prix soumis
        evaluation = PricingCalculator.calculate_price_delta(quote_price, market_median)
        
        # Génère une recommandation
        recommendation = PricingCalculator._generate_recommendation(evaluation, market_stats)
        
        return {
            "category": category,
            "region_code": region_code,
            "market_stats": market_stats,
            "evaluation": evaluation,
            "recommendation": recommendation
        }
    
    @staticmethod
    def _generate_recommendation(evaluation: Dict[str, Any], market_stats: Dict[str, Any]) -> str:
        """Génère une recommandation basée sur l'évaluation"""
        status = evaluation["status"]
        delta_percent = evaluation["delta_percent"]
        
        recommendations = {
            "significantly_below_market": f"⚠️ Prix significativement sous le marché ({delta_percent}%). Vérifiez la qualité des matériaux et la couverture.",
            "below_market": f"✅ Prix légèrement sous le marché ({delta_percent}%). Bonne affaire potentielle.",
            "at_market": f"✅ Prix aligné avec le marché (±{abs(delta_percent)}%).",
            "above_market": f"⚠️ Prix légèrement au-dessus du marché (+{delta_percent}%). Négociation possible.",
            "significantly_above_market": f"🔴 Prix significativement au-dessus du marché (+{delta_percent}%). Demandez un détail des coûts."
        }
        
        return recommendations.get(status, "Statut inconnu")
