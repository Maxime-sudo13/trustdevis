# Artisans Compare Service - TrustDevis

Service de comparaison d'artisans - Concurrence directe Travaux.com

## Fonctionnalités

- Base d'artisans avec profils complets
- Matching intelligent client/artisan
- Comparaison de 3 artisans avec tableau comparatif
- API REST complète
- Intégration landing page

## Endpoints API

- `GET /artisans/search` - Rechercher des artisans
- `GET /artisans/{id}` - Détails d'un artisan
- `POST /artisans/compare` - Comparer 3 artisans
- `GET /artisans/{id}/reviews` - Avis clients d'un artisan

## Lancer le service

```bash
pip install -r requirements.txt
python main.py
```
