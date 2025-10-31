/**
 * LisaChatWindow Component
 * Main chat interface for Lisa AI chatbot
 * Features:
 * - Header with Lisa avatar and close button
 * - Message list with auto-scroll
 * - Typing indicator
 * - Quick actions (when no messages)
 * - Message input
 * - Slide in/out animation
 * - Responsive design
 */

import React from "react";
import { motion, AnimatePresence } from "framer-motion";
import { X, Trash2, Bot } from "lucide-react";
import { useChat } from "../../hooks/useChat";
import MessageList from "./MessageList";
import MessageInput from "./MessageInput";
import TypingIndicator from "./TypingIndicator";
import QuickActions from "./QuickActions";

const LisaChatWindow = () => {
  const {
    isOpen,
    messages,
    isTyping,
    closeChat,
    sendMessage,
    clearChat,
    sendQuickAction,
  } = useChat();

  const handleClearChat = () => {
    if (window.confirm("Are you sure you want to clear this chat?")) {
      clearChat();
    }
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop for mobile */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={closeChat}
            className="fixed inset-0 bg-black/20 backdrop-blur-sm z-40 md:hidden"
          />

          {/* Chat Window */}
          <motion.div
            initial={{ opacity: 0, y: 20, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 20, scale: 0.95 }}
            transition={{ duration: 0.2 }}
            className="fixed bottom-0 right-0 md:bottom-4 md:right-4 w-full md:w-[400px] h-[100vh] md:h-[600px] bg-white md:rounded-2xl shadow-[0_8px_32px_rgba(0,0,0,0.15)] flex flex-col z-50 overflow-hidden"
          >
            {/* Header */}
            <div className="flex items-center justify-between p-4 bg-gradient-to-r from-primary-500 to-secondary-500 text-white">
              <div className="flex items-center gap-3">
                {/* Lisa Avatar */}
                <div className="w-10 h-10 bg-white rounded-full flex items-center justify-center">
                  <Bot className="h-6 w-6 text-primary-500" />
                </div>
                <div>
                  <h3 className="font-semibold">Lisa</h3>
                  <p className="text-xs text-white/80">AI Assistant</p>
                </div>
              </div>

              {/* Actions */}
              <div className="flex items-center gap-2">
                {messages.length > 0 && (
                  <button
                    onClick={handleClearChat}
                    className="p-2 hover:bg-white/20 rounded-lg transition-colors duration-200"
                    title="Clear chat"
                  >
                    <Trash2 className="h-4 w-4" />
                  </button>
                )}
                <button
                  onClick={closeChat}
                  className="p-2 hover:bg-white/20 rounded-lg transition-colors duration-200"
                  title="Close chat"
                >
                  <X className="h-5 w-5" />
                </button>
              </div>
            </div>

            {/* Messages Area */}
            {messages.length === 0 ? (
              <div className="flex-1 flex flex-col items-center justify-center p-4 bg-slate-50 overflow-y-auto">
                <div className="flex flex-col items-center justify-center">
                  <div className="w-20 h-20 bg-gradient-to-r from-primary-500 to-secondary-500 rounded-full flex items-center justify-center mb-4">
                    <Bot className="h-12 w-12 text-white" />
                  </div>
                  <h3 className="text-xl font-bold text-slate-800 mb-2">
                    Welcome to Lisa!
                  </h3>
                  <p className="text-sm text-slate-600 text-center mb-6 max-w-xs">
                    Your AI-powered assistant for booking services and getting
                    help
                  </p>
                  <QuickActions onActionClick={sendQuickAction} />
                </div>
              </div>
            ) : (
              <>
                <MessageList messages={messages} isTyping={isTyping} />

                {/* Typing Indicator */}
                {isTyping && (
                  <div className="px-4 pb-4 bg-slate-50">
                    <TypingIndicator />
                  </div>
                )}
              </>
            )}

            {/* Input Area */}
            <MessageInput
              onSend={sendMessage}
              disabled={isTyping}
              placeholder="Type your message..."
            />
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
};

export default LisaChatWindow;
