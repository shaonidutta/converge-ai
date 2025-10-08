/**
 * API Error Handler
 * Centralized error handling for API requests
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
 * Maps common error scenarios to user-friendly messages
 */
const ERROR_MESSAGES = {
  // Network Errors
  NETWORK_ERROR: 'Network error. Please check your internet connection.',
  TIMEOUT_ERROR: 'Request timeout. Please try again.',
  
  // Authentication Errors
  UNAUTHORIZED: 'Invalid credentials. Please try again.',
  FORBIDDEN: 'You do not have permission to perform this action.',
  TOKEN_EXPIRED: 'Your session has expired. Please login again.',
  
  // Validation Errors
  VALIDATION_ERROR: 'Please check your input and try again.',
  EMAIL_EXISTS: 'This email is already registered.',
  MOBILE_EXISTS: 'This mobile number is already registered.',
  INVALID_EMAIL: 'Please enter a valid email address.',
  INVALID_MOBILE: 'Please enter a valid mobile number.',
  WEAK_PASSWORD: 'Password does not meet security requirements.',
  
  // Server Errors
  SERVER_ERROR: 'Something went wrong on our end. Please try again later.',
  SERVICE_UNAVAILABLE: 'Service temporarily unavailable. Please try again later.',
  
  // Generic
  UNKNOWN_ERROR: 'An unexpected error occurred. Please try again.',
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
      if (message.toLowerCase().includes('email already registered')) {
        message = ERROR_MESSAGES.EMAIL_EXISTS;
      } else if (message.toLowerCase().includes('mobile') && message.toLowerCase().includes('already')) {
        message = ERROR_MESSAGES.MOBILE_EXISTS;
      } else if (message.toLowerCase().includes('invalid credentials')) {
        message = ERROR_MESSAGES.UNAUTHORIZED;
      } else if (message.toLowerCase().includes('password')) {
        if (message.toLowerCase().includes('uppercase') || 
            message.toLowerCase().includes('lowercase') || 
            message.toLowerCase().includes('digit') || 
            message.toLowerCase().includes('special')) {
          message = ERROR_MESSAGES.WEAK_PASSWORD + '\n' + data.detail;
        }
      }
    }
    
    // Handle validation errors (422)
    if (status === 422 && data.detail && Array.isArray(data.detail)) {
      details = data.detail;
      message = ERROR_MESSAGES.VALIDATION_ERROR;
    }
  }

  // Status-based error messages
  switch (status) {
    case 400:
      // Bad request - use backend message or default
      break;
    case 401:
      message = message || ERROR_MESSAGES.UNAUTHORIZED;
      break;
    case 403:
      message = ERROR_MESSAGES.FORBIDDEN;
      break;
    case 404:
      message = 'Resource not found.';
      break;
    case 422:
      // Validation error - already handled above
      break;
    case 500:
      message = ERROR_MESSAGES.SERVER_ERROR;
      break;
    case 503:
      message = ERROR_MESSAGES.SERVICE_UNAVAILABLE;
      break;
    default:
      break;
  }

  return {
    message,
    status,
    details,
  };
};

/**
 * Handle API error and return user-friendly message
 * @param {Object} error - Axios error object
 * @param {string} defaultMessage - Default message if parsing fails
 * @returns {string} User-friendly error message
 */
export const handleAPIError = (error, defaultMessage = ERROR_MESSAGES.UNKNOWN_ERROR) => {
  const parsedError = parseError(error);
  return parsedError.message || defaultMessage;
};

/**
 * Log error for debugging (can be extended to send to logging service)
 * @param {Object} error - Error object
 * @param {string} context - Context where error occurred
 */
export const logError = (error, context = 'API') => {
  if (import.meta.env.DEV) {
    console.group(`🔴 ${context} Error`);
    console.error('Error:', error);
    if (error.response) {
      console.error('Status:', error.response.status);
      console.error('Data:', error.response.data);
      console.error('Headers:', error.response.headers);
    } else if (error.request) {
      console.error('Request:', error.request);
    } else {
      console.error('Message:', error.message);
    }
    console.groupEnd();
  }
};

/**
 * Check if error is authentication related
 * @param {Object} error - Error object
 * @returns {boolean} True if auth error
 */
export const isAuthError = (error) => {
  return error.response && (error.response.status === 401 || error.response.status === 403);
};

/**
 * Check if error is validation related
 * @param {Object} error - Error object
 * @returns {boolean} True if validation error
 */
export const isValidationError = (error) => {
  return error.response && error.response.status === 422;
};

/**
 * Extract validation errors for form fields
 * @param {Object} error - Error object
 * @returns {Object} Field-specific error messages
 */
export const extractValidationErrors = (error) => {
  if (!isValidationError(error)) {
    return {};
  }

  const errors = {};
  const details = error.response?.data?.detail;

  if (Array.isArray(details)) {
    details.forEach((err) => {
      // Pydantic validation errors have 'loc' (location) and 'msg' (message)
      const field = err.loc?.[err.loc.length - 1]; // Get last item in location array
      const message = err.msg;
      if (field && message) {
        errors[field] = message;
      }
    });
  }

  return errors;
};

/**
 * Create a standardized error response
 * @param {string} message - Error message
 * @param {number} status - HTTP status code
 * @param {Object} data - Additional error data
 * @returns {APIError} Standardized error object
 */
export const createError = (message, status = 500, data = null) => {
  return new APIError(message, status, data);
};

export default {
  APIError,
  parseError,
  handleAPIError,
  logError,
  isAuthError,
  isValidationError,
  extractValidationErrors,
  createError,
  ERROR_MESSAGES,
};

