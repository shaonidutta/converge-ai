/**
 * Axios Configuration
 * Centralized axios instance with interceptors
 */

import axios from 'axios';
import { API_BASE_URL } from './urls';
import { logError, isAuthError } from './errorHandler';

/**
 * Create axios instance with default configuration
 */
const axiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000, // 30 seconds
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Request Interceptor
 * Adds authentication token to all requests
 */
axiosInstance.interceptors.request.use(
  (config) => {
    // Get access token from localStorage
    const accessToken = localStorage.getItem('access_token');
    
    if (accessToken) {
      config.headers.Authorization = `Bearer ${accessToken}`;
    }

    // Log request in development
    if (import.meta.env.DEV) {
      console.log(`🚀 ${config.method.toUpperCase()} ${config.url}`, {
        data: config.data,
        params: config.params,
      });
    }

    return config;
  },
  (error) => {
    logError(error, 'Request Interceptor');
    return Promise.reject(error);
  }
);

/**
 * Response Interceptor
 * Handles token refresh and error responses
 */
axiosInstance.interceptors.response.use(
  (response) => {
    // Log successful response in development
    if (import.meta.env.DEV) {
      console.log(`✅ ${response.config.method.toUpperCase()} ${response.config.url}`, response.data);
    }
    return response;
  },
  async (error) => {
    const originalRequest = error.config;

    // Log error
    logError(error, 'Response Interceptor');

    // Handle 401 Unauthorized - Token expired
    if (isAuthError(error) && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        // Get refresh token
        const refreshToken = localStorage.getItem('refresh_token');

        if (!refreshToken) {
          // No refresh token, redirect to login
          handleAuthFailure();
          return Promise.reject(error);
        }

        // Attempt to refresh token
        const response = await axios.post(
          `${API_BASE_URL}/api/v1/auth/refresh`,
          { refresh_token: refreshToken },
          {
            headers: {
              'Content-Type': 'application/json',
            },
          }
        );

        // Extract new tokens from response
        const { tokens } = response.data;
        
        if (tokens && tokens.access_token && tokens.refresh_token) {
          // Store new tokens
          localStorage.setItem('access_token', tokens.access_token);
          localStorage.setItem('refresh_token', tokens.refresh_token);

          // Update authorization header
          originalRequest.headers.Authorization = `Bearer ${tokens.access_token}`;

          // Retry original request
          return axiosInstance(originalRequest);
        } else {
          // Invalid response format
          handleAuthFailure();
          return Promise.reject(error);
        }
      } catch (refreshError) {
        // Refresh failed, clear tokens and redirect to login
        logError(refreshError, 'Token Refresh');
        handleAuthFailure();
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

/**
 * Handle authentication failure
 * Clears tokens and redirects to login
 */
const handleAuthFailure = () => {
  // Clear all auth data
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
  localStorage.removeItem('user');

  // Redirect to login page
  if (window.location.pathname !== '/login' && window.location.pathname !== '/signup') {
    window.location.href = '/login';
  }
};

/**
 * Get current access token
 * @returns {string|null} Access token or null
 */
export const getAccessToken = () => {
  return localStorage.getItem('access_token');
};

/**
 * Get current refresh token
 * @returns {string|null} Refresh token or null
 */
export const getRefreshToken = () => {
  return localStorage.getItem('refresh_token');
};

/**
 * Check if user is authenticated
 * @returns {boolean} True if access token exists
 */
export const isAuthenticated = () => {
  return !!getAccessToken();
};

/**
 * Clear all authentication data
 */
export const clearAuth = () => {
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
  localStorage.removeItem('user');
};

/**
 * Store authentication data
 * @param {Object} authData - Authentication data with tokens and user
 */
export const storeAuthData = (authData) => {
  if (authData.tokens) {
    localStorage.setItem('access_token', authData.tokens.access_token);
    localStorage.setItem('refresh_token', authData.tokens.refresh_token);
  }
  
  if (authData.user) {
    localStorage.setItem('user', JSON.stringify(authData.user));
  }
};

/**
 * Get stored user data
 * @returns {Object|null} User data or null
 */
export const getStoredUser = () => {
  const userStr = localStorage.getItem('user');
  if (userStr) {
    try {
      return JSON.parse(userStr);
    } catch (e) {
      console.error('Failed to parse user data:', e);
      return null;
    }
  }
  return null;
};

export default axiosInstance;

