# Issues GitHub - MVP TrustDevis

Ce document contient toutes les issues du MVP prêtes à être créées dans GitHub. Chaque issue est formatée selon les standards professionnels avec titre, labels, story points, description, critères d'acceptation et tâches techniques.

---

## [MVP-001] Repo skeleton + CI pipeline

**Labels:** `infra`, `setup`  
**Story Points:** 3  
**Priority:** P0 - Blocker

### Description
Création de la structure initiale du repository TrustDevis et mise en place de la pipeline CI/CD avec GitHub Actions. Cette issue est fondatrice et bloque toutes les autres.

### Critères d'acceptation
- [ ] Repository GitHub créé avec structure claire (frontend/, backend/, docs/)
- [ ] GitHub Actions configuré pour CI (lint, test, build)
- [ ] Templates de Pull Request créés
- [ ] Templates d'issues créés (bug, feature, task)
- [ ] Branch protection rules configurées (main branch)
- [ ] README.md initial avec setup instructions
- [ ] LICENSE file (à définir avec le fondateur)

### Tâches techniques
1. **Structure repo**
   - Créer les dossiers : `frontend/`, `backend/`, `docs/`, `.github/`
   - Ajouter `.gitignore` adapté (Node, Python, IDE)

2. **CI Pipeline**
   - Workflow `ci.yml` : lint, test, build sur PR
   - Workflow `deploy-staging.yml` : auto-deploy sur merge
   - Caching des dépendances pour optimisation

3. **Templates**
   - `.github/pull_request_template.md`
   - `.github/ISSUE_TEMPLATE/bug_report.md`
   - `.github/ISSUE_TEMPLATE/feature_request.md`
   - `.github/ISSUE_TEMPLATE/task.md`

---

## [MVP-002] Upload UI + checkbox consentement RGPD

**Labels:** `frontend`, `rgpd`  
**Story Points:** 5  
**Priority:** P0 - Core Feature

### Description
Développement de la page d'upload de devis avec une checkbox de consentement RGPD explicite et obligatoire. Interface simple et intuitive pour les utilisateurs finaux.

### Critères d'acceptation
- [ ] Page upload responsive (mobile-first)
- [ ] Drag & drop fonctionnel pour fichiers PDF/images
- [ ] Checkbox consentement RGPD obligatoire (bloquante)
   - [ ] Texte de consentement clair et explicite
   - [ ] Lien vers politique de confidentialité
   - [ ] Timestamp du consentement enregistré
- [ ] Validation des formats (PDF, JPG, PNG, max 10MB)
- [ ] Feedback visuel pendant l'upload (progress bar)
- [ ] Messages d'erreur explicites
- [ ] Accessibilité (ARIA labels, contrastes)

### Tâches techniques
1. **Composants UI**
   - Composant `FileUploader` avec drag & drop
   - Composant `ConsentCheckbox` avec validation
   - Composant `UploadProgress` pour feedback

2. **Validation**
   - Validation côté client (type, taille)
   - Validation côté serveur (sécurité)
   - Stockage du timestamp consentement

3. **RGPD Compliance**
   - Texte de consentement rédigé (validation légale requise)
   - Politique de confidentialité (lien placeholder pour MVP)
   - Log du consentement (user_id, timestamp, ip_hash)

---

## [OCR-001] Pipeline OCR extraction lignes devis

**Labels:** `backend`, `ocr`, `ai`  
**Story Points:** 8  
**Priority:** P0 - Core Feature

### Description
Implémentation du pipeline OCR pour extraire le texte des devis PDF/images et parser les lignes en données structurées. C'est le cœur du traitement des documents.

### Critères d'acceptation
- [ ] Intégration Tesseract.js (frontend) ou Tesseract OCR (backend)
- [ ] Support PDF multi-pages
- [ ] Extraction texte brut avec confiance score
- [ ] Parsing des lignes de devis structuré :
   - [ ] Désignation/prestation
   - [ ] Quantité
   - [ ] Unité
   - [ ] Prix unitaire HT
   - [ ] Prix total HT
- [ ] Gestion des cas dégradés (OCR faible qualité)
- [ ] API endpoint `/api/ocr/extract` fonctionnel
- [ ] Tests unitaires sur échantillon de devis

### Tâches techniques
1. **Setup OCR**
   - Installation Tesseract + langpack FR
   - Configuration preprocessing images (contraste, resize)

2. **Extraction**
   - Convertir PDF → images (si nécessaire)
   - OCR avec Tesseract (lang=fr)
   - Récupération texte + confidence scores

3. **Parsing intelligent**
   - Regex pour identifier lignes de tableau
   - Extraction champs : désignation, qté, unité, PU, total
   - Gestion des variations de format (espaces, symboles)

4. **API**
   - Endpoint POST `/api/ocr/extract`
   - Input: fichier (multipart) ou URL
   - Output: JSON structuré avec lignes extraites

---

## [NORM-001] Normalizer bâtiment + mécanique

**Labels:** `backend`, `ai`  
**Story Points:** 5  
**Priority:** P1 - Important

### Description
Système de normalisation pour classifier automatiquement les prestations extraites par OCR dans les catégories bâtiment et mécanique, avec mapping des unités standardisées.

### Critères d'acceptation
- [ ] Classification automatique des prestations :
   - [ ] Catégories bâtiment (maçonnerie, plomberie, électricité, etc.)
   - [ ] Catégories mécanique (moteur, freins, carrosserie, etc.)
- [ ] Mapping unités vers standard (m², m, u, h, forfait, etc.)
- [ ] Désignations normalisées (suppression variations, fautes)
- [ ] API endpoint `/api/normalize` fonctionnel
- [ ] Fallback "non classé" pour prestations inconnues
- [ ] Logs pour amélioration continue du modèle

### Tâches techniques
1. **Classification**
   - Dictionnaire de mots-clés par catégorie
   - Algorithme de matching fuzzy (Levenshtein, etc.)
   - Scoring de confiance par classification

2. **Normalisation unités**
   - Mapping : m²/m2/m² → m², ml/mlin → m, etc.
   - Normalisation forfait/f/forf → forfait
   - Détection automatique si unité manquante

3. **API**
   - Endpoint POST `/api/normalize`
   - Input: lignes OCR brutes
   - Output: lignes normalisées avec catégories

---

## [PRICING-001] Base de données prix régionaux + endpoint

**Labels:** `backend`, `data`  
**Story Points:** 5  
**Priority:** P1 - Important

### Description
Création de la base de données de prix de référence régionaux pour le bâtiment et la mécanique, avec API endpoint pour récupérer les prix selon la localisation et la prestation.

### Critères d'acceptation
- [ ] Schéma DB pour prix régionaux :
   - [ ] Table `prestations` (id, catégorie, désignation normalisée)
   - [ ] Table `prix_regionaux` (prestation_id, region, prix_min, prix_max, prix_median, source, date_maj)
   - [ ] Table `regions` (code, nom, départements)
- [ ] Seed data initiale :
   - [ ] 50+ prestations bâtiment
   - [ ] 30+ prestations mécanique
   - [ ] Prix pour région Île-de-France (référence)
- [ ] API endpoint `/api/pricing` fonctionnel
- [ ] Endpoint filtrable par prestation et région

### Tâches techniques
1. **Database Schema**
   - Migration création tables
   - Index sur (prestation_id, region) pour perfs
   - Contraintes d'intégrité

2. **Seed Data**
   - Recherche sources prix (BTP, garages)
   - Format CSV/JSON pour import
   - Script d'import initial

3. **API**
   - GET `/api/pricing?prestation={id}&region={code}`
   - GET `/api/pricing/search?q={terme}` (recherche fuzzy)
   - Response: prix_min, prix_max, prix_median, confiance

---

## [SCORE-001] MarketScore MVP règles + LLM

**Labels:** `backend`, `ai`, `core`  
**Story Points:** 8  
**Priority:** P0 - Core Feature

### Description
Implémentation de l'algorithme MarketScore MVP combinant règles métier et LLM (Kimi K2) pour évaluer la cohérence des prix d'un devis par rapport au marché.

### Critères d'acceptation
- [ ] Algorithme scoring règles :
   - [ ] Comparaison prix vs fourchette régionale
   - [ ] Détection écarts significatifs (>20% hors fourchette)
   - [ ] Scoring global (0-100) et par ligne
- [ ] Intégration Kimi K2 API :
   - [ ] Prompt optimisé pour analyse de devis
   - [ ] Format JSON output structuré
   - [ ] Gestion erreurs et timeout
- [ ] API endpoint `/api/score` fonctionnel
- [ ] Explication du score (pourquoi ce score ?)
- [ ] Flag "low confidence" pour révision humaine

### Tâches techniques
1. **Algorithme règles**
   - Règles métier de scoring
   - Pondération par catégorie
   - Détection anomalies (prix négatifs, quantités aberrantes)

2. **Intégration LLM**
   - Client API Kimi K2
   - Prompt engineering pour analyse devis
   - Parsing réponse JSON
   - Cache des appels LLM (mêmes devis)

3. **API**
   - POST `/api/score`
   - Input: devis normalisé + région
   - Output: score global, scores par ligne, explications, flags

4. **Output format**
   ```json
   {
     "score_global": 78,
     "niveau": "acceptable",
     "lignes": [...],
     "explications": [...],
     "flags": ["low_confidence"]
   }
   ```

---

## [PILOT-ONB-001] Page onboarding pilotes + contrat

**Labels:** `frontend`, `legal`  
**Story Points:** 3  
**Priority:** P1 - Important

### Description
Création de la page d'onboarding pour les utilisateurs pilotes avec formulaire d'inscription et page de contrat de participation au programme pilote.

### Critères d'acceptation
- [ ] Formulaire inscription pilote :
   - [ ] Nom, prénom, email, téléphone
   - [ ] Type d'activité (artisan bâtiment / garagiste / autre)
   - [ ] Zone géographique (région/département)
   - [ ] Volume estimé de devis/mois
- [ ] Page contrat pilote :
   - [ ] Conditions de participation
   - [ ] Engagement de feedback
   - [ ] Gratuité pendant la phase pilote
   - [ ] Checkbox acceptation contrat
- [ ] Email de confirmation d'inscription
- [ ] Stockage des données pilote en DB

### Tâches techniques
1. **Formulaire**
   - Validation champs (email, téléphone)
   - Champs conditionnels selon type activité
   - UX mobile optimisée

2. **Contrat**
   - Template contrat (validation légale requise)
   - Checkbox acceptation avec timestamp
   - Génération PDF contrat signé (optionnel MVP)

3. **Backend**
   - Table `pilotes` (profil, date_inscription, statut)
   - Endpoint `/api/pilotes/register`
   - Envoi email confirmation

---

## [WIDGET-001] Widget public "Vérifier un devis"

**Labels:** `frontend`, `widget`  
**Story Points:** 5  
**Priority:** P2 - Nice to have

### Description
Développement d'un widget embeddable "Vérifier un devis" permettant aux sites tiers d'intégrer la fonctionnalité TrustDevis via iframe ou script.

### Critères d'acceptation
- [ ] Widget autonome et léger (< 200KB)
- [ ] Mode embeddable (script JS)
   - [ ] `data-api-key` pour tracking origine
   - [ ] `data-theme` (light/dark)
   - [ ] `data-lang` (fr)
- [ ] Mode iframe
   - [ ] URL dédiée `/widget?key={api_key}`
   - [ ] Paramètres de personnalisation
- [ ] Responsive (s'adapte au container parent)
- [ ] Branding TrustDevis discret
- [ ] CTA vers TrustDevis pour analyse complète
- [ ] Documentation d'intégration

### Tâches techniques
1. **Architecture**
   - Build séparé du widget
   - Vanilla JS (pas de framework lourd)
   - CSS scoped pour éviter conflits

2. **Script embed**
   - `trustdevis-widget.js` à inclure
   - Création iframe invisible ou composant inline
   - Communication postMessage si besoin

3. **Iframe mode**
   - Route `/widget` dans l'app principale
   - Query params pour configuration
   - X-Frame-Options pour domains autorisés

4. **Analytics**
   - Tracking utilisation par partenaire
   - Conversion vers app complète

---

## [HUMAN-001] Interface révision humaine

**Labels:** `frontend`, `backend`  
**Story Points:** 5  
**Priority:** P1 - Important

### Description
Développement de l'interface de révision humaine pour les cas "low confidence" (OCR douteux, scoring incertain, prestations non reconnues).

### Critères d'acceptation
- [ ] Queue des cas à réviser :
   - [ ] Liste filtrable (par type, date, priorité)
   - [ ] Indicateurs visuels de confiance
   - [ ] Temps estimé de révision
- [ ] Interface de révision :
   - [ ] Visualisation du document original
   - [ ] Édition des données OCR extraites
   - [ ] Correction catégories et prix
   - [ ] Re-calcul du score en temps réel
- [ ] Actions possibles :
   - [ ] Valider et envoyer résultat
   - [ ] Rejeter (document illisible)
   - [ ] Demander nouveau document (email user)
- [ ] Historique des révisions par utilisateur

### Tâches techniques
1. **Queue backend**
   - Table `review_queue` (devis_id, statut, priorité, assigned_to)
   - API `/api/review/queue` (liste, filtre, assign)
   - Webhook ou polling pour nouveaux cas

2. **Interface admin**
   - Dashboard révision
   - Split view : document | données éditables
   - Composants édition inline

3. **Workflow**
   - Transition statuts : pending → in_review → validated/rejected
   - Notification email si rejeté
   - Audit trail des modifications

---

## Résumé des Story Points

| Issue | Titre | Points |
|-------|-------|--------|
| MVP-001 | Repo skeleton + CI pipeline | 3 |
| MVP-002 | Upload UI + checkbox consentement RGPD | 5 |
| OCR-001 | Pipeline OCR extraction lignes devis | 8 |
| NORM-001 | Normalizer bâtiment + mécanique | 5 |
| PRICING-001 | Base de données prix régionaux + endpoint | 5 |
| SCORE-001 | MarketScore MVP règles + LLM | 8 |
| PILOT-ONB-001 | Page onboarding pilotes + contrat | 3 |
| WIDGET-001 | Widget public "Vérifier un devis" | 5 |
| HUMAN-001 | Interface révision humaine | 5 |
| **TOTAL** | | **47** |

---

## Notes pour création GitHub

Pour créer ces issues dans GitHub :

1. Créer les labels manquants : `infra`, `setup`, `frontend`, `rgpd`, `backend`, `ocr`, `ai`, `data`, `core`, `legal`, `widget`
2. Créer les milestones si besoin (MVP Sprint 1, Sprint 2, etc.)
3. Copier-coller chaque section dans une nouvelle issue
4. Assigner les story points (utiliser un champ personnalisé ou labels `points:3`, `points:5`, etc.)

---

*Document généré par l'Agent Product TrustDevis*  
*Date : 2026-03-09*
