/**
 * StarRating Component
 * Interactive star rating input and display
 */

import React, { useState } from 'react';
import { Star } from 'lucide-react';
import { motion } from 'framer-motion';

const StarRating = ({ 
  rating = 0, 
  onChange, 
  readonly = false, 
  size = 'md',
  showLabel = false 
}) => {
  const [hoverRating, setHoverRating] = useState(0);

  // Size configurations
  const sizeClasses = {
    sm: 'h-4 w-4',
    md: 'h-6 w-6',
    lg: 'h-8 w-8'
  };

  const iconSize = sizeClasses[size] || sizeClasses.md;

  const handleClick = (value) => {
    if (!readonly && onChange) {
      onChange(value);
    }
  };

  const handleMouseEnter = (value) => {
    if (!readonly) {
      setHoverRating(value);
    }
  };

  const handleMouseLeave = () => {
    if (!readonly) {
      setHoverRating(0);
    }
  };

  const displayRating = hoverRating || rating;

  const getRatingLabel = (value) => {
    const labels = {
      1: 'Poor',
      2: 'Fair',
      3: 'Good',
      4: 'Very Good',
      5: 'Excellent'
    };
    return labels[value] || '';
  };

  return (
    <div className="flex items-center gap-2">
      <div className="flex items-center gap-1">
        {[1, 2, 3, 4, 5].map((value) => {
          const isFilled = value <= displayRating;
          
          return (
            <motion.button
              key={value}
              type="button"
              onClick={() => handleClick(value)}
              onMouseEnter={() => handleMouseEnter(value)}
              onMouseLeave={handleMouseLeave}
              disabled={readonly}
              whileHover={!readonly ? { scale: 1.1 } : {}}
              whileTap={!readonly ? { scale: 0.95 } : {}}
              className={`
                transition-all duration-200
                ${readonly ? 'cursor-default' : 'cursor-pointer'}
                ${!readonly && 'hover:scale-110'}
              `}
            >
              <Star
                className={`
                  ${iconSize}
                  transition-colors duration-200
                  ${isFilled 
                    ? 'fill-yellow-400 text-yellow-400' 
                    : 'fill-none text-slate-300'
                  }
                  ${!readonly && hoverRating >= value && 'fill-yellow-400 text-yellow-400'}
                `}
              />
            </motion.button>
          );
        })}
      </div>

      {showLabel && displayRating > 0 && (
        <span className="text-sm font-medium text-slate-700">
          {getRatingLabel(displayRating)}
        </span>
      )}

      {readonly && rating > 0 && (
        <span className="text-sm text-slate-600">
          {rating.toFixed(1)}
        </span>
      )}
    </div>
  );
};

export default StarRating;

