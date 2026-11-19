# 🤖 Agent MarketScore - TrustDevis

Agent d'analyse automatique des devis avec scoring de confiance basé sur les prix du marché.

## 🎯 Mission

Analyser les devis collectés et produire des scores de confiance 0-100 en comparant aux prix du marché régional.

## 📁 Structure

```
marketscore/
├── agent.py           # Agent principal (surveillance + analyse)
├── main.py            # Service FastAPI (endpoints HTTP)
├── scorer.py          # Algorithme de scoring
├── rules.py           # Règles métier par secteur
├── llm_integration.py # Intégration Kimi K2 pour justifications
├── test_agent.py      # Tests unitaires
├── start.sh           # Script de démarrage
├── config.json        # Configuration
├── marketscore.db     # Base de données SQLite
├── marketscore.log    # Logs
└── results/           # Résultats JSON
```

## 🚀 Démarrage

```bash
# Mode interactif
python3 agent.py

# Ou via le script
./start.sh
```

## 📊 Fonctionnement

### 1. Surveillance (toutes les 5 min)
- Vérifie les nouveaux devis dans `devis_queue`
- Récupère les devis avec status='pending'

### 2. Analyse
Pour chaque ligne du devis :
- Extraction de la catégorie
- Récupération de la médiane du marché (pricing.db)
- Calcul du delta %
- Détection d'anomalies (delta > 40%)

### 3. Scoring (0-100)
```
Delta ≤ 5%  → Score 90-95
Delta 5-15% → Score 70-90
Delta 15-25% → Score 40-70
Delta > 25% → Score 0-40
```

### 4. Niveaux de risque
- 🟢 **low**: Delta ≤ 25%
- 🟡 **moderate**: Delta 25-40%
- 🔴 **high**: Delta > 40%

### 5. Revue humaine
Nécessaire si :
- Score < 60
- Risque = high
- Delta global > 30%

## 🔌 API Endpoints (main.py)

```bash
# Health check
GET /health

# Scoring complet
POST /score
{
  "devis": {
    "secteur": "batiment",
    "lignes": [...]
  },
  "market_stats": {...}
}

# Scoring simplifié
POST /score/simple
```

## 📈 Rapport horaire

L'agent génère automatiquement un rapport toutes les heures :
- Nombre de devis analysés
- Score moyen
- Anomalies détectées
- Répartition par niveau de risque

## 🗄️ Base de données

### Tables
- `devis_queue`: File d'attente des devis
- `analysis_results`: Résultats d'analyse
- `learning_stats`: Statistiques d'apprentissage

### Schéma JSON résultat
```json
{
  "devis_id": "DEV_001",
  "score": 75,
  "delta_pct": 15.2,
  "risk_level": "low",
  "lignes_detail": [...],
  "justification": [...],
  "actions": [...],
  "requires_human_review": false,
  "timestamp": "2026-03-09T01:30:00Z"
}
```

## ⚙️ Configuration

Éditer `config.json` :
```json
{
  "check_interval_minutes": 5,
  "thresholds": {
    "moderate_risk": 25,
    "high_risk": 40,
    "human_review_score": 60
  },
  "weights": {
    "main_oeuvre": 0.35,
    "materiaux": 0.25,
    "pieces": 0.25,
    ...
  }
}
```

## 🧪 Tests

```bash
python3 test_agent.py
```

## 📝 Logs

```bash
# Suivre les logs en temps réel
tail -f marketscore.log
```

## 🔄 Intégration

L'agent s'intègre avec :
- **Pricing Engine**: Base de données des prix du marché
- **Normalizer**: Extraction des lignes de devis
- **OCR Parser**: Récupération des devis scannés
- **CRM**: Notification des anomalies

## 🛡️ Règles de langage

**INTERDIT** : "arnaque", "fraude", "escroquerie"
**OBLIGATOIRE** : "probabilité de sur-tarification", "écart significatif"

## 📊 Statistiques actuelles

- Total devis analysés: 3
- Score moyen: 22.0/100
- Anomalies détectées: 6
- Répartition: 🔴 2 | 🟡 0 | 🟢 1

---

**TrustDevis** - Vérification intelligente de devis
