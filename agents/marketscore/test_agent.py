#!/usr/bin/env python3
"""
Script de test rapide pour l'agent MarketScore
"""

import sys
sys.path.insert(0, '/root/.openclaw/workspace/trustdevis/agents/marketscore')

from agent import MarketScoreAgent, DatabaseManager, PricingEngine, MarketScoreAnalyzer
from pathlib import Path

def test_analyzer():
    """Teste l'analyseur de devis."""
    print("🧪 Test de l'analyseur MarketScore\n")
    
    # Initialiser
    pricing = PricingEngine('/root/.openclaw/workspace/trustdevis/agents/pricing-engine/pricing.db')
    analyzer = MarketScoreAnalyzer(pricing)
    
    # Test 1: Devis bâtiment IDF
    print("📋 Test 1: Devis Bâtiment IDF")
    lignes1 = [
        {"categorie": "peinture", "description": "Peinture salon 30m²", "montant": 950},
        {"categorie": "electricite", "description": "Installation 3 prises", "montant": 350},
        {"categorie": "plomberie", "description": "Remplacement robinetterie", "montant": 300}
    ]
    
    result1 = analyzer.analyser_devis("TEST_001", lignes1, "IDF")
    print(f"   Score: {result1.score}/100")
    print(f"   Delta: {result1.delta_pct}%")
    print(f"   Risque: {result1.risk_level}")
    print(f"   Revue humaine: {'Oui' if result1.requires_human_review else 'Non'}")
    print(f"   Total devis: {result1.total_devis}€")
    print(f"   Total marché: {result1.total_marche}€")
    print()
    
    # Test 2: Devis mécanique IDF
    print("📋 Test 2: Devis Mécanique IDF")
    lignes2 = [
        {"categorie": "vidange_standard", "description": "Vidange + filtres", "montant": 150},
        {"categorie": "freins_plaquettes_avant", "description": "Remplacement plaquettes AV", "montant": 220},
        {"categorie": "main_oeuvre_mecanique", "description": "Main d'oeuvre", "montant": 100}
    ]
    
    result2 = analyzer.analyser_devis("TEST_002", lignes2, "IDF")
    print(f"   Score: {result2.score}/100")
    print(f"   Delta: {result2.delta_pct}%")
    print(f"   Risque: {result2.risk_level}")
    print(f"   Revue humaine: {'Oui' if result2.requires_human_review else 'Non'}")
    print()
    
    # Test 3: Devis surtarifé (anomalie)
    print("📋 Test 3: Devis avec surtarification")
    lignes3 = [
        {"categorie": "peinture", "description": "Peinture chambre 15m²", "montant": 1500},  # Très cher
        {"categorie": "electricite", "description": "Installation simple prise", "montant": 500}  # Très cher
    ]
    
    result3 = analyzer.analyser_devis("TEST_003", lignes3, "IDF")
    print(f"   Score: {result3.score}/100")
    print(f"   Delta: {result3.delta_pct}%")
    print(f"   Risque: {result3.risk_level}")
    print(f"   Anomalies: {sum(1 for l in result3.lignes_detail if l.anomalie)}")
    print()
    
    # Afficher les justifications
    print("📝 Justifications Test 3:")
    for j in result3.justification:
        print(f"   • {j}")
    print()
    
    print("📝 Actions recommandées:")
    for a in result3.actions:
        print(f"   • {a}")
    print()
    
    pricing.close()
    print("✅ Tests terminés avec succès!")


def test_database():
    """Teste la base de données."""
    print("\n🗄️  Test de la base de données\n")
    
    db_path = '/root/.openclaw/workspace/trustdevis/agents/marketscore/test.db'
    db = DatabaseManager(db_path)
    
    # Ajouter un devis
    lignes = [
        {"categorie": "peinture", "description": "Test", "montant": 500}
    ]
    db.add_devis("TEST_DB_001", "batiment", "IDF", lignes)
    
    # Vérifier
    pending = db.get_pending_devis()
    print(f"   Devis en attente: {len(pending)}")
    
    stats = db.get_global_stats()
    print(f"   Stats globales: {stats}")
    
    print("✅ Base de données OK!")


if __name__ == "__main__":
    test_analyzer()
    test_database()
