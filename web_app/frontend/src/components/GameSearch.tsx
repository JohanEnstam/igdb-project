/**
 * GameSearch component with autocomplete functionality
 */

'use client';

import { useState, useEffect, useRef } from 'react';
import { Search, Loader2 } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { GameInfo, GameSearchProps } from '@/lib/types';
import { gameAPI } from '@/lib/api';
import { useDebounce } from '@/hooks/useDebounce';

export function GameSearch({ onGameSelect, placeholder = "Search for a game...", className }: GameSearchProps) {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<GameInfo[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isOpen, setIsOpen] = useState(false);
  const [selectedIndex, setSelectedIndex] = useState(-1);

  const debouncedQuery = useDebounce(query, 300);
  const inputRef = useRef<HTMLInputElement>(null);
  const resultsRef = useRef<HTMLDivElement>(null);

  // Search for games when debounced query changes
  useEffect(() => {
    if (debouncedQuery.length < 2) {
      setResults([]);
      setIsLoading(false);
      return;
    }

    const searchGames = async () => {
      setIsLoading(true);
      try {
        const searchResults = await gameAPI.searchGames(debouncedQuery, 10);
        setResults(searchResults);
        setSelectedIndex(-1);
      } catch (error) {
        console.error('Search failed:', error);
        setResults([]);
      } finally {
        setIsLoading(false);
      }
    };

    searchGames();
  }, [debouncedQuery]);

  // Handle input change
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setQuery(e.target.value);
    setIsOpen(true);
  };

  // Handle game selection
  const handleGameSelect = (game: GameInfo) => {
    setQuery(game.name);
    setResults([]);
    setIsOpen(false);
    onGameSelect(game);
  };

  // Handle keyboard navigation
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (!isOpen || results.length === 0) return;

    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault();
        setSelectedIndex(prev =>
          prev < results.length - 1 ? prev + 1 : prev
        );
        break;
      case 'ArrowUp':
        e.preventDefault();
        setSelectedIndex(prev => prev > 0 ? prev - 1 : -1);
        break;
      case 'Enter':
        e.preventDefault();
        if (selectedIndex >= 0 && selectedIndex < results.length) {
          handleGameSelect(results[selectedIndex]);
        }
        break;
      case 'Escape':
        setIsOpen(false);
        setSelectedIndex(-1);
        break;
    }
  };

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        resultsRef.current &&
        !resultsRef.current.contains(event.target as Node) &&
        inputRef.current &&
        !inputRef.current.contains(event.target as Node)
      ) {
        setIsOpen(false);
        setSelectedIndex(-1);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  return (
    <div className={`relative w-full max-w-2xl ${className}`}>
      <div className="relative">
        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground h-4 w-4" />
        <Input
          ref={inputRef}
          type="text"
          placeholder={placeholder}
          value={query}
          onChange={handleInputChange}
          onKeyDown={handleKeyDown}
          onFocus={() => setIsOpen(true)}
          className="pl-10 pr-10"
        />
        {isLoading && (
          <Loader2 className="absolute right-3 top-1/2 transform -translate-y-1/2 h-4 w-4 animate-spin text-muted-foreground" />
        )}
      </div>

      {/* Search Results Dropdown */}
      {isOpen && (results.length > 0 || isLoading) && (
        <Card
          ref={resultsRef}
          className="absolute top-full left-0 right-0 mt-1 max-h-80 overflow-y-auto z-50"
        >
          <div className="p-2">
            {isLoading ? (
              <div className="flex items-center justify-center py-4">
                <Loader2 className="h-4 w-4 animate-spin mr-2" />
                <span className="text-sm text-muted-foreground">Searching...</span>
              </div>
            ) : results.length > 0 ? (
              <div className="space-y-1">
                {results.map((game, index) => (
                  <Button
                    key={game.id}
                    variant={selectedIndex === index ? "secondary" : "ghost"}
                    className="w-full justify-start h-auto p-3"
                    onClick={() => handleGameSelect(game)}
                  >
                    <div className="text-left">
                      <div className="font-medium">{game.name}</div>
                      {game.summary && (
                        <div className="text-sm text-muted-foreground line-clamp-2">
                          {game.summary}
                        </div>
                      )}
                      <div className="flex gap-2 mt-1">
                        {game.genre_names.slice(0, 2).map((genre, index) => (
                          <span
                            key={`${genre}-${index}`}
                            className="text-xs bg-secondary px-2 py-1 rounded"
                          >
                            {genre}
                          </span>
                        ))}
                      </div>
                    </div>
                  </Button>
                ))}
              </div>
            ) : query.length >= 2 && (
              <div className="text-center py-4 text-muted-foreground">
                No games found for &quot;{query}&quot;
              </div>
            )}
          </div>
        </Card>
      )}
    </div>
  );
}
