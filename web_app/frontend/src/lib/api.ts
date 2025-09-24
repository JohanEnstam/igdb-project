/**
 * API client for the IGDB Game Recommendation System
 */

import { 
  GameInfo, 
  GameRecommendation, 
  TextRecommendationRequest,
  HealthStatus,
  ModelStatus,
  APIError 
} from './types';

class GameAPI {
  private baseURL: string;

  constructor(baseURL?: string) {
    // Use environment variable in production, fallback to staging API for production
    this.baseURL = baseURL || process.env.NEXT_PUBLIC_API_URL || 'https://igdb-api-staging-d6xpjrmqsa-ew.a.run.app';
  }

  private async request<T>(endpoint: string, options?: RequestInit): Promise<T> {
    const url = `${this.baseURL}${endpoint}`;
    
    try {
      const response = await fetch(url, {
        headers: {
          'Content-Type': 'application/json',
          ...options?.headers,
        },
        ...options,
      });

      if (!response.ok) {
        const errorData: APIError = await response.json();
        throw new Error(errorData.detail || `HTTP ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error(`API request failed for ${endpoint}:`, error);
      throw error;
    }
  }

  /**
   * Search for games by name or summary
   */
  async searchGames(query: string, limit: number = 20): Promise<GameInfo[]> {
    const params = new URLSearchParams({
      query,
      limit: limit.toString(),
    });
    
    return this.request<GameInfo[]>(`/games/search?${params}`);
  }

  /**
   * Get detailed information about a specific game
   */
  async getGameInfo(gameId: number): Promise<GameInfo> {
    return this.request<GameInfo>(`/games/${gameId}`);
  }

  /**
   * Get recommendations for a specific game
   */
  async getRecommendations(gameId: number, topK: number = 10): Promise<GameRecommendation[]> {
    const params = new URLSearchParams({
      top_k: topK.toString(),
    });
    
    return this.request<GameRecommendation[]>(`/games/${gameId}/recommendations?${params}`);
  }

  /**
   * Get text-based recommendations
   */
  async getTextRecommendations(request: TextRecommendationRequest): Promise<GameRecommendation[]> {
    return this.request<GameRecommendation[]>('/recommendations/text', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  /**
   * Get list of all available genres
   */
  async getGenres(): Promise<string[]> {
    return this.request<string[]>('/genres');
  }

  /**
   * Get list of all available platforms
   */
  async getPlatforms(): Promise<string[]> {
    return this.request<string[]>('/platforms');
  }

  /**
   * Get model status information
   */
  async getModelStatus(): Promise<ModelStatus> {
    return this.request<ModelStatus>('/model/status');
  }

  /**
   * Get system health status
   */
  async getHealthStatus(): Promise<HealthStatus> {
    return this.request<HealthStatus>('/health');
  }

  /**
   * List games with pagination
   */
  async listGames(limit: number = 50, offset: number = 0): Promise<GameInfo[]> {
    const params = new URLSearchParams({
      limit: limit.toString(),
      offset: offset.toString(),
    });
    
    return this.request<GameInfo[]>(`/games?${params}`);
  }
}

// Create and export a singleton instance
export const gameAPI = new GameAPI();

// Export the class for testing or custom instances
export { GameAPI };
