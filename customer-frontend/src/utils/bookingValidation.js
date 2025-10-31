/**
 * Booking Validation Utilities
 * Contains validation logic for booking operations like cancellation and rescheduling
 */

import { format, isAfter, startOfDay, parseISO } from 'date-fns';

/**
 * Check if a booking can be cancelled based on its scheduled date
 * Business Rule: Users can only cancel bookings scheduled for tomorrow or later
 *
 * @param {string} scheduledDate - The booking's scheduled date (YYYY-MM-DD format)
 * @returns {boolean} True if booking can be cancelled, false otherwise
 */
export const canCancelBookingByDate = (scheduledDate) => {
  try {
    if (!scheduledDate) {
      return false;
    }

    // Get today's date at start of day (00:00:00)
    const today = startOfDay(new Date());

    // Parse the scheduled date and get start of that day
    const bookingDate = startOfDay(parseISO(scheduledDate));

    // Booking can be cancelled only if it's scheduled for tomorrow or later
    // This means the booking date must be after today
    return isAfter(bookingDate, today);
  } catch (error) {
    console.error('Error validating booking cancellation date:', error);
    return false;
  }
};

/**
 * Check if a booking can be rescheduled based on its scheduled date
 * Business Rule: Users can only reschedule bookings scheduled for tomorrow or later
 *
 * @param {string} scheduledDate - The booking's scheduled date (YYYY-MM-DD format)
 * @returns {boolean} True if booking can be rescheduled, false otherwise
 */
export const canRescheduleBookingByDate = (scheduledDate) => {
  // Same logic as cancellation for now
  return canCancelBookingByDate(scheduledDate);
};

/**
 * Get a human-readable reason why a booking cannot be cancelled
 *
 * @param {string} scheduledDate - The booking's scheduled date (YYYY-MM-DD format)
 * @returns {string} Reason message
 */
export const getCancellationRestrictionReason = (scheduledDate) => {
  try {
    if (!scheduledDate) {
      return 'Invalid booking date';
    }

    const today = startOfDay(new Date());
    const bookingDate = startOfDay(parseISO(scheduledDate));

    if (isAfter(bookingDate, today)) {
      return ''; // No restriction
    }

    // Check if it's today
    if (bookingDate.getTime() === today.getTime()) {
      return 'Bookings scheduled for today cannot be cancelled';
    }

    // It's in the past
    return 'Past bookings cannot be cancelled';
  } catch (error) {
    return 'Unable to validate booking date';
  }
};

/**
 * Check if a booking can be cancelled based on both status and date
 *
 * @param {Object} booking - The booking object
 * @param {string} booking.status - The booking status
 * @param {string} booking.preferred_date - The booking's preferred date (YYYY-MM-DD format)
 * @returns {Object} Object with canCancel boolean and reason string
 */
export const validateBookingCancellation = (booking) => {
  if (!booking) {
    return { canCancel: false, reason: 'Invalid booking' };
  }

  // Check status first
  const validStatuses = ['pending', 'confirmed'];
  const hasValidStatus = validStatuses.includes(booking.status?.toLowerCase());

  if (!hasValidStatus) {
    return {
      canCancel: false,
      reason: `Cannot cancel booking with status: ${booking.status}`
    };
  }

  // Check date - use preferred_date (backend field name) or scheduled_date (legacy)
  const bookingDate = booking.preferred_date || booking.scheduled_date;
  const canCancelByDate = canCancelBookingByDate(bookingDate);

  if (!canCancelByDate) {
    return {
      canCancel: false,
      reason: getCancellationRestrictionReason(bookingDate)
    };
  }

  return { canCancel: true, reason: '' };
};

/**
 * Check if a booking can be rescheduled based on both status and date
 *
 * @param {Object} booking - The booking object
 * @param {string} booking.status - The booking status
 * @param {string} booking.preferred_date - The booking's preferred date (YYYY-MM-DD format)
 * @returns {Object} Object with canReschedule boolean and reason string
 */
export const validateBookingReschedule = (booking) => {
  if (!booking) {
    return { canReschedule: false, reason: 'Invalid booking' };
  }

  // Check status first
  const validStatuses = ['pending', 'confirmed'];
  const hasValidStatus = validStatuses.includes(booking.status?.toLowerCase());

  if (!hasValidStatus) {
    return {
      canReschedule: false,
      reason: `Cannot reschedule booking with status: ${booking.status}`
    };
  }

  // Check date - use preferred_date (backend field name) or scheduled_date (legacy)
  const bookingDate = booking.preferred_date || booking.scheduled_date;
  const canRescheduleByDate = canRescheduleBookingByDate(bookingDate);

  if (!canRescheduleByDate) {
    return {
      canReschedule: false,
      reason: getCancellationRestrictionReason(bookingDate) // Same logic for now
    };
  }

  return { canReschedule: true, reason: '' };
};
