/**
 * LisaChatBubble Component
 * Floating AI assistant chat bubble
 * Integrated with ChatContext
 */

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Sparkles } from 'lucide-react';
import { useChat } from '../../hooks/useChat';

/**
 * LisaChatBubble Component
 * Opens chat window when clicked
 */
const LisaChatBubble = () => {
  const [isHovered, setIsHovered] = useState(false);
  const { openChat, unreadCount } = useChat();

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
        onClick={openChat}
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

export default LisaChatBubble;

