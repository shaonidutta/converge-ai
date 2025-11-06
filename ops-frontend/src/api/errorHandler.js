/**
 * Operations API Error Handler
 * Centralized error handling for operations dashboard API requests
 */

/**
 * Custom API Error Class
 */
export class APIError extends Error {
  constructor(message, status, data) {
    super(message);
    this.name = 'APIError';
    this.status = status;
    this.data = data;
  }
}

/**
 * Error Messages Map
 * Maps common error scenarios to user-friendly messages for operations staff
 */
const ERROR_MESSAGES = {
  // Network Errors
  NETWORK_ERROR: 'Network error. Please check your connection and try again.',
  TIMEOUT_ERROR: 'Request timeout. The server is taking too long to respond.',
  
  // Authentication Errors
  UNAUTHORIZED: 'Invalid staff credentials. Please check your login details.',
  FORBIDDEN: 'You do not have permission to perform this action. Contact your administrator.',
  TOKEN_EXPIRED: 'Your session has expired. Please login again.',
  ACCOUNT_LOCKED: 'Your account has been locked due to multiple failed login attempts.',
  
  // Staff Management Errors
  STAFF_NOT_FOUND: 'Staff member not found.',
  INSUFFICIENT_PERMISSIONS: 'You do not have sufficient permissions for this operation.',
  ROLE_ASSIGNMENT_ERROR: 'Unable to assign role. Please check role permissions.',
  
  // Priority Queue Errors
  QUEUE_ITEM_NOT_FOUND: 'Priority queue item not found.',
  ALREADY_REVIEWED: 'This item has already been reviewed.',
  ASSIGNMENT_FAILED: 'Failed to assign item. Please try again.',
  
  // Complaint Management Errors
  COMPLAINT_NOT_FOUND: 'Complaint not found.',
  COMPLAINT_ALREADY_RESOLVED: 'This complaint has already been resolved.',
  INVALID_STATUS_TRANSITION: 'Invalid status change for this complaint.',
  
  // Alert System Errors
  ALERT_NOT_FOUND: 'Alert not found.',
  ALERT_RULE_ERROR: 'Error in alert rule configuration.',
  SUBSCRIPTION_ERROR: 'Failed to update alert subscription.',
  
  // Configuration Errors
  CONFIG_NOT_FOUND: 'Configuration setting not found.',
  CONFIG_VALIDATION_ERROR: 'Invalid configuration value.',
  CONFIG_UPDATE_FAILED: 'Failed to update configuration.',
  
  // Data Access Errors
  PII_ACCESS_DENIED: 'PII access denied. You do not have permission to view sensitive data.',
  RATE_LIMIT_EXCEEDED: 'Rate limit exceeded. Please wait before making more requests.',
  
  // Server Errors
  SERVER_ERROR: 'Internal server error. Please contact technical support.',
  SERVICE_UNAVAILABLE: 'Service temporarily unavailable. Please try again later.',
  DATABASE_ERROR: 'Database connection error. Please try again.',
  
  // Generic
  UNKNOWN_ERROR: 'An unexpected error occurred. Please try again or contact support.',
};

/**
 * Parse error response from backend
 * @param {Object} error - Axios error object
 * @returns {Object} Parsed error with message and details
 */
export const parseError = (error) => {
  // Network error (no response from server)
  if (!error.response) {
    if (error.code === 'ECONNABORTED') {
      return {
        message: ERROR_MESSAGES.TIMEOUT_ERROR,
        status: null,
        details: null,
      };
    }
    return {
      message: ERROR_MESSAGES.NETWORK_ERROR,
      status: null,
      details: null,
    };
  }

  const { status, data } = error.response;

  // Extract error message from response
  let message = ERROR_MESSAGES.UNKNOWN_ERROR;
  let details = null;

  if (data) {
    // Backend returns error in 'detail' field
    if (data.detail) {
      message = data.detail;
      
      // Map specific backend messages to user-friendly ones
      if (message.toLowerCase().includes('invalid credentials')) {
        message = ERROR_MESSAGES.UNAUTHORIZED;
      } else if (message.toLowerCase().includes('account locked')) {
        message = ERROR_MESSAGES.ACCOUNT_LOCKED;
      } else if (message.toLowerCase().includes('insufficient permissions')) {
        message = ERROR_MESSAGES.INSUFFICIENT_PERMISSIONS;
      } else if (message.toLowerCase().includes('pii access denied')) {
        message = ERROR_MESSAGES.PII_ACCESS_DENIED;
      } else if (message.toLowerCase().includes('rate limit')) {
        message = ERROR_MESSAGES.RATE_LIMIT_EXCEEDED;
      } else if (message.toLowerCase().includes('not found')) {
        if (message.toLowerCase().includes('staff')) {
          message = ERROR_MESSAGES.STAFF_NOT_FOUND;
        } else if (message.toLowerCase().includes('complaint')) {
          message = ERROR_MESSAGES.COMPLAINT_NOT_FOUND;
        } else if (message.toLowerCase().includes('alert')) {
          message = ERROR_MESSAGES.ALERT_NOT_FOUND;
        } else if (message.toLowerCase().includes('config')) {
          message = ERROR_MESSAGES.CONFIG_NOT_FOUND;
        }
      }
    }
    
    // Handle validation errors (422)
    if (status === 422 && data.detail && Array.isArray(data.detail)) {
      details = data.detail;
      message = 'Please check the following errors:';
    }
    
    // Handle specific error messages from backend
    if (data.message) {
      message = data.message;
    }
  }

  // Map HTTP status codes to appropriate messages
  switch (status) {
    case 401:
      message = ERROR_MESSAGES.UNAUTHORIZED;
      break;
    case 403:
      message = ERROR_MESSAGES.FORBIDDEN;
      break;
    case 404:
      // Keep the specific not found message if already set
      if (message === ERROR_MESSAGES.UNKNOWN_ERROR) {
        message = 'Resource not found.';
      }
      break;
    case 429:
      message = ERROR_MESSAGES.RATE_LIMIT_EXCEEDED;
      break;
    case 500:
      message = ERROR_MESSAGES.SERVER_ERROR;
      break;
    case 502:
    case 503:
    case 504:
      message = ERROR_MESSAGES.SERVICE_UNAVAILABLE;
      break;
  }

  return {
    message,
    status,
    details,
  };
};

/**
 * Check if error is authentication related
 * @param {Object} error - Parsed error object
 * @returns {boolean} True if authentication error
 */
export const isAuthError = (error) => {
  return error.status === 401 || 
         error.message === ERROR_MESSAGES.UNAUTHORIZED ||
         error.message === ERROR_MESSAGES.TOKEN_EXPIRED;
};

/**
 * Check if error is permission related
 * @param {Object} error - Parsed error object
 * @returns {boolean} True if permission error
 */
export const isPermissionError = (error) => {
  return error.status === 403 || 
         error.message === ERROR_MESSAGES.FORBIDDEN ||
         error.message === ERROR_MESSAGES.INSUFFICIENT_PERMISSIONS;
};

/**
 * Check if error is rate limiting related
 * @param {Object} error - Parsed error object
 * @returns {boolean} True if rate limit error
 */
export const isRateLimitError = (error) => {
  return error.status === 429 || 
         error.message === ERROR_MESSAGES.RATE_LIMIT_EXCEEDED;
};

/**
 * Log error for debugging (development only)
 * @param {Object} error - Error object
 * @param {string} context - Context where error occurred
 */
export const logError = (error, context = 'API') => {
  if (import.meta.env.DEV) {
    console.group(`🚨 ${context} Error`);
    console.error('Error:', error);
    if (error.response) {
      console.error('Response:', error.response);
    }
    if (error.request) {
      console.error('Request:', error.request);
    }
    console.groupEnd();
  }
};

/**
 * Handle API error and return user-friendly message
 * @param {Object} error - Axios error object
 * @param {string} context - Context where error occurred
 * @returns {Object} Parsed error object
 */
export const handleAPIError = (error, context = 'API') => {
  logError(error, context);
  const parsedError = parseError(error);
  
  // Create APIError instance
  throw new APIError(
    parsedError.message,
    parsedError.status,
    parsedError.details
  );
};

export default {
  APIError,
  parseError,
  isAuthError,
  isPermissionError,
  isRateLimitError,
  logError,
  handleAPIError,
};
