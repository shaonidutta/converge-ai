/**
 * QuickActions Component
 * Displays suggested quick action buttons for common tasks
 */

import React from 'react';
import { motion } from 'framer-motion';
import { Sparkles, Calendar, Search, HelpCircle } from 'lucide-react';

const QuickActions = ({ onActionClick }) => {
  const actions = [
    {
      id: 'book',
      icon: Sparkles,
      label: 'Book a Service',
      message: 'I want to book a service',
    },
    {
      id: 'track',
      icon: Calendar,
      label: 'Track Booking',
      message: 'Show me my bookings',
    },
    {
      id: 'browse',
      icon: Search,
      label: 'Browse Services',
      message: 'What services do you offer?',
    },
    {
      id: 'help',
      icon: HelpCircle,
      label: 'Get Help',
      message: 'I need help',
    },
  ];

  return (
    <div className="p-4 space-y-3">
      <p className="text-sm text-slate-600 text-center mb-4">
        Hi! I'm Lisa, your AI assistant. How can I help you today?
      </p>
      <div className="grid grid-cols-2 gap-2">
        {actions.map((action, index) => {
          const Icon = action.icon;
          return (
            <motion.button
              key={action.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.2, delay: index * 0.1 }}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={() => onActionClick(action.message)}
              className="flex flex-col items-center gap-2 p-4 bg-white border border-slate-200 rounded-xl hover:border-primary-300 hover:shadow-[0_4px_12px_rgba(108,99,255,0.1)] transition-all duration-200"
            >
              <div className="w-10 h-10 bg-gradient-to-r from-primary-500 to-secondary-500 rounded-full flex items-center justify-center">
                <Icon className="h-5 w-5 text-white" />
              </div>
              <span className="text-xs font-medium text-slate-700 text-center">
                {action.label}
              </span>
            </motion.button>
          );
        })}
      </div>
    </div>
  );
};

export default QuickActions;

