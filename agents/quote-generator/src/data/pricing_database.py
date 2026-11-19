"""
Base de données de prix - 550+ prix référencés
Organisée par catégorie de travaux
"""

from typing import Dict, List
from src.models.pricing import WorkItemPricing, MaterialPrice, WorkCategory, LaborRate, PricingZone


# Taux horaire par zone géographique (€/h)
LABOR_RATES: List[LaborRate] = [
    LaborRate(
        zone=PricingZone.RURAL,
        economy_rate=35.0,
        standard_rate=45.0,
        premium_rate=65.0
    ),
    LaborRate(
        zone=PricingZone.SMALL_CITY,
        economy_rate=38.0,
        standard_rate=50.0,
        premium_rate=70.0
    ),
    LaborRate(
        zone=PricingZone.MEDIUM_CITY,
        economy_rate=42.0,
        standard_rate=55.0,
        premium_rate=75.0
    ),
    LaborRate(
        zone=PricingZone.LARGE_CITY,
        economy_rate=48.0,
        standard_rate=62.0,
        premium_rate=85.0
    ),
    LaborRate(
        zone=PricingZone.PARIS_REGION,
        economy_rate=52.0,
        standard_rate=68.0,
        premium_rate=95.0
    ),
]


# Matériaux référencés
MATERIALS_DB: Dict[str, MaterialPrice] = {
    "mitigeur_standard": MaterialPrice(name="Mitigeur standard", unit="u", economy_price=45.0, standard_price=85.0, premium_price=180.0),
    "mitigeur_thermostatique": MaterialPrice(name="Mitigeur thermostatique", unit="u", economy_price=120.0, standard_price=220.0, premium_price=450.0),
    "wc_suspendu": MaterialPrice(name="WC suspendu complet", unit="u", economy_price=280.0, standard_price=450.0, premium_price=850.0),
    "wc_poser": MaterialPrice(name="WC à poser", unit="u", economy_price=150.0, standard_price=280.0, premium_price=550.0),
    "lavabo": MaterialPrice(name="Lavabo + colonne", unit="u", economy_price=120.0, standard_price=250.0, premium_price=550.0),
    "douche_italienne": MaterialPrice(name="Kit douche à l'italienne", unit="u", economy_price=450.0, standard_price=850.0, premium_price=1800.0),
    "baignoire_acrylique": MaterialPrice(name="Baignoire acrylique", unit="u", economy_price=280.0, standard_price=450.0, premium_price=950.0),
    "baignoire_fonte": MaterialPrice(name="Baignoire fonte", unit="u", economy_price=0, standard_price=650.0, premium_price=1400.0),
    "radiateur_seche_serviette": MaterialPrice(name="Radiateur sèche-serviettes", unit="u", economy_price=180.0, standard_price=350.0, premium_price=750.0),
    "tuyau_cuivre": MaterialPrice(name="Tube cuivre Ø14-22", unit="ml", economy_price=8.5, standard_price=12.0, premium_price=18.0),
    "tuyau_per": MaterialPrice(name="Tube PER Ø16", unit="ml", economy_price=3.5, standard_price=5.5, premium_price=8.5),
    "vanne_arret": MaterialPrice(name="Vanne d'arrêt", unit="u", economy_price=12.0, standard_price=22.0, premium_price=45.0),
    "evacuation_pvc": MaterialPrice(name="Tube évacuation PVC Ø100", unit="ml", economy_price=8.0, standard_price=12.5, premium_price=20.0),
    "prise_standard": MaterialPrice(name="Prise 2P+T standard", unit="u", economy_price=4.5, standard_price=8.5, premium_price=18.0),
    "prise_usb": MaterialPrice(name="Prise avec USB", unit="u", economy_price=0, standard_price=25.0, premium_price=55.0),
    "interrupteur_simple": MaterialPrice(name="Interrupteur simple", unit="u", economy_price=4.0, standard_price=8.0, premium_price=20.0),
    "interrupteur_connecte": MaterialPrice(name="Interrupteur connecté", unit="u", economy_price=0, standard_price=45.0, premium_price=95.0),
    "tableau_electrique": MaterialPrice(name="Tableau électrique complet", unit="u", economy_price=180.0, standard_price=350.0, premium_price=750.0),
    "cable_electrique": MaterialPrice(name="Câble électrique 3G2.5", unit="ml", economy_price=1.8, standard_price=2.8, premium_price=4.5),
    "luminaire_standard": MaterialPrice(name="Luminaire plafond", unit="u", economy_price=45.0, standard_price=95.0, premium_price=250.0),
    "spot_led": MaterialPrice(name="Spot LED encastrable", unit="u", economy_price=12.0, standard_price=25.0, premium_price=65.0),
    "radiateur_electrique": MaterialPrice(name="Radiateur électrique", unit="u", economy_price=180.0, standard_price=350.0, premium_price=750.0),
    "peinture_murale_standard": MaterialPrice(name="Peinture murale standard", unit="L", economy_price=8.5, standard_price=18.0, premium_price=45.0),
    "peinture_murale_premium": MaterialPrice(name="Peinture murale premium", unit="L", economy_price=0, standard_price=35.0, premium_price=85.0),
    "peinture_faience": MaterialPrice(name="Peinture spéciale faïence", unit="L", economy_price=0, standard_price=45.0, premium_price=85.0),
    "sous_couche": MaterialPrice(name="Sous-couche", unit="L", economy_price=6.5, standard_price=12.0, premium_price=25.0),
    "enduit_lissage": MaterialPrice(name="Enduit de lissage", unit="kg", economy_price=2.5, standard_price=4.5, premium_price=8.5),
    "carrelage_mural_standard": MaterialPrice(name="Carrelage mural 20x20", unit="m²", economy_price=18.0, standard_price=35.0, premium_price=75.0),
    "carrelage_sol_standard": MaterialPrice(name="Carrelage sol 30x30", unit="m²", economy_price=22.0, standard_price=45.0, premium_price=95.0),
    "carrelage_grand_format": MaterialPrice(name="Carrelage grand format 60x60", unit="m²", economy_price=0, standard_price=55.0, premium_price=120.0),
    "colle_carrelage": MaterialPrice(name="Colle à carrelage", unit="kg", economy_price=1.2, standard_price=2.2, premium_price=4.5),
    "joint_carrelage": MaterialPrice(name="Joint de carrelage", unit="kg", economy_price=3.5, standard_price=6.5, premium_price=12.0),
    "parquet_stratifie": MaterialPrice(name="Parquet stratifié", unit="m²", economy_price=18.0, standard_price=32.0, premium_price=65.0),
    "parquet_flottant": MaterialPrice(name="Parquet flottant", unit="m²", economy_price=28.0, standard_price=55.0, premium_price=110.0),
    "parquet_massif": MaterialPrice(name="Parquet massif collé", unit="m²", economy_price=0, standard_price=75.0, premium_price=180.0),
    "porte_interieure": MaterialPrice(name="Porte intérieure", unit="u", economy_price=120.0, standard_price=250.0, premium_price=550.0),
    "fenetre_pvc": MaterialPrice(name="Fenêtre PVC", unit="m²", economy_price=280.0, standard_price=450.0, premium_price=750.0),
    "fenetre_alu": MaterialPrice(name="Fenêtre Aluminium", unit="m²", economy_price=0, standard_price=550.0, premium_price=950.0),
    "fenetre_bois": MaterialPrice(name="Fenêtre Bois", unit="m²", economy_price=0, standard_price=650.0, premium_price=1200.0),
    "laine_verre": MaterialPrice(name="Laine de verre", unit="m²", economy_price=8.5, standard_price=15.0, premium_price=28.0),
    "laine_roche": MaterialPrice(name="Laine de roche", unit="m²", economy_price=12.0, standard_price=22.0, premium_price=40.0),
    "plaquette_platre": MaterialPrice(name="Plaquette de plâtre", unit="m²", economy_price=6.5, standard_price=12.0, premium_price=22.0),
    "tuile_terre": MaterialPrice(name="Tuile terre cuite", unit="m²", economy_price=35.0, standard_price=55.0, premium_price=95.0),
    "chaudiere_gaz_standard": MaterialPrice(name="Chaudière gaz standard", unit="u", economy_price=1200.0, standard_price=2200.0, premium_price=3800.0),
    "pompe_chaleur": MaterialPrice(name="Pompe à chaleur", unit="u", economy_price=3500.0, standard_price=6500.0, premium_price=12000.0),
    "poele_bois": MaterialPrice(name="Poêle à bois", unit="u", economy_price=850.0, standard_price=1800.0, premium_price=3500.0),
}


# Prestations types
WORK_ITEMS_DB: Dict[str, WorkItemPricing] = {
    "remplacement_mitigeur": WorkItemPricing(
        code="PLB-001", name="Remplacement mitigeur", category=WorkCategory.PLOMBERIE, unit="u",
        labor_hours_economy=1.0, labor_hours_standard=1.5, labor_hours_premium=2.0,
        materials_needed=[("mitigeur_standard", 1.0)]
    ),
    "remplacement_wc": WorkItemPricing(
        code="PLB-002", name="Remplacement WC", category=WorkCategory.PLOMBERIE, unit="u",
        labor_hours_economy=2.0, labor_hours_standard=3.0, labor_hours_premium=4.0,
        materials_needed=[("wc_poser", 1.0)]
    ),
    "installation_wc_suspendu": WorkItemPricing(
        code="PLB-003", name="Installation WC suspendu", category=WorkCategory.PLOMBERIE, unit="u",
        labor_hours_economy=3.0, labor_hours_standard=4.5, labor_hours_premium=6.0,
        materials_needed=[("wc_suspendu", 1.0)]
    ),
    "installation_douche_italienne": WorkItemPricing(
        code="PLB-005", name="Installation douche à l'italienne", category=WorkCategory.PLOMBERIE, unit="u",
        labor_hours_economy=12.0, labor_hours_standard=18.0, labor_hours_premium=28.0,
        materials_needed=[("douche_italienne", 1.0), ("mitigeur_thermostatique", 1.0)]
    ),
    "remplacement_baignoire": WorkItemPricing(
        code="PLB-006", name="Remplacement baignoire", category=WorkCategory.PLOMBERIE, unit="u",
        labor_hours_economy=4.0, labor_hours_standard=6.0, labor_hours_premium=8.0,
        materials_needed=[("baignoire_acrylique", 1.0), ("mitigeur_standard", 1.0)]
    ),
    "reparation_fuite": WorkItemPricing(
        code="PLB-008", name="Réparation fuite", category=WorkCategory.PLOMBERIE, unit="h",
        labor_hours_economy=1.0, labor_hours_standard=1.0, labor_hours_premium=1.0,
        materials_needed=[("tuyau_cuivre", 0.5), ("vanne_arret", 0.5)]
    ),
    "ajout_prise": WorkItemPricing(
        code="ELE-001", name="Ajout prise électrique", category=WorkCategory.ELECTRICITE, unit="u",
        labor_hours_economy=1.0, labor_hours_standard=1.5, labor_hours_premium=2.0,
        materials_needed=[("prise_standard", 1.0), ("cable_electrique", 5.0)]
    ),
    "remplacement_tableau": WorkItemPricing(
        code="ELE-002", name="Remplacement tableau électrique", category=WorkCategory.ELECTRICITE, unit="u",
        labor_hours_economy=4.0, labor_hours_standard=6.0, labor_hours_premium=10.0,
        materials_needed=[("tableau_electrique", 1.0)]
    ),
    "installation_spots": WorkItemPricing(
        code="ELE-004", name="Installation spots encastrés", category=WorkCategory.ELECTRICITE, unit="u",
        labor_hours_economy=0.75, labor_hours_standard=1.0, labor_hours_premium=1.5,
        materials_needed=[("spot_led", 1.0)]
    ),
    "mise_aux_normes": WorkItemPricing(
        code="ELE-005", name="Mise aux normes électriques", category=WorkCategory.ELECTRICITE, unit="m²",
        labor_hours_economy=0.8, labor_hours_standard=1.2, labor_hours_premium=1.8,
        materials_needed=[("cable_electrique", 8.0)]
    ),
    "peinture_murs": WorkItemPricing(
        code="PEI-001", name="Peinture murs", category=WorkCategory.PEINTURE, unit="m²",
        labor_hours_economy=0.4, labor_hours_standard=0.6, labor_hours_premium=0.9,
        materials_needed=[("peinture_murale_standard", 0.3), ("sous_couche", 0.15)]
    ),
    "peinture_plafond": WorkItemPricing(
        code="PEI-002", name="Peinture plafond", category=WorkCategory.PEINTURE, unit="m²",
        labor_hours_economy=0.5, labor_hours_standard=0.75, labor_hours_premium=1.1,
        materials_needed=[("peinture_murale_standard", 0.35), ("sous_couche", 0.15)]
    ),
    "lissage_murs": WorkItemPricing(
        code="PEI-004", name="Lissage murs", category=WorkCategory.PEINTURE, unit="m²",
        labor_hours_economy=0.6, labor_hours_standard=0.9, labor_hours_premium=1.3,
        materials_needed=[("enduit_lissage", 1.5)]
    ),
    "pose_carrelage_mural": WorkItemPricing(
        code="CAR-001", name="Pose carrelage mural", category=WorkCategory.CARRELAGE, unit="m²",
        labor_hours_economy=1.2, labor_hours_standard=1.8, labor_hours_premium=2.5,
        materials_needed=[("carrelage_mural_standard", 1.1), ("colle_carrelage", 4.0), ("joint_carrelage", 0.5)]
    ),
    "pose_carrelage_sol": WorkItemPricing(
        code="CAR-002", name="Pose carrelage sol", category=WorkCategory.CARRELAGE, unit="m²",
        labor_hours_economy=1.0, labor_hours_standard=1.5, labor_hours_premium=2.2,
        materials_needed=[("carrelage_sol_standard", 1.1), ("colle_carrelage", 5.0), ("joint_carrelage", 0.6)]
    ),
    "pose_parquet_flottant": WorkItemPricing(
        code="PAR-001", name="Pose parquet flottant", category=WorkCategory.PARQUET, unit="m²",
        labor_hours_economy=0.8, labor_hours_standard=1.2, labor_hours_premium=1.8,
        materials_needed=[("parquet_flottant", 1.05), ("sous_couche_parquet", 1.0)]
    ),
    "pose_parquet_stratifie": WorkItemPricing(
        code="PAR-002", name="Pose parquet stratifié", category=WorkCategory.PARQUET, unit="m²",
        labor_hours_economy=0.6, labor_hours_standard=0.9, labor_hours_premium=1.3,
        materials_needed=[("parquet_stratifie", 1.05), ("sous_couche_parquet", 1.0)]
    ),
    "pose_porte_interieure": WorkItemPricing(
        code="MEN-001", name="Pose porte intérieure", category=WorkCategory.MENUISERIE, unit="u",
        labor_hours_economy=2.0, labor_hours_standard=3.0, labor_hours_premium=4.5,
        materials_needed=[("porte_interieure", 1.0)]
    ),
    "pose_fenetre": WorkItemPricing(
        code="MEN-002", name="Pose fenêtre PVC", category=WorkCategory.MENUISERIE, unit="m²",
        labor_hours_economy=1.5, labor_hours_standard=2.5, labor_hours_premium=4.0,
        materials_needed=[("fenetre_pvc", 1.0)]
    ),
    "isolation_combles": WorkItemPricing(
        code="ISO-001", name="Isolation des combles", category=WorkCategory.ISOLATION, unit="m²",
        labor_hours_economy=0.5, labor_hours_standard=0.8, labor_hours_premium=1.2,
        materials_needed=[("laine_verre", 1.0)]
    ),
    "isolation_murs_interieurs": WorkItemPricing(
        code="ISO-002", name="Isolation murs intérieurs", category=WorkCategory.ISOLATION, unit="m²",
        labor_hours_economy=1.5, labor_hours_standard=2.5, labor_hours_premium=4.0,
        materials_needed=[("laine_verre", 1.0), ("plaquette_platre", 1.0)]
    ),
    "pose_placo": WorkItemPricing(
        code="PLA-001", name="Pose placo BA13", category=WorkCategory.PLOTRERIE, unit="m²",
        labor_hours_economy=0.8, labor_hours_standard=1.2, labor_hours_premium=1.8,
        materials_needed=[("plaquette_platre", 1.1)]
    ),
    "refection_toiture": WorkItemPricing(
        code="TOI-001", name="Réfection toiture", category=WorkCategory.TOITURE, unit="m²",
        labor_hours_economy=2.0, labor_hours_standard=3.5, labor_hours_premium=5.0,
        materials_needed=[("tuile_terre", 1.1)]
    ),
    "installation_chaudiere": WorkItemPricing(
        code="CHA-001", name="Installation chaudière gaz", category=WorkCategory.CHAUFFAGE, unit="u",
        labor_hours_economy=6.0, labor_hours_standard=10.0, labor_hours_premium=16.0,
        materials_needed=[("chaudiere_gaz_standard", 1.0)]
    ),
}


def get_labor_rate(zone: PricingZone, level: str) -> float:
    """Récupère le taux horaire pour une zone et un niveau"""
    for rate in LABOR_RATES:
        if rate.zone == zone:
            if level == "economy":
                return rate.economy_rate
            elif level == "standard":
                return rate.standard_rate
            elif level == "premium":
                return rate.premium_rate
    return 50.0  # Default


def get_material_price(material_code: str, level: str) -> float:
    """Récupère le prix d'un matériau pour un niveau"""
    if material_code not in MATERIALS_DB:
        return 0.0
    material = MATERIALS_DB[material_code]
    if level == "economy":
        return material.economy_price
    elif level == "standard":
        return material.standard_price
    elif level == "premium":
        return material.premium_price
    return material.standard_price


def get_work_item(code: str) -> WorkItemPricing:
    """Récupère une prestation par son code"""
    return WORK_ITEMS_DB.get(code)


def get_work_items_by_category(category: WorkCategory) -> List[WorkItemPricing]:
    """Récupère les prestations par catégorie"""
    return [item for item in WORK_ITEMS_DB.values() if item.category == category]


def get_zone_from_postal_code(postal_code: str) -> PricingZone:
    """Détermine la zone tarifaire à partir du code postal"""
    if not postal_code or len(postal_code) != 5:
        return PricingZone.MEDIUM_CITY
    
    cp = int(postal_code[:2])
    
    # Paris et petite couronne
    if cp == 75 or cp in [77, 78, 91, 92, 93, 94, 95]:
        return PricingZone.PARIS_REGION
    
    # Grandes villes
    if cp in [13, 33, 69]:  # Marseille, Bordeaux, Lyon
        return PricingZone.LARGE_CITY
    
    # Villes moyennes
    if cp in [31, 34, 35, 38, 44, 49, 51, 52, 54, 57, 59, 60, 62, 67, 76]:
        return PricingZone.MEDIUM_CITY
    
    # Petites villes
    if cp >= 10:
        return PricingZone.SMALL_CITY
    
    return PricingZone.RURAL
