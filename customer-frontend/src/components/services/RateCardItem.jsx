/**
 * RateCardItem Component
 * Displays a single rate card with pricing and add to cart functionality
 * Features:
 * - Service name and description
 * - Price display with strike price
 * - Quantity selector (1-10)
 * - Add to cart button
 * - Hover effects
 */

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Check, Minus, Plus } from 'lucide-react';
import AddToCartButton from '../cart/AddToCartButton';

const RateCardItem = ({ rateCard, onAddToCart, index = 0 }) => {
  const [quantity, setQuantity] = useState(1);
  const [loading, setLoading] = useState(false);

  const handleQuantityChange = (delta) => {
    const newQuantity = quantity + delta;
    if (newQuantity >= 1 && newQuantity <= 10) {
      setQuantity(newQuantity);
    }
  };

  const handleAddToCart = async () => {
    setLoading(true);
    try {
      await onAddToCart(rateCard, quantity);
    } finally {
      setLoading(false);
    }
  };

  const price = parseFloat(rateCard.price);
  const strikePrice = rateCard.strike_price ? parseFloat(rateCard.strike_price) : null;
  const discount = strikePrice ? Math.round(((strikePrice - price) / strikePrice) * 100) : 0;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, delay: index * 0.1 }}
      className="bg-white rounded-xl shadow-[0_4px_20px_rgba(0,0,0,0.05)] hover:shadow-[0_8px_32px_rgba(108,99,255,0.15)] transition-all duration-300 p-6"
    >
      {/* Header */}
      <div className="mb-4">
        <div className="flex items-start justify-between mb-2">
          <h3 className="text-xl font-semibold text-slate-800 flex-1">
            {rateCard.name}
          </h3>
          {discount > 0 && (
            <span className="ml-2 px-2 py-1 bg-green-100 text-green-700 text-xs font-semibold rounded-full">
              {discount}% OFF
            </span>
          )}
        </div>
        
        {rateCard.description && (
          <p className="text-sm text-slate-600 line-clamp-2">
            {rateCard.description}
          </p>
        )}
      </div>

      {/* Price */}
      <div className="mb-4">
        <div className="flex items-baseline gap-2">
          <span className="text-3xl font-bold text-slate-800">
            ₹{price.toFixed(2)}
          </span>
          {strikePrice && (
            <span className="text-lg text-slate-400 line-through">
              ₹{strikePrice.toFixed(2)}
            </span>
          )}
        </div>
      </div>

      {/* Divider */}
      <div className="border-t border-slate-200 my-4"></div>

      {/* Quantity Selector and Add to Cart */}
      <div className="flex items-center gap-4">
        {/* Quantity Selector */}
        <div className="flex items-center gap-2">
          <span className="text-sm text-slate-600 font-medium">Qty:</span>
          <div className="flex items-center border border-slate-300 rounded-lg overflow-hidden">
            <button
              onClick={() => handleQuantityChange(-1)}
              disabled={quantity <= 1}
              className="p-2 hover:bg-slate-100 disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-200"
            >
              <Minus className="h-4 w-4 text-slate-600" />
            </button>
            <span className="px-4 py-2 text-sm font-medium text-slate-800 min-w-[40px] text-center">
              {quantity}
            </span>
            <button
              onClick={() => handleQuantityChange(1)}
              disabled={quantity >= 10}
              className="p-2 hover:bg-slate-100 disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-200"
            >
              <Plus className="h-4 w-4 text-slate-600" />
            </button>
          </div>
        </div>

        {/* Add to Cart Button */}
        <AddToCartButton
          onClick={handleAddToCart}
          loading={loading}
          className="flex-1"
        />
      </div>

      {/* Total Price */}
      {quantity > 1 && (
        <motion.div
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: 'auto' }}
          className="mt-4 pt-4 border-t border-slate-200"
        >
          <div className="flex items-center justify-between">
            <span className="text-sm text-slate-600">Total:</span>
            <span className="text-xl font-bold text-primary-600">
              ₹{(price * quantity).toFixed(2)}
            </span>
          </div>
        </motion.div>
      )}
    </motion.div>
  );
};

export default RateCardItem;

