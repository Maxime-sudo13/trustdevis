import apiClient from '../api/client';
import { AnalysisResult } from '../store/analysisStore';

export interface UploadResponse {
  analysisId: string;
  status: 'pending' | 'processing';
}

export interface AnalysisResponse extends AnalysisResult {}

export const analysisService = {
  async uploadImage(imageUri: string): Promise<UploadResponse> {
    const formData = new FormData();
    
    // Créer le fichier à partir de l'URI
    const filename = imageUri.split('/').pop() || 'image.jpg';
    const match = /\.([a-zA-Z]+)$/.exec(filename);
    const type = match ? `image/${match[1]}` : 'image/jpeg';
    
    formData.append('image', {
      uri: imageUri,
      name: filename,
      type,
    } as any);

    const response = await apiClient.post<UploadResponse>('/analysis/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      timeout: 60000, // 60s pour l'upload
    });
    
    return response.data;
  },

  async getAnalysis(analysisId: string): Promise<AnalysisResponse> {
    const response = await apiClient.get<AnalysisResponse>(`/analysis/${analysisId}`);
    return response.data;
  },

  async getHistory(): Promise<AnalysisResponse[]> {
    const response = await apiClient.get<AnalysisResponse[]>('/analysis/history');
    return response.data;
  },

  async deleteAnalysis(analysisId: string): Promise<void> {
    await apiClient.delete(`/analysis/${analysisId}`);
  },

  async pollAnalysisStatus(
    analysisId: string,
    onUpdate: (analysis: AnalysisResponse) => void,
    onError: (error: Error) => void
  ): Promise<void> {
    const maxAttempts = 60; // 60 tentatives max (2 minutes)
    const interval = 2000; // 2 secondes entre chaque polling
    
    for (let attempt = 0; attempt < maxAttempts; attempt++) {
      try {
        const analysis = await this.getAnalysis(analysisId);
        onUpdate(analysis);
        
        if (analysis.status === 'completed' || analysis.status === 'error') {
          return;
        }
        
        await new Promise((resolve) => setTimeout(resolve, interval));
      } catch (error) {
        onError(error as Error);
        return;
      }
    }
    
    onError(new Error('Timeout: L\'analyse a pris trop de temps'));
  },
};
