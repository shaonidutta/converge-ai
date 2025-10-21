/**
 * RecentBookingsSection Component
 * Display recent bookings with quick actions
 */

import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { ArrowRight, Calendar } from 'lucide-react';
import BookingCard from '../booking/BookingCard';
import { BookingListSkeleton } from '../common/LoadingSkeleton';
import { Button } from '../ui/button';

/**
 * RecentBookingsSection Component
 * @param {Object} props
 * @param {Array} props.bookings - List of recent bookings
 * @param {boolean} props.loading - Loading state
 * @param {string} props.error - Error message
 * @param {Function} props.onReschedule - Callback for reschedule action
 * @param {Function} props.onCancel - Callback for cancel action
 */
const RecentBookingsSection = ({
  bookings = [],
  loading = false,
  error = null,
  onReschedule,
  onCancel,
}) => {
  const navigate = useNavigate();

  // Don't show section if no bookings and not loading
  if (!loading && (!bookings || bookings.length === 0)) {
    return null;
  }

  // Show loading skeleton
  if (loading) {
    return (
      <section className="py-12 bg-gradient-to-br from-slate-50 to-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="mb-8">
            <div className="h-8 w-48 bg-slate-200 rounded animate-pulse mb-2" />
            <div className="h-4 w-64 bg-slate-200 rounded animate-pulse" />
          </div>
          <BookingListSkeleton count={3} />
        </div>
      </section>
    );
  }

  // Show error state
  if (error) {
    return (
      <section className="py-12 bg-gradient-to-br from-slate-50 to-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center py-8">
            <p className="text-sm text-red-600">{error}</p>
          </div>
        </div>
      </section>
    );
  }

  return (
    <section className="py-12 bg-gradient-to-br from-slate-50 to-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
          className="flex items-center justify-between mb-8"
        >
          <div>
            <h2 className="text-3xl font-black text-slate-900 mb-2">
              Recent Bookings
            </h2>
            <p className="text-slate-600">
              Track and manage your recent service bookings
            </p>
          </div>

          <Button
            onClick={() => navigate('/bookings')}
            variant="outline"
            className="hidden md:flex items-center gap-2 hover:bg-primary-50 hover:border-primary-300 hover:text-primary-700 transition-all duration-300"
          >
            View All
            <ArrowRight className="h-4 w-4" />
          </Button>
        </motion.div>

        {/* Bookings Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {bookings.map((booking, index) => (
            <BookingCard
              key={booking.id}
              booking={booking}
              index={index}
              onReschedule={onReschedule}
              onCancel={onCancel}
            />
          ))}
        </div>

        {/* View All Button - Mobile */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
          className="mt-8 text-center md:hidden"
        >
          <Button
            onClick={() => navigate('/bookings')}
            className="w-full bg-gradient-to-r from-primary-500 to-secondary-500 hover:from-primary-600 hover:to-secondary-600 text-white"
          >
            View All Bookings
            <ArrowRight className="h-4 w-4 ml-2" />
          </Button>
        </motion.div>

        {/* Empty State for No Bookings */}
        {bookings.length === 0 && !loading && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="text-center py-12 bg-white rounded-xl shadow-[0_4px_20px_rgba(0,0,0,0.05)]"
          >
            <div className="w-16 h-16 rounded-full bg-gradient-to-br from-primary-100 to-secondary-100 flex items-center justify-center mx-auto mb-4">
              <Calendar className="h-8 w-8 text-primary-600" />
            </div>
            <h3 className="text-lg font-semibold text-slate-900 mb-2">
              No Bookings Yet
            </h3>
            <p className="text-sm text-slate-600 mb-6">
              Start booking services to see them here
            </p>
            <Button
              onClick={() => navigate('/services')}
              className="bg-gradient-to-r from-primary-500 to-secondary-500 hover:from-primary-600 hover:to-secondary-600 text-white"
            >
              Browse Services
            </Button>
          </motion.div>
        )}
      </div>
    </section>
  );
};

export default RecentBookingsSection;

