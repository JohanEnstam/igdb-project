/**
 * TypeScript type definitions for the IGDB Game Recommendation System
 */

export interface GameInfo {
  id: number;
  name: string;
  summary: string;
  rating: number;
  rating_count: number;
  release_date: string;
  release_year: number;
  genre_names: string[];
  platform_names: string[];
  theme_names: string[];
}

export interface GameRecommendation {
  game_id: number;
  name: string;
  similarity_score: number;
  rating?: number;
  genres?: string[];
  platforms?: string[];
  summary?: string;
}

export interface TextRecommendationRequest {
  query: string;
  top_k: number;
}

export interface GameSearchRequest {
  query: string;
  limit: number;
}

export interface ModelStatus {
  is_loaded: boolean;
  games_count: number;
  feature_count: number;
}

export interface HealthStatus {
  status: string;
  model_loaded: string;
  games_count: string;
  port: string;
  gcs_available?: string;
  data_accessible?: string;
  models_accessible?: string;
}

// API Error types
export interface APIError {
  detail: string;
  status_code?: number;
}

// Component prop types
export interface GameSearchProps {
  onGameSelect: (game: GameInfo) => void;
  placeholder?: string;
  className?: string;
}

export interface GameCardProps {
  game: GameInfo;
  onClick?: () => void;
  showRecommendations?: boolean;
  className?: string;
}

export interface RecommendationListProps {
  gameId: number;
  topK?: number;
  className?: string;
}

export interface TextRecommendationProps {
  onRecommendations: (recommendations: GameRecommendation[]) => void;
  className?: string;
}
