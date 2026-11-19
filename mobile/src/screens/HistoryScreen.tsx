import React from 'react';
import { View, StyleSheet, FlatList, TouchableOpacity } from 'react-native';
import { Text, Surface, IconButton } from 'react-native-paper';
import { useNavigation } from '@react-navigation/native';
import { StackNavigationProp } from '@react-navigation/stack';
import { MaterialCommunityIcons } from '@expo/vector-icons';
import Animated, { FadeInUp } from 'react-native-reanimated';

import { RootStackParamList } from '../navigation';
import { colors, spacing, typography, shadows } from '../theme';
import { TrustBadge } from '../components/TrustBadge';
import { useAnalysisStore } from '../store/analysisStore';

type HistoryScreenNavigationProp = StackNavigationProp<RootStackParamList>;

export default function HistoryScreen() {
  const navigation = useNavigation<HistoryScreenNavigationProp>();
  const analyses = useAnalysisStore((state) => state.analyses);
  const deleteAnalysis = useAnalysisStore((state) => state.deleteAnalysis);

  const renderItem = ({ item, index }: { item: typeof analyses[0]; index: number }) => (
    <Animated.View entering={FadeInUp.delay(index * 50)}>
      <TouchableOpacity
        onPress={() => navigation.navigate('Result', { analysisId: item.id })}
      >
        <Surface style={styles.item}>
          <View style={styles.itemContent}>
            {/* Icon */}
            <View style={styles.iconContainer}>
              <MaterialCommunityIcons
                name="file-document-outline"
                size={32}
                color={colors.primary}
              />
            </View>

            {/* Info */}
            <View style={styles.infoContainer}>
              <Text style={styles.companyName}>
                {item.extractedData?.companyName || 'Devis'}
              </Text>
              <Text style={styles.date}>
                {new Date(item.createdAt).toLocaleDateString('fr-FR', {
                  day: 'numeric',
                  month: 'long',
                  year: 'numeric',
                })}
              </Text>
              {item.extractedData?.totalAmount && (
                <Text style={styles.amount}>
                  {item.extractedData.totalAmount.toFixed(2)} €
                </Text>
              )}
            </View>

            {/* Badge */}
            <View style={styles.badgeContainer}>
              {item.trustScore ? (
                <TrustBadge level={item.trustScore.level} size="small" />
              ) : (
                <View style={styles.statusBadge}>
                  <Text style={styles.statusText}>
                    {item.status === 'processing' ? 'En cours' : 'Erreur'}
                  </Text>
                </View>
              )}
            </View>

            {/* Delete button */}
            <IconButton
              icon="delete-outline"
              size={20}
              iconColor={colors.textSecondary}
              onPress={() => deleteAnalysis(item.id)}
            />
          </View>
        </Surface>
      </TouchableOpacity>
    </Animated.View>
  );

  if (analyses.length === 0) {
    return (
      <View style={styles.emptyContainer}>
        <MaterialCommunityIcons
          name="history"
          size={80}
          color={colors.textTertiary}
        />
        <Text style={styles.emptyTitle}>Aucune analyse</Text>
        <Text style={styles.emptyText}>
          Vos analyses de devis apparaîtront ici
        </Text>
        <TouchableOpacity
          style={styles.emptyButton}
          onPress={() => navigation.navigate('Scan')}
        >
          <Text style={styles.emptyButtonText}>Analyser un devis</Text>
        </TouchableOpacity>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Historique</Text>
      <Text style={styles.subtitle}>
        {analyses.length} analyse{analyses.length > 1 ? 's' : ''}
      </Text>

      <FlatList
        data={analyses}
        renderItem={renderItem}
        keyExtractor={(item) => item.id}
        contentContainerStyle={styles.list}
        showsVerticalScrollIndicator={false}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
    padding: spacing.md,
  },
  title: {
    ...typography.h2,
    color: colors.textPrimary,
    marginTop: spacing.lg,
  },
  subtitle: {
    ...typography.body,
    color: colors.textSecondary,
    marginBottom: spacing.md,
  },
  list: {
    paddingBottom: spacing.xl,
  },
  item: {
    marginBottom: spacing.sm,
    borderRadius: 12,
    ...shadows.small,
  },
  itemContent: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: spacing.md,
  },
  iconContainer: {
    width: 48,
    height: 48,
    borderRadius: 24,
    backgroundColor: colors.primaryLight,
    justifyContent: 'center',
    alignItems: 'center',
  },
  infoContainer: {
    flex: 1,
    marginLeft: spacing.md,
  },
  companyName: {
    ...typography.body,
    color: colors.textPrimary,
    fontWeight: '600',
  },
  date: {
    ...typography.caption,
    color: colors.textSecondary,
    marginTop: 2,
  },
  amount: {
    ...typography.bodySmall,
    color: colors.primary,
    fontWeight: '600',
    marginTop: 2,
  },
  badgeContainer: {
    marginRight: spacing.sm,
  },
  statusBadge: {
    paddingHorizontal: spacing.sm,
    paddingVertical: 4,
    borderRadius: 12,
    backgroundColor: colors.surface,
  },
  statusText: {
    ...typography.caption,
    color: colors.textSecondary,
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: spacing.lg,
  },
  emptyTitle: {
    ...typography.h2,
    color: colors.textPrimary,
    marginTop: spacing.lg,
  },
  emptyText: {
    ...typography.body,
    color: colors.textSecondary,
    textAlign: 'center',
    marginTop: spacing.xs,
    marginBottom: spacing.lg,
  },
  emptyButton: {
    backgroundColor: colors.primary,
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.md,
    borderRadius: 8,
  },
  emptyButtonText: {
    ...typography.button,
    color: '#fff',
  },
});
