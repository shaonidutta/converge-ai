/**
 * AddToCartButton Component
 * Button to add items to cart with loading and success states
 * Features:
 * - Gradient button design
 * - Loading spinner
 * - Success checkmark animation
 * - Disabled state
 */

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ShoppingCart, Check, Loader2 } from 'lucide-react';

const AddToCartButton = ({ 
  onClick, 
  disabled = false, 
  loading = false,
  className = '',
  children = 'Add to Cart'
}) => {
  const [showSuccess, setShowSuccess] = useState(false);

  const handleClick = async () => {
    if (disabled || loading) return;

    try {
      await onClick();
      
      // Show success animation
      setShowSuccess(true);
      setTimeout(() => {
        setShowSuccess(false);
      }, 2000);
    } catch (error) {
      console.error('Error adding to cart:', error);
    }
  };

  return (
    <motion.button
      onClick={handleClick}
      disabled={disabled || loading}
      whileHover={!disabled && !loading ? { scale: 1.02 } : {}}
      whileTap={!disabled && !loading ? { scale: 0.98 } : {}}
      className={`
        relative flex items-center justify-center gap-2 px-6 py-3 
        bg-gradient-to-r from-primary-500 to-secondary-500 
        text-white rounded-lg font-medium 
        hover:shadow-[0_4px_12px_rgba(108,99,255,0.3)] 
        transition-all duration-300
        disabled:opacity-50 disabled:cursor-not-allowed
        ${className}
      `}
    >
      <AnimatePresence mode="wait">
        {loading ? (
          <motion.div
            key="loading"
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.8 }}
            className="flex items-center gap-2"
          >
            <Loader2 className="h-5 w-5 animate-spin" />
            <span>Adding...</span>
          </motion.div>
        ) : showSuccess ? (
          <motion.div
            key="success"
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.8 }}
            className="flex items-center gap-2"
          >
            <Check className="h-5 w-5" />
            <span>Added!</span>
          </motion.div>
        ) : (
          <motion.div
            key="default"
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.8 }}
            className="flex items-center gap-2"
          >
            <ShoppingCart className="h-5 w-5" />
            <span>{children}</span>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.button>
  );
};

export default AddToCartButton;

