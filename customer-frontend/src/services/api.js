import axios from 'axios';

/**
 * API Configuration
 * Base URL for the backend API
 */
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

/**
 * Axios instance with default configuration
 * Includes interceptors for request/response handling
 */
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 seconds
});

/**
 * Request Interceptor
 * Adds authentication token to requests if available
 */
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

/**
 * Response Interceptor
 * Handles token refresh and error responses
 */
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // Handle 401 Unauthorized - Token expired
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = localStorage.getItem('refresh_token');
        if (refreshToken) {
          const response = await axios.post(`${API_BASE_URL}/api/v1/auth/refresh`, {
            refresh_token: refreshToken,
          });

          const { access_token } = response.data;
          localStorage.setItem('access_token', access_token);

          // Retry original request with new token
          originalRequest.headers.Authorization = `Bearer ${access_token}`;
          return apiClient(originalRequest);
        }
      } catch (refreshError) {
        // Refresh failed - logout user
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

/**
 * API Service Object
 * Contains all API endpoint methods organized by feature
 */
const api = {
  // ============================================
  // Authentication APIs
  // ============================================
  auth: {
    /**
     * Register a new user
     * @param {Object} userData - User registration data
     * @returns {Promise} API response
     */
    register: (userData) => apiClient.post('/api/v1/auth/register', userData),

    /**
     * Login user
     * @param {Object} credentials - Login credentials (username/email and password)
     * @returns {Promise} API response with tokens
     */
    login: (credentials) => apiClient.post('/api/v1/auth/login', credentials),

    /**
     * Refresh access token
     * @param {string} refreshToken - Refresh token
     * @returns {Promise} API response with new access token
     */
    refresh: (refreshToken) => apiClient.post('/api/v1/auth/refresh', { refresh_token: refreshToken }),

    /**
     * Logout user
     * @returns {Promise} API response
     */
    logout: () => apiClient.post('/api/v1/auth/logout'),

    /**
     * Change password
     * @param {Object} passwordData - Password data (current_password, new_password)
     * @returns {Promise} API response
     */
    changePassword: (passwordData) => apiClient.post('/api/v1/auth/change-password', passwordData),
  },

  // ============================================
  // User Profile APIs
  // ============================================
  user: {
    /**
     * Get current user profile
     * @returns {Promise} API response with user data
     */
    getProfile: () => apiClient.get('/api/v1/users/me'),

    /**
     * Update user profile
     * @param {Object} userData - Updated user data
     * @returns {Promise} API response
     */
    updateProfile: (userData) => apiClient.put('/api/v1/users/me', userData),

    /**
     * Delete user account
     * @returns {Promise} API response
     */
    deleteAccount: () => apiClient.delete('/api/v1/users/me'),
  },

  // ============================================
  // Service Categories APIs
  // ============================================
  categories: {
    /**
     * Get all service categories
     * @returns {Promise} API response with categories list
     */
    getAll: () => apiClient.get('/api/v1/categories'),

    /**
     * Get specific category by ID
     * @param {number} categoryId - Category ID
     * @returns {Promise} API response with category details
     */
    getById: (categoryId) => apiClient.get(`/api/v1/categories/${categoryId}`),

    /**
     * Get subcategories for a category
     * @param {number} categoryId - Category ID
     * @returns {Promise} API response with subcategories list
     */
    getSubcategories: (categoryId) => apiClient.get(`/api/v1/categories/${categoryId}/subcategories`),

    /**
     * Get rate cards for a subcategory
     * @param {number} subcategoryId - Subcategory ID
     * @returns {Promise} API response with rate cards list
     */
    getRateCards: (subcategoryId) => apiClient.get(`/api/v1/categories/subcategories/${subcategoryId}/rate-cards`),
  },

  // ============================================
  // Shopping Cart APIs
  // ============================================
  cart: {
    /**
     * Get current user's cart
     * @returns {Promise} API response with cart data
     */
    get: () => apiClient.get('/api/v1/cart'),

    /**
     * Add item to cart
     * @param {Object} item - Cart item data
     * @returns {Promise} API response
     */
    addItem: (item) => apiClient.post('/api/v1/cart/items', item),

    /**
     * Update cart item
     * @param {number} itemId - Cart item ID
     * @param {Object} updates - Updated item data
     * @returns {Promise} API response
     */
    updateItem: (itemId, updates) => apiClient.put(`/api/v1/cart/items/${itemId}`, updates),

    /**
     * Remove item from cart
     * @param {number} itemId - Cart item ID
     * @returns {Promise} API response
     */
    removeItem: (itemId) => apiClient.delete(`/api/v1/cart/items/${itemId}`),

    /**
     * Clear all items from cart
     * @returns {Promise} API response
     */
    clear: () => apiClient.delete('/api/v1/cart'),
  },

  // ============================================
  // Bookings APIs
  // ============================================
  bookings: {
    /**
     * Create new booking from cart
     * @param {Object} bookingData - Booking details
     * @returns {Promise} API response
     */
    create: (bookingData) => apiClient.post('/api/v1/bookings', bookingData),

    /**
     * Get all user bookings
     * @param {Object} params - Query parameters (page, limit, status)
     * @returns {Promise} API response with bookings list
     */
    getAll: (params) => apiClient.get('/api/v1/bookings', { params }),

    /**
     * Get specific booking by ID
     * @param {number} bookingId - Booking ID
     * @returns {Promise} API response with booking details
     */
    getById: (bookingId) => apiClient.get(`/api/v1/bookings/${bookingId}`),

    /**
     * Reschedule a booking
     * @param {number} bookingId - Booking ID
     * @param {Object} rescheduleData - New schedule data
     * @returns {Promise} API response
     */
    reschedule: (bookingId, rescheduleData) => apiClient.post(`/api/v1/bookings/${bookingId}/reschedule`, rescheduleData),

    /**
     * Cancel a booking
     * @param {number} bookingId - Booking ID
     * @param {Object} cancelData - Cancellation reason
     * @returns {Promise} API response
     */
    cancel: (bookingId, cancelData) => apiClient.post(`/api/v1/bookings/${bookingId}/cancel`, cancelData),
  },

  // ============================================
  // Address Management APIs
  // ============================================
  addresses: {
    /**
     * Get all user addresses
     * @returns {Promise} API response with addresses list
     */
    getAll: () => apiClient.get('/api/v1/addresses'),

    /**
     * Add new address
     * @param {Object} addressData - Address details
     * @returns {Promise} API response
     */
    add: (addressData) => apiClient.post('/api/v1/addresses', addressData),

    /**
     * Get specific address by ID
     * @param {number} addressId - Address ID
     * @returns {Promise} API response with address details
     */
    getById: (addressId) => apiClient.get(`/api/v1/addresses/${addressId}`),

    /**
     * Update address
     * @param {number} addressId - Address ID
     * @param {Object} addressData - Updated address data
     * @returns {Promise} API response
     */
    update: (addressId, addressData) => apiClient.put(`/api/v1/addresses/${addressId}`, addressData),

    /**
     * Delete address
     * @param {number} addressId - Address ID
     * @returns {Promise} API response
     */
    delete: (addressId) => apiClient.delete(`/api/v1/addresses/${addressId}`),
  },

  // ============================================
  // Chat APIs
  // ============================================
  chat: {
    /**
     * Send a chat message
     * @param {Object} messageData - Message data (message, session_id, channel)
     * @returns {Promise} API response with user and assistant messages
     */
    sendMessage: (messageData) => apiClient.post('/api/v1/chat/message', messageData),

    /**
     * Get chat history for a session
     * @param {string} sessionId - Session ID
     * @param {Object} params - Query parameters (limit, skip)
     * @returns {Promise} API response with messages array
     */
    getHistory: (sessionId, params = {}) => apiClient.get(`/api/v1/chat/history/${sessionId}`, { params }),

    /**
     * Get all chat sessions
     * @param {Object} params - Query parameters (limit, skip)
     * @returns {Promise} API response with sessions array
     */
    getSessions: (params = {}) => apiClient.get('/api/v1/chat/sessions', { params }),

    /**
     * End a chat session
     * @param {string} sessionId - Session ID
     * @returns {Promise} API response
     */
    endSession: (sessionId) => apiClient.delete(`/api/v1/chat/sessions/${sessionId}`),
  },

  // ============================================
  // Customer Profile APIs
  // ============================================
  customers: {
    /**
     * Get current customer profile
     * @returns {Promise} API response with customer data
     */
    getProfile: () => apiClient.get('/api/v1/customers/me'),

    /**
     * Update customer profile
     * @param {Object} profileData - Updated profile data
     * @returns {Promise} API response
     */
    updateProfile: (profileData) => apiClient.put('/api/v1/customers/me', profileData),

    /**
     * Get customer statistics
     * @returns {Promise} API response with stats
     */
    getStats: () => apiClient.get('/api/v1/customers/me/stats'),

    /**
     * Upload profile avatar
     * @param {FormData} formData - Form data with avatar file
     * @returns {Promise} API response
     */
    uploadAvatar: (formData) => apiClient.post('/api/v1/customers/me/avatar', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),

    /**
     * Delete customer account
     * @param {Object} data - Confirmation data (password)
     * @returns {Promise} API response
     */
    deleteAccount: (data) => apiClient.delete('/api/v1/customers/me', { data }),
  },

  // ============================================
  // Health Check API
  // ============================================
  health: {
    /**
     * Check API health status
     * @returns {Promise} API response with health status
     */
    check: () => apiClient.get('/health'),
  },
};

export default api;
export { apiClient, API_BASE_URL };

