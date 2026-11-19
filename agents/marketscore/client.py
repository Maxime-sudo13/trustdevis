#!/usr/bin/env python3
"""
Client API pour ajouter des devis à analyser
"""

import sys
import json
import requests
from datetime import datetime

BASE_URL = "http://localhost:8000"

def add_devis(devis_data: dict):
    """Ajoute un devis via l'API."""
    try:
        response = requests.post(f"{BASE_URL}/score", json=devis_data, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError:
        print("❌ Erreur: Le service MarketScore n'est pas démarré")
        print("   Démarrez-le avec: python3 agent.py")
        return None
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return None


def exemple_devis_batiment():
    """Exemple de devis bâtiment."""
    return {
        "devis": {
            "secteur": "batiment",
            "lignes": [
                {"categorie": "peinture", "description": "Peinture salon 30m²", "montant": 750},
                {"categorie": "electricite", "description": "Installation 3 prises", "montant": 280},
                {"categorie": "plomberie", "description": "Remplacement robinetterie sdb", "montant": 250}
            ]
        },
        "market_stats": {
            "region": "IDF",
            "medianes": {
                "peinture": {"median": 700, "q1": 600, "q3": 800},
                "electricite": {"median": 250, "q1": 200, "q3": 300},
                "plomberie": {"median": 220, "q1": 180, "q3": 260}
            }
        },
        "historique": []
    }


def exemple_devis_mecanique():
    """Exemple de devis mécanique."""
    return {
        "devis": {
            "secteur": "mecanique",
            "lignes": [
                {"categorie": "vidange_standard", "description": "Vidange + filtres", "montant": 110},
                {"categorie": "freins_plaquettes_avant", "description": "Remplacement plaquettes AV", "montant": 195}
            ]
        },
        "market_stats": {
            "region": "IDF",
            "medianes": {
                "vidange_standard": {"median": 95, "q1": 85, "q3": 110},
                "freins_plaquettes_avant": {"median": 185, "q1": 160, "q3": 210}
            }
        },
        "historique": []
    }


def main():
    print("🚀 Client MarketScore API")
    print()
    
    # Test 1: Devis bâtiment
    print("📋 Test 1: Devis Bâtiment IDF")
    result1 = add_devis(exemple_devis_batiment())
    if result1:
        print(f"   Score: {result1['score']}/100")
        print(f"   Risque: {result1['risk_level']}")
        print(f"   Delta: {result1['delta_pct']}%")
        print(f"   Revue humaine: {'Oui' if result1['requires_human_review'] else 'Non'}")
    print()
    
    # Test 2: Devis mécanique
    print("📋 Test 2: Devis Mécanique IDF")
    result2 = add_devis(exemple_devis_mecanique())
    if result2:
        print(f"   Score: {result2['score']}/100")
        print(f"   Risque: {result2['risk_level']}")
        print(f"   Delta: {result2['delta_pct']}%")
    print()
    
    print("✅ Tests terminés!")


if __name__ == "__main__":
    main()
