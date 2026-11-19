# TrustDevis - Checklist Sécurité et RGPD

> Version 1.0 | 9 Mars 2026 | Agent Architecte

---

## Vue d'Ensemble

Ce document établit les standards de sécurité et de conformité RGPD pour TrustDevis. Il doit être suivi lors du développement, du déploiement et de la maintenance de la plateforme.

**Statut de conformité cible:** 100%  
**Dernière révision:** 9 Mars 2026  
**Prochaine révision:** Après chaque mise en production majeure

---

## 🔐 Sécurité Technique

### 1. Chiffrement

#### Données en Transit

| Exigence | Statut | Implémentation |
|----------|--------|----------------|
| TLS 1.2 minimum | ✅ | Nginx configuration |
| TLS 1.3 préféré | ✅ | Nginx configuration |
| HSTS activé | ✅ | Header Strict-Transport-Security |
| Certificats valides | ✅ | Let's Encrypt auto-renewal |
| Redirection HTTP→HTTPS | ✅ | Nginx 301 redirect |

**Configuration Nginx:**
```nginx
ssl_protocols TLSv1.2 TLSv1.3;
ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256;
ssl_prefer_server_ciphers off;
add_header Strict-Transport-Security "max-age=63072000" always;
```

#### Données au Repos

| Exigence | Statut | Implémentation |
|----------|--------|----------------|
| Mots de passe hashés | ✅ | bcrypt (cost: 12) |
| Tokens chiffrés | ✅ | JWT RS256 |
| Base de données | 📝 | PostgreSQL encryption at rest |
| Backups chiffrés | 📝 | GPG encryption avant stockage |
| Fichiers uploads | 📝 | Chiffrement côté serveur |

**Hashage mots de passe:**
```javascript
const bcrypt = require('bcrypt');
const SALT_ROUNDS = 12;

const hashPassword = async (password) => {
    return bcrypt.hash(password, SALT_ROUNDS);
};
```

### 2. Authentification et Autorisation

#### JWT (JSON Web Tokens)

| Exigence | Statut | Notes |
|----------|--------|-------|
| Algorithme RS256 | ✅ | Asymétrique, plus sécurisé |
| Expiration courte | ✅ | 1 heure (access token) |
| Refresh token | ✅ | 7 jours, rotation |
| Stockage sécurisé | ✅ | HttpOnly cookies |
| Validation côté serveur | ✅ | Middleware Express |

**Structure JWT:**
```json
{
  "header": {
    "alg": "RS256",
    "typ": "JWT"
  },
  "payload": {
    "sub": "user_uuid",
    "email": "user@example.com",
    "role": "user",
    "iat": 1646784000,
    "exp": 1646787600
  }
}
```

#### Contrôle d'Accès (RBAC)

| Rôle | Permissions |
|------|-------------|
| `user` | CRUD sur ses propres devis, lecture profil |
| `artisan` | + Statistiques anonymisées, feedback prix |
| `admin` | + Gestion utilisateurs, configuration système |
| `superadmin` | + Accès base de données, logs système |

### 3. Protection Contre les Attaques Courantes

#### OWASP Top 10

| Vulnérabilité | Protection | Statut |
|---------------|------------|--------|
| Injection SQL | Requêtes paramétrées (pg) | ✅ |
| XSS | Échappement output, CSP headers | ✅ |
| CSRF | Tokens CSRF, SameSite cookies | ✅ |
| Broken Auth | JWT sécurisés, rate limiting | ✅ |
| Security Misconfig | Headers sécurité, logs | ✅ |
| Sensitive Data Exposure | Chiffrement, minimisation données | ✅ |
| Broken Access Control | Middleware auth, RBAC | ✅ |
| XXE | Pas de parsing XML externe | N/A |
| Components vulnérables | Dependabot, npm audit | 🔄 |
| Insufficient Logging | Winston, logs structurés | ✅ |

#### Headers de Sécurité

```javascript
// Middleware Express
app.use(helmet({
    contentSecurityPolicy: {
        directives: {
            defaultSrc: ["'self'"],
            styleSrc: ["'self'", "'unsafe-inline'"],
            scriptSrc: ["'self'"],
            imgSrc: ["'self'", "data:", "https:"],
        },
    },
    hsts: {
        maxAge: 31536000,
        includeSubDomains: true,
        preload: true
    }
}));
```

#### Rate Limiting

```javascript
const rateLimit = require('express-rate-limit');

const apiLimiter = rateLimit({
    windowMs: 15 * 60 * 1000, // 15 minutes
    max: 100, // 100 requêtes par fenêtre
    message: {
        error: 'Trop de requêtes, veuillez réessayer plus tard'
    },
    standardHeaders: true,
    legacyHeaders: false,
});

app.use('/api/', apiLimiter);
```

### 4. Sécurité Réseau

#### Firewall (UFW)

```bash
# Ports autorisés
ufw default deny incoming
ufw default allow outgoing
ufw allow ssh      # 22
ufw allow http     # 80
ufw allow https    # 443
ufw enable
```

#### Fail2Ban

```ini
# /etc/fail2ban/jail.local
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 5
backend = systemd

[sshd]
enabled = true
port = ssh
filter = sshd
logpath = /var/log/auth.log

[nginx-limit-req]
enabled = true
filter = nginx-limit-req
action = iptables-multiport[name=ReqLimit, port="http,https", protocol=tcp]
logpath = /var/log/nginx/error.log
```

#### Isolation Réseau Docker

```yaml
# docker-compose.yml
networks:
  trustdevis-network:
    driver: bridge
    internal: false
    
  # Base de données isolée
  db-network:
    driver: bridge
    internal: true  # Pas d'accès externe
```

---

## 📋 Conformité RGPD

### 1. Principes Fondamentaux

| Principe | Implémentation |
|----------|----------------|
| **Licéité** | Consentement explicite lors de l'inscription |
| **Limitation des finalités** | Données utilisées uniquement pour l'analyse de devis |
| **Minimisation** | Collecte uniquement des données nécessaires |
| **Exactitude** | Possibilité de mise à jour par l'utilisateur |
| **Limitation de conservation** | Suppression après 3 ans d'inactivité |
| **Intégrité et confidentialité** | Chiffrement, contrôles d'accès |
| **Rendre de comptes** | Documentation, registre des traitements |

### 2. Données Personnelles Traitées

#### Inventaire des Données

| Donnée | Catégorie | Finalité | Base légale | Conservation |
|--------|-----------|----------|-------------|--------------|
| Email | Identification | Authentification, communications | Consentement | Durée du compte |
| Nom/Prénom | Identification | Personnalisation | Consentement | Durée du compte |
| Téléphone | Contact | Support, alertes | Consentement | Durée du compte |
| Adresse | Localisation | Benchmark prix géolocalisé | Consentement | Durée du compte |
| Documents devis | Professionnelles | Analyse, génération rapport | Exécution contrat | 1 an |
| Données analyses | Professionnelles | Amélioration service | Intérêt légitime | Anonymisées après 1 an |
| Logs techniques | Techniques | Sécurité, debugging | Intérêt légitime | 1 an |
| Cookies | Techniques | Session, préférences | Consentement | Session / 1 an |

### 3. Droits des Personnes

#### Implémentation des Droits

| Droit | Endpoint | Délai | Statut |
|-------|----------|-------|--------|
| **Accès** | `GET /user/profile` + `GET /user/data-export` | 30 jours | ✅ |
| **Rectification** | `PUT /user/profile` | Immédiat | ✅ |
| **Effacement** | `DELETE /user/account` | 30 jours | ✅ |
| **Portabilité** | `GET /user/data-export` (JSON) | 30 jours | ✅ |
| **Opposition** | Paramètres compte / email | Immédiat | ✅ |
| **Limitation** | Contact support | 30 jours | 📝 |

**Export de données (Portabilité):**
```javascript
// GET /user/data-export
{
  "user": {
    "email": "user@example.com",
    "nom": "Doe",
    "prenom": "John",
    "created_at": "2026-01-15T10:30:00Z"
  },
  "devis": [...],
  "analyses": [...],
  "export_date": "2026-03-09T00:00:00Z"
}
```

### 4. Consentement

#### Formulaire d'Inscription

```html
<!-- Checkbox obligatoire -->
<input type="checkbox" id="accept-terms" required>
<label for="accept-terms">
    J'accepte les <a href="/cgv">Conditions Générales</a> 
    et la <a href="/privacy">Politique de Confidentialité</a>
</label>

<!-- Checkbox optionnelle -->
<input type="checkbox" id="newsletter">
<label for="newsletter">
    J'accepte de recevoir des conseils et actualités (optionnel)
</label>
```

#### Preuve de Consentement

```javascript
// Stockage dans la base de données
{
  "user_id": "uuid",
  "consents": [
    {
      "type": "terms",
      "version": "1.0",
      "accepted_at": "2026-03-09T00:00:00Z",
      "ip_address": "xxx.xxx.xxx.xxx",
      "user_agent": "..."
    },
    {
      "type": "newsletter",
      "version": "1.0",
      "accepted_at": "2026-03-09T00:00:00Z",
      "ip_address": "xxx.xxx.xxx.xxx"
    }
  ]
}
```

### 5. Registre des Traitements

#### Fiche de Traitement

```markdown
## Traitement: Analyse de devis TrustDevis

**Responsable:** TrustDevis SAS
**DPO:** [Nom du DPO] - dpo@trustdevis.com
**Finalité:** Permettre aux utilisateurs de vérifier la cohérence des devis reçus

**Catégories de données:**
- Données d'identification (email, nom)
- Données de contact (téléphone, adresse)
- Données professionnelles (devis, analyses)

**Destinataires:**
- Équipe TrustDevis (technique, support)
- Sous-traitants: Hostinger (hébergement), Kimi (API LLM)

**Transferts hors UE:**
- Kimi API: Données traitées via API, stockées en Chine
  - Garanties: Accord de traitement signé, minimisation des données

**Durée de conservation:**
- Compte actif: Durée de la relation contractuelle
- Compte inactif: 3 ans après dernière connexion
- Devis: 1 an après upload
- Logs: 1 an

**Mesures de sécurité:**
- Chiffrement TLS 1.3
- Authentification forte
- Contrôles d'accès
- Audit logs
```

### 6. Violations de Données

#### Procédure de Notification

```
1. DÉTECTION (T0)
   └─> Identification de la violation
   └─> Évaluation de la gravité

2. ÉVALUATION (T0 + 24h)
   └─> Nature des données concernées
   └─> Nombre de personnes affectées
   └─> Risques potentiels

3. DÉCISION (T0 + 48h)
   └─> Notification CNIL requise ? (si risque élevé)
   └─> Notification utilisateurs ?

4. NOTIFICATION (T0 + 72h max si CNIL)
   └─> CNIL via formulaire en ligne
   └─> Utilisateurs concernés par email

5. DOCUMENTATION
   └─> Fiche d'incident
   └─> Mesures correctives
```

#### Template Notification

```markdown
Objet: Incident de sécurité - Vos données personnelles

Cher(e) [Prénom],

Nous vous informons qu'un incident de sécurité a affecté vos données 
personnelles le [date].

**Nature de l'incident:** [brève description]
**Données concernées:** [liste des données]
**Risques potentiels:** [risques identifiés]

**Mesures prises:**
- [Mesure 1]
- [Mesure 2]

**Recommandations:**
- [Action utilisateur 1]
- [Action utilisateur 2]

Pour toute question: dpo@trustdevis.com

TrustDevis
```

---

## 🔍 Audit et Monitoring

### 1. Logs de Sécurité

#### Événements à Logger

| Événement | Niveau | Conservation |
|-----------|--------|--------------|
| Connexion réussie | INFO | 1 an |
| Connexion échouée | WARN | 1 an |
| Déconnexion | INFO | 1 an |
| Changement mot de passe | INFO | 1 an |
| Modification profil | INFO | 1 an |
| Suppression compte | WARN | 3 ans |
| Upload devis | INFO | 1 an |
| Accès admin | INFO | 2 ans |
| Erreur authentification | ERROR | 1 an |
| Tentative accès non autorisé | WARN | 2 ans |

#### Format des Logs

```json
{
  "timestamp": "2026-03-09T00:00:00Z",
  "level": "INFO",
  "event": "user.login",
  "user_id": "uuid",
  "ip_address": "xxx.xxx.xxx.xxx",
  "user_agent": "Mozilla/5.0...",
  "success": true,
  "metadata": {
    "method": "password",
    "mfa_used": false
  }
}
```

### 2. Alertes de Sécurité

#### Déclencheurs

```javascript
const ALERT_RULES = [
    {
        name: 'brute_force',
        condition: 'failed_logins > 5 in 5 minutes',
        action: 'block_ip + notify_admin'
    },
    {
        name: 'unusual_access',
        condition: 'login_from_new_country',
        action: 'require_mfa + notify_user'
    },
    {
        name: 'data_exfiltration',
        condition: 'bulk_download > 100 records',
        action: 'block + notify_admin'
    }
];
```

### 3. Tests de Sécurité

#### Tests Automatisés

```bash
# Tests de dépendances
npm audit

# Tests SAST (Static Analysis)
npx eslint --ext .js . --security

# Tests de configuration
npx helmet-csp-check

# Tests de vulnérabilités
npx snyk test
```

#### Tests Manuels (Trimestriel)

- [ ] Pentest externe
- [ ] Review code sécurité
- [ ] Test recovery DRP
- [ ] Vérification backups
- [ ] Audit accès admin

---

## 📜 Documents Légaux Requis

### 1. Mentions Légales

À inclure sur le site:
- Éditeur du site (TrustDevis SAS)
- Adresse siège social
- Numéro SIRET
- Directeur de publication
- Hébergeur (Hostinger)
- Contact

### 2. Politique de Confidentialité

Sections obligatoires:
1. Qui sommes-nous ?
2. Quelles données collectons-nous ?
3. Pourquoi les collectons-nous ?
4. Qui y a accès ?
5. Combien de temps les conservons-nous ?
6. Vos droits
7. Cookies
8. Modifications
9. Contact DPO

### 3. Conditions Générales d'Utilisation

Sections recommandées:
1. Objet
2. Définitions
3. Inscription
4. Services
5. Obligations utilisateur
6. Propriété intellectuelle
7. Responsabilité
8. Durée et résiliation
9. Droit applicable

---

## ✅ Checklist Pré-Production

### Avant Mise en Production

#### Sécurité Technique
- [ ] Tous les mots de passe changés (pas de "password123")
- [ ] Variables d'environnement sécurisées (pas dans le code)
- [ ] HTTPS forcé sur tous les domaines
- [ ] Headers de sécurité configurés
- [ ] Rate limiting activé
- [ ] Logs de sécurité configurés
- [ ] Backups automatisés testés
- [ ] Plan de recovery documenté

#### RGPD
- [ ] Registre des traitements complété
- [ ] Politique de confidentialité publiée
- [ ] CGU publiées
- [ ] Formulaires de consentement configurés
- [ ] Droits utilisateurs implémentés (accès, rectification, suppression)
- [ ] Procédure violation de données documentée
- [ ] DPO désigné (si nécessaire)
- [ ] Cookies configurés (bannière si tracking)

#### Documentation
- [ ] Procédures d'urgence
- [ ] Contacts sécurité
- [ ] Inventaire données
- [ ] Schéma architecture sécurisée

---

## 📞 Contacts Sécurité

| Rôle | Contact | Email |
|------|---------|-------|
| Responsable Sécurité | [Nom] | security@trustdevis.com |
| DPO | [Nom] | dpo@trustdevis.com |
| Équipe Technique | [Nom] | tech@trustdevis.com |
| Hébergeur | Hostinger | support@hostinger.com |

---

## 🔄 Révisions

| Version | Date | Auteur | Modifications |
|---------|------|--------|---------------|
| 1.0 | 2026-03-09 | Agent Architecte | Création initiale |

---

*Document confidentiel - TrustDevis*
