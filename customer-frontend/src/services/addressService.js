/**
 * Address Service
 * Handles all address-related API calls
 */

import api from './api';

/**
 * Fetch all user addresses
 * @returns {Promise<Array>} List of addresses
 */
export const fetchAddresses = async () => {
  try {
    const response = await api.addresses.getAll();
    return response.data;
  } catch (error) {
    console.error('Error fetching addresses:', error);
    throw new Error(error.response?.data?.detail || 'Failed to fetch addresses');
  }
};

/**
 * Fetch address by ID
 * @param {number} addressId - Address ID
 * @returns {Promise<Object>} Address details
 */
export const fetchAddressById = async (addressId) => {
  try {
    const response = await api.addresses.getById(addressId);
    return response.data;
  } catch (error) {
    console.error(`Error fetching address ${addressId}:`, error);
    throw new Error(error.response?.data?.detail || 'Failed to fetch address');
  }
};

/**
 * Add new address
 * @param {Object} addressData - Address details (address_line1, address_line2, city, state, pincode, is_default)
 * @returns {Promise<Object>} Created address
 */
export const addAddress = async (addressData) => {
  try {
    const response = await api.addresses.add(addressData);
    return response.data;
  } catch (error) {
    console.error('Error adding address:', error);
    throw new Error(error.response?.data?.detail || 'Failed to add address');
  }
};

/**
 * Update address
 * @param {number} addressId - Address ID
 * @param {Object} addressData - Updated address data
 * @returns {Promise<Object>} Updated address
 */
export const updateAddress = async (addressId, addressData) => {
  try {
    const response = await api.addresses.update(addressId, addressData);
    return response.data;
  } catch (error) {
    console.error(`Error updating address ${addressId}:`, error);
    throw new Error(error.response?.data?.detail || 'Failed to update address');
  }
};

/**
 * Delete address
 * @param {number} addressId - Address ID
 * @returns {Promise<Object>} Success message
 */
export const deleteAddress = async (addressId) => {
  try {
    const response = await api.addresses.delete(addressId);
    return response.data;
  } catch (error) {
    console.error(`Error deleting address ${addressId}:`, error);
    throw new Error(error.response?.data?.detail || 'Failed to delete address');
  }
};

/**
 * Set address as default
 * @param {number} addressId - Address ID
 * @returns {Promise<Object>} Updated address
 */
export const setDefaultAddress = async (addressId) => {
  try {
    // Update address with is_default = true
    const response = await api.addresses.update(addressId, { is_default: true });
    return response.data;
  } catch (error) {
    console.error(`Error setting default address ${addressId}:`, error);
    throw new Error(error.response?.data?.detail || 'Failed to set default address');
  }
};

/**
 * Get default address
 * @returns {Promise<Object|null>} Default address or null
 */
export const getDefaultAddress = async () => {
  try {
    const response = await api.addresses.getAll();
    const addresses = response.data;
    
    // Find default address
    const defaultAddress = addresses.find(addr => addr.is_default);
    return defaultAddress || (addresses.length > 0 ? addresses[0] : null);
  } catch (error) {
    console.error('Error getting default address:', error);
    throw new Error(error.response?.data?.detail || 'Failed to get default address');
  }
};

/**
 * Export all address service functions
 */
export default {
  fetchAddresses,
  fetchAddressById,
  addAddress,
  updateAddress,
  deleteAddress,
  setDefaultAddress,
  getDefaultAddress,
};

