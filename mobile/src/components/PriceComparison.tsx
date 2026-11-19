import React from 'react';
import { View, StyleSheet } from 'react-native';
import { Text, ProgressBar } from 'react-native-paper';
import { MaterialCommunityIcons } from '@expo/vector-icons';

import { colors, spacing, typography } from '../theme';

interface MarketComparison {
  averagePrice: number;
  priceRange: { min: number; max: number };
  comparison: 'below' | 'within' | 'above';
  savings?: number;
  excess?: number;
}

interface PriceComparisonProps {
  comparison: MarketComparison;
}

export function PriceComparison({ comparison }: PriceComparisonProps) {
  const { averagePrice, priceRange, comparison: comp, savings, excess } = comparison;

  const getComparisonColor = () => {
    switch (comp) {
      case 'below':
        return colors.success;
      case 'within':
        return colors.primary;
      case 'above':
        return colors.warning;
      default:
        return colors.textSecondary;
    }
  };

  const getComparisonIcon = () => {
    switch (comp) {
      case 'below':
        return 'trending-down';
      case 'within':
        return 'check-circle';
      case 'above':
        return 'trending-up';
      default:
        return 'help-circle';
    }
  };

  const getComparisonText = () => {
    switch (comp) {
      case 'below':
        return `Vous économisez ${savings?.toFixed(2)} €`;
      case 'within':
        return 'Prix dans la fourchette du marché';
      case 'above':
        return `Surcoût estimé de ${excess?.toFixed(2)} €`;
      default:
        return 'Comparaison non disponible';
    }
  };

  const comparisonColor = getComparisonColor();

  return (
    <View style={styles.container}>
      {/* Indicateur visuel */}
      <View style={styles.comparisonRow}>
        <MaterialCommunityIcons
          name={getComparisonIcon() as any}
          size={32}
          color={comparisonColor}
        />
        <View style={styles.comparisonTextContainer}>
          <Text style={[styles.comparisonText, { color: comparisonColor }]}>
            {getComparisonText()}
          </Text>
          <Text style={styles.comparisonSubtext}>
            Prix moyen du marché: {averagePrice.toFixed(2)} €
          </Text>
        </View>
      </View>

      {/* Barre de fourchette */}
      <View style={styles.rangeContainer}>
        <View style={styles.rangeLabels}>
          <Text style={styles.rangeLabel}>{priceRange.min.toFixed(0)} €</Text>
          <Text style={styles.rangeLabel}>{priceRange.max.toFixed(0)} €</Text>
        </View>
        <View style={styles.rangeBar}>
          <View style={styles.rangeTrack} />
          <View 
            style={[
              styles.rangeIndicator, 
              { 
                left: `${((averagePrice - priceRange.min) / (priceRange.max - priceRange.min)) * 100}%`,
                backgroundColor: comparisonColor,
              }
            ]} 
          />
        </View>
        <Text style={styles.rangeCaption}>Fourchette de prix du marché</Text>
      </View>

      {/* Détails */}
      <View style={styles.detailsContainer}>
        <View style={styles.detailItem}>
          <MaterialCommunityIcons name="cash-minus" size={20} color={colors.success} />
          <View style={styles.detailTextContainer}>
            <Text style={styles.detailLabel}>Minimum du marché</Text>
            <Text style={styles.detailValue}>{priceRange.min.toFixed(2)} €</Text>
          </View>
        </View>
        
        <View style={styles.detailItem}>
          <MaterialCommunityIcons name="cash" size={20} color={colors.primary} />
          <View style={styles.detailTextContainer}>
            <Text style={styles.detailLabel}>Moyenne du marché</Text>
            <Text style={styles.detailValue}>{averagePrice.toFixed(2)} €</Text>
          </View>
        </View>
        
        <View style={styles.detailItem}>
          <MaterialCommunityIcons name="cash-plus" size={20} color={colors.warning} />
          <View style={styles.detailTextContainer}>
            <Text style={styles.detailLabel}>Maximum du marché</Text>
            <Text style={styles.detailValue}>{priceRange.max.toFixed(2)} €</Text>
          </View>
        </View>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    gap: spacing.md,
  },
  comparisonRow: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: colors.surface,
    padding: spacing.md,
    borderRadius: 12,
  },
  comparisonTextContainer: {
    marginLeft: spacing.md,
    flex: 1,
  },
  comparisonText: {
    ...typography.h3,
    fontWeight: '600',
  },
  comparisonSubtext: {
    ...typography.bodySmall,
    color: colors.textSecondary,
    marginTop: 2,
  },
  rangeContainer: {
    marginTop: spacing.sm,
  },
  rangeLabels: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: spacing.xs,
  },
  rangeLabel: {
    ...typography.caption,
    color: colors.textSecondary,
  },
  rangeBar: {
    height: 8,
    position: 'relative',
  },
  rangeTrack: {
    position: 'absolute',
    left: 0,
    right: 0,
    top: 3,
    height: 2,
    backgroundColor: colors.border,
    borderRadius: 1,
  },
  rangeIndicator: {
    position: 'absolute',
    width: 16,
    height: 16,
    borderRadius: 8,
    top: -4,
    marginLeft: -8,
    borderWidth: 2,
    borderColor: colors.background,
  },
  rangeCaption: {
    ...typography.caption,
    color: colors.textTertiary,
    textAlign: 'center',
    marginTop: spacing.xs,
  },
  detailsContainer: {
    gap: spacing.sm,
    marginTop: spacing.sm,
  },
  detailItem: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: spacing.xs,
  },
  detailTextContainer: {
    marginLeft: spacing.sm,
    flex: 1,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  detailLabel: {
    ...typography.bodySmall,
    color: colors.textSecondary,
  },
  detailValue: {
    ...typography.body,
    color: colors.textPrimary,
    fontWeight: '600',
  },
});
