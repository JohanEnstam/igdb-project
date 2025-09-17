/**
 * GameCard component for displaying game information
 */

'use client';

import { Star, Calendar } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { GameCardProps } from '@/lib/types';

export function GameCard({ game, onClick, className }: GameCardProps) {
  const formatRating = (rating: number) => {
    return rating > 0 ? rating.toFixed(1) : 'N/A';
  };

  const formatReleaseYear = (year: number) => {
    return year > 0 ? year.toString() : 'Unknown';
  };

  const formatRatingCount = (count: number) => {
    if (count >= 1000000) {
      return `${(count / 1000000).toFixed(1)}M`;
    } else if (count >= 1000) {
      return `${(count / 1000).toFixed(1)}K`;
    }
    return count.toString();
  };

  return (
    <Card
      className={`cursor-pointer transition-all duration-200 hover:shadow-lg hover:scale-[1.02] ${className}`}
      onClick={onClick}
    >
      <CardHeader className="pb-3">
        <CardTitle className="text-lg line-clamp-2">{game.name}</CardTitle>
      </CardHeader>

      <CardContent className="space-y-3">
        {/* Game Summary */}
        {game.summary && (
          <p className="text-sm text-muted-foreground line-clamp-3">
            {game.summary}
          </p>
        )}

        {/* Rating and Release Info */}
        <div className="flex items-center gap-4 text-sm">
          <div className="flex items-center gap-1">
            <Star className="h-4 w-4 text-yellow-500" />
            <span className="font-medium">{formatRating(game.rating)}</span>
            {game.rating_count > 0 && (
              <span className="text-muted-foreground">
                ({formatRatingCount(game.rating_count)})
              </span>
            )}
          </div>

          <div className="flex items-center gap-1">
            <Calendar className="h-4 w-4 text-muted-foreground" />
            <span className="text-muted-foreground">
              {formatReleaseYear(game.release_year)}
            </span>
          </div>
        </div>

        {/* Genres */}
        {game.genre_names.length > 0 && (
          <div className="space-y-2">
            <h4 className="text-sm font-medium">Genres</h4>
            <div className="flex flex-wrap gap-1">
              {game.genre_names.slice(0, 4).map((genre, index) => (
                <span
                  key={`${genre}-${index}`}
                  className="text-xs bg-secondary px-2 py-1 rounded-full"
                >
                  {genre}
                </span>
              ))}
              {game.genre_names.length > 4 && (
                <span className="text-xs text-muted-foreground">
                  +{game.genre_names.length - 4} more
                </span>
              )}
            </div>
          </div>
        )}

        {/* Platforms */}
        {game.platform_names.length > 0 && (
          <div className="space-y-2">
            <h4 className="text-sm font-medium">Platforms</h4>
            <div className="flex flex-wrap gap-1">
              {game.platform_names.slice(0, 3).map((platform, index) => (
                <span
                  key={`${platform}-${index}`}
                  className="text-xs bg-primary/10 text-primary px-2 py-1 rounded-full"
                >
                  {platform}
                </span>
              ))}
              {game.platform_names.length > 3 && (
                <span className="text-xs text-muted-foreground">
                  +{game.platform_names.length - 3} more
                </span>
              )}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
