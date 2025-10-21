/**
 * useSubcategories Hook
 * Custom hooks for fetching and managing subcategory data
 */

import { useState, useEffect, useCallback } from 'react';
import { fetchSubcategories, fetchSubcategoryById } from '../services/subcategoryService';

/**
 * Hook to fetch subcategories for a category
 * @param {number} categoryId - Category ID
 * @returns {object} { subcategories, loading, error, refetch }
 */
export const useSubcategories = (categoryId) => {
  const [subcategories, setSubcategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchData = useCallback(async () => {
    if (!categoryId) {
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      setError(null);
      const data = await fetchSubcategories(categoryId);
      setSubcategories(data);
    } catch (err) {
      setError(err.message);
      console.error('Error in useSubcategories:', err);
    } finally {
      setLoading(false);
    }
  }, [categoryId]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const refetch = useCallback(() => {
    fetchData();
  }, [fetchData]);

  return {
    subcategories,
    loading,
    error,
    refetch,
  };
};

/**
 * Hook to fetch a single subcategory by ID
 * Note: Since backend doesn't have direct endpoint, this returns null
 * Components should get subcategory from the list instead
 * @param {number} subcategoryId - Subcategory ID
 * @returns {object} { subcategory, loading, error, refetch }
 */
export const useSubcategory = (subcategoryId) => {
  const [subcategory, setSubcategory] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchData = useCallback(async () => {
    if (!subcategoryId) {
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      setError(null);
      const data = await fetchSubcategoryById(subcategoryId);
      setSubcategory(data);
    } catch (err) {
      setError(err.message);
      console.error('Error in useSubcategory:', err);
    } finally {
      setLoading(false);
    }
  }, [subcategoryId]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const refetch = useCallback(() => {
    fetchData();
  }, [fetchData]);

  return {
    subcategory,
    loading,
    error,
    refetch,
  };
};

export default useSubcategories;

