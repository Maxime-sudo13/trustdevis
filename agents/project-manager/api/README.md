# API Endpoints - Project Manager

## Base URL
```
http://localhost:3003/api
```

## Projets

### Liste des projets
```
GET /projects
Query params: ?status=planning|in_progress|completed&client_id=xxx
```

### Créer un projet
```
POST /projects
Body: {
  "name": "Nom du projet",
  "address": "Adresse",
  "work_type": "Type de travaux",
  "budget_total": 25000,
  "start_date": "2025-04-01",
  "end_date": "2025-05-15",
  "client_id": "xxx",
  "description": "Description"
}
```

### Détails d'un projet
```
GET /projects/:id
```

### Mettre à jour un projet
```
PUT /projects/:id
Body: { champs à mettre à jour }
```

### Supprimer un projet
```
DELETE /projects/:id
```

### Ajouter un artisan
```
POST /projects/:id/artisans
Body: { "artisan_id": "xxx", "role": "Maître d'œuvre" }
```

### Changer le statut
```
PUT /projects/:id/status
Body: { "status": "in_progress" }
```

## Étapes

### Liste des étapes d'un projet
```
GET /steps/project/:projectId
```

### Créer une étape
```
POST /steps
Body: {
  "project_id": "xxx",
  "name": "Nom de l'étape",
  "description": "Description",
  "planned_start_date": "2025-04-01",
  "planned_end_date": "2025-04-15",
  "order_index": 0
}
```

### Démarrer une étape
```
POST /steps/:id/start
```

### Terminer une étape
```
POST /steps/:id/complete
```

### Valider une étape (client)
```
POST /steps/:id/validate
```

## Finances

### Transactions d'un projet
```
GET /finances/project/:projectId
```

### Résumé financier
```
GET /finances/project/:projectId/summary
```

### Acomptes versés
```
GET /finances/project/:projectId/deposits
```

### Créer une transaction
```
POST /finances
Body: {
  "project_id": "xxx",
  "type": "deposit|expense|estimate|progress_payment|final_payment",
  "amount": 5000,
  "description": "Acompte",
  "date": "2025-04-01",
  "artisan_id": "xxx"
}
```

## Documents

### Liste des documents
```
GET /documents/project/:projectId?type=contract
```

### Upload un document
```
POST /documents/upload
Content-Type: multipart/form-data
Body: {
  "file": <fichier>,
  "project_id": "xxx",
  "type": "contract|invoice|insurance|photo|plan|permit|final_dossier",
  "artisan_id": "xxx"
}
```

### Vérifier documents requis
```
GET /documents/project/:projectId/required
```

### Générer dossier final
```
GET /documents/project/:projectId/dossier
```

## Alertes

### Toutes les alertes actives
```
GET /alerts
```

### Alertes d'un projet
```
GET /alerts/project/:projectId?unread=true&unresolved=true
```

### Marquer comme lue
```
PUT /alerts/:id/read
```

### Résoudre une alerte
```
PUT /alerts/:id/resolve
```

## Dashboard

### Dashboard global
```
GET /dashboard
```

### Dashboard projet
```
GET /dashboard/project/:projectId
```

### Calendrier
```
GET /dashboard/calendar?start=2025-04-01&end=2025-05-31
```

### Projets nécessitant attention
```
GET /dashboard/attention
```

## Health Check
```
GET /health
```
