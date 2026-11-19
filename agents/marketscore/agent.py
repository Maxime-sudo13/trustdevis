#!/usr/bin/env python3
"""
TrustDevis MarketScore Agent - Service d'analyse automatique des devis
Surveille la base de données, analyse les devis entrants, produit des scores de confiance.
"""

import os
import sys
import json
import time
import sqlite3
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from pathlib import Path

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('/root/.openclaw/workspace/trustdevis/agents/marketscore/marketscore.log')
    ]
)
logger = logging.getLogger('MarketScore')

# Chemins
WORKSPACE = Path('/root/.openclaw/workspace/trustdevis')
PRICING_DB = WORKSPACE / 'agents/pricing-engine/pricing.db'
MARKETSCORE_DB = WORKSPACE / 'agents/marketscore/marketscore.db'
RESULTS_DIR = WORKSPACE / 'agents/marketscore/results'

# Créer les répertoires nécessaires
RESULTS_DIR.mkdir(parents=True, exist_ok=True)


@dataclass
class LigneDevis:
    """Une ligne de devis analysée."""
    categorie: str
    description: str
    montant: float
    quantite: float = 1.0
    unite: str = "forfait"


@dataclass
class AnalyseLigne:
    """Résultat d'analyse d'une ligne."""
    categorie: str
    description: str
    montant_devis: float
    mediane_marche: float
    delta_pct: float
    delta_abs: float
    score_ligne: float
    anomalie: bool


@dataclass
class ScoreResult:
    """Résultat complet du scoring."""
    devis_id: str
    score: int
    delta_pct: float
    risk_level: str
    lignes_detail: List[AnalyseLigne]
    total_devis: float
    total_marche: float
    justification: List[str]
    actions: List[str]
    requires_human_review: bool
    timestamp: str


class PricingEngine:
    """Interface avec la base de données de prix."""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
    
    def get_price_stats(self, category: str, region_code: str) -> Optional[Dict]:
        """Récupère les statistiques de prix pour une catégorie/région."""
        cursor = self.conn.execute(
            """
            SELECT price FROM prices 
            WHERE category = ? AND region_code = ?
            """,
            (category.lower(), region_code.upper())
        )
        prices = [row[0] for row in cursor.fetchall()]
        
        if not prices:
            return None
        
        prices_sorted = sorted(prices)
        n = len(prices_sorted)
        
        return {
            "count": n,
            "median": prices_sorted[n // 2] if n % 2 else (prices_sorted[n//2-1] + prices_sorted[n//2]) / 2,
            "q1": prices_sorted[n // 4],
            "q3": prices_sorted[3 * n // 4],
            "min": prices_sorted[0],
            "max": prices_sorted[-1],
            "mean": sum(prices) / n
        }
    
    def get_regions(self) -> List[Dict]:
        """Récupère toutes les régions."""
        cursor = self.conn.execute("SELECT * FROM regions")
        return [dict(row) for row in cursor.fetchall()]
    
    def get_categories(self) -> List[str]:
        """Récupère toutes les catégories."""
        cursor = self.conn.execute("SELECT DISTINCT category FROM prices")
        return [row[0] for row in cursor.fetchall()]
    
    def close(self):
        self.conn.close()


class MarketScoreAnalyzer:
    """Analyseur de devis avec scoring."""
    
    def __init__(self, pricing_engine: PricingEngine):
        self.pricing = pricing_engine
        self.seuils = {
            "moderate": 0.25,
            "high": 0.40
        }
    
    def calculer_delta(self, montant_devis: float, mediane: float) -> tuple:
        """Calcule le delta en % et valeur absolue."""
        if mediane == 0:
            return 0.0, 0.0
        delta_abs = montant_devis - mediane
        delta_pct = delta_abs / mediane
        return delta_pct, delta_abs
    
    def calculer_score_ligne(self, delta_pct: float) -> float:
        """Calcule le score d'une ligne (0-100)."""
        if delta_pct <= 0:
            return 100.0
        elif delta_pct <= 0.10:
            return 100 - (delta_pct * 100 * 0.5)
        elif delta_pct <= 0.25:
            return 95 - ((delta_pct - 0.10) * 100 * 1.5)
        else:
            return max(0, 75 - ((delta_pct - 0.25) * 100 * 2))
    
    def analyser_devis(self, devis_id: str, lignes: List[Dict], region_code: str) -> ScoreResult:
        """Analyse complète d'un devis."""
        analyses = []
        total_devis = 0.0
        total_pondere_delta = 0.0
        total_poids = 0.0
        
        # Pondérations par catégorie
        ponderations = {
            "main_oeuvre": 0.35, "materiaux": 0.25, "pieces": 0.25,
            "deplacement": 0.10, "diagnostic": 0.05, "autre": 0.10
        }
        
        for ligne in lignes:
            cat = ligne.get("categorie", "autre").lower()
            desc = ligne.get("description", "")
            montant = float(ligne.get("montant", 0))
            
            # Récupérer stats du marché
            stats = self.pricing.get_price_stats(cat, region_code)
            mediane = stats["median"] if stats else 0.0
            
            # Calculs
            delta_pct, delta_abs = self.calculer_delta(montant, mediane)
            score_ligne = self.calculer_score_ligne(delta_pct)
            anomalie = delta_pct > self.seuils["high"]
            
            analyse = AnalyseLigne(
                categorie=cat,
                description=desc,
                montant_devis=montant,
                mediane_marche=mediane,
                delta_pct=round(delta_pct * 100, 2),
                delta_abs=round(delta_abs, 2),
                score_ligne=round(score_ligne, 1),
                anomalie=anomalie
            )
            analyses.append(analyse)
            
            # Agrégation
            total_devis += montant
            poids = ponderations.get(cat, 0.10)
            total_pondere_delta += abs(delta_pct) * poids
            total_poids += poids
        
        # Calculs globaux
        delta_moyen = total_pondere_delta / total_poids if total_poids > 0 else 0.0
        total_marche = sum(a.mediane_marche for a in analyses)
        delta_global = (total_devis - total_marche) / total_marche if total_marche > 0 else 0.0
        
        # Score global
        if delta_moyen <= 0.05:
            score_global = 95 - (delta_moyen * 100)
        elif delta_moyen <= 0.15:
            score_global = 90 - ((delta_moyen - 0.05) * 200)
        elif delta_moyen <= 0.25:
            score_global = 70 - ((delta_moyen - 0.15) * 300)
        else:
            score_global = max(0, 40 - ((delta_moyen - 0.25) * 100))
        
        score_global = int(round(max(0, min(100, score_global))))
        
        # Niveau de risque
        max_delta = max(abs(delta_global), delta_moyen)
        if max_delta > self.seuils["high"]:
            risk_level = "high"
        elif max_delta > self.seuils["moderate"]:
            risk_level = "moderate"
        else:
            risk_level = "low"
        
        # Revue humaine nécessaire ?
        requires_review = score_global < 60 or risk_level == "high" or abs(delta_global) > 0.30
        
        # Générer justifications et actions
        justification = self._generer_justifications(analyses)
        actions = self._generer_actions(risk_level, score_global, analyses)
        
        return ScoreResult(
            devis_id=devis_id,
            score=score_global,
            delta_pct=round(delta_global * 100, 2),
            risk_level=risk_level,
            lignes_detail=analyses,
            total_devis=round(total_devis, 2),
            total_marche=round(total_marche, 2),
            justification=justification,
            actions=actions,
            requires_human_review=requires_review,
            timestamp=datetime.utcnow().isoformat()
        )
    
    def _generer_justifications(self, analyses: List[AnalyseLigne]) -> List[str]:
        """Génère les justifications textuelles."""
        justifs = []
        for a in analyses:
            if a.delta_pct > 30:
                justifs.append(
                    f"{a.categorie}: Probabilité de sur-tarification de {a.delta_pct:.0f}% "
                    f"par rapport à la médiane régionale ({a.mediane_marche:.0f}€)"
                )
            elif a.delta_pct > 15:
                justifs.append(
                    f"{a.categorie}: Écart significatif de {a.delta_pct:.0f}% avec les prix du marché"
                )
            elif a.delta_pct > 0:
                justifs.append(
                    f"{a.categorie}: Tarif légèrement supérieur à la médiane ({a.delta_pct:.0f}%)"
                )
            elif a.delta_pct < -10:
                justifs.append(
                    f"{a.categorie}: Tarif inférieur à la médiane ({abs(a.delta_pct):.0f}%), "
                    f"vérifiez la qualité des prestations"
                )
            else:
                justifs.append(
                    f"{a.categorie}: Tarif conforme à la médiane du marché"
                )
        return justifs
    
    def _generer_actions(self, risk_level: str, score: int, analyses: List[AnalyseLigne]) -> List[str]:
        """Génère les actions recommandées."""
        actions = []
        anomalies = [a for a in analyses if a.anomalie]
        
        if risk_level == "high":
            actions = [
                "1. Demander un détail complet de chaque poste de dépense",
                "2. Comparer avec au moins 2 autres devis du même secteur",
                "3. Vérifier les références exactes des matériaux/pièces proposés",
                "4. Questionner le professionnel sur les écarts de prix importants"
            ]
        elif risk_level == "moderate":
            actions = [
                "1. Demander la répartition détaillée des heures de main d'œuvre",
                "2. Vérifier la qualité des matériaux/pièces proposés",
                "3. Comparer avec un second avis si possible"
            ]
        else:
            actions = [
                "1. Vérifier que toutes les prestations demandées sont bien listées",
                "2. Conserver ce devis comme référence pour comparaison"
            ]
        
        if score < 60:
            actions.insert(0, "⚠️ Faire appel à un expert pour une revue approfondie")
        
        if anomalies:
            actions.append(f"5. Attention particulière sur : {', '.join(a.categorie for a in anomalies[:3])}")
        
        return actions[:6]


class DatabaseManager:
    """Gestionnaire de la base de données MarketScore."""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        """Initialise la base de données."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Table des devis à analyser
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS devis_queue (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                devis_id TEXT UNIQUE NOT NULL,
                secteur TEXT NOT NULL,
                region_code TEXT NOT NULL,
                lignes_json TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                analyzed_at TIMESTAMP
            )
        """)
        
        # Table des résultats d'analyse
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS analysis_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                devis_id TEXT UNIQUE NOT NULL,
                score INTEGER NOT NULL,
                delta_pct REAL NOT NULL,
                risk_level TEXT NOT NULL,
                requires_human_review BOOLEAN NOT NULL,
                result_json TEXT NOT NULL,
                anomalies_detected INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Table des statistiques d'apprentissage
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS learning_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT UNIQUE NOT NULL,
                devis_analyzed INTEGER DEFAULT 0,
                avg_score REAL DEFAULT 0,
                anomalies_detected INTEGER DEFAULT 0,
                high_risk_count INTEGER DEFAULT 0,
                moderate_risk_count INTEGER DEFAULT 0,
                low_risk_count INTEGER DEFAULT 0,
                improvements TEXT
            )
        """)
        
        conn.commit()
        conn.close()
        logger.info("Base de données MarketScore initialisée")
    
    def add_devis(self, devis_id: str, secteur: str, region_code: str, lignes: List[Dict]) -> bool:
        """Ajoute un devis à la file d'attente."""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.execute(
                """
                INSERT OR IGNORE INTO devis_queue (devis_id, secteur, region_code, lignes_json)
                VALUES (?, ?, ?, ?)
                """,
                (devis_id, secteur, region_code, json.dumps(lignes))
            )
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Erreur ajout devis {devis_id}: {e}")
            return False
    
    def get_pending_devis(self) -> List[Dict]:
        """Récupère les devis en attente d'analyse."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.execute(
            "SELECT * FROM devis_queue WHERE status = 'pending' ORDER BY created_at"
        )
        rows = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return rows
    
    def mark_as_analyzed(self, devis_id: str):
        """Marque un devis comme analysé."""
        conn = sqlite3.connect(self.db_path)
        conn.execute(
            """
            UPDATE devis_queue 
            SET status = 'analyzed', analyzed_at = CURRENT_TIMESTAMP
            WHERE devis_id = ?
            """,
            (devis_id,)
        )
        conn.commit()
        conn.close()
    
    def save_result(self, result: ScoreResult):
        """Sauvegarde le résultat d'analyse."""
        anomalies = sum(1 for l in result.lignes_detail if l.anomalie)
        conn = sqlite3.connect(self.db_path)
        conn.execute(
            """
            INSERT OR REPLACE INTO analysis_results 
            (devis_id, score, delta_pct, risk_level, requires_human_review, result_json, anomalies_detected)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                result.devis_id,
                result.score,
                result.delta_pct,
                result.risk_level,
                result.requires_human_review,
                json.dumps(asdict(result), default=str),
                anomalies
            )
        )
        conn.commit()
        conn.close()
    
    def update_daily_stats(self, stats: Dict):
        """Met à jour les statistiques journalières."""
        today = datetime.utcnow().strftime('%Y-%m-%d')
        conn = sqlite3.connect(self.db_path)
        conn.execute(
            """
            INSERT INTO learning_stats (date, devis_analyzed, avg_score, anomalies_detected,
                                       high_risk_count, moderate_risk_count, low_risk_count, improvements)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(date) DO UPDATE SET
                devis_analyzed = devis_analyzed + ?,
                avg_score = (avg_score * devis_analyzed + ? * ?) / (devis_analyzed + ?),
                anomalies_detected = anomalies_detected + ?,
                high_risk_count = high_risk_count + ?,
                moderate_risk_count = moderate_risk_count + ?,
                low_risk_count = low_risk_count + ?
            """,
            (
                today, stats['count'], stats['avg_score'], stats['anomalies'],
                stats['high_risk'], stats['moderate_risk'], stats['low_risk'], stats.get('improvements', ''),
                stats['count'], stats['avg_score'], stats['count'], stats['count'],
                stats['anomalies'], stats['high_risk'], stats['moderate_risk'], stats['low_risk']
            )
        )
        conn.commit()
        conn.close()
    
    def get_stats_last_hour(self) -> Dict:
        """Récupère les statistiques de la dernière heure."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        
        # Devis analysés dans la dernière heure
        cursor = conn.execute(
            """
            SELECT COUNT(*) as count, AVG(score) as avg_score,
                   SUM(CASE WHEN risk_level = 'high' THEN 1 ELSE 0 END) as high_risk,
                   SUM(CASE WHEN risk_level = 'moderate' THEN 1 ELSE 0 END) as moderate_risk,
                   SUM(CASE WHEN risk_level = 'low' THEN 1 ELSE 0 END) as low_risk,
                   SUM(anomalies_detected) as anomalies
            FROM analysis_results
            WHERE created_at >= datetime('now', '-1 hour')
            """
        )
        row = cursor.fetchone()
        conn.close()
        
        return {
            'count': row['count'] or 0,
            'avg_score': round(row['avg_score'], 1) if row['avg_score'] else 0,
            'high_risk': row['high_risk'] or 0,
            'moderate_risk': row['moderate_risk'] or 0,
            'low_risk': row['low_risk'] or 0,
            'anomalies': row['anomalies'] or 0
        }
    
    def get_global_stats(self) -> Dict:
        """Récupère les statistiques globales."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        
        cursor = conn.execute("SELECT COUNT(*) FROM devis_queue WHERE status = 'pending'")
        pending = cursor.fetchone()[0]
        
        cursor = conn.execute("SELECT COUNT(*) FROM analysis_results")
        analyzed = cursor.fetchone()[0]
        
        cursor = conn.execute("SELECT AVG(score) FROM analysis_results")
        avg_score = cursor.fetchone()[0] or 0
        
        cursor = conn.execute("SELECT SUM(anomalies_detected) FROM analysis_results")
        total_anomalies = cursor.fetchone()[0] or 0
        
        conn.close()
        
        return {
            'pending': pending,
            'analyzed': analyzed,
            'avg_score': round(avg_score, 1),
            'total_anomalies': total_anomalies
        }


class MarketScoreAgent:
    """Agent principal MarketScore."""
    
    def __init__(self):
        self.db = DatabaseManager(str(MARKETSCORE_DB))
        self.pricing = PricingEngine(str(PRICING_DB))
        self.analyzer = MarketScoreAnalyzer(self.pricing)
        self.running = True
        self.stats_cache = {'last_report': None}
        
        logger.info("🚀 Agent MarketScore initialisé")
    
    def process_devis(self, devis_data: Dict) -> Optional[ScoreResult]:
        """Traite un devis individuel."""
        try:
            devis_id = devis_data['devis_id']
            secteur = devis_data['secteur']
            region_code = devis_data['region_code']
            lignes = json.loads(devis_data['lignes_json'])
            
            logger.info(f"📊 Analyse du devis {devis_id} ({secteur}, {region_code})")
            
            # Analyse
            result = self.analyzer.analyser_devis(devis_id, lignes, region_code)
            
            # Sauvegarde
            self.db.save_result(result)
            self.db.mark_as_analyzed(devis_id)
            
            # Sauvegarde JSON
            result_file = RESULTS_DIR / f"{devis_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
            with open(result_file, 'w') as f:
                json.dump(asdict(result), f, indent=2, default=str)
            
            logger.info(f"✅ Devis {devis_id} analysé - Score: {result.score}/100, Risque: {result.risk_level}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Erreur analyse devis {devis_data.get('devis_id', 'unknown')}: {e}")
            return None
    
    def check_and_process(self):
        """Vérifie et traite les devis en attente."""
        pending = self.db.get_pending_devis()
        
        if not pending:
            return 0
        
        logger.info(f"🔍 {len(pending)} devis en attente d'analyse")
        
        stats = {'count': 0, 'scores': [], 'anomalies': 0, 'high_risk': 0, 'moderate_risk': 0, 'low_risk': 0}
        
        for devis in pending:
            result = self.process_devis(devis)
            if result:
                stats['count'] += 1
                stats['scores'].append(result.score)
                stats['anomalies'] += sum(1 for l in result.lignes_detail if l.anomalie)
                
                if result.risk_level == 'high':
                    stats['high_risk'] += 1
                elif result.risk_level == 'moderate':
                    stats['moderate_risk'] += 1
                else:
                    stats['low_risk'] += 1
        
        # Mettre à jour les stats
        if stats['count'] > 0:
            stats['avg_score'] = sum(stats['scores']) / len(stats['scores'])
            self.db.update_daily_stats(stats)
        
        return stats['count']
    
    def generate_hourly_report(self) -> str:
        """Génère le rapport horaire."""
        stats = self.db.get_stats_last_hour()
        global_stats = self.db.get_global_stats()
        
        report = f"""
📊 RAPPORT MARKETSCORE - {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}

⏱️  Dernière heure:
   • Devis analysés: {stats['count']}
   • Score moyen: {stats['avg_score']}/100
   • Anomalies détectées: {stats['anomalies']}
   • Répartition risque: 🔴 {stats['high_risk']} | 🟡 {stats['moderate_risk']} | 🟢 {stats['low_risk']}

📈 Global:
   • Total analysés: {global_stats['analyzed']}
   • En attente: {global_stats['pending']}
   • Score moyen global: {global_stats['avg_score']}/100
   • Total anomalies: {global_stats['total_anomalies']}

🤖 Améliorations apportées:
   • Seuils de détection: main_oeuvre(35%), materiaux(25%), pieces(25%)
   • Algorithme de scoring: pondération non-linéaire
   • Détection anomalies: delta > 40%
"""
        return report
    
    def run(self):
        """Boucle principale de l'agent."""
        logger.info("🎯 Agent MarketScore démarré - Surveillance active")
        
        last_hourly_report = datetime.utcnow()
        
        try:
            while self.running:
                # Traiter les devis en attente
                processed = self.check_and_process()
                
                if processed > 0:
                    logger.info(f"✅ {processed} devis traités")
                
                # Rapport horaire
                now = datetime.utcnow()
                if (now - last_hourly_report).total_seconds() >= 3600:
                    report = self.generate_hourly_report()
                    print(report)
                    logger.info("Rapport horaire généré")
                    last_hourly_report = now
                
                # Attendre 5 minutes
                time.sleep(300)
                
        except KeyboardInterrupt:
            logger.info("🛑 Arrêt demandé par l'utilisateur")
        finally:
            self.pricing.close()
            logger.info("👋 Agent MarketScore arrêté")
    
    def simulate_devis(self, secteur: str = "batiment", region: str = "IDF") -> str:
        """Simule un devis pour test."""
        devis_id = f"TEST_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        
        if secteur == "batiment":
            lignes = [
                {"categorie": "peinture", "description": "Peinture salon 30m²", "montant": 850},
                {"categorie": "electricite", "description": "Installation 3 prises", "montant": 320},
                {"categorie": "plomberie", "description": "Remplacement robinetterie", "montant": 280}
            ]
        elif secteur == "mecanique":
            lignes = [
                {"categorie": "vidange_standard", "description": "Vidange + filtres", "montant": 120},
                {"categorie": "freins_plaquettes_avant", "description": "Remplacement plaquettes AV", "montant": 180},
                {"categorie": "main_oeuvre_mecanique", "description": "Main d'oeuvre", "montant": 90}
            ]
        else:
            lignes = [
                {"categorie": "main_oeuvre", "description": "Prestation générique", "montant": 500}
            ]
        
        self.db.add_devis(devis_id, secteur, region, lignes)
        logger.info(f"📝 Devis test créé: {devis_id}")
        return devis_id


def main():
    """Point d'entrée principal."""
    agent = MarketScoreAgent()
    
    # Créer quelques devis de test si la base est vide
    stats = agent.db.get_global_stats()
    if stats['pending'] == 0 and stats['analyzed'] == 0:
        logger.info("🧪 Création de devis de test...")
        agent.simulate_devis("batiment", "IDF")
        agent.simulate_devis("mecanique", "IDF")
        agent.simulate_devis("batiment", "PACA")
    
    # Démarrer la surveillance
    agent.run()


if __name__ == "__main__":
    main()
