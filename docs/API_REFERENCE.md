# TrustDevis - Référence API

> Version 1.0 | 9 Mars 2026 | Agent Architecte

---

## Base URL

```
Production:  https://api.trustdevis.com/v1
Staging:     https://staging-api.trustdevis.com/v1
Local:       http://localhost:3001/v1
```

---

## Authentification

### JWT Bearer Token

Toutes les routes protégées nécessitent un token JWT dans le header:

```http
Authorization: Bearer {access_token}
```

### Obtenir un Token

#### POST /auth/login

**Request:**
```json
{
  "email": "max@example.com",
  "password": "motdepasse123"
}
```

**Response 200:**
```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "dGhpcyBpcyBhIHJlZnJlc2ggdG9rZW4...",
    "expires_in": 3600,
    "token_type": "Bearer",
    "user": {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "email": "max@example.com",
      "nom": "Ime",
      "prenom": "Max",
      "role": "user"
    }
  }
}
```

**Response 401:**
```json
{
  "success": false,
  "error": {
    "code": "INVALID_CREDENTIALS",
    "message": "Email ou mot de passe incorrect"
  }
}
```

---

#### POST /auth/register

**Request:**
```json
{
  "email": "max@example.com",
  "password": "motdepasse123",
  "nom": "Ime",
  "prenom": "Max",
  "telephone": "+33612345678"
}
```

**Response 201:**
```json
{
  "success": true,
  "data": {
    "user": {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "email": "max@example.com",
      "nom": "Ime",
      "prenom": "Max",
      "role": "user",
      "created_at": "2026-03-09T00:00:00Z"
    },
    "message": "Compte créé. Veuillez vérifier votre email."
  }
}
```

---

#### POST /auth/refresh

**Request:**
```json
{
  "refresh_token": "dGhpcyBpcyBhIHJlZnJlc2ggdG9rZW4..."
}
```

**Response 200:**
```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
    "expires_in": 3600
  }
}
```

---

#### POST /auth/logout

**Request:**
```http
Authorization: Bearer {access_token}
```

**Response 200:**
```json
{
  "success": true,
  "message": "Déconnexion réussie"
}
```

---

#### POST /auth/forgot-password

**Request:**
```json
{
  "email": "max@example.com"
}
```

**Response 200:**
```json
{
  "success": true,
  "message": "Si cet email existe, un lien de réinitialisation a été envoyé"
}
```

---

## Devis

### Upload et Traitement

#### POST /devis/upload

Upload un fichier devis pour analyse.

**Headers:**
```http
Authorization: Bearer {access_token}
Content-Type: multipart/form-data
```

**Request:**
```
file: [Fichier PDF/Image]
secteur: "batiment" (optionnel)
```

**Response 202 (Accepted):**
```json
{
  "success": true,
  "data": {
    "devis_id": "550e8400-e29b-41d4-a716-446655440001",
    "status": "processing",
    "message": "Devis en cours d'analyse",
    "estimated_time": "30s",
    "check_url": "/v1/devis/550e8400-e29b-41d4-a716-446655440001/status"
  }
}
```

**Response 400:**
```json
{
  "success": false,
  "error": {
    "code": "INVALID_FILE",
    "message": "Format de fichier non supporté. Utilisez PDF, JPG ou PNG"
  }
}
```

**Response 413:**
```json
{
  "success": false,
  "error": {
    "code": "FILE_TOO_LARGE",
    "message": "Fichier trop volumineux (max 10MB)"
  }
}
```

---

#### GET /devis/{id}

Récupère les détails d'un devis.

**Headers:**
```http
Authorization: Bearer {access_token}
```

**Response 200:**
```json
{
  "success": true,
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440001",
    "filename": "devis-renovation.pdf",
    "secteur": "batiment",
    "status": "completed",
    "trust_score": 78,
    "risk_level": "low",
    "created_at": "2026-03-09T00:00:00Z",
    "completed_at": "2026-03-09T00:00:30Z",
    "normalized_data": {
      "metadata": {
        "artisan": {
          "nom": "Dupont Construction",
          "siret": "12345678900012",
          "adresse": "12 Rue des Artisans, 75001 Paris"
        },
        "client": {
          "nom": "Max Ime",
          "adresse_chantier": "45 Avenue des Champs, 75008 Paris"
        },
        "devis": {
          "numero": "DEV-2026-001",
          "date": "2026-03-01",
          "validite": "30 jours"
        }
      },
      "prestations": [
        {
          "ligne": 1,
          "description": "Pose de carrelage sol",
          "quantite": 25,
          "unite": "m²",
          "prix_unitaire_ht": 45.50,
          "total_ht": 1137.50,
          "tva": 20
        }
      ],
      "recapitulatif": {
        "total_ht": 5000.00,
        "total_tva": 1000.00,
        "total_ttc": 6000.00
      }
    }
  }
}
```

---

#### GET /devis/{id}/status

Vérifie le statut de traitement d'un devis.

**Response 200:**
```json
{
  "success": true,
  "data": {
    "devis_id": "550e8400-e29b-41d4-a716-446655440001",
    "status": "processing",
    "progress": 60,
    "steps": [
      { "name": "upload", "status": "completed", "duration": "2s" },
      { "name": "ocr", "status": "completed", "duration": "8s" },
      { "name": "normalization", "status": "completed", "duration": "5s" },
      { "name": "pricing", "status": "in_progress", "duration": "10s" },
      { "name": "scoring", "status": "pending" }
    ],
    "estimated_completion": "15s"
  }
}
```

**Statuts possibles:**
- `pending` - En attente de traitement
- `processing` - En cours d'analyse
- `completed` - Analyse terminée
- `error` - Erreur lors du traitement

---

#### GET /devis/{id}/rapport

Récupère le rapport d'analyse complet.

**Response 200:**
```json
{
  "success": true,
  "data": {
    "devis_id": "550e8400-e29b-41d4-a716-446655440001",
    "generated_at": "2026-03-09T00:00:30Z",
    "trust_score": 78,
    "risk_level": "low",
    "summary": {
      "total_prestations": 5,
      "total_materiaux": 3,
      "montant_total": 6000.00,
      "anomalies_count": 1,
      "recommandations_count": 2
    },
    "scores": {
      "price_score": 82,
      "consistency_score": 75,
      "detail_score": 80,
      "source_score": 70
    },
    "benchmarks": [
      {
        "prestation": "Pose de carrelage sol",
        "prix_propose": 45.50,
        "prix_marche_min": 35.00,
        "prix_marche_max": 55.00,
        "prix_marche_avg": 42.00,
        "ecart_percent": 8.3,
        "position": "within"
      }
    ],
    "anomalies": [
      {
        "type": "price_high",
        "severity": "medium",
        "prestation": "Peinture plafond",
        "message": "Prix 15% supérieur à la moyenne du marché",
        "details": "Prix proposé: 38€/m² | Moyenne marché: 32€/m²"
      }
    ],
    "recommandations": [
      {
        "priority": "high",
        "category": "verification",
        "message": "Demandez le détail des quantités de peinture"
      },
      {
        "priority": "medium",
        "category": "comparison",
        "message": "Obtenez un second devis pour la peinture"
      }
    ],
    "rapport_url": "/v1/devis/550e8400-e29b-41d4-a716-446655440001/rapport/pdf",
    "share_url": "https://app.trustdevis.com/rapport/abc123"
  }
}
```

---

#### GET /devis/{id}/rapport/pdf

Télécharge le rapport au format PDF.

**Response:** Fichier PDF (Content-Type: application/pdf)

---

#### GET /devis

Liste les devis de l'utilisateur connecté.

**Query Parameters:**
```
?status=completed    # Filtrer par statut
?secteur=batiment    # Filtrer par secteur
?page=1              # Pagination
?limit=20            # Nombre par page (max 100)
?sort=created_at:desc # Tri
```

**Response 200:**
```json
{
  "success": true,
  "data": {
    "devis": [
      {
        "id": "550e8400-e29b-41d4-a716-446655440001",
        "filename": "devis-renovation.pdf",
        "secteur": "batiment",
        "status": "completed",
        "trust_score": 78,
        "created_at": "2026-03-09T00:00:00Z"
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 20,
      "total": 15,
      "pages": 1
    }
  }
}
```

---

#### DELETE /devis/{id}

Supprime un devis et toutes ses données associées.

**Response 200:**
```json
{
  "success": true,
  "message": "Devis supprimé avec succès"
}
```

---

## Utilisateur

#### GET /user/profile

Récupère le profil de l'utilisateur connecté.

**Response 200:**
```json
{
  "success": true,
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "max@example.com",
    "nom": "Ime",
    "prenom": "Max",
    "telephone": "+33612345678",
    "adresse": {
      "rue": "45 Avenue des Champs",
      "ville": "Paris",
      "code_postal": "75008",
      "pays": "France"
    },
    "role": "user",
    "email_verified": true,
    "created_at": "2026-01-15T10:30:00Z",
    "stats": {
      "total_devis": 15,
      "devis_this_month": 3,
      "average_trust_score": 72
    }
  }
}
```

---

#### PUT /user/profile

Met à jour le profil utilisateur.

**Request:**
```json
{
  "nom": "Ime",
  "prenom": "Maxime",
  "telephone": "+33612345679",
  "adresse": {
    "rue": "46 Avenue des Champs",
    "ville": "Paris",
    "code_postal": "75008",
    "pays": "France"
  }
}
```

**Response 200:**
```json
{
  "success": true,
  "data": {
    "user": {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "email": "max@example.com",
      "nom": "Ime",
      "prenom": "Maxime",
      "updated_at": "2026-03-09T01:00:00Z"
    }
  }
}
```

---

#### PUT /user/password

Change le mot de passe.

**Request:**
```json
{
  "current_password": "ancien_mdp",
  "new_password": "nouveau_mdp123"
}
```

---

#### DELETE /user/account

Supprime le compte utilisateur et toutes les données (RGPD).

**Request:**
```json
{
  "password": "motdepasse123",
  "confirm": true
}
```

---

## Statistiques

#### GET /stats/dashboard

Récupère les statistiques pour le dashboard.

**Response 200:**
```json
{
  "success": true,
  "data": {
    "overview": {
      "total_devis": 15,
      "devis_this_month": 3,
      "average_trust_score": 72,
      "anomalies_detected": 8
    },
    "trust_score_trend": [
      { "month": "2026-01", "score": 68 },
      { "month": "2026-02", "score": 72 },
      { "month": "2026-03", "score": 75 }
    ],
    "secteurs": [
      { "secteur": "batiment", "count": 10 },
      { "secteur": "mecanique", "count": 5 }
    ],
    "recent_activity": [
      {
        "type": "devis_analyzed",
        "devis_id": "...",
        "trust_score": 78,
        "created_at": "2026-03-09T00:00:00Z"
      }
    ]
  }
}
```

---

## Feedback

#### POST /feedback/price

Signale une erreur sur un prix de référence.

**Request:**
```json
{
  "benchmark_id": "550e8400-e29b-41d4-a716-446655440002",
  "type": "price_too_low",
  "comment": "Dans ma région, ce prix est plutôt autour de 50€",
  "suggested_price": 50.00
}
```

---

#### POST /feedback/rapport

Donne un feedback sur un rapport généré.

**Request:**
```json
{
  "devis_id": "550e8400-e29b-41d4-a716-446655440001",
  "rating": 4,
  "comment": "Très utile, mais aurait pu détecter l'anomalie sur la main d'œuvre",
  "helpful": true
}
```

---

## Endpoints Agents Internes

> Ces endpoints sont réservés à la communication inter-services

### Agent OCR (Port 3002)

#### POST /ocr/extract

**Request:**
```json
{
  "file_url": "https://storage.trustdevis.com/devis/abc.pdf",
  "file_type": "pdf"
}
```

**Response 200:**
```json
{
  "success": true,
  "data": {
    "raw_text": "Texte extrait du document...",
    "tables": [
      {
        "headers": ["Description", "Qté", "Prix"],
        "rows": [["...", "10", "450"]]
      }
    ],
    "confidence_score": 0.92,
    "processing_time": "8.5s"
  }
}
```

---

### Agent Normalizer (Port 3003)

#### POST /normalize

**Request:**
```json
{
  "raw_text": "Texte OCR...",
  "tables": [...],
  "secteur_hint": "batiment"
}
```

**Response 200:**
```json
{
  "success": true,
  "data": {
    "version": "1.0",
    "secteur": "batiment",
    "confidence": 0.88,
    "metadata": { ... },
    "prestations": [ ... ],
    "recapitulatif": { ... }
  }
}
```

---

### Agent Pricing (Port 3004)

#### POST /pricing/analyze

**Request:**
```json
{
  "devis_id": "550e8400-e29b-41d4-a716-446655440001",
  "prestations": [...],
  "localisation": {
    "code_postal": "75008",
    "ville": "Paris"
  }
}
```

**Response 200:**
```json
{
  "success": true,
  "data": {
    "benchmarks": [...],
    "market_position": "within",
    "anomalies": [...]
  }
}
```

---

### Agent MarketScore (Port 3005)

#### POST /score/calculate

**Request:**
```json
{
  "devis_id": "550e8400-e29b-41d4-a716-446655440001",
  "normalized_data": {...},
  "benchmarks": [...]
}
```

**Response 200:**
```json
{
  "success": true,
  "data": {
    "trust_score": 78,
    "risk_level": "low",
    "scores": {...},
    "recommendations": [...]
  }
}
```

---

## Codes d'Erreur

### Erreurs Générales (4xx)

| Code | HTTP | Description |
|------|------|-------------|
| `BAD_REQUEST` | 400 | Requête mal formée |
| `UNAUTHORIZED` | 401 | Token manquant ou invalide |
| `FORBIDDEN` | 403 | Accès interdit (permissions) |
| `NOT_FOUND` | 404 | Ressource non trouvée |
| `CONFLICT` | 409 | Conflit (ex: email déjà utilisé) |
| `UNPROCESSABLE` | 422 | Validation échouée |
| `RATE_LIMITED` | 429 | Trop de requêtes |

### Erreurs Spécifiques (4xx)

| Code | HTTP | Description |
|------|------|-------------|
| `INVALID_CREDENTIALS` | 401 | Email/mot de passe incorrect |
| `TOKEN_EXPIRED` | 401 | Token JWT expiré |
| `INVALID_FILE` | 400 | Format de fichier non supporté |
| `FILE_TOO_LARGE` | 413 | Fichier > 10MB |
| `INVALID_FILE_TYPE` | 400 | Type MIME non accepté |
| `PROCESSING_ERROR` | 422 | Erreur lors du traitement |
| `QUOTA_EXCEEDED` | 429 | Limite de devis atteinte |

### Erreurs Serveur (5xx)

| Code | HTTP | Description |
|------|------|-------------|
| `INTERNAL_ERROR` | 500 | Erreur interne |
| `SERVICE_UNAVAILABLE` | 503 | Service temporairement indisponible |
| `GATEWAY_TIMEOUT` | 504 | Délai d'attente dépassé |

---

## Rate Limiting

### Limites par Endpoint

| Endpoint | Limite | Fenêtre |
|----------|--------|---------|
| POST /auth/login | 5 | 1 minute |
| POST /auth/register | 3 | 1 heure |
| POST /devis/upload | 10 | 1 heure |
| GET /devis | 100 | 1 minute |
| Tous autres | 1000 | 1 minute |

### Headers de Réponse

```http
X-RateLimit-Limit: 10
X-RateLimit-Remaining: 8
X-RateLimit-Reset: 1646784000
```

---

## Pagination

### Paramètres

```
?page=1&limit=20
```

### Réponse Paginée

```json
{
  "data": [...],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 150,
    "pages": 8,
    "has_next": true,
    "has_prev": false
  },
  "links": {
    "self": "/v1/devis?page=1&limit=20",
    "next": "/v1/devis?page=2&limit=20",
    "prev": null,
    "first": "/v1/devis?page=1&limit=20",
    "last": "/v1/devis?page=8&limit=20"
  }
}
```

---

## Webhooks (Futur)

### Configuration

```json
{
  "url": "https://client.com/webhooks/trustdevis",
  "events": ["devis.completed", "devis.error"],
  "secret": "whsec_..."
}
```

### Événements

| Événement | Description |
|-----------|-------------|
| `devis.created` | Devis uploadé |
| `devis.processing` | Traitement démarré |
| `devis.completed` | Analyse terminée |
| `devis.error` | Erreur de traitement |
| `rapport.generated` | Rapport généré |

### Payload

```json
{
  "event": "devis.completed",
  "timestamp": "2026-03-09T00:00:30Z",
  "data": {
    "devis_id": "550e8400-e29b-41d4-a716-446655440001",
    "trust_score": 78,
    "rapport_url": "https://api.trustdevis.com/v1/devis/.../rapport"
  }
}
```

---

## SDK et Exemples

### cURL

```bash
# Login
curl -X POST https://api.trustdevis.com/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"max@example.com","password":"xxx"}'

# Upload devis
curl -X POST https://api.trustdevis.com/v1/devis/upload \
  -H "Authorization: Bearer {token}" \
  -F "file=@devis.pdf" \
  -F "secteur=batiment"

# Récupérer rapport
curl https://api.trustdevis.com/v1/devis/{id}/rapport \
  -H "Authorization: Bearer {token}"
```

### JavaScript/TypeScript

```typescript
const trustdevis = new TrustDevisClient({
  apiKey: 'your_api_key'
});

// Upload
const devis = await trustdevis.devis.upload({
  file: fileInput.files[0],
  secteur: 'batiment'
});

// Poll status
const rapport = await trustdevis.devis.waitForAnalysis(devis.id);
console.log(rapport.trust_score);
```

### Python

```python
from trustdevis import Client

client = Client(api_key="your_api_key")

# Upload
devis = client.devis.upload(
    file_path="devis.pdf",
    secteur="batiment"
)

# Get rapport
rapport = client.devis.get_rapport(devis.id)
print(f"Trust Score: {rapport.trust_score}")
```

---

## Changelog

### v1.0.0 (2026-03-09)
- Release initiale
- Endpoints auth, devis, user
- Intégration agents OCR, Normalizer, Pricing, MarketScore
