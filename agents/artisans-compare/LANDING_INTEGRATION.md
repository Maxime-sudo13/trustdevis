# Artisans Compare - Intégration Landing Page

## Section "Trouver un artisan de confiance"

```html
<section class="artisans-section">
  <h2>Trouver un artisan de confiance</h2>
  <p>Comparez les artisans vérifiés par TrustDevis</p>
  
  <div id="artisans-recommended"></div>
  
  <a href="/artisans" class="cta-button">
    Voir tous les artisans
  </a>
</section>

<script>
// Charger les artisans recommandés
fetch('/api/artisans/landing/recommended')
  .then(r => r.json())
  .then(data => {
    renderArtisans(data.artisans);
  });
</script>
```

## Après analyse de devis

```html
<section class="artisans-after-analysis">
  <h2>Artisans recommandés pour votre projet</h2>
  <p>Basé sur votre devis analysé</p>
  
  <div id="matching-artisans"></div>
  
  <button onclick="compareSelected()">
    Comparer ces artisans
  </button>
</section>

<script>
// Après analyse du devis quote_123
fetch(`/api/artisans/landing/after-analysis?quote_id=${quoteId}&project_type=${type}&detected_price=${price}`)
  .then(r => r.json())
  .then(data => {
    renderMatchingArtisans(data.artisans);
  });
</script>
```

## Widget de comparaison

```html
<div class="artisan-compare-widget">
  <h3>Comparez jusqu'à 3 artisans</h3>
  
  <div class="artisan-selector">
    <select id="artisan1"></select>
    <select id="artisan2"></select>
    <select id="artisan3"></select>
  </div>
  
  <button onclick="launchComparison()">Comparer</button>
  
  <div id="comparison-results"></div>
</div>
```

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /artisans/search` | Rechercher des artisans |
| `GET /artisans/{id}` | Détails d'un artisan |
| `POST /artisans/compare` | Comparer 2-3 artisans |
| `GET /artisans/{id}/reviews` | Avis clients |
| `POST /artisans/match` | Matching intelligent |
| `GET /specialties` | Liste des spécialités |
| `GET /badges` | Info badges |
