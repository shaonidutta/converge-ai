/**
 * Search Service
 * Handles search and filtering operations
 */

import api from './api';

/**
 * Search for services
 * @param {string} query - Search query
 * @param {Object} filters - Filter options
 * @returns {Promise<Array>} Search results
 */
export const searchServices = async (query, filters = {}) => {
  try {
    // In production, this would call backend API with query and filters
    // For now, we'll fetch all categories and subcategories and filter client-side
    
    const response = await api.categories.list();
    const categories = response.data || [];
    
    const results = [];
    
    // Search through categories and subcategories
    categories.forEach(category => {
      if (category.subcategories && category.subcategories.length > 0) {
        category.subcategories.forEach(subcategory => {
          // Check if subcategory matches search query
          const matchesQuery = !query || 
            subcategory.name.toLowerCase().includes(query.toLowerCase()) ||
            subcategory.description?.toLowerCase().includes(query.toLowerCase()) ||
            category.name.toLowerCase().includes(query.toLowerCase());
          
          // Apply filters
          const matchesFilters = applyFilters(subcategory, category, filters);
          
          if (matchesQuery && matchesFilters) {
            results.push({
              id: subcategory.id,
              name: subcategory.name,
              description: subcategory.description,
              icon: subcategory.icon,
              category_id: category.id,
              category_name: category.name,
              category_icon: category.icon,
              // Add mock data for filtering
              rating: Math.random() * 2 + 3, // 3-5 rating
              price_range: getPriceRange(),
              is_popular: Math.random() > 0.7,
              is_new: Math.random() > 0.8
            });
          }
        });
      }
    });
    
    // Apply sorting
    if (filters.sort_by) {
      results.sort((a, b) => {
        switch (filters.sort_by) {
          case 'name_asc':
            return a.name.localeCompare(b.name);
          case 'name_desc':
            return b.name.localeCompare(a.name);
          case 'rating_desc':
            return b.rating - a.rating;
          case 'rating_asc':
            return a.rating - b.rating;
          case 'popular':
            return b.is_popular - a.is_popular;
          default:
            return 0;
        }
      });
    }
    
    return results;
  } catch (error) {
    console.error('Error searching services:', error);
    throw new Error('Failed to search services');
  }
};

/**
 * Apply filters to a subcategory
 */
const applyFilters = (subcategory, category, filters) => {
  // Category filter
  if (filters.category_id && category.id !== filters.category_id) {
    return false;
  }
  
  // Price range filter (mock implementation)
  if (filters.price_range) {
    const priceRange = getPriceRange();
    if (priceRange !== filters.price_range) {
      return false;
    }
  }
  
  // Rating filter (mock implementation)
  if (filters.min_rating) {
    const rating = Math.random() * 2 + 3;
    if (rating < filters.min_rating) {
      return false;
    }
  }
  
  return true;
};

/**
 * Get random price range for mock data
 */
const getPriceRange = () => {
  const ranges = ['budget', 'moderate', 'premium'];
  return ranges[Math.floor(Math.random() * ranges.length)];
};

/**
 * Get popular searches
 */
export const getPopularSearches = () => {
  return [
    'AC Repair',
    'Plumbing',
    'Electrical Work',
    'House Cleaning',
    'Painting',
    'Carpentry',
    'Pest Control',
    'Appliance Repair'
  ];
};

/**
 * Get recent searches from localStorage
 */
export const getRecentSearches = () => {
  try {
    const stored = localStorage.getItem('convergeai_recent_searches');
    return stored ? JSON.parse(stored) : [];
  } catch (error) {
    console.error('Error getting recent searches:', error);
    return [];
  }
};

/**
 * Save search to recent searches
 */
export const saveRecentSearch = (query) => {
  try {
    if (!query || !query.trim()) return;
    
    const recent = getRecentSearches();
    
    // Remove if already exists
    const filtered = recent.filter(s => s.toLowerCase() !== query.toLowerCase());
    
    // Add to beginning
    const updated = [query, ...filtered].slice(0, 10); // Keep only 10 recent searches
    
    localStorage.setItem('convergeai_recent_searches', JSON.stringify(updated));
  } catch (error) {
    console.error('Error saving recent search:', error);
  }
};

/**
 * Clear recent searches
 */
export const clearRecentSearches = () => {
  try {
    localStorage.removeItem('convergeai_recent_searches');
  } catch (error) {
    console.error('Error clearing recent searches:', error);
  }
};

