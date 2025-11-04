/**
 * Operations Axios Configuration
 * Centralized axios instance with interceptors for operations dashboard
 */

import axios from 'axios';
import { API_BASE_URL } from './urls';
import { logError, isAuthError } from './errorHandler';

/**
 * Create axios instance with default configuration for operations
 */
const axiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 45000, // 45 seconds (longer for operations queries)
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Request Interceptor
 * Adds authentication token and staff context to all requests
 */
axiosInstance.interceptors.request.use(
  (config) => {
    // Get access token from localStorage
    const accessToken = localStorage.getItem('ops_access_token');
    
    if (accessToken) {
      config.headers.Authorization = `Bearer ${accessToken}`;
    }

    // Add staff context headers
    const staffId = localStorage.getItem('ops_staff_id');
    const staffRole = localStorage.getItem('ops_staff_role');
    
    if (staffId) {
      config.headers['X-Staff-ID'] = staffId;
    }
    
    if (staffRole) {
      config.headers['X-Staff-Role'] = staffRole;
    }

    // Add request timestamp for audit logging
    config.headers['X-Request-Timestamp'] = new Date().toISOString();

    // Log request in development
    if (import.meta.env.DEV) {
      console.log(`🚀 OPS ${config.method.toUpperCase()} ${config.url}`, {
        data: config.data,
        params: config.params,
        headers: {
          Authorization: config.headers.Authorization ? '[REDACTED]' : 'None',
          'X-Staff-ID': config.headers['X-Staff-ID'],
          'X-Staff-Role': config.headers['X-Staff-Role'],
        },
      });
    }

    return config;
  },
  (error) => {
    logError(error, 'Operations Request Interceptor');
    return Promise.reject(error);
  }
);

/**
 * Response Interceptor
 * Handles token refresh, error responses, and audit logging
 */
axiosInstance.interceptors.response.use(
  (response) => {
    // Log successful response in development
    if (import.meta.env.DEV) {
      console.log(`✅ OPS ${response.config.method.toUpperCase()} ${response.config.url}`, {
        status: response.status,
        data: response.data,
      });
    }

    // Log PII access for audit trail
    if (response.config.url.includes('/complaints/') || 
        response.config.url.includes('/users/') ||
        response.config.headers['X-PII-Access']) {
      logPIIAccess(response.config);
    }

    return response;
  },
  async (error) => {
    const originalRequest = error.config;

    // Log error
    logError(error, 'Operations Response Interceptor');

    // Handle 401 Unauthorized - Token expired
    if (isAuthError(error) && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        // Get refresh token
        const refreshToken = localStorage.getItem('ops_refresh_token');

        if (!refreshToken) {
          // No refresh token, redirect to login
          handleAuthFailure();
          return Promise.reject(error);
        }

        // Attempt to refresh token
        const response = await axios.post(
          `${API_BASE_URL}/auth/refresh`,
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
          // Store new tokens with ops prefix
          localStorage.setItem('ops_access_token', tokens.access_token);
          localStorage.setItem('ops_refresh_token', tokens.refresh_token);

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
        logError(refreshError, 'Operations Token Refresh');
        handleAuthFailure();
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

/**
 * Handle authentication failure for operations staff
 * Clears tokens and redirects to operations login
 */
const handleAuthFailure = () => {
  // Clear all operations auth data
  localStorage.removeItem('ops_access_token');
  localStorage.removeItem('ops_refresh_token');
  localStorage.removeItem('ops_staff');
  localStorage.removeItem('ops_staff_id');
  localStorage.removeItem('ops_staff_role');
  localStorage.removeItem('ops_permissions');

  // Dispatch custom event for auth context
  window.dispatchEvent(new CustomEvent('ops-auth-failure'));

  // Redirect to operations login page
  if (window.location.pathname !== '/login') {
    window.location.href = '/login';
  }
};

/**
 * Log PII access for audit trail
 * @param {Object} config - Request configuration
 */
const logPIIAccess = (config) => {
  const staffId = localStorage.getItem('ops_staff_id');
  const timestamp = new Date().toISOString();
  
  // In production, this would send to audit service
  if (import.meta.env.DEV) {
    console.log('🔒 PII Access Logged:', {
      staffId,
      url: config.url,
      method: config.method,
      timestamp,
    });
  }
};

/**
 * Get current access token
 * @returns {string|null} Access token or null
 */
export const getAccessToken = () => {
  return localStorage.getItem('ops_access_token');
};

/**
 * Get current refresh token
 * @returns {string|null} Refresh token or null
 */
export const getRefreshToken = () => {
  return localStorage.getItem('ops_refresh_token');
};

/**
 * Check if staff is authenticated
 * @returns {boolean} True if access token exists
 */
export const isAuthenticated = () => {
  return !!getAccessToken();
};

/**
 * Get current staff information
 * @returns {Object|null} Staff object or null
 */
export const getCurrentStaff = () => {
  const staffData = localStorage.getItem('ops_staff');
  return staffData ? JSON.parse(staffData) : null;
};

/**
 * Get staff permissions
 * @returns {Array} Array of permission strings
 */
export const getStaffPermissions = () => {
  const permissions = localStorage.getItem('ops_permissions');
  return permissions ? JSON.parse(permissions) : [];
};

/**
 * Check if staff has specific permission
 * @param {string} permission - Permission to check
 * @returns {boolean} True if staff has permission
 */
export const hasPermission = (permission) => {
  const permissions = getStaffPermissions();
  return permissions.includes(permission) || permissions.includes('admin');
};

/**
 * Clear all authentication data
 */
export const clearAuth = () => {
  localStorage.removeItem('ops_access_token');
  localStorage.removeItem('ops_refresh_token');
  localStorage.removeItem('ops_staff');
  localStorage.removeItem('ops_staff_id');
  localStorage.removeItem('ops_staff_role');
  localStorage.removeItem('ops_permissions');
};

export default axiosInstance;
