/**
 * CartItem Component
 * Displays individual cart item with quantity controls
 */

import React from 'react';
import { motion } from 'framer-motion';
import { Minus, Plus, Trash2, Clock, IndianRupee } from 'lucide-react';
import { useCart } from '../../hooks/useCart';

const CartItem = ({ item }) => {
  const { updateQuantity, removeFromCart } = useCart();

  const handleQuantityChange = (newQuantity) => {
    if (newQuantity >= 1 && newQuantity <= 10) {
      updateQuantity(item.id, newQuantity);
    }
  };

  const handleRemove = () => {
    removeFromCart(item.id);
  };

  const itemTotal = item.price * item.quantity;

  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, x: -100 }}
      className="bg-white rounded-xl border border-slate-200 p-4 hover:shadow-[0_4px_12px_rgba(108,99,255,0.1)] transition-all duration-200"
    >
      <div className="flex gap-4">
        {/* Service Icon */}
        <div className="flex-shrink-0 w-20 h-20 bg-gradient-to-br from-primary-100 to-secondary-100 rounded-lg flex items-center justify-center">
          <span className="text-2xl">{item.icon || '🛠️'}</span>
        </div>

        {/* Item Details */}
        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between gap-2 mb-2">
            <div className="flex-1 min-w-0">
              <h3 className="font-semibold text-slate-900 truncate">
                {item.subcategoryName}
              </h3>
              <p className="text-sm text-slate-600 truncate">
                {item.categoryName}
              </p>
            </div>
            <button
              onClick={handleRemove}
              className="flex-shrink-0 p-2 text-red-500 hover:bg-red-50 rounded-lg transition-colors duration-200"
              title="Remove from cart"
            >
              <Trash2 className="h-4 w-4" />
            </button>
          </div>

          {/* Rate Card Details */}
          <div className="flex items-center gap-4 text-sm text-slate-600 mb-3">
            <div className="flex items-center gap-1">
              <Clock className="h-4 w-4" />
              <span>{item.duration}</span>
            </div>
            <div className="flex items-center gap-1">
              <IndianRupee className="h-4 w-4" />
              <span>{parseFloat(item.price).toFixed(2)}</span>
            </div>
          </div>

          {/* Quantity Controls & Price */}
          <div className="flex items-center justify-between">
            {/* Quantity Selector */}
            <div className="flex items-center gap-2">
              <span className="text-sm text-slate-600">Quantity:</span>
              <div className="flex items-center gap-2 bg-slate-100 rounded-lg p-1">
                <button
                  onClick={() => handleQuantityChange(item.quantity - 1)}
                  disabled={item.quantity <= 1}
                  className="p-1 hover:bg-white rounded disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-200"
                >
                  <Minus className="h-4 w-4 text-slate-600" />
                </button>
                <span className="w-8 text-center font-medium text-slate-900">
                  {item.quantity}
                </span>
                <button
                  onClick={() => handleQuantityChange(item.quantity + 1)}
                  disabled={item.quantity >= 10}
                  className="p-1 hover:bg-white rounded disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-200"
                >
                  <Plus className="h-4 w-4 text-slate-600" />
                </button>
              </div>
            </div>

            {/* Item Total */}
            <div className="text-right">
              <p className="text-sm text-slate-600">Total</p>
              <p className="text-lg font-bold text-slate-900 flex items-center">
                <IndianRupee className="h-4 w-4" />
                {itemTotal.toFixed(2)}
              </p>
            </div>
          </div>
        </div>
      </div>
    </motion.div>
  );
};

export default CartItem;

