/**
 * AddressesPage Component
 * Dedicated page for managing user addresses
 * Features:
 * - View all addresses in a grid layout
 * - Add new address
 * - Edit existing address
 * - Delete address
 * - Set default address
 * - Empty state when no addresses
 * - Loading and error states
 */

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { MapPin, Plus, Home } from 'lucide-react';
import { useAddresses } from '../hooks/useAddresses';
import { addAddress, updateAddress, deleteAddress, setDefaultAddress } from '../services/addressService';
import Navbar from '../components/common/Navbar';
import Footer from '../components/common/Footer';
import AddressCard from '../components/profile/AddressCard';
import AddressForm from '../components/profile/AddressForm';
import { CardSkeleton } from '../components/common/LoadingSkeleton';

const AddressesPage = () => {
  const { addresses, loading, error, refetch } = useAddresses();
  const [isAddingAddress, setIsAddingAddress] = useState(false);
  const [editingAddress, setEditingAddress] = useState(null);
  const [actionLoading, setActionLoading] = useState(false);

  // Handle add address
  const handleAddAddress = async (addressData) => {
    setActionLoading(true);
    try {
      await addAddress(addressData);
      await refetch();
      setIsAddingAddress(false);
    } catch (error) {
      console.error('Failed to add address:', error);
      alert(error.message || 'Failed to add address');
    } finally {
      setActionLoading(false);
    }
  };

  // Handle edit address
  const handleEditAddress = (address) => {
    setEditingAddress(address);
  };

  // Handle update address
  const handleUpdateAddress = async (addressData) => {
    if (!editingAddress) return;

    setActionLoading(true);
    try {
      await updateAddress(editingAddress.id, addressData);
      await refetch();
      setEditingAddress(null);
    } catch (error) {
      console.error('Failed to update address:', error);
      alert(error.message || 'Failed to update address');
    } finally {
      setActionLoading(false);
    }
  };

  // Handle delete address
  const handleAddressDelete = async (addressId) => {
    if (!window.confirm('Are you sure you want to delete this address?')) {
      return;
    }

    setActionLoading(true);
    try {
      await deleteAddress(addressId);
      await refetch();
    } catch (error) {
      console.error('Failed to delete address:', error);
      alert(error.message || 'Failed to delete address');
    } finally {
      setActionLoading(false);
    }
  };

  // Handle set default address
  const handleSetDefaultAddress = async (addressId) => {
    setActionLoading(true);
    try {
      await setDefaultAddress(addressId);
      await refetch();
    } catch (error) {
      console.error('Failed to set default address:', error);
      alert(error.message || 'Failed to set default address');
    } finally {
      setActionLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-primary-50/20 flex flex-col">
      <Navbar />

      <main className="flex-1 pt-20 pb-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          {/* Header */}
          <div className="mb-8">
            <div className="flex items-center justify-between">
              <div>
                <div className="flex items-center gap-3 mb-2">
                  <MapPin className="h-8 w-8 text-primary-500" />
                  <h1 className="text-3xl font-bold text-slate-900">My Addresses</h1>
                </div>
                <p className="text-slate-600">
                  Manage your delivery and service addresses
                </p>
              </div>

              {/* Add Address Button */}
              {!isAddingAddress && !editingAddress && addresses.length > 0 && (
                <motion.button
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={() => setIsAddingAddress(true)}
                  className="flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-primary-500 to-secondary-500 text-white font-semibold rounded-xl hover:shadow-[0_4px_12px_rgba(108,99,255,0.3)] transition-all duration-200"
                >
                  <Plus className="h-5 w-5" />
                  Add Address
                </motion.button>
              )}
            </div>
          </div>

          {/* Content */}
          {loading ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {[1, 2, 3].map((i) => (
                <CardSkeleton key={i} className="h-48" />
              ))}
            </div>
          ) : error ? (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="p-8 bg-red-50 border border-red-200 rounded-xl text-red-700 text-center"
            >
              <p className="font-medium mb-2">Failed to load addresses</p>
              <p className="text-sm">{error}</p>
              <button
                onClick={refetch}
                className="mt-4 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
              >
                Try Again
              </button>
            </motion.div>
          ) : (
            <div className="space-y-6">
              {/* Add Address Form */}
              <AnimatePresence>
                {isAddingAddress && (
                  <motion.div
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: 'auto' }}
                    exit={{ opacity: 0, height: 0 }}
                    transition={{ duration: 0.3 }}
                  >
                    <AddressForm
                      onSave={handleAddAddress}
                      onCancel={() => setIsAddingAddress(false)}
                      loading={actionLoading}
                    />
                  </motion.div>
                )}
              </AnimatePresence>

              {/* Edit Address Form */}
              <AnimatePresence>
                {editingAddress && (
                  <motion.div
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: 'auto' }}
                    exit={{ opacity: 0, height: 0 }}
                    transition={{ duration: 0.3 }}
                  >
                    <AddressForm
                      address={editingAddress}
                      onSave={handleUpdateAddress}
                      onCancel={() => setEditingAddress(null)}
                      loading={actionLoading}
                    />
                  </motion.div>
                )}
              </AnimatePresence>

              {/* Addresses Grid or Empty State */}
              {addresses.length === 0 ? (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="text-center py-16 bg-white rounded-xl border border-slate-200"
                >
                  <div className="w-20 h-20 bg-primary-100 rounded-full flex items-center justify-center mx-auto mb-6">
                    <Home className="h-10 w-10 text-primary-500" />
                  </div>
                  <h3 className="text-xl font-semibold text-slate-900 mb-2">
                    No Addresses Yet
                  </h3>
                  <p className="text-slate-600 mb-6 max-w-md mx-auto">
                    Add your first address to start booking services at your preferred location
                  </p>
                  <motion.button
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    onClick={() => setIsAddingAddress(true)}
                    className="px-6 py-3 bg-gradient-to-r from-primary-500 to-secondary-500 text-white font-semibold rounded-xl hover:shadow-[0_4px_12px_rgba(108,99,255,0.3)] transition-all duration-200"
                  >
                    Add Your First Address
                  </motion.button>
                </motion.div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  <AnimatePresence mode="popLayout">
                    {addresses.map((address) => (
                      <AddressCard
                        key={address.id}
                        address={address}
                        onEdit={handleEditAddress}
                        onDelete={handleAddressDelete}
                        onSetDefault={handleSetDefaultAddress}
                      />
                    ))}
                  </AnimatePresence>
                </div>
              )}
            </div>
          )}
        </div>
      </main>

      <Footer />
    </div>
  );
};

export default AddressesPage;

