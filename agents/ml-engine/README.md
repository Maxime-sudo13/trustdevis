# TrustDevis ML Engine

Agent Data/ML pour la plateforme TrustDevis.

## Architecture

```
ml-engine/
├── models/           # Modèles entraînés (pickle/joblib)
├── data/            # Datasets et features
├── api/             # API FastAPI pour prédictions
├── training/        # Scripts d'entraînement
├── monitoring/      # Monitoring et métriques
├── notebooks/       # Exploration et analyse
├── tests/           # Tests unitaires
└── config/          # Configuration
```

## Modèles

1. **Fraud Detection** - Random Forest/XGBoost
2. **Price Prediction** - Régression avec intervalles
3. **Artisan Scoring** - Système de recommandation
4. **Market Analytics** - Analyse prédictive

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
# Entraîner tous les modèles
python training/train_all.py

# Lancer l'API
uvicorn api.main:app --reload
```

## API Endpoints

- `POST /predict/fraud` - Détection fraude
- `POST /predict/price` - Prédiction prix
- `POST /recommend/artisans` - Recommandation artisans
- `GET /analytics/trends` - Tendances marché
