import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import AsyncStorage from '@react-native-async-storage/async-storage';

export type TrustLevel = 'high' | 'medium' | 'low' | 'unknown';

export interface AnalysisResult {
  id: string;
  imageUri: string;
  createdAt: string;
  status: 'pending' | 'processing' | 'completed' | 'error';
  
  // Données extraites
  extractedData?: {
    companyName?: string;
    totalAmount?: number;
    date?: string;
    items?: Array<{
      description: string;
      quantity: number;
      unitPrice: number;
      total: number;
    }>;
  };
  
  // Score de confiance
  trustScore?: {
    level: TrustLevel;
    score: number;
    reasons: string[];
  };
  
  // Comparaison marché
  marketComparison?: {
    averagePrice: number;
    priceRange: { min: number; max: number };
    comparison: 'below' | 'within' | 'above';
    savings?: number;
    excess?: number;
  };
  
  // Recommandations
  recommendations?: string[];
  
  // Erreur
  error?: string;
}

interface AnalysisState {
  analyses: AnalysisResult[];
  currentAnalysis: AnalysisResult | null;
  isUploading: boolean;
  uploadProgress: number;
  
  // Actions
  addAnalysis: (analysis: AnalysisResult) => void;
  updateAnalysis: (id: string, updates: Partial<AnalysisResult>) => void;
  setCurrentAnalysis: (analysis: AnalysisResult | null) => void;
  deleteAnalysis: (id: string) => void;
  setUploading: (isUploading: boolean) => void;
  setUploadProgress: (progress: number) => void;
  getAnalysisById: (id: string) => AnalysisResult | undefined;
}

export const useAnalysisStore = create<AnalysisState>()(
  persist(
    (set, get) => ({
      analyses: [],
      currentAnalysis: null,
      isUploading: false,
      uploadProgress: 0,

      addAnalysis: (analysis) => {
        set((state) => ({
          analyses: [analysis, ...state.analyses],
        }));
      },

      updateAnalysis: (id, updates) => {
        set((state) => ({
          analyses: state.analyses.map((a) =>
            a.id === id ? { ...a, ...updates } : a
          ),
          currentAnalysis:
            state.currentAnalysis?.id === id
              ? { ...state.currentAnalysis, ...updates }
              : state.currentAnalysis,
        }));
      },

      setCurrentAnalysis: (analysis) => {
        set({ currentAnalysis: analysis });
      },

      deleteAnalysis: (id) => {
        set((state) => ({
          analyses: state.analyses.filter((a) => a.id !== id),
          currentAnalysis:
            state.currentAnalysis?.id === id ? null : state.currentAnalysis,
        }));
      },

      setUploading: (isUploading) => set({ isUploading }),
      setUploadProgress: (uploadProgress) => set({ uploadProgress }),

      getAnalysisById: (id) => {
        return get().analyses.find((a) => a.id === id);
      },
    }),
    {
      name: 'analysis-storage',
      storage: createJSONStorage(() => AsyncStorage),
    }
  )
);
