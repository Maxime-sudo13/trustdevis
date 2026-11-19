# TrustDevis Mobile - Screenshots & Preview

## 📱 Screenshots de l'Application

### Écran d'accueil
- Logo TrustDevis
- Statistiques utilisateur
- CTA principal "Analyser un devis"
- Historique récent

### Scanner
- Interface caméra native
- Cadre de guidage
- Capture photo
- Import galerie

### Analyse en cours
- Progress bar animée
- Étapes du processus
- Preview de l'image
- Animation de chargement

### Résultat
- Badge de confiance (couleur selon niveau)
- Résumé du devis
- Comparaison marché
- Recommandations
- Bouton partage

### Historique
- Liste des analyses
- Filtres et recherche
- Suppression
- Navigation vers détail

### Profil
- Informations utilisateur
- Statistiques
- Paramètres
- Déconnexion

### Authentification
- Login
- Register
- Formulaires avec validation
- Animations fluides

## 🎨 Design System

### Couleurs
- **Primary**: #2563EB (Bleu)
- **Success**: #059669 (Vert)
- **Warning**: #D97706 (Orange)
- **Error**: #DC2626 (Rouge)

### Typography
- H1: 32px Bold
- H2: 24px Bold
- H3: 20px SemiBold
- Body: 16px Regular
- Caption: 12px Regular

### Composants
- Cards avec ombres
- Badges colorés
- Boutons arrondis
- Progress bars
- Icônes Material

## 📲 Stores Ready

### iOS
- Bundle ID: com.trustdevis.app
- Build number: 1.0.0
- Permissions: Caméra, Photos, Notifications

### Android
- Package: com.trustdevis.app
- Version Code: 1
- Permissions: Caméra, Stockage, Notifications

## 🚀 Build Commands

```bash
# Preview builds
expo eas build --profile preview --platform ios
expo eas build --profile preview --platform android

# Production builds
expo eas build --profile production --platform ios
expo eas build --profile production --platform android
```

## 📦 Assets Requis pour Stores

### iOS
- [ ] Icon: 1024x1024
- [ ] Screenshots: iPhone 6.5", 5.5", iPad
- [ ] App Preview video (optionnel)

### Android
- [ ] Icon: 512x512
- [ ] Feature Graphic: 1024x500
- [ ] Screenshots: Phone + 7" + 10" tablets

## ✅ Checklist Pré-lancement

- [ ] Tests sur iOS (simulator + device)
- [ ] Tests sur Android (emulator + device)
- [ ] Mode offline testé
- [ ] Notifications configurées
- [ ] Analytics intégrés
- [ ] Crash reporting (Sentry)
- [ ] Politique de confidentialité
- [ ] Conditions d'utilisation
- [ ] Support email configuré
