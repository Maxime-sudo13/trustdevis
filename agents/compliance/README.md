# 🤖 TrustDevis Compliance Agent

Service de gestion de la conformité RGPD et protection des données personnelles pour la plateforme TrustDevis.

## 📋 Description

Ce service gère :
- Les **consentements utilisateurs** (collecte, révocation, vérification)
- L'**export des données** (droit à la portabilité)
- La **suppression des données** (droit à l'oubli)
- Le **registre des traitements** (conformité CNIL)
- Les **logs d'audit** (traçabilité)

## 🚀 Démarrage rapide

### Local

```bash
# Installation des dépendances
pip install -r requirements.txt

# Lancement du service
python main.py

# Ou avec uvicorn directement
uvicorn main:app --host 0.0.0.0 --port 8003 --reload
```

### Docker

```bash
# Construction de l'image
docker build -t trustdevis-compliance .

# Exécution
docker run -p 8003:8003 trustdevis-compliance
```

### Docker Compose

```yaml
version: '3.8'
services:
  compliance:
    build: .
    ports:
      - "8003:8003"
    environment:
      - ENVIRONMENT=production
    restart: unless-stopped
```

## 📚 API Endpoints

### Santé

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/health` | Vérification de santé |
| GET | `/` | Page d'accueil |

### Consentements

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| POST | `/consent/log` | Enregistrer un consentement |
| POST | `/consent/revoke` | Révoquer un consentement |
| GET | `/consent/{user_id}` | Lister les consentements |
| GET | `/consent/{user_id}/check/{type}` | Vérifier un consentement |

### RGPD

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| POST | `/gdpr/export` | Exporter les données (portabilité) |
| POST | `/gdpr/delete` | Supprimer/anonymiser (oubli) |
| GET | `/gdpr/register` | Registre des traitements |
| GET | `/gdpr/register/{id}` | Détails d'un traitement |
| GET | `/gdpr/retention/{user_id}` | Infos de conservation |

### Admin

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/admin/logs` | Logs d'accès |
| POST | `/admin/treatments` | Ajouter un traitement |

## 📖 Exemples d'utilisation

### Enregistrer un consentement

```bash
curl -X POST http://localhost:8003/consent/log \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_123",
    "type": "terms_of_service",
    "version": "v1.0"
  }'
```

### Vérifier les consentements

```bash
curl http://localhost:8003/consent/user_123
```

### Exporter les données (RGPD)

```bash
curl -X POST http://localhost:8003/gdpr/export \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_123"
  }'
```

### Demander la suppression

```bash
curl -X POST http://localhost:8003/gdpr/delete \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_123",
    "reason": "Demande utilisateur"
  }'
```

### Consulter le registre des traitements

```bash
curl http://localhost:8003/gdpr/register
```

## 🔒 Types de consentements

- `terms_of_service` - Conditions d'utilisation
- `marketing` - Communications marketing
- `analytics` - Cookies d'analyse
- `third_party_sharing` - Partage avec des tiers
- `cookies` - Cookies essentiels

## 📁 Structure du projet

```
compliance/
├── main.py              # Application FastAPI
├── models.py            # Modèles Pydantic
├── gdpr_core.py         # Logique métier RGPD
├── middleware.py        # Middlewares de sécurité
├── register.md          # Registre des traitements CNIL
├── requirements.txt     # Dépendances Python
├── Dockerfile           # Image Docker
└── README.md            # Ce fichier
```

## 🔐 Sécurité

- Headers de sécurité (CSP, HSTS, X-Frame-Options)
- Rate limiting (100 req/min par défaut)
- CORS configuré
- Logs d'audit complets
- Validation des entrées

## 📝 Conformité RGPD

Ce service implémente :
- ✅ Consentement explicite et traçable
- ✅ Droit à la portabilité (export JSON)
- ✅ Droit à l'oubli (suppression/anonymisation)
- ✅ Registre des traitements (art. 30)
- ✅ Logs d'audit (traçabilité)
- ✅ Minimisation des données
- ✅ Limitation de conservation

## 🛠️ Développement

```bash
# Mode développement avec reload
uvicorn main:app --reload --port 8003

# Tests
pytest tests/

# Formatagelack .
isort .
```

## 📞 Contact DPO

Pour toute question relative à la protection des données :
- Email : dpo@trustdevis.fr

## 📄 Licence

Propriétaire - TrustDevis

---

*Dernière mise à jour : Mars 2024*
