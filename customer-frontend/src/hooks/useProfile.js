/**
 * useProfile Hook
 * Custom hook for fetching and managing user profile
 */

import { useState, useEffect, useCallback } from 'react';
import { fetchProfile, updateProfile, fetchProfileStats } from '../services/profileService';

/**
 * Hook to fetch and manage user profile
 * @returns {Object} { profile, loading, error, refetch, updateProfileData }
 */
export const useProfile = () => {
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const loadProfile = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await fetchProfile();
      setProfile(data);
    } catch (err) {
      setError(err.message);
      console.error('Error loading profile:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadProfile();
  }, [loadProfile]);

  const refetch = useCallback(() => {
    loadProfile();
  }, [loadProfile]);

  const updateProfileData = useCallback(async (profileData) => {
    try {
      setLoading(true);
      setError(null);
      const updatedProfile = await updateProfile(profileData);
      setProfile(updatedProfile);
      return updatedProfile;
    } catch (err) {
      setError(err.message);
      console.error('Error updating profile:', err);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  return { profile, loading, error, refetch, updateProfileData };
};

/**
 * Hook to fetch profile statistics
 * @returns {Object} { stats, loading, error, refetch }
 */
export const useProfileStats = () => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const loadStats = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await fetchProfileStats();
      setStats(data);
    } catch (err) {
      setError(err.message);
      console.error('Error loading profile stats:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadStats();
  }, [loadStats]);

  const refetch = useCallback(() => {
    loadStats();
  }, [loadStats]);

  return { stats, loading, error, refetch };
};

/**
 * Export all hooks
 */
export default {
  useProfile,
  useProfileStats,
};

