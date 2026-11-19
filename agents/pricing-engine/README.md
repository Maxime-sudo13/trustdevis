# TrustDevis Pricing Engine

Service FastAPI pour le calcul des prix médians du marché par catégorie et région.

## Architecture

```
pricing-engine/
├── main.py           # Service FastAPI + endpoints
├── database.py       # Modèles SQLAlchemy + requêtes
├── calculator.py     # Logique de calcul (médiane, percentiles)
├── seed_data.py      # Données initiales réalistes
├── requirements.txt  # Dépendances
├── Dockerfile        # Containerisation
└── README.md         # Documentation
```

## Endpoints API

### GET /pricing/{category}/{region_code}
Retourne les statistiques de prix pour une catégorie et région.

**Exemple:**
```bash
curl http://localhost:8000/pricing/peinture/IDF
```

**Réponse:**
```json
{
  "category": "peinture",
  "region_code": "IDF",
  "region_name": "Île-de-France",
  "unit": "m²",
  "count": 150,
  "median": 35.50,
  "percentile_25": 28.00,
  "percentile_75": 42.00,
  "percentile_90": 50.00,
  "min": 20.00,
  "max": 65.00,
  "labor_coefficient": 1.25
}
```

### POST /pricing/ingest
Ajoute un nouveau prix au dataset.

**Exemple:**
```bash
curl -X POST http://localhost:8000/pricing/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "category": "peinture",
    "region_code": "IDF",
    "price": 38.00,
    "unit": "m²",
    "source": "artisan_paris_001"
  }'
```

### GET /pricing/stats
Retourne les statistiques globales.

**Exemple:**
```bash
curl http://localhost:8000/pricing/stats
```

## Démarrage

### Local (développement)
```bash
pip install -r requirements.txt
python seed_data.py  # Initialise la base avec données réalistes
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Docker
```bash
docker build -t trustdevis-pricing .
docker run -p 8000:8000 trustdevis-pricing
```

## Données

Les données initiales incluent:
- **Bâtiment**: peinture, plomberie, toiture, électricité
- **Mécanique**: freins, vidange, pneus, main d'œuvre
- **Régions**: IDF, PACA, Auvergne-Rhône-Alpes, etc.

Basé sur les tarifs moyens France 2024.

## Stack Technique

- FastAPI
- SQLAlchemy
- SQLite (dev) / PostgreSQL (prod)
- NumPy pour les calculs statistiques
