/**
 * Cart Migration Utility
 * Fixes existing cart items that may be missing required fields
 */

/**
 * Migrate existing cart items to new structure
 * @param {Array} cartItems - Existing cart items
 * @returns {Array} Migrated cart items
 */
export const migrateCartItems = (cartItems) => {
  if (!Array.isArray(cartItems)) {
    return [];
  }

  return cartItems.map(item => {
    // Ensure all required fields exist
    const migratedItem = {
      ...item,
      // Add missing fields with defaults
      subcategoryName: item.subcategoryName || item.name || 'Service',
      categoryName: item.categoryName || 'Category',
      duration: item.duration || '1 hour',
      description: item.description || '',
      // Ensure proper data types
      price: typeof item.price === 'number' ? item.price : parseFloat(item.price) || 0,
      quantity: typeof item.quantity === 'number' ? item.quantity : parseInt(item.quantity) || 1,
      strikePrice: item.strikePrice ? (typeof item.strikePrice === 'number' ? item.strikePrice : parseFloat(item.strikePrice)) : null,
    };

    return migratedItem;
  });
};

/**
 * Check if cart needs migration
 * @param {Array} cartItems - Cart items to check
 * @returns {boolean} True if migration is needed
 */
export const needsMigration = (cartItems) => {
  if (!Array.isArray(cartItems) || cartItems.length === 0) {
    return false;
  }

  return cartItems.some(item => 
    !item.subcategoryName || 
    !item.categoryName || 
    !item.duration ||
    typeof item.price !== 'number' ||
    typeof item.quantity !== 'number'
  );
};

/**
 * Migrate cart in localStorage if needed
 */
export const migrateLocalStorageCart = () => {
  try {
    const savedCart = localStorage.getItem('cart');
    if (!savedCart) {
      return;
    }

    const parsedCart = JSON.parse(savedCart);
    if (!parsedCart.items || !Array.isArray(parsedCart.items)) {
      return;
    }

    if (needsMigration(parsedCart.items)) {
      console.log('🔄 Migrating cart items to new structure...');
      
      const migratedItems = migrateCartItems(parsedCart.items);
      
      // Recalculate totals
      const totalItems = migratedItems.reduce((sum, item) => sum + item.quantity, 0);
      const totalPrice = migratedItems.reduce((sum, item) => sum + (item.price * item.quantity), 0);
      
      const migratedCart = {
        ...parsedCart,
        items: migratedItems,
        totalItems,
        totalPrice: parseFloat(totalPrice.toFixed(2))
      };

      localStorage.setItem('cart', JSON.stringify(migratedCart));
      console.log('✅ Cart migration completed successfully');
    }
  } catch (error) {
    console.error('❌ Error migrating cart:', error);
    // Clear corrupted cart data
    localStorage.removeItem('cart');
  }
};
