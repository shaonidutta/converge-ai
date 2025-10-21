/**
 * ServiceCard Component
 * Reusable card for displaying service categories
 */

import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { ArrowRight, Layers } from 'lucide-react';

/**
 * ServiceCard Component
 * @param {Object} props
 * @param {Object} props.category - Category data (id, name, description, image, subcategory_count)
 * @param {number} props.index - Card index for staggered animation
 */
const ServiceCard = ({ category, index = 0 }) => {
  const navigate = useNavigate();

  const handleClick = () => {
    navigate(`/services/${category.id}`);
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
      {/* Gradient Border Effect on Hover */}
      <div className="absolute inset-0 bg-gradient-to-br from-primary-500 to-secondary-500 opacity-0 group-hover:opacity-100 transition-opacity duration-300 rounded-xl" />
      <div className="absolute inset-[2px] bg-white rounded-xl" />

      {/* Content */}
      <div className="relative p-6">
        {/* Image/Icon Section */}
        <div className="relative mb-4 h-48 rounded-lg overflow-hidden bg-gradient-to-br from-primary-50 to-secondary-50">
          {category.image ? (
            <img
              src={category.image}
              alt={category.name}
              className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500"
            />
          ) : (
            <div className="w-full h-full flex items-center justify-center">
              <div className="w-20 h-20 rounded-full bg-gradient-to-br from-primary-500 to-secondary-500 flex items-center justify-center shadow-[0_8px_24px_rgba(108,99,255,0.3)]">
                <Layers className="h-10 w-10 text-white" />
              </div>
            </div>
          )}

          {/* Gradient Overlay */}
          <div className="absolute inset-0 bg-gradient-to-t from-black/20 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
        </div>

        {/* Title */}
        <h3 className="text-lg font-bold text-slate-900 mb-2 group-hover:text-primary-600 transition-colors duration-300">
          {category.name}
        </h3>

        {/* Description */}
        <p className="text-sm text-slate-600 mb-4 line-clamp-2 min-h-[40px]">
          {category.description || 'Professional services at your doorstep'}
        </p>

        {/* Footer */}
        <div className="flex items-center justify-between">
          {/* Subcategory Count Badge */}
          <div className="flex items-center gap-2 px-3 py-1.5 bg-gradient-to-r from-primary-50 to-secondary-50 rounded-full">
            <Layers className="h-3.5 w-3.5 text-primary-600" />
            <span className="text-xs font-semibold text-primary-700">
              {category.subcategory_count || 0} Services
            </span>
          </div>

          {/* Explore Button */}
          <motion.div
            whileHover={{ x: 4 }}
            className="flex items-center gap-1 text-sm font-semibold text-primary-600 group-hover:text-secondary-600 transition-colors duration-300"
          >
            <span>Explore</span>
            <ArrowRight className="h-4 w-4" />
          </motion.div>
        </div>
      </div>

      {/* Active Indicator */}
      {category.is_active && (
        <div className="absolute top-4 right-4">
          <div className="w-2 h-2 rounded-full bg-green-500 shadow-[0_0_8px_rgba(34,197,94,0.6)] animate-pulse" />
        </div>
      )}
    </motion.div>
  );
};

export default ServiceCard;

