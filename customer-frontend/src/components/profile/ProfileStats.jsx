/**
 * ProfileStats Component
 * Displays user booking statistics
 */

import React from 'react';
import { motion } from 'framer-motion';
import { Calendar, CheckCircle, Clock, IndianRupee } from 'lucide-react';

const ProfileStats = ({ stats }) => {
  const statCards = [
    {
      label: 'Total Bookings',
      value: stats?.total_bookings || 0,
      icon: Calendar,
      color: 'primary',
      bgColor: 'bg-primary-100',
      textColor: 'text-primary-600',
    },
    {
      label: 'Completed',
      value: stats?.completed_bookings || 0,
      icon: CheckCircle,
      color: 'green',
      bgColor: 'bg-green-100',
      textColor: 'text-green-600',
    },
    {
      label: 'Pending',
      value: stats?.pending_bookings || 0,
      icon: Clock,
      color: 'yellow',
      bgColor: 'bg-yellow-100',
      textColor: 'text-yellow-600',
    },
    {
      label: 'Total Spent',
      value: `₹${stats?.total_spent?.toFixed(2) || '0.00'}`,
      icon: IndianRupee,
      color: 'secondary',
      bgColor: 'bg-secondary-100',
      textColor: 'text-secondary-600',
    },
  ];

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      {statCards.map((stat, index) => {
        const Icon = stat.icon;
        return (
          <motion.div
            key={stat.label}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            whileHover={{ scale: 1.02 }}
            className="bg-white rounded-xl border border-slate-200 p-6 hover:shadow-[0_4px_12px_rgba(108,99,255,0.1)] transition-all duration-200"
          >
            <div className="flex items-center justify-between mb-3">
              <div className={`w-12 h-12 ${stat.bgColor} rounded-lg flex items-center justify-center`}>
                <Icon className={`h-6 w-6 ${stat.textColor}`} />
              </div>
            </div>
            <p className="text-2xl font-bold text-slate-900 mb-1">{stat.value}</p>
            <p className="text-sm text-slate-600">{stat.label}</p>
          </motion.div>
        );
      })}
    </div>
  );
};

export default ProfileStats;

