# TrustDevis Mobile - Documentation

## Architecture

### Stack Technique
- **React Native (Expo)**: Framework cross-platform
- **TypeScript**: Typage statique
- **Zustand**: State management léger
- **React Query**: Gestion des requêtes API
- **React Native Paper**: Composants UI Material Design
- **React Navigation**: Navigation entre écrans
- **Reanimated**: Animations fluides

### Structure des Dossiers
```
src/
├── api/           # Configuration Axios
├── assets/        # Images, fonts
├── components/    # Composants réutilisables
├── constants/     # Constantes globales
├── hooks/         # Custom React hooks
├── navigation/    # Configuration navigation
├── screens/       # Écrans de l'application
├── services/      # Services métier (API)
├── store/         # Zustand stores
├── theme/         # Thème et styles
├── types/         # Types TypeScript
└── utils/         # Fonctions utilitaires
```

## Flux de Données

### Authentification
1. Login/Register → authService → API
2. Token stocké dans SecureStore
3. AuthStore mis à jour
4. Navigation redirige vers Main

### Analyse de Devis
1. ScanScreen → capture image
2. AnalysisScreen → upload vers API
3. Polling jusqu'à completion
4. ResultScreen → affichage résultats

## API Integration

### Endpoints attendus
```
POST   /auth/login
POST   /auth/register
GET    /auth/me
POST   /analysis/upload
GET    /analysis/:id
GET    /analysis/history
DELETE /analysis/:id
```

### Format de réponse Analysis
```typescript
{
  id: string;
  status: 'completed' | 'error';
  extractedData: {
    companyName: string;
    totalAmount: number;
    date: string;
    items: Array<{
      description: string;
      quantity: number;
      unitPrice: number;
      total: number;
    }>;
  };
  trustScore: {
    level: 'high' | 'medium' | 'low';
    score: number;
    reasons: string[];
  };
  marketComparison: {
    averagePrice: number;
    priceRange: { min: number; max: number };
    comparison: 'below' | 'within' | 'above';
    savings?: number;
    excess?: number;
  };
  recommendations: string[];
}
```

## Composants Clés

### TrustBadge
Affiche le niveau de confiance avec couleur et icône adaptées.

```tsx
<TrustBadge level="high" score={85} size="large" />
```

### PriceComparison
Visualise la comparaison avec le marché.

```tsx
<PriceComparison comparison={marketComparison} />
```

## Offline Mode

L'application supporte le mode offline grâce à:
- AsyncStorage pour les données
- React Query pour le cache
- Queue des uploads en attente

## Notifications Push

Configuration Expo Notifications:
- Token enregistré au login
- Notifications sur completion d'analyse
- Badge count sur l'icône app

## Sécurité

- Token JWT dans SecureStore
- HTTPS obligatoire
- Validation des inputs
- Pas de données sensibles en clair

## Tests

```bash
# Tests unitaires
npm test

# Type checking
npm run type-check

# Linting
npm run lint
```

## Personnalisation

### Thème
Modifier `src/theme/index.ts`:
- Couleurs
- Typography
- Spacing
- Shadows

### Langue
L'app est en français. Pour ajouter i18n:
1. Installer `react-i18next`
2. Créer fichiers de traduction
3. Wrapper l'app avec I18nextProvider

## Débogage

### Expo Dev Tools
```bash
npm start
# Appuyer sur 'd' pour ouvrir DevTools
```

### React Native Debugger
```bash
# MacOS
open "rndebugger://set-debugger-loc?host=localhost&port=8081"
```

### Logs
```bash
# iOS
npx react-native log-ios

# Android
npx react-native log-android
```

## Ressources

- [Expo Docs](https://docs.expo.dev)
- [React Native Docs](https://reactnative.dev)
- [React Navigation](https://reactnavigation.org)
- [React Native Paper](https://callstack.github.io/react-native-paper)
