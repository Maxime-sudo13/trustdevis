# Fichiers de test pour l'OCR Parser

Placez ici des échantillons de devis pour tester le service.

## Formats supportés
- PDF (.pdf)
- PNG (.png)
- JPEG (.jpg, .jpeg)
- TIFF (.tiff)
- BMP (.bmp)
- GIF (.gif)

## Types de devis à tester

### Bâtiment
- Devis travaux (électricité, plomberie, maçonnerie...)
- Postes avec quantités (m², ml, u, forfait)
- Prix unitaires et totaux

### Mécanique
- Devis garage (pièces + main d'œuvre)
- Réparations et entretien
- Forfaits

## Commande de test

```bash
curl -X POST "http://localhost:8000/extract/pdf" \
  -F "file=@test_samples/mon_devis.pdf"
```