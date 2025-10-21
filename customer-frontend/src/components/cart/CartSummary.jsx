/**
 * CartSummary Component
 * Displays price breakdown and checkout button
 */

import React from 'react';
import { motion } from 'framer-motion';
import { IndianRupee, ShoppingBag, Tag } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

const CartSummary = ({ items, promoDiscount = 0 }) => {
  const navigate = useNavigate();

  // Calculate totals
  const subtotal = items.reduce((sum, item) => sum + (item.price * item.quantity), 0);
  const tax = subtotal * 0.18; // 18% GST
  const discount = promoDiscount;
  const total = subtotal + tax - discount;

  const handleCheckout = () => {
    navigate('/checkout');
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-white rounded-xl border border-slate-200 p-6 sticky top-24"
    >
      {/* Header */}
      <div className="flex items-center gap-2 mb-6">
        <ShoppingBag className="h-5 w-5 text-primary-500" />
        <h2 className="text-lg font-bold text-slate-900">Order Summary</h2>
      </div>

      {/* Price Breakdown */}
      <div className="space-y-3 mb-6">
        {/* Subtotal */}
        <div className="flex items-center justify-between text-slate-600">
          <span>Subtotal ({items.length} {items.length === 1 ? 'item' : 'items'})</span>
          <span className="flex items-center font-medium">
            <IndianRupee className="h-4 w-4" />
            {subtotal.toFixed(2)}
          </span>
        </div>

        {/* Tax */}
        <div className="flex items-center justify-between text-slate-600">
          <span>Tax (GST 18%)</span>
          <span className="flex items-center font-medium">
            <IndianRupee className="h-4 w-4" />
            {tax.toFixed(2)}
          </span>
        </div>

        {/* Discount */}
        {discount > 0 && (
          <div className="flex items-center justify-between text-green-600">
            <span className="flex items-center gap-1">
              <Tag className="h-4 w-4" />
              Discount
            </span>
            <span className="flex items-center font-medium">
              - <IndianRupee className="h-4 w-4" />
              {discount.toFixed(2)}
            </span>
          </div>
        )}

        {/* Divider */}
        <div className="border-t border-slate-200 pt-3">
          <div className="flex items-center justify-between text-slate-900">
            <span className="text-lg font-bold">Total</span>
            <span className="text-xl font-bold flex items-center">
              <IndianRupee className="h-5 w-5" />
              {total.toFixed(2)}
            </span>
          </div>
        </div>
      </div>

      {/* Checkout Button */}
      <motion.button
        onClick={handleCheckout}
        whileHover={{ scale: 1.02 }}
        whileTap={{ scale: 0.98 }}
        className="w-full py-3 bg-gradient-to-r from-primary-500 to-secondary-500 text-white font-semibold rounded-xl hover:shadow-[0_4px_12px_rgba(108,99,255,0.3)] transition-all duration-200"
      >
        Proceed to Checkout
      </motion.button>

      {/* Info Text */}
      <p className="text-xs text-slate-500 text-center mt-4">
        You can review and modify your order before final confirmation
      </p>
    </motion.div>
  );
};

export default CartSummary;

