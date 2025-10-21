/**
 * AddressSelector Component
 * Select or add delivery address
 */

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { MapPin, Plus, Home, Briefcase, MapPinned } from 'lucide-react';
import { useAddresses } from '../../hooks/useAddresses';
import LoadingSkeleton from '../common/LoadingSkeleton';

const AddressSelector = ({ selectedAddressId, onAddressSelect, error }) => {
  const { addresses, loading, error: fetchError } = useAddresses();
  const [showAddForm, setShowAddForm] = useState(false);

  const getAddressIcon = (type) => {
    switch (type?.toLowerCase()) {
      case 'home':
        return <Home className="h-5 w-5" />;
      case 'work':
        return <Briefcase className="h-5 w-5" />;
      default:
        return <MapPinned className="h-5 w-5" />;
    }
  };

  if (loading) {
    return (
      <div className="space-y-3">
        <LoadingSkeleton className="h-24" />
        <LoadingSkeleton className="h-24" />
      </div>
    );
  }

  if (fetchError) {
    return (
      <div className="p-4 bg-red-50 border border-red-200 rounded-xl text-red-700">
        Failed to load addresses. Please try again.
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between mb-4">
        <label className="flex items-center gap-2 text-sm font-medium text-slate-700">
          <MapPin className="h-4 w-4" />
          Select Delivery Address
        </label>
        <button
          type="button"
          onClick={() => setShowAddForm(!showAddForm)}
          className="flex items-center gap-1 text-sm text-primary-500 hover:text-primary-600 font-medium transition-colors duration-200"
        >
          <Plus className="h-4 w-4" />
          Add New
        </button>
      </div>

      {/* Address List */}
      {addresses.length === 0 ? (
        <div className="p-8 text-center bg-slate-50 rounded-xl border-2 border-dashed border-slate-300">
          <MapPin className="h-12 w-12 text-slate-400 mx-auto mb-3" />
          <p className="text-slate-600 mb-4">No saved addresses</p>
          <button
            type="button"
            onClick={() => setShowAddForm(true)}
            className="px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition-colors duration-200"
          >
            Add Your First Address
          </button>
        </div>
      ) : (
        <div className="space-y-3">
          {addresses.map((address) => (
            <motion.div
              key={address.id}
              whileHover={{ scale: 1.01 }}
              onClick={() => onAddressSelect(address.id)}
              className={`p-4 border-2 rounded-xl cursor-pointer transition-all duration-200 ${
                selectedAddressId === address.id
                  ? 'border-primary-500 bg-primary-50 shadow-[0_4px_12px_rgba(108,99,255,0.2)]'
                  : 'border-slate-200 bg-white hover:border-primary-300'
              }`}
            >
              <div className="flex items-start gap-3">
                {/* Radio Button */}
                <div className="flex-shrink-0 mt-1">
                  <div className={`w-5 h-5 rounded-full border-2 flex items-center justify-center transition-all duration-200 ${
                    selectedAddressId === address.id
                      ? 'border-primary-500 bg-primary-500'
                      : 'border-slate-300'
                  }`}>
                    {selectedAddressId === address.id && (
                      <div className="w-2 h-2 bg-white rounded-full" />
                    )}
                  </div>
                </div>

                {/* Address Details */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <div className={`${
                      selectedAddressId === address.id ? 'text-primary-600' : 'text-slate-600'
                    }`}>
                      {getAddressIcon(address.address_type)}
                    </div>
                    <span className="font-semibold text-slate-900 capitalize">
                      {address.address_type || 'Other'}
                    </span>
                    {address.is_default && (
                      <span className="px-2 py-0.5 bg-accent-100 text-accent-700 text-xs font-medium rounded">
                        Default
                      </span>
                    )}
                  </div>
                  <p className="text-sm text-slate-700">
                    {address.street_address}
                  </p>
                  <p className="text-sm text-slate-600">
                    {address.city}, {address.state} {address.pincode}
                  </p>
                  {address.landmark && (
                    <p className="text-xs text-slate-500 mt-1">
                      Landmark: {address.landmark}
                    </p>
                  )}
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      )}

      {error && (
        <p className="text-sm text-red-500 mt-2">{error}</p>
      )}

      {/* Add Address Form (Placeholder) */}
      <AnimatePresence>
        {showAddForm && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="mt-4 p-4 bg-slate-50 rounded-xl border border-slate-200"
          >
            <p className="text-sm text-slate-600 text-center">
              Add address functionality will be implemented in Profile section
            </p>
            <button
              type="button"
              onClick={() => setShowAddForm(false)}
              className="mt-3 w-full px-4 py-2 bg-white border border-slate-300 text-slate-700 rounded-lg hover:bg-slate-50 transition-colors duration-200"
            >
              Close
            </button>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default AddressSelector;

