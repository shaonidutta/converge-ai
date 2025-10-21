/**
 * ServiceScheduler Component
 * Date and time selection for service booking
 */

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import DatePicker from 'react-datepicker';
import 'react-datepicker/dist/react-datepicker.css';
import { Calendar, Clock } from 'lucide-react';
import { addDays, format } from 'date-fns';

const ServiceScheduler = ({ selectedDate, selectedTime, onDateChange, onTimeChange, error }) => {
  // Time slots from 8 AM to 8 PM
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

  return (
    <div className="space-y-6">
      {/* Date Picker */}
      <div>
        <label className="flex items-center gap-2 text-sm font-medium text-slate-700 mb-2">
          <Calendar className="h-4 w-4" />
          Select Date
        </label>
        <div className="relative">
          <DatePicker
            selected={selectedDate}
            onChange={onDateChange}
            minDate={addDays(new Date(), 1)}
            dateFormat="MMMM d, yyyy"
            className="w-full px-4 py-3 border border-slate-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200"
            placeholderText="Choose a date"
            calendarClassName="custom-calendar"
          />
        </div>
        {error?.date && (
          <p className="text-sm text-red-500 mt-1">{error.date}</p>
        )}
      </div>

      {/* Time Slots */}
      <div>
        <label className="flex items-center gap-2 text-sm font-medium text-slate-700 mb-2">
          <Clock className="h-4 w-4" />
          Select Time Slot
        </label>
        <div className="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-5 gap-2">
          {timeSlots.map((time) => (
            <motion.button
              key={time}
              type="button"
              onClick={() => onTimeChange(time)}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${
                selectedTime === time
                  ? 'bg-gradient-to-r from-primary-500 to-secondary-500 text-white shadow-[0_4px_12px_rgba(108,99,255,0.3)]'
                  : 'bg-white border border-slate-300 text-slate-700 hover:border-primary-300 hover:bg-primary-50'
              }`}
            >
              {formatTimeSlot(time)}
            </motion.button>
          ))}
        </div>
        {error?.time && (
          <p className="text-sm text-red-500 mt-2">{error.time}</p>
        )}
      </div>

      {/* Selected Summary */}
      {selectedDate && selectedTime && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="p-4 bg-primary-50 border border-primary-200 rounded-xl"
        >
          <p className="text-sm text-primary-900">
            <span className="font-semibold">Scheduled for:</span>{' '}
            {format(selectedDate, 'MMMM d, yyyy')} at {formatTimeSlot(selectedTime)}
          </p>
        </motion.div>
      )}
    </div>
  );
};

export default ServiceScheduler;

