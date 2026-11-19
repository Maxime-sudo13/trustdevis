# TrustDevis OCR Parser Service

Service d'extraction de texte et de données structurées depuis des PDF et images de devis.

## 📋 Fonctionnalités

- Extraction OCR depuis PDF et images (PNG, JPG, JPEG)
- Détection automatique des lignes de devis
- Extraction structurée : description, quantité, prix unitaire, total
- Scoring de confiance par ligne
- Support des devis bâtiment et mécanique

## 🚀 Démarrage Rapide

### Installation locale

```bash
pip install -r requirements.txt

# Installer Tesseract OCR (Ubuntu/Debian)
sudo apt-get update
sudo apt-get install -y tesseract-ocr tesseract-ocr-fra

# Lancer le service
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Docker

```bash
docker build -t trustdevis-ocr-parser .
docker run -p 8000:8000 trustdevis-ocr-parser
```

## 📡 API Endpoints

### POST `/extract/pdf`

Upload un fichier PDF et extrait le texte structuré.

**Request:**
```bash
curl -X POST "http://localhost:8000/extract/pdf" \
  -F "file=@devis.pdf"
```

**Response:**
```json
{
  "filename": "devis.pdf",
  "raw_text": "DEVIS N°2024-001...",
  "lines": [
    {
      "description": "Pose de carrelage sol",
      "quantity": 45.5,
      "unit_price": 35.0,
      "total": 1592.5,
      "confidence": 0.92
    }
  ]
}
```

### POST `/extract/image`

Upload une image et extrait le texte structuré.

**Request:**
```bash
curl -X POST "http://localhost:8000/extract/image" \
  -F "file=@devis.jpg"
```

**Response:** Identique à `/extract/pdf`

## 🏗️ Architecture

```
ocr-parser/
├── main.py              # Service FastAPI
├── engine.py            # Moteur OCR Tesseract
├── requirements.txt     # Dépendances Python
├── Dockerfile           # Container Docker
├── test_samples/        # Fichiers de test
└── README.md           # Documentation
```

## 🔧 Configuration

Variables d'environnement :
- `TESSDATA_PREFIX` : Chemin vers les données Tesseract
- `OCR_LANG` : Langue OCR (défaut: fra+eng)
- `OCR_DPI` : Résolution pour conversion PDF (défaut: 300)

## 📝 Format des Devis Supportés

### Bâtiment
- Devis travaux (pose, fourniture, main d'œuvre)
- Postes avec quantités en m², ml, u, forfait
- Prix HT et TTC

### Mécanique
- Devis garage (pièces, main d'œuvre)
- Réparations et entretien
- Forfaits et lignes détaillées

## 🧪 Tests

Placer des fichiers de test dans `test_samples/` :
```bash
curl -X POST "http://localhost:8000/extract/pdf" \
  -F "file=@test_samples/devis_batiment.pdf"
```

## 📊 Scoring de Confiance

Le score de confiance (0.0 - 1.0) est calculé selon :
- Qualité de l'OCR (clarté du texte)
- Cohérence des données numériques
- Structure reconnue du devis

## 🔒 Sécurité

- Validation des types de fichiers
- Nettoyage des uploads
- Pas de persistance des fichiers après traitement
