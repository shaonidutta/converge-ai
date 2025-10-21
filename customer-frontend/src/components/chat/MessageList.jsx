/**
 * MessageList Component
 * Displays all chat messages with auto-scroll
 * Features:
 * - User vs Lisa message styling
 * - Timestamp display
 * - Auto-scroll to bottom
 * - Smooth animations
 */

import React, { useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Bot, User } from 'lucide-react';

const MessageList = ({ messages, isTyping }) => {
  const messagesEndRef = useRef(null);
  const containerRef = useRef(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages, isTyping]);

  const formatTime = (timestamp) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString('en-US', { 
      hour: '2-digit', 
      minute: '2-digit',
      hour12: true 
    });
  };

  return (
    <div 
      ref={containerRef}
      className="flex-1 overflow-y-auto p-4 space-y-4 bg-slate-50"
      style={{ scrollBehavior: 'smooth' }}
    >
      <AnimatePresence>
        {messages.map((message, index) => (
          <motion.div
            key={message.id || index}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            transition={{ duration: 0.2 }}
            className={`flex gap-3 ${message.role === 'user' ? 'flex-row-reverse' : 'flex-row'}`}
          >
            {/* Avatar */}
            <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
              message.role === 'user' 
                ? 'bg-slate-200' 
                : 'bg-gradient-to-r from-primary-500 to-secondary-500'
            }`}>
              {message.role === 'user' ? (
                <User className="h-4 w-4 text-slate-600" />
              ) : (
                <Bot className="h-4 w-4 text-white" />
              )}
            </div>

            {/* Message Bubble */}
            <div className={`flex flex-col max-w-[75%] ${message.role === 'user' ? 'items-end' : 'items-start'}`}>
              <div className={`px-4 py-3 rounded-2xl ${
                message.role === 'user'
                  ? 'bg-white border border-slate-200 rounded-br-none'
                  : message.isError
                  ? 'bg-red-50 border border-red-200 rounded-bl-none'
                  : 'bg-gradient-to-r from-primary-500 to-secondary-500 text-white rounded-bl-none'
              }`}>
                <p className={`text-sm whitespace-pre-wrap break-words ${
                  message.role === 'user' 
                    ? 'text-slate-800' 
                    : message.isError
                    ? 'text-red-800'
                    : 'text-white'
                }`}>
                  {message.message}
                </p>
              </div>
              
              {/* Timestamp */}
              <span className="text-xs text-slate-400 mt-1 px-1">
                {formatTime(message.created_at)}
              </span>
            </div>
          </motion.div>
        ))}
      </AnimatePresence>

      {/* Scroll anchor */}
      <div ref={messagesEndRef} />
    </div>
  );
};

export default MessageList;

