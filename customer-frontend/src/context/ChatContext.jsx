/**
 * Chat Context
 * Global state management for Lisa AI chatbot
 * Features:
 * - Session management
 * - Message history
 * - Send/receive messages
 * - Typing indicator
 * - LocalStorage persistence
 */

import React, { createContext, useState, useEffect, useCallback } from 'react';
import { sendMessage as sendMessageAPI, getChatHistory } from '../services/chatService';

// Create Chat Context
export const ChatContext = createContext(null);

/**
 * Chat Provider Component
 * Wraps the app to provide chat state and methods
 */
export const ChatProvider = ({ children }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [isTyping, setIsTyping] = useState(false);
  const [error, setError] = useState(null);
  const [unreadCount, setUnreadCount] = useState(0);

  // Load session from localStorage on mount
  useEffect(() => {
    try {
      const savedSessionId = localStorage.getItem('chat_session_id');
      const savedMessages = localStorage.getItem('chat_messages');
      
      if (savedSessionId) {
        setSessionId(savedSessionId);
      }
      
      if (savedMessages) {
        setMessages(JSON.parse(savedMessages));
      }
    } catch (error) {
      console.error('Error loading chat from localStorage:', error);
    }
  }, []);

  // Save session to localStorage whenever it changes
  useEffect(() => {
    try {
      if (sessionId) {
        localStorage.setItem('chat_session_id', sessionId);
      }
      if (messages.length > 0) {
        localStorage.setItem('chat_messages', JSON.stringify(messages));
      }
    } catch (error) {
      console.error('Error saving chat to localStorage:', error);
    }
  }, [sessionId, messages]);

  /**
   * Open chat window
   */
  const openChat = useCallback(() => {
    setIsOpen(true);
    setUnreadCount(0);
  }, []);

  /**
   * Close chat window
   */
  const closeChat = useCallback(() => {
    setIsOpen(false);
  }, []);

  /**
   * Send a message to Lisa
   * @param {string} text - Message text
   */
  const sendMessage = useCallback(async (text) => {
    if (!text.trim()) return;

    // Add user message immediately
    const userMessage = {
      id: Date.now(),
      role: 'user',
      message: text,
      created_at: new Date().toISOString(),
    };

    setMessages(prev => [...prev, userMessage]);
    setIsTyping(true);
    setError(null);

    try {
      // Send to backend
      const response = await sendMessageAPI(text, sessionId);
      
      // Update session ID if new
      if (response.session_id && response.session_id !== sessionId) {
        setSessionId(response.session_id);
      }

      // Add assistant message
      const assistantMessage = {
        id: response.assistant_message.id,
        role: 'assistant',
        message: response.assistant_message.message,
        created_at: response.assistant_message.created_at,
      };

      setMessages(prev => [...prev, assistantMessage]);
      
      // Increment unread count if chat is closed
      if (!isOpen) {
        setUnreadCount(prev => prev + 1);
      }
    } catch (err) {
      setError(err.message);
      console.error('Error sending message:', err);
      
      // Add error message
      const errorMessage = {
        id: Date.now() + 1,
        role: 'assistant',
        message: 'Sorry, I encountered an error. Please try again.',
        created_at: new Date().toISOString(),
        isError: true,
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsTyping(false);
    }
  }, [sessionId, isOpen]);

  /**
   * Load chat history from backend
   */
  const loadHistory = useCallback(async () => {
    if (!sessionId) return;

    try {
      const response = await getChatHistory(sessionId);
      setMessages(response.messages || []);
    } catch (err) {
      console.error('Error loading chat history:', err);
    }
  }, [sessionId]);

  /**
   * Clear chat and start new session
   */
  const clearChat = useCallback(() => {
    setMessages([]);
    setSessionId(null);
    setError(null);
    setUnreadCount(0);
    localStorage.removeItem('chat_session_id');
    localStorage.removeItem('chat_messages');
  }, []);

  /**
   * Add a quick action message
   * @param {string} text - Quick action text
   */
  const sendQuickAction = useCallback((text) => {
    sendMessage(text);
  }, [sendMessage]);

  const value = {
    // State
    isOpen,
    sessionId,
    messages,
    isTyping,
    error,
    unreadCount,
    
    // Methods
    openChat,
    closeChat,
    sendMessage,
    loadHistory,
    clearChat,
    sendQuickAction,
  };

  return (
    <ChatContext.Provider value={value}>
      {children}
    </ChatContext.Provider>
  );
};

export default ChatContext;

