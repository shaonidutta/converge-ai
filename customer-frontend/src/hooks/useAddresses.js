/**
 * useAddresses Hook
 * Custom hook for fetching and managing user addresses
 */

import { useState, useEffect, useCallback } from 'react';
import {
  fetchAddresses,
  fetchAddressById,
  addAddress,
  updateAddress,
  deleteAddress,
  setDefaultAddress,
  getDefaultAddress,
} from '../services/addressService';

/**
 * Hook to fetch all addresses with selection management
 * @returns {Object} { addresses, selectedAddress, selectAddress, loading, error, refetch }
 */
export const useAddresses = () => {
  const [addresses, setAddresses] = useState([]);
  const [selectedAddress, setSelectedAddress] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const loadAddresses = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await fetchAddresses();
      setAddresses(data);

      // Check if there's a stored selected address
      const storedAddress = localStorage.getItem('selectedAddress');
      if (storedAddress) {
        try {
          const parsed = JSON.parse(storedAddress);
          // Verify the stored address still exists
          const exists = data.find(addr => addr.id === parsed.id);
          if (exists) {
            setSelectedAddress(exists);
            return;
          }
        } catch (e) {
          console.error('Error parsing stored address:', e);
        }
      }

      // Set default address if exists
      const defaultAddr = data.find(addr => addr.is_default);
      if (defaultAddr) {
        setSelectedAddress(defaultAddr);
        localStorage.setItem('selectedAddress', JSON.stringify(defaultAddr));
      } else if (data.length > 0) {
        // Set first address if no default
        setSelectedAddress(data[0]);
        localStorage.setItem('selectedAddress', JSON.stringify(data[0]));
      }
    } catch (err) {
      setError(err.message);
      console.error('Error loading addresses:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadAddresses();
  }, [loadAddresses]);

  const selectAddress = useCallback((address) => {
    setSelectedAddress(address);
    // Store in localStorage for persistence
    localStorage.setItem('selectedAddress', JSON.stringify(address));
  }, []);

  const refetch = useCallback(() => {
    loadAddresses();
  }, [loadAddresses]);

  return {
    addresses,
    selectedAddress,
    selectAddress,
    loading,
    error,
    refetch,
  };
};

/**
 * Hook to fetch a single address by ID
 * @param {number} addressId - Address ID
 * @returns {Object} { address, loading, error, refetch }
 */
export const useAddress = (addressId) => {
  const [address, setAddress] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const loadAddress = useCallback(async () => {
    if (!addressId) {
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      setError(null);
      const data = await fetchAddressById(addressId);
      setAddress(data);
    } catch (err) {
      setError(err.message);
      console.error(`Error loading address ${addressId}:`, err);
    } finally {
      setLoading(false);
    }
  }, [addressId]);

  useEffect(() => {
    loadAddress();
  }, [loadAddress]);

  const refetch = useCallback(() => {
    loadAddress();
  }, [loadAddress]);

  return { address, loading, error, refetch };
};

/**
 * Hook to manage address actions (add, update, delete, set default)
 * @returns {Object} { addAddress, updateAddress, deleteAddress, setDefaultAddress, loading, error }
 */
export const useAddressActions = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleAddAddress = useCallback(async (addressData) => {
    try {
      setLoading(true);
      setError(null);
      const data = await addAddress(addressData);
      return data;
    } catch (err) {
      setError(err.message);
      console.error('Error adding address:', err);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const handleUpdateAddress = useCallback(async (addressId, addressData) => {
    try {
      setLoading(true);
      setError(null);
      const data = await updateAddress(addressId, addressData);
      return data;
    } catch (err) {
      setError(err.message);
      console.error(`Error updating address ${addressId}:`, err);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const handleDeleteAddress = useCallback(async (addressId) => {
    try {
      setLoading(true);
      setError(null);
      const data = await deleteAddress(addressId);
      return data;
    } catch (err) {
      setError(err.message);
      console.error(`Error deleting address ${addressId}:`, err);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const handleSetDefaultAddress = useCallback(async (addressId) => {
    try {
      setLoading(true);
      setError(null);
      const data = await setDefaultAddress(addressId);
      return data;
    } catch (err) {
      setError(err.message);
      console.error(`Error setting default address ${addressId}:`, err);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  return {
    addAddress: handleAddAddress,
    updateAddress: handleUpdateAddress,
    deleteAddress: handleDeleteAddress,
    setDefaultAddress: handleSetDefaultAddress,
    loading,
    error,
  };
};

/**
 * Export all hooks
 */
export default {
  useAddresses,
  useAddress,
  useAddressActions,
};

