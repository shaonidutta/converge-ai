/**
 * Category Service
 * Handles all category-related API calls
 */

import api from './api';

/**
 * Fetch all service categories
 * @returns {Promise<Array>} List of categories
 */
export const fetchCategories = async () => {
  try {
    const response = await api.categories.getAll();
    return response.data;
  } catch (error) {
    console.error('Error fetching categories:', error);
    throw new Error(error.response?.data?.detail || 'Failed to fetch categories');
  }
};

/**
 * Fetch category by ID
 * @param {number} categoryId - Category ID
 * @returns {Promise<Object>} Category details
 */
export const fetchCategoryById = async (categoryId) => {
  try {
    const response = await api.categories.getById(categoryId);
    return response.data;
  } catch (error) {
    console.error(`Error fetching category ${categoryId}:`, error);
    throw new Error(error.response?.data?.detail || 'Failed to fetch category');
  }
};

/**
 * Fetch subcategories for a category
 * @param {number} categoryId - Category ID
 * @returns {Promise<Array>} List of subcategories
 */
export const fetchSubcategories = async (categoryId) => {
  try {
    const response = await api.categories.getSubcategories(categoryId);
    return response.data;
  } catch (error) {
    console.error(`Error fetching subcategories for category ${categoryId}:`, error);
    throw new Error(error.response?.data?.detail || 'Failed to fetch subcategories');
  }
};

/**
 * Fetch rate cards for a subcategory
 * @param {number} subcategoryId - Subcategory ID
 * @returns {Promise<Array>} List of rate cards
 */
export const fetchRateCards = async (subcategoryId) => {
  try {
    const response = await api.categories.getRateCards(subcategoryId);
    return response.data;
  } catch (error) {
    console.error(`Error fetching rate cards for subcategory ${subcategoryId}:`, error);
    throw new Error(error.response?.data?.detail || 'Failed to fetch rate cards');
  }
};

/**
 * Search services by query
 * @param {string} query - Search query
 * @returns {Promise<Array>} Filtered categories
 */
export const searchServices = async (query) => {
  try {
    // Fetch all categories and filter client-side
    // TODO: Replace with backend search endpoint when available
    const response = await api.categories.getAll();
    const categories = response.data;
    
    if (!query || query.trim() === '') {
      return categories;
    }
    
    const lowerQuery = query.toLowerCase().trim();
    
    // Filter categories by name or description
    return categories.filter(category => 
      category.name.toLowerCase().includes(lowerQuery) ||
      (category.description && category.description.toLowerCase().includes(lowerQuery))
    );
  } catch (error) {
    console.error('Error searching services:', error);
    throw new Error(error.response?.data?.detail || 'Failed to search services');
  }
};

/**
 * Export all category service functions
 */
export default {
  fetchCategories,
  fetchCategoryById,
  fetchSubcategories,
  fetchRateCards,
  searchServices,
};

