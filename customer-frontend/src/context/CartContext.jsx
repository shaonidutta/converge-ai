/**
 * Cart Context
 * Global state management for shopping cart
 * Features:
 * - Add/remove/update cart items
 * - LocalStorage persistence
 * - Auto-calculate totals
 * - Handle duplicate items
 */

import React, { createContext, useState, useEffect, useCallback } from 'react';

// Create Cart Context
export const CartContext = createContext(null);

/**
 * Generate unique ID for cart items
 * @returns {string} Unique ID
 */
const generateId = () => {
  return `cart-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
};

/**
 * Cart Provider Component
 * Wraps the app to provide cart state and methods
 */
export const CartProvider = ({ children }) => {
  const [cart, setCart] = useState({
    items: [],
    totalItems: 0,
    totalPrice: 0,
  });

  // Load cart from localStorage on mount
  useEffect(() => {
    try {
      const savedCart = localStorage.getItem('cart');
      if (savedCart) {
        const parsedCart = JSON.parse(savedCart);
        setCart(parsedCart);
      }
    } catch (error) {
      console.error('Error loading cart from localStorage:', error);
    }
  }, []);

  // Save cart to localStorage whenever it changes
  useEffect(() => {
    try {
      localStorage.setItem('cart', JSON.stringify(cart));
    } catch (error) {
      console.error('Error saving cart to localStorage:', error);
    }
  }, [cart]);

  /**
   * Calculate cart totals
   * @param {Array} items - Cart items
   * @returns {object} { totalItems, totalPrice }
   */
  const calculateTotals = useCallback((items) => {
    const totalItems = items.reduce((sum, item) => sum + item.quantity, 0);
    const totalPrice = items.reduce((sum, item) => sum + (parseFloat(item.price) * item.quantity), 0);
    
    return {
      totalItems,
      totalPrice: parseFloat(totalPrice.toFixed(2)),
    };
  }, []);

  /**
   * Add item to cart or update quantity if exists
   * @param {object} rateCard - Rate card object
   * @param {number} quantity - Quantity to add
   */
  const addToCart = useCallback((rateCard, quantity = 1) => {
    setCart((prevCart) => {
      // Check if item already exists
      const existingItemIndex = prevCart.items.findIndex(
        item => item.rateCardId === rateCard.id
      );

      let newItems;
      
      if (existingItemIndex >= 0) {
        // Update quantity of existing item
        newItems = [...prevCart.items];
        newItems[existingItemIndex] = {
          ...newItems[existingItemIndex],
          quantity: newItems[existingItemIndex].quantity + quantity,
        };
      } else {
        // Add new item
        const newItem = {
          id: generateId(),
          rateCardId: rateCard.id,
          subcategoryId: rateCard.subcategory_id,
          categoryId: rateCard.category_id,
          name: rateCard.name,
          description: rateCard.description || '',
          price: parseFloat(rateCard.price),
          strikePrice: rateCard.strike_price ? parseFloat(rateCard.strike_price) : null,
          quantity: quantity,
          addedAt: new Date().toISOString(),
        };
        newItems = [...prevCart.items, newItem];
      }

      const totals = calculateTotals(newItems);

      return {
        items: newItems,
        ...totals,
      };
    });
  }, [calculateTotals]);

  /**
   * Remove item from cart
   * @param {string} itemId - Cart item ID
   */
  const removeFromCart = useCallback((itemId) => {
    setCart((prevCart) => {
      const newItems = prevCart.items.filter(item => item.id !== itemId);
      const totals = calculateTotals(newItems);

      return {
        items: newItems,
        ...totals,
      };
    });
  }, [calculateTotals]);

  /**
   * Update item quantity
   * @param {string} itemId - Cart item ID
   * @param {number} quantity - New quantity
   */
  const updateQuantity = useCallback((itemId, quantity) => {
    if (quantity <= 0) {
      removeFromCart(itemId);
      return;
    }

    setCart((prevCart) => {
      const newItems = prevCart.items.map(item =>
        item.id === itemId ? { ...item, quantity } : item
      );
      const totals = calculateTotals(newItems);

      return {
        items: newItems,
        ...totals,
      };
    });
  }, [calculateTotals, removeFromCart]);

  /**
   * Clear entire cart
   */
  const clearCart = useCallback(() => {
    setCart({
      items: [],
      totalItems: 0,
      totalPrice: 0,
    });
  }, []);

  /**
   * Get cart item by rate card ID
   * @param {number} rateCardId - Rate card ID
   * @returns {object|null} Cart item or null
   */
  const getCartItem = useCallback((rateCardId) => {
    return cart.items.find(item => item.rateCardId === rateCardId) || null;
  }, [cart.items]);

  /**
   * Check if item is in cart
   * @param {number} rateCardId - Rate card ID
   * @returns {boolean} True if item is in cart
   */
  const isInCart = useCallback((rateCardId) => {
    return cart.items.some(item => item.rateCardId === rateCardId);
  }, [cart.items]);

  /**
   * Get item quantity in cart
   * @param {number} rateCardId - Rate card ID
   * @returns {number} Quantity (0 if not in cart)
   */
  const getItemQuantity = useCallback((rateCardId) => {
    const item = getCartItem(rateCardId);
    return item ? item.quantity : 0;
  }, [getCartItem]);

  const value = {
    // State
    cart,
    items: cart.items,
    totalItems: cart.totalItems,
    totalPrice: cart.totalPrice,
    
    // Methods
    addToCart,
    removeFromCart,
    updateQuantity,
    clearCart,
    getCartItem,
    isInCart,
    getItemQuantity,
  };

  return (
    <CartContext.Provider value={value}>
      {children}
    </CartContext.Provider>
  );
};

export default CartContext;

