# Agent Quote Generator - TrustDevis

## Mission
Générateur de devis pour clients sans devis existant.

## Concept
Le client décrit ses travaux → Le système génère 3 devis types d'artisans locaux

## Structure

```
quote-generator/
├── src/
│   ├── __init__.py
│   ├── main.py                 # Point d'entrée FastAPI
│   ├── config.py               # Configuration
│   ├── models/
│   │   ├── __init__.py
│   │   ├── quote.py            # Modèles de données
│   │   └── pricing.py          # Modèles de tarification
│   ├── services/
│   │   ├── __init__.py
│   │   ├── quote_generator.py  # Logique de génération
│   │   ├── pricing_engine.py   # Moteur de calcul des prix
│   │   ├── comparison.py       # Logique de comparaison
│   │   └── email_service.py    # Envoi d'emails
│   ├── data/
│   │   ├── __init__.py
│   │   ├── pricing_database.py # Base de 550+ prix
│   │   └── materials.py        # Base de matériaux
│   └── api/
│       ├── __init__.py
│       └── routes.py           # Endpoints API
├── tests/
├── requirements.txt
├── Dockerfile
└── README.md
```

## API Endpoints

- `POST /quote/generate` - Générer un devis
- `GET /quote/{id}` - Récupérer un devis
- `POST /quote/send-email` - Envoyer par email
- `POST /quote/contact-artisans` - Contacter artisans

## Fonctionnalités

1. **Formulaire intelligent**
   - Type de travaux (plomberie, électricité, peinture, etc.)
   - Surface / dimensions
   - Matériaux souhaités (standard, premium, éco)
   - Localisation (code postal)
   - Urgence (standard, express)
   - Budget indicatif

2. **Génération devis**
   - Algorithme basé sur la base de 550+ prix
   - 3 niveaux : économique, standard, premium
   - Détail main d'œuvre vs matériaux
   - Durée estimée
   - TVA incluse

3. **Comparaison**
   - Tableau comparatif 3 devis
   - Graphique répartition prix
   - Explications des différences
   - Recommandation personnalisée

4. **Call-to-action**
   - "Recevoir ces devis par email"
   - "Être mis en relation avec artisans"
   - "Analyser mon vrai devis" (si déjà reçu)
