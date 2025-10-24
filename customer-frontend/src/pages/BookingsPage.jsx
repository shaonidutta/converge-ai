/**
 * BookingsPage Component
 * Displays list of user's bookings with filters
 */

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Calendar, Search } from 'lucide-react';
import { useBookings, useBookingActions } from '../hooks/useBookings';
import Navbar from '../components/common/Navbar';
import Footer from '../components/common/Footer';
import BookingCard from '../components/bookings/BookingCard';
import BookingFilters from '../components/bookings/BookingFilters';
import { CardSkeleton } from '../components/common/LoadingSkeleton';
import CancelBookingModal from '../components/bookings/CancelBookingModal';
import RescheduleModal from '../components/bookings/RescheduleModal';

const BookingsPage = () => {
  const [activeFilter, setActiveFilter] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedBooking, setSelectedBooking] = useState(null);
  const [showCancelModal, setShowCancelModal] = useState(false);
  const [showRescheduleModal, setShowRescheduleModal] = useState(false);

  // Fetch bookings with filter
  const filterParams = activeFilter === 'all' ? {} : { status: activeFilter };
  const { bookings, loading, error, refetch } = useBookings(filterParams);
  const { cancelBooking, rescheduleBooking, loading: actionLoading } = useBookingActions();

  // Filter bookings by search query
  const filteredBookings = bookings.filter((booking) => {
    if (!searchQuery) return true;
    const query = searchQuery.toLowerCase();
    return (
      booking.rate_card?.subcategory?.name?.toLowerCase().includes(query) ||
      booking.rate_card?.subcategory?.category?.name?.toLowerCase().includes(query) ||
      booking.address?.city?.toLowerCase().includes(query)
    );
  });

  const handleCancelClick = (booking) => {
    setSelectedBooking(booking);
    setShowCancelModal(true);
  };

  const handleRescheduleClick = (booking) => {
    setSelectedBooking(booking);
    setShowRescheduleModal(true);
  };

  const handleCancelConfirm = async (reason) => {
    try {
      await cancelBooking(selectedBooking.id, reason);
      setShowCancelModal(false);
      setSelectedBooking(null);
      refetch();
    } catch (error) {
      console.error('Cancel failed:', error);
    }
  };

  const handleRescheduleConfirm = async (rescheduleData) => {
    try {
      await rescheduleBooking(selectedBooking.id, rescheduleData);
      setShowRescheduleModal(false);
      setSelectedBooking(null);
      refetch();
    } catch (error) {
      console.error('Reschedule failed:', error);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col">
      <Navbar />

      <main className="flex-1 pt-20 pb-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          {/* Header */}
          <div className="mb-8">
            <div className="flex items-center gap-3 mb-2">
              <Calendar className="h-8 w-8 text-primary-500" />
              <h1 className="text-3xl font-bold text-slate-900">My Bookings</h1>
            </div>
            <p className="text-slate-600">
              View and manage all your service bookings
            </p>
          </div>

          {/* Search Bar */}
          <div className="mb-6">
            <div className="relative max-w-md">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-slate-400" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search bookings..."
                className="w-full pl-10 pr-4 py-3 border border-slate-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200"
              />
            </div>
          </div>

          {/* Filters */}
          <div className="mb-8">
            <BookingFilters
              activeFilter={activeFilter}
              onFilterChange={setActiveFilter}
            />
          </div>

          {/* Bookings List */}
          {loading ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {[1, 2, 3, 4, 5, 6].map((i) => (
                <CardSkeleton key={i} className="h-64" />
              ))}
            </div>
          ) : error ? (
            <div className="p-8 bg-red-50 border border-red-200 rounded-xl text-red-700 text-center">
              <p className="font-medium mb-2">Failed to load bookings</p>
              <p className="text-sm">{error}</p>
              <button
                onClick={refetch}
                className="mt-4 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors duration-200"
              >
                Try Again
              </button>
            </div>
          ) : filteredBookings.length === 0 ? (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="flex flex-col items-center justify-center py-16 px-4"
            >
              <div className="w-32 h-32 bg-gradient-to-br from-primary-100 to-secondary-100 rounded-full flex items-center justify-center mb-6">
                <Calendar className="h-16 w-16 text-primary-500" />
              </div>
              <h2 className="text-2xl font-bold text-slate-900 mb-2">
                {searchQuery ? 'No bookings found' : 'No bookings yet'}
              </h2>
              <p className="text-slate-600 text-center mb-8 max-w-md">
                {searchQuery
                  ? 'Try adjusting your search or filters'
                  : 'Start booking services to see them here'}
              </p>
              {!searchQuery && (
                <motion.button
                  onClick={() => window.location.href = '/home'}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  className="px-6 py-3 bg-gradient-to-r from-primary-500 to-secondary-500 text-white font-semibold rounded-xl hover:shadow-[0_4px_12px_rgba(108,99,255,0.3)] transition-all duration-200"
                >
                  Browse Services
                </motion.button>
              )}
            </motion.div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              <AnimatePresence mode="popLayout">
                {filteredBookings.map((booking) => (
                  <BookingCard
                    key={booking.id}
                    booking={booking}
                    onCancel={handleCancelClick}
                    onReschedule={handleRescheduleClick}
                  />
                ))}
              </AnimatePresence>
            </div>
          )}
        </div>
      </main>

      <Footer />

      {/* Modals */}
      <CancelBookingModal
        isOpen={showCancelModal}
        onClose={() => {
          setShowCancelModal(false);
          setSelectedBooking(null);
        }}
        onConfirm={handleCancelConfirm}
        booking={selectedBooking}
        loading={actionLoading}
      />

      <RescheduleModal
        isOpen={showRescheduleModal}
        onClose={() => {
          setShowRescheduleModal(false);
          setSelectedBooking(null);
        }}
        onConfirm={handleRescheduleConfirm}
        booking={selectedBooking}
        loading={actionLoading}
      />
    </div>
  );
};

export default BookingsPage;

