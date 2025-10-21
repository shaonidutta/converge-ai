/**
 * SubcategoryCard Component
 * Displays a single subcategory with image, name, description, and rate card count
 * Features:
 * - Hover effects (scale, shadow)
 * - Click navigation to rate cards page
 * - Stagger animation
 * - Fallback icon if no image
 */

import React from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Wrench, ArrowRight } from 'lucide-react';

const SubcategoryCard = ({ subcategory, index = 0 }) => {
  const navigate = useNavigate();

  const handleClick = () => {
    navigate(`/services/${subcategory.category_id}/${subcategory.id}`);
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, delay: index * 0.1 }}
      whileHover={{ y: -4 }}
      onClick={handleClick}
      className="group relative bg-white rounded-xl overflow-hidden shadow-[0_4px_20px_rgba(0,0,0,0.05)] hover:shadow-[0_8px_32px_rgba(108,99,255,0.15)] transition-all duration-300 cursor-pointer"
    >
      {/* Gradient Border on Hover */}
      <div className="absolute inset-0 bg-gradient-to-br from-primary-500 to-secondary-500 opacity-0 group-hover:opacity-100 transition-opacity duration-300 rounded-xl" 
           style={{ padding: '2px' }}>
        <div className="bg-white rounded-xl h-full w-full"></div>
      </div>

      {/* Content */}
      <div className="relative p-6">
        {/* Image or Icon */}
        <div className="mb-4 flex items-center justify-center h-20 w-20 mx-auto bg-gradient-to-br from-primary-50 to-secondary-50 rounded-xl group-hover:scale-110 transition-transform duration-300">
          {subcategory.image ? (
            <img
              src={subcategory.image}
              alt={subcategory.name}
              className="h-12 w-12 object-contain"
            />
          ) : (
            <Wrench className="h-12 w-12 text-primary-500" />
          )}
        </div>

        {/* Name */}
        <h3 className="text-lg font-semibold text-slate-800 mb-2 text-center group-hover:text-primary-600 transition-colors duration-300">
          {subcategory.name}
        </h3>

        {/* Description */}
        <p className="text-sm text-slate-600 mb-4 text-center line-clamp-2 min-h-[40px]">
          {subcategory.description || 'Professional service available'}
        </p>

        {/* Rate Card Count Badge */}
        <div className="flex items-center justify-center gap-2 mb-4">
          <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-primary-50 text-primary-700">
            {subcategory.rate_card_count || 0} {subcategory.rate_card_count === 1 ? 'Option' : 'Options'}
          </span>
        </div>

        {/* View Rates Button */}
        <button
          className="w-full flex items-center justify-center gap-2 px-4 py-2.5 bg-gradient-to-r from-primary-500 to-secondary-500 text-white rounded-lg font-medium hover:shadow-[0_4px_12px_rgba(108,99,255,0.3)] transition-all duration-300 group-hover:scale-105"
        >
          <span>View Rates</span>
          <ArrowRight className="h-4 w-4 group-hover:translate-x-1 transition-transform duration-300" />
        </button>
      </div>
    </motion.div>
  );
};

export default SubcategoryCard;

