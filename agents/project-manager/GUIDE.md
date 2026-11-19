# Agent Project Manager - TrustDevis

## Démarrage rapide

```bash
# Installation des dépendances
npm install

# Configuration
cp .env.example .env
# Éditer .env avec vos paramètres

# Initialisation de la base de données
npm run db:migrate

# Seed (données de test)
npm run db:seed

# Démarrage du serveur
npm run dev
```

## Structure

```
project-manager/
├── api/              # Serveur Express + Routes
├── database/         # Connexion SQLite + Migrations
├── models/           # Classes métier
├── services/         # Logique métier
├── utils/            # Utilitaires
└── tests/            # Tests Jest
```

## Fonctionnalités

✅ **Création projet** - Nom, adresse, type, budget, dates, artisans
✅ **Suivi chantier** - Étapes, photos, validation client, alertes retard
✅ **Gestion financière** - Devis vs réel, acomptes, reste à payer, alertes budget
✅ **Documents** - Contrats, factures, assurances, dossier final
✅ **API endpoints** - CRUD complet, upload, timeline, alertes
✅ **Dashboard** - Vue d'ensemble, calendrier, alertes

## API

Le serveur démarre sur le port 3003 (configurable via PORT dans .env)

Voir `api/README.md` pour la documentation complète des endpoints.

### Endpoints principaux

- `GET /api/projects` - Liste des projets
- `POST /api/projects` - Créer un projet
- `GET /api/dashboard` - Dashboard global
- `GET /api/dashboard/project/:id` - Dashboard projet
- `POST /api/documents/upload` - Upload de fichiers

## Modèles de données

### Project
- id, name, address, work_type
- budget_total, budget_spent
- start_date, end_date, actual_start_date, actual_end_date
- status (planning, in_progress, completed)

### ProjectStep
- id, project_id, name, description
- status (pending, in_progress, completed)
- planned_start_date, planned_end_date
- client_validated

### ProjectAlert
- Types: budget_warning, budget_exceeded, delay_warning, delay_exceeded
- Severity: info, warning, critical

### ProjectFinance
- Types: estimate, deposit, progress_payment, final_payment, expense

### ProjectDocument
- Types: contract, estimate, invoice, insurance, photo, plan, permit, final_dossier
