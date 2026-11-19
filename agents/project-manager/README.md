# Agent Project Manager - TrustDevis

Outil de gestion de projet travaux pour artisans et clients.

## Architecture

```
project-manager/
├── api/              # Endpoints API
├── database/         # Schémas et migrations
├── models/           # Modèles de données
├── services/         # Logique métier
├── utils/            # Utilitaires
└── tests/            # Tests
```

## Fonctionnalités

1. **Création projet** - Nom, adresse, type, budget, dates, artisans
2. **Suivi chantier** - Étapes, photos, validation client, alertes retard
3. **Gestion financière** - Devis vs réel, acomptes, reste à payer, alertes budget
4. **Documents** - Contrats, factures, assurances, dossier final
5. **API** - CRUD, upload, timeline, alertes
6. **Dashboard** - Vue d'ensemble, calendrier, alertes

## Démarrage

```bash
# Installation
npm install

# Configuration
cp .env.example .env
# Éditer .env avec vos paramètres

# Démarrage
npm run dev
```

## API Endpoints

Voir `api/README.md`
