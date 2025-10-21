/**
 * useCart Hook
 * Custom hook to access Cart Context
 * Provides easy access to cart state and methods
 */

import { useContext } from 'react';
import { CartContext } from '../context/CartContext';

/**
 * Hook to access cart context
 * @returns {object} Cart state and methods
 * @throws {Error} If used outside CartProvider
 */
export const useCart = () => {
  const context = useContext(CartContext);
  
  if (!context) {
    throw new Error('useCart must be used within a CartProvider');
  }
  
  return context;
};

export default useCart;

