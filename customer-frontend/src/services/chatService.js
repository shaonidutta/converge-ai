/**
 * Chat Service
 * Handles all chat-related API calls for Lisa AI chatbot
 */

import api from './api';

/**
 * Send a message to Lisa
 * @param {string} message - User message text
 * @param {string} sessionId - Optional session ID to continue conversation
 * @returns {Promise<object>} Response with user message, assistant message, and session ID
 */
export const sendMessage = async (message, sessionId = null) => {
  try {
    const payload = {
      message,
      channel: 'web',
    };
    
    if (sessionId) {
      payload.session_id = sessionId;
    }
    
    const response = await api.chat.sendMessage(payload);
    return response.data;
  } catch (error) {
    console.error('Error sending message:', error);
    throw new Error(error.response?.data?.detail || 'Failed to send message');
  }
};

/**
 * Get chat history for a session
 * @param {string} sessionId - Session ID
 * @param {object} params - Query parameters (limit, skip)
 * @returns {Promise<object>} Response with messages array and total count
 */
export const getChatHistory = async (sessionId, params = {}) => {
  try {
    const response = await api.chat.getHistory(sessionId, params);
    return response.data;
  } catch (error) {
    console.error('Error fetching chat history:', error);
    throw new Error(error.response?.data?.detail || 'Failed to fetch chat history');
  }
};

/**
 * Get all chat sessions for current user
 * @param {object} params - Query parameters (limit, skip)
 * @returns {Promise<Array>} Array of session objects
 */
export const getChatSessions = async (params = {}) => {
  try {
    const response = await api.chat.getSessions(params);
    return response.data;
  } catch (error) {
    console.error('Error fetching chat sessions:', error);
    throw new Error(error.response?.data?.detail || 'Failed to fetch chat sessions');
  }
};

/**
 * End a chat session
 * @param {string} sessionId - Session ID to end
 * @returns {Promise<object>} Success response
 */
export const endChatSession = async (sessionId) => {
  try {
    const response = await api.chat.endSession(sessionId);
    return response.data;
  } catch (error) {
    console.error('Error ending chat session:', error);
    throw new Error(error.response?.data?.detail || 'Failed to end chat session');
  }
};

export default {
  sendMessage,
  getChatHistory,
  getChatSessions,
  endChatSession,
};

