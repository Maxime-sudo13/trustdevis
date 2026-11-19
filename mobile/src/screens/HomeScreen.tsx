import React from 'react';
import { View, StyleSheet, TouchableOpacity } from 'react-native';
import { Text, Button, Surface } from 'react-native-paper';
import { MaterialCommunityIcons } from '@expo/vector-icons';
import { useNavigation } from '@react-navigation/native';
import { StackNavigationProp } from '@react-navigation/stack';
import Animated, { FadeIn, FadeInUp } from 'react-native-reanimated';

import { RootStackParamList } from '../navigation';
import { colors, spacing, typography, shadows } from '../theme';
import { TrustBadge } from '../components/TrustBadge';
import { useAnalysisStore } from '../store/analysisStore';

type HomeScreenNavigationProp = StackNavigationProp<RootStackParamList>;

export default function HomeScreen() {
  const navigation = useNavigation<HomeScreenNavigationProp>();
  const analyses = useAnalysisStore((state) => state.analyses);
  
  const recentAnalyses = analyses.slice(0, 3);
  const completedCount = analyses.filter(a => a.status === 'completed').length;

  return (
    <View style={styles.container}>
      {/* Header */}
      <Animated.View entering={FadeIn} style={styles.header}>
        <Text style={styles.title}>TrustDevis</Text>
        <Text style={styles.subtitle}>Vérifiez vos devis en toute confiance</Text>
      </Animated.View>

      {/* Stats Cards */}
      <Animated.View entering={FadeInUp.delay(100)} style={styles.statsContainer}>
        <Surface style={styles.statCard}>
          <MaterialCommunityIcons name="file-check" size={32} color={colors.primary} />
          <Text style={styles.statNumber}>{completedCount}</Text>
          <Text style={styles.statLabel}>Devis analysés</Text>
        </Surface>
        
        <Surface style={styles.statCard}>
          <MaterialCommunityIcons name="shield-check" size={32} color={colors.success} />
          <Text style={styles.statNumber}>
            {analyses.length > 0 
              ? Math.round((analyses.filter(a => a.trustScore?.level === 'high').length / analyses.length) * 100)
              : 0}%
          </Text>
          <Text style={styles.statLabel}>Taux de confiance</Text>
        </Surface>
      </Animated.View>

      {/* CTA Principal */}
      <Animated.View entering={FadeInUp.delay(200)} style={styles.ctaContainer}>
        <Surface style={styles.ctaCard}>
          <MaterialCommunityIcons name="camera" size={48} color={colors.primary} />
          <Text style={styles.ctaTitle}>Analyser un devis</Text>
          <Text style={styles.ctaDescription}>
            Prenez une photo ou importez un document pour vérifier votre devis
          </Text>
          <Button
            mode="contained"
            onPress={() => navigation.navigate('Scan')}
            style={styles.ctaButton}
            contentStyle={styles.ctaButtonContent}
          >
            Commencer l'analyse
          </Button>
        </Surface>
      </Animated.View>

      {/* Analyses récentes */}
      {recentAnalyses.length > 0 && (
        <Animated.View entering={FadeInUp.delay(300)} style={styles.recentContainer}>
          <View style={styles.recentHeader}>
            <Text style={styles.recentTitle}>Analyses récentes</Text>
            <TouchableOpacity onPress={() => navigation.navigate('Main', { screen: 'History' })}>
              <Text style={styles.seeAll}>Voir tout</Text>
            </TouchableOpacity>
          </View>
          
          {recentAnalyses.map((analysis, index) => (
            <TouchableOpacity
              key={analysis.id}
              onPress={() => navigation.navigate('Result', { analysisId: analysis.id })}
            >
              <Surface style={styles.recentItem}>
                <View style={styles.recentItemLeft}>
                  <MaterialCommunityIcons 
                    name="file-document" 
                    size={24} 
                    color={colors.textSecondary} 
                  />
                  <View style={styles.recentItemInfo}>
                    <Text style={styles.recentItemTitle}>
                      {analysis.extractedData?.companyName || 'Devis'}
                    </Text>
                    <Text style={styles.recentItemDate}>
                      {new Date(analysis.createdAt).toLocaleDateString('fr-FR')}
                    </Text>
                  </View>
                </View>
                {analysis.trustScore && (
                  <TrustBadge level={analysis.trustScore.level} size="small" />
                )}
              </Surface>
            </TouchableOpacity>
          ))}
        </Animated.View>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
    padding: spacing.md,
  },
  header: {
    marginTop: spacing.xl,
    marginBottom: spacing.lg,
  },
  title: {
    ...typography.h1,
    color: colors.primary,
    textAlign: 'center',
  },
  subtitle: {
    ...typography.body,
    color: colors.textSecondary,
    textAlign: 'center',
    marginTop: spacing.xs,
  },
  statsContainer: {
    flexDirection: 'row',
    gap: spacing.md,
    marginBottom: spacing.lg,
  },
  statCard: {
    flex: 1,
    padding: spacing.md,
    borderRadius: 12,
    alignItems: 'center',
    ...shadows.small,
  },
  statNumber: {
    ...typography.h2,
    color: colors.textPrimary,
    marginTop: spacing.xs,
  },
  statLabel: {
    ...typography.caption,
    color: colors.textSecondary,
    marginTop: spacing.xs,
  },
  ctaContainer: {
    marginBottom: spacing.lg,
  },
  ctaCard: {
    padding: spacing.lg,
    borderRadius: 16,
    alignItems: 'center',
    ...shadows.medium,
  },
  ctaTitle: {
    ...typography.h3,
    color: colors.textPrimary,
    marginTop: spacing.sm,
  },
  ctaDescription: {
    ...typography.bodySmall,
    color: colors.textSecondary,
    textAlign: 'center',
    marginTop: spacing.xs,
    marginBottom: spacing.md,
  },
  ctaButton: {
    width: '100%',
    borderRadius: 8,
  },
  ctaButtonContent: {
    paddingVertical: spacing.sm,
  },
  recentContainer: {
    flex: 1,
  },
  recentHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: spacing.sm,
  },
  recentTitle: {
    ...typography.h3,
    color: colors.textPrimary,
  },
  seeAll: {
    ...typography.bodySmall,
    color: colors.primary,
  },
  recentItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: spacing.md,
    borderRadius: 12,
    marginBottom: spacing.sm,
    ...shadows.small,
  },
  recentItemLeft: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  recentItemInfo: {
    marginLeft: spacing.sm,
    flex: 1,
  },
  recentItemTitle: {
    ...typography.body,
    color: colors.textPrimary,
    fontWeight: '600',
  },
  recentItemDate: {
    ...typography.caption,
    color: colors.textSecondary,
    marginTop: 2,
  },
});
