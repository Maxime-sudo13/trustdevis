import React, { useEffect, useState } from 'react';
import { View, StyleSheet, Image, ScrollView } from 'react-native';
import { Text, Button, ActivityIndicator, Surface, ProgressBar } from 'react-native-paper';
import { useNavigation, useRoute, RouteProp } from '@react-navigation/native';
import { StackNavigationProp } from '@react-navigation/stack';
import Animated, { FadeIn, FadeInUp } from 'react-native-reanimated';
import { MaterialCommunityIcons } from '@expo/vector-icons';

import { RootStackParamList } from '../navigation';
import { colors, spacing, typography, shadows } from '../theme';
import { analysisService } from '../services/analysisService';
import { useAnalysisStore, AnalysisResult } from '../store/analysisStore';

type AnalysisScreenRouteProp = RouteProp<RootStackParamList, 'Analysis'>;
type AnalysisScreenNavigationProp = StackNavigationProp<RootStackParamList>;

const STEPS = [
  { id: 'upload', label: 'Upload de l\'image', icon: 'cloud-upload' },
  { id: 'ocr', label: 'Extraction du texte', icon: 'text-recognition' },
  { id: 'parse', label: 'Analyse des données', icon: 'file-document' },
  { id: 'market', label: 'Comparaison marché', icon: 'chart-bar' },
  { id: 'score', label: 'Calcul du score', icon: 'shield-check' },
];

export default function AnalysisScreen() {
  const navigation = useNavigation<AnalysisScreenNavigationProp>();
  const route = useRoute<AnalysisScreenRouteProp>();
  const { imageUri } = route.params;
  
  const [currentStep, setCurrentStep] = useState(0);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [analysisId, setAnalysisId] = useState<string | null>(null);
  
  const addAnalysis = useAnalysisStore((state) => state.addAnalysis);
  const updateAnalysis = useAnalysisStore((state) => state.updateAnalysis);

  useEffect(() => {
    startAnalysis();
  }, []);

  const startAnalysis = async () => {
    try {
      // Étape 1: Upload
      setCurrentStep(0);
      setProgress(0.1);
      
      const uploadResponse = await analysisService.uploadImage(imageUri);
      setAnalysisId(uploadResponse.analysisId);
      
      // Créer l'analyse initiale
      const initialAnalysis: AnalysisResult = {
        id: uploadResponse.analysisId,
        imageUri,
        createdAt: new Date().toISOString(),
        status: 'processing',
      };
      addAnalysis(initialAnalysis);
      
      // Simuler la progression des étapes
      for (let i = 1; i < STEPS.length; i++) {
        await new Promise((resolve) => setTimeout(resolve, 1500));
        setCurrentStep(i);
        setProgress((i + 1) / STEPS.length);
      }
      
      // Polling pour récupérer le résultat
      await analysisService.pollAnalysisStatus(
        uploadResponse.analysisId,
        (analysis) => {
          updateAnalysis(uploadResponse.analysisId, analysis);
          if (analysis.status === 'completed') {
            navigation.replace('Result', { analysisId: uploadResponse.analysisId });
          }
        },
        (err) => {
          setError(err.message);
          updateAnalysis(uploadResponse.analysisId, { 
            status: 'error',
            error: err.message 
          });
        }
      );
      
    } catch (err: any) {
      setError(err.message || 'Une erreur est survenue lors de l\'analyse');
    }
  };

  if (error) {
    return (
      <View style={styles.container}>
        <Animated.View entering={FadeIn} style={styles.errorContainer}>
          <MaterialCommunityIcons name="alert-circle" size={64} color={colors.error} />
          <Text style={styles.errorTitle}>Oups !</Text>
          <Text style={styles.errorText}>{error}</Text>
          <Button
            mode="contained"
            onPress={() => navigation.goBack()}
            style={styles.errorButton}
          >
            Réessayer
          </Button>
        </Animated.View>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <ScrollView contentContainerStyle={styles.scrollContent}>
        {/* Image preview */}
        <Animated.View entering={FadeIn} style={styles.imageContainer}>
          <Image source={{ uri: imageUri }} style={styles.image} />
          <View style={styles.processingOverlay}>
            <ActivityIndicator size="large" color="#fff" />
          </View>
        </Animated.View>

        {/* Progress */}
        <Animated.View entering={FadeInUp.delay(200)} style={styles.progressContainer}>
          <ProgressBar
            progress={progress}
            color={colors.primary}
            style={styles.progressBar}
          />
          <Text style={styles.progressText}>{Math.round(progress * 100)}%</Text>
        </Animated.View>

        {/* Steps */}
        <View style={styles.stepsContainer}>
          {STEPS.map((step, index) => (
            <Animated.View
              key={step.id}
              entering={FadeInUp.delay(300 + index * 100)}
              style={[
                styles.stepItem,
                index === currentStep && styles.stepItemActive,
                index < currentStep && styles.stepItemCompleted,
              ]}
            >
              <Surface
                style={[
                  styles.stepIcon,
                  index === currentStep && styles.stepIconActive,
                  index < currentStep && styles.stepIconCompleted,
                ]}
              >
                <MaterialCommunityIcons
                  name={index < currentStep ? 'check' : step.icon as any}
                  size={24}
                  color={
                    index === currentStep
                      ? colors.primary
                      : index < currentStep
                      ? colors.success
                      : colors.textTertiary
                  }
                />
              </Surface>
              <Text
                style={[
                  styles.stepLabel,
                  index === currentStep && styles.stepLabelActive,
                  index < currentStep && styles.stepLabelCompleted,
                ]}
              >
                {step.label}
              </Text>
              {index === currentStep && (
                <ActivityIndicator size="small" color={colors.primary} style={styles.stepLoader} />
              )}
            </Animated.View>
          ))}
        </View>

        {/* Info text */}
        <Animated.View entering={FadeInUp.delay(800)} style={styles.infoContainer}>
          <MaterialCommunityIcons name="information" size={20} color={colors.textSecondary} />
          <Text style={styles.infoText}>
            L'analyse peut prendre jusqu'à 30 secondes. Ne fermez pas l'application.
          </Text>
        </Animated.View>
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
  },
  scrollContent: {
    padding: spacing.md,
  },
  imageContainer: {
    alignSelf: 'center',
    marginTop: spacing.lg,
    borderRadius: 16,
    overflow: 'hidden',
    ...shadows.medium,
  },
  image: {
    width: 200,
    height: 280,
    resizeMode: 'cover',
  },
  processingOverlay: {
    ...StyleSheet.absoluteFillObject,
    backgroundColor: 'rgba(0,0,0,0.4)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  progressContainer: {
    marginTop: spacing.lg,
    alignItems: 'center',
  },
  progressBar: {
    width: '100%',
    height: 8,
    borderRadius: 4,
  },
  progressText: {
    ...typography.h3,
    color: colors.primary,
    marginTop: spacing.sm,
  },
  stepsContainer: {
    marginTop: spacing.lg,
  },
  stepItem: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: spacing.sm,
    opacity: 0.5,
  },
  stepItemActive: {
    opacity: 1,
  },
  stepItemCompleted: {
    opacity: 0.8,
  },
  stepIcon: {
    width: 48,
    height: 48,
    borderRadius: 24,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: colors.surface,
  },
  stepIconActive: {
    backgroundColor: colors.primaryLight,
  },
  stepIconCompleted: {
    backgroundColor: colors.success + '20',
  },
  stepLabel: {
    ...typography.body,
    color: colors.textSecondary,
    marginLeft: spacing.md,
    flex: 1,
  },
  stepLabelActive: {
    color: colors.textPrimary,
    fontWeight: '600',
  },
  stepLabelCompleted: {
    color: colors.success,
  },
  stepLoader: {
    marginLeft: spacing.sm,
  },
  infoContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: colors.surface,
    padding: spacing.md,
    borderRadius: 12,
    marginTop: spacing.lg,
  },
  infoText: {
    ...typography.bodySmall,
    color: colors.textSecondary,
    marginLeft: spacing.sm,
    flex: 1,
  },
  errorContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: spacing.lg,
  },
  errorTitle: {
    ...typography.h2,
    color: colors.textPrimary,
    marginTop: spacing.md,
  },
  errorText: {
    ...typography.body,
    color: colors.textSecondary,
    textAlign: 'center',
    marginTop: spacing.sm,
    marginBottom: spacing.lg,
  },
  errorButton: {
    paddingHorizontal: spacing.xl,
  },
});
