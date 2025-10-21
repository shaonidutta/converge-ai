/**
 * EmptyCart Component
 * Displays empty state when cart has no items
 */

import React from 'react';
import { motion } from 'framer-motion';
import { ShoppingCart, Sparkles } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

const EmptyCart = () => {
  const navigate = useNavigate();

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="flex flex-col items-center justify-center py-16 px-4"
    >
      {/* Icon */}
      <div className="relative mb-6">
        <div className="w-32 h-32 bg-gradient-to-br from-primary-100 to-secondary-100 rounded-full flex items-center justify-center">
          <ShoppingCart className="h-16 w-16 text-primary-500" />
        </div>
        <motion.div
          animate={{
            scale: [1, 1.2, 1],
            rotate: [0, 10, -10, 0],
          }}
          transition={{
            duration: 2,
            repeat: Infinity,
            ease: "easeInOut",
          }}
          className="absolute -top-2 -right-2 w-12 h-12 bg-gradient-to-br from-accent-400 to-accent-500 rounded-full flex items-center justify-center"
        >
          <Sparkles className="h-6 w-6 text-white" />
        </motion.div>
      </div>

      {/* Text */}
      <h2 className="text-2xl font-bold text-slate-900 mb-2">
        Your cart is empty
      </h2>
      <p className="text-slate-600 text-center mb-8 max-w-md">
        Looks like you haven't added any services yet. Browse our services and add them to your cart!
      </p>

      {/* Action Buttons */}
      <div className="flex flex-col sm:flex-row gap-3">
        <motion.button
          onClick={() => navigate('/home')}
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          className="px-6 py-3 bg-gradient-to-r from-primary-500 to-secondary-500 text-white font-semibold rounded-xl hover:shadow-[0_4px_12px_rgba(108,99,255,0.3)] transition-all duration-200"
        >
          Browse Services
        </motion.button>
        <motion.button
          onClick={() => navigate('/home')}
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          className="px-6 py-3 bg-white border-2 border-primary-500 text-primary-500 font-semibold rounded-xl hover:bg-primary-50 transition-all duration-200"
        >
          Go to Home
        </motion.button>
      </div>

      {/* Decorative Elements */}
      <div className="mt-12 grid grid-cols-3 gap-4 max-w-md w-full">
        {[
          { icon: '🏠', label: 'Home Services' },
          { icon: '💼', label: 'Professional' },
          { icon: '⚡', label: 'Quick Booking' },
        ].map((item, index) => (
          <motion.div
            key={index}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            className="flex flex-col items-center gap-2 p-4 bg-slate-50 rounded-lg"
          >
            <span className="text-3xl">{item.icon}</span>
            <span className="text-xs text-slate-600 text-center">{item.label}</span>
          </motion.div>
        ))}
      </div>
    </motion.div>
  );
};

export default EmptyCart;

