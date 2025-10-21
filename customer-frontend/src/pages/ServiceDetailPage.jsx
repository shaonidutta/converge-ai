/**
 * Service Detail Page
 * Displays category details and list of subcategories
 * Route: /services/:categoryId
 * Features:
 * - Breadcrumb navigation
 * - Category header with image and description
 * - Subcategories grid
 * - Loading and error states
 */

import React, { useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Home, ChevronRight, Sparkles } from 'lucide-react';
import { useCategory } from '../hooks/useCategories';
import { useSubcategories } from '../hooks/useSubcategories';
import SubcategoryGrid from '../components/services/SubcategoryGrid';
import Navbar from '../components/common/Navbar';
import Footer from '../components/common/Footer';

const ServiceDetailPage = () => {
  const { categoryId } = useParams();
  const navigate = useNavigate();

  // Fetch category details
  const { category, loading: categoryLoading, error: categoryError } = useCategory(parseInt(categoryId));
  
  // Fetch subcategories
  const { subcategories, loading: subcategoriesLoading, error: subcategoriesError, refetch } = useSubcategories(parseInt(categoryId));

  // Scroll to top on mount
  useEffect(() => {
    window.scrollTo(0, 0);
  }, []);

  // Check authentication
  useEffect(() => {
    const user = localStorage.getItem('user');
    if (!user) {
      navigate('/login');
    }
  }, [navigate]);

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
            className="flex items-center gap-2 text-sm text-slate-600 mb-8"
          >
            <Link to="/home" className="hover:text-primary-600 transition-colors duration-200">
              <Home className="h-4 w-4" />
            </Link>
            <ChevronRight className="h-4 w-4" />
            <Link to="/home" className="hover:text-primary-600 transition-colors duration-200">
              Services
            </Link>
            <ChevronRight className="h-4 w-4" />
            <span className="text-slate-800 font-medium">
              {category?.name || 'Loading...'}
            </span>
          </motion.nav>

          {/* Category Header */}
          {!categoryLoading && category && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="bg-white rounded-2xl shadow-[0_4px_20px_rgba(0,0,0,0.05)] p-8 mb-8"
            >
              <div className="flex flex-col md:flex-row items-center gap-6">
                {/* Category Icon/Image */}
                <div className="flex-shrink-0">
                  <div className="h-24 w-24 bg-gradient-to-br from-primary-500 to-secondary-500 rounded-2xl flex items-center justify-center">
                    {category.image ? (
                      <img
                        src={category.image}
                        alt={category.name}
                        className="h-16 w-16 object-contain"
                      />
                    ) : (
                      <Sparkles className="h-16 w-16 text-white" />
                    )}
                  </div>
                </div>

                {/* Category Info */}
                <div className="flex-1 text-center md:text-left">
                  <h1 className="text-3xl md:text-4xl font-bold text-slate-800 mb-3">
                    {category.name}
                  </h1>
                  <p className="text-lg text-slate-600 mb-4">
                    {category.description}
                  </p>
                  <div className="flex items-center justify-center md:justify-start gap-4">
                    <span className="inline-flex items-center px-4 py-2 rounded-full text-sm font-medium bg-primary-50 text-primary-700">
                      {category.subcategory_count || subcategories.length} {category.subcategory_count === 1 ? 'Service' : 'Services'}
                    </span>
                    <span className="inline-flex items-center px-4 py-2 rounded-full text-sm font-medium bg-green-50 text-green-700">
                      ✓ Verified Professionals
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
              Choose a Service
            </h2>
            <p className="text-slate-600">
              Select from our range of professional services
            </p>
          </motion.div>

          {/* Subcategories Grid */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
          >
            <SubcategoryGrid
              subcategories={subcategories}
              loading={subcategoriesLoading}
              error={subcategoriesError}
              onRetry={refetch}
            />
          </motion.div>
        </div>
      </main>

      <Footer />
    </div>
  );
};

export default ServiceDetailPage;

