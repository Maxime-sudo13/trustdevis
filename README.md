<p align="center">
  <img src="logo_trustdevis.svg" alt="TrustDevis" width="96">
</p>

# TrustDevis

**Votre devis est-il honnête ?** TrustDevis analyse un devis d'artisan (bâtiment, chauffage, mécanique…) et le compare aux prix du marché de la région pour donner un **score de confiance**, une justification ligne par ligne et des conseils concrets au client.

Projet personnel construit comme une plateforme de **microservices Python (FastAPI)** orchestrés avec **Docker Compose**, avec une landing page, un tableau de bord et une application mobile React Native.

---

## Comment ça marche

```
 Devis PDF / photo
        │
        ▼
 ┌──────────────┐    ┌──────────────┐    ┌────────────────┐    ┌──────────────┐
 │  OCR Parser  │──▶│  Normalizer  │──▶│ Pricing Engine │──▶│  MarketScore │──▶  Score 0-100
 │  Tesseract   │    │ lignes → cat.│    │ médianes / zone│    │ règles (+LLM)│     + justification
 └──────────────┘    └──────────────┘    └────────────────┘    └──────────────┘

 Services métier autour : LeadFinder (artisans) · CRM (relances) · Compliance (RGPD) · Billing (Stripe)
```

| Service | Port | Rôle |
|---|---|---|
| `ocr-parser` | 8001 | Extraction du texte et des lignes d'un devis PDF ou image (Tesseract, poppler) |
| `normalizer` | 8002 | Classe chaque ligne dans une catégorie de travaux, détecte unité et quantité |
| `pricing-engine` | 8003 | Prix médians / quartiles par catégorie et région, avec coefficient main-d'œuvre régional |
| `marketscore` | 8004 | Score de confiance du devis, niveau de risque, justification et actions conseillées |
| `leadfinder` | 8005 | Recherche et scoring d'artisans |
| `crm` | 8006 | Clients, devis et relances planifiées (APScheduler + Redis) |
| `compliance` | 8007 | RGPD : consentements, export et suppression des données, registre des traitements |
| `billing` | 8008 | Plans d'abonnement et paiements Stripe (mode test) |

Chaque service expose sa documentation interactive Swagger sur `http://localhost:<port>/docs`.

## Démarrer en local

Prérequis : [Docker Desktop](https://www.docker.com/products/docker-desktop/) lancé.

```bash
git clone https://github.com/Maxime-sudo13/trustdevis.git
cd trustdevis
docker compose up -d --build     # ~5 min la première fois (image OCR)
docker compose ps                # les 8 agents doivent passer en "healthy"
```

Aucune configuration n'est nécessaire : les valeurs par défaut suffisent. Pour les changer (mots de passe locaux, clé Stripe de test, clé LLM optionnelle), copiez `.env.example` en `.env`.

Arrêter : `docker compose down` (ajoutez `-v` pour effacer aussi les données).

### Essayer l'API

```bash
# Prix du marché d'une installation de chaudière en Île-de-France
curl http://localhost:8003/pricing/installation_chaudiere/IDF

# Classer des lignes de devis
curl -X POST http://localhost:8002/normalize -H "Content-Type: application/json" \
  -d '{"lines": ["Pose carrelage 20m2", "Remplacement chaudiere gaz"], "sector": "batiment"}'

# Scorer un devis par rapport au marché
curl -X POST http://localhost:8004/score -H "Content-Type: application/json" -d '{
  "devis": {"secteur": "batiment", "lignes": [
    {"categorie": "main_oeuvre", "description": "Pose carrelage", "montant": 1500},
    {"categorie": "materiaux", "description": "Carrelage premium", "montant": 800}]},
  "market_stats": {"region": "IDF", "medianes": {
    "main_oeuvre": {"median": 1200, "q1": 1000, "q3": 1400},
    "materiaux":   {"median": 700,  "q1": 600,  "q3": 800}}},
  "historique": []
}'
# → {"score": 53, "risk_level": "low", "justification": ["main_oeuvre: Écart de 25% ..."], ...}

# Extraire un devis PDF
curl -F "file=@mon-devis.pdf" http://localhost:8001/extract
```

### Les pages web

Ce sont des pages statiques (le tableau de bord tourne sur des données de démonstration) :

```bash
python -m http.server 5500
```

- Landing page : http://localhost:5500/landing/
- Générateur de devis : http://localhost:5500/landing/generer-devis.html
- Tableau de bord : http://localhost:5500/dashboard/

### Application mobile

`mobile/` contient l'application React Native / Expo (scan de devis, analyse, résultats, compte). Voir [mobile/README.md](mobile/README.md).

## Structure

```
agents/           un dossier par microservice (FastAPI + Dockerfile + README)
  ocr-parser/  normalizer/  pricing-engine/  marketscore/
  leadfinder/  crm/  compliance/  billing/
  ml-engine/  quote-generator/  artisans-compare/  project-manager/  ux-optimizer/   ← modules expérimentaux
landing/          site vitrine + générateur de devis
dashboard/        tableau de bord de supervision des agents
mobile/           application React Native (Expo)
data/             schéma SQL et jeu de prix de démonstration
docs/             architecture, référence API, sécurité, déploiement
docker-compose.yml
```

## Stack

Python 3.11 · FastAPI · Pydantic · SQLAlchemy · PostgreSQL · Redis · Tesseract OCR · APScheduler · Stripe · Docker Compose · HTML/CSS/JS · React Native (Expo, TypeScript, Zustand)

## État du projet

Prototype fonctionnel : les 8 services ci-dessus démarrent et répondent. Les modules marqués « expérimentaux » (ML, génération de devis, comparaison d'artisans, gestion de chantier, UX) sont des explorations non branchées à la stack Docker. La documentation de `docs/` décrit l'architecture cible, plus large que ce qui est implémenté.
