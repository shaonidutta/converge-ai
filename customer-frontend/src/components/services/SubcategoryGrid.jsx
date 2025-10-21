/**
 * SubcategoryGrid Component
 * Displays a grid of subcategory cards with loading and error states
 * Features:
 * - Responsive grid (1/2/3 columns)
 * - Loading skeleton
 * - Error state with retry
 * - Empty state
 */

import React from 'react';
import { motion } from 'framer-motion';
import { AlertCircle, RefreshCw } from 'lucide-react';
import SubcategoryCard from './SubcategoryCard';
import { ServiceGridSkeleton } from '../common/LoadingSkeleton';

const SubcategoryGrid = ({ subcategories, loading, error, onRetry }) => {
  // Loading State
  if (loading) {
    return <ServiceGridSkeleton count={6} />;
  }

  // Error State
  if (error) {
    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex flex-col items-center justify-center py-16 px-4"
      >
        <div className="bg-red-50 rounded-full p-4 mb-4">
          <AlertCircle className="h-12 w-12 text-red-500" />
        </div>
        <h3 className="text-xl font-semibold text-slate-800 mb-2">
          Failed to Load Subcategories
        </h3>
        <p className="text-slate-600 mb-6 text-center max-w-md">
          {error}
        </p>
        {onRetry && (
          <button
            onClick={onRetry}
            className="flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-primary-500 to-secondary-500 text-white rounded-lg font-medium hover:shadow-[0_4px_12px_rgba(108,99,255,0.3)] transition-all duration-300"
          >
            <RefreshCw className="h-4 w-4" />
            <span>Try Again</span>
          </button>
        )}
      </motion.div>
    );
  }

  // Empty State
  if (!subcategories || subcategories.length === 0) {
    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex flex-col items-center justify-center py-16 px-4"
      >
        <div className="bg-slate-100 rounded-full p-4 mb-4">
          <AlertCircle className="h-12 w-12 text-slate-400" />
        </div>
        <h3 className="text-xl font-semibold text-slate-800 mb-2">
          No Subcategories Found
        </h3>
        <p className="text-slate-600 text-center max-w-md">
          There are no subcategories available for this service category at the moment.
        </p>
      </motion.div>
    );
  }

  // Grid of Subcategories
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {subcategories.map((subcategory, index) => (
        <SubcategoryCard
          key={subcategory.id}
          subcategory={subcategory}
          index={index}
        />
      ))}
    </div>
  );
};

export default SubcategoryGrid;

