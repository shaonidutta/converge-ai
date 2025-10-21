/**
 * AddressCard Component
 * Displays address information with edit/delete actions
 */

import React from 'react';
import { motion } from 'framer-motion';
import { Home, Briefcase, MapPin, Edit, Trash2, Star } from 'lucide-react';

const AddressCard = ({ address, onEdit, onDelete, onSetDefault }) => {
  const getAddressIcon = (type) => {
    switch (type?.toLowerCase()) {
      case 'home':
        return Home;
      case 'work':
        return Briefcase;
      default:
        return MapPin;
    }
  };

  const Icon = getAddressIcon(address.address_type);

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ scale: 1.01 }}
      className="bg-white rounded-xl border border-slate-200 p-6 hover:shadow-[0_4px_12px_rgba(108,99,255,0.1)] transition-all duration-200"
    >
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-primary-100 rounded-lg flex items-center justify-center">
            <Icon className="h-5 w-5 text-primary-500" />
          </div>
          <div>
            <h3 className="font-semibold text-slate-900">{address.address_type}</h3>
            {address.is_default && (
              <span className="inline-flex items-center gap-1 text-xs text-amber-600 bg-amber-50 px-2 py-0.5 rounded-full mt-1">
                <Star className="h-3 w-3 fill-current" />
                Default
              </span>
            )}
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex items-center gap-2">
          <motion.button
            onClick={() => onEdit(address)}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className="p-2 text-blue-500 hover:bg-blue-50 rounded-lg transition-colors duration-200"
            title="Edit"
          >
            <Edit className="h-4 w-4" />
          </motion.button>

          <motion.button
            onClick={() => onDelete(address.id)}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className="p-2 text-red-500 hover:bg-red-50 rounded-lg transition-colors duration-200"
            title="Delete"
          >
            <Trash2 className="h-4 w-4" />
          </motion.button>
        </div>
      </div>

      {/* Address Details */}
      <div className="text-sm text-slate-600 space-y-1">
        <p>{address.street_address}</p>
        {address.apartment_number && <p>{address.apartment_number}</p>}
        <p>
          {address.city}, {address.state} {address.postal_code}
        </p>
      </div>

      {/* Set as Default Button */}
      {!address.is_default && (
        <motion.button
          onClick={() => onSetDefault(address.id)}
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          className="mt-4 w-full px-4 py-2 text-sm font-medium text-primary-500 border border-primary-300 rounded-lg hover:bg-primary-50 transition-all duration-200"
        >
          Set as Default
        </motion.button>
      )}
    </motion.div>
  );
};

export default AddressCard;

