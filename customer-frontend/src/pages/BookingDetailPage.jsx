/**
 * BookingDetailPage Component
 * Displays detailed information about a single booking
 */

import React, { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import {
  ArrowLeft,
  Calendar,
  Clock,
  MapPin,
  IndianRupee,
  User,
  Phone,
  Mail,
  FileText,
  XCircle,
  RefreshCw,
  CheckCircle,
  Star,
} from "lucide-react";
import { format } from "date-fns";
import { useBooking, useBookingActions } from "../hooks/useBookings";
import { useCanReview, useReviewActions } from "../hooks/useReviews";
import { fetchReviewByBooking } from "../services/reviewService";
import Navbar from "../components/common/Navbar";
import Footer from "../components/common/Footer";
import BookingStatusBadge from "../components/bookings/BookingStatusBadge";
import { CardSkeleton } from "../components/common/LoadingSkeleton";
import CancelBookingModal from "../components/bookings/CancelBookingModal";
import RescheduleModal from "../components/bookings/RescheduleModal";
import ReviewForm from "../components/reviews/ReviewForm";
import ReviewCard from "../components/reviews/ReviewCard";
import {
  validateBookingCancellation,
  validateBookingReschedule,
} from "../utils/bookingValidation";

const BookingDetailPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { booking, loading, error, refetch } = useBooking(id);
  const {
    cancelBooking,
    rescheduleBooking,
    loading: actionLoading,
  } = useBookingActions();
  const { canReview, reason: reviewReason } = useCanReview(id, booking?.status);
  const {
    submit: submitReview,
    update: updateReview,
    remove: deleteReview,
    loading: reviewLoading,
  } = useReviewActions();

  const [showCancelModal, setShowCancelModal] = useState(false);
  const [showRescheduleModal, setShowRescheduleModal] = useState(false);
  const [showReviewForm, setShowReviewForm] = useState(false);
  const [existingReview, setExistingReview] = useState(null);
  const [editingReview, setEditingReview] = useState(null);

  // Fetch existing review for this booking
  useEffect(() => {
    const loadReview = async () => {
      if (id) {
        const review = await fetchReviewByBooking(parseInt(id));
        setExistingReview(review);
      }
    };
    loadReview();
  }, [id]);

  const formatDate = (dateString) => {
    try {
      return format(new Date(dateString), "MMMM d, yyyy");
    } catch {
      return dateString;
    }
  };

  const formatTime = (timeString) => {
    try {
      const [hours] = timeString.split(":");
      const hour = parseInt(hours);
      const period = hour >= 12 ? "PM" : "AM";
      const displayHour = hour > 12 ? hour - 12 : hour === 0 ? 12 : hour;
      return `${displayHour}:00 ${period}`;
    } catch {
      return timeString;
    }
  };

  const handleCancelConfirm = async (reason) => {
    try {
      await cancelBooking(id, reason);
      setShowCancelModal(false);
      refetch();
    } catch (error) {
      console.error("Cancel failed:", error);
    }
  };

  const handleRescheduleConfirm = async (rescheduleData) => {
    try {
      await rescheduleBooking(id, rescheduleData);
      setShowRescheduleModal(false);
      refetch();
    } catch (error) {
      console.error("Reschedule failed:", error);
    }
  };

  const handleReviewSubmit = async (reviewData) => {
    try {
      if (editingReview) {
        await updateReview(editingReview.id, reviewData);
        alert("Review updated successfully!");
      } else {
        await submitReview(parseInt(id), reviewData);
        alert("Review submitted successfully!");
      }
      setShowReviewForm(false);
      setEditingReview(null);
      // Reload review
      const review = await fetchReviewByBooking(parseInt(id));
      setExistingReview(review);
    } catch (error) {
      alert(error.message || "Failed to submit review");
    }
  };

  const handleEditReview = (review) => {
    setEditingReview(review);
    setShowReviewForm(true);
  };

  const handleDeleteReview = async (reviewId) => {
    if (
      !confirm(
        "Are you sure you want to delete this review? This action cannot be undone."
      )
    ) {
      return;
    }

    try {
      await deleteReview(reviewId);
      setExistingReview(null);
      alert("Review deleted successfully!");
    } catch (error) {
      alert("Failed to delete review");
    }
  };

  // Validate cancellation and rescheduling with proper date checks
  const { canCancel, reason: cancelReason } =
    validateBookingCancellation(booking);
  const { canReschedule, reason: rescheduleReason } =
    validateBookingReschedule(booking);

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col">
      <Navbar />

      <main className="flex-1 pt-20 pb-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          {/* Back Button */}
          <button
            onClick={() => navigate("/bookings")}
            className="flex items-center gap-2 text-slate-600 hover:text-primary-500 mb-6 transition-colors duration-200"
          >
            <ArrowLeft className="h-5 w-5" />
            <span className="font-medium">Back to Bookings</span>
          </button>

          {loading ? (
            <div className="space-y-6">
              <CardSkeleton className="h-32" />
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <div className="lg:col-span-2 space-y-6">
                  <CardSkeleton className="h-64" />
                  <CardSkeleton className="h-48" />
                </div>
                <CardSkeleton className="h-96" />
              </div>
            </div>
          ) : error ? (
            <div className="p-8 bg-red-50 border border-red-200 rounded-xl text-red-700 text-center">
              <p className="font-medium mb-2">Failed to load booking details</p>
              <p className="text-sm mb-4">{error}</p>
              <button
                onClick={refetch}
                className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors duration-200"
              >
                Try Again
              </button>
            </div>
          ) : !booking ? (
            <div className="p-8 bg-amber-50 border border-amber-200 rounded-xl text-amber-700 text-center">
              <p className="font-medium">Booking not found</p>
            </div>
          ) : (
            <div className="space-y-6">
              {/* Header */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="bg-white rounded-xl border border-slate-200 p-6"
              >
                <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
                  <div className="flex items-center gap-4">
                    <div className="w-16 h-16 bg-gradient-to-br from-primary-100 to-secondary-100 rounded-xl flex items-center justify-center">
                      <span className="text-3xl">
                        {booking.items?.[0]?.rate_card?.subcategory?.image ||
                          "🛠️"}
                      </span>
                    </div>
                    <div>
                      <h1 className="text-2xl font-bold text-slate-900">
                        {booking.items?.[0]?.rate_card?.subcategory?.name ||
                          booking.items?.[0]?.service_name ||
                          "Service"}
                      </h1>
                      <p className="text-slate-600">
                        {booking.items?.[0]?.rate_card?.subcategory?.category
                          ?.name || "Category"}
                      </p>
                    </div>
                  </div>
                  <BookingStatusBadge status={booking.status} size="lg" />
                </div>
              </motion.div>

              {/* Main Content */}
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Left Column - Details */}
                <div className="lg:col-span-2 space-y-6">
                  {/* Schedule Details */}
                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.1 }}
                    className="bg-white rounded-xl border border-slate-200 p-6"
                  >
                    <h2 className="text-lg font-bold text-slate-900 mb-4">
                      Schedule Details
                    </h2>
                    <div className="space-y-3">
                      <div className="flex items-center gap-3">
                        <div className="w-10 h-10 bg-primary-100 rounded-lg flex items-center justify-center">
                          <Calendar className="h-5 w-5 text-primary-500" />
                        </div>
                        <div>
                          <p className="text-sm text-slate-600">Date</p>
                          <p className="font-semibold text-slate-900">
                            {formatDate(booking.preferred_date)}
                          </p>
                        </div>
                      </div>
                      <div className="flex items-center gap-3">
                        <div className="w-10 h-10 bg-secondary-100 rounded-lg flex items-center justify-center">
                          <Clock className="h-5 w-5 text-secondary-500" />
                        </div>
                        <div>
                          <p className="text-sm text-slate-600">Time</p>
                          <p className="font-semibold text-slate-900">
                            {formatTime(booking.preferred_time)}
                          </p>
                        </div>
                      </div>
                    </div>
                  </motion.div>

                  {/* Address Details */}
                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.2 }}
                    className="bg-white rounded-xl border border-slate-200 p-6"
                  >
                    <h2 className="text-lg font-bold text-slate-900 mb-4">
                      Service Location
                    </h2>
                    {booking.address ? (
                      <div className="flex items-start gap-3">
                        <div className="w-10 h-10 bg-accent-100 rounded-lg flex items-center justify-center flex-shrink-0">
                          <MapPin className="h-5 w-5 text-accent-500" />
                        </div>
                        <div>
                          <p className="font-semibold text-slate-900">
                            {booking.address.address_type}
                          </p>
                          <p className="text-slate-600 mt-1">
                            {booking.address.street_address}
                            {booking.address.apartment_number &&
                              `, ${booking.address.apartment_number}`}
                          </p>
                          <p className="text-slate-600">
                            {booking.address.city}, {booking.address.state}{" "}
                            {booking.address.postal_code}
                          </p>
                        </div>
                      </div>
                    ) : (
                      <p className="text-slate-500">Address not available</p>
                    )}
                  </motion.div>

                  {/* Special Instructions */}
                  {booking.special_instructions && (
                    <motion.div
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: 0.3 }}
                      className="bg-white rounded-xl border border-slate-200 p-6"
                    >
                      <h2 className="text-lg font-bold text-slate-900 mb-4">
                        Special Instructions
                      </h2>
                      <div className="flex items-start gap-3">
                        <FileText className="h-5 w-5 text-slate-400 flex-shrink-0 mt-0.5" />
                        <p className="text-slate-600">
                          {booking.special_instructions}
                        </p>
                      </div>
                    </motion.div>
                  )}
                </div>

                {/* Right Column - Actions & Summary */}
                <div className="space-y-6">
                  {/* Action Buttons */}
                  {(canCancel ||
                    canReschedule ||
                    (canReview && !existingReview)) && (
                    <motion.div
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: 0.1 }}
                      className="bg-white rounded-xl border border-slate-200 p-6 space-y-3"
                    >
                      <h2 className="text-lg font-bold text-slate-900 mb-4">
                        Actions
                      </h2>

                      {/* Review Button */}
                      {canReview && !existingReview && (
                        <motion.button
                          onClick={() => setShowReviewForm(true)}
                          whileHover={{ scale: 1.02 }}
                          whileTap={{ scale: 0.98 }}
                          className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-gradient-to-r from-yellow-500 to-amber-500 text-white font-semibold rounded-xl hover:shadow-[0_4px_12px_rgba(245,158,11,0.3)] transition-all duration-200"
                        >
                          <Star className="h-5 w-5" />
                          Write a Review
                        </motion.button>
                      )}

                      {canReschedule && (
                        <motion.button
                          onClick={() => setShowRescheduleModal(true)}
                          whileHover={{ scale: 1.02 }}
                          whileTap={{ scale: 0.98 }}
                          className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-gradient-to-r from-blue-500 to-blue-600 text-white font-semibold rounded-xl hover:shadow-[0_4px_12px_rgba(59,130,246,0.3)] transition-all duration-200"
                        >
                          <RefreshCw className="h-5 w-5" />
                          Reschedule
                        </motion.button>
                      )}
                      {canCancel && (
                        <motion.button
                          onClick={() => setShowCancelModal(true)}
                          whileHover={{ scale: 1.02 }}
                          whileTap={{ scale: 0.98 }}
                          className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-white border-2 border-red-500 text-red-500 font-semibold rounded-xl hover:bg-red-50 transition-all duration-200"
                        >
                          <XCircle className="h-5 w-5" />
                          Cancel Booking
                        </motion.button>
                      )}
                    </motion.div>
                  )}

                  {/* Restriction Messages */}
                  {(!canCancel || !canReschedule) &&
                    (cancelReason || rescheduleReason) && (
                      <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.2 }}
                        className="bg-amber-50 border border-amber-200 rounded-xl p-4"
                      >
                        <h3 className="text-sm font-semibold text-amber-900 mb-2">
                          Booking Restrictions
                        </h3>
                        {!canCancel && cancelReason && (
                          <p className="text-sm text-amber-800 mb-1">
                            • {cancelReason}
                          </p>
                        )}
                        {!canReschedule &&
                          rescheduleReason &&
                          rescheduleReason !== cancelReason && (
                            <p className="text-sm text-amber-800">
                              • {rescheduleReason}
                            </p>
                          )}
                      </motion.div>
                    )}

                  {/* Review Display */}
                  {existingReview && (
                    <motion.div
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: 0.15 }}
                      className="bg-white rounded-xl border border-slate-200 p-6"
                    >
                      <h2 className="text-lg font-bold text-slate-900 mb-4">
                        Your Review
                      </h2>
                      <ReviewCard
                        review={existingReview}
                        showActions={true}
                        onEdit={handleEditReview}
                        onDelete={handleDeleteReview}
                      />
                    </motion.div>
                  )}

                  {/* Review Not Available Message */}
                  {!canReview && !existingReview && reviewReason && (
                    <motion.div
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: 0.15 }}
                      className="bg-slate-50 rounded-xl border border-slate-200 p-4"
                    >
                      <p className="text-sm text-slate-600 text-center">
                        {reviewReason}
                      </p>
                    </motion.div>
                  )}

                  {/* Payment Summary */}
                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.2 }}
                    className="bg-white rounded-xl border border-slate-200 p-6"
                  >
                    <h2 className="text-lg font-bold text-slate-900 mb-4">
                      Payment Summary
                    </h2>
                    <div className="space-y-3">
                      <div className="flex justify-between text-slate-600">
                        <span>Subtotal</span>
                        <div className="flex items-center gap-1">
                          <IndianRupee className="h-4 w-4" />
                          <span>
                            {(parseFloat(booking.total_amount) / 1.18).toFixed(
                              2
                            )}
                          </span>
                        </div>
                      </div>
                      <div className="flex justify-between text-slate-600">
                        <span>Tax (18% GST)</span>
                        <div className="flex items-center gap-1">
                          <IndianRupee className="h-4 w-4" />
                          <span>
                            {(
                              parseFloat(booking.total_amount) -
                              parseFloat(booking.total_amount) / 1.18
                            ).toFixed(2)}
                          </span>
                        </div>
                      </div>
                      <div className="pt-3 border-t border-slate-200 flex justify-between items-center">
                        <span className="font-bold text-slate-900">Total</span>
                        <div className="flex items-center gap-1 text-xl font-bold text-slate-900">
                          <IndianRupee className="h-5 w-5" />
                          <span>
                            {booking.total_amount
                              ? parseFloat(booking.total_amount).toFixed(2)
                              : "0.00"}
                          </span>
                        </div>
                      </div>
                    </div>
                  </motion.div>
                </div>
              </div>
            </div>
          )}
        </div>
      </main>

      <Footer />

      {/* Modals */}
      <CancelBookingModal
        isOpen={showCancelModal}
        onClose={() => setShowCancelModal(false)}
        onConfirm={handleCancelConfirm}
        booking={booking}
        loading={actionLoading}
      />

      <RescheduleModal
        isOpen={showRescheduleModal}
        onClose={() => setShowRescheduleModal(false)}
        onConfirm={handleRescheduleConfirm}
        booking={booking}
        loading={actionLoading}
      />

      {/* Review Form Modal */}
      <AnimatePresence>
        {showReviewForm && (
          <ReviewForm
            booking={booking}
            existingReview={editingReview}
            onSubmit={handleReviewSubmit}
            onCancel={() => {
              setShowReviewForm(false);
              setEditingReview(null);
            }}
            loading={reviewLoading}
          />
        )}
      </AnimatePresence>
    </div>
  );
};

export default BookingDetailPage;
