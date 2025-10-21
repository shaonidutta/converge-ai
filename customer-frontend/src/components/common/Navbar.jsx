/**
 * Navbar Component
 * Main navigation bar with address selector, search, cart, and user menu
 */

import { useState, useEffect, useRef } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Search,
  ShoppingCart,
  User,
  LogOut,
  Calendar,
  MapPin,
  Settings,
  ChevronDown,
  Star,
} from 'lucide-react';
import Logo from '../Logo';
import AddressSelector from './AddressSelector';
import NotificationBell from '../notifications/NotificationBell';
import { Button } from '../ui/button';
import { getStoredUser, clearAuth } from '../../api/axiosConfig';
import { useAddresses } from '../../hooks/useAddresses';
import { useCart } from '../../hooks/useCart';

/**
 * Navbar Component
 * @param {Object} props
 * @param {Function} props.onAddAddress - Callback to open add address modal
 */
const Navbar = ({ onAddAddress }) => {
  const navigate = useNavigate();
  const location = useLocation();
  const [user, setUser] = useState(null);
  const [isScrolled, setIsScrolled] = useState(false);
  const [isUserMenuOpen, setIsUserMenuOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const userMenuRef = useRef(null);

  // Fetch addresses
  const { addresses, selectedAddress, selectAddress, loading: addressesLoading } = useAddresses();

  // Get cart data
  const { totalItems } = useCart();

  // Get user data
  useEffect(() => {
    const storedUser = getStoredUser();
    setUser(storedUser);
  }, []);

  // Handle scroll effect
  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 10);
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  // Close user menu when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (userMenuRef.current && !userMenuRef.current.contains(event.target)) {
        setIsUserMenuOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleLogout = () => {
    clearAuth();
    navigate('/login');
  };

  const handleSearch = (e) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      navigate(`/search?q=${encodeURIComponent(searchQuery)}`);
    }
  };

  return (
    <motion.header
      initial={{ y: -100 }}
      animate={{ y: 0 }}
      transition={{ duration: 0.3, ease: 'easeOut' }}
      className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
        isScrolled
          ? 'bg-white/95 backdrop-blur-lg shadow-[0_4px_20px_rgba(0,0,0,0.08)]'
          : 'bg-white/80 backdrop-blur-sm'
      }`}
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16 gap-4">
          {/* Left Section: Logo + Address Selector */}
          <div className="flex items-center gap-4">
            {/* Logo */}
            <button
              onClick={() => navigate('/home')}
              className="flex-shrink-0 hover:opacity-80 transition-opacity duration-200"
            >
              <Logo size="sm" showText={true} />
            </button>

            {/* Address Selector - Hidden on mobile */}
            <div className="hidden md:block">
              <AddressSelector
                addresses={addresses}
                selectedAddress={selectedAddress}
                onSelectAddress={selectAddress}
                onAddAddress={onAddAddress}
                loading={addressesLoading}
              />
            </div>
          </div>

          {/* Center Section: Search Bar - Hidden on mobile */}
          <div className="hidden lg:block flex-1 max-w-xl">
            <form onSubmit={handleSearch} className="relative">
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search for services..."
                className="w-full px-4 py-2 pl-10 pr-4 bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-400 focus:border-transparent transition-all duration-300 text-sm"
              />
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
            </form>
          </div>

          {/* Right Section: Cart + User Menu */}
          <div className="flex items-center gap-3">
            {/* Cart Button */}
            <button
              onClick={() => navigate('/cart')}
              className="relative p-2 hover:bg-slate-100 rounded-lg transition-colors duration-200"
            >
              <ShoppingCart className="h-5 w-5 text-slate-700" />
              {totalItems > 0 && (
                <motion.span
                  key={totalItems}
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  className="absolute -top-1 -right-1 w-5 h-5 bg-gradient-to-r from-primary-500 to-secondary-500 text-white text-xs font-bold rounded-full flex items-center justify-center shadow-[0_2px_8px_rgba(108,99,255,0.4)]"
                >
                  {totalItems > 9 ? '9+' : totalItems}
                </motion.span>
              )}
            </button>

            {/* Notification Bell */}
            <NotificationBell />

            {/* User Menu */}
            <div className="relative" ref={userMenuRef}>
              <button
                onClick={() => setIsUserMenuOpen(!isUserMenuOpen)}
                className="flex items-center gap-2 px-3 py-2 hover:bg-slate-100 rounded-lg transition-colors duration-200"
              >
                <div className="w-8 h-8 rounded-full bg-gradient-to-br from-primary-500 to-secondary-500 flex items-center justify-center text-white font-semibold text-sm shadow-[0_2px_8px_rgba(108,99,255,0.3)]">
                  {user?.first_name?.[0]?.toUpperCase() || 'U'}
                </div>
                <ChevronDown
                  className={`h-4 w-4 text-slate-400 transition-transform duration-300 hidden sm:block ${
                    isUserMenuOpen ? 'rotate-180' : ''
                  }`}
                />
              </button>

              {/* User Dropdown Menu */}
              <AnimatePresence>
                {isUserMenuOpen && (
                  <motion.div
                    initial={{ opacity: 0, y: -10, scale: 0.95 }}
                    animate={{ opacity: 1, y: 0, scale: 1 }}
                    exit={{ opacity: 0, y: -10, scale: 0.95 }}
                    transition={{ duration: 0.2, ease: 'easeOut' }}
                    className="absolute right-0 top-full mt-2 w-64 bg-white rounded-xl shadow-[0_8px_32px_rgba(0,0,0,0.12)] border border-slate-200 overflow-hidden"
                  >
                    {/* User Info */}
                    <div className="px-4 py-3 bg-gradient-to-r from-primary-50 to-secondary-50 border-b border-slate-200">
                      <p className="text-sm font-semibold text-slate-900">
                        {user?.first_name} {user?.last_name}
                      </p>
                      <p className="text-xs text-slate-600">{user?.email}</p>
                    </div>

                    {/* Menu Items */}
                    <div className="py-2">
                      <button
                        onClick={() => {
                          setIsUserMenuOpen(false);
                          navigate('/profile');
                        }}
                        className="w-full px-4 py-2 text-left text-sm text-slate-700 hover:bg-slate-50 transition-colors duration-200 flex items-center gap-3"
                      >
                        <User className="h-4 w-4 text-slate-400" />
                        My Profile
                      </button>

                      <button
                        onClick={() => {
                          setIsUserMenuOpen(false);
                          navigate('/bookings');
                        }}
                        className="w-full px-4 py-2 text-left text-sm text-slate-700 hover:bg-slate-50 transition-colors duration-200 flex items-center gap-3"
                      >
                        <Calendar className="h-4 w-4 text-slate-400" />
                        My Bookings
                      </button>

                      <button
                        onClick={() => {
                          setIsUserMenuOpen(false);
                          navigate('/reviews');
                        }}
                        className="w-full px-4 py-2 text-left text-sm text-slate-700 hover:bg-slate-50 transition-colors duration-200 flex items-center gap-3"
                      >
                        <Star className="h-4 w-4 text-slate-400" />
                        My Reviews
                      </button>

                      <button
                        onClick={() => {
                          setIsUserMenuOpen(false);
                          navigate('/addresses');
                        }}
                        className="w-full px-4 py-2 text-left text-sm text-slate-700 hover:bg-slate-50 transition-colors duration-200 flex items-center gap-3"
                      >
                        <MapPin className="h-4 w-4 text-slate-400" />
                        My Addresses
                      </button>

                      <button
                        onClick={() => {
                          setIsUserMenuOpen(false);
                          navigate('/settings');
                        }}
                        className="w-full px-4 py-2 text-left text-sm text-slate-700 hover:bg-slate-50 transition-colors duration-200 flex items-center gap-3"
                      >
                        <Settings className="h-4 w-4 text-slate-400" />
                        Settings
                      </button>
                    </div>

                    {/* Logout */}
                    <div className="border-t border-slate-200 py-2">
                      <button
                        onClick={handleLogout}
                        className="w-full px-4 py-2 text-left text-sm text-red-600 hover:bg-red-50 transition-colors duration-200 flex items-center gap-3"
                      >
                        <LogOut className="h-4 w-4" />
                        Logout
                      </button>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          </div>
        </div>
      </div>
    </motion.header>
  );
};

export default Navbar;

