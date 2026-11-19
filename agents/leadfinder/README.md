# 🎯 TrustDevis LeadFinder

Agent de détection et scoring de leads pour travaux du bâtiment et garagistes.

## 📋 Description

LeadFinder est un service FastAPI qui :
- Détecte les opportunités de travaux sur multiples sources
- Score la pertinence des leads (0-100)
- Classifie la qualité (hot/warm/cold)
- Expose une API REST pour la gestion des leads

## 🏗️ Architecture

```
leadfinder/
├── main.py           # Service FastAPI + endpoints
├── models.py         # Modèles Pydantic (Lead, Filtres, etc.)
├── scorer.py         # Moteur de scoring 0-100
├── sources.py        # Connecteurs sources (placeholders)
├── requirements.txt  # Dépendances Python
├── Dockerfile        # Conteneurisation
└── README.md         # Ce fichier
```

## 🚀 Démarrage Rapide

### Local (sans Docker)

```bash
cd /root/.openclaw/workspace/trustdevis/agents/leadfinder
pip install -r requirements.txt
python main.py
```

Le service démarre sur `http://localhost:8000`

### Avec Docker

```bash
cd /root/.openclaw/workspace/trustdevis/agents/leadfinder
docker build -t trustdevis-leadfinder .
docker run -p 8000:8000 trustdevis-leadfinder
```

## 📡 API Endpoints

### Santé
- `GET /` - Info service
- `GET /health` - Health check
- `GET /stats` - Statistiques leads

### Leads
- `POST /leads/search` - Recherche avec filtres
- `GET /leads` - Liste avec query params
- `GET /leads/{id}` - Détail d'un lead
- `POST /leads` - Créer un lead (manuel)
- `DELETE /leads/{id}` - Supprimer un lead
- `POST /leads/{id}/score` - Recalculer le score
- `GET /leads/{id}/score-details` - Détails du scoring

### Sources
- `GET /sources` - Liste des sources disponibles
- `POST /sources/search` - Recherche sur sources externes

## 📊 Scoring

Le score (0-100) est calculé sur 5 critères pondérés :

| Critère | Poids | Description |
|---------|-------|-------------|
| Type travaux | 25% | Construction/Rénovation = plus haut |
| Budget | 25% | Budget estimé du projet |
| Urgence | 20% | Date souhaitée, mots-clés |
| Localisation | 15% | Complétude adresse |
| Contact | 15% | Qualité infos contact |

### Classification
- **Hot** (70-100) : Urgent, budget confirmé, contact complet
- **Warm** (40-69) : Intéressant, à qualifier
- **Cold** (0-39) : Faible priorité

## 🔌 Sources (Placeholders)

Les connecteurs suivants sont structurés mais nécessitent une implémentation réelle :

### 1. Leboncoin
- **Type** : Scraping annonces immobilières
- **Challenge** : Protection Datadome
- **Solution** : Proxies rotatifs, Playwright, ou API payante

### 2. SeLoger
- **Type** : Scraping annonces
- **Challenge** : API privée
- **Solution** : Partenariat ou scraping avancé

### 3. DataGouv (Permis de construire)
- **Type** : API ou CSV
- **URL** : https://www.data.gouv.fr/fr/datasets/permis-de-construire/
- **Status** : Données publiques disponibles

### 4. Twitter/X
- **Type** : API v2
- **Recherche** : "cherche artisan", "devis travaux", etc.
- **Nécessite** : Clé API Twitter

## 🔧 Configuration

Variables d'environnement :

```bash
PORT=8000              # Port du service
HOST=0.0.0.0           # Interface réseau
DEBUG=false            # Mode debug (reload)
TWITTER_BEARER_TOKEN=  # Pour source Twitter
```

## 📝 Exemples d'utilisation

### Créer un lead
```bash
curl -X POST http://localhost:8000/leads \
  -H "Content-Type: application/json" \
  -d '{
    "id": "test-001",
    "source": "manual",
    "type_travaux": "renovation",
    "sous_type": "salle_de_bain",
    "localisation": {
      "ville": "Lyon",
      "code_postal": "69001"
    },
    "budget_estime": 15000,
    "description": "Rénovation complète salle de bain"
  }'
```

### Rechercher des leads
```bash
# Tous les leads "hot"
curl "http://localhost:8000/leads?qualite=hot"

# Par localisation et budget
curl "http://localhost:8000/leads?ville=Lyon&budget_min=10000"

# Avec pagination
curl "http://localhost:8000/leads?limit=10&offset=0"
```

### Lancer une recherche sur les sources
```bash
curl -X POST http://localhost:8000/sources/search \
  -H "Content-Type: application/json" \
  -d '{
    "sources": ["datagouv_permis"],
    "departement": "69"
  }'
```

## 🗺️ Roadmap

### Phase 1 (MVP)
- [x] Structure API FastAPI
- [x] Modèles de données
- [x] Moteur de scoring
- [x] Placeholders sources

### Phase 2 (Intégration)
- [ ] Connecteur DataGouv fonctionnel
- [ ] Scraping Leboncoin (avec proxies)
- [ ] Intégration Twitter API
- [ ] Persistance PostgreSQL

### Phase 3 (Scaling)
- [ ] File de traitement (Celery/Redis)
- [ ] Alertes webhooks
- [ ] Dashboard analytics
- [ ] ML pour amélioration scoring

## 🔗 Intégration TrustDevis

Ce service est conçu pour s'intégrer avec :
- **Agent Verificateur** : Vérification des leads qualifiés
- **Agent ArtisanMatcher** : Matching leads ↔ artisans
- **Base de données centrale** : Persistance des leads

## 📄 Licence

Propriétaire - TrustDevis
