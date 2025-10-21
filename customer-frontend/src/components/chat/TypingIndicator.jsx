/**
 * TypingIndicator Component
 * Shows animated dots when Lisa is typing
 */

import React from 'react';
import { motion } from 'framer-motion';

const TypingIndicator = () => {
  return (
    <div className="flex items-center gap-2 px-4 py-3 bg-gradient-to-r from-primary-500 to-secondary-500 rounded-2xl rounded-bl-none max-w-[200px]">
      <span className="text-white text-sm">Lisa is typing</span>
      <div className="flex gap-1">
        {[0, 1, 2].map((index) => (
          <motion.div
            key={index}
            className="w-2 h-2 bg-white rounded-full"
            animate={{
              y: [0, -8, 0],
              opacity: [0.5, 1, 0.5],
            }}
            transition={{
              duration: 0.6,
              repeat: Infinity,
              delay: index * 0.2,
              ease: "easeInOut",
            }}
          />
        ))}
      </div>
    </div>
  );
};

export default TypingIndicator;

