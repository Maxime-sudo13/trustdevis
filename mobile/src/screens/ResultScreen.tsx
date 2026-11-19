import React from 'react';
import { View, StyleSheet, ScrollView, Share } from 'react-native';
import { Text, Button, Surface, IconButton, Divider } from 'react-native-paper';
import { useNavigation, useRoute, RouteProp } from '@react-navigation/native';
import { StackNavigationProp } from '@react-navigation/stack';
import { MaterialCommunityIcons } from '@expo/vector-icons';
import Animated, { FadeIn, FadeInUp } from 'react-native-reanimated';

import { RootStackParamList } from '../navigation';
import { colors, spacing, typography, shadows } from '../theme';
import { TrustBadge } from '../components/TrustBadge';
import { PriceComparison } from '../components/PriceComparison';
import { useAnalysisStore } from '../store/analysisStore';

type ResultScreenRouteProp = RouteProp<RootStackParamList, 'Result'>;
type ResultScreenNavigationProp = StackNavigationProp<RootStackParamList>;

export default function ResultScreen() {
  const navigation = useNavigation<ResultScreenNavigationProp>();
  const route = useRoute<ResultScreenRouteProp>();
  const { analysisId } = route.params;
  
  const analysis = useAnalysisStore((state) => 
    state.analyses.find((a) => a.id === analysisId)
  );

  if (!analysis) {
    return (
      <View style={styles.container}>
        <Text>Analyse non trouvée</Text>
        <Button onPress={() => navigation.goBack()}>Retour</Button>
      </View>
    );
  }

  const handleShare = async () => {
    try {
      const message = `TrustDevis - Analyse de devis\n\n` +
        `Entreprise: ${analysis.extractedData?.companyName || 'N/A'}\n` +
        `Montant total: ${analysis.extractedData?.totalAmount?.toFixed(2) || 'N/A'} €\n` +
        `Score de confiance: ${analysis.trustScore?.score || 'N/A'}/100\n` +
        `Niveau: ${analysis.trustScore?.level === 'high' ? '✅ Fiable' : analysis.trustScore?.level === 'medium' ? '⚠️ À vérifier' : '❌ Risqué'}`;
      
      await Share.share({
        message,
        title: 'Mon analyse TrustDevis',
      });
    } catch (error) {
      console.error('Share error:', error);
    }
  };

  return (
    <View style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <IconButton
          icon="arrow-left"
          size={28}
          onPress={() => navigation.navigate('Main')}
        />
        <Text style={styles.headerTitle}>Résultat de l'analyse</Text>
        <IconButton
          icon="share-variant"
          size={24}
          onPress={handleShare}
        />
      </View>

      <ScrollView contentContainerStyle={styles.scrollContent}>
        {/* Trust Badge */}
        <Animated.View entering={FadeIn} style={styles.badgeContainer}>
          <TrustBadge 
            level={analysis.trustScore?.level || 'unknown'} 
            score={analysis.trustScore?.score}
            size="large"
          />
        </Animated.View>

        {/* Résumé */}
        <Animated.View entering={FadeInUp.delay(100)}>
          <Surface style={styles.card}>
            <Text style={styles.cardTitle}>Résumé du devis</Text>
            
            <View style={styles.summaryRow}>
              <Text style={styles.summaryLabel}>Entreprise</Text>
              <Text style={styles.summaryValue}>
                {analysis.extractedData?.companyName || 'Non détecté'}
              </Text>
            </View>
            
            <Divider style={styles.divider} />
            
            <View style={styles.summaryRow}>
              <Text style={styles.summaryLabel}>Montant total</Text>
              <Text style={styles.summaryValue}>
                {analysis.extractedData?.totalAmount 
                  ? `${analysis.extractedData.totalAmount.toFixed(2)} €`
                  : 'Non détecté'}
              </Text>
            </View>
            
            <Divider style={styles.divider} />
            
            <View style={styles.summaryRow}>
              <Text style={styles.summaryLabel}>Date du devis</Text>
              <Text style={styles.summaryValue}>
                {analysis.extractedData?.date 
                  ? new Date(analysis.extractedData.date).toLocaleDateString('fr-FR')
                  : 'Non détectée'}
              </Text>
            </View>
          </Surface>
        </Animated.View>

        {/* Comparaison prix */}
        {analysis.marketComparison && (
          <Animated.View entering={FadeInUp.delay(200)}>
            <Surface style={styles.card}>
              <Text style={styles.cardTitle}>Comparaison marché</Text>
              <PriceComparison comparison={analysis.marketComparison} />
            </Surface>
          </Animated.View>
        )}

        {/* Points d'attention */}
        {analysis.trustScore?.reasons && analysis.trustScore.reasons.length > 0 && (
          <Animated.View entering={FadeInUp.delay(300)}>
            <Surface style={styles.card}>
              <Text style={styles.cardTitle}>Points d'attention</Text>
              {analysis.trustScore.reasons.map((reason, index) => (
                <View key={index} style={styles.reasonItem}>
                  <MaterialCommunityIcons
                    name={analysis.trustScore?.level === 'high' ? 'check-circle' : 'alert-circle'}
                    size={20}
                    color={analysis.trustScore?.level === 'high' ? colors.success : colors.warning}
                  />
                  <Text style={styles.reasonText}>{reason}</Text>
                </View>
              ))}
            </Surface>
          </Animated.View>
        )}

        {/* Recommandations */}
        {analysis.recommendations && analysis.recommendations.length > 0 && (
          <Animated.View entering={FadeInUp.delay(400)}>
            <Surface style={styles.card}>
              <Text style={styles.cardTitle}>Nos recommandations</Text>
              {analysis.recommendations.map((rec, index) => (
                <View key={index} style={styles.recommendationItem}>
                  <MaterialCommunityIcons name="lightbulb" size={20} color={colors.primary} />
                  <Text style={styles.recommendationText}>{rec}</Text>
                </View>
              ))}
            </Surface>
          </Animated.View>
        )}

        {/* Détails */}
        {analysis.extractedData?.items && analysis.extractedData.items.length > 0 && (
          <Animated.View entering={FadeInUp.delay(500)}>
            <Surface style={styles.card}>
              <Text style={styles.cardTitle}>Détails des prestations</Text>
              {analysis.extractedData.items.map((item, index) => (
                <View key={index} style={styles.itemRow}>
                  <View style={styles.itemDescription}>
                    <Text style={styles.itemName}>{item.description}</Text>
                    <Text style={styles.itemQuantity}>{item.quantity} x {item.unitPrice.toFixed(2)} €</Text>
                  </View>
                  <Text style={styles.itemTotal}>{item.total.toFixed(2)} €</Text>
                </View>
              ))}
            </Surface>
          </Animated.View>
        )}

        {/* Boutons d'action */}
        <Animated.View entering={FadeInUp.delay(600)} style={styles.actionsContainer}>
          <Button
            mode="contained"
            onPress={() => navigation.navigate('Scan')}
            style={styles.actionButton}
            icon="camera"
          >
            Analyser un autre devis
          </Button>
          
          <Button
            mode="outlined"
            onPress={handleShare}
            style={styles.actionButton}
            icon="share-variant"
          >
            Partager le résultat
          </Button>
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
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingTop: spacing.lg,
    paddingHorizontal: spacing.sm,
  },
  headerTitle: {
    ...typography.h3,
    color: colors.textPrimary,
  },
  scrollContent: {
    padding: spacing.md,
    paddingBottom: spacing.xxl,
  },
  badgeContainer: {
    alignItems: 'center',
    marginVertical: spacing.lg,
  },
  card: {
    padding: spacing.md,
    borderRadius: 12,
    marginBottom: spacing.md,
    ...shadows.small,
  },
  cardTitle: {
    ...typography.h3,
    color: colors.textPrimary,
    marginBottom: spacing.md,
  },
  summaryRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: spacing.sm,
  },
  summaryLabel: {
    ...typography.body,
    color: colors.textSecondary,
  },
  summaryValue: {
    ...typography.body,
    color: colors.textPrimary,
    fontWeight: '600',
  },
  divider: {
    backgroundColor: colors.border,
  },
  reasonItem: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: spacing.xs,
  },
  reasonText: {
    ...typography.body,
    color: colors.textPrimary,
    marginLeft: spacing.sm,
    flex: 1,
  },
  recommendationItem: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    paddingVertical: spacing.xs,
  },
  recommendationText: {
    ...typography.body,
    color: colors.textPrimary,
    marginLeft: spacing.sm,
    flex: 1,
  },
  itemRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: spacing.sm,
    borderBottomWidth: 1,
    borderBottomColor: colors.borderLight,
  },
  itemDescription: {
    flex: 1,
  },
  itemName: {
    ...typography.body,
    color: colors.textPrimary,
  },
  itemQuantity: {
    ...typography.caption,
    color: colors.textSecondary,
    marginTop: 2,
  },
  itemTotal: {
    ...typography.body,
    color: colors.textPrimary,
    fontWeight: '600',
  },
  actionsContainer: {
    marginTop: spacing.md,
    gap: spacing.sm,
  },
  actionButton: {
    borderRadius: 8,
  },
});
