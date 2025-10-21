/**
 * NotificationBell Component
 * Bell icon with unread badge and dropdown panel
 */

import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Bell } from 'lucide-react';
import { useNotifications, useNotificationActions } from '../../hooks/useNotifications';
import NotificationPanel from './NotificationPanel';

const NotificationBell = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [hasNewNotification, setHasNewNotification] = useState(false);
  const panelRef = useRef(null);
  const buttonRef = useRef(null);

  const { notifications, unreadCount, refetch } = useNotifications(30000); // Poll every 30 seconds
  const { markRead, markAllRead, deleteNotif, clearAll } = useNotificationActions();

  // Detect new notifications for animation
  useEffect(() => {
    if (unreadCount > 0) {
      setHasNewNotification(true);
      const timer = setTimeout(() => setHasNewNotification(false), 1000);
      return () => clearTimeout(timer);
    }
  }, [unreadCount]);

  // Close panel when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (
        panelRef.current &&
        !panelRef.current.contains(event.target) &&
        buttonRef.current &&
        !buttonRef.current.contains(event.target)
      ) {
        setIsOpen(false);
      }
    };

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
      return () => document.removeEventListener('mousedown', handleClickOutside);
    }
  }, [isOpen]);

  const handleToggle = () => {
    setIsOpen(!isOpen);
  };

  const handleMarkRead = async (notificationId) => {
    await markRead(notificationId);
    refetch();
  };

  const handleMarkAllRead = async () => {
    if (confirm('Mark all notifications as read?')) {
      await markAllRead();
      refetch();
    }
  };

  const handleDelete = async (notificationId) => {
    await deleteNotif(notificationId);
    refetch();
  };

  const handleClearAll = async () => {
    if (confirm('Clear all notifications? This action cannot be undone.')) {
      await clearAll();
      refetch();
      setIsOpen(false);
    }
  };

  return (
    <div className="relative">
      {/* Bell Button */}
      <motion.button
        ref={buttonRef}
        onClick={handleToggle}
        animate={hasNewNotification ? { rotate: [0, -15, 15, -15, 15, 0] } : {}}
        transition={{ duration: 0.5 }}
        className="relative p-2 text-slate-600 hover:text-primary-600 hover:bg-primary-50 rounded-lg transition-all duration-200"
        title="Notifications"
      >
        <Bell className="h-6 w-6" />
        
        {/* Unread Badge */}
        {unreadCount > 0 && (
          <motion.span
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            className="absolute -top-1 -right-1 min-w-[20px] h-5 px-1.5 bg-red-500 text-white text-xs font-bold rounded-full flex items-center justify-center"
          >
            {unreadCount > 99 ? '99+' : unreadCount}
          </motion.span>
        )}
      </motion.button>

      {/* Notification Panel */}
      <AnimatePresence>
        {isOpen && (
          <div ref={panelRef}>
            <NotificationPanel
              notifications={notifications}
              onMarkRead={handleMarkRead}
              onMarkAllRead={handleMarkAllRead}
              onDelete={handleDelete}
              onClearAll={handleClearAll}
              onClose={() => setIsOpen(false)}
            />
          </div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default NotificationBell;

