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
import SearchResultsPage from "./pages/SearchResultsPage";
import ProtectedRoute from "./components/ProtectedRoute";
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
        <Route
          path="/home"
          element={
            <ProtectedRoute>
              <Home />
            </ProtectedRoute>
          }
        />
        <Route path="/search" element={<SearchResultsPage />} />
        <Route path="/services/:categoryId" element={<ServiceDetailPage />} />
        <Route
          path="/services/:categoryId/:subcategoryId"
          element={<RateCardsPage />}
        />
        <Route
          path="/cart"
          element={
            <ProtectedRoute>
              <CartPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/checkout"
          element={
            <ProtectedRoute>
              <CheckoutPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/bookings"
          element={
            <ProtectedRoute>
              <BookingsPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/bookings/:id"
          element={
            <ProtectedRoute>
              <BookingDetailPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/profile"
          element={
            <ProtectedRoute>
              <ProfilePage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/settings"
          element={
            <ProtectedRoute>
              <SettingsPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/reviews"
          element={
            <ProtectedRoute>
              <MyReviewsPage />
            </ProtectedRoute>
          }
        />
      </Routes>

      {/* Global Chat Components */}
      <LisaChatBubble />
      <LisaChatWindow />
    </Router>
  );
}

export default App;
