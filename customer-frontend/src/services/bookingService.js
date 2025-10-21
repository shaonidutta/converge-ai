/**
 * Booking Service
 * Handles all booking-related API calls
 */

import api from './api';
import { format } from 'date-fns';

/**
 * Fetch user's bookings with optional filters
 * @param {Object} params - Query parameters (status, skip, limit)
 * @returns {Promise<Array>} List of bookings
 */
export const fetchBookings = async (params = {}) => {
  try {
    const response = await api.bookings.getAll(params);
    return response.data;
  } catch (error) {
    console.error('Error fetching bookings:', error);
    throw new Error(error.response?.data?.detail || 'Failed to fetch bookings');
  }
};

/**
 * Fetch recent bookings (last 3)
 * @returns {Promise<Array>} List of recent bookings
 */
export const fetchRecentBookings = async () => {
  try {
    const response = await api.bookings.getAll({ limit: 3 });
    return response.data;
  } catch (error) {
    console.error('Error fetching recent bookings:', error);
    throw new Error(error.response?.data?.detail || 'Failed to fetch recent bookings');
  }
};

/**
 * Fetch booking by ID
 * @param {number} bookingId - Booking ID
 * @returns {Promise<Object>} Booking details
 */
export const fetchBookingById = async (bookingId) => {
  try {
    const response = await api.bookings.getById(bookingId);
    return response.data;
  } catch (error) {
    console.error(`Error fetching booking ${bookingId}:`, error);
    throw new Error(error.response?.data?.detail || 'Failed to fetch booking');
  }
};

/**
 * Create new booking from cart
 * @param {Object} bookingData - Booking details (address_id, scheduled_date, scheduled_time, payment_method)
 * @returns {Promise<Object>} Created booking
 */
export const createBooking = async (bookingData) => {
  try {
    const response = await api.bookings.create(bookingData);
    return response.data;
  } catch (error) {
    console.error('Error creating booking:', error);
    throw new Error(error.response?.data?.detail || 'Failed to create booking');
  }
};

/**
 * Cancel booking
 * @param {number} bookingId - Booking ID
 * @param {string} reason - Cancellation reason
 * @returns {Promise<Object>} Updated booking
 */
export const cancelBooking = async (bookingId, reason) => {
  try {
    const response = await api.bookings.cancel(bookingId, { reason });
    return response.data;
  } catch (error) {
    console.error(`Error cancelling booking ${bookingId}:`, error);
    throw new Error(error.response?.data?.detail || 'Failed to cancel booking');
  }
};

/**
 * Reschedule booking
 * @param {number} bookingId - Booking ID
 * @param {Object} rescheduleData - New schedule data (scheduled_date, scheduled_time)
 * @returns {Promise<Object>} Updated booking
 */
export const rescheduleBooking = async (bookingId, rescheduleData) => {
  try {
    const response = await api.bookings.reschedule(bookingId, rescheduleData);
    return response.data;
  } catch (error) {
    console.error(`Error rescheduling booking ${bookingId}:`, error);
    throw new Error(error.response?.data?.detail || 'Failed to reschedule booking');
  }
};

/**
 * Get booking statistics
 * @returns {Promise<Object>} Booking stats (total, pending, completed, cancelled)
 */
export const getBookingStats = async () => {
  try {
    // Fetch all bookings and calculate stats client-side
    // TODO: Replace with backend stats endpoint when available
    const response = await api.bookings.getAll({ limit: 1000 });
    const bookings = response.data;
    
    const stats = {
      total: bookings.length,
      pending: bookings.filter(b => b.status === 'pending').length,
      confirmed: bookings.filter(b => b.status === 'confirmed').length,
      completed: bookings.filter(b => b.status === 'completed').length,
      cancelled: bookings.filter(b => b.status === 'cancelled').length,
    };
    
    return stats;
  } catch (error) {
    console.error('Error fetching booking stats:', error);
    throw new Error(error.response?.data?.detail || 'Failed to fetch booking stats');
  }
};

/**
 * Export all booking service functions
 */
export default {
  fetchBookings,
  fetchRecentBookings,
  fetchBookingById,
  createBooking,
  cancelBooking,
  rescheduleBooking,
  getBookingStats,
};

