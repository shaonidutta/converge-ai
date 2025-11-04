/**
 * Operations Authentication Context
 * Global state management for staff authentication
 * Features:
 * - Staff authentication state management
 * - Token validation and refresh
 * - Role-based permissions
 * - Cross-tab synchronization
 * - Automatic logout on token expiry
 * - PII access logging
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
  getCurrentStaff,
  getStaffPermissions,
  hasPermission,
  clearAuth,
} from "../api/axiosConfig";
import api from "../services/api";

// Create Auth Context
export const AuthContext = createContext(null);

/**
 * Auth Provider Component
 * Wraps the app to provide staff authentication state and methods
 */
export const AuthProvider = ({ children }) => {
  const [staff, setStaff] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [permissions, setPermissions] = useState([]);
  const [role, setRole] = useState(null);

  /**
   * Get stored staff data from localStorage
   */
  const getStoredStaff = useCallback(() => {
    try {
      const staffData = localStorage.getItem("ops_staff");
      return staffData ? JSON.parse(staffData) : null;
    } catch (error) {
      console.error("Error parsing stored staff data:", error);
      return null;
    }
  }, []);

  /**
   * Store staff data in localStorage
   */
  const storeStaffData = useCallback((staffData, tokens, staffPermissions) => {
    try {
      // Store tokens
      localStorage.setItem("ops_access_token", tokens.access_token);
      localStorage.setItem("ops_refresh_token", tokens.refresh_token);
      
      // Store staff data
      localStorage.setItem("ops_staff", JSON.stringify(staffData));
      localStorage.setItem("ops_staff_id", staffData.id.toString());
      localStorage.setItem("ops_staff_role", staffData.role);
      localStorage.setItem("ops_permissions", JSON.stringify(staffPermissions));
    } catch (error) {
      console.error("Error storing staff data:", error);
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
        setStaff(null);
        setPermissions([]);
        setRole(null);
        setLoading(false);
        return;
      }

      // Get stored staff data
      const storedStaff = getStoredStaff();
      const storedPermissions = getStaffPermissions();
      
      if (storedStaff) {
        setStaff(storedStaff);
        setPermissions(storedPermissions);
        setRole(storedStaff.role);
        setIsLoggedIn(true);
      }

      // Validate token by making a test API call
      try {
        const response = await api.auth.getMe();
        const staffData = response.data;
        
        setStaff(staffData);
        setPermissions(staffData.permissions || []);
        setRole(staffData.role);
        setIsLoggedIn(true);
        
        // Update stored data
        localStorage.setItem("ops_staff", JSON.stringify(staffData));
        localStorage.setItem("ops_staff_id", staffData.id.toString());
        localStorage.setItem("ops_staff_role", staffData.role);
        localStorage.setItem("ops_permissions", JSON.stringify(staffData.permissions || []));
        
      } catch (error) {
        console.error("Token validation failed:", error);
        // Token is invalid, clear auth data
        handleLogout();
      }
    } catch (error) {
      console.error("Auth initialization error:", error);
      handleLogout();
    } finally {
      setLoading(false);
    }
  }, [getStoredStaff]);

  /**
   * Login function
   */
  const login = useCallback(async (credentials) => {
    try {
      setLoading(true);
      
      const response = await api.auth.login(credentials);
      const { staff: staffData, tokens, permissions: staffPermissions } = response.data;

      // Store authentication data
      storeStaffData(staffData, tokens, staffPermissions);

      // Update state
      setStaff(staffData);
      setPermissions(staffPermissions);
      setRole(staffData.role);
      setIsLoggedIn(true);

      return { success: true, staff: staffData };
    } catch (error) {
      console.error("Login error:", error);
      return { 
        success: false, 
        error: error.response?.data?.detail || "Login failed" 
      };
    } finally {
      setLoading(false);
    }
  }, [storeStaffData]);

  /**
   * Logout function
   */
  const logout = useCallback(async () => {
    try {
      // Call logout API
      await api.auth.logout();
    } catch (error) {
      console.error("Logout API error:", error);
    } finally {
      handleLogout();
    }
  }, []);

  /**
   * Handle logout (clear state and storage)
   */
  const handleLogout = useCallback(() => {
    // Clear authentication data
    clearAuth();
    
    // Reset state
    setStaff(null);
    setPermissions([]);
    setRole(null);
    setIsLoggedIn(false);
    setLoading(false);
  }, []);

  /**
   * Check if staff has specific permission
   */
  const checkPermission = useCallback((permission) => {
    return hasPermission(permission);
  }, []);

  /**
   * Check if staff has any of the specified permissions
   */
  const hasAnyPermission = useCallback((permissionList) => {
    return permissionList.some(permission => hasPermission(permission));
  }, []);

  /**
   * Check if staff has all of the specified permissions
   */
  const hasAllPermissions = useCallback((permissionList) => {
    return permissionList.every(permission => hasPermission(permission));
  }, []);

  /**
   * Listen for storage changes (cross-tab synchronization)
   */
  useEffect(() => {
    const handleStorageChange = (e) => {
      if (e.key === "ops_access_token") {
        if (!e.newValue) {
          // Token was removed, logout
          handleLogout();
        } else {
          // Token was added/changed, reinitialize
          initializeAuth();
        }
      }
    };

    window.addEventListener("storage", handleStorageChange);
    return () => window.removeEventListener("storage", handleStorageChange);
  }, [initializeAuth, handleLogout]);

  /**
   * Listen for auth failure events
   */
  useEffect(() => {
    const handleAuthFailure = () => {
      handleLogout();
    };

    window.addEventListener("ops-auth-failure", handleAuthFailure);
    return () => window.removeEventListener("ops-auth-failure", handleAuthFailure);
  }, [handleLogout]);

  /**
   * Initialize auth on mount
   */
  useEffect(() => {
    initializeAuth();
  }, [initializeAuth]);

  // Context value
  const value = {
    // State
    staff,
    loading,
    isLoggedIn,
    permissions,
    role,
    
    // Methods
    login,
    logout,
    checkPermission,
    hasAnyPermission,
    hasAllPermissions,
    
    // Utilities
    isAuthenticated: isAuthenticated(),
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

/**
 * Custom hook to use auth context
 */
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};

export default AuthContext;
