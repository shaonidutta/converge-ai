/**
 * useChat Hook
 * Custom hook to access Chat Context
 * Provides easy access to chat state and methods
 */

import { useContext } from 'react';
import { ChatContext } from '../context/ChatContext';

/**
 * Hook to access chat context
 * @returns {object} Chat state and methods
 * @throws {Error} If used outside ChatProvider
 */
export const useChat = () => {
  const context = useContext(ChatContext);
  
  if (!context) {
    throw new Error('useChat must be used within a ChatProvider');
  }
  
  return context;
};

export default useChat;

