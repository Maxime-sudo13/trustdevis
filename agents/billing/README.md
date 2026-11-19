# TrustDevis Billing Agent

Service de gestion des abonnements et paiements via Stripe pour la plateforme TrustDevis.

## 🎯 Fonctionnalités

- **Gestion des abonnements** : Création, modification, annulation
- **Paiements Stripe** : Intégration complète avec Stripe Checkout
- **Webhooks** : Gestion automatique des événements Stripe
- **Facturation** : Consultation des factures et historique
- **Plans tarifaires** : STARTER, PRO, ENTERPRISE

## 🚀 Démarrage Rapide

### Local

```bash
# Installation des dépendances
pip install -r requirements.txt

# Configuration
export STRIPE_SECRET_KEY="sk_test_..."
export STRIPE_WEBHOOK_SECRET="whsec_..."
export STRIPE_PUBLISHABLE_KEY="pk_test_..."

# Lancement
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Docker

```bash
# Build
docker build -t trustdevis-billing .

# Run
docker run -p 8000:8000 \
  -e STRIPE_SECRET_KEY="sk_test_..." \
  -e STRIPE_WEBHOOK_SECRET="whsec_..." \
  -e STRIPE_PUBLISHABLE_KEY="pk_test_..." \
  trustdevis-billing
```

## 📋 Plans Tarifaires

| Plan | Prix | Fonctionnalités |
|------|------|-----------------|
| **STARTER** | 29€/mois | 50 analyses/mois, support email |
| **PRO** | 79€/mois | 200 analyses/mois, support prioritaire, API access |
| **ENTERPRISE** | 149€/mois | Analyses illimitées, support dédié, API + Webhooks |

## 🔌 API Endpoints

### Souscriptions
- `POST /billing/subscribe` - Créer un abonnement
- `POST /billing/cancel` - Annuler un abonnement

### Facturation
- `GET /billing/invoice` - Récupérer les factures

### Webhooks
- `POST /billing/webhook` - Endpoint Stripe webhook

### Informations
- `GET /billing/plans` - Liste des plans disponibles
- `GET /health` - Health check

## 🔐 Variables d'Environnement

| Variable | Description | Requis |
|----------|-------------|--------|
| `STRIPE_SECRET_KEY` | Clé secrète Stripe | ✅ |
| `STRIPE_WEBHOOK_SECRET` | Secret webhook Stripe | ✅ |
| `STRIPE_PUBLISHABLE_KEY` | Clé publique Stripe | ✅ |
| `API_PORT` | Port du service (défaut: 8000) | ❌ |
| `LOG_LEVEL` | Niveau de log (défaut: INFO) | ❌ |

## 📝 Exemples d'Utilisation

### Créer un abonnement

```bash
curl -X POST http://localhost:8000/billing/subscribe \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_123",
    "plan_id": "pro",
    "success_url": "https://trustdevis.com/success",
    "cancel_url": "https://trustdevis.com/cancel"
  }'
```

### Annuler un abonnement

```bash
curl -X POST http://localhost:8000/billing/cancel \
  -H "Content-Type: application/json" \
  -d '{
    "subscription_id": "sub_xxx"
  }'
```

### Récupérer les factures

```bash
curl "http://localhost:8000/billing/invoice?user_id=user_123"
```

## 🧪 Tests

```bash
# Tests unitaires
pytest tests/

# Tests avec couverture
pytest --cov=app tests/
```

## 📦 Structure du Projet

```
billing/
├── main.py                 # Service FastAPI principal
├── models.py               # Modèles Pydantic
├── plans.py                # Configuration des plans
├── stripe_integration.py   # Intégration Stripe
├── webhook_handlers.py     # Gestionnaires de webhooks
├── requirements.txt        # Dépendances
├── Dockerfile             # Configuration Docker
└── README.md              # Documentation
```

## 🔗 Intégration Stripe

### Configuration du Webhook

1. Aller sur [Stripe Dashboard](https://dashboard.stripe.com/webhooks)
2. Ajouter un endpoint : `https://api.trustdevis.com/billing/webhook`
3. Sélectionner les événements :
   - `checkout.session.completed`
   - `invoice.paid`
   - `invoice.payment_failed`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`

## 📄 Licence

Propriétaire - TrustDevis © 2025
