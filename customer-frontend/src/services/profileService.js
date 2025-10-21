/**
 * Profile Service
 * Handles all profile-related API calls
 */

import api from './api';

/**
 * Fetch user profile
 * @returns {Promise<Object>} User profile data
 */
export const fetchProfile = async () => {
  try {
    const response = await api.customers.getProfile();
    return response.data;
  } catch (error) {
    console.error('Error fetching profile:', error);
    throw new Error(error.response?.data?.detail || 'Failed to fetch profile');
  }
};

/**
 * Update user profile
 * @param {Object} profileData - Profile data to update (first_name, last_name, phone)
 * @returns {Promise<Object>} Updated profile
 */
export const updateProfile = async (profileData) => {
  try {
    const response = await api.customers.updateProfile(profileData);
    return response.data;
  } catch (error) {
    console.error('Error updating profile:', error);
    throw new Error(error.response?.data?.detail || 'Failed to update profile');
  }
};

/**
 * Change password
 * @param {Object} passwordData - Password data (current_password, new_password)
 * @returns {Promise<Object>} Success message
 */
export const changePassword = async (passwordData) => {
  try {
    const response = await api.auth.changePassword(passwordData);
    return response.data;
  } catch (error) {
    console.error('Error changing password:', error);
    throw new Error(error.response?.data?.detail || 'Failed to change password');
  }
};

/**
 * Upload profile avatar
 * @param {File} file - Image file
 * @returns {Promise<Object>} Updated profile with avatar URL
 */
export const uploadAvatar = async (file) => {
  try {
    const formData = new FormData();
    formData.append('avatar', file);
    
    const response = await api.customers.uploadAvatar(formData);
    return response.data;
  } catch (error) {
    console.error('Error uploading avatar:', error);
    throw new Error(error.response?.data?.detail || 'Failed to upload avatar');
  }
};

/**
 * Get profile statistics
 * @returns {Promise<Object>} Profile statistics (total_bookings, completed_bookings, etc.)
 */
export const fetchProfileStats = async () => {
  try {
    const response = await api.customers.getStats();
    return response.data;
  } catch (error) {
    console.error('Error fetching profile stats:', error);
    throw new Error(error.response?.data?.detail || 'Failed to fetch profile statistics');
  }
};

/**
 * Delete account
 * @param {string} password - User password for confirmation
 * @returns {Promise<Object>} Success message
 */
export const deleteAccount = async (password) => {
  try {
    const response = await api.customers.deleteAccount({ password });
    return response.data;
  } catch (error) {
    console.error('Error deleting account:', error);
    throw new Error(error.response?.data?.detail || 'Failed to delete account');
  }
};

/**
 * Export all profile service functions
 */
export default {
  fetchProfile,
  updateProfile,
  changePassword,
  uploadAvatar,
  fetchProfileStats,
  deleteAccount,
};

