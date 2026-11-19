# TrustDevis - Architecture Technique

> Version 1.0 | 9 Mars 2026 | Agent Architecte

---

## Vue d'Ensemble

TrustDevis est une plateforme modulaire de vérification de devis, construite sur une architecture micro-services avec agents spécialisés.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              TRUSTDEVIS PLATFORM                            │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │   CLIENT    │  │   CLIENT    │  │   CLIENT    │  │      DASHBOARD      │ │
│  │   Mobile    │  │    Web      │  │   API Ext   │  │      Admin (3000)   │ │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────────┬──────────┘ │
│         │                │                │                    │            │
│         └────────────────┴────────────────┘                    │            │
│                          │                                     │            │
│                          ▼                                     ▼            │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                      API GATEWAY (Nginx)                            │   │
│  │                    Port 80/443 - HTTPS                              │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                     AGENT DIRECTEUR (3001)                          │   │
│  │              Orchestration, Routing, Authentification               │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│         ┌──────────────────────────┼──────────────────────────┐             │
│         │                          │                          │             │
│         ▼                          ▼                          ▼             │
│  ┌─────────────┐           ┌─────────────┐           ┌─────────────────┐   │
│  │ AGENT OCR   │           │ AGENT       │           │ AGENT PRICING   │   │
│  │ (3002)      │           │ NORMALIZER  │           │ (3004)          │   │
│  │             │──────────▶│ (3003)      │──────────▶│                 │   │
│  │ Extraction  │           │ Structuration           │ Benchmark       │   │
│  │ Texte/Table │           │ Standardisation         │ Prix Marché     │   │
│  └─────────────┘           └─────────────┘           └────────┬────────┘   │
│                                                               │            │
│                                                               ▼            │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                     AGENT MARKETSCORE (3005)                        │   │
│  │              Scoring, Recommandations, Rapports                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                     BASE DE DONNÉES (PostgreSQL)                    │   │
│  │                         Port 5432                                   │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Flux de Données Détaillé

### 1. Upload et Traitement d'un Devis

```
┌─────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Client │────▶│   Upload    │────▶│  Agent OCR  │────▶│  Raw Data   │
│         │     │   (API)     │     │   (3002)    │     │   (JSON)    │
└─────────┘     └─────────────┘     └─────────────┘     └──────┬──────┘
                                                               │
┌─────────┐     ┌─────────────┐     ┌─────────────┐            │
│  Client │◀────│   Rapport   │◀────│ MarketScore │◀───────────┘
│         │     │   Final     │     │   (3005)    │
└─────────┘     └─────────────┘     └──────┬──────┘
                                           │
                              ┌────────────┴────────────┐
                              │                         │
                              ▼                         ▼
                        ┌─────────────┐           ┌─────────────┐
                        │   Pricing   │◀─────────▶│  Normalizer │
                        │   (3004)    │           │   (3003)    │
                        └─────────────┘           └─────────────┘
```

### 2. Séquence Complète

```
1. POST /api/v1/devis/upload
   → Upload PDF/Image
   → Retour: devis_id

2. Agent OCR (3002) - POST /ocr/extract
   → Input: fichier PDF/Image
   → Output: { raw_text, tables, confidence_score }

3. Agent Normalizer (3003) - POST /normalize
   → Input: raw_text + secteur
   → Output: { 
       client: {...}, 
       prestations: [...], 
       materiaux: [...], 
       main_oeuvre: {...},
       totaux: {...}
     }

4. Agent Pricing (3004) - POST /pricing/analyze
   → Input: prestations normalisées + localisation
   → Output: { 
       benchmarks: [...],
       anomalies: [...],
       market_position: "above|below|within"
     }

5. Agent MarketScore (3005) - POST /score/calculate
   → Input: devis normalisé + benchmarks
   → Output: {
       trust_score: 0-100,
       risk_level: "low|medium|high",
       recommendations: [...],
       rapport_url: "..."
     }

6. GET /api/v1/devis/{id}/rapport
   → Retour: rapport complet au client
```

---

## Description des Agents

### Agent Directeur (Port 3001)

**Rôle:** Cœur orchestrateur de la plateforme

**Responsabilités:**
- Routage des requêtes vers les agents spécialisés
- Authentification et autorisation (JWT)
- Gestion des sessions utilisateurs
- Rate limiting et throttling
- Monitoring et health checks
- Agrégation des réponses

**Endpoints:**
```
POST   /api/v1/auth/login
POST   /api/v1/auth/register
POST   /api/v1/auth/refresh
POST   /api/v1/devis/upload
GET    /api/v1/devis/{id}
GET    /api/v1/devis/{id}/rapport
GET    /api/v1/devis/{id}/status
DELETE /api/v1/devis/{id}
GET    /api/v1/user/profile
PUT    /api/v1/user/profile
GET    /api/v1/stats/dashboard
```

**Tech Stack:**
- Node.js / Express
- JWT (jsonwebtoken)
- Redis (sessions/cache)
- Winston (logging)

---

### Agent OCR (Port 3002)

**Rôle:** Extraction intelligente de données depuis les documents

**Responsabilités:**
- Extraction texte depuis PDF (texte natif + OCR)
- Extraction texte depuis images (photos de devis)
- Détection et parsing des tableaux
- Reconnaissance des structures de devis
- Scoring de confiance par zone

**Endpoints:**
```
POST /ocr/extract          # Extraction complète
POST /ocr/extract-text     # Texte brut uniquement
POST /ocr/extract-tables   # Tableaux uniquement
GET  /ocr/supported-formats
GET  /health
```

**Tech Stack:**
- Node.js / Express
- pdf-parse (PDF natif)
- Tesseract.js / Kimi Vision API (OCR)
- Sharp (traitement image)

**Formats Supportés:**
- PDF (texte natif et scanné)
- JPG, PNG, WEBP, TIFF
- Taille max: 10MB

---

### Agent Normalizer (Port 3003)

**Rôle:** Structuration et standardisation des données

**Responsabilités:**
- Parsing du texte brut OCR
- Identification du secteur (bâtiment, mécanique, etc.)
- Extraction structurée des entités:
  - Informations client/artisan
  - Liste des prestations
  - Matériaux et quantités
  - Main d'œuvre
  - Totaux et TVA
- Normalisation des unités
- Validation des données

**Endpoints:**
```
POST /normalize            # Normalisation complète
POST /normalize/secteur    # Détection secteur uniquement
POST /normalize/validate   # Validation structure
GET  /health
```

**Tech Stack:**
- Node.js / Express
- Kimi K2 API (LLM pour parsing intelligent)
- Joi (validation schémas)

**Schéma de Sortie:**
```json
{
  "version": "1.0",
  "secteur": "batiment|mecanique|...",
  "metadata": {
    "artisan": { "nom": "...", "siret": "...", "adresse": "..." },
    "client": { "nom": "...", "adresse_chantier": "..." },
    "devis": { "numero": "...", "date": "...", "validite": "..." }
  },
  "prestations": [
    {
      "ligne": 1,
      "description": "...",
      "quantite": 10,
      "unite": "m²",
      "prix_unitaire_ht": 45.50,
      "total_ht": 455.00,
      "tva": 20
    }
  ],
  "recapitulatif": {
    "total_ht": 1000.00,
    "total_tva": 200.00,
    "total_ttc": 1200.00
  }
}
```

---

### Agent Pricing (Port 3004)

**Rôle:** Benchmarking et analyse des prix

**Responsabilités:**
- Recherche de prix de référence par prestation
- Analyse géolocalisée (prix par région)
- Détection d'anomalies tarifaires
- Historisation des benchmarks
- Mise à jour des bases de prix

**Endpoints:**
```
POST /pricing/analyze      # Analyse complète d'un devis
POST /pricing/benchmark    # Benchmark d'une prestation
GET  /pricing/reference/{secteur}/{prestation}
GET  /pricing/stats/{secteur}
POST /pricing/feedback     # Feedback utilisateur sur prix
GET  /health
```

**Tech Stack:**
- Node.js / Express
- PostgreSQL (base de prix)
- Redis (cache)
- API externes (Batiactu, Argus, etc.)

**Sources de Données:**
- Base interne (historique TrustDevis)
- Bases publiques (Batiactu, etc.)
- APIs partenaires
- Contributions utilisateurs (anonymisées)

---

### Agent MarketScore (Port 3005)

**Rôle:** Scoring et génération de recommandations

**Responsabilités:**
- Calcul du TrustScore (0-100)
- Évaluation du niveau de risque
- Génération de recommandations personnalisées
- Création de rapports PDF/HTML
- Suivi des tendances

**Endpoints:**
```
POST /score/calculate      # Calcul du score
GET  /score/{devis_id}     # Récupération score
POST /score/feedback       # Feedback utilisateur
GET  /rapport/{devis_id}   # Génération rapport
GET  /rapport/{id}/pdf     # Téléchargement PDF
GET  /health
```

**Algorithmique:**
```
TrustScore = (
  0.40 * PriceScore +      // Position par rapport au marché
  0.25 * ConsistencyScore + // Cohérence interne du devis
  0.20 * DetailScore +      // Niveau de détail
  0.15 * SourceScore        // Fiabilité de la source
)

RiskLevel:
- HIGH:   Score < 40 ou anomalies critiques
- MEDIUM: Score 40-70 ou anomalies mineures
- LOW:    Score > 70 et cohérent
```

**Tech Stack:**
- Node.js / Express
- Puppeteer (PDF generation)
- Chart.js (visualisations)

---

### Dashboard Admin (Port 3000)

**Rôle:** Interface d'administration et monitoring

**Responsabilités:**
- Vue d'ensemble des métriques
- Gestion des utilisateurs
- Monitoring des agents
- Configuration des seuils
- Analytics et rapports

**Tech Stack:**
- React / Next.js
- Tailwind CSS
- Recharts (graphiques)

---

## Schéma de Base de Données

### Diagramme Entité-Relation

```
┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
│     users       │       │     devis       │       │   analyses      │
├─────────────────┤       ├─────────────────┤       ├─────────────────┤
│ id (PK)         │──┐    │ id (PK)         │──┐    │ id (PK)         │
│ email           │  │    │ user_id (FK)    │──┘    │ devis_id (FK)   │──┘
│ password_hash   │  │    │ filename        │       │ trust_score     │
│ nom             │  │    │ file_path       │       │ risk_level      │
│ prenom          │  │    │ secteur         │       │ anomalies       │
│ telephone       │  │    │ status          │       │ recommendations │
│ adresse         │  │    │ raw_data        │       │ created_at      │
│ role            │  │    │ normalized_data │       └─────────────────┘
│ created_at      │  │    │ trust_score     │
│ updated_at      │  │    │ created_at      │
└─────────────────┘  │    │ updated_at      │
                     │    └─────────────────┘
                     │              │
                     │              ▼
                     │    ┌─────────────────┐
                     │    │  benchmarks     │
                     │    ├─────────────────┤
                     └───▶│ id (PK)         │
                          │ devis_id (FK)   │
                          │ prestation      │
                          │ prix_propose    │
                          │ prix_marche_min │
                          │ prix_marche_max │
                          │ prix_marche_avg │
                          │ ecart_percent   │
                          │ source          │
                          └─────────────────┘

┌─────────────────┐       ┌─────────────────┐
│  price_references      │       │    sessions     │
├─────────────────┤       ├─────────────────┤
│ id (PK)         │       │ id (PK)         │
│ secteur         │       │ user_id (FK)    │
│ categorie       │       │ token           │
│ prestation      │       │ expires_at      │
│ unite           │       │ created_at      │
│ prix_min        │       └─────────────────┘
│ prix_max        │
│ prix_avg        │
│ region          │
│ source          │
│ date_maj        │
└─────────────────┘
```

### Détail des Tables

#### users
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    nom VARCHAR(100),
    prenom VARCHAR(100),
    telephone VARCHAR(20),
    adresse JSONB,
    role VARCHAR(20) DEFAULT 'user', -- user, admin, artisan
    email_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

#### devis
```sql
CREATE TABLE devis (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    filename VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_size INTEGER,
    mime_type VARCHAR(50),
    secteur VARCHAR(50), -- batiment, mecanique, etc.
    status VARCHAR(20) DEFAULT 'pending', -- pending, processing, completed, error
    raw_data JSONB, -- Résultat OCR brut
    normalized_data JSONB, -- Données structurées
    trust_score INTEGER,
    rapport_url VARCHAR(500),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

#### analyses
```sql
CREATE TABLE analyses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    devis_id UUID REFERENCES devis(id) ON DELETE CASCADE,
    trust_score INTEGER NOT NULL CHECK (trust_score >= 0 AND trust_score <= 100),
    risk_level VARCHAR(10) CHECK (risk_level IN ('low', 'medium', 'high')),
    price_score INTEGER,
    consistency_score INTEGER,
    detail_score INTEGER,
    source_score INTEGER,
    anomalies JSONB DEFAULT '[]',
    recommendations JSONB DEFAULT '[]',
    rapport_html TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### benchmarks
```sql
CREATE TABLE benchmarks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    devis_id UUID REFERENCES devis(id) ON DELETE CASCADE,
    prestation_id VARCHAR(100),
    description TEXT,
    quantite DECIMAL(10,2),
    unite VARCHAR(20),
    prix_propose DECIMAL(10,2),
    prix_marche_min DECIMAL(10,2),
    prix_marche_max DECIMAL(10,2),
    prix_marche_avg DECIMAL(10,2),
    ecart_percent DECIMAL(5,2),
    source VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### price_references
```sql
CREATE TABLE price_references (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    secteur VARCHAR(50) NOT NULL,
    categorie VARCHAR(100) NOT NULL,
    prestation VARCHAR(255) NOT NULL,
    description TEXT,
    unite VARCHAR(20),
    prix_min DECIMAL(10,2),
    prix_max DECIMAL(10,2),
    prix_avg DECIMAL(10,2),
    region VARCHAR(50) DEFAULT 'national',
    source VARCHAR(100),
    date_maj DATE DEFAULT CURRENT_DATE,
    active BOOLEAN DEFAULT TRUE
);
```

---

## Ports et Services

| Service | Port | Description | Health Check |
|---------|------|-------------|--------------|
| Dashboard | 3000 | Interface admin React | GET /health |
| Agent Directeur | 3001 | API Gateway / Orchestration | GET /health |
| Agent OCR | 3002 | Extraction document | GET /health |
| Agent Normalizer | 3003 | Structuration données | GET /health |
| Agent Pricing | 3004 | Benchmark prix | GET /health |
| Agent MarketScore | 3005 | Scoring et rapports | GET /health |
| PostgreSQL | 5432 | Base de données | pg_isready |
| Redis | 6379 | Cache / Sessions | redis-cli ping |
| Nginx | 80/443 | Reverse proxy | /nginx-health |

---

## Communication Inter-Services

### Protocole

Tous les agents communiquent via HTTP/JSON REST API.

### Authentification Inter-Services

```
Headers requis:
X-Internal-API-Key: {INTERNAL_API_KEY}
X-Service-Name: {service_name}
```

### Retry Policy

```javascript
{
  retries: 3,
  backoff: 'exponential',
  initialDelay: 1000,
  maxDelay: 10000
}
```

### Circuit Breaker

```javascript
{
  failureThreshold: 5,
  resetTimeout: 30000,
  halfOpenRequests: 3
}
```

---

## Sécurité

### Flux d'Authentification

```
Client ──POST /auth/login──▶ Agent Directeur
                               │
                               ▼
                         ┌─────────────┐
                         │  Vérifier   │
                         │  credentials│
                         └──────┬──────┘
                                │
                                ▼
                         ┌─────────────┐
                         │ Générer JWT │
                         │  + Refresh  │
                         └──────┬──────┘
                                │
Client ◀──{access, refresh}────┘

Client ──GET /devis/{id}──▶ Agent Directeur
                               │
                               ▼
                         ┌─────────────┐
                         │ Vérifier    │
                         │ JWT valide? │
                         └──────┬──────┘
                                │
                    ┌───────────┴───────────┐
                    │ NON                   │ OUI
                    ▼                       ▼
              401 Unauthorized      Route vers agent
```

### Chiffrement

- **Transport:** TLS 1.3 minimum
- **Données sensibles:** AES-256-GCM
- **Mots de passe:** bcrypt (cost: 12)
- **Tokens:** JWT RS256 (asymétrique)

---

## Monitoring et Logging

### Métriques Clés

| Métrique | Source | Seuil d'alerte |
|----------|--------|----------------|
| CPU Usage | All services | > 80% |
| Memory Usage | All services | > 85% |
| Response Time | All services | > 2000ms |
| Error Rate | All services | > 5% |
| Queue Depth | Agent OCR | > 100 |

### Logs

- Format: JSON structuré
- Niveaux: ERROR, WARN, INFO, DEBUG
- Rotation: 7 jours
- Centralisation: Agent Directeur

---

## Scalabilité

### Horizontal Scaling

Tous les agents sont stateless et peuvent être répliqués:

```yaml
# docker-compose.scale.yml
services:
  agent-ocr:
    deploy:
      replicas: 3
  agent-pricing:
    deploy:
      replicas: 2
```

### Load Balancing

Nginx en reverse proxy avec health checks:

```nginx
upstream agent_ocr {
    least_conn;
    server agent-ocr-1:3002;
    server agent-ocr-2:3002;
    server agent-ocr-3:3002;
    check interval=3000 rise=2 fall=3 timeout=1000;
}
```

---

## Roadmap Technique

### Phase 1 (MVP - Semaines 1-4)
- [x] Architecture de base
- [x] Agent Directeur
- [x] Agent OCR (basique)
- [x] Agent Normalizer
- [ ] Agent Pricing (base interne)
- [ ] Agent MarketScore (basique)

### Phase 2 (Semaines 5-8)
- [ ] Agent OCR avancé (Kimi Vision)
- [ ] Intégration APIs externes prix
- [ ] Dashboard admin v1
- [ ] Système de feedback utilisateur

### Phase 3 (Semaines 9-12)
- [ ] Machine Learning pour détection anomalies
- [ ] Base de prix communautaire
- [ ] API publique
- [ ] Mobile app

---

## Annexes

### Variables d'Environnement

Voir `DEPLOYMENT_GUIDE.md` pour la liste complète.

### Dépendances Externes

- **Kimi K2 API:** LLM pour parsing et analyse
- **PostgreSQL:** Base de données relationnelle
- **Redis:** Cache et sessions
- **Nginx:** Reverse proxy et load balancing

### Documentation Complémentaire

- `API_REFERENCE.md` - Documentation API détaillée
- `DEPLOYMENT_GUIDE.md` - Guide de déploiement
- `SECURITY.md` - Checklist sécurité et RGPD
