/**
 * useBookings Hook
 * Custom hook for fetching and managing bookings
 */

import { useState, useEffect, useCallback } from 'react';
import {
  fetchBookings,
  fetchRecentBookings,
  fetchBookingById,
  cancelBooking,
  rescheduleBooking,
} from '../services/bookingService';

/**
 * Hook to fetch all bookings with optional filters
 * @param {Object} params - Query parameters (status, skip, limit)
 * @returns {Object} { bookings, loading, error, refetch }
 */
export const useBookings = (params = {}) => {
  const [bookings, setBookings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const loadBookings = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await fetchBookings(params);
      setBookings(data);
    } catch (err) {
      setError(err.message);
      console.error('Error loading bookings:', err);
    } finally {
      setLoading(false);
    }
  }, [params]);

  useEffect(() => {
    loadBookings();
  }, [loadBookings]);

  const refetch = useCallback(() => {
    loadBookings();
  }, [loadBookings]);

  return { bookings, loading, error, refetch };
};

/**
 * Hook to fetch recent bookings (last 3)
 * @returns {Object} { bookings, loading, error, refetch }
 */
export const useRecentBookings = () => {
  const [bookings, setBookings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const loadRecentBookings = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await fetchRecentBookings();
      setBookings(data);
    } catch (err) {
      setError(err.message);
      console.error('Error loading recent bookings:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadRecentBookings();
  }, [loadRecentBookings]);

  const refetch = useCallback(() => {
    loadRecentBookings();
  }, [loadRecentBookings]);

  return { bookings, loading, error, refetch };
};

/**
 * Hook to fetch a single booking by ID
 * @param {number} bookingId - Booking ID
 * @returns {Object} { booking, loading, error, refetch }
 */
export const useBooking = (bookingId) => {
  const [booking, setBooking] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const loadBooking = useCallback(async () => {
    if (!bookingId) {
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      setError(null);
      const data = await fetchBookingById(bookingId);
      setBooking(data);
    } catch (err) {
      setError(err.message);
      console.error(`Error loading booking ${bookingId}:`, err);
    } finally {
      setLoading(false);
    }
  }, [bookingId]);

  useEffect(() => {
    loadBooking();
  }, [loadBooking]);

  const refetch = useCallback(() => {
    loadBooking();
  }, [loadBooking]);

  return { booking, loading, error, refetch };
};

/**
 * Hook to manage booking actions (cancel, reschedule)
 * @returns {Object} { cancelBooking, rescheduleBooking, loading, error }
 */
export const useBookingActions = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleCancelBooking = useCallback(async (bookingId, reason) => {
    try {
      setLoading(true);
      setError(null);
      const data = await cancelBooking(bookingId, reason);
      return data;
    } catch (err) {
      setError(err.message);
      console.error(`Error cancelling booking ${bookingId}:`, err);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const handleRescheduleBooking = useCallback(async (bookingId, rescheduleData) => {
    try {
      setLoading(true);
      setError(null);
      const data = await rescheduleBooking(bookingId, rescheduleData);
      return data;
    } catch (err) {
      setError(err.message);
      console.error(`Error rescheduling booking ${bookingId}:`, err);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  return {
    cancelBooking: handleCancelBooking,
    rescheduleBooking: handleRescheduleBooking,
    loading,
    error,
  };
};

/**
 * Export all hooks
 */
export default {
  useBookings,
  useRecentBookings,
  useBooking,
  useBookingActions,
};

