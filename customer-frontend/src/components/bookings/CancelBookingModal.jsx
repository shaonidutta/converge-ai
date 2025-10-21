/**
 * CancelBookingModal Component
 * Modal for cancelling a booking with reason selection
 */

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, AlertTriangle } from 'lucide-react';

const CancelBookingModal = ({ isOpen, onClose, onConfirm, booking, loading }) => {
  const [reason, setReason] = useState('');
  const [customReason, setCustomReason] = useState('');

  const predefinedReasons = [
    'Change of plans',
    'Found alternative service',
    'Incorrect booking details',
    'Service no longer needed',
    'Other',
  ];

  const handleConfirm = () => {
    const finalReason = reason === 'Other' ? customReason : reason;
    if (finalReason.trim()) {
      onConfirm(finalReason);
    }
  };

  const handleClose = () => {
    setReason('');
    setCustomReason('');
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
          className="relative bg-white rounded-2xl shadow-2xl max-w-md w-full max-h-[90vh] overflow-y-auto"
        >
          {/* Header */}
          <div className="flex items-center justify-between p-6 border-b border-slate-200">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-red-100 rounded-full flex items-center justify-center">
                <AlertTriangle className="h-5 w-5 text-red-600" />
              </div>
              <h2 className="text-xl font-bold text-slate-900">Cancel Booking</h2>
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
            {/* Warning */}
            <div className="p-4 bg-amber-50 border border-amber-200 rounded-xl">
              <p className="text-sm text-amber-900">
                <span className="font-semibold">Important:</span> Cancelling this booking cannot be undone. 
                Please select a reason for cancellation.
              </p>
            </div>

            {/* Booking Info */}
            {booking && (
              <div className="p-4 bg-slate-50 rounded-xl">
                <p className="text-sm text-slate-600 mb-1">Booking Details</p>
                <p className="font-semibold text-slate-900">
                  {booking.rate_card?.subcategory?.name || 'Service'}
                </p>
                <p className="text-sm text-slate-600">
                  {booking.scheduled_date} at {booking.scheduled_time}
                </p>
              </div>
            )}

            {/* Reason Selection */}
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-3">
                Reason for cancellation *
              </label>
              <div className="space-y-2">
                {predefinedReasons.map((r) => (
                  <label
                    key={r}
                    className={`flex items-center gap-3 p-3 border-2 rounded-lg cursor-pointer transition-all duration-200 ${
                      reason === r
                        ? 'border-primary-500 bg-primary-50'
                        : 'border-slate-200 hover:border-primary-300'
                    }`}
                  >
                    <input
                      type="radio"
                      name="reason"
                      value={r}
                      checked={reason === r}
                      onChange={(e) => setReason(e.target.value)}
                      className="w-4 h-4 text-primary-500 focus:ring-primary-500"
                    />
                    <span className="text-sm text-slate-700">{r}</span>
                  </label>
                ))}
              </div>
            </div>

            {/* Custom Reason */}
            {reason === 'Other' && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
              >
                <label className="block text-sm font-medium text-slate-700 mb-2">
                  Please specify
                </label>
                <textarea
                  value={customReason}
                  onChange={(e) => setCustomReason(e.target.value)}
                  placeholder="Enter your reason..."
                  rows={3}
                  maxLength={200}
                  className="w-full px-4 py-3 border border-slate-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent resize-none transition-all duration-200"
                />
                <p className="text-xs text-slate-500 mt-1">
                  {customReason.length}/200 characters
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
              Keep Booking
            </button>
            <button
              onClick={handleConfirm}
              disabled={loading || !reason || (reason === 'Other' && !customReason.trim())}
              className="flex-1 px-4 py-3 bg-gradient-to-r from-red-500 to-red-600 text-white font-semibold rounded-xl hover:shadow-[0_4px_12px_rgba(239,68,68,0.3)] disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200"
            >
              {loading ? 'Cancelling...' : 'Cancel Booking'}
            </button>
          </div>
        </motion.div>
      </div>
    </AnimatePresence>
  );
};

export default CancelBookingModal;

