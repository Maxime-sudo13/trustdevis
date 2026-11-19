"""
Dictionnaire des catégories TrustDevis
"""

from typing import Dict, List, Tuple

BUILDING_CATEGORIES = {
    "painting.m2": {
        "name": "Peinture au m²",
        "unit": "m2",
        "keywords": ["peinture", "peint", "peindre", "sous-couche", "enduit", "lasure", "mural", "mur", "plafond", "facade", "boiserie"],
        "exclude": ["papier peint", "toile de verre"]
    },
    "painting.room": {
        "name": "Peinture forfait pièce",
        "unit": "item",
        "keywords": ["peinture complete", "peinture chambre", "peinture salon", "forfait peinture"],
        "exclude": []
    },
    "plumbing.fix": {
        "name": "Intervention plomberie",
        "unit": "unit",
        "keywords": ["robinet", "mitigeur", "evier", "lavabo", "wc", "toilette", "siphon", "fuite", "debouchage", "changement"],
        "exclude": []
    },
    "plumbing.install": {
        "name": "Installation sanitaire",
        "unit": "unit",
        "keywords": ["installation", "douche", "baignoire", "chauffe-eau", "cumulus"],
        "exclude": []
    },
    "plumbing.hour": {
        "name": "Main d'œuvre plomberie",
        "unit": "hour",
        "keywords": ["heure plombier", "heure plomberie", "mo plomberie"],
        "exclude": []
    },
    "roofing.m2": {
        "name": "Toiture au m²",
        "unit": "m2",
        "keywords": ["toiture", "tuile", "ardoise", "zinc", "etancheite", "gouttiere"],
        "exclude": []
    },
    "electricity.point": {
        "name": "Point électrique",
        "unit": "unit",
        "keywords": ["point", "prise", "interrupteur", "va-et-vient", "appareillage"],
        "exclude": []
    },
    "electricity.light": {
        "name": "Éclairage / Luminaire",
        "unit": "unit",
        "keywords": ["luminaire", "spot", "plafonnier", "applique", "led", "ampoule"],
        "exclude": []
    },
    "electricity.panel": {
        "name": "Tableau électrique",
        "unit": "unit",
        "keywords": ["tableau", "disjoncteur", "coffret", "repiquage"],
        "exclude": []
    },
    "tiling.m2": {
        "name": "Carrelage au m²",
        "unit": "m2",
        "keywords": ["carrelage", "faience", "mosaique", "carreau", "joint"],
        "exclude": []
    },
    "flooring.m2": {
        "name": "Parquet / Sol souple au m²",
        "unit": "m2",
        "keywords": ["parquet", "stratifie", "flottant", "pvc", "lino", "moquette"],
        "exclude": []
    },
    "plastering.m2": {
        "name": "Plâtrerie / Placo au m²",
        "unit": "m2",
        "keywords": ["placo", "platre", "ba13", "faux plafond", "enduit"],
        "exclude": []
    },
    "insulation.m2": {
        "name": "Isolation au m²",
        "unit": "m2",
        "keywords": ["isolation", "laine de verre", "polystyrene", "combles"],
        "exclude": []
    },
    "carpentry.door": {
        "name": "Porte / Portail",
        "unit": "unit",
        "keywords": ["porte", "portail", "bloc porte", "serrure"],
        "exclude": []
    },
    "carpentry.window": {
        "name": "Fenêtre / Ouverture",
        "unit": "unit",
        "keywords": ["fenetre", "baie", "velux", "volet"],
        "exclude": []
    },
    "masonry.m2": {
        "name": "Maçonnerie au m²",
        "unit": "m2",
        "keywords": ["maconnerie", "mur", "parpaing", "brique", "cloison"],
        "exclude": []
    },
    "demolition.m2": {
        "name": "Démolition au m²",
        "unit": "m2",
        "keywords": ["demolition", "depose", "enlevement", "cassage"],
        "exclude": []
    },
    "labor.hour": {
        "name": "Main d'œuvre générale",
        "unit": "hour",
        "keywords": ["main d'oeuvre", "heure ouvrier", "mo generale"],
        "exclude": ["plomberie", "electricite"]
    },
    "fees.fixed": {
        "name": "Frais fixes",
        "unit": "unit",
        "keywords": ["deplacement", "diagnostic", "devis", "etude"],
        "exclude": []
    },
}

MECHANIC_CATEGORIES = {
    "brakes.unit": {
        "name": "Freinage",
        "unit": "unit",
        "keywords": ["frein", "plaquette", "disque", "tambour", "etrier"],
        "exclude": []
    },
    "oil.change": {
        "name": "Vidange",
        "unit": "unit",
        "keywords": ["vidange", "huile moteur", "filtre a huile", "revision"],
        "exclude": []
    },
    "tires.unit": {
        "name": "Pneus / Roues",
        "unit": "unit",
        "keywords": ["pneu", "montage pneu", "equilibrage", "jante", "roue"],
        "exclude": []
    },
    "engine.parts": {
        "name": "Pièces moteur",
        "unit": "unit",
        "keywords": ["courroie", "kit distribution", "bougie", "filtre air", "batterie"],
        "exclude": []
    },
    "exhaust.unit": {
        "name": "Échappement",
        "unit": "unit",
        "keywords": ["echappement", "pot", "silencieux", "catalyseur"],
        "exclude": []
    },
    "clutch.unit": {
        "name": "Embrayage",
        "unit": "unit",
        "keywords": ["embrayage", "kit embrayage", "butee"],
        "exclude": []
    },
    "suspension.unit": {
        "name": "Suspension",
        "unit": "unit",
        "keywords": ["suspension", "amortisseur", "ressort", "rotule"],
        "exclude": []
    },
    "cooling.unit": {
        "name": "Refroidissement",
        "unit": "unit",
        "keywords": ["radiateur", "liquide refroidissement", "durite", "pompe a eau"],
        "exclude": []
    },
    "ac.unit": {
        "name": "Climatisation",
        "unit": "unit",
        "keywords": ["climatisation", "recharge clim", "compresseur clim"],
        "exclude": []
    },
    "electrical.unit": {
        "name": "Électricité auto",
        "unit": "unit",
        "keywords": ["alternateur", "demarreur", "batterie", "ampoule"],
        "exclude": []
    },
    "bodywork.unit": {
        "name": "Carrosserie",
        "unit": "unit",
        "keywords": ["carrosserie", "pare-choc", "capot", "porte"],
        "exclude": []
    },
    "labor.hour": {
        "name": "Main d'œuvre mécanique",
        "unit": "hour",
        "keywords": ["main d'oeuvre", "heure mecanicien", "mo garage"],
        "exclude": []
    },
}

ALL_CATEGORIES = {**BUILDING_CATEGORIES, **MECHANIC_CATEGORIES}

SECTOR_MAP = {
    "building": BUILDING_CATEGORIES,
    "mechanic": MECHANIC_CATEGORIES,
}

def get_category_info(category_id: str) -> dict:
    return ALL_CATEGORIES.get(category_id, {})

def get_categories_by_sector(sector: str) -> dict:
    return SECTOR_MAP.get(sector.lower(), ALL_CATEGORIES)

# Catégories supplémentaires pour une meilleure couverture

# Bâtiment - suppléments
BUILDING_CATEGORIES.update({
    "roofing.linear": {
        "name": "Toiture linéaire",
        "unit": "unit",
        "keywords": ["gouttiere ml", "cheneau ml", "faitage ml"],
        "exclude": []
    },
    "electricity.cable": {
        "name": "Câblage",
        "unit": "unit",
        "keywords": ["cable", "fil electrique", "gaine", "conduit", "passage cable"],
        "exclude": []
    },
    "electricity.hour": {
        "name": "Main d'œuvre électricité",
        "unit": "hour",
        "keywords": ["heure electricien", "mo electricite"],
        "exclude": []
    },
    "tiling.linear": {
        "name": "Plinthe carrelage",
        "unit": "unit",
        "keywords": ["plinthe", "baguette", "quart de rond"],
        "exclude": []
    },
    "flooring.preparation": {
        "name": "Préparation support sol",
        "unit": "m2",
        "keywords": ["ragreage", "chape", "beton", "nivellement", "preparation sol"],
        "exclude": []
    },
    "masonry.linear": {
        "name": "Maçonnerie linéaire",
        "unit": "unit",
        "keywords": ["mur ml", "fondation ml", "longrine", "semelle"],
        "exclude": []
    },
    "masonry.cubic": {
        "name": "Maçonnerie au m³",
        "unit": "unit",
        "keywords": ["beton m3", "coulage beton", "fondation m3"],
        "exclude": []
    },
    "insulation.linear": {
        "name": "Isolation linéaire",
        "unit": "unit",
        "keywords": ["isolation ml", "calfeutrement", "mousse expansive"],
        "exclude": []
    },
    "carpentry.custom": {
        "name": "Menuiserie sur mesure",
        "unit": "unit",
        "keywords": ["menuiserie", "placard", "dressing", "escalier", "verriere"],
        "exclude": []
    },
    "hvac.unit": {
        "name": "Ventilation / Climatisation",
        "unit": "unit",
        "keywords": ["vmc", "ventilation", "pompe a chaleur", "chauffage"],
        "exclude": []
    },
    "earthwork.m3": {
        "name": "Terrassement au m³",
        "unit": "unit",
        "keywords": ["terrassement", "excavation", "terre vegetale", "m3 terre"],
        "exclude": []
    },
    "demolition.unit": {
        "name": "Démolition forfait",
        "unit": "unit",
        "keywords": ["demolition complete", "evacuation gravat", "benne"],
        "exclude": []
    },
    "cleaning.m2": {
        "name": "Nettoyage au m²",
        "unit": "m2",
        "keywords": ["nettoyage", "nettoyage fin chantier", "poncage"],
        "exclude": []
    },
})

# Mécanique - suppléments
MECHANIC_CATEGORIES.update({
    "oil.other": {
        "name": "Autres fluides",
        "unit": "unit",
        "keywords": ["huile boite", "huile pont", "liquide direction", "lhm"],
        "exclude": []
    },
    "tires.repair": {
        "name": "Réparation pneu",
        "unit": "unit",
        "keywords": ["crevaison", "meche", "patch", "rustine"],
        "exclude": []
    },
    "engine.repair": {
        "name": "Réparation moteur",
        "unit": "unit",
        "keywords": ["joint culasse", "segment", "soupape", "piston", "fuite moteur"],
        "exclude": []
    },
    "transmission.unit": {
        "name": "Transmission / BV",
        "unit": "unit",
        "keywords": ["boite de vitesse", "transmission", "cardan", "soufflet"],
        "exclude": []
    },
    "steering.unit": {
        "name": "Direction",
        "unit": "unit",
        "keywords": ["cremaillere", "pompe direction", "rotule direction"],
        "exclude": []
    },
})

# Mise à jour des catégories globales
ALL_CATEGORIES = {**BUILDING_CATEGORIES, **MECHANIC_CATEGORIES}

SECTOR_MAP = {
    "building": BUILDING_CATEGORIES,
    "mechanic": MECHANIC_CATEGORIES,
}
