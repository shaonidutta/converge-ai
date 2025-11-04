/**
 * Operations API URLs Configuration
 * Centralized endpoint definitions for the operations backend API
 */

/**
 * Base API URL for Operations
 * Uses environment variable or defaults to localhost ops endpoints
 */
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1/ops';

/**
 * WebSocket URL for real-time updates
 */
export const WS_BASE_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws/ops';

/**
 * Authentication Endpoints
 */
export const AUTH_ENDPOINTS = {
  LOGIN: '/auth/login',
  LOGOUT: '/auth/logout',
  REFRESH: '/auth/refresh',
  ME: '/auth/me',
  REGISTER: '/auth/register',
};

/**
 * Dashboard & Metrics Endpoints
 */
export const DASHBOARD_ENDPOINTS = {
  METRICS: '/dashboard/metrics',
  PRIORITY_QUEUE: '/dashboard/priority-queue',
};

/**
 * Individual Metrics Endpoints
 */
export const METRICS_ENDPOINTS = {
  BOOKINGS: '/metrics/bookings',
  COMPLAINTS: '/metrics/complaints',
  SLA: '/metrics/sla',
  REVENUE: '/metrics/revenue',
  REALTIME: '/metrics/realtime',
};

/**
 * Priority Queue Endpoints
 */
export const PRIORITY_QUEUE_ENDPOINTS = {
  LIST: '/priority-queue',
  DETAIL: (itemId) => `/priority-queue/${itemId}`,
  REVIEW: (itemId) => `/priority-queue/${itemId}/review`,
  ASSIGN: (itemId) => `/priority-queue/${itemId}/assign`,
};

/**
 * Complaints Management Endpoints
 */
export const COMPLAINTS_ENDPOINTS = {
  LIST: '/complaints',
  DETAIL: (complaintId) => `/complaints/${complaintId}`,
  UPDATE: (complaintId) => `/complaints/${complaintId}`,
  ASSIGN: (complaintId) => `/complaints/${complaintId}/assign`,
  RESOLVE: (complaintId) => `/complaints/${complaintId}/resolve`,
  UPDATES: (complaintId) => `/complaints/${complaintId}/updates`,
  ADD_UPDATE: (complaintId) => `/complaints/${complaintId}/updates`,
};

/**
 * Alert System Endpoints
 */
export const ALERT_ENDPOINTS = {
  LIST: '/alerts',
  DETAIL: (alertId) => `/alerts/${alertId}`,
  READ: (alertId) => `/alerts/${alertId}/read`,
  DISMISS: (alertId) => `/alerts/${alertId}/dismiss`,
  RULES: '/alerts/rules',
  RULE_DETAIL: (ruleId) => `/alerts/rules/${ruleId}`,
  SUBSCRIPTIONS: '/alerts/subscriptions',
};

/**
 * Staff Management Endpoints
 */
export const STAFF_ENDPOINTS = {
  LIST: '/users',
  DETAIL: (staffId) => `/users/${staffId}`,
  UPDATE: (staffId) => `/users/${staffId}`,
  CREATE: '/users',
  ROLES: '/roles',
  PERMISSIONS: '/permissions',
};

/**
 * Configuration Management Endpoints
 */
export const CONFIG_ENDPOINTS = {
  LIST: '/config',
  DETAIL: (key) => `/config/${key}`,
  UPDATE: (key) => `/config/${key}`,
};

/**
 * Audit & Logging Endpoints
 */
export const AUDIT_ENDPOINTS = {
  LOGS: '/audit/logs',
  PII_ACCESS: '/audit/pii-access',
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
  DASHBOARD: DASHBOARD_ENDPOINTS,
  METRICS: METRICS_ENDPOINTS,
  PRIORITY_QUEUE: PRIORITY_QUEUE_ENDPOINTS,
  COMPLAINTS: COMPLAINTS_ENDPOINTS,
  ALERTS: ALERT_ENDPOINTS,
  STAFF: STAFF_ENDPOINTS,
  CONFIG: CONFIG_ENDPOINTS,
  AUDIT: AUDIT_ENDPOINTS,
  HEALTH: HEALTH_ENDPOINT,
};

export default API_ENDPOINTS;
