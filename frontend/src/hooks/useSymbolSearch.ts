import { useState, useEffect, useCallback } from 'react';
import { marketDataService, SymbolSearchResult } from '../services/marketDataService';

interface UseSymbolSearchReturn {
  searchResults: SymbolSearchResult[];
  isSearching: boolean;
  searchError: string | null;
  hasSearched: boolean;
}

export const useSymbolSearch = (query: string, debounceMs: number = 300): UseSymbolSearchReturn => {
  const [searchResults, setSearchResults] = useState<SymbolSearchResult[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [searchError, setSearchError] = useState<string | null>(null);
  const [hasSearched, setHasSearched] = useState(false);

  const performSearch = useCallback(async (searchQuery: string) => {
    if (!searchQuery.trim()) {
      setSearchResults([]);
      setSearchError(null);
      setHasSearched(false);
      return;
    }

    setIsSearching(true);
    setSearchError(null);

    try {
      const response = await marketDataService.searchSymbols(searchQuery.trim(), 10);
      setSearchResults(response.results);
      setHasSearched(true);
    } catch (error) {
      console.error('Symbol search error:', error);
      setSearchError('Failed to search symbols');
      setSearchResults([]);
      setHasSearched(true);
    } finally {
      setIsSearching(false);
    }
  }, []);

  useEffect(() => {
    const timer = setTimeout(() => {
      performSearch(query);
    }, debounceMs);

    return () => clearTimeout(timer);
  }, [query, debounceMs, performSearch]);

  return {
    searchResults,
    isSearching,
    searchError,
    hasSearched
  };
};