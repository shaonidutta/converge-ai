/**
 * BookingStatusBadge Component
 * Displays booking status with appropriate color coding
 */

import React from 'react';
import { Clock, CheckCircle, XCircle, AlertCircle, Loader } from 'lucide-react';

const BookingStatusBadge = ({ status, size = 'md' }) => {
  const statusConfig = {
    pending: {
      label: 'Pending',
      icon: Clock,
      bgColor: 'bg-yellow-100',
      textColor: 'text-yellow-800',
      borderColor: 'border-yellow-200',
    },
    confirmed: {
      label: 'Confirmed',
      icon: CheckCircle,
      bgColor: 'bg-blue-100',
      textColor: 'text-blue-800',
      borderColor: 'border-blue-200',
    },
    in_progress: {
      label: 'In Progress',
      icon: Loader,
      bgColor: 'bg-purple-100',
      textColor: 'text-purple-800',
      borderColor: 'border-purple-200',
    },
    completed: {
      label: 'Completed',
      icon: CheckCircle,
      bgColor: 'bg-green-100',
      textColor: 'text-green-800',
      borderColor: 'border-green-200',
    },
    cancelled: {
      label: 'Cancelled',
      icon: XCircle,
      bgColor: 'bg-red-100',
      textColor: 'text-red-800',
      borderColor: 'border-red-200',
    },
  };

  const config = statusConfig[status?.toLowerCase()] || statusConfig.pending;
  const Icon = config.icon;

  const sizeClasses = {
    sm: 'px-2 py-1 text-xs',
    md: 'px-3 py-1.5 text-sm',
    lg: 'px-4 py-2 text-base',
  };

  const iconSizes = {
    sm: 'h-3 w-3',
    md: 'h-4 w-4',
    lg: 'h-5 w-5',
  };

  return (
    <span
      className={`inline-flex items-center gap-1.5 font-medium rounded-full border ${config.bgColor} ${config.textColor} ${config.borderColor} ${sizeClasses[size]}`}
    >
      <Icon className={iconSizes[size]} />
      {config.label}
    </span>
  );
};

export default BookingStatusBadge;

