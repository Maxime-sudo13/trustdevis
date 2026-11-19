# Registre des Traitements - TrustDevis
## Conformité CNIL / RGPD

---

### Informations Générales

| Champ | Valeur |
|-------|--------|
| **Organisation** | TrustDevis |
| **Adresse** | À définir |
| **DPO (Délégué à la Protection des Données)** | dpo@trustdevis.fr |
| **Date de création du registre** | 2024-03-09 |
| **Version** | 1.0.0 |

---

### Traitement 1: Création et gestion du compte utilisateur

| Champ | Valeur |
|-------|--------|
| **ID** | USER_REGISTRATION |
| **Finalité** | Création et gestion du compte utilisateur |
| **Description** | Stockage des informations de profil et authentification |
| **Base légale** | Exécution du contrat (art. 6.1.b RGPD) |
| **Catégories de données** | Nom, email, téléphone, adresse, mot de passe hashé |
| **Destinataires** | TrustDevis |
| **Durée de conservation** | 3 ans après suppression du compte |
| **Mesures de sécurité** | Chiffrement AES-256, authentification 2FA |

---

### Traitement 2: Analyse et vérification de devis

| Champ | Valeur |
|-------|--------|
| **ID** | QUOTE_ANALYSIS |
| **Finalité** | Analyse et vérification de devis |
| **Description** | Traitement des documents de devis pour détection d'anomalies |
| **Base légale** | Exécution du contrat (art. 6.1.b RGPD) |
| **Catégories de données** | Documents de devis, informations du projet, métadonnées |
| **Destinataires** | TrustDevis, Prestataires de vérification |
| **Durée de conservation** | 5 ans |
| **Mesures de sécurité** | Stockage chiffré, accès restreint, logs d'audit |

---

### Traitement 3: Communication avec l'utilisateur

| Champ | Valeur |
|-------|--------|
| **ID** | COMMUNICATION |
| **Finalité** | Communication avec l'utilisateur |
| **Description** | Envoi de notifications et mises à jour |
| **Base légale** | Exécution du contrat (art. 6.1.b RGPD) |
| **Catégories de données** | Email, préférences de notification, historique des communications |
| **Destinataires** | TrustDevis, SendGrid (service d'email) |
| **Durée de conservation** | 3 ans |
| **Mesures de sécurité** | Connexion TLS, authentification API |

---

### Traitement 4: Marketing et communications commerciales

| Champ | Valeur |
|-------|--------|
| **ID** | MARKETING |
| **Finalité** | Marketing et communications commerciales |
| **Description** | Newsletters, offres promotionnelles |
| **Base légale** | Consentement (art. 6.1.a RGPD) |
| **Catégories de données** | Email, préférences marketing, comportement de navigation |
| **Destinataires** | TrustDevis |
| **Durée de conservation** | 3 ans ou jusqu'à révocation du consentement |
| **Mesures de sécurité** | Double opt-in, lien de désinscription dans chaque email |

---

### Traitement 5: Analyse d'utilisation et amélioration du service

| Champ | Valeur |
|-------|--------|
| **ID** | ANALYTICS |
| **Finalité** | Analyse d'utilisation et amélioration du service |
| **Description** | Statistiques d'utilisation anonymisées |
| **Base légale** | Consentement (art. 6.1.a RGPD) |
| **Catégories de données** | Données de navigation anonymisées, cookies techniques |
| **Destinataires** | TrustDevis, Google Analytics |
| **Durée de conservation** | 2 ans |
| **Mesures de sécurité** | Anonymisation IP, pas de données personnelles |

---

### Traitement 6: Prévention de la fraude et sécurité

| Champ | Valeur |
|-------|--------|
| **ID** | FRAUD_PREVENTION |
| **Finalité** | Prévention de la fraude et sécurité |
| **Description** | Détection d'activités suspectes et sécurisation |
| **Base légale** | Intérêt légitime (art. 6.1.f RGPD) |
| **Catégories de données** | Logs de connexion, IP, comportement utilisateur |
| **Destinataires** | TrustDevis |
| **Durée de conservation** | 5 ans |
| **Mesures de sécurité** | Chiffrement, accès restreint, surveillance temps réel |

---

### Traitement 7: Obligations légales et réglementaires

| Champ | Valeur |
|-------|--------|
| **ID** | LEGAL_COMPLIANCE |
| **Finalité** | Obligations légales et réglementaires |
| **Description** | Conservation pour obligations fiscales et légales |
| **Base légale** | Obligation légale (art. 6.1.c RGPD) |
| **Catégories de données** | Données de facturation, transactions |
| **Destinataires** | TrustDevis, Autorités compétentes (si requis) |
| **Durée de conservation** | 10 ans (obligation fiscale) |
| **Mesures de sécurité** | Archivage sécurisé, accès restreint |

---

## Droits des personnes concernées

Conformément au RGPD, les utilisateurs disposent des droits suivants :

1. **Droit d'accès** (art. 15) - Obtenir une copie de leurs données
2. **Droit de rectification** (art. 16) - Corriger des données inexactes
3. **Droit à l'effacement** (art. 17) - Demander la suppression de leurs données
4. **Droit à la limitation du traitement** (art. 18)
5. **Droit à la portabilité** (art. 20) - Récupérer leurs données dans un format structuré
6. **Droit d'opposition** (art. 21) - S'opposer au traitement
7. **Droit de ne pas faire l'objet d'une décision automatisée** (art. 22)

**Exercice des droits** : dpo@trustdevis.fr ou via l'API `/gdpr/export` et `/gdpr/delete`

---

## Mesures de sécurité mises en œuvre

- Chiffrement des données en transit (TLS 1.3)
- Chiffrement des données au repos (AES-256)
- Authentification forte (2FA)
- Logs d'audit complets
- Accès restreint par rôle (RBAC)
- Sauvegardes chiffrées
- Tests de pénétration annuels
- Formation RGPD de l'équipe

---

## Sous-traitants

| Prestataire | Service | Pays | Garanties |
|-------------|---------|------|-----------|
| SendGrid | Envoi d'emails | USA | DPA signé, SCC |
| Google Analytics | Analytics | USA | DPA signé, SCC |
| Hostinger | Hébergement | Lituanie | DPA |

---

## Date de dernière mise à jour

**09 Mars 2024**

---

*Ce registre est mis à jour régulièrement et conforme aux exigences de l'article 30 du RGPD.*
