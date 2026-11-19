"""
Moteur de calcul des prix
"""

from typing import Dict, List, Tuple, Optional
from src.models.quote import (
    WorkDescription, QuoteLevel, QuoteVariant, CostBreakdown, 
    TimelineEstimate, QuoteComparison, PriceDistribution
)
from src.models.pricing import PricingZone
from src.data.pricing_database import (
    get_labor_rate, get_material_price, get_work_item,
    get_zone_from_postal_code, WORK_ITEMS_DB
)


class PricingEngine:
    """Moteur de calcul des prix de devis"""
    
    # Multiplicateurs d'urgence
    URGENCY_MULTIPLIERS = {
        "standard": 1.0,
        "express": 1.25,
        "urgent": 1.5
    }
    
    # Multiplicateurs de difficulté (basés sur la description)
    DIFFICULTY_MULTIPLIERS = {
        "simple": 1.0,
        "normal": 1.15,
        "complex": 1.35,
        "very_complex": 1.6
    }
    
    # Garanties par niveau
    WARRANTY_YEARS = {
        "economy": 1,
        "standard": 2,
        "premium": 10
    }
    
    # TVA
    VAT_RATE = 20.0
    
    def __init__(self):
        self.zone_cache = {}
    
    def get_zone(self, postal_code: str) -> PricingZone:
        """Récupère la zone tarifaire (avec cache)"""
        if postal_code not in self.zone_cache:
            self.zone_cache[postal_code] = get_zone_from_postal_code(postal_code)
        return self.zone_cache[postal_code]
    
    def detect_work_items(self, work_description: WorkDescription) -> List[Tuple[str, float]]:
        """
        Détecte les prestations correspondantes à la description
        Retourne une liste de (code_prestation, quantité)
        """
        items = []
        desc_lower = work_description.description.lower()
        work_type = work_description.work_type.value
        
        # Plomberie
        if work_type == "plomberie":
            if "mitigeur" in desc_lower or "robinet" in desc_lower:
                items.append(("remplacement_mitigeur", 1.0))
            if "wc" in desc_lower or "toilette" in desc_lower:
                if "suspendu" in desc_lower:
                    items.append(("installation_wc_suspendu", 1.0))
                else:
                    items.append(("remplacement_wc", 1.0))
            if "lavabo" in desc_lower or "vasque" in desc_lower:
                items.append(("remplacement_lavabo", 1.0))
            if "douche" in desc_lower and "italienne" in desc_lower:
                items.append(("installation_douche_italienne", 1.0))
            if "baignoire" in desc_lower:
                items.append(("remplacement_baignoire", 1.0))
            if "sèche-serviette" in desc_lower or "seche serviette" in desc_lower:
                items.append(("installation_radiateur_ss", 1.0))
            if "fuite" in desc_lower:
                items.append(("reparation_fuite", 2.0))  # 2h estimées
            if "évier" in desc_lower or "evier" in desc_lower:
                items.append(("installation_evier", 1.0))
        
        # Électricité
        elif work_type == "electricite":
            if "prise" in desc_lower:
                # Estimer nombre de prises
                count = desc_lower.count("prise")
                items.append(("ajout_prise", max(1, count)))
            if "tableau" in desc_lower or "disjoncteur" in desc_lower:
                items.append(("remplacement_tableau", 1.0))
            if "spot" in desc_lower or "led" in desc_lower:
                count = desc_lower.count("spot") + desc_lower.count("point")
                items.append(("installation_spots", max(1, count)))
            if "norme" in desc_lower or "mise aux normes" in desc_lower:
                surface = work_description.surface_m2 or 50
                items.append(("mise_aux_normes", surface))
            if "luminaire" in desc_lower or "suspension" in desc_lower:
                items.append(("installation_luminaire", 1.0))
            if "radiateur" in desc_lower and "électrique" in desc_lower:
                items.append(("installation_radiateur_elec", 1.0))
        
        # Peinture
        elif work_type == "peinture":
            surface = work_description.surface_m2
            if surface:
                if "plafond" in desc_lower:
                    items.append(("peinture_plafond", surface * 0.3))  # 30% surface plafond
                if "mur" in desc_lower or "murs" in desc_lower:
                    items.append(("peinture_murs", surface * 2.5))  # 2.5x surface sol
                if "faïence" in desc_lower or "carrelage" in desc_lower:
                    items.append(("peinture_faience", surface * 0.5))
                if "lissage" in desc_lower or "enduit" in desc_lower:
                    items.append(("lissage_murs", surface))
            else:
                # Estimation par défaut
                items.append(("peinture_murs", 30))
        
        # Carrelage
        elif work_type == "carrelage":
            surface = work_description.surface_m2 or 10
            if "mural" in desc_lower or "mur" in desc_lower:
                items.append(("pose_carrelage_mural", surface))
            else:
                items.append(("pose_carrelage_sol", surface))
        
        # Parquet
        elif work_type == "parquet":
            surface = work_description.surface_m2 or 20
            if "stratifié" in desc_lower or "stratifie" in desc_lower:
                items.append(("pose_parquet_stratifie", surface))
            else:
                items.append(("pose_parquet_flottant", surface))
        
        # Menuiserie
        elif work_type == "menuiserie":
            if "porte" in desc_lower:
                count = desc_lower.count("porte")
                items.append(("pose_porte_interieure", max(1, count)))
            if "fenêtre" in desc_lower or "fenetre" in desc_lower:
                items.append(("pose_fenetre", 2.0))  # 2m² par défaut
        
        # Isolation
        elif work_type == "isolation":
            surface = work_description.surface_m2 or 50
            if "comble" in desc_lower or "grenier" in desc_lower:
                items.append(("isolation_combles", surface))
            else:
                items.append(("isolation_murs_interieurs", surface))
        
        # Plâtrerie
        elif work_type == "platerie" or work_type == "plâtrerie":
            surface = work_description.surface_m2 or 20
            items.append(("pose_placo", surface))
        
        # Toiture
        elif work_type == "toiture":
            surface = work_description.surface_m2 or 50
            items.append(("refection_toiture", surface))
        
        # Chauffage
        elif work_type == "chauffage":
            if "chaudière" in desc_lower or "chaudiere" in desc_lower:
                items.append(("installation_chaudiere", 1.0))
        
        # Si aucun item détecté, ajouter une prestation générique basée sur la surface
        if not items and work_description.surface_m2:
            # Estimation générique
            items.append(("peinture_murs", work_description.surface_m2 * 2))
        
        return items
    
    def calculate_difficulty(self, work_description: WorkDescription) -> str:
        """Détecte la difficulté basée sur la description"""
        desc_lower = work_description.description.lower()
        
        indicators_complex = ["démolition", "demolition", "structur", "porteur", "complexe", "difficile"]
        indicators_very_complex = ["maçonnerie", "maconnerie", "fondation", "poutre", "charpente"]
        
        for indicator in indicators_very_complex:
            if indicator in desc_lower:
                return "very_complex"
        
        for indicator in indicators_complex:
            if indicator in desc_lower:
                return "complex"
        
        if work_description.access_constraints:
            return "complex"
        
        return "normal"
    
    def calculate_variant(
        self, 
        work_description: WorkDescription, 
        level: str,
        work_items: List[Tuple[str, float]]
    ) -> QuoteVariant:
        """Calcule une variante de devis"""
        
        zone = self.get_zone(work_description.postal_code)
        labor_rate = get_labor_rate(zone, level)
        
        total_labor_hours = 0.0
        total_materials_cost = 0.0
        
        # Calcul pour chaque prestation
        for item_code, quantity in work_items:
            item = get_work_item(item_code)
            if not item:
                continue
            
            # Heures de travail selon le niveau
            if level == "economy":
                hours = item.labor_hours_economy
            elif level == "standard":
                hours = item.labor_hours_standard
            else:
                hours = item.labor_hours_premium
            
            total_labor_hours += hours * quantity
            
            # Coût matériaux
            for material_code, material_qty in item.materials_needed:
                material_price = get_material_price(material_code, level)
                total_materials_cost += material_price * material_qty * quantity
        
        # Ajustements
        difficulty = self.calculate_difficulty(work_description)
        difficulty_mult = self.DIFFICULTY_MULTIPLIERS.get(difficulty, 1.0)
        urgency_mult = self.URGENCY_MULTIPLIERS.get(work_description.urgency.value, 1.0)
        
        # Calcul des coûts
        labor_cost = total_labor_hours * labor_rate * difficulty_mult * urgency_mult
        
        # Coûts additionnels
        transport_cost = 30.0 * urgency_mult  # Base transport
        disposal_cost = total_labor_hours * 5.0  # Estimation déchets
        equipment_cost = total_labor_hours * 3.0  # Outils/équipement
        
        subtotal_ht = labor_cost + total_materials_cost + transport_cost + disposal_cost + equipment_cost
        
        # Minimum de devis
        if subtotal_ht < 150:
            subtotal_ht = 150
        
        vat_amount = subtotal_ht * (self.VAT_RATE / 100)
        total_ttc = subtotal_ht + vat_amount
        
        # Durée estimée
        days_min = max(1, int(total_labor_hours / 8))
        days_max = max(days_min + 1, int(total_labor_hours / 6))
        
        # Titres et descriptions par niveau
        titles = {
            "economy": "Solution Économique",
            "standard": "Solution Standard",
            "premium": "Solution Premium"
        }
        descriptions = {
            "economy": "Solution économique avec matériaux standards et garantie limitée",
            "standard": "Solution équilibrée avec matériaux de qualité et garantie standard",
            "premium": "Solution haut de gamme avec matériaux premium et garantie étendue"
        }
        qualities = {
            "economy": "Matériaux standards, entrée de gamme",
            "standard": "Matériaux de qualité professionnelle",
            "premium": "Matériaux haut de gamme et premium"
        }
        
        # Services inclus/exclus
        if level == "economy":
            included = ["Main d'œuvre", "Matériaux standards", "Nettoyage de fin de chantier"]
            excluded = ["Déplacement des meubles", "Protection des sols", "Garantie décennale"]
        elif level == "standard":
            included = ["Main d'œuvre qualifiée", "Matériaux de qualité", "Protection des sols", "Garantie 2 ans"]
            excluded = ["Déplacement des meubles lourds", "Travaux annexes"]
        else:
            included = ["Main d'œuvre experte", "Matériaux premium", "Protection complète", "Garantie 10 ans", "Conseil personnalisé"]
            excluded = []
        
        return QuoteVariant(
            level=QuoteLevel(level),
            title=titles[level],
            description=descriptions[level],
            materials_quality=qualities[level],
            cost_breakdown=CostBreakdown(
                labor_cost=round(labor_cost, 2),
                materials_cost=round(total_materials_cost, 2),
                equipment_cost=round(equipment_cost, 2),
                disposal_cost=round(disposal_cost, 2),
                transport_cost=round(transport_cost, 2),
                subtotal_ht=round(subtotal_ht, 2),
                vat_rate=self.VAT_RATE,
                vat_amount=round(vat_amount, 2),
                total_ttc=round(total_ttc, 2)
            ),
            timeline=TimelineEstimate(
                days_min=days_min,
                days_max=days_max,
                total_hours_estimate=int(total_labor_hours)
            ),
            warranty_years=self.WARRANTY_YEARS[level],
            included_services=included,
            excluded_services=excluded
        )
    
    def generate_comparison(self, variants: Dict[QuoteLevel, QuoteVariant]) -> QuoteComparison:
        """Génère la comparaison entre les 3 devis"""
        
        eco = variants[QuoteLevel.ECONOMIQUE]
        std = variants[QuoteLevel.STANDARD]
        pre = variants[QuoteLevel.PREMIUM]
        
        eco_total = eco.cost_breakdown.total_ttc
        std_total = std.cost_breakdown.total_ttc
        pre_total = pre.cost_breakdown.total_ttc
        
        diff_eco_std = std_total - eco_total
        diff_std_pre = pre_total - std_total
        savings = pre_total - eco_total
        
        # Scores qualité
        quality_eco = 60
        quality_std = 80
        quality_pre = 95
        
        # Recommandation
        if std_total <= eco_total * 1.3:  # Standard à moins de 30% plus cher
            recommendation = QuoteLevel.STANDARD
            explanation = "La solution Standard offre le meilleur rapport qualité/prix avec des matériaux de qualité professionnelle."
        elif eco_total > 5000 and savings / eco_total < 0.4:  # Gros chantier, écart < 40%
            recommendation = QuoteLevel.PREMIUM
            explanation = "Pour ce chantier conséquent, l'investissement dans la solution Premium est rentabilisé par la durabilité et la garantie étendue."
        else:
            recommendation = QuoteLevel.STANDARD
            explanation = "La solution Standard reste le choix le plus équilibré pour la plupart des projets."
        
        return QuoteComparison(
            price_difference_economy_to_standard=round(diff_eco_std, 2),
            price_difference_standard_to_premium=round(diff_std_pre, 2),
            savings_economy_vs_premium=round(savings, 2),
            quality_score_economy=quality_eco,
            quality_score_standard=quality_std,
            quality_score_premium=quality_pre,
            value_for_money_recommendation=recommendation,
            explanation=explanation
        )
    
    def generate_price_distribution(self, variant: QuoteVariant) -> PriceDistribution:
        """Génère la répartition des prix pour graphique"""
        cb = variant.cost_breakdown
        
        return PriceDistribution(
            labels=["Main d'œuvre", "Matériaux", "Équipement", "Évacuation", "Transport"],
            values=[
                cb.labor_cost,
                cb.materials_cost,
                cb.equipment_cost,
                cb.disposal_cost,
                cb.transport_cost
            ],
            colors=["#3B82F6", "#10B981", "#F59E0B", "#EF4444", "#8B5CF6"]
        )
