/**
 * NotificationItem Component
 * Single notification display with actions
 */

import React from 'react';
import { motion } from 'framer-motion';
import { 
  CheckCircle, 
  XCircle, 
  Clock, 
  Tag, 
  Gift, 
  Bell, 
  Info, 
  MessageCircle,
  X 
} from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';
import { useNavigate } from 'react-router-dom';

const NotificationItem = ({ notification, onMarkRead, onDelete }) => {
  const navigate = useNavigate();

  // Get icon based on notification type and icon name
  const getIcon = () => {
    const iconMap = {
      CheckCircle,
      XCircle,
      Clock,
      Tag,
      Gift,
      Bell,
      Info,
      MessageCircle
    };
    
    const IconComponent = iconMap[notification.icon] || Bell;
    return IconComponent;
  };

  // Get color based on notification type
  const getTypeColor = () => {
    const colorMap = {
      booking_update: 'text-primary-500 bg-primary-50',
      promotion: 'text-accent-500 bg-accent-50',
      system: 'text-slate-500 bg-slate-50',
      chat: 'text-secondary-500 bg-secondary-50'
    };
    
    return colorMap[notification.type] || 'text-slate-500 bg-slate-50';
  };

  // Handle notification click
  const handleClick = () => {
    // Mark as read
    if (!notification.read) {
      onMarkRead(notification.id);
    }
    
    // Navigate if link exists
    if (notification.metadata?.link) {
      navigate(notification.metadata.link);
    }
  };

  // Handle delete
  const handleDelete = (e) => {
    e.stopPropagation();
    onDelete(notification.id);
  };

  const Icon = getIcon();
  const typeColor = getTypeColor();
  const timeAgo = formatDistanceToNow(new Date(notification.created_at), { addSuffix: true });

  return (
    <motion.div
      initial={{ opacity: 0, y: -10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, x: -100 }}
      transition={{ duration: 0.2 }}
      onClick={handleClick}
      className={`
        p-4 border-b border-slate-200 cursor-pointer transition-all duration-200
        hover:bg-slate-50
        ${notification.read ? 'bg-white' : 'bg-primary-50/30'}
      `}
    >
      <div className="flex items-start gap-3">
        {/* Icon */}
        <div className={`flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center ${typeColor}`}>
          <Icon className="h-5 w-5" />
        </div>

        {/* Content */}
        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between gap-2 mb-1">
            <h4 className={`font-semibold text-sm ${notification.read ? 'text-slate-700' : 'text-slate-900'}`}>
              {notification.title}
            </h4>
            
            {/* Delete Button */}
            <button
              onClick={handleDelete}
              className="flex-shrink-0 p-1 text-slate-400 hover:text-red-500 hover:bg-red-50 rounded transition-colors duration-200"
              title="Delete notification"
            >
              <X className="h-4 w-4" />
            </button>
          </div>

          <p className={`text-sm mb-2 ${notification.read ? 'text-slate-500' : 'text-slate-700'}`}>
            {notification.message}
          </p>

          <div className="flex items-center gap-2">
            <span className="text-xs text-slate-400">{timeAgo}</span>
            {!notification.read && (
              <span className="w-2 h-2 bg-primary-500 rounded-full"></span>
            )}
          </div>
        </div>
      </div>
    </motion.div>
  );
};

export default NotificationItem;

