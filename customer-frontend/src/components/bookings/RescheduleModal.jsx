/**
 * RescheduleModal Component
 * Modal for rescheduling a booking
 */

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, RefreshCw } from 'lucide-react';
import DatePicker from 'react-datepicker';
import { addDays, format } from 'date-fns';
import 'react-datepicker/dist/react-datepicker.css';

const RescheduleModal = ({ isOpen, onClose, onConfirm, booking, loading }) => {
  const [newDate, setNewDate] = useState(null);
  const [newTime, setNewTime] = useState('');
  const [reason, setReason] = useState('');

  const timeSlots = [
    '08:00', '09:00', '10:00', '11:00', '12:00',
    '13:00', '14:00', '15:00', '16:00', '17:00',
    '18:00', '19:00', '20:00'
  ];

  const formatTimeSlot = (time) => {
    const [hours] = time.split(':');
    const hour = parseInt(hours);
    const period = hour >= 12 ? 'PM' : 'AM';
    const displayHour = hour > 12 ? hour - 12 : hour === 0 ? 12 : hour;
    return `${displayHour}:00 ${period}`;
  };

  const handleConfirm = () => {
    if (newDate && newTime) {
      onConfirm({
        new_date: format(newDate, 'yyyy-MM-dd'),
        new_time: newTime,
        reason: reason || 'Rescheduled by customer',
      });
    }
  };

  const handleClose = () => {
    setNewDate(null);
    setNewTime('');
    setReason('');
    onClose();
  };

  if (!isOpen) return null;

  return (
    <AnimatePresence>
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
        {/* Backdrop */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          onClick={handleClose}
          className="absolute inset-0 bg-black/50 backdrop-blur-sm"
        />

        {/* Modal */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95, y: 20 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.95, y: 20 }}
          className="relative bg-white rounded-2xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto"
        >
          {/* Header */}
          <div className="flex items-center justify-between p-6 border-b border-slate-200">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
                <RefreshCw className="h-5 w-5 text-blue-600" />
              </div>
              <h2 className="text-xl font-bold text-slate-900">Reschedule Booking</h2>
            </div>
            <button
              onClick={handleClose}
              className="p-2 hover:bg-slate-100 rounded-lg transition-colors duration-200"
            >
              <X className="h-5 w-5 text-slate-500" />
            </button>
          </div>

          {/* Content */}
          <div className="p-6 space-y-6">
            {/* Current Booking Info */}
            {booking && (
              <div className="p-4 bg-slate-50 rounded-xl">
                <p className="text-sm text-slate-600 mb-2">Current Booking</p>
                <p className="font-semibold text-slate-900">
                  {booking.items?.[0]?.rate_card?.subcategory?.name || booking.items?.[0]?.service_name || 'Service'}
                </p>
                <p className="text-sm text-slate-600">
                  {booking.preferred_date} at {booking.preferred_time}
                </p>
              </div>
            )}

            {/* Date Picker */}
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">
                Select New Date *
              </label>
              <DatePicker
                selected={newDate}
                onChange={setNewDate}
                minDate={addDays(new Date(), 1)}
                dateFormat="MMMM d, yyyy"
                className="w-full px-4 py-3 border border-slate-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200"
                placeholderText="Choose a new date"
              />
            </div>

            {/* Time Slots */}
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">
                Select New Time Slot *
              </label>
              <div className="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-5 gap-2">
                {timeSlots.map((time) => (
                  <motion.button
                    key={time}
                    type="button"
                    onClick={() => setNewTime(time)}
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    className={`px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${
                      newTime === time
                        ? 'bg-gradient-to-r from-primary-500 to-secondary-500 text-white shadow-[0_4px_12px_rgba(108,99,255,0.3)]'
                        : 'bg-white border border-slate-300 text-slate-700 hover:border-primary-300 hover:bg-primary-50'
                    }`}
                  >
                    {formatTimeSlot(time)}
                  </motion.button>
                ))}
              </div>
            </div>

            {/* Reason (Optional) */}
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">
                Reason for Rescheduling (Optional)
              </label>
              <textarea
                value={reason}
                onChange={(e) => setReason(e.target.value)}
                placeholder="Enter reason for rescheduling..."
                rows={3}
                maxLength={200}
                className="w-full px-4 py-3 border border-slate-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent resize-none transition-all duration-200"
              />
              <p className="text-xs text-slate-500 mt-1">
                {reason.length}/200 characters
              </p>
            </div>

            {/* New Schedule Summary */}
            {newDate && newTime && (
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className="p-4 bg-blue-50 border border-blue-200 rounded-xl"
              >
                <p className="text-sm text-blue-900">
                  <span className="font-semibold">New Schedule:</span>{' '}
                  {format(newDate, 'MMMM d, yyyy')} at {formatTimeSlot(newTime)}
                </p>
              </motion.div>
            )}
          </div>

          {/* Footer */}
          <div className="flex items-center gap-3 p-6 border-t border-slate-200">
            <button
              onClick={handleClose}
              disabled={loading}
              className="flex-1 px-4 py-3 bg-white border-2 border-slate-300 text-slate-700 font-semibold rounded-xl hover:bg-slate-50 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200"
            >
              Cancel
            </button>
            <button
              onClick={handleConfirm}
              disabled={loading || !newDate || !newTime}
              className="flex-1 px-4 py-3 bg-gradient-to-r from-blue-500 to-blue-600 text-white font-semibold rounded-xl hover:shadow-[0_4px_12px_rgba(59,130,246,0.3)] disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200"
            >
              {loading ? 'Rescheduling...' : 'Confirm Reschedule'}
            </button>
          </div>
        </motion.div>
      </div>
    </AnimatePresence>
  );
};

export default RescheduleModal;

