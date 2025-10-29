/**
 * Authentication Context
 * Global state management for user authentication
 * Features:
 * - Authentication state management
 * - Token validation and refresh
 * - Cross-tab synchronization
 * - Automatic logout on token expiry
 */

import React, {
  createContext,
  useState,
  useEffect,
  useCallback,
  useContext,
} from "react";
import {
  isAuthenticated,
  getAccessToken,
  getRefreshToken,
  storeAuthData,
  clearAuth,
} from "../api/axiosConfig";
import api from "../services/api";

// Create Auth Context
export const AuthContext = createContext(null);

/**
 * Auth Provider Component
 * Wraps the app to provide authentication state and methods
 */
export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  /**
   * Get stored user data from localStorage
   */
  const getStoredUser = useCallback(() => {
    try {
      const userData = localStorage.getItem("user");
      return userData ? JSON.parse(userData) : null;
    } catch (error) {
      console.error("Error parsing stored user data:", error);
      return null;
    }
  }, []);

  /**
   * Initialize authentication state
   */
  const initializeAuth = useCallback(async () => {
    try {
      setLoading(true);

      // Check if tokens exist
      const accessToken = getAccessToken();
      const refreshToken = getRefreshToken();

      if (!accessToken || !refreshToken) {
        setIsLoggedIn(false);
        setUser(null);
        setLoading(false);
        return;
      }

      // Get stored user data
      const storedUser = getStoredUser();
      if (storedUser) {
        setUser(storedUser);
        setIsLoggedIn(true);
      }

      // Validate token by making a test API call
      try {
        const response = await api.user.getProfile();
        setUser(response.data);
        setIsLoggedIn(true);

        // Update stored user data
        localStorage.setItem("user", JSON.stringify(response.data));
      } catch (error) {
        // Token might be expired, try to refresh
        console.warn("Token validation failed, clearing auth state");
        handleLogout();
      }
    } catch (error) {
      console.error("Error initializing auth:", error);
      handleLogout();
    } finally {
      setLoading(false);
    }
  }, [getStoredUser]);

  /**
   * Handle login
   */
  const handleLogin = useCallback(async (credentials) => {
    try {
      setLoading(true);
      const response = await api.auth.login(credentials);

      // Extract data from axios response
      const responseData = response.data;

      // Store auth data
      storeAuthData(responseData);

      // Update state
      setUser(responseData.user);
      setIsLoggedIn(true);

      return responseData;
    } catch (error) {
      console.error("Login error:", error);
      throw error;
    } finally {
      setLoading(false);
    }
  }, []);

  /**
   * Handle logout
   */
  const handleLogout = useCallback(async () => {
    try {
      // Call logout API if possible
      if (isAuthenticated()) {
        try {
          await api.auth.logout();
        } catch (error) {
          console.warn("Logout API call failed:", error);
        }
      }
    } catch (error) {
      console.error("Logout error:", error);
    } finally {
      // Clear auth state regardless of API call result
      clearAuth();
      setUser(null);
      setIsLoggedIn(false);
    }
  }, []);

  /**
   * Handle registration
   */
  const handleRegister = useCallback(async (userData) => {
    try {
      setLoading(true);
      const response = await api.auth.register(userData);

      // Extract data from axios response
      const responseData = response.data;

      // Store auth data
      storeAuthData(responseData);

      // Update state
      setUser(responseData.user);
      setIsLoggedIn(true);

      return responseData;
    } catch (error) {
      console.error("Registration error:", error);
      throw error;
    } finally {
      setLoading(false);
    }
  }, []);

  /**
   * Update user profile
   */
  const updateUser = useCallback((updatedUser) => {
    setUser(updatedUser);
    localStorage.setItem("user", JSON.stringify(updatedUser));
  }, []);

  // Initialize auth state on mount
  useEffect(() => {
    initializeAuth();
  }, [initializeAuth]);

  // Listen for storage changes (cross-tab synchronization)
  useEffect(() => {
    const handleStorageChange = (e) => {
      if (e.key === "access_token" || e.key === "user") {
        // Re-initialize auth state when tokens or user data changes
        initializeAuth();
      }
    };

    window.addEventListener("storage", handleStorageChange);
    return () => window.removeEventListener("storage", handleStorageChange);
  }, [initializeAuth]);

  // Listen for focus events to check auth state
  useEffect(() => {
    const handleFocus = () => {
      // Check auth state when tab becomes active
      if (!isAuthenticated() && isLoggedIn) {
        handleLogout();
      }
    };

    window.addEventListener("focus", handleFocus);
    return () => window.removeEventListener("focus", handleFocus);
  }, [isLoggedIn, handleLogout]);

  const value = {
    // State
    user,
    loading,
    isLoggedIn,
    isAuthenticated: isLoggedIn,

    // Methods
    login: handleLogin,
    logout: handleLogout,
    register: handleRegister,
    updateUser,
    initializeAuth,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

/**
 * Hook to use auth context
 */
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};

export default AuthContext;
