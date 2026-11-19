# TrustDevis Normalizer

Service de classification des lignes de devis pour TrustDevis.

## Description

L'Agent Normalizer classifie automatiquement chaque ligne d'un devis OCR dans une catégorie standardisée avec :
- Catégorie (ex: `painting.m2`, `brakes.unit`)
- Unité de mesure (`m2`, `hour`, `unit`, `item`)
- Quantité extraite
- Score de confiance

## Installation

```bash
pip install -r requirements.txt
```

## Démarrage

```bash
# Développement
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Production
uvicorn main:app --host 0.0.0.0 --port 8000
```

## Docker

```bash
docker build -t trustdevis-normalizer .
docker run -p 8000:8000 trustdevis-normalizer
```

## API Endpoints

### POST /normalize

Classifie une liste de lignes de devis.

**Request:**
```json
{
  "lines": [
    "Peinture salon 45m²",
    "Changement robinet cuisine",
    "Vidange + filtres 89€"
  ],
  "sector": "building"
}
```

**Response:**
```json
{
  "results": [
    {
      "orig_line": "Peinture salon 45m²",
      "category": "painting.m2",
      "unit": "m2",
      "qty": 45.0,
      "normalized_desc": "Peinture salon",
      "confidence": 92.5,
      "category_name": "Peinture au m²"
    }
  ],
  "stats": {
    "total_lines": 3,
    "categorized": 3,
    "high_confidence": 2,
    "medium_confidence": 1,
    "low_confidence": 0,
    "categories_found": 2
  }
}
```

### GET /categories

Liste toutes les catégories disponibles.

### GET /categories/{category_id}

Détail d'une catégorie spécifique.

### GET /health

Health check du service.

## Catégories

### Bâtiment

| Catégorie | Description | Unité |
|-----------|-------------|-------|
| `painting.m2` | Peinture au m² | m2 |
| `plumbing.fix` | Intervention plomberie | unit |
| `plumbing.install` | Installation sanitaire | unit |
| `roofing.m2` | Toiture au m² | m2 |
| `electricity.point` | Point électrique | unit |
| `electricity.light` | Éclairage / Luminaire | unit |
| `tiling.m2` | Carrelage au m² | m2 |
| `flooring.m2` | Parquet / Sol souple | m2 |
| `plastering.m2` | Plâtrerie / Placo | m2 |
| `insulation.m2` | Isolation au m² | m2 |
| `carpentry.door` | Porte / Portail | unit |
| `carpentry.window` | Fenêtre / Ouverture | unit |
| `masonry.m2` | Maçonnerie au m² | m2 |
| `demolition.m2` | Démolition au m² | m2 |
| `labor.hour` | Main d'œuvre générale | hour |
| `fees.fixed` | Frais fixes | unit |

### Mécanique

| Catégorie | Description | Unité |
|-----------|-------------|-------|
| `brakes.unit` | Freinage | unit |
| `oil.change` | Vidange | unit |
| `tires.unit` | Pneus / Roues | unit |
| `engine.parts` | Pièces moteur | unit |
| `exhaust.unit` | Échappement | unit |
| `clutch.unit` | Embrayage | unit |
| `suspension.unit` | Suspension | unit |
| `cooling.unit` | Refroidissement | unit |
| `ac.unit` | Climatisation | unit |
| `electrical.unit` | Électricité auto | unit |
| `bodywork.unit` | Carrosserie | unit |
| `labor.hour` | Main d'œuvre mécanique | hour |

## Scoring de Confiance

- **90-100%**: Très haute confiance - matching exact
- **70-89%**: Haute confiance - matching fuzzy fort
- **50-69%**: Confiance moyenne - vérification recommandée
- **<50%**: Faible confiance - revue manuelle nécessaire

## Support des Fautes d'Ortographe

Le service supporte les fautes courantes en français :
- `peintur` → `peinture`
- `robine` → `robinet`
- `etancheite` → `étanchéité`
- `maconerie` → `maçonnerie`

## Tests

```bash
# Test rapide
curl -X POST http://localhost:8000/normalize \
  -H "Content-Type: application/json" \
  -d '{"lines": ["Peinture chambre 25m²", "Changement mitigeur"]}'
```
