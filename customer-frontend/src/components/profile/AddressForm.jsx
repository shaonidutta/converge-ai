/**
 * AddressForm Component
 * Form for adding or editing addresses
 */

import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Save, X } from 'lucide-react';

const AddressForm = ({ address, onSave, onCancel, loading }) => {
  const [formData, setFormData] = useState({
    address_type: 'Home',
    street_address: '',
    apartment_number: '',
    city: '',
    state: '',
    postal_code: '',
    is_default: false,
  });

  const [errors, setErrors] = useState({});

  useEffect(() => {
    if (address) {
      setFormData({
        address_type: address.address_type || 'Home',
        street_address: address.street_address || '',
        apartment_number: address.apartment_number || '',
        city: address.city || '',
        state: address.state || '',
        postal_code: address.postal_code || '',
        is_default: address.is_default || false,
      });
    }
  }, [address]);

  const validateForm = () => {
    const newErrors = {};

    if (!formData.street_address.trim()) {
      newErrors.street_address = 'Street address is required';
    }

    if (!formData.city.trim()) {
      newErrors.city = 'City is required';
    }

    if (!formData.state.trim()) {
      newErrors.state = 'State is required';
    }

    if (!formData.postal_code.trim()) {
      newErrors.postal_code = 'Postal code is required';
    } else if (!/^\d{6}$/.test(formData.postal_code)) {
      newErrors.postal_code = 'Invalid postal code (6 digits required)';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value,
    }));
    // Clear error for this field
    if (errors[name]) {
      setErrors((prev) => ({ ...prev, [name]: '' }));
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (validateForm()) {
      onSave(formData);
    }
  };

  return (
    <motion.form
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      onSubmit={handleSubmit}
      className="bg-white rounded-xl border border-slate-200 p-6"
    >
      <h2 className="text-xl font-bold text-slate-900 mb-6">
        {address ? 'Edit Address' : 'Add New Address'}
      </h2>

      <div className="space-y-4">
        {/* Address Type */}
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-2">
            Address Type *
          </label>
          <select
            name="address_type"
            value={formData.address_type}
            onChange={handleChange}
            className="w-full px-4 py-3 border border-slate-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200"
          >
            <option value="Home">Home</option>
            <option value="Work">Work</option>
            <option value="Other">Other</option>
          </select>
        </div>

        {/* Street Address */}
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-2">
            Street Address *
          </label>
          <input
            type="text"
            name="street_address"
            value={formData.street_address}
            onChange={handleChange}
            className={`w-full px-4 py-3 border rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200 ${
              errors.street_address ? 'border-red-500' : 'border-slate-300'
            }`}
            placeholder="Enter street address"
          />
          {errors.street_address && (
            <p className="text-sm text-red-600 mt-1">{errors.street_address}</p>
          )}
        </div>

        {/* Apartment/Suite Number */}
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-2">
            Apartment/Suite Number
          </label>
          <input
            type="text"
            name="apartment_number"
            value={formData.apartment_number}
            onChange={handleChange}
            className="w-full px-4 py-3 border border-slate-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200"
            placeholder="Apt, Suite, Unit, etc. (optional)"
          />
        </div>

        {/* City */}
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-2">
            City *
          </label>
          <input
            type="text"
            name="city"
            value={formData.city}
            onChange={handleChange}
            className={`w-full px-4 py-3 border rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200 ${
              errors.city ? 'border-red-500' : 'border-slate-300'
            }`}
            placeholder="Enter city"
          />
          {errors.city && (
            <p className="text-sm text-red-600 mt-1">{errors.city}</p>
          )}
        </div>

        {/* State and Postal Code */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">
              State *
            </label>
            <input
              type="text"
              name="state"
              value={formData.state}
              onChange={handleChange}
              className={`w-full px-4 py-3 border rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200 ${
                errors.state ? 'border-red-500' : 'border-slate-300'
              }`}
              placeholder="State"
            />
            {errors.state && (
              <p className="text-sm text-red-600 mt-1">{errors.state}</p>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">
              Postal Code *
            </label>
            <input
              type="text"
              name="postal_code"
              value={formData.postal_code}
              onChange={handleChange}
              maxLength={6}
              className={`w-full px-4 py-3 border rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200 ${
                errors.postal_code ? 'border-red-500' : 'border-slate-300'
              }`}
              placeholder="000000"
            />
            {errors.postal_code && (
              <p className="text-sm text-red-600 mt-1">{errors.postal_code}</p>
            )}
          </div>
        </div>

        {/* Set as Default */}
        <div className="flex items-center gap-2">
          <input
            type="checkbox"
            id="is_default"
            name="is_default"
            checked={formData.is_default}
            onChange={handleChange}
            className="w-4 h-4 text-primary-500 border-slate-300 rounded focus:ring-primary-500"
          />
          <label htmlFor="is_default" className="text-sm text-slate-700">
            Set as default address
          </label>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex items-center gap-3 mt-6">
        <motion.button
          type="submit"
          disabled={loading}
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          className="flex-1 flex items-center justify-center gap-2 px-4 py-3 bg-gradient-to-r from-primary-500 to-secondary-500 text-white font-semibold rounded-xl hover:shadow-[0_4px_12px_rgba(108,99,255,0.3)] disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200"
        >
          <Save className="h-5 w-5" />
          {loading ? 'Saving...' : 'Save Address'}
        </motion.button>

        <motion.button
          type="button"
          onClick={onCancel}
          disabled={loading}
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          className="px-4 py-3 bg-white border-2 border-slate-300 text-slate-700 font-semibold rounded-xl hover:bg-slate-50 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200"
        >
          <X className="h-5 w-5" />
        </motion.button>
      </div>
    </motion.form>
  );
};

export default AddressForm;

