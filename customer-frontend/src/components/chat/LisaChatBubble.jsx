/**
 * LisaChatBubble Component
 * Floating AI assistant chat bubble
 */

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Sparkles, X, MessageCircle } from 'lucide-react';

/**
 * LisaChatBubble Component
 * @param {Object} props
 * @param {Function} props.onClick - Callback when bubble is clicked
 * @param {number} props.unreadCount - Number of unread messages
 */
const LisaChatBubble = ({ onClick, unreadCount = 0 }) => {
  const [isHovered, setIsHovered] = useState(false);

  return (
    <div className="fixed bottom-6 right-6 z-50">
      {/* Tooltip */}
      <AnimatePresence>
        {isHovered && (
          <motion.div
            initial={{ opacity: 0, x: 10, scale: 0.9 }}
            animate={{ opacity: 1, x: 0, scale: 1 }}
            exit={{ opacity: 0, x: 10, scale: 0.9 }}
            transition={{ duration: 0.2 }}
            className="absolute bottom-full right-0 mb-4 px-4 py-2 bg-slate-900 text-white text-sm font-medium rounded-lg shadow-lg whitespace-nowrap"
          >
            Chat with Lisa
            <div className="absolute top-full right-6 w-0 h-0 border-l-8 border-r-8 border-t-8 border-transparent border-t-slate-900" />
          </motion.div>
        )}
      </AnimatePresence>

      {/* Chat Bubble */}
      <motion.button
        onClick={onClick}
        onMouseEnter={() => setIsHovered(true)}
        onMouseLeave={() => setIsHovered(false)}
        whileHover={{ scale: 1.1, rotate: 5 }}
        whileTap={{ scale: 0.95 }}
        className="relative w-16 h-16 rounded-full bg-gradient-to-br from-primary-500 to-secondary-500 shadow-[0_8px_32px_rgba(108,99,255,0.4)] hover:shadow-[0_12px_40px_rgba(108,99,255,0.5)] flex items-center justify-center transition-all duration-300 group"
      >
        {/* Pulse Animation */}
        <motion.div
          animate={{
            scale: [1, 1.3, 1],
            opacity: [0.5, 0, 0.5],
          }}
          transition={{
            duration: 2,
            repeat: Infinity,
            ease: 'easeInOut',
          }}
          className="absolute inset-0 rounded-full bg-gradient-to-br from-primary-500 to-secondary-500"
        />

        {/* Icon */}
        <motion.div
          animate={{
            rotate: [0, 10, -10, 0],
          }}
          transition={{
            duration: 3,
            repeat: Infinity,
            ease: 'easeInOut',
          }}
          className="relative z-10"
        >
          <Sparkles className="h-7 w-7 text-white" />
        </motion.div>

        {/* Unread Badge */}
        {unreadCount > 0 && (
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            className="absolute -top-1 -right-1 w-6 h-6 bg-red-500 text-white text-xs font-bold rounded-full flex items-center justify-center shadow-[0_2px_8px_rgba(239,68,68,0.4)]"
          >
            {unreadCount > 9 ? '9+' : unreadCount}
          </motion.div>
        )}

        {/* Glow Effect */}
        <div className="absolute inset-0 rounded-full bg-gradient-to-br from-primary-400 to-secondary-400 opacity-0 group-hover:opacity-50 blur-xl transition-opacity duration-300" />
      </motion.button>

      {/* Floating Particles */}
      <motion.div
        animate={{
          y: [-10, -20, -10],
          opacity: [0.3, 0.6, 0.3],
        }}
        transition={{
          duration: 3,
          repeat: Infinity,
          ease: 'easeInOut',
        }}
        className="absolute top-0 right-0 w-2 h-2 rounded-full bg-primary-400 blur-sm"
      />
      <motion.div
        animate={{
          y: [-15, -25, -15],
          opacity: [0.3, 0.6, 0.3],
        }}
        transition={{
          duration: 3,
          repeat: Infinity,
          ease: 'easeInOut',
          delay: 0.5,
        }}
        className="absolute top-2 right-8 w-1.5 h-1.5 rounded-full bg-secondary-400 blur-sm"
      />
      <motion.div
        animate={{
          y: [-12, -22, -12],
          opacity: [0.3, 0.6, 0.3],
        }}
        transition={{
          duration: 3,
          repeat: Infinity,
          ease: 'easeInOut',
          delay: 1,
        }}
        className="absolute top-4 right-4 w-1 h-1 rounded-full bg-accent-400 blur-sm"
      />
    </div>
  );
};

/**
 * LisaChatWindow Component (Placeholder for Phase 8)
 * Full chat window that opens when bubble is clicked
 */
export const LisaChatWindow = ({ isOpen, onClose }) => {
  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          initial={{ opacity: 0, y: 20, scale: 0.95 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          exit={{ opacity: 0, y: 20, scale: 0.95 }}
          transition={{ duration: 0.3, ease: 'easeOut' }}
          className="fixed bottom-24 right-6 w-96 h-[600px] bg-white rounded-2xl shadow-[0_12px_48px_rgba(0,0,0,0.15)] border border-slate-200 overflow-hidden z-50"
        >
          {/* Header */}
          <div className="bg-gradient-to-r from-primary-500 to-secondary-500 px-6 py-4 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-white/20 backdrop-blur-sm flex items-center justify-center">
                <Sparkles className="h-5 w-5 text-white" />
              </div>
              <div>
                <h3 className="text-white font-bold">Lisa</h3>
                <p className="text-xs text-white/80">AI Assistant</p>
              </div>
            </div>
            <button
              onClick={onClose}
              className="w-8 h-8 rounded-lg bg-white/20 hover:bg-white/30 flex items-center justify-center transition-colors duration-200"
            >
              <X className="h-5 w-5 text-white" />
            </button>
          </div>

          {/* Chat Content - Placeholder */}
          <div className="flex items-center justify-center h-[calc(100%-80px)] bg-slate-50">
            <div className="text-center px-6">
              <div className="w-16 h-16 rounded-full bg-gradient-to-br from-primary-100 to-secondary-100 flex items-center justify-center mx-auto mb-4">
                <MessageCircle className="h-8 w-8 text-primary-600" />
              </div>
              <h4 className="text-lg font-bold text-slate-900 mb-2">
                Chat Coming Soon!
              </h4>
              <p className="text-sm text-slate-600">
                The full chat interface will be available in Phase 8.
                Stay tuned!
              </p>
            </div>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
};

export default LisaChatBubble;

