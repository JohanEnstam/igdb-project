'use client';

import { useState } from 'react';
import { GameSearch } from '@/components/GameSearch';
import { GameCard } from '@/components/GameCard';
import { RecommendationList } from '@/components/RecommendationList';
import { GameInfo } from '@/lib/types';

export default function Home() {
  const [selectedGame, setSelectedGame] = useState<GameInfo | null>(null);

  const handleGameSelect = (game: GameInfo) => {
    setSelectedGame(game);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-slate-900 dark:text-slate-100 mb-4">
            Upptäck Ditt Nästa Spel
          </h1>
          <p className="text-lg text-slate-600 dark:text-slate-400 max-w-2xl mx-auto">
            Hitta spel du kommer att älska med AI-drivna rekommendationer baserade på dina preferenser
          </p>
        </div>

        {/* Search Section */}
        <div className="flex justify-center mb-8">
          <GameSearch
            onGameSelect={handleGameSelect}
            placeholder="Search for a game you like..."
            className="w-full max-w-2xl"
          />
        </div>

        {/* Results Section */}
        {selectedGame && (
          <div className="max-w-6xl mx-auto">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              {/* Selected Game */}
              <div className="space-y-4">
                <h2 className="text-2xl font-semibold text-slate-900 dark:text-slate-100">
                  Selected Game
                </h2>
                <GameCard
                  game={selectedGame}
                  className="w-full"
                />
              </div>

              {/* Recommendations */}
              <div className="space-y-4">
                <h2 className="text-2xl font-semibold text-slate-900 dark:text-slate-100">
                  Recommendations
                </h2>
                <RecommendationList
                  gameId={selectedGame.id}
                  topK={8}
                  className="w-full"
                />
              </div>
            </div>
          </div>
        )}

        {/* Instructions */}
        {!selectedGame && (
          <div className="max-w-2xl mx-auto text-center">
            <div className="bg-white dark:bg-slate-800 rounded-lg p-8 shadow-sm border">
              <h3 className="text-xl font-semibold text-slate-900 dark:text-slate-100 mb-4">
                How it works
              </h3>
              <div className="space-y-4 text-left">
                <div className="flex items-start gap-3">
                  <div className="flex-shrink-0 w-6 h-6 bg-primary text-primary-foreground rounded-full flex items-center justify-center text-sm font-medium">
                    1
                  </div>
                  <p className="text-slate-600 dark:text-slate-400">
                    Search for a game you like using the search box above
                  </p>
                </div>
                <div className="flex items-start gap-3">
                  <div className="flex-shrink-0 w-6 h-6 bg-primary text-primary-foreground rounded-full flex items-center justify-center text-sm font-medium">
                    2
                  </div>
                  <p className="text-slate-600 dark:text-slate-400">
                    Select the game from the autocomplete suggestions
                  </p>
                </div>
                <div className="flex items-start gap-3">
                  <div className="flex-shrink-0 w-6 h-6 bg-primary text-primary-foreground rounded-full flex items-center justify-center text-sm font-medium">
                    3
                  </div>
                  <p className="text-slate-600 dark:text-slate-400">
                    Discover similar games you might enjoy based on our AI recommendations
                  </p>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
