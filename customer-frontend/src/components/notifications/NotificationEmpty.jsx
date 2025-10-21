/**
 * NotificationEmpty Component
 * Empty state for notifications
 */

import React from 'react';
import { Bell } from 'lucide-react';

const NotificationEmpty = () => {
  return (
    <div className="flex flex-col items-center justify-center py-12 px-4">
      <div className="w-16 h-16 bg-slate-100 rounded-full flex items-center justify-center mb-4">
        <Bell className="h-8 w-8 text-slate-400" />
      </div>
      <h3 className="text-lg font-semibold text-slate-700 mb-2">
        No notifications
      </h3>
      <p className="text-sm text-slate-500 text-center max-w-xs">
        You're all caught up! We'll notify you when something important happens.
      </p>
    </div>
  );
};

export default NotificationEmpty;

