#!/usr/bin/env python3
"""
Script de rapport horaire pour le Pricing Scraper TrustDevis.
À exécuter toutes les heures pour suivre la collecte.
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta

# Ajoute le path pour les imports
sys.path.insert(0, '/root/.openclaw/workspace/trustdevis/agents/leadfinder')

from pricing_scraper import PricingScraperManager, PricingDataStore
import json


async def generate_hourly_report():
    """Génère le rapport de l'heure écoulée"""
    
    print(f"\n{'='*70}")
    print(f"📊 RAPPORT HORAIRE PRICING SCRAPER")
    print(f"🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print(f"{'='*70}\n")
    
    store = PricingDataStore()
    
    # Récupère toutes les données (incluant les fichiers demo_* et consolidated_*)
    import glob
    import os
    
    all_data = []
    patterns = [
        f"{store.data_dir}/pricing_*.json",
        f"{store.data_dir}/demo_*.json",
        f"{store.data_dir}/consolidated_*.json",
        f"{store.data_dir}/reddit_*.json",
    ]
    
    for pattern in patterns:
        for filepath in glob.glob(pattern):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    all_data.extend(data)
            except Exception as e:
                pass  # Ignore les erreurs de chargement
    
    if not all_data:
        print("⚠️  Aucune donnée collectée pour le moment.")
        print("   Le scraper est peut-être en cours d'exécution...")
        return
    
    # Filtre les données des dernières heures
    one_hour_ago = datetime.now() - timedelta(hours=1)
    recent_data = [
        d for d in all_data 
        if d.get('scraped_at') and datetime.fromisoformat(d['scraped_at']) > one_hour_ago
    ]
    
    # Statistiques globales
    print(f"📈 DONNÉES COLLECTÉES")
    print(f"   • Nouvelles entrées (dernière heure): {len(recent_data)}")
    print(f"   • Total cumulé: {len(all_data)}")
    
    if recent_data:
        # Par type
        print(f"\n🔧 PAR TYPE DE TRAVAUX (dernière heure)")
        types = {}
        for d in recent_data:
            t = d.get('type_travaux', 'inconnu')
            types[t] = types.get(t, 0) + 1
        for t, count in sorted(types.items(), key=lambda x: -x[1]):
            print(f"   • {t}: {count}")
        
        # Par région
        print(f"\n🌍 PAR RÉGION (dernière heure)")
        regions = {}
        for d in recent_data:
            r = d.get('region', 'inconnue')
            regions[r] = regions.get(r, 0) + 1
        for r, count in sorted(regions.items(), key=lambda x: -x[1])[:5]:
            print(f"   • {r}: {count}")
        
        # Par source
        print(f"\n🔗 PAR SOURCE (dernière heure)")
        sources = {}
        for d in recent_data:
            s = d.get('source', 'inconnue')
            sources[s] = sources.get(s, 0) + 1
        for s, count in sorted(sources.items(), key=lambda x: -x[1]):
            print(f"   • {s}: {count}")
        
        # Prix extraits
        prices = [d.get('prix') for d in recent_data if d.get('prix')]
        if prices:
            print(f"\n💰 PRIX EXTRAITS (dernière heure)")
            print(f"   • Nombre: {len(prices)}")
            print(f"   • Moyenne: {sum(prices)/len(prices):.2f}€")
            print(f"   • Min: {min(prices):.2f}€")
            print(f"   • Max: {max(prices):.2f}€")
        
        # Qualité
        confidences = [d.get('confiance', 0) for d in recent_data]
        if confidences:
            avg_conf = sum(confidences) / len(confidences)
            print(f"\n✅ QUALITÉ DES DONNÉES")
            print(f"   • Confiance moyenne: {avg_conf:.1f}/100")
            high_conf = len([c for c in confidences if c >= 70])
            print(f"   • Données haute confiance (≥70): {high_conf}/{len(confidences)}")
    
    # Échantillon de données récentes
    print(f"\n📝 ÉCHANTILLON RÉCENT (3 dernières entrées)")
    for d in recent_data[:3]:
        print(f"\n   [{d.get('type_travaux', 'N/A')}] {d.get('sous_categorie', 'N/A')}")
        print(f"   Prix: {d.get('prix', 'N/A')}€ | Région: {d.get('region', 'N/A')}")
        print(f"   Source: {d.get('source', 'N/A')}")
        print(f"   Contexte: {d.get('contexte', 'N/A')[:100]}...")
    
    print(f"\n{'='*70}")
    print(f"✅ Rapport généré avec succès")
    print(f"{'='*70}\n")


def run_report():
    """Point d'entrée synchrone"""
    asyncio.run(generate_hourly_report())


if __name__ == "__main__":
    run_report()
