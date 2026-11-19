import React from 'react';
import { View, StyleSheet, ViewStyle } from 'react-native';
import { Text } from 'react-native-paper';
import { MaterialCommunityIcons } from '@expo/vector-icons';
import Animated, { useAnimatedStyle, withSpring } from 'react-native-reanimated';

import { colors, spacing, typography } from '../theme';
import { TrustLevel } from '../store/analysisStore';

interface TrustBadgeProps {
  level: TrustLevel;
  score?: number;
  size?: 'small' | 'medium' | 'large';
}

const TRUST_CONFIG = {
  high: {
    color: colors.trustHigh,
    bgColor: colors.trustHigh + '20',
    icon: 'shield-check',
    label: 'Fiable',
    description: 'Ce devis présente un bon rapport qualité-prix',
  },
  medium: {
    color: colors.trustMedium,
    bgColor: colors.trustMedium + '20',
    icon: 'alert-circle',
    label: 'À vérifier',
    description: 'Certains éléments méritent votre attention',
  },
  low: {
    color: colors.trustLow,
    bgColor: colors.trustLow + '20',
    icon: 'alert-octagon',
    label: 'Risqué',
    description: 'Ce devis présente des anomalies significatives',
  },
  unknown: {
    color: colors.trustUnknown,
    bgColor: colors.trustUnknown + '20',
    icon: 'help-circle',
    label: 'Inconnu',
    description: 'Impossible d\'évaluer ce devis',
  },
};

const SIZE_CONFIG = {
  small: {
    padding: { paddingHorizontal: 8, paddingVertical: 4 },
    iconSize: 16,
    fontSize: 12,
    borderRadius: 12,
  },
  medium: {
    padding: { paddingHorizontal: 12, paddingVertical: 6 },
    iconSize: 20,
    fontSize: 14,
    borderRadius: 16,
  },
  large: {
    padding: { paddingHorizontal: 24, paddingVertical: 16 },
    iconSize: 48,
    fontSize: 24,
    borderRadius: 20,
  },
};

export function TrustBadge({ level, score, size = 'medium' }: TrustBadgeProps) {
  const config = TRUST_CONFIG[level];
  const sizeConfig = SIZE_CONFIG[size];

  const animatedStyle = useAnimatedStyle(() => ({
    transform: [{ scale: withSpring(1, { damping: 10 }) }],
  }));

  return (
    <Animated.View
      style={[
        styles.container,
        {
          backgroundColor: config.bgColor,
          borderRadius: sizeConfig.borderRadius,
          ...sizeConfig.padding,
        },
        animatedStyle,
      ]}
    >
      <MaterialCommunityIcons
        name={config.icon as any}
        size={sizeConfig.iconSize}
        color={config.color}
      />
      <View style={styles.textContainer}>
        <Text
          style={[
            styles.label,
            {
              color: config.color,
              fontSize: sizeConfig.fontSize,
            },
          ]}
        >
          {config.label}
        </Text>
        {score !== undefined && size !== 'small' && (
          <Text style={[styles.score, { color: config.color }]}>
            {score}/100
          </Text>
        )}
        {size === 'large' && (
          <Text style={[styles.description, { color: config.color }]}>
            {config.description}
          </Text>
        )}
      </View>
    </Animated.View>
  );
}

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  textContainer: {
    marginLeft: spacing.sm,
  },
  label: {
    fontWeight: '700',
  },
  score: {
    ...typography.caption,
    marginTop: 2,
    opacity: 0.8,
  },
  description: {
    ...typography.bodySmall,
    marginTop: spacing.xs,
    opacity: 0.9,
  },
});
