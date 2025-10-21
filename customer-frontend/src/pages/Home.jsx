/**
 * Home Page Component
 * Main home page after successful authentication
 * Displays services catalog, recent bookings, and AI assistant
 */

import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { getStoredUser } from '../api/axiosConfig';
import { useCategories } from '../hooks/useCategories';
import { useRecentBookings } from '../hooks/useBookings';
import { useBookingActions } from '../hooks/useBookings';
import Navbar from '../components/common/Navbar';
import Footer from '../components/common/Footer';
import HeroSection from '../components/home/HeroSection';
import ServicesSection from '../components/home/ServicesSection';
import RecentBookingsSection from '../components/home/RecentBookingsSection';
import LisaChatBubble from '../components/chat/LisaChatBubble';
import LisaChatWindow from '../components/chat/LisaChatWindow';

/**
 * Home Component
 */
const Home = () => {
  const navigate = useNavigate();
  const [user, setUser] = useState(null);
  const [showAddAddressModal, setShowAddAddressModal] = useState(false);

  // Fetch data using custom hooks
  const { categories, loading: categoriesLoading, error: categoriesError } = useCategories();
  const { bookings, loading: bookingsLoading, error: bookingsError, refetch: refetchBookings } = useRecentBookings();
  const { cancelBooking, rescheduleBooking } = useBookingActions();

  // Get user data on mount
  useEffect(() => {
    const storedUser = getStoredUser();

    if (!storedUser) {
      // No user data, redirect to login
      navigate('/login');
      return;
    }

    setUser(storedUser);
  }, [navigate]);

  // Handle reschedule booking
  const handleReschedule = async (booking) => {
    // TODO: Open reschedule modal
    console.log('Reschedule booking:', booking);
    // For now, just show alert
    alert('Reschedule functionality will be available in Phase 6');
  };

  // Handle cancel booking
  const handleCancel = async (booking) => {
    // Confirm cancellation
    const confirmed = window.confirm(
      `Are you sure you want to cancel booking #${booking.id}?`
    );

    if (!confirmed) return;

    try {
      await cancelBooking(booking.id, 'User requested cancellation');
      // Refetch bookings to update UI
      refetchBookings();
      alert('Booking cancelled successfully');
    } catch (error) {
      alert(`Failed to cancel booking: ${error.message}`);
    }
  };

  // Handle add address
  const handleAddAddress = () => {
    // TODO: Open add address modal
    console.log('Add address clicked');
    setShowAddAddressModal(true);
    // For now, just show alert
    alert('Add address functionality will be available in Phase 7');
  };



  // Show loading state
  if (!user) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-50 via-white to-primary-50/20">
        <div className="text-center">
          <div className="w-16 h-16 rounded-full border-4 border-primary-200 border-t-primary-600 animate-spin mx-auto mb-4"></div>
          <p className="text-slate-600 font-medium">Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-primary-50/20">
      {/* Navbar */}
      <Navbar
        cartItemCount={0} // TODO: Get from cart context/state
        onAddAddress={handleAddAddress}
      />

      {/* Main Content */}
      <main className="pt-16">
        {/* Hero Section */}
        <HeroSection user={user} />

        {/* Services Section */}
        <ServicesSection
          categories={categories}
          loading={categoriesLoading}
          error={categoriesError}
        />

        {/* Recent Bookings Section */}
        <RecentBookingsSection
          bookings={bookings}
          loading={bookingsLoading}
          error={bookingsError}
          onReschedule={handleReschedule}
          onCancel={handleCancel}
        />
      </main>

      {/* Footer */}
      <Footer />

      {/* Lisa AI Chat Bubble */}
      <LisaChatBubble />

      {/* Lisa Chat Window */}
      <LisaChatWindow />
    </div>
  );
};

export default Home;

