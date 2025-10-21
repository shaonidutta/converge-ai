/**
 * useRateCards Hook
 * Custom hooks for fetching and managing rate card data
 */

import { useState, useEffect, useCallback } from 'react';
import { fetchRateCards } from '../services/subcategoryService';

/**
 * Hook to fetch rate cards for a subcategory
 * @param {number} subcategoryId - Subcategory ID
 * @returns {object} { rateCards, loading, error, refetch }
 */
export const useRateCards = (subcategoryId) => {
  const [rateCards, setRateCards] = useState([]);
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
      const data = await fetchRateCards(subcategoryId);
      setRateCards(data);
    } catch (err) {
      setError(err.message);
      console.error('Error in useRateCards:', err);
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
    rateCards,
    loading,
    error,
    refetch,
  };
};

/**
 * Hook to fetch a single rate card by ID
 * Note: Backend doesn't have direct endpoint, so we filter from list
 * @param {number} rateCardId - Rate card ID
 * @param {number} subcategoryId - Subcategory ID (required to fetch list)
 * @returns {object} { rateCard, loading, error, refetch }
 */
export const useRateCard = (rateCardId, subcategoryId) => {
  const [rateCard, setRateCard] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchData = useCallback(async () => {
    if (!rateCardId || !subcategoryId) {
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      setError(null);
      const data = await fetchRateCards(subcategoryId);
      const found = data.find(card => card.id === rateCardId);
      setRateCard(found || null);
    } catch (err) {
      setError(err.message);
      console.error('Error in useRateCard:', err);
    } finally {
      setLoading(false);
    }
  }, [rateCardId, subcategoryId]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const refetch = useCallback(() => {
    fetchData();
  }, [fetchData]);

  return {
    rateCard,
    loading,
    error,
    refetch,
  };
};

export default useRateCards;

