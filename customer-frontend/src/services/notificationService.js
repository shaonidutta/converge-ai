/**
 * Notification Service
 * Handles notification operations
 * 
 * Note: This is a frontend-only implementation using localStorage
 * In production, this should be replaced with backend API calls
 */

const NOTIFICATIONS_KEY = 'convergeai_notifications';
const MAX_NOTIFICATIONS = 50;

/**
 * Get all notifications from localStorage
 */
export const fetchNotifications = async () => {
  try {
    const stored = localStorage.getItem(NOTIFICATIONS_KEY);
    if (!stored) return [];
    
    const notifications = JSON.parse(stored);
    // Sort by created_at descending (newest first)
    return notifications.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
  } catch (error) {
    console.error('Error fetching notifications:', error);
    return [];
  }
};

/**
 * Get unread notifications count
 */
export const getUnreadCount = async () => {
  try {
    const notifications = await fetchNotifications();
    return notifications.filter(n => !n.read).length;
  } catch (error) {
    console.error('Error getting unread count:', error);
    return 0;
  }
};

/**
 * Mark notification as read
 */
export const markAsRead = async (notificationId) => {
  try {
    const notifications = await fetchNotifications();
    const updated = notifications.map(n => 
      n.id === notificationId ? { ...n, read: true, read_at: new Date().toISOString() } : n
    );
    localStorage.setItem(NOTIFICATIONS_KEY, JSON.stringify(updated));
    return true;
  } catch (error) {
    console.error('Error marking notification as read:', error);
    throw new Error('Failed to mark notification as read');
  }
};

/**
 * Mark all notifications as read
 */
export const markAllAsRead = async () => {
  try {
    const notifications = await fetchNotifications();
    const updated = notifications.map(n => ({ 
      ...n, 
      read: true, 
      read_at: n.read_at || new Date().toISOString() 
    }));
    localStorage.setItem(NOTIFICATIONS_KEY, JSON.stringify(updated));
    return true;
  } catch (error) {
    console.error('Error marking all as read:', error);
    throw new Error('Failed to mark all as read');
  }
};

/**
 * Delete notification
 */
export const deleteNotification = async (notificationId) => {
  try {
    const notifications = await fetchNotifications();
    const filtered = notifications.filter(n => n.id !== notificationId);
    localStorage.setItem(NOTIFICATIONS_KEY, JSON.stringify(filtered));
    return true;
  } catch (error) {
    console.error('Error deleting notification:', error);
    throw new Error('Failed to delete notification');
  }
};

/**
 * Clear all notifications
 */
export const clearAllNotifications = async () => {
  try {
    localStorage.setItem(NOTIFICATIONS_KEY, JSON.stringify([]));
    return true;
  } catch (error) {
    console.error('Error clearing notifications:', error);
    throw new Error('Failed to clear notifications');
  }
};

/**
 * Create a new notification
 * This is used internally to generate notifications from booking events
 */
export const createNotification = async (notificationData) => {
  try {
    const notifications = await fetchNotifications();
    
    const newNotification = {
      id: Date.now(), // Simple ID generation
      type: notificationData.type || 'system',
      title: notificationData.title,
      message: notificationData.message,
      icon: notificationData.icon || 'Bell',
      read: false,
      created_at: new Date().toISOString(),
      metadata: notificationData.metadata || {}
    };
    
    // Add to beginning of array
    const updated = [newNotification, ...notifications];
    
    // Keep only MAX_NOTIFICATIONS
    const trimmed = updated.slice(0, MAX_NOTIFICATIONS);
    
    localStorage.setItem(NOTIFICATIONS_KEY, JSON.stringify(trimmed));
    
    return newNotification;
  } catch (error) {
    console.error('Error creating notification:', error);
    throw new Error('Failed to create notification');
  }
};

/**
 * Helper: Create booking notification
 */
export const createBookingNotification = async (booking, action) => {
  const notificationMap = {
    created: {
      title: 'Booking Created',
      message: `Your booking #${booking.booking_number} has been created successfully`,
      icon: 'CheckCircle',
      type: 'booking_update'
    },
    confirmed: {
      title: 'Booking Confirmed',
      message: `Your booking #${booking.booking_number} has been confirmed`,
      icon: 'CheckCircle',
      type: 'booking_update'
    },
    cancelled: {
      title: 'Booking Cancelled',
      message: `Your booking #${booking.booking_number} has been cancelled`,
      icon: 'XCircle',
      type: 'booking_update'
    },
    rescheduled: {
      title: 'Booking Rescheduled',
      message: `Your booking #${booking.booking_number} has been rescheduled`,
      icon: 'Clock',
      type: 'booking_update'
    },
    completed: {
      title: 'Booking Completed',
      message: `Your booking #${booking.booking_number} has been completed. Please leave a review!`,
      icon: 'CheckCircle',
      type: 'booking_update'
    }
  };
  
  const config = notificationMap[action];
  if (!config) return null;
  
  return await createNotification({
    ...config,
    metadata: {
      booking_id: booking.id,
      booking_number: booking.booking_number,
      link: `/bookings/${booking.id}`
    }
  });
};

/**
 * Helper: Create promotion notification
 */
export const createPromotionNotification = async (promotion) => {
  return await createNotification({
    type: 'promotion',
    title: promotion.title || 'Special Offer',
    message: promotion.message,
    icon: 'Tag',
    metadata: {
      promotion_id: promotion.id,
      link: promotion.link || '/home'
    }
  });
};

/**
 * Helper: Create system notification
 */
export const createSystemNotification = async (title, message, metadata = {}) => {
  return await createNotification({
    type: 'system',
    title,
    message,
    icon: 'Info',
    metadata
  });
};

/**
 * Helper: Create chat notification
 */
export const createChatNotification = async (message) => {
  return await createNotification({
    type: 'chat',
    title: 'New Message from Lisa',
    message: message.substring(0, 100) + (message.length > 100 ? '...' : ''),
    icon: 'MessageCircle',
    metadata: {
      link: '/home' // Opens chat
    }
  });
};

