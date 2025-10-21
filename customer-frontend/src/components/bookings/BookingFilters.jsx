/**
 * BookingFilters Component
 * Filter bookings by status
 */

import React from 'react';
import { motion } from 'framer-motion';

const BookingFilters = ({ activeFilter, onFilterChange }) => {
  const filters = [
    { value: 'all', label: 'All Bookings', count: null },
    { value: 'pending', label: 'Pending', color: 'yellow' },
    { value: 'confirmed', label: 'Confirmed', color: 'blue' },
    { value: 'in_progress', label: 'In Progress', color: 'purple' },
    { value: 'completed', label: 'Completed', color: 'green' },
    { value: 'cancelled', label: 'Cancelled', color: 'red' },
  ];

  const getColorClasses = (color, isActive) => {
    if (color === 'yellow') {
      return isActive
        ? 'bg-yellow-100 text-yellow-800 border-yellow-300'
        : 'hover:bg-yellow-50 hover:border-yellow-200';
    }
    if (color === 'blue') {
      return isActive
        ? 'bg-blue-100 text-blue-800 border-blue-300'
        : 'hover:bg-blue-50 hover:border-blue-200';
    }
    if (color === 'purple') {
      return isActive
        ? 'bg-purple-100 text-purple-800 border-purple-300'
        : 'hover:bg-purple-50 hover:border-purple-200';
    }
    if (color === 'green') {
      return isActive
        ? 'bg-green-100 text-green-800 border-green-300'
        : 'hover:bg-green-50 hover:border-green-200';
    }
    if (color === 'red') {
      return isActive
        ? 'bg-red-100 text-red-800 border-red-300'
        : 'hover:bg-red-50 hover:border-red-200';
    }
    return isActive
      ? 'bg-primary-100 text-primary-800 border-primary-300'
      : 'hover:bg-slate-50 hover:border-slate-300';
  };

  return (
    <div className="flex flex-wrap gap-2">
      {filters.map((filter) => {
        const isActive = activeFilter === filter.value;
        return (
          <motion.button
            key={filter.value}
            onClick={() => onFilterChange(filter.value)}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            className={`px-4 py-2 rounded-lg border-2 font-medium text-sm transition-all duration-200 ${
              isActive
                ? getColorClasses(filter.color, true)
                : `bg-white text-slate-700 border-slate-200 ${getColorClasses(filter.color, false)}`
            }`}
          >
            {filter.label}
          </motion.button>
        );
      })}
    </div>
  );
};

export default BookingFilters;

