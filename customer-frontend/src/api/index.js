/**
 * API Service
 * Main API service that combines axios, URLs, and error handling
 */

import axiosInstance from './axiosConfig';
import { AUTH_ENDPOINTS, USER_ENDPOINTS, CATEGORY_ENDPOINTS, CART_ENDPOINTS, BOOKING_ENDPOINTS, ADDRESS_ENDPOINTS, HEALTH_ENDPOINT } from './urls';
import { handleAPIError, extractValidationErrors, logError } from './errorHandler';

/**
 * Authentication API Service
 */
export const authAPI = {
  /**
   * Register a new user
   * @param {Object} userData - User registration data
   * @param {string} userData.email - Email address
   * @param {string} userData.mobile - Mobile number
   * @param {string} userData.password - Password
   * @param {string} userData.first_name - First name
   * @param {string} userData.last_name - Last name (optional)
   * @param {string} userData.referral_code - Referral code (optional)
   * @returns {Promise<Object>} Response with user and tokens
   */
  register: async (userData) => {
    try {
      const response = await axiosInstance.post(AUTH_ENDPOINTS.REGISTER, userData);
      return response.data;
    } catch (error) {
      logError(error, 'Register');
      throw error;
    }
  },

  /**
   * Login user
   * @param {Object} credentials - Login credentials
   * @param {string} credentials.identifier - Email or mobile number
   * @param {string} credentials.password - Password
   * @returns {Promise<Object>} Response with user and tokens
   */
  login: async (credentials) => {
    try {
      const response = await axiosInstance.post(AUTH_ENDPOINTS.LOGIN, credentials);
      return response.data;
    } catch (error) {
      logError(error, 'Login');
      throw error;
    }
  },

  /**
   * Logout user
   * @returns {Promise<Object>} Logout response
   */
  logout: async () => {
    try {
      const response = await axiosInstance.post(AUTH_ENDPOINTS.LOGOUT);
      return response.data;
    } catch (error) {
      logError(error, 'Logout');
      throw error;
    }
  },

  /**
   * Refresh access token
   * @param {string} refreshToken - Refresh token
   * @returns {Promise<Object>} New tokens
   */
  refresh: async (refreshToken) => {
    try {
      const response = await axiosInstance.post(AUTH_ENDPOINTS.REFRESH, {
        refresh_token: refreshToken,
      });
      return response.data;
    } catch (error) {
      logError(error, 'Refresh Token');
      throw error;
    }
  },

  /**
   * Change password
   * @param {Object} passwordData - Password change data
   * @param {string} passwordData.current_password - Current password
   * @param {string} passwordData.new_password - New password
   * @returns {Promise<Object>} Success message
   */
  changePassword: async (passwordData) => {
    try {
      const response = await axiosInstance.post(AUTH_ENDPOINTS.CHANGE_PASSWORD, passwordData);
      return response.data;
    } catch (error) {
      logError(error, 'Change Password');
      throw error;
    }
  },
};

/**
 * User Profile API Service
 */
export const userAPI = {
  /**
   * Get current user profile
   * @returns {Promise<Object>} User profile data
   */
  getProfile: async () => {
    try {
      const response = await axiosInstance.get(USER_ENDPOINTS.PROFILE);
      return response.data;
    } catch (error) {
      logError(error, 'Get Profile');
      throw error;
    }
  },

  /**
   * Update user profile
   * @param {Object} userData - Updated user data
   * @returns {Promise<Object>} Updated user data
   */
  updateProfile: async (userData) => {
    try {
      const response = await axiosInstance.put(USER_ENDPOINTS.UPDATE_PROFILE, userData);
      return response.data;
    } catch (error) {
      logError(error, 'Update Profile');
      throw error;
    }
  },

  /**
   * Delete user account
   * @returns {Promise<Object>} Deletion confirmation
   */
  deleteAccount: async () => {
    try {
      const response = await axiosInstance.delete(USER_ENDPOINTS.DELETE_ACCOUNT);
      return response.data;
    } catch (error) {
      logError(error, 'Delete Account');
      throw error;
    }
  },
};

/**
 * Service Categories API Service
 */
export const categoryAPI = {
  /**
   * Get all service categories
   * @returns {Promise<Array>} List of categories
   */
  getAll: async () => {
    try {
      const response = await axiosInstance.get(CATEGORY_ENDPOINTS.LIST);
      return response.data;
    } catch (error) {
      logError(error, 'Get Categories');
      throw error;
    }
  },

  /**
   * Get category by ID
   * @param {number} categoryId - Category ID
   * @returns {Promise<Object>} Category details
   */
  getById: async (categoryId) => {
    try {
      const response = await axiosInstance.get(CATEGORY_ENDPOINTS.DETAIL(categoryId));
      return response.data;
    } catch (error) {
      logError(error, 'Get Category');
      throw error;
    }
  },

  /**
   * Get subcategories for a category
   * @param {number} categoryId - Category ID
   * @returns {Promise<Array>} List of subcategories
   */
  getSubcategories: async (categoryId) => {
    try {
      const response = await axiosInstance.get(CATEGORY_ENDPOINTS.SUBCATEGORIES(categoryId));
      return response.data;
    } catch (error) {
      logError(error, 'Get Subcategories');
      throw error;
    }
  },

  /**
   * Get rate cards for a category
   * @param {number} categoryId - Category ID
   * @returns {Promise<Array>} List of rate cards
   */
  getRateCards: async (categoryId) => {
    try {
      const response = await axiosInstance.get(CATEGORY_ENDPOINTS.RATE_CARDS(categoryId));
      return response.data;
    } catch (error) {
      logError(error, 'Get Rate Cards');
      throw error;
    }
  },
};

/**
 * Cart API Service
 */
export const cartAPI = {
  /**
   * Get user's cart
   * @returns {Promise<Object>} Cart data
   */
  get: async () => {
    try {
      const response = await axiosInstance.get(CART_ENDPOINTS.GET);
      return response.data;
    } catch (error) {
      logError(error, 'Get Cart');
      throw error;
    }
  },

  /**
   * Add item to cart
   * @param {Object} itemData - Item data
   * @returns {Promise<Object>} Updated cart
   */
  addItem: async (itemData) => {
    try {
      const response = await axiosInstance.post(CART_ENDPOINTS.ADD_ITEM, itemData);
      return response.data;
    } catch (error) {
      logError(error, 'Add Cart Item');
      throw error;
    }
  },

  /**
   * Update cart item
   * @param {number} itemId - Item ID
   * @param {Object} itemData - Updated item data
   * @returns {Promise<Object>} Updated cart
   */
  updateItem: async (itemId, itemData) => {
    try {
      const response = await axiosInstance.put(CART_ENDPOINTS.UPDATE_ITEM(itemId), itemData);
      return response.data;
    } catch (error) {
      logError(error, 'Update Cart Item');
      throw error;
    }
  },

  /**
   * Remove item from cart
   * @param {number} itemId - Item ID
   * @returns {Promise<Object>} Updated cart
   */
  removeItem: async (itemId) => {
    try {
      const response = await axiosInstance.delete(CART_ENDPOINTS.REMOVE_ITEM(itemId));
      return response.data;
    } catch (error) {
      logError(error, 'Remove Cart Item');
      throw error;
    }
  },

  /**
   * Clear cart
   * @returns {Promise<Object>} Empty cart
   */
  clear: async () => {
    try {
      const response = await axiosInstance.post(CART_ENDPOINTS.CLEAR);
      return response.data;
    } catch (error) {
      logError(error, 'Clear Cart');
      throw error;
    }
  },
};

/**
 * Booking API Service
 */
export const bookingAPI = {
  /**
   * Create new booking
   * @param {Object} bookingData - Booking data
   * @returns {Promise<Object>} Created booking
   */
  create: async (bookingData) => {
    try {
      const response = await axiosInstance.post(BOOKING_ENDPOINTS.CREATE, bookingData);
      return response.data;
    } catch (error) {
      logError(error, 'Create Booking');
      throw error;
    }
  },

  /**
   * Get all user bookings
   * @param {Object} params - Query parameters (page, limit, status)
   * @returns {Promise<Array>} List of bookings
   */
  getAll: async (params = {}) => {
    try {
      const response = await axiosInstance.get(BOOKING_ENDPOINTS.LIST, { params });
      return response.data;
    } catch (error) {
      logError(error, 'Get Bookings');
      throw error;
    }
  },

  /**
   * Get booking by ID
   * @param {number} bookingId - Booking ID
   * @returns {Promise<Object>} Booking details
   */
  getById: async (bookingId) => {
    try {
      const response = await axiosInstance.get(BOOKING_ENDPOINTS.DETAIL(bookingId));
      return response.data;
    } catch (error) {
      logError(error, 'Get Booking');
      throw error;
    }
  },

  /**
   * Reschedule booking
   * @param {number} bookingId - Booking ID
   * @param {Object} rescheduleData - New schedule data
   * @returns {Promise<Object>} Updated booking
   */
  reschedule: async (bookingId, rescheduleData) => {
    try {
      const response = await axiosInstance.post(BOOKING_ENDPOINTS.RESCHEDULE(bookingId), rescheduleData);
      return response.data;
    } catch (error) {
      logError(error, 'Reschedule Booking');
      throw error;
    }
  },

  /**
   * Cancel booking
   * @param {number} bookingId - Booking ID
   * @param {Object} cancelData - Cancellation data
   * @returns {Promise<Object>} Cancelled booking
   */
  cancel: async (bookingId, cancelData) => {
    try {
      const response = await axiosInstance.post(BOOKING_ENDPOINTS.CANCEL(bookingId), cancelData);
      return response.data;
    } catch (error) {
      logError(error, 'Cancel Booking');
      throw error;
    }
  },
};

/**
 * Address API Service
 */
export const addressAPI = {
  /**
   * Get all user addresses
   * @returns {Promise<Array>} List of addresses
   */
  getAll: async () => {
    try {
      const response = await axiosInstance.get(ADDRESS_ENDPOINTS.LIST);
      return response.data;
    } catch (error) {
      logError(error, 'Get Addresses');
      throw error;
    }
  },

  /**
   * Create new address
   * @param {Object} addressData - Address data
   * @returns {Promise<Object>} Created address
   */
  create: async (addressData) => {
    try {
      const response = await axiosInstance.post(ADDRESS_ENDPOINTS.CREATE, addressData);
      return response.data;
    } catch (error) {
      logError(error, 'Create Address');
      throw error;
    }
  },

  /**
   * Get address by ID
   * @param {number} addressId - Address ID
   * @returns {Promise<Object>} Address details
   */
  getById: async (addressId) => {
    try {
      const response = await axiosInstance.get(ADDRESS_ENDPOINTS.DETAIL(addressId));
      return response.data;
    } catch (error) {
      logError(error, 'Get Address');
      throw error;
    }
  },

  /**
   * Update address
   * @param {number} addressId - Address ID
   * @param {Object} addressData - Updated address data
   * @returns {Promise<Object>} Updated address
   */
  update: async (addressId, addressData) => {
    try {
      const response = await axiosInstance.put(ADDRESS_ENDPOINTS.UPDATE(addressId), addressData);
      return response.data;
    } catch (error) {
      logError(error, 'Update Address');
      throw error;
    }
  },

  /**
   * Delete address
   * @param {number} addressId - Address ID
   * @returns {Promise<Object>} Deletion confirmation
   */
  delete: async (addressId) => {
    try {
      const response = await axiosInstance.delete(ADDRESS_ENDPOINTS.DELETE(addressId));
      return response.data;
    } catch (error) {
      logError(error, 'Delete Address');
      throw error;
    }
  },
};

/**
 * Health Check API Service
 */
export const healthAPI = {
  /**
   * Check API health status
   * @returns {Promise<Object>} Health status
   */
  check: async () => {
    try {
      const response = await axiosInstance.get(HEALTH_ENDPOINT);
      return response.data;
    } catch (error) {
      logError(error, 'Health Check');
      throw error;
    }
  },
};

/**
 * Combined API object for easy imports
 */
const api = {
  auth: authAPI,
  user: userAPI,
  category: categoryAPI,
  cart: cartAPI,
  booking: bookingAPI,
  address: addressAPI,
  health: healthAPI,
};

export default api;

