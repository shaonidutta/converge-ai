/**
 * useSearch Hook
 * Custom hook for search functionality
 */

import { useState, useEffect, useCallback } from 'react';
import { searchServices, saveRecentSearch } from '../services/searchService';

/**
 * Hook for searching services
 */
export const useSearch = (initialQuery = '', initialFilters = {}) => {
  const [query, setQuery] = useState(initialQuery);
  const [filters, setFilters] = useState(initialFilters);
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [hasSearched, setHasSearched] = useState(false);

  const performSearch = useCallback(async (searchQuery, searchFilters) => {
    try {
      setLoading(true);
      setError(null);
      setHasSearched(true);
      
      const data = await searchServices(searchQuery, searchFilters);
      setResults(data);
      
      // Save to recent searches if query is not empty
      if (searchQuery && searchQuery.trim()) {
        saveRecentSearch(searchQuery);
      }
    } catch (err) {
      console.error('Search error:', err);
      setError(err.message);
      setResults([]);
    } finally {
      setLoading(false);
    }
  }, []);

  // Perform search when query or filters change
  useEffect(() => {
    if (query || Object.keys(filters).length > 0) {
      performSearch(query, filters);
    }
  }, [query, filters, performSearch]);

  const search = useCallback((newQuery) => {
    setQuery(newQuery);
  }, []);

  const updateFilters = useCallback((newFilters) => {
    setFilters(prev => ({ ...prev, ...newFilters }));
  }, []);

  const clearFilters = useCallback(() => {
    setFilters({});
  }, []);

  const reset = useCallback(() => {
    setQuery('');
    setFilters({});
    setResults([]);
    setHasSearched(false);
    setError(null);
  }, []);

  return {
    query,
    filters,
    results,
    loading,
    error,
    hasSearched,
    search,
    updateFilters,
    clearFilters,
    reset
  };
};

