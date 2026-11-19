#!/usr/bin/env python3
"""
Générateur de données tarifaires de démonstration pour TrustDevis.
À utiliser pour initialiser la base pendant le développement.
Les données sont réalistes et basées sur des fourchettes de prix du marché français.
"""

import json
import random
from datetime import datetime, timedelta
from typing import List, Dict
import os

# Données de référence basées sur le marché français
data_dir = "/root/.openclaw/workspace/trustdevis/data/pricing"
os.makedirs(data_dir, exist_ok=True)

# Types de travaux avec fourchettes de prix réalistes (€)
TRAVAUX_PRIX = {
    'plomberie': {
        'installation_wc': (300, 800),
        'installation_lavabo': (200, 500),
        'installation_douche': (800, 2500),
        'remplacement_robinet': (100, 300),
        'reparation_fuite': (150, 500),
        'debouchage': (100, 400),
        'installation_chauffe_eau': (500, 1500),
    },
    'electricite': {
        'installation_prise': (80, 200),
        'installation_tableau': (800, 2500),
        'mise_aux_normes': (1500, 5000),
        'installation_eclairage': (150, 500),
        'installation_vmc': (800, 2000),
        'cablage_piece': (400, 1200),
    },
    'peinture': {
        'piece_20m2': (400, 1000),
        'piece_30m2': (600, 1500),
        'facade_m2': (30, 80),
        'plafond_m2': (25, 60),
        'papier_peint_m2': (20, 50),
    },
    'carrelage': {
        'sol_m2': (50, 150),
        'mur_m2': (60, 180),
        'salle_de_bain_complete': (3000, 8000),
        'terrasse_m2': (60, 200),
    },
    'parquet': {
        'pose_m2': (40, 100),
        'poncage_m2': (25, 60),
        'vitrification_m2': (20, 50),
        'pose_complete_50m2': (2000, 5000),
    },
    'menuiserie': {
        'fenetre_pvc': (400, 1200),
        'fenetre_alu': (600, 1800),
        'fenetre_bois': (800, 2500),
        'porte_interieure': (300, 800),
        'porte_entree': (800, 3000),
        'volet_roulant': (500, 1500),
        'baie_vitree': (1500, 5000),
    },
    'toiture': {
        'refection_m2': (80, 200),
        'nettoyage_demoussage': (20, 50),
        'reparation_fuite': (300, 1500),
        'gouttieres_ml': (30, 80),
        'isolation_sarking_m2': (100, 250),
    },
    'chauffage': {
        'chaudiere_gaz': (3000, 8000),
        'chaudiere_fioul': (4000, 10000),
        'pompe_chaleur_air_air': (8000, 15000),
        'pompe_chaleur_air_eau': (12000, 25000),
        'poele_bois': (2000, 6000),
        'poele_granules': (4000, 10000),
        'radiateur_electrique': (400, 1200),
        'plancher_chauffant_m2': (80, 200),
    },
    'isolation': {
        'combles_soufflage_m2': (20, 50),
        'combles_rouleaux_m2': (25, 60),
        'ite_m2': (80, 200),
        'iti_m2': (60, 150),
        'sous_sol_m2': (30, 80),
        'garage_m2': (25, 70),
    },
    'salle_de_bain': {
        'renovation_complete': (8000, 25000),
        'remplacement_baignoire': (1500, 4000),
        'installation_douche_italienne': (3000, 8000),
        'pose_meubles': (1000, 3000),
        'carrelage_sol_mural': (2000, 6000),
    },
    'cuisine': {
        'pose_cuisine_ikea': (1500, 4000),
        'pose_cuisine_sur_mesure': (4000, 12000),
        'plan_travail': (800, 2500),
        'credence': (400, 1200),
        'electromenager': (2000, 8000),
    },
    'maconnerie': {
        'ouverture_mur_non_porteur': (800, 2500),
        'ouverture_mur_porteur': (3000, 8000),
        'construction_mur_parpaing_m2': (150, 400),
        'enduit_m2': (30, 80),
        'dalle_beton_m2': (80, 200),
    },
    'terrasse': {
        'terrasse_bois_m2': (100, 300),
        'terrasse_carrelage_m2': (80, 250),
        'terrasse_beton_m2': (60, 180),
        'terrasse_pierre_m2': (150, 400),
    },
}

REGIONS = [
    'Île-de-France', 'Auvergne-Rhône-Alpes', 'Provence-Alpes-Côte d\'Azur',
    'Occitanie', 'Nouvelle-Aquitaine', 'Hauts-de-France', 'Grand Est',
    'Bretagne', 'Pays de la Loire', 'Normandie', 'Centre-Val de Loire',
    'Bourgogne-Franche-Comté', 'Corse'
]

SOURCES = ['reddit_bricolage', 'forum_travaux', 'avis_clients', 'discussion_forum']

def generate_pricing_data(count: int = 500) -> List[Dict]:
    """Génère des données tarifaires réalistes"""
    data = []
    
    for i in range(count):
        # Choisit un type de travaux aléatoire
        type_travaux = random.choice(list(TRAVAUX_PRIX.keys()))
        sous_categories = TRAVAUX_PRIX[type_travaux]
        sous_categorie = random.choice(list(sous_categories.keys()))
        
        # Récupère la fourchette de prix
        prix_min, prix_max = sous_categories[sous_categorie]
        
        # Génère un prix avec variation réaliste
        prix = round(random.uniform(prix_min, prix_max), 2)
        
        # Détermine l'unité
        if 'm2' in sous_categorie:
            unite = 'm²'
            prix_unitaire = prix
        elif 'ml' in sous_categorie:
            unite = 'ml'
            prix_unitaire = prix
        else:
            unite = 'forfait'
            prix_unitaire = None
        
        # Région aléatoire
        region = random.choice(REGIONS)
        
        # Date aléatoire dans les 6 derniers mois
        days_ago = random.randint(1, 180)
        date_mention = (datetime.now() - timedelta(days=days_ago)).isoformat()
        
        # Génère un contexte réaliste
        contextes = [
            f"Devis reçu pour {sous_categorie.replace('_', ' ')}. Prix TTC.",
            f"Travaux réalisés en {region}. {sous_categorie.replace('_', ' ')}.",
            f"Artisan recommandé. {sous_categorie.replace('_', ' ')} pour {prix}€.",
            f"Projet terminé. {sous_categorie.replace('_', ' ')}. Satisfait du résultat.",
            f"Comparaison de devis pour {sous_categorie.replace('_', ' ')}. Celui-ci à {prix}€.",
        ]
        contexte = random.choice(contextes)
        
        # Calcul de la confiance
        confiance = random.randint(60, 95)
        
        # Crée l'entrée
        entry = {
            'id': f"demo_{i:05d}",
            'type_travaux': type_travaux,
            'sous_categorie': sous_categorie,
            'prix': prix,
            'prix_unitaire': prix_unitaire,
            'unite': unite,
            'region': region,
            'departement': None,
            'date_mention': date_mention,
            'source': random.choice(SOURCES),
            'url_source': None,
            'contexte': contexte,
            'confiance': confiance,
            'scraped_at': datetime.now().isoformat()
        }
        
        data.append(entry)
    
    return data


def save_data(data: List[Dict], filename: str = None):
    """Sauvegarde les données en JSON"""
    if filename is None:
        filename = f"demo_pricing_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    filepath = os.path.join(data_dir, filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ {len(data)} données sauvegardées dans {filepath}")
    return filepath


def generate_stats(data: List[Dict]) -> Dict:
    """Génère des statistiques sur les données"""
    stats = {
        'total': len(data),
        'by_type': {},
        'by_region': {},
        'by_source': {},
        'price_stats': {}
    }
    
    for entry in data:
        # Par type
        t = entry['type_travaux']
        stats['by_type'][t] = stats['by_type'].get(t, 0) + 1
        
        # Par région
        r = entry['region']
        stats['by_region'][r] = stats['by_region'].get(r, 0) + 1
        
        # Par source
        s = entry['source']
        stats['by_source'][s] = stats['by_source'].get(s, 0) + 1
    
    # Stats de prix par type
    for type_t in stats['by_type'].keys():
        prices = [e['prix'] for e in data if e['type_travaux'] == type_t and e['prix']]
        if prices:
            stats['price_stats'][type_t] = {
                'count': len(prices),
                'avg': round(sum(prices) / len(prices), 2),
                'min': round(min(prices), 2),
                'max': round(max(prices), 2),
                'median': round(sorted(prices)[len(prices)//2], 2)
            }
    
    return stats


def print_report(data: List[Dict]):
    """Affiche un rapport des données"""
    stats = generate_stats(data)
    
    print("\n" + "="*70)
    print("📊 RAPPORT DONNÉES TARIFAIRES TRUSTDEVIS")
    print("="*70)
    print(f"\n📈 STATISTIQUES GLOBALES")
    print(f"   Total entrées: {stats['total']}")
    
    print(f"\n🔧 PAR TYPE DE TRAVAUX")
    for t, count in sorted(stats['by_type'].items(), key=lambda x: -x[1]):
        pct = count / stats['total'] * 100
        print(f"   • {t}: {count} ({pct:.1f}%)")
    
    print(f"\n🌍 PAR RÉGION (top 5)")
    for r, count in sorted(stats['by_region'].items(), key=lambda x: -x[1])[:5]:
        print(f"   • {r}: {count}")
    
    print(f"\n💰 STATISTIQUES DE PRIX PAR TYPE")
    for t, ps in sorted(stats['price_stats'].items(), key=lambda x: -x[1]['count']):
        print(f"   • {t}:")
        print(f"     Moy: {ps['avg']}€ | Min: {ps['min']}€ | Max: {ps['max']}€ | Med: {ps['median']}€")
    
    print("\n" + "="*70)


if __name__ == "__main__":
    print("🚀 Génération de données tarifaires de démonstration...")
    
    # Génère 500 entrées
    data = generate_pricing_data(500)
    
    # Sauvegarde
    filepath = save_data(data)
    
    # Affiche le rapport
    print_report(data)
    
    print(f"\n✅ Données générées avec succès!")
    print(f"📁 Fichier: {filepath}")
