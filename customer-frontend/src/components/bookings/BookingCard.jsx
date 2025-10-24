/**
 * BookingCard Component
 * Displays booking information in a card format
 */

import React from 'react';
import { motion } from 'framer-motion';
import { Calendar, Clock, MapPin, IndianRupee, Eye, XCircle, RefreshCw } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { format } from 'date-fns';
import BookingStatusBadge from './BookingStatusBadge';

const BookingCard = ({ booking, onCancel, onReschedule }) => {
  const navigate = useNavigate();

  const formatDate = (dateString) => {
    try {
      return format(new Date(dateString), 'MMM d, yyyy');
    } catch {
      return dateString;
    }
  };

  const formatTime = (timeString) => {
    try {
      const [hours] = timeString.split(':');
      const hour = parseInt(hours);
      const period = hour >= 12 ? 'PM' : 'AM';
      const displayHour = hour > 12 ? hour - 12 : hour === 0 ? 12 : hour;
      return `${displayHour}:00 ${period}`;
    } catch {
      return timeString;
    }
  };

  const canCancel = ['pending', 'confirmed'].includes(booking.status?.toLowerCase());
  const canReschedule = ['pending', 'confirmed'].includes(booking.status?.toLowerCase());

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ scale: 1.01 }}
      className="bg-white rounded-xl border border-slate-200 p-6 hover:shadow-[0_4px_12px_rgba(108,99,255,0.1)] transition-all duration-200 cursor-pointer"
      onClick={() => navigate(`/bookings/${booking.id}`)}
    >
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 bg-gradient-to-br from-primary-100 to-secondary-100 rounded-lg flex items-center justify-center">
            <span className="text-2xl">{booking.rate_card?.subcategory?.icon || '🛠️'}</span>
          </div>
          <div>
            <h3 className="font-semibold text-slate-900">
              {booking.rate_card?.subcategory?.name || 'Service'}
            </h3>
            <p className="text-sm text-slate-600">
              {booking.rate_card?.subcategory?.category?.name || 'Category'}
            </p>
          </div>
        </div>
        <BookingStatusBadge status={booking.status} size="sm" />
      </div>

      {/* Details */}
      <div className="space-y-2 mb-4">
        <div className="flex items-center gap-2 text-sm text-slate-600">
          <Calendar className="h-4 w-4" />
          <span>{formatDate(booking.scheduled_date)}</span>
        </div>
        <div className="flex items-center gap-2 text-sm text-slate-600">
          <Clock className="h-4 w-4" />
          <span>{formatTime(booking.scheduled_time)}</span>
        </div>
        <div className="flex items-center gap-2 text-sm text-slate-600">
          <MapPin className="h-4 w-4" />
          <span className="truncate">
            {booking.address?.city || 'Address not available'}
          </span>
        </div>
      </div>

      {/* Price */}
      <div className="flex items-center justify-between pt-4 border-t border-slate-200">
        <div className="flex items-center gap-1 text-lg font-bold text-slate-900">
          <IndianRupee className="h-5 w-5" />
          <span>{booking.total_amount ? parseFloat(booking.total_amount).toFixed(2) : '0.00'}</span>
        </div>

        {/* Quick Actions */}
        <div className="flex items-center gap-2">
          <motion.button
            onClick={(e) => {
              e.stopPropagation();
              navigate(`/bookings/${booking.id}`);
            }}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className="p-2 text-primary-500 hover:bg-primary-50 rounded-lg transition-colors duration-200"
            title="View Details"
          >
            <Eye className="h-4 w-4" />
          </motion.button>

          {canReschedule && (
            <motion.button
              onClick={(e) => {
                e.stopPropagation();
                onReschedule(booking);
              }}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className="p-2 text-blue-500 hover:bg-blue-50 rounded-lg transition-colors duration-200"
              title="Reschedule"
            >
              <RefreshCw className="h-4 w-4" />
            </motion.button>
          )}

          {canCancel && (
            <motion.button
              onClick={(e) => {
                e.stopPropagation();
                onCancel(booking);
              }}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className="p-2 text-red-500 hover:bg-red-50 rounded-lg transition-colors duration-200"
              title="Cancel"
            >
              <XCircle className="h-4 w-4" />
            </motion.button>
          )}
        </div>
      </div>
    </motion.div>
  );
};

export default BookingCard;

