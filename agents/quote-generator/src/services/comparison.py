"""
Service de comparaison de devis
"""

from typing import Dict, List
from src.models.quote import GeneratedQuote, QuoteLevel, QuoteVariant


class QuoteComparisonService:
    """Service d'analyse comparative des devis"""
    
    def generate_comparison_table(self, quote: GeneratedQuote) -> Dict:
        """Génère un tableau comparatif des 3 devis"""
        
        variants = quote.variants
        
        table = {
            "headers": ["Critère", "Économique", "Standard", "Premium"],
            "rows": [
                {
                    "critere": "Prix total TTC",
                    "economique": f"{variants[QuoteLevel.ECONOMIQUE].cost_breakdown.total_ttc:.2f} €",
                    "standard": f"{variants[QuoteLevel.STANDARD].cost_breakdown.total_ttc:.2f} €",
                    "premium": f"{variants[QuoteLevel.PREMIUM].cost_breakdown.total_ttc:.2f} €"
                },
                {
                    "critere": "Main d'œuvre",
                    "economique": f"{variants[QuoteLevel.ECONOMIQUE].cost_breakdown.labor_cost:.2f} €",
                    "standard": f"{variants[QuoteLevel.STANDARD].cost_breakdown.labor_cost:.2f} €",
                    "premium": f"{variants[QuoteLevel.PREMIUM].cost_breakdown.labor_cost:.2f} €"
                },
                {
                    "critere": "Matériaux",
                    "economique": f"{variants[QuoteLevel.ECONOMIQUE].cost_breakdown.materials_cost:.2f} €",
                    "standard": f"{variants[QuoteLevel.STANDARD].cost_breakdown.materials_cost:.2f} €",
                    "premium": f"{variants[QuoteLevel.PREMIUM].cost_breakdown.materials_cost:.2f} €"
                },
                {
                    "critere": "Durée estimée",
                    "economique": f"{variants[QuoteLevel.ECONOMIQUE].timeline.days_min}-{variants[QuoteLevel.ECONOMIQUE].timeline.days_max} jours",
                    "standard": f"{variants[QuoteLevel.STANDARD].timeline.days_min}-{variants[QuoteLevel.STANDARD].timeline.days_max} jours",
                    "premium": f"{variants[QuoteLevel.PREMIUM].timeline.days_min}-{variants[QuoteLevel.PREMIUM].timeline.days_max} jours"
                },
                {
                    "critere": "Garantie",
                    "economique": f"{variants[QuoteLevel.ECONOMIQUE].warranty_years} an(s)",
                    "standard": f"{variants[QuoteLevel.STANDARD].warranty_years} ans",
                    "premium": f"{variants[QuoteLevel.PREMIUM].warranty_years} ans"
                },
                {
                    "critere": "Qualité matériaux",
                    "economique": "Standard",
                    "standard": "Qualité pro",
                    "premium": "Haut de gamme"
                }
            ]
        }
        
        return table
    
    def explain_differences(self, quote: GeneratedQuote) -> List[str]:
        """Explique les différences entre les 3 devis"""
        
        variants = quote.variants
        explanations = []
        
        eco = variants[QuoteLevel.ECONOMIQUE]
        std = variants[QuoteLevel.STANDARD]
        pre = variants[QuoteLevel.PREMIUM]
        
        # Différence de prix
        eco_total = eco.cost_breakdown.total_ttc
        std_total = std.cost_breakdown.total_ttc
        pre_total = pre.cost_breakdown.total_ttc
        
        diff_eco_std = std_total - eco_total
        diff_std_pre = pre_total - std_total
        
        explanations.append(
            f"La solution Standard coûte {diff_eco_std:.0f}€ de plus que l'Économique "
            f"({(diff_eco_std/eco_total)*100:.0f}% d'écart). Cette différence s'explique principalement "
            f"par des matériaux de meilleure qualité et une garantie plus longue."
        )
        
        explanations.append(
            f"La solution Premium représente un surcoût de {diff_std_pre:.0f}€ par rapport au Standard "
            f"({(diff_std_pre/std_total)*100:.0f}% d'écart). Ce niveau inclut des matériaux haut de gamme, "
            f"une finition soignée et une garantie décennale."
        )
        
        # Différence de main d'œuvre
        labor_eco = eco.cost_breakdown.labor_cost
        labor_std = std.cost_breakdown.labor_cost
        labor_pre = pre.cost_breakdown.labor_cost
        
        explanations.append(
            f"La main d'œuvre varie de {labor_eco:.0f}€ (Économique) à {labor_pre:.0f}€ (Premium). "
            f"Cette différence reflète le niveau d'expertise et le temps consacré aux finitions."
        )
        
        # Différence de matériaux
        mat_eco = eco.cost_breakdown.materials_cost
        mat_std = std.cost_breakdown.materials_cost
        mat_pre = pre.cost_breakdown.materials_cost
        
        explanations.append(
            f"Les matériaux représentent un écart significatif : {mat_eco:.0f}€ (Économique), "
            f"{mat_std:.0f}€ (Standard), {mat_pre:.0f}€ (Premium). "
            f"Les matériaux Premium offrent généralement une durabilité supérieure."
        )
        
        return explanations
    
    def get_personalized_recommendation(self, quote: GeneratedQuote) -> Dict:
        """Génère une recommandation personnalisée"""
        
        comparison = quote.comparison
        variants = quote.variants
        
        recommendation = comparison.value_for_money_recommendation
        variant = variants[recommendation]
        
        return {
            "recommended_level": recommendation.value,
            "recommended_title": variant.title,
            "total_price": variant.cost_breakdown.total_ttc,
            "explanation": comparison.explanation,
            "key_points": [
                f"Prix total : {variant.cost_breakdown.total_ttc:.2f} € TTC",
                f"Garantie : {variant.warranty_years} ans",
                f"Durée estimée : {variant.timeline.days_min}-{variant.timeline.days_max} jours",
                f"Qualité : {variant.materials_quality}"
            ]
        }
