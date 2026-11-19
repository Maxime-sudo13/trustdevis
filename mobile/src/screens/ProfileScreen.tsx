import React from 'react';
import { View, StyleSheet, ScrollView, TouchableOpacity, Alert } from 'react-native';
import { Text, Surface, Button, Avatar, Divider } from 'react-native-paper';
import { MaterialCommunityIcons } from '@expo/vector-icons';
import { useNavigation } from '@react-navigation/native';

import { colors, spacing, typography, shadows } from '../theme';
import { useAuthStore } from '../store/authStore';

export default function ProfileScreen() {
  const navigation = useNavigation();
  const user = useAuthStore((state) => state.user);
  const logout = useAuthStore((state) => state.logout);

  const handleLogout = () => {
    Alert.alert(
      'Déconnexion',
      'Êtes-vous sûr de vouloir vous déconnecter ?',
      [
        { text: 'Annuler', style: 'cancel' },
        { 
          text: 'Déconnexion', 
          style: 'destructive',
          onPress: () => logout()
        },
      ]
    );
  };

  const menuItems = [
    {
      icon: 'account-edit',
      label: 'Modifier mon profil',
      onPress: () => {},
    },
    {
      icon: 'bell-outline',
      label: 'Notifications',
      onPress: () => {},
    },
    {
      icon: 'shield-check',
      label: 'Confidentialité',
      onPress: () => {},
    },
    {
      icon: 'help-circle-outline',
      label: 'Aide & Support',
      onPress: () => {},
    },
    {
      icon: 'information-outline',
      label: 'À propos',
      onPress: () => {},
    },
  ];

  return (
    <ScrollView style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.title}>Profil</Text>
      </View>

      {/* User Card */}
      <Surface style={styles.userCard}>
        <Avatar.Text
          size={80}
          label={`${user?.firstName?.[0] || ''}${user?.lastName?.[0] || ''}`}
          style={styles.avatar}
          labelStyle={styles.avatarLabel}
        />
        <Text style={styles.userName}>
          {user?.firstName} {user?.lastName}
        </Text>
        <Text style={styles.userEmail}>{user?.email}</Text>
        {user?.company && (
          <View style={styles.companyBadge}>
            <MaterialCommunityIcons name="office-building" size={16} color={colors.primary} />
            <Text style={styles.companyText}>{user.company}</Text>
          </View>
        )}
      </Surface>

      {/* Stats */}
      <View style={styles.statsContainer}>
        <Surface style={styles.statCard}>
          <MaterialCommunityIcons name="file-check" size={24} color={colors.primary} />
          <Text style={styles.statValue}>12</Text>
          <Text style={styles.statLabel}>Devis analysés</Text>
        </Surface>
        
        <Surface style={styles.statCard}>
          <MaterialCommunityIcons name="cash-multiple" size={24} color={colors.success} />
          <Text style={styles.statValue}>2.4k€</Text>
          <Text style={styles.statLabel}>Économisés</Text>
        </Surface>
        
        <Surface style={styles.statCard}>
          <MaterialCommunityIcons name="trending-up" size={24} color={colors.warning} />
          <Text style={styles.statValue}>85%</Text>
          <Text style={styles.statLabel}>Taux de confiance</Text>
        </Surface>
      </View>

      {/* Menu */}
      <Surface style={styles.menuCard}>
        {menuItems.map((item, index) => (
          <TouchableOpacity key={index} onPress={item.onPress}>
            <View style={styles.menuItem}>
              <View style={styles.menuItemLeft}>
                <MaterialCommunityIcons
                  name={item.icon as any}
                  size={24}
                  color={colors.textSecondary}
                />
                <Text style={styles.menuItemLabel}>{item.label}</Text>
              </View>
              <MaterialCommunityIcons
                name="chevron-right"
                size={24}
                color={colors.textTertiary}
              />
            </View>
            {index < menuItems.length - 1 && <Divider style={styles.divider} />}
          </TouchableOpacity>
        ))}
      </Surface>

      {/* Logout */}
      <Button
        mode="outlined"
        onPress={handleLogout}
        style={styles.logoutButton}
        icon="logout"
        textColor={colors.error}
      >
        Se déconnecter
      </Button>

      {/* Version */}
      <Text style={styles.version}>TrustDevis v1.0.0</Text>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
  },
  header: {
    padding: spacing.md,
    paddingTop: spacing.xl,
  },
  title: {
    ...typography.h2,
    color: colors.textPrimary,
  },
  userCard: {
    margin: spacing.md,
    padding: spacing.lg,
    borderRadius: 16,
    alignItems: 'center',
    ...shadows.medium,
  },
  avatar: {
    backgroundColor: colors.primary,
  },
  avatarLabel: {
    ...typography.h2,
    color: '#fff',
  },
  userName: {
    ...typography.h3,
    color: colors.textPrimary,
    marginTop: spacing.md,
  },
  userEmail: {
    ...typography.body,
    color: colors.textSecondary,
    marginTop: spacing.xs,
  },
  companyBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: colors.primaryLight,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.xs,
    borderRadius: 16,
    marginTop: spacing.sm,
  },
  companyText: {
    ...typography.bodySmall,
    color: colors.primary,
    marginLeft: spacing.xs,
    fontWeight: '600',
  },
  statsContainer: {
    flexDirection: 'row',
    paddingHorizontal: spacing.md,
    gap: spacing.sm,
  },
  statCard: {
    flex: 1,
    padding: spacing.md,
    borderRadius: 12,
    alignItems: 'center',
    ...shadows.small,
  },
  statValue: {
    ...typography.h3,
    color: colors.textPrimary,
    marginTop: spacing.xs,
  },
  statLabel: {
    ...typography.caption,
    color: colors.textSecondary,
    textAlign: 'center',
    marginTop: 2,
  },
  menuCard: {
    margin: spacing.md,
    borderRadius: 12,
    ...shadows.small,
  },
  menuItem: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: spacing.md,
  },
  menuItemLeft: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  menuItemLabel: {
    ...typography.body,
    color: colors.textPrimary,
    marginLeft: spacing.md,
  },
  divider: {
    backgroundColor: colors.border,
    marginHorizontal: spacing.md,
  },
  logoutButton: {
    margin: spacing.md,
    marginTop: spacing.lg,
    borderColor: colors.error,
    borderRadius: 8,
  },
  version: {
    ...typography.caption,
    color: colors.textTertiary,
    textAlign: 'center',
    marginBottom: spacing.xl,
  },
});
