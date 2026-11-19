# Agent Quote Generator - TrustDevis

## Démarrage rapide

### Local

```bash
# Installation des dépendances
pip install -r requirements.txt

# Lancement du serveur
uvicorn src.main:app --reload
```

### Docker

```bash
# Build
docker build -t trustdevis-quote-generator .

# Run
docker run -p 8000:8000 trustdevis-quote-generator
```

## API Endpoints

### Générer un devis
```bash
POST /quote/generate

{
  "work_description": {
    "work_type": "plomberie",
    "description": "Remplacement d'un mitigeur de douche qui fuit",
    "postal_code": "75001",
    "urgency": "standard",
    "material_preference": "standard"
  }
}
```

### Récupérer un devis
```bash
GET /quote/{id}
```

### Envoyer par email
```bash
POST /quote/send-email

{
  "quote_id": "abc123",
  "email": "client@example.com"
}
```

### Mise en relation artisans
```bash
POST /quote/contact-artisans

{
  "quote_id": "abc123",
  "contact_name": "Jean Dupont",
  "contact_email": "jean@example.com",
  "contact_phone": "0612345678"
}
```

### Tableau comparatif
```bash
GET /quote/{id}/comparison
```

### Répartition des prix (pour graphiques)
```bash
GET /quote/{id}/distribution
```

## Types de travaux supportés

- plomberie
- electricite
- peinture
- maconnerie
- menuiserie
- chauffage
- platerie
- carrelage
- parquet
- toiture
- isolation
- menuiserie_exterieure
- renovation_complete

## Niveaux de devis

1. **Économique** : Matériaux standards, garantie 1 an
2. **Standard** : Matériaux qualité pro, garantie 2 ans (recommandé)
3. **Premium** : Matériaux haut de gamme, garantie 10 ans
