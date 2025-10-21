/**
 * BookingCard Component
 * Reusable card for displaying booking information
 */

import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import {
  Calendar,
  Clock,
  MapPin,
  ArrowRight,
  RotateCcw,
  X,
} from 'lucide-react';
import { Button } from '../ui/button';

/**
 * Get status badge styling
 */
const getStatusBadge = (status) => {
  const statusConfig = {
    pending: {
      bg: 'bg-yellow-100',
      text: 'text-yellow-800',
      label: 'Pending',
    },
    confirmed: {
      bg: 'bg-blue-100',
      text: 'text-blue-800',
      label: 'Confirmed',
    },
    in_progress: {
      bg: 'bg-purple-100',
      text: 'text-purple-800',
      label: 'In Progress',
    },
    completed: {
      bg: 'bg-green-100',
      text: 'text-green-800',
      label: 'Completed',
    },
    cancelled: {
      bg: 'bg-red-100',
      text: 'text-red-800',
      label: 'Cancelled',
    },
  };

  const config = statusConfig[status] || statusConfig.pending;

  return (
    <span
      className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold ${config.bg} ${config.text}`}
    >
      {config.label}
    </span>
  );
};

/**
 * Format date to readable string
 */
const formatDate = (dateString) => {
  const date = new Date(dateString);
  return date.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  });
};

/**
 * Format time to readable string
 */
const formatTime = (timeString) => {
  if (!timeString) return '';
  
  // Handle both "HH:MM:SS" and "HH:MM" formats
  const parts = timeString.split(':');
  const hours = parseInt(parts[0], 10);
  const minutes = parts[1];
  
  const period = hours >= 12 ? 'PM' : 'AM';
  const displayHours = hours % 12 || 12;
  
  return `${displayHours}:${minutes} ${period}`;
};

/**
 * BookingCard Component
 * @param {Object} props
 * @param {Object} props.booking - Booking data
 * @param {Function} props.onReschedule - Callback for reschedule action
 * @param {Function} props.onCancel - Callback for cancel action
 * @param {number} props.index - Card index for staggered animation
 */
const BookingCard = ({ booking, onReschedule, onCancel, index = 0 }) => {
  const navigate = useNavigate();

  const handleViewDetails = () => {
    navigate(`/bookings/${booking.id}`);
  };

  const canReschedule = ['pending', 'confirmed'].includes(booking.status);
  const canCancel = ['pending', 'confirmed'].includes(booking.status);

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, delay: index * 0.1 }}
      className="group bg-white rounded-xl p-6 shadow-[0_4px_20px_rgba(0,0,0,0.05)] hover:shadow-[0_6px_24px_rgba(108,99,255,0.12)] transition-all duration-300"
    >
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1">
          <h3 className="text-lg font-bold text-slate-900 mb-1">
            Booking #{booking.id}
          </h3>
          <p className="text-sm text-slate-600">
            {booking.items?.length || 0} service(s)
          </p>
        </div>
        {getStatusBadge(booking.status)}
      </div>

      {/* Booking Details */}
      <div className="space-y-3 mb-4">
        {/* Date */}
        <div className="flex items-center gap-3 text-sm text-slate-600">
          <div className="w-8 h-8 rounded-lg bg-primary-50 flex items-center justify-center">
            <Calendar className="h-4 w-4 text-primary-600" />
          </div>
          <span>{formatDate(booking.scheduled_date)}</span>
        </div>

        {/* Time */}
        {booking.scheduled_time && (
          <div className="flex items-center gap-3 text-sm text-slate-600">
            <div className="w-8 h-8 rounded-lg bg-secondary-50 flex items-center justify-center">
              <Clock className="h-4 w-4 text-secondary-600" />
            </div>
            <span>{formatTime(booking.scheduled_time)}</span>
          </div>
        )}

        {/* Address */}
        {booking.address && (
          <div className="flex items-start gap-3 text-sm text-slate-600">
            <div className="w-8 h-8 rounded-lg bg-accent-50 flex items-center justify-center flex-shrink-0">
              <MapPin className="h-4 w-4 text-accent-600" />
            </div>
            <span className="line-clamp-2">
              {booking.address.address_line1}, {booking.address.city}, {booking.address.pincode}
            </span>
          </div>
        )}

        {/* Total Amount */}
        <div className="pt-3 border-t border-slate-200">
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium text-slate-600">Total Amount</span>
            <span className="text-lg font-bold text-primary-600">
              ₹{booking.total_amount?.toFixed(2) || '0.00'}
            </span>
          </div>
        </div>
      </div>

      {/* Actions */}
      <div className="flex items-center gap-2">
        <Button
          onClick={handleViewDetails}
          variant="outline"
          size="sm"
          className="flex-1 hover:bg-primary-50 hover:border-primary-300 hover:text-primary-700 transition-all duration-300"
        >
          View Details
          <ArrowRight className="h-4 w-4 ml-2" />
        </Button>

        {canReschedule && (
          <Button
            onClick={() => onReschedule?.(booking)}
            variant="outline"
            size="sm"
            className="hover:bg-secondary-50 hover:border-secondary-300 hover:text-secondary-700 transition-all duration-300"
          >
            <RotateCcw className="h-4 w-4" />
          </Button>
        )}

        {canCancel && (
          <Button
            onClick={() => onCancel?.(booking)}
            variant="outline"
            size="sm"
            className="hover:bg-red-50 hover:border-red-300 hover:text-red-700 transition-all duration-300"
          >
            <X className="h-4 w-4" />
          </Button>
        )}
      </div>
    </motion.div>
  );
};

export default BookingCard;

