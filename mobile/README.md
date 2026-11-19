# TrustDevis Mobile

## 🎯 Application de vérification de devis - iOS & Android

### Stack Technique
- **Framework**: React Native (Expo)
- **Navigation**: React Navigation v6
- **State Management**: Zustand
- **UI**: React Native Paper + NativeWind
- **Storage**: AsyncStorage + MMKV
- **API**: Axios + React Query

### Structure du Projet
```
/src
  /api          - Configuration API
  /assets       - Images, fonts, icônes
  /components   - Composants réutilisables
  /constants    - Constantes globales
  /context      - Contextes React
  /hooks        - Custom hooks
  /navigation   - Configuration navigation
  /screens      - Écrans de l'app
  /services     - Services métier
  /store        - State management (Zustand)
  /theme        - Thème et styles
  /types        - Types TypeScript
  /utils        - Utilitaires
```

### Fonctionnalités MVP
1. 📸 Upload photo devis (caméra native)
2. 🔍 Analyse en temps réel
3. ✅ Badge de confiance
4. 📚 Historique analyses
5. 🔔 Notifications push

### Scripts
```bash
npm start      # Démarrer le serveur Metro
npm run ios    # Lancer sur iOS
npm run android # Lancer sur Android
npm run web    # Lancer sur Web
npm run test   # Tests
npm run lint   # Linting
```

### Prérequis
- Node.js 18+
- Expo CLI
- Xcode (iOS)
- Android Studio (Android)

### Configuration API
Créer un fichier `.env`:
```
API_URL=https://api.trustdevis.com
API_KEY=votre_cle_api
```

---
Développé par TrustDevis © 2026
