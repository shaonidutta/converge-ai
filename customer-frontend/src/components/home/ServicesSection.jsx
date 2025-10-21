/**
 * ServicesSection Component
 * Display grid of service categories
 */

import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { ArrowRight, AlertCircle } from 'lucide-react';
import ServiceCard from '../services/ServiceCard';
import { ServiceGridSkeleton } from '../common/LoadingSkeleton';
import { Button } from '../ui/button';

/**
 * ServicesSection Component
 * @param {Object} props
 * @param {Array} props.categories - List of service categories
 * @param {boolean} props.loading - Loading state
 * @param {string} props.error - Error message
 */
const ServicesSection = ({ categories = [], loading = false, error = null }) => {
  const navigate = useNavigate();

  // Show loading skeleton
  if (loading) {
    return (
      <section className="py-12 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="mb-8">
            <div className="h-8 w-48 bg-slate-200 rounded animate-pulse mb-2" />
            <div className="h-4 w-64 bg-slate-200 rounded animate-pulse" />
          </div>
          <ServiceGridSkeleton count={6} />
        </div>
      </section>
    );
  }

  // Show error state
  if (error) {
    return (
      <section className="py-12 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center py-12">
            <div className="w-16 h-16 rounded-full bg-red-100 flex items-center justify-center mx-auto mb-4">
              <AlertCircle className="h-8 w-8 text-red-600" />
            </div>
            <h3 className="text-lg font-semibold text-slate-900 mb-2">
              Failed to Load Services
            </h3>
            <p className="text-sm text-slate-600 mb-6">{error}</p>
            <Button
              onClick={() => window.location.reload()}
              className="bg-gradient-to-r from-primary-500 to-secondary-500 hover:from-primary-600 hover:to-secondary-600 text-white"
            >
              Try Again
            </Button>
          </div>
        </div>
      </section>
    );
  }

  // Show empty state
  if (!categories || categories.length === 0) {
    return (
      <section className="py-12 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center py-12">
            <div className="w-16 h-16 rounded-full bg-slate-100 flex items-center justify-center mx-auto mb-4">
              <AlertCircle className="h-8 w-8 text-slate-400" />
            </div>
            <h3 className="text-lg font-semibold text-slate-900 mb-2">
              No Services Available
            </h3>
            <p className="text-sm text-slate-600">
              We're working on adding services to your area. Check back soon!
            </p>
          </div>
        </div>
      </section>
    );
  }

  return (
    <section className="py-12 bg-white">
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
              Browse Services
            </h2>
            <p className="text-slate-600">
              Choose from our wide range of professional home services
            </p>
          </div>

          <Button
            onClick={() => navigate('/services')}
            variant="outline"
            className="hidden md:flex items-center gap-2 hover:bg-primary-50 hover:border-primary-300 hover:text-primary-700 transition-all duration-300"
          >
            View All
            <ArrowRight className="h-4 w-4" />
          </Button>
        </motion.div>

        {/* Services Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {categories.map((category, index) => (
            <ServiceCard key={category.id} category={category} index={index} />
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
            onClick={() => navigate('/services')}
            className="w-full bg-gradient-to-r from-primary-500 to-secondary-500 hover:from-primary-600 hover:to-secondary-600 text-white"
          >
            View All Services
            <ArrowRight className="h-4 w-4 ml-2" />
          </Button>
        </motion.div>
      </div>
    </section>
  );
};

export default ServicesSection;

