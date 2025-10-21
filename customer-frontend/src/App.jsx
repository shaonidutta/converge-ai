import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import LandingPage from "./pages/LandingPage";
import LoginPage from "./pages/LoginPage";
import SignupPage from "./pages/SignupPage";
import Home from "./pages/Home";
import ServiceDetailPage from "./pages/ServiceDetailPage";
import RateCardsPage from "./pages/RateCardsPage";
import CartPage from "./pages/CartPage";
import CheckoutPage from "./pages/CheckoutPage";
import BookingsPage from "./pages/BookingsPage";
import BookingDetailPage from "./pages/BookingDetailPage";
import ProfilePage from "./pages/ProfilePage";
import SettingsPage from "./pages/SettingsPage";
import MyReviewsPage from "./pages/MyReviewsPage";
import LisaChatBubble from "./components/chat/LisaChatBubble";
import LisaChatWindow from "./components/chat/LisaChatWindow";

/**
 * Main App Component
 * Handles routing for the customer frontend application
 */
function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/signup" element={<SignupPage />} />
        <Route path="/home" element={<Home />} />
        <Route path="/services/:categoryId" element={<ServiceDetailPage />} />
        <Route path="/services/:categoryId/:subcategoryId" element={<RateCardsPage />} />
        <Route path="/cart" element={<CartPage />} />
        <Route path="/checkout" element={<CheckoutPage />} />
        <Route path="/bookings" element={<BookingsPage />} />
        <Route path="/bookings/:id" element={<BookingDetailPage />} />
        <Route path="/profile" element={<ProfilePage />} />
        <Route path="/settings" element={<SettingsPage />} />
        <Route path="/reviews" element={<MyReviewsPage />} />
      </Routes>

      {/* Global Chat Components */}
      <LisaChatBubble />
      <LisaChatWindow />
    </Router>
  );
}

export default App;
