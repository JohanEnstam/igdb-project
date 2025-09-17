/**
 * RecommendationList component for displaying game recommendations
 */

'use client';

import { useState, useEffect } from 'react';
import { Loader2, Star } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { GameRecommendation, RecommendationListProps } from '@/lib/types';
import { gameAPI } from '@/lib/api';

export function RecommendationList({ gameId, topK = 10, className }: RecommendationListProps) {
  const [recommendations, setRecommendations] = useState<GameRecommendation[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchRecommendations = async () => {
      if (!gameId) return;

      setIsLoading(true);
      setError(null);

      try {
        const results = await gameAPI.getRecommendations(gameId, topK);
        setRecommendations(results);
      } catch (err) {
        console.error('Failed to fetch recommendations:', err);
        setError(err instanceof Error ? err.message : 'Failed to load recommendations');
      } finally {
        setIsLoading(false);
      }
    };

    fetchRecommendations();
  }, [gameId, topK]);

  const formatSimilarityScore = (score: number) => {
    return (score * 100).toFixed(0);
  };

  const formatRating = (rating?: number) => {
    return rating && rating > 0 ? rating.toFixed(1) : 'N/A';
  };

  if (isLoading) {
    return (
      <Card className={className}>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Loader2 className="h-5 w-5 animate-spin" />
            Loading Recommendations...
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8 text-muted-foreground">
            Finding similar games for you...
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card className={className}>
        <CardHeader>
          <CardTitle>Recommendations</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8">
            <p className="text-destructive mb-2">Failed to load recommendations</p>
            <p className="text-sm text-muted-foreground">{error}</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (recommendations.length === 0) {
    return (
      <Card className={className}>
        <CardHeader>
          <CardTitle>Recommendations</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8 text-muted-foreground">
            No recommendations found for this game.
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className={className}>
      <CardHeader>
        <CardTitle>Similar Games</CardTitle>
        <p className="text-sm text-muted-foreground">
          Games you might also enjoy
        </p>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {recommendations.map((rec) => (
            <div
              key={rec.game_id}
              className="flex items-start gap-3 p-3 rounded-lg border hover:bg-muted/50 transition-colors cursor-pointer"
            >
              {/* Similarity Score */}
              <div className="flex-shrink-0 w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center">
                <span className="text-sm font-bold text-primary">
                  {formatSimilarityScore(rec.similarity_score)}%
                </span>
              </div>

              {/* Game Info */}
              <div className="flex-1 min-w-0">
                <h4 className="font-medium text-sm line-clamp-1">{rec.name}</h4>

                {rec.summary && (
                  <p className="text-xs text-muted-foreground line-clamp-2 mt-1">
                    {rec.summary}
                  </p>
                )}

                {/* Rating and Genres */}
                <div className="flex items-center gap-3 mt-2">
                  {rec.rating && rec.rating > 0 && (
                    <div className="flex items-center gap-1">
                      <Star className="h-3 w-3 text-yellow-500" />
                      <span className="text-xs font-medium">{formatRating(rec.rating)}</span>
                    </div>
                  )}

                  {rec.genres && rec.genres.length > 0 && (
                    <div className="flex gap-1">
                      {rec.genres.slice(0, 2).map((genre, index) => (
                        <span
                          key={`${genre}-${index}`}
                          className="text-xs bg-secondary px-2 py-1 rounded-full"
                        >
                          {genre}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
