/**
 * useCategories Hook
 * Custom hook for fetching and managing service categories
 */

import { useState, useEffect, useCallback } from 'react';
import { fetchCategories, fetchCategoryById, searchServices } from '../services/categoryService';

/**
 * Hook to fetch all categories
 * @returns {Object} { categories, loading, error, refetch }
 */
export const useCategories = () => {
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const loadCategories = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await fetchCategories();
      setCategories(data);
    } catch (err) {
      setError(err.message);
      console.error('Error loading categories:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadCategories();
  }, [loadCategories]);

  const refetch = useCallback(() => {
    loadCategories();
  }, [loadCategories]);

  return { categories, loading, error, refetch };
};

/**
 * Hook to fetch a single category by ID
 * @param {number} categoryId - Category ID
 * @returns {Object} { category, loading, error, refetch }
 */
export const useCategory = (categoryId) => {
  const [category, setCategory] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const loadCategory = useCallback(async () => {
    if (!categoryId) {
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      setError(null);
      const data = await fetchCategoryById(categoryId);
      setCategory(data);
    } catch (err) {
      setError(err.message);
      console.error(`Error loading category ${categoryId}:`, err);
    } finally {
      setLoading(false);
    }
  }, [categoryId]);

  useEffect(() => {
    loadCategory();
  }, [loadCategory]);

  const refetch = useCallback(() => {
    loadCategory();
  }, [loadCategory]);

  return { category, loading, error, refetch };
};

/**
 * Hook to search services
 * @param {string} initialQuery - Initial search query
 * @returns {Object} { results, loading, error, search }
 */
export const useServiceSearch = (initialQuery = '') => {
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [query, setQuery] = useState(initialQuery);

  const search = useCallback(async (searchQuery) => {
    try {
      setLoading(true);
      setError(null);
      setQuery(searchQuery);
      const data = await searchServices(searchQuery);
      setResults(data);
    } catch (err) {
      setError(err.message);
      console.error('Error searching services:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (initialQuery) {
      search(initialQuery);
    }
  }, [initialQuery, search]);

  return { results, loading, error, query, search };
};

/**
 * Export all hooks
 */
export default {
  useCategories,
  useCategory,
  useServiceSearch,
};

