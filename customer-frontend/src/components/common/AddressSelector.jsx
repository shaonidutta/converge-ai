/**
 * AddressSelector Component
 * Dropdown for selecting delivery address
 */

import { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { MapPin, ChevronDown, Plus, Check } from 'lucide-react';
import { Button } from '../ui/button';

/**
 * AddressSelector Component
 * @param {Object} props
 * @param {Array} props.addresses - List of addresses
 * @param {Object} props.selectedAddress - Currently selected address
 * @param {Function} props.onSelectAddress - Callback when address is selected
 * @param {Function} props.onAddAddress - Callback to open add address modal
 * @param {boolean} props.loading - Loading state
 */
const AddressSelector = ({
  addresses = [],
  selectedAddress = null,
  onSelectAddress,
  onAddAddress,
  loading = false,
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef(null);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleSelectAddress = (address) => {
    onSelectAddress(address);
    setIsOpen(false);
  };

  const formatAddress = (address) => {
    if (!address) return 'Select Address';
    
    const parts = [
      address.address_line1,
      address.city,
      address.pincode,
    ].filter(Boolean);
    
    return parts.join(', ');
  };

  const getShortAddress = (address) => {
    if (!address) return 'Select Address';
    return `${address.city}, ${address.pincode}`;
  };

  return (
    <div className="relative" ref={dropdownRef}>
      {/* Trigger Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        disabled={loading}
        className="flex items-center gap-2 px-4 py-2 bg-white/80 backdrop-blur-sm rounded-xl border border-slate-200 hover:border-primary-300 hover:bg-white transition-all duration-300 shadow-[0_2px_8px_rgba(0,0,0,0.04)] hover:shadow-[0_4px_12px_rgba(108,99,255,0.15)] group"
      >
        {/* Location Icon with Gradient */}
        <div className="flex items-center justify-center w-8 h-8 rounded-lg bg-gradient-to-br from-primary-500 to-secondary-500 shadow-[0_2px_8px_rgba(108,99,255,0.3)]">
          <MapPin className="h-4 w-4 text-white" />
        </div>

        {/* Address Text */}
        <div className="flex flex-col items-start">
          <span className="text-xs text-slate-500 font-medium">Deliver to</span>
          <span className="text-sm font-semibold text-slate-900 max-w-[200px] truncate">
            {loading ? 'Loading...' : getShortAddress(selectedAddress)}
          </span>
        </div>

        {/* Chevron Icon */}
        <ChevronDown
          className={`h-4 w-4 text-slate-400 transition-transform duration-300 ${
            isOpen ? 'rotate-180' : ''
          }`}
        />
      </button>

      {/* Dropdown Menu */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: -10, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -10, scale: 0.95 }}
            transition={{ duration: 0.2, ease: 'easeOut' }}
            className="absolute top-full left-0 mt-2 w-96 bg-white rounded-xl shadow-[0_8px_32px_rgba(0,0,0,0.12)] border border-slate-200 overflow-hidden z-50"
          >
            {/* Header */}
            <div className="px-4 py-3 bg-gradient-to-r from-primary-50 to-secondary-50 border-b border-slate-200">
              <h3 className="text-sm font-semibold text-slate-900">
                Select Delivery Address
              </h3>
            </div>

            {/* Address List */}
            <div className="max-h-80 overflow-y-auto">
              {addresses.length === 0 ? (
                <div className="px-4 py-8 text-center">
                  <MapPin className="h-12 w-12 text-slate-300 mx-auto mb-3" />
                  <p className="text-sm text-slate-500 mb-4">
                    No addresses saved yet
                  </p>
                  <Button
                    onClick={() => {
                      setIsOpen(false);
                      onAddAddress?.();
                    }}
                    size="sm"
                    className="bg-gradient-to-r from-primary-500 to-secondary-500 hover:from-primary-600 hover:to-secondary-600 text-white"
                  >
                    <Plus className="h-4 w-4 mr-2" />
                    Add Address
                  </Button>
                </div>
              ) : (
                <div className="py-2">
                  {addresses.map((address) => (
                    <button
                      key={address.id}
                      onClick={() => handleSelectAddress(address)}
                      className="w-full px-4 py-3 text-left hover:bg-slate-50 transition-colors duration-200 flex items-start gap-3 group"
                    >
                      {/* Radio/Check Icon */}
                      <div
                        className={`flex-shrink-0 w-5 h-5 rounded-full border-2 flex items-center justify-center transition-all duration-200 ${
                          selectedAddress?.id === address.id
                            ? 'border-primary-500 bg-primary-500'
                            : 'border-slate-300 group-hover:border-primary-300'
                        }`}
                      >
                        {selectedAddress?.id === address.id && (
                          <Check className="h-3 w-3 text-white" />
                        )}
                      </div>

                      {/* Address Details */}
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-1">
                          <span className="text-sm font-semibold text-slate-900">
                            {address.label || 'Address'}
                          </span>
                          {address.is_default && (
                            <span className="px-2 py-0.5 text-xs font-medium bg-primary-100 text-primary-700 rounded-full">
                              Default
                            </span>
                          )}
                        </div>
                        <p className="text-sm text-slate-600 line-clamp-2">
                          {formatAddress(address)}
                        </p>
                      </div>
                    </button>
                  ))}
                </div>
              )}
            </div>

            {/* Footer - Add New Address */}
            {addresses.length > 0 && (
              <div className="px-4 py-3 bg-slate-50 border-t border-slate-200">
                <Button
                  onClick={() => {
                    setIsOpen(false);
                    onAddAddress?.();
                  }}
                  variant="outline"
                  size="sm"
                  className="w-full justify-center hover:bg-primary-50 hover:border-primary-300 hover:text-primary-700 transition-all duration-300"
                >
                  <Plus className="h-4 w-4 mr-2" />
                  Add New Address
                </Button>
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default AddressSelector;

