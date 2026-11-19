import React, { useState } from 'react';
import { View, StyleSheet, ScrollView, KeyboardAvoidingView, Platform } from 'react-native';
import { Text, TextInput, Button, Surface, Checkbox } from 'react-native-paper';
import { MaterialCommunityIcons } from '@expo/vector-icons';
import { useNavigation } from '@react-navigation/native';
import { StackNavigationProp } from '@react-navigation/stack';
import Animated, { FadeIn, FadeInUp } from 'react-native-reanimated';

import { RootStackParamList } from '../navigation';
import { colors, spacing, typography, shadows } from '../theme';
import { useAuthStore } from '../store/authStore';

type RegisterScreenNavigationProp = StackNavigationProp<RootStackParamList>;

export default function RegisterScreen() {
  const navigation = useNavigation<RegisterScreenNavigationProp>();
  const register = useAuthStore((state) => state.register);
  const isLoading = useAuthStore((state) => state.isLoading);
  const error = useAuthStore((state) => state.error);
  const clearError = useAuthStore((state) => state.clearError);

  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [email, setEmail] = useState('');
  const [company, setCompany] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [acceptTerms, setAcceptTerms] = useState(false);

  const handleRegister = async () => {
    if (password !== confirmPassword) {
      return;
    }
    if (!acceptTerms) {
      return;
    }
    try {
      await register({
        firstName,
        lastName,
        email,
        password,
        company: company || undefined,
      });
    } catch (error) {
      // Error handled by store
    }
  };

  const isValid = 
    firstName && 
    lastName && 
    email && 
    password && 
    password === confirmPassword && 
    acceptTerms;

  return (
    <KeyboardAvoidingView
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      style={styles.container}
    >
      <ScrollView contentContainerStyle={styles.scrollContent}>
        {/* Header */}
        <Animated.View entering={FadeIn} style={styles.header}>
          <MaterialCommunityIcons name="arrow-left" size={28} color={colors.textPrimary} onPress={() => navigation.goBack()} />
          <Text style={styles.title}>Créer un compte</Text>
          <View style={{ width: 28 }} />
        </Animated.View>

        {/* Form */}
        <Animated.View entering={FadeInUp.delay(100)}>
          <Surface style={styles.formCard}>
            {error && (
              <View style={styles.errorContainer}>
                <MaterialCommunityIcons name="alert-circle" size={20} color={colors.error} />
                <Text style={styles.errorText}>{error}</Text>
              </View>
            )}

            <View style={styles.nameRow}>
              <TextInput
                label="Prénom"
                value={firstName}
                onChangeText={(text) => {
                  setFirstName(text);
                  clearError();
                }}
                style={[styles.input, styles.nameInput]}
              />
              <TextInput
                label="Nom"
                value={lastName}
                onChangeText={(text) => {
                  setLastName(text);
                  clearError();
                }}
                style={[styles.input, styles.nameInput]}
              />
            </View>

            <TextInput
              label="Email"
              value={email}
              onChangeText={(text) => {
                setEmail(text);
                clearError();
              }}
              autoCapitalize="none"
              keyboardType="email-address"
              style={styles.input}
              left={<TextInput.Icon icon="email" />}
            />

            <TextInput
              label="Entreprise (optionnel)"
              value={company}
              onChangeText={(text) => {
                setCompany(text);
                clearError();
              }}
              style={styles.input}
              left={<TextInput.Icon icon="office-building" />}
            />

            <TextInput
              label="Mot de passe"
              value={password}
              onChangeText={(text) => {
                setPassword(text);
                clearError();
              }}
              secureTextEntry={!showPassword}
              style={styles.input}
              left={<TextInput.Icon icon="lock" />}
              right={
                <TextInput.Icon
                  icon={showPassword ? 'eye-off' : 'eye'}
                  onPress={() => setShowPassword(!showPassword)}
                />
              }
            />

            <TextInput
              label="Confirmer le mot de passe"
              value={confirmPassword}
              onChangeText={(text) => {
                setConfirmPassword(text);
                clearError();
              }}
              secureTextEntry={!showPassword}
              style={styles.input}
              left={<TextInput.Icon icon="lock-check" />}
            />

            {password && confirmPassword && password !== confirmPassword && (
              <Text style={styles.passwordError}>Les mots de passe ne correspondent pas</Text>
            )}

            <View style={styles.termsContainer}>
              <Checkbox
                status={acceptTerms ? 'checked' : 'unchecked'}
                onPress={() => setAcceptTerms(!acceptTerms)}
              />
              <Text style={styles.termsText}>
                J'accepte les <Text style={styles.termsLink}>conditions d'utilisation</Text> et la{' '}
                <Text style={styles.termsLink}>politique de confidentialité</Text>
              </Text>
            </View>

            <Button
              mode="contained"
              onPress={handleRegister}
              loading={isLoading}
              disabled={isLoading || !isValid}
              style={styles.registerButton}
              contentStyle={styles.registerButtonContent}
            >
              Créer mon compte
            </Button>
          </Surface>
        </Animated.View>

        {/* Login link */}
        <Animated.View entering={FadeInUp.delay(300)} style={styles.loginContainer}>
          <Text style={styles.loginText}>Déjà un compte ?</Text>
          <Text style={styles.loginLink} onPress={() => navigation.navigate('Login')}>
            Se connecter
          </Text>
        </Animated.View>
      </ScrollView>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
  },
  scrollContent: {
    padding: spacing.lg,
    paddingTop: spacing.xl,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: spacing.lg,
  },
  title: {
    ...typography.h2,
    color: colors.textPrimary,
  },
  formCard: {
    padding: spacing.lg,
    borderRadius: 16,
    ...shadows.medium,
  },
  errorContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: colors.error + '15',
    padding: spacing.md,
    borderRadius: 8,
    marginBottom: spacing.md,
  },
  errorText: {
    ...typography.bodySmall,
    color: colors.error,
    marginLeft: spacing.sm,
    flex: 1,
  },
  nameRow: {
    flexDirection: 'row',
    gap: spacing.sm,
  },
  nameInput: {
    flex: 1,
  },
  input: {
    marginBottom: spacing.md,
    backgroundColor: colors.surface,
  },
  passwordError: {
    ...typography.caption,
    color: colors.error,
    marginBottom: spacing.md,
  },
  termsContainer: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    marginBottom: spacing.md,
  },
  termsText: {
    ...typography.bodySmall,
    color: colors.textSecondary,
    flex: 1,
    marginLeft: spacing.sm,
    marginTop: 6,
  },
  termsLink: {
    color: colors.primary,
    fontWeight: '600',
  },
  registerButton: {
    borderRadius: 8,
  },
  registerButtonContent: {
    paddingVertical: spacing.sm,
  },
  loginContainer: {
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    marginTop: spacing.lg,
  },
  loginText: {
    ...typography.body,
    color: colors.textSecondary,
  },
  loginLink: {
    ...typography.body,
    color: colors.primary,
    fontWeight: '600',
    marginLeft: spacing.xs,
  },
});
