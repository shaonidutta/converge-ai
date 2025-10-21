import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import LandingPage from "./pages/LandingPage";
import LoginPage from "./pages/LoginPage";
import SignupPage from "./pages/SignupPage";
import Home from "./pages/Home";
import ServiceDetailPage from "./pages/ServiceDetailPage";
import RateCardsPage from "./pages/RateCardsPage";
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
      </Routes>

      {/* Global Chat Components */}
      <LisaChatBubble />
      <LisaChatWindow />
    </Router>
  );
}

export default App;
