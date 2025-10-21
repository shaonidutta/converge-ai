/**
 * NotificationPanel Component
 * Dropdown panel displaying notifications
 */

import React, { useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { CheckCheck, Trash2 } from 'lucide-react';
import { format, isToday, isYesterday } from 'date-fns';
import NotificationItem from './NotificationItem';
import NotificationEmpty from './NotificationEmpty';

const NotificationPanel = ({ 
  notifications, 
  onMarkRead, 
  onMarkAllRead, 
  onDelete, 
  onClearAll,
  onClose 
}) => {
  // Group notifications by date
  const groupedNotifications = useMemo(() => {
    const groups = {
      today: [],
      yesterday: [],
      earlier: []
    };

    notifications.forEach(notification => {
      const date = new Date(notification.created_at);
      if (isToday(date)) {
        groups.today.push(notification);
      } else if (isYesterday(date)) {
        groups.yesterday.push(notification);
      } else {
        groups.earlier.push(notification);
      }
    });

    return groups;
  }, [notifications]);

  const hasNotifications = notifications.length > 0;
  const hasUnread = notifications.some(n => !n.read);

  return (
    <motion.div
      initial={{ opacity: 0, y: -10, scale: 0.95 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      exit={{ opacity: 0, y: -10, scale: 0.95 }}
      transition={{ duration: 0.2 }}
      className="absolute top-full right-0 mt-2 w-96 max-w-[calc(100vw-2rem)] bg-white rounded-xl shadow-[0_8px_32px_rgba(0,0,0,0.15)] border border-slate-200 overflow-hidden z-50"
    >
      {/* Header */}
      <div className="p-4 border-b border-slate-200 bg-slate-50">
        <div className="flex items-center justify-between mb-2">
          <h3 className="font-bold text-lg text-slate-900">Notifications</h3>
          {hasNotifications && (
            <div className="flex items-center gap-2">
              {hasUnread && (
                <button
                  onClick={onMarkAllRead}
                  className="text-xs text-primary-600 hover:text-primary-700 font-medium flex items-center gap-1 transition-colors duration-200"
                  title="Mark all as read"
                >
                  <CheckCheck className="h-4 w-4" />
                  Mark all read
                </button>
              )}
              <button
                onClick={onClearAll}
                className="text-xs text-red-600 hover:text-red-700 font-medium flex items-center gap-1 transition-colors duration-200"
                title="Clear all"
              >
                <Trash2 className="h-4 w-4" />
                Clear all
              </button>
            </div>
          )}
        </div>
        {hasNotifications && (
          <p className="text-xs text-slate-600">
            {notifications.length} notification{notifications.length !== 1 ? 's' : ''}
            {hasUnread && ` • ${notifications.filter(n => !n.read).length} unread`}
          </p>
        )}
      </div>

      {/* Notifications List */}
      <div className="max-h-[500px] overflow-y-auto">
        {!hasNotifications ? (
          <NotificationEmpty />
        ) : (
          <AnimatePresence mode="popLayout">
            {/* Today */}
            {groupedNotifications.today.length > 0 && (
              <div key="today">
                <div className="px-4 py-2 bg-slate-50 border-b border-slate-200">
                  <h4 className="text-xs font-semibold text-slate-600 uppercase tracking-wide">
                    Today
                  </h4>
                </div>
                {groupedNotifications.today.map(notification => (
                  <NotificationItem
                    key={notification.id}
                    notification={notification}
                    onMarkRead={onMarkRead}
                    onDelete={onDelete}
                  />
                ))}
              </div>
            )}

            {/* Yesterday */}
            {groupedNotifications.yesterday.length > 0 && (
              <div key="yesterday">
                <div className="px-4 py-2 bg-slate-50 border-b border-slate-200">
                  <h4 className="text-xs font-semibold text-slate-600 uppercase tracking-wide">
                    Yesterday
                  </h4>
                </div>
                {groupedNotifications.yesterday.map(notification => (
                  <NotificationItem
                    key={notification.id}
                    notification={notification}
                    onMarkRead={onMarkRead}
                    onDelete={onDelete}
                  />
                ))}
              </div>
            )}

            {/* Earlier */}
            {groupedNotifications.earlier.length > 0 && (
              <div key="earlier">
                <div className="px-4 py-2 bg-slate-50 border-b border-slate-200">
                  <h4 className="text-xs font-semibold text-slate-600 uppercase tracking-wide">
                    Earlier
                  </h4>
                </div>
                {groupedNotifications.earlier.map(notification => (
                  <NotificationItem
                    key={notification.id}
                    notification={notification}
                    onMarkRead={onMarkRead}
                    onDelete={onDelete}
                  />
                ))}
              </div>
            )}
          </AnimatePresence>
        )}
      </div>
    </motion.div>
  );
};

export default NotificationPanel;

