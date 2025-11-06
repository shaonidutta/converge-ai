/**
 * API Module Exports
 * Centralized exports for all API-related modules
 */

// Axios instance and configuration
export { default as axiosInstance } from './axiosConfig';
export {
  getAccessToken,
  getRefreshToken,
  isAuthenticated,
  getCurrentStaff,
  getStaffPermissions,
  hasPermission,
  clearAuth,
} from './axiosConfig';

// API endpoints
export { default as API_ENDPOINTS } from './urls';
export * from './urls';

// Error handling
export {
  APIError,
  parseError,
  isAuthError,
  isPermissionError,
  isRateLimitError,
  logError,
  handleAPIError,
} from './errorHandler';
