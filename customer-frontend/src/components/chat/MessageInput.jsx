/**
 * MessageInput Component
 * Text input for sending messages to Lisa
 * Features:
 * - Auto-resize textarea
 * - Enter to send (Shift+Enter for new line)
 * - Character limit
 * - Disabled when typing
 */

import React, { useState, useRef, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Send } from 'lucide-react';

const MessageInput = ({ onSend, disabled = false, placeholder = "Type your message..." }) => {
  const [message, setMessage] = useState('');
  const textareaRef = useRef(null);
  const maxLength = 1000;

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 120)}px`;
    }
  }, [message]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (message.trim() && !disabled) {
      onSend(message.trim());
      setMessage('');
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="border-t border-slate-200 p-4 bg-white">
      <div className="flex items-end gap-2">
        <div className="flex-1 relative">
          <textarea
            ref={textareaRef}
            value={message}
            onChange={(e) => setMessage(e.target.value.slice(0, maxLength))}
            onKeyDown={handleKeyDown}
            placeholder={placeholder}
            disabled={disabled}
            rows={1}
            className="w-full px-4 py-3 pr-12 border border-slate-300 rounded-xl resize-none focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent disabled:bg-slate-100 disabled:cursor-not-allowed transition-all duration-200"
            style={{ minHeight: '48px', maxHeight: '120px' }}
          />
          {message.length > 0 && (
            <span className="absolute bottom-2 right-3 text-xs text-slate-400">
              {message.length}/{maxLength}
            </span>
          )}
        </div>
        <motion.button
          type="submit"
          disabled={!message.trim() || disabled}
          whileHover={!disabled && message.trim() ? { scale: 1.05 } : {}}
          whileTap={!disabled && message.trim() ? { scale: 0.95 } : {}}
          className="flex-shrink-0 p-3 bg-gradient-to-r from-primary-500 to-secondary-500 text-white rounded-xl disabled:opacity-50 disabled:cursor-not-allowed hover:shadow-[0_4px_12px_rgba(108,99,255,0.3)] transition-all duration-200"
        >
          <Send className="h-5 w-5" />
        </motion.button>
      </div>
      <p className="text-xs text-slate-500 mt-2">
        Press Enter to send, Shift+Enter for new line
      </p>
    </form>
  );
};

export default MessageInput;

