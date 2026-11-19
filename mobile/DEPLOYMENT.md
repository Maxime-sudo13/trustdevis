# TrustDevis Mobile - Guide de Déploiement

## Prérequis

- Node.js 18+
- Expo CLI: `npm install -g expo-cli`
- Xcode (pour iOS) - Mac uniquement
- Android Studio (pour Android)
- Compte Expo (gratuit sur https://expo.dev)

## Installation

```bash
# Cloner le projet
cd trustdevis/mobile

# Installer les dépendances
npm install

# Configurer les variables d'environnement
cp .env.example .env
# Éditer .env avec vos valeurs
```

## Développement Local

```bash
# Démarrer le serveur de développement
npm start

# Lancer sur iOS (simulator)
npm run ios

# Lancer sur Android (emulator)
npm run android
```

## Build pour les Stores

### iOS App Store

```bash
# Prérequis: Compte Apple Developer ($99/an)

# Configuration
expo eas build:configure

# Build de production
expo eas build --platform ios --profile production

# Soumettre à l'App Store
expo eas submit --platform ios
```

### Google Play Store

```bash
# Configuration
expo eas build:configure

# Build de production
expo eas build --platform android --profile production

# Soumettre au Play Store
expo eas submit --platform android
```

## Configuration EAS (Expo Application Services)

Créer `eas.json`:

```json
{
  "cli": {
    "version": ">= 5.0.0"
  },
  "build": {
    "development": {
      "developmentClient": true,
      "distribution": "internal"
    },
    "preview": {
      "distribution": "internal",
      "android": {
        "buildType": "apk"
      }
    },
    "production": {
      "autoIncrement": true
    }
  },
  "submit": {
    "production": {}
  }
}
```

## Checklist avant publication

### iOS
- [ ] Icône App Store (1024x1024)
- [ ] Captures d'écran pour iPhone (6.5", 5.5", iPad)
- [ ] Description de l'app
- [ ] Mots-clés
- [ ] URL de support
- [ ] URL de politique de confidentialité
- [ ] Informations de contact

### Android
- [ ] Icône (512x512)
- [ ] Captures d'écran (phone + tablet)
- [ ] Feature graphic (1024x500)
- [ ] Description courte et longue
- [ ] Politique de confidentialité

## Tests

```bash
# Tests unitaires
npm test

# Tests E2E avec Detox (optionnel)
npm run test:e2e
```

## Optimisations

### Performance
- Images optimisées (WebP)
- Code splitting
- Lazy loading des écrans
- Memoization des composants

### Taille de l'app
- Analyser avec `npx expo optimize`
- Supprimer les assets non utilisés
- Utiliser des icônes vectorielles

## Support

Pour toute question, contactez l'équipe TrustDevis.
