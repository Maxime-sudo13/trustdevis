#!/usr/bin/env python3
"""
Script de scraping continu pour TrustDevis Pricing.
S'exécute en arrière-plan et collecte les données toutes les heures.
"""

import asyncio
import sys
import os
from datetime import datetime
import time

sys.path.insert(0, '/root/.openclaw/workspace/trustdevis/agents/leadfinder')

from pricing_scraper import PricingScraperManager


async def continuous_scraping():
    """Boucle de scraping continu"""
    print("🚀 Démarrage du scraping continu TrustDevis Pricing")
    print("="*70)
    print("Intervalle: Toutes les heures")
    print("Appuyez sur Ctrl+C pour arrêter")
    print("="*70 + "\n")
    
    iteration = 0
    
    while True:
        iteration += 1
        start_time = datetime.now()
        
        print(f"\n{'='*70}")
        print(f"🔄 ITERATION #{iteration} - {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*70}")
        
        manager = PricingScraperManager()
        
        try:
            # Exécute le scraping
            results = await manager.run_all(max_pages=2)
            
            # Compte les nouvelles données
            total_new = sum(len(data) for data in results.values())
            
            print(f"\n✅ Itération terminée: {total_new} nouvelles données collectées")
            
            # Affiche le rapport
            print(manager.get_report())
            
        except Exception as e:
            print(f"\n❌ Erreur lors du scraping: {e}")
        
        finally:
            await manager.close_all()
        
        # Attend 1 heure avant la prochaine itération
        next_run = datetime.now()
        print(f"\n⏳ Prochain scraping à {(next_run + asyncio.timedelta(hours=1)).strftime('%H:%M:%S')}")
        print("En attente... (Ctrl+C pour arrêter)\n")
        
        await asyncio.sleep(3600)  # 1 heure


def main():
    """Point d'entrée"""
    try:
        asyncio.run(continuous_scraping())
    except KeyboardInterrupt:
        print("\n\n🛑 Arrêt demandé par l'utilisateur")
        print("✅ Scraping continu arrêté proprement")


if __name__ == "__main__":
    main()
