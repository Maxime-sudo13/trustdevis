# TrustDevis CRM Agent

Agent de gestion clients, relances automatiques et feedback pour la plateforme TrustDevis.

## 🎯 Fonctionnalités

### Gestion Clients
- CRUD complet des clients
- Segmentation par secteur (Bâtiment, Mécanique, Autre)
- Gestion des plans (Essai, Basique, Pro, Entreprise)
- Recherche et filtres avancés

### Gestion des Devis
- Historique des devis par client
- Suivi du statut (en attente, analyse, terminé, erreur)
- Stockage des résultats d'analyse
- Score de confiance

### Relances Automatiques
- **Onboarding** : J+1, J+3, J+7 après inscription
- **Conversion** : J-3 et J-1 avant fin d'essai
- **NPS** : J+30 après inscription
- **Renouvellement** : J-7 et J-1 avant expiration

### Feedback & NPS
- Collecte des scores NPS (0-10)
- Calcul du NPS global
- Commentaires clients
- Statistiques détaillées

### Campagnes
- Création de campagnes personnalisées
- Ciblage par plan, secteur, ancienneté
- Planification des envois

## 🚀 Démarrage

### Local

```bash
# Installation des dépendances
pip install -r requirements.txt

# Démarrage du serveur
uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

### Docker

```bash
# Construction de l'image
docker build -t trustdevis-crm .

# Exécution
docker run -p 8001:8001 -v $(pwd)/data:/app/data trustdevis-crm
```

### Docker Compose

```yaml
version: '3.8'
services:
  crm:
    build: .
    ports:
      - "8001:8001"
    volumes:
      - ./data:/app/data
    environment:
      - DATABASE_URL=sqlite:///./data/crm.db
```

## 📚 API Endpoints

### Clients
| Méthode | Endpoint | Description |
|---------|----------|-------------|
| POST | `/clients` | Créer un client |
| GET | `/clients` | Liste des clients |
| GET | `/clients/{id}` | Détail client |
| PUT | `/clients/{id}` | Modifier client |
| DELETE | `/clients/{id}` | Désactiver client |

### Devis
| Méthode | Endpoint | Description |
|---------|----------|-------------|
| POST | `/devis` | Créer un devis |
| GET | `/devis` | Liste des devis |
| GET | `/clients/{id}/devis` | Devis d'un client |
| PUT | `/devis/{id}` | Mettre à jour résultat |
| DELETE | `/devis/{id}` | Supprimer devis |

### Relances
| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/relances` | Liste des relances |
| GET | `/clients/{id}/relances` | Relances client |
| POST | `/campagnes` | Créer une campagne |

### NPS
| Méthode | Endpoint | Description |
|---------|----------|-------------|
| POST | `/nps` | Enregistrer NPS |
| GET | `/nps` | Liste des NPS |
| GET | `/nps/stats` | Statistiques NPS |

### Stats
| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/stats` | Stats globales |
| GET | `/health` | Health check |

## 📊 Modèles de données

### Client
- `id`: Identifiant unique
- `nom`: Nom du contact
- `email`: Email (unique)
- `tel`: Téléphone
- `entreprise`: Nom entreprise
- `secteur`: bâtiment | mécanique | autre
- `plan`: essai | basique | pro | entreprise
- `date_inscription`: Date d'inscription
- `date_fin_essai`: Fin de période d'essai
- `date_fin_abonnement`: Fin d'abonnement payant
- `actif`: 0 ou 1

### Devis
- `id`: Identifiant unique
- `client_id`: Référence client
- `fichier`: Chemin fichier analysé
- `fichier_origine`: Nom original
- `score`: Score de confiance (0-100)
- `date_upload`: Date upload
- `status`: en_attente | analyse | termine | erreur
- `resultat_analyse`: JSON résultats
- `nb_lignes`: Nombre de lignes
- `montant_total`: Montant total

### Relance
- `id`: Identifiant unique
- `client_id`: Référence client
- `type`: onboarding_j1 | onboarding_j3 | onboarding_j7 | conversion | nps | renouvellement
- `date_planification`: Date planifiée
- `date_envoi`: Date effective d'envoi
- `status`: planifie | envoye | ouvert | clique | erreur
- `sujet`: Sujet email
- `contenu`: Contenu/template utilisé
- `ouvert`: 0 ou 1
- `clique`: 0 ou 1

### NPS
- `id`: Identifiant unique
- `client_id`: Référence client
- `score`: 0-10
- `commentaire`: Texte libre
- `date`: Date de réponse

## 🔧 Configuration

### Variables d'environnement
| Variable | Description | Défaut |
|----------|-------------|--------|
| `DATABASE_URL` | URL de la base de données | `sqlite:///./crm.db` |
| `BASE_URL` | URL base pour les liens | `https://trustdevis.com` |
| `SMTP_HOST` | Serveur SMTP | - |
| `SMTP_PORT` | Port SMTP | 587 |
| `SMTP_USER` | Utilisateur SMTP | - |
| `SMTP_PASS` | Mot de passe SMTP | - |

## 📝 Templates d'emails

Les templates sont définis dans `templates.py` :
- **bienvenue** : Email de bienvenue J+1
- **relance_upload** : Relance pour upload devis
- **resultat_analyse** : Notification résultat prêt
- **nps** : Demande de feedback NPS
- **renouvellement** : Rappel renouvellement
- **conversion_essai** : Conversion essai → payant

## 🕐 Tâches planifiées

Le scheduler démarre automatiquement avec l'application :

| Heure | Tâche |
|-------|-------|
| 09:00 | Relances onboarding |
| 10:00 | Relances conversion |
| 11:00 | Demandes NPS |
| 12:00 | Relances renouvellement |

## 🔍 Exemples d'utilisation

### Créer un client
```bash
curl -X POST "http://localhost:8001/clients" \
  -H "Content-Type: application/json" \
  -d '{
    "nom": "Jean Dupont",
    "email": "jean@example.com",
    "entreprise": "Dupont SARL",
    "secteur": "batiment",
    "plan": "essai"
  }'
```

### Créer un devis
```bash
curl -X POST "http://localhost:8001/devis" \
  -H "Content-Type: application/json" \
  -d '{
    "client_id": 1,
    "fichier": "/uploads/devis_123.pdf"
  }'
```

### Mettre à jour résultat analyse
```bash
curl -X PUT "http://localhost:8001/devis/1" \
  -H "Content-Type: application/json" \
  -d '{
    "score": 85.5,
    "status": "termine",
    "resultat_analyse": "{\"anomalies\": []}",
    "nb_lignes": 12,
    "montant_total": 15400.00
  }'
```

### Enregistrer un NPS
```bash
curl -X POST "http://localhost:8001/nps" \
  -H "Content-Type: application/json" \
  -d '{
    "client_id": 1,
    "score": 9,
    "commentaire": "Excellent service !"
  }'
```

### Créer une campagne
```bash
curl -X POST "http://localhost:8001/campagnes" \
  -H "Content-Type: application/json" \
  -d '{
    "nom": "Promotion été",
    "type": "conversion",
    "date_envoi": "2024-12-25T09:00:00",
    "criteres": {
      "plan": "essai",
      "min_jours_inscription": 7
    }
  }'
```

## 📖 Documentation API

Une fois le service démarré, accédez à :
- Swagger UI : http://localhost:8001/docs
- ReDoc : http://localhost:8001/redoc
- OpenAPI JSON : http://localhost:8001/openapi.json

## 🤝 Intégration

Ce service s'intègre avec :
- **Agent Parser** : Réception des résultats d'analyse
- **Agent Pricing** : Données de comparaison
- **Frontend** : Dashboard client
- **Service Email** : Envoi des relances

## 📄 Licence

Propriétaire - TrustDevis
