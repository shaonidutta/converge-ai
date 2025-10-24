/**
 * OrderSummary Component
 * Final order review before booking
 */

import React from 'react';
import { motion } from 'framer-motion';
import { Calendar, Clock, MapPin, ShoppingBag, IndianRupee, AlertCircle } from 'lucide-react';
import { format } from 'date-fns';

const OrderSummary = ({ 
  items, 
  selectedDate, 
  selectedTime, 
  selectedAddress, 
  specialInstructions,
  onInstructionsChange,
  error 
}) => {
  // Calculate totals
  const subtotal = items.reduce((sum, item) => sum + (item.price * item.quantity), 0);
  const tax = subtotal * 0.18;
  const total = subtotal + tax;

  const formatTimeSlot = (time) => {
    const [hours] = time.split(':');
    const hour = parseInt(hours);
    const period = hour >= 12 ? 'PM' : 'AM';
    const displayHour = hour > 12 ? hour - 12 : hour === 0 ? 12 : hour;
    return `${displayHour}:00 ${period}`;
  };

  return (
    <div className="space-y-6">
      {/* Service Details */}
      <div className="bg-white rounded-xl border border-slate-200 p-6">
        <div className="flex items-center gap-2 mb-4">
          <ShoppingBag className="h-5 w-5 text-primary-500" />
          <h3 className="font-semibold text-slate-900">Service Details</h3>
        </div>
        <div className="space-y-3">
          {items.map((item, index) => (
            <div key={index} className="flex items-center justify-between py-2 border-b border-slate-100 last:border-0">
              <div className="flex-1">
                <p className="font-medium text-slate-900">{item.subcategoryName}</p>
                <p className="text-sm text-slate-600">Qty: {item.quantity}</p>
              </div>
              <p className="font-semibold text-slate-900 flex items-center">
                <IndianRupee className="h-4 w-4" />
                {(parseFloat(item.price) * item.quantity).toFixed(2)}
              </p>
            </div>
          ))}
        </div>
      </div>

      {/* Schedule Details */}
      <div className="bg-white rounded-xl border border-slate-200 p-6">
        <div className="flex items-center gap-2 mb-4">
          <Calendar className="h-5 w-5 text-primary-500" />
          <h3 className="font-semibold text-slate-900">Schedule</h3>
        </div>
        <div className="space-y-2">
          <div className="flex items-center gap-2 text-slate-700">
            <Calendar className="h-4 w-4 text-slate-500" />
            <span>{selectedDate ? format(selectedDate, 'MMMM d, yyyy') : 'Not selected'}</span>
          </div>
          <div className="flex items-center gap-2 text-slate-700">
            <Clock className="h-4 w-4 text-slate-500" />
            <span>{selectedTime ? formatTimeSlot(selectedTime) : 'Not selected'}</span>
          </div>
        </div>
      </div>

      {/* Address Details */}
      <div className="bg-white rounded-xl border border-slate-200 p-6">
        <div className="flex items-center gap-2 mb-4">
          <MapPin className="h-5 w-5 text-primary-500" />
          <h3 className="font-semibold text-slate-900">Service Address</h3>
        </div>
        {selectedAddress ? (
          <div className="text-slate-700">
            <p className="font-medium capitalize">{selectedAddress.address_type || 'Address'}</p>
            <p className="text-sm mt-1">{selectedAddress.street_address}</p>
            <p className="text-sm">{selectedAddress.city}, {selectedAddress.state} {selectedAddress.pincode}</p>
            {selectedAddress.landmark && (
              <p className="text-xs text-slate-500 mt-1">Landmark: {selectedAddress.landmark}</p>
            )}
          </div>
        ) : (
          <p className="text-slate-500">No address selected</p>
        )}
      </div>

      {/* Special Instructions */}
      <div className="bg-white rounded-xl border border-slate-200 p-6">
        <label className="block text-sm font-medium text-slate-700 mb-2">
          Special Instructions (Optional)
        </label>
        <textarea
          value={specialInstructions}
          onChange={(e) => onInstructionsChange(e.target.value)}
          placeholder="Any specific requirements or instructions for the service provider..."
          rows={3}
          maxLength={500}
          className="w-full px-4 py-3 border border-slate-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent resize-none transition-all duration-200"
        />
        <p className="text-xs text-slate-500 mt-1">
          {specialInstructions.length}/500 characters
        </p>
      </div>

      {/* Price Summary */}
      <div className="bg-gradient-to-br from-primary-50 to-secondary-50 rounded-xl border border-primary-200 p-6">
        <h3 className="font-semibold text-slate-900 mb-4">Payment Summary</h3>
        <div className="space-y-2">
          <div className="flex items-center justify-between text-slate-700">
            <span>Subtotal</span>
            <span className="flex items-center font-medium">
              <IndianRupee className="h-4 w-4" />
              {subtotal.toFixed(2)}
            </span>
          </div>
          <div className="flex items-center justify-between text-slate-700">
            <span>Tax (GST 18%)</span>
            <span className="flex items-center font-medium">
              <IndianRupee className="h-4 w-4" />
              {tax.toFixed(2)}
            </span>
          </div>
          <div className="border-t border-primary-200 pt-2 mt-2">
            <div className="flex items-center justify-between text-slate-900">
              <span className="text-lg font-bold">Total Amount</span>
              <span className="text-xl font-bold flex items-center">
                <IndianRupee className="h-5 w-5" />
                {total.toFixed(2)}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Important Note */}
      <div className="flex items-start gap-3 p-4 bg-amber-50 border border-amber-200 rounded-xl">
        <AlertCircle className="h-5 w-5 text-amber-600 flex-shrink-0 mt-0.5" />
        <div className="text-sm text-amber-900">
          <p className="font-medium mb-1">Important:</p>
          <ul className="list-disc list-inside space-y-1 text-amber-800">
            <li>Payment will be collected after service completion</li>
            <li>You can cancel or reschedule up to 2 hours before the scheduled time</li>
            <li>Service provider will contact you 30 minutes before arrival</li>
          </ul>
        </div>
      </div>

      {error && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-xl text-red-700">
          {error}
        </div>
      )}
    </div>
  );
};

export default OrderSummary;

