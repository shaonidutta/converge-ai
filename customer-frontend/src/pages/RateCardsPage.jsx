/**
 * Rate Cards Page
 * Displays rate cards for a subcategory with pricing and add to cart
 * Route: /services/:categoryId/:subcategoryId
 * Features:
 * - Breadcrumb navigation
 * - Subcategory header
 * - Rate cards list
 * - Add to cart functionality
 * - Loading and error states
 */

import React, { useEffect, useState } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import { motion } from "framer-motion";
import {
  Home,
  ChevronRight,
  Wrench,
  AlertCircle,
  RefreshCw,
  ShoppingCart,
} from "lucide-react";
import { useRateCards } from "../hooks/useRateCards";
import { useSubcategories } from "../hooks/useSubcategories";
import { useCart } from "../hooks/useCart";
import RateCardItem from "../components/services/RateCardItem";
import Navbar from "../components/common/Navbar";
import Footer from "../components/common/Footer";
import { ServiceGridSkeleton } from "../components/common/LoadingSkeleton";

const RateCardsPage = () => {
  const { categoryId, subcategoryId } = useParams();
  const navigate = useNavigate();
  const { addToCart, totalItems, totalPrice } = useCart();

  // Fetch subcategories to get subcategory details
  const { subcategories } = useSubcategories(parseInt(categoryId));
  const [subcategory, setSubcategory] = useState(null);

  // Fetch rate cards
  const { rateCards, loading, error, refetch } = useRateCards(
    parseInt(subcategoryId)
  );

  // Find subcategory from list
  useEffect(() => {
    if (subcategories && subcategories.length > 0) {
      const found = subcategories.find(
        (sub) => sub.id === parseInt(subcategoryId)
      );
      setSubcategory(found);
    }
  }, [subcategories, subcategoryId]);

  // Scroll to top on mount
  useEffect(() => {
    window.scrollTo(0, 0);
  }, []);

  // Check authentication
  useEffect(() => {
    const user = localStorage.getItem("user");
    if (!user) {
      navigate("/login");
    }
  }, [navigate]);

  const handleAddToCart = async (rateCard, quantity) => {
    // Get category name from subcategory data
    const categoryName = subcategory?.category?.name || "Category";
    const subcategoryName = subcategory?.name || "Service";

    addToCart(rateCard, quantity, {
      categoryName,
      subcategoryName,
    });
  };

  return (
    <div className="min-h-screen bg-slate-50">
      <Navbar />

      {/* Main Content */}
      <main className="pt-20 pb-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          {/* Breadcrumb Navigation */}
          <motion.nav
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="flex items-center gap-2 text-sm text-slate-600 mb-8 flex-wrap"
          >
            <Link
              to="/home"
              className="hover:text-primary-600 transition-colors duration-200"
            >
              <Home className="h-4 w-4" />
            </Link>
            <ChevronRight className="h-4 w-4" />
            <Link
              to="/home"
              className="hover:text-primary-600 transition-colors duration-200"
            >
              Services
            </Link>
            <ChevronRight className="h-4 w-4" />
            <Link
              to={`/services/${categoryId}`}
              className="hover:text-primary-600 transition-colors duration-200"
            >
              {subcategory?.category_name || "Category"}
            </Link>
            <ChevronRight className="h-4 w-4" />
            <span className="text-slate-800 font-medium">
              {subcategory?.name || "Loading..."}
            </span>
          </motion.nav>

          {/* Subcategory Header */}
          {subcategory && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="bg-white rounded-2xl shadow-[0_4px_20px_rgba(0,0,0,0.05)] p-8 mb-8"
            >
              <div className="flex flex-col md:flex-row items-center gap-6">
                {/* Subcategory Icon */}
                <div className="flex-shrink-0">
                  <div className="h-20 w-20 bg-gradient-to-br from-primary-500 to-secondary-500 rounded-2xl flex items-center justify-center">
                    {subcategory.image ? (
                      <img
                        src={subcategory.image}
                        alt={subcategory.name}
                        className="h-12 w-12 object-contain"
                      />
                    ) : (
                      <Wrench className="h-12 w-12 text-white" />
                    )}
                  </div>
                </div>

                {/* Subcategory Info */}
                <div className="flex-1 text-center md:text-left">
                  <h1 className="text-3xl md:text-4xl font-bold text-slate-800 mb-3">
                    {subcategory.name}
                  </h1>
                  <p className="text-lg text-slate-600 mb-4">
                    {subcategory.description}
                  </p>
                  <div className="flex items-center justify-center md:justify-start gap-4">
                    <span className="inline-flex items-center px-4 py-2 rounded-full text-sm font-medium bg-primary-50 text-primary-700">
                      {rateCards.length}{" "}
                      {rateCards.length === 1 ? "Option" : "Options"} Available
                    </span>
                  </div>
                </div>
              </div>
            </motion.div>
          )}

          {/* Section Title */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="mb-6"
          >
            <h2 className="text-2xl font-bold text-slate-800 mb-2">
              Choose Your Package
            </h2>
            <p className="text-slate-600">
              Select the package that best fits your needs
            </p>
          </motion.div>

          {/* Rate Cards List */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
          >
            {loading ? (
              <ServiceGridSkeleton count={3} />
            ) : error ? (
              <div className="flex flex-col items-center justify-center py-16 px-4">
                <div className="bg-red-50 rounded-full p-4 mb-4">
                  <AlertCircle className="h-12 w-12 text-red-500" />
                </div>
                <h3 className="text-xl font-semibold text-slate-800 mb-2">
                  Failed to Load Packages
                </h3>
                <p className="text-slate-600 mb-6 text-center max-w-md">
                  {error}
                </p>
                <button
                  onClick={refetch}
                  className="flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-primary-500 to-secondary-500 text-white rounded-lg font-medium hover:shadow-[0_4px_12px_rgba(108,99,255,0.3)] transition-all duration-300"
                >
                  <RefreshCw className="h-4 w-4" />
                  <span>Try Again</span>
                </button>
              </div>
            ) : rateCards.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-16 px-4">
                <div className="bg-slate-100 rounded-full p-4 mb-4">
                  <AlertCircle className="h-12 w-12 text-slate-400" />
                </div>
                <h3 className="text-xl font-semibold text-slate-800 mb-2">
                  No Packages Available
                </h3>
                <p className="text-slate-600 text-center max-w-md">
                  There are no packages available for this service at the
                  moment.
                </p>
              </div>
            ) : (
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {rateCards.map((rateCard, index) => (
                  <RateCardItem
                    key={rateCard.id}
                    rateCard={rateCard}
                    onAddToCart={handleAddToCart}
                    index={index}
                  />
                ))}
              </div>
            )}
          </motion.div>

          {/* Sticky Cart Summary (Mobile) */}
          {totalItems > 0 && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="fixed bottom-0 left-0 right-0 bg-white border-t border-slate-200 p-4 shadow-[0_-4px_20px_rgba(0,0,0,0.1)] md:hidden z-40"
            >
              <div className="flex items-center justify-between max-w-7xl mx-auto">
                <div>
                  <p className="text-sm text-slate-600">
                    {totalItems} {totalItems === 1 ? "item" : "items"} in cart
                  </p>
                  <p className="text-xl font-bold text-slate-800">
                    ₹{totalPrice.toFixed(2)}
                  </p>
                </div>
                <button
                  onClick={() => navigate("/cart")}
                  className="flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-primary-500 to-secondary-500 text-white rounded-lg font-medium hover:shadow-[0_4px_12px_rgba(108,99,255,0.3)] transition-all duration-300"
                >
                  <ShoppingCart className="h-5 w-5" />
                  <span>View Cart</span>
                </button>
              </div>
            </motion.div>
          )}
        </div>
      </main>

      <Footer />
    </div>
  );
};

export default RateCardsPage;
