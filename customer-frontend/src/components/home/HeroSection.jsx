/**
 * HeroSection Component
 * Hero section with welcome message and search
 */

import { useState } from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { Search, Sparkles, Zap, Shield, Clock } from 'lucide-react';
import { Button } from '../ui/button';

/**
 * HeroSection Component
 * @param {Object} props
 * @param {Object} props.user - User data
 */
const HeroSection = ({ user }) => {
  const navigate = useNavigate();
  const [searchQuery, setSearchQuery] = useState('');

  const handleSearch = (e) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      navigate(`/search?q=${encodeURIComponent(searchQuery)}`);
    }
  };

  const quickActions = [
    { icon: Sparkles, label: 'AI Assistant', action: () => {}, gradient: 'from-primary-500 to-secondary-500' },
    { icon: Zap, label: 'Quick Book', action: () => navigate('/services'), gradient: 'from-accent-500 to-primary-500' },
    { icon: Shield, label: 'My Bookings', action: () => navigate('/bookings'), gradient: 'from-secondary-500 to-primary-500' },
  ];

  return (
    <section className="relative min-h-[400px] flex items-center overflow-hidden bg-gradient-to-br from-slate-50 via-white to-primary-50/20 pt-24 pb-12">
      {/* Animated Background Orbs */}
      <motion.div
        animate={{
          scale: [1, 1.2, 1],
          opacity: [0.3, 0.5, 0.3],
        }}
        transition={{
          duration: 8,
          repeat: Infinity,
          ease: 'easeInOut',
        }}
        className="absolute top-0 right-0 w-96 h-96 bg-gradient-to-br from-primary-300/30 to-primary-400/30 rounded-full blur-3xl"
      />
      <motion.div
        animate={{
          scale: [1, 1.3, 1],
          opacity: [0.2, 0.4, 0.2],
        }}
        transition={{
          duration: 10,
          repeat: Infinity,
          ease: 'easeInOut',
          delay: 1,
        }}
        className="absolute bottom-0 left-0 w-96 h-96 bg-gradient-to-tr from-secondary-300/30 to-secondary-400/30 rounded-full blur-3xl"
      />

      {/* Content */}
      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 w-full">
        <div className="max-w-3xl">
          {/* Welcome Message */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <h1 className="text-4xl md:text-5xl font-black text-slate-900 mb-4">
              Welcome back,{' '}
              <span className="bg-gradient-to-r from-primary-600 to-secondary-600 bg-clip-text text-transparent">
                {user?.first_name}
              </span>
              ! 👋
            </h1>
            <p className="text-lg text-slate-600 mb-8">
              What service can we help you with today?
            </p>
          </motion.div>

          {/* Search Bar */}
          <motion.form
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.1 }}
            onSubmit={handleSearch}
            className="relative mb-8"
          >
            <div className="relative">
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search for plumbing, cleaning, electrical..."
                className="w-full px-6 py-4 pl-14 pr-32 bg-white border-2 border-slate-200 rounded-2xl focus:outline-none focus:ring-2 focus:ring-primary-400 focus:border-transparent transition-all duration-300 text-base shadow-[0_4px_20px_rgba(0,0,0,0.08)] hover:shadow-[0_6px_24px_rgba(108,99,255,0.12)]"
              />
              <Search className="absolute left-5 top-1/2 -translate-y-1/2 h-5 w-5 text-slate-400" />
              <Button
                type="submit"
                className="absolute right-2 top-1/2 -translate-y-1/2 bg-gradient-to-r from-primary-500 to-secondary-500 hover:from-primary-600 hover:to-secondary-600 text-white px-6 py-2 rounded-xl shadow-[0_4px_12px_rgba(108,99,255,0.3)] hover:shadow-[0_6px_16px_rgba(108,99,255,0.4)] transition-all duration-300"
              >
                Search
              </Button>
            </div>
          </motion.form>

          {/* Quick Actions */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
            className="flex flex-wrap items-center gap-3"
          >
            <span className="text-sm font-medium text-slate-600">Quick Actions:</span>
            {quickActions.map((action, index) => (
              <motion.button
                key={action.label}
                onClick={action.action}
                whileHover={{ scale: 1.05, y: -2 }}
                whileTap={{ scale: 0.95 }}
                className={`flex items-center gap-2 px-4 py-2 bg-gradient-to-r ${action.gradient} text-white rounded-xl shadow-[0_4px_12px_rgba(108,99,255,0.2)] hover:shadow-[0_6px_16px_rgba(108,99,255,0.3)] transition-all duration-300`}
              >
                <action.icon className="h-4 w-4" />
                <span className="text-sm font-semibold">{action.label}</span>
              </motion.button>
            ))}
          </motion.div>

          {/* Features Pills */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.3 }}
            className="mt-8 flex flex-wrap items-center gap-4"
          >
            <div className="flex items-center gap-2 px-4 py-2 bg-white rounded-full shadow-[0_2px_8px_rgba(0,0,0,0.04)]">
              <Clock className="h-4 w-4 text-primary-600" />
              <span className="text-sm font-medium text-slate-700">24/7 Available</span>
            </div>
            <div className="flex items-center gap-2 px-4 py-2 bg-white rounded-full shadow-[0_2px_8px_rgba(0,0,0,0.04)]">
              <Shield className="h-4 w-4 text-secondary-600" />
              <span className="text-sm font-medium text-slate-700">Verified Professionals</span>
            </div>
            <div className="flex items-center gap-2 px-4 py-2 bg-white rounded-full shadow-[0_2px_8px_rgba(0,0,0,0.04)]">
              <Zap className="h-4 w-4 text-accent-600" />
              <span className="text-sm font-medium text-slate-700">Instant Booking</span>
            </div>
          </motion.div>
        </div>
      </div>
    </section>
  );
};

export default HeroSection;

