/**
 * useNotifications Hook
 * Custom hook for managing notifications
 */

import { useState, useEffect, useCallback } from 'react';
import {
  fetchNotifications,
  getUnreadCount,
  markAsRead,
  markAllAsRead,
  deleteNotification,
  clearAllNotifications
} from '../services/notificationService';

/**
 * Hook for fetching and managing notifications
 */
export const useNotifications = (pollingInterval = 30000) => {
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Fetch notifications
  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const [notifs, count] = await Promise.all([
        fetchNotifications(),
        getUnreadCount()
      ]);
      setNotifications(notifs);
      setUnreadCount(count);
    } catch (err) {
      console.error('Error fetching notifications:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  // Initial fetch
  useEffect(() => {
    fetchData();
  }, [fetchData]);

  // Polling for updates
  useEffect(() => {
    if (!pollingInterval) return;

    const interval = setInterval(() => {
      fetchData();
    }, pollingInterval);

    return () => clearInterval(interval);
  }, [pollingInterval, fetchData]);

  // Refetch manually
  const refetch = useCallback(() => {
    fetchData();
  }, [fetchData]);

  return {
    notifications,
    unreadCount,
    loading,
    error,
    refetch
  };
};

/**
 * Hook for notification actions
 */
export const useNotificationActions = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const markRead = useCallback(async (notificationId) => {
    try {
      setLoading(true);
      setError(null);
      await markAsRead(notificationId);
      return true;
    } catch (err) {
      console.error('Error marking as read:', err);
      setError(err.message);
      return false;
    } finally {
      setLoading(false);
    }
  }, []);

  const markAllRead = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      await markAllAsRead();
      return true;
    } catch (err) {
      console.error('Error marking all as read:', err);
      setError(err.message);
      return false;
    } finally {
      setLoading(false);
    }
  }, []);

  const deleteNotif = useCallback(async (notificationId) => {
    try {
      setLoading(true);
      setError(null);
      await deleteNotification(notificationId);
      return true;
    } catch (err) {
      console.error('Error deleting notification:', err);
      setError(err.message);
      return false;
    } finally {
      setLoading(false);
    }
  }, []);

  const clearAll = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      await clearAllNotifications();
      return true;
    } catch (err) {
      console.error('Error clearing all:', err);
      setError(err.message);
      return false;
    } finally {
      setLoading(false);
    }
  }, []);

  return {
    markRead,
    markAllRead,
    deleteNotif,
    clearAll,
    loading,
    error
  };
};

