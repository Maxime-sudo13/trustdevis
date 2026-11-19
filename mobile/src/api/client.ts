import axios from 'axios';
import * as SecureStore from 'expo-secure-store';

const API_URL = process.env.API_URL || 'https://api.trustdevis.com';

const apiClient = axios.create({
  baseURL: API_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Intercepteur pour ajouter le token
apiClient.interceptors.request.use(
  async (config) => {
    const token = await SecureStore.getItemAsync('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Intercepteur pour gérer les erreurs
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      // Token expiré, déconnecter l'utilisateur
      await SecureStore.deleteItemAsync('auth_token');
      // Redirection vers login gérée par le store
    }
    return Promise.reject(error);
  }
);

export default apiClient;
