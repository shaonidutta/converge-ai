/**
 * Operations API Service
 * Uses the centralized axios instance from api/axiosConfig.js
 * This ensures consistent authentication and error handling across the ops dashboard
 */

import axiosInstance from '../api/axiosConfig';

// Use the centralized axios instance (no duplicate interceptors)
const apiClient = axiosInstance;

/**
 * Operations API Service Object
 * Contains all API endpoint methods organized by feature
 */
const api = {
  // ============================================
  // Authentication APIs
  // ============================================
  auth: {
    /**
     * Staff login
     * @param {Object} credentials - Login credentials (username/email and password)
     * @returns {Promise} API response with tokens and staff data
     */
    login: (credentials) => apiClient.post('/auth/login', credentials),

    /**
     * Get current staff profile
     * @returns {Promise} API response with staff data
     */
    getMe: () => apiClient.get('/auth/me'),

    /**
     * Refresh access token
     * @param {string} refreshToken - Refresh token
     * @returns {Promise} API response with new access token
     */
    refresh: (refreshToken) => apiClient.post('/auth/refresh', { refresh_token: refreshToken }),

    /**
     * Logout staff
     * @returns {Promise} API response
     */
    logout: () => apiClient.post('/auth/logout'),

    /**
     * Register new staff (admin only)
     * @param {Object} staffData - Staff registration data
     * @returns {Promise} API response
     */
    register: (staffData) => apiClient.post('/auth/register', staffData),
  },

  // ============================================
  // Dashboard & Metrics APIs
  // ============================================
  dashboard: {
    /**
     * Get dashboard metrics overview
     * @param {Object} params - Query parameters (timeframe, filters)
     * @returns {Promise} API response with metrics data
     */
    getMetrics: (params = {}) => apiClient.get('/dashboard/metrics', { params }),

    /**
     * Get priority queue items
     * @param {Object} params - Query parameters (limit, priority, status)
     * @returns {Promise} API response with priority queue data
     */
    getPriorityQueue: (params = {}) => apiClient.get('/dashboard/priority-queue', { params }),
  },

  // ============================================
  // Individual Metrics APIs
  // ============================================
  metrics: {
    /**
     * Get booking metrics
     * @param {Object} params - Query parameters (timeframe, granularity)
     * @returns {Promise} API response with booking metrics
     */
    getBookings: (params = {}) => apiClient.get('/metrics/bookings', { params }),

    /**
     * Get complaint metrics
     * @param {Object} params - Query parameters (timeframe, status)
     * @returns {Promise} API response with complaint metrics
     */
    getComplaints: (params = {}) => apiClient.get('/metrics/complaints', { params }),

    /**
     * Get SLA metrics
     * @param {Object} params - Query parameters (timeframe, service_type)
     * @returns {Promise} API response with SLA metrics
     */
    getSLA: (params = {}) => apiClient.get('/metrics/sla', { params }),

    /**
     * Get revenue metrics
     * @param {Object} params - Query parameters (timeframe, category)
     * @returns {Promise} API response with revenue metrics
     */
    getRevenue: (params = {}) => apiClient.get('/metrics/revenue', { params }),

    /**
     * Get real-time metrics
     * @returns {Promise} API response with real-time data
     */
    getRealtime: () => apiClient.get('/metrics/realtime'),
  },

  // ============================================
  // Priority Queue Management APIs
  // ============================================
  priorityQueue: {
    /**
     * Get priority queue items
     * @param {Object} params - Query parameters (page, limit, priority, status)
     * @returns {Promise} API response with priority queue items
     */
    getItems: (params = {}) => apiClient.get('/priority-queue', { params }),

    /**
     * Get specific priority queue item
     * @param {string} itemId - Item ID
     * @returns {Promise} API response with item details
     */
    getItem: (itemId) => apiClient.get(`/priority-queue/${itemId}`),

    /**
     * Review priority queue item
     * @param {string} itemId - Item ID
     * @param {Object} reviewData - Review data (action, notes, priority)
     * @returns {Promise} API response
     */
    reviewItem: (itemId, reviewData) => apiClient.post(`/priority-queue/${itemId}/review`, reviewData),

    /**
     * Assign priority queue item to staff
     * @param {string} itemId - Item ID
     * @param {Object} assignmentData - Assignment data (staff_id, notes)
     * @returns {Promise} API response
     */
    assignItem: (itemId, assignmentData) => apiClient.post(`/priority-queue/${itemId}/assign`, assignmentData),
  },

  // ============================================
  // Complaints Management APIs
  // ============================================
  complaints: {
    /**
     * Get complaints list
     * @param {Object} params - Query parameters (page, limit, status, priority)
     * @returns {Promise} API response with complaints
     */
    getComplaints: (params = {}) => apiClient.get('/complaints', { params }),

    /**
     * Get specific complaint
     * @param {string} complaintId - Complaint ID
     * @returns {Promise} API response with complaint details
     */
    getComplaint: (complaintId) => apiClient.get(`/complaints/${complaintId}`),

    /**
     * Update complaint
     * @param {string} complaintId - Complaint ID
     * @param {Object} updateData - Update data (status, priority, notes)
     * @returns {Promise} API response
     */
    updateComplaint: (complaintId, updateData) => apiClient.put(`/complaints/${complaintId}`, updateData),

    /**
     * Assign complaint to staff
     * @param {string} complaintId - Complaint ID
     * @param {Object} assignmentData - Assignment data (staff_id, notes)
     * @returns {Promise} API response
     */
    assignComplaint: (complaintId, assignmentData) => apiClient.post(`/complaints/${complaintId}/assign`, assignmentData),
    assign: (complaintId, assignmentData) => apiClient.post(`/complaints/${complaintId}/assign`, assignmentData),

    /**
     * Resolve complaint
     * @param {string} complaintId - Complaint ID
     * @param {Object} resolutionData - Resolution data (resolution, notes)
     * @returns {Promise} API response
     */
    resolveComplaint: (complaintId, resolutionData) => apiClient.post(`/complaints/${complaintId}/resolve`, resolutionData),
    resolve: (complaintId, resolutionData) => apiClient.post(`/complaints/${complaintId}/resolve`, resolutionData),

    /**
     * Get complaint updates/history
     * @param {string} complaintId - Complaint ID
     * @returns {Promise} API response with complaint updates
     */
    getComplaintUpdates: (complaintId) => apiClient.get(`/complaints/${complaintId}/updates`),
    getUpdates: (complaintId) => apiClient.get(`/complaints/${complaintId}/updates`),

    /**
     * Add complaint update
     * @param {string} complaintId - Complaint ID
     * @param {Object} updateData - Update data (message, internal_note)
     * @returns {Promise} API response
     */
    addComplaintUpdate: (complaintId, updateData) => apiClient.post(`/complaints/${complaintId}/updates`, updateData),
    addUpdate: (complaintId, updateData) => apiClient.post(`/complaints/${complaintId}/updates`, updateData),
  },

  // ============================================
  // Staff Management APIs
  // ============================================
  staff: {
    /**
     * Get staff list
     * @param {Object} params - Query parameters (page, limit, role, status)
     * @returns {Promise} API response with staff list
     */
    getStaff: (params = {}) => apiClient.get('/users', { params }),
    getStaffList: (params = {}) => apiClient.get('/users', { params }),

    /**
     * Get specific staff member
     * @param {string} staffId - Staff ID
     * @returns {Promise} API response with staff details
     */
    getStaffMember: (staffId) => apiClient.get(`/users/${staffId}`),

    /**
     * Update staff member
     * @param {string} staffId - Staff ID
     * @param {Object} updateData - Update data (role, permissions, status)
     * @returns {Promise} API response
     */
    updateStaffMember: (staffId, updateData) => apiClient.put(`/users/${staffId}`, updateData),

    /**
     * Create new staff member
     * @param {Object} staffData - Staff data (name, email, role, permissions)
     * @returns {Promise} API response
     */
    createStaffMember: (staffData) => apiClient.post('/users', staffData),

    /**
     * Get available roles
     * @returns {Promise} API response with roles list
     */
    getRoles: () => apiClient.get('/roles'),

    /**
     * Get available permissions
     * @returns {Promise} API response with permissions list
     */
    getPermissions: () => apiClient.get('/permissions'),
  },

  // ============================================
  // Analytics APIs
  // ============================================
  analytics: {
    /**
     * Get KPI metrics for analytics dashboard
     * @param {Object} params - Query parameters (time_range, start_date, end_date)
     * @returns {Promise} API response with KPI data
     */
    getKPIs: (params = {}) => apiClient.get('/analytics/kpis', { params }),

    /**
     * Get trend data for charts
     * @param {Object} params - Query parameters (time_range, start_date, end_date)
     * @returns {Promise} API response with trend data
     */
    getTrends: (params = {}) => apiClient.get('/analytics/trends', { params }),

    /**
     * Get service category distribution
     * @param {Object} params - Query parameters (time_range, start_date, end_date)
     * @returns {Promise} API response with category data
     */
    getCategories: (params = {}) => apiClient.get('/analytics/categories', { params }),

    /**
     * Get booking status distribution
     * @param {Object} params - Query parameters (time_range, start_date, end_date)
     * @returns {Promise} API response with status data
     */
    getStatus: (params = {}) => apiClient.get('/analytics/status', { params }),

    /**
     * Get performance metrics vs targets
     * @param {Object} params - Query parameters (time_range, start_date, end_date)
     * @returns {Promise} API response with performance data
     */
    getPerformance: (params = {}) => apiClient.get('/analytics/performance', { params }),
  },

  // ============================================
  // Health Check API
  // ============================================
  health: {
    /**
     * Check API health
     * @returns {Promise} API response with health status
     */
    check: () => apiClient.get('/health'),
  },

  // Reports API
  reports: {
    /**
     * Generate a report
     * @param {Object} data - Report generation parameters
     * @returns {Promise} API response with generated report
     */
    generate: (data) => apiClient.post('/ops/reports/generate', data, { responseType: 'blob' }),

    /**
     * Get list of reports
     * @param {Object} params - Query parameters
     * @returns {Promise} API response with reports list
     */
    list: (params) => apiClient.get('/ops/reports', { params }),

    /**
     * Get report by ID
     * @param {number} id - Report ID
     * @returns {Promise} API response with report details
     */
    getById: (id) => apiClient.get(`/ops/reports/${id}`),

    /**
     * Download report
     * @param {number} id - Report ID
     * @returns {Promise} API response with report file
     */
    download: (id) => apiClient.get(`/ops/reports/${id}/download`, { responseType: 'blob' }),

    /**
     * Delete report
     * @param {number} id - Report ID
     * @returns {Promise} API response
     */
    delete: (id) => apiClient.delete(`/ops/reports/${id}`),

    /**
     * Schedule report
     * @param {Object} data - Schedule parameters
     * @returns {Promise} API response
     */
    schedule: (data) => apiClient.post('/ops/reports/schedule', data),
  },
};

export default api;
