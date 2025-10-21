/**
 * Subcategory Service
 * Handles all subcategory and rate card related API calls
 */

import api from './api';

/**
 * Fetch subcategories for a category
 * @param {number} categoryId - Category ID
 * @param {object} params - Query parameters (skip, limit)
 * @returns {Promise<Array>} Array of subcategory objects
 */
export const fetchSubcategories = async (categoryId, params = {}) => {
  try {
    const response = await api.categories.getSubcategories(categoryId, params);
    return response.data;
  } catch (error) {
    console.error('Error fetching subcategories:', error);
    throw new Error(error.response?.data?.detail || 'Failed to fetch subcategories');
  }
};

/**
 * Fetch single subcategory by ID
 * Note: This endpoint might not exist in backend, so we'll fetch from list
 * @param {number} subcategoryId - Subcategory ID
 * @returns {Promise<object>} Subcategory object
 */
export const fetchSubcategoryById = async (subcategoryId) => {
  try {
    // Since there's no direct endpoint, we'll need to get it from the parent category
    // This is a workaround - ideally backend should have GET /subcategories/:id
    // For now, we'll return null and handle it in the component
    console.warn('fetchSubcategoryById: Direct endpoint not available');
    return null;
  } catch (error) {
    console.error('Error fetching subcategory:', error);
    throw new Error(error.response?.data?.detail || 'Failed to fetch subcategory');
  }
};

/**
 * Fetch rate cards for a subcategory
 * @param {number} subcategoryId - Subcategory ID
 * @param {object} params - Query parameters (skip, limit)
 * @returns {Promise<Array>} Array of rate card objects
 */
export const fetchRateCards = async (subcategoryId, params = {}) => {
  try {
    const response = await api.categories.getRateCards(subcategoryId, params);
    return response.data;
  } catch (error) {
    console.error('Error fetching rate cards:', error);
    throw new Error(error.response?.data?.detail || 'Failed to fetch rate cards');
  }
};

/**
 * Search rate cards within a subcategory
 * @param {number} subcategoryId - Subcategory ID
 * @param {string} query - Search query
 * @returns {Promise<Array>} Array of matching rate cards
 */
export const searchRateCards = async (subcategoryId, query) => {
  try {
    // Fetch all rate cards and filter client-side
    // Ideally, backend should support search parameter
    const rateCards = await fetchRateCards(subcategoryId);
    
    if (!query) return rateCards;
    
    const lowerQuery = query.toLowerCase();
    return rateCards.filter(card => 
      card.name?.toLowerCase().includes(lowerQuery) ||
      card.description?.toLowerCase().includes(lowerQuery)
    );
  } catch (error) {
    console.error('Error searching rate cards:', error);
    throw new Error('Failed to search rate cards');
  }
};

export default {
  fetchSubcategories,
  fetchSubcategoryById,
  fetchRateCards,
  searchRateCards,
};

