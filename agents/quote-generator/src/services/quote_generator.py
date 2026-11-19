"""
Service de génération de devis
"""

import uuid
from typing import Optional, Dict, List
from datetime import datetime

from src.models.quote import (
    WorkDescription, GeneratedQuote, QuoteLevel, QuoteVariant,
    QuoteRequest, QuoteResponse, QuoteStorage, PriceDistribution
)
from src.services.pricing_engine import PricingEngine


class QuoteGenerator:
    """Générateur de devis TrustDevis"""
    
    def __init__(self):
        self.pricing_engine = PricingEngine()
        self.storage = QuoteStorage()
        
        # Profils types d'artisans par niveau
        self.artisan_profiles = {
            QuoteLevel.ECONOMIQUE: "Artisan indépendant, petites structures, tarifs compétitifs",
            QuoteLevel.STANDARD: "Artisan confirmé, entreprise locale, bon rapport qualité/prix",
            QuoteLevel.PREMIUM: "Entreprise réputée, certifications, service premium"
        }
    
    def generate_quote(self, request: QuoteRequest) -> QuoteResponse:
        """Génère un devis complet à partir d'une demande"""
        
        try:
            work_desc = request.work_description
            
            # Détection des prestations
            work_items = self.pricing_engine.detect_work_items(work_desc)
            
            if not work_items:
                return QuoteResponse(
                    success=False,
                    message="Impossible d'identifier les travaux demandés. Veuillez fournir plus de détails.",
                    estimated_accuracy=0
                )
            
            # Génération des 3 variantes
            variants = {}
            for level in ["economy", "standard", "premium"]:
                variant = self.pricing_engine.calculate_variant(work_desc, level, work_items)
                variants[variant.level] = variant
            
            # Comparaison
            comparison = self.pricing_engine.generate_comparison(variants)
            
            # Répartition des prix
            price_distribution = {}
            for level, variant in variants.items():
                price_distribution[level] = self.pricing_engine.generate_price_distribution(variant)
            
            # Recommandations personnalisées
            recommendations = self._generate_recommendations(work_desc, variants, comparison)
            
            # Prochaines étapes
            next_steps = [
                "Comparez ces estimations avec les devis que vous recevrez",
                "Vérifiez que tous les artisans ont bien compris votre besoin",
                "Demandez des références et vérifiez les assurances",
                "Négociez en vous appuyant sur ces chiffrages de référence"
            ]
            
            # Création du devis
            quote = GeneratedQuote(
                id=str(uuid.uuid4())[:8],
                work_description=work_desc,
                variants=variants,
                comparison=comparison,
                price_distribution=price_distribution,
                artisan_profiles=self.artisan_profiles,
                recommendations=recommendations,
                next_steps=next_steps
            )
            
            # Stockage
            self.storage.add_quote(quote)
            
            # Calcul de la fiabilité
            accuracy = self._calculate_accuracy(work_desc, work_items)
            
            return QuoteResponse(
                success=True,
                quote=quote,
                message="Devis généré avec succès",
                estimated_accuracy=accuracy
            )
            
        except Exception as e:
            return QuoteResponse(
                success=False,
                message=f"Erreur lors de la génération: {str(e)}",
                estimated_accuracy=0
            )
    
    def _generate_recommendations(
        self, 
        work_desc: WorkDescription, 
        variants: Dict[QuoteLevel, QuoteVariant],
        comparison: 'QuoteComparison'
    ) -> List[str]:
        """Génère des recommandations personnalisées"""
        
        recommendations = []
        
        # Recommandation basée sur le budget
        if work_desc.budget_indicative:
            eco_total = variants[QuoteLevel.ECONOMIQUE].cost_breakdown.total_ttc
            std_total = variants[QuoteLevel.STANDARD].cost_breakdown.total_ttc
            
            if work_desc.budget_indicative < eco_total:
                recommendations.append(f"Votre budget semble inférieur aux estimations. Envisagez de réduire la surface ou d'étaler les travaux.")
            elif work_desc.budget_indicative >= std_total:
                recommendations.append("Votre budget permet d'envisager la solution Standard pour un bon équilibre qualité/prix.")
        
        # Recommandation basée sur l'urgence
        if work_desc.urgency.value == "urgent":
            recommendations.append("En cas d'urgence, privilégiez des artisans disponibles rapidement même si le tarif est légèrement supérieur.")
        
        # Recommandation basée sur la comparaison
        if comparison.savings_economy_vs_premium > variants[QuoteLevel.ECONOMIQUE].cost_breakdown.total_ttc * 0.5:
            recommendations.append("L'écart entre les solutions est significatif. Demandez des devis détaillés pour comprendre les différences.")
        
        # Recommandation générale
        recommendations.append(f"Solution recommandée : {comparison.value_for_money_recommendation.value}")
        
        return recommendations
    
    def _calculate_accuracy(self, work_desc: WorkDescription, work_items: List) -> int:
        """Calcule la fiabilité estimée du devis"""
        
        accuracy = 70  # Base
        
        # Plus de détails = plus précis
        if work_desc.surface_m2:
            accuracy += 10
        if work_desc.dimensions:
            accuracy += 5
        if len(work_desc.description) > 100:
            accuracy += 5
        
        # Présence de plusieurs prestations identifiées
        if len(work_items) > 1:
            accuracy += 5
        
        # Urgence réduit la précision (souvent plus cher)
        if work_desc.urgency.value == "urgent":
            accuracy -= 10
        
        return min(95, max(50, accuracy))
    
    def get_quote(self, quote_id: str) -> Optional[GeneratedQuote]:
        """Récupère un devis par son ID"""
        return self.storage.get_quote(quote_id)
    
    def analyze_existing_quote(
        self, 
        quote_id: str, 
        received_amount: float,
        details: Optional[str] = None
    ) -> Dict:
        """Analyse un devis reçu par rapport à notre estimation"""
        
        quote = self.get_quote(quote_id)
        if not quote:
            return {"error": "Devis non trouvé"}
        
        std_total = quote.variants[QuoteLevel.STANDARD].cost_breakdown.total_ttc
        eco_total = quote.variants[QuoteLevel.ECONOMIQUE].cost_breakdown.total_ttc
        pre_total = quote.variants[QuoteLevel.PREMIUM].cost_breakdown.total_ttc
        
        analysis = {
            "received_amount": received_amount,
            "our_estimate_standard": std_total,
            "difference": round(received_amount - std_total, 2),
            "difference_percent": round(((received_amount - std_total) / std_total) * 100, 1),
            "within_range": eco_total <= received_amount <= pre_total,
            "assessment": ""
        }
        
        if analysis["within_range"]:
            analysis["assessment"] = "Le devis reçu est dans la fourchette de nos estimations."
        elif received_amount < eco_total:
            analysis["assessment"] = "Le devis est inférieur à notre estimation économique. Vérifiez la qualité des matériaux et la garantie."
        else:
            analysis["assessment"] = "Le devis est supérieur à notre estimation premium. Demandez un détail des coûts."
        
        return analysis
