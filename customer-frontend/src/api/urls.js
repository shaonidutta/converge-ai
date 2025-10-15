/**
 * API URLs Configuration
 * Centralized endpoint definitions for the backend API
 */

/**
 * Base API URL
 * Uses environment variable or defaults to localhost
 */
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

/**
 * API Version Prefix
 */
const API_VERSION = '/api/v1';

/**
 * Authentication Endpoints
 */
export const AUTH_ENDPOINTS = {
  REGISTER: `${API_VERSION}/auth/register`,
  LOGIN: `${API_VERSION}/auth/login`,
  LOGOUT: `${API_VERSION}/auth/logout`,
  REFRESH: `${API_VERSION}/auth/refresh`,
  CHANGE_PASSWORD: `${API_VERSION}/auth/change-password`,
};

/**
 * User Profile Endpoints
 */
export const USER_ENDPOINTS = {
  PROFILE: `${API_VERSION}/users/me`,
  UPDATE_PROFILE: `${API_VERSION}/users/me`,
  DELETE_ACCOUNT: `${API_VERSION}/users/me`,
};

/**
 * Service Categories Endpoints
 */
export const CATEGORY_ENDPOINTS = {
  LIST: `${API_VERSION}/categories`,
  DETAIL: (categoryId) => `${API_VERSION}/categories/${categoryId}`,
  SUBCATEGORIES: (categoryId) => `${API_VERSION}/categories/${categoryId}/subcategories`,
  RATE_CARDS: (categoryId) => `${API_VERSION}/categories/${categoryId}/rate-cards`,
};

/**
 * Cart Endpoints
 */
export const CART_ENDPOINTS = {
  GET: `${API_VERSION}/cart`,
  ADD_ITEM: `${API_VERSION}/cart/items`,
  UPDATE_ITEM: (itemId) => `${API_VERSION}/cart/items/${itemId}`,
  REMOVE_ITEM: (itemId) => `${API_VERSION}/cart/items/${itemId}`,
  CLEAR: `${API_VERSION}/cart/clear`,
};

/**
 * Booking Endpoints
 */
export const BOOKING_ENDPOINTS = {
  CREATE: `${API_VERSION}/bookings`,
  LIST: `${API_VERSION}/bookings`,
  DETAIL: (bookingId) => `${API_VERSION}/bookings/${bookingId}`,
  RESCHEDULE: (bookingId) => `${API_VERSION}/bookings/${bookingId}/reschedule`,
  CANCEL: (bookingId) => `${API_VERSION}/bookings/${bookingId}/cancel`,
};

/**
 * Address Endpoints
 */
export const ADDRESS_ENDPOINTS = {
  LIST: `${API_VERSION}/addresses`,
  CREATE: `${API_VERSION}/addresses`,
  DETAIL: (addressId) => `${API_VERSION}/addresses/${addressId}`,
  UPDATE: (addressId) => `${API_VERSION}/addresses/${addressId}`,
  DELETE: (addressId) => `${API_VERSION}/addresses/${addressId}`,
};

/**
 * Health Check Endpoint
 */
export const HEALTH_ENDPOINT = '/health';

/**
 * Export all endpoints as a single object
 */
export const API_ENDPOINTS = {
  AUTH: AUTH_ENDPOINTS,
  USER: USER_ENDPOINTS,
  CATEGORY: CATEGORY_ENDPOINTS,
  CART: CART_ENDPOINTS,
  BOOKING: BOOKING_ENDPOINTS,
  ADDRESS: ADDRESS_ENDPOINTS,
  HEALTH: HEALTH_ENDPOINT,
};

export default API_ENDPOINTS;

