/**
 * ProtectedRoute Component
 * Wrapper component that protects routes requiring authentication
 * Features:
 * - Authentication check
 * - Loading state handling
 * - Automatic redirect to login
 * - Preserves intended destination
 */

import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Loader2 } from 'lucide-react';

/**
 * ProtectedRoute Component
 * @param {Object} props - Component props
 * @param {React.ReactNode} props.children - Child components to render if authenticated
 * @param {string} props.redirectTo - Path to redirect to if not authenticated (default: '/login')
 */
const ProtectedRoute = ({ children, redirectTo = '/login' }) => {
  const { isAuthenticated, loading } = useAuth();
  const location = useLocation();

  // Show loading spinner while checking authentication
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-50 via-white to-primary-50/20">
        <div className="flex flex-col items-center space-y-4">
          <Loader2 className="h-8 w-8 animate-spin text-primary-500" />
          <p className="text-slate-600 font-medium">Loading...</p>
        </div>
      </div>
    );
  }

  // Redirect to login if not authenticated
  if (!isAuthenticated) {
    return (
      <Navigate 
        to={redirectTo} 
        state={{ from: location }} 
        replace 
      />
    );
  }

  // Render protected content
  return children;
};

export default ProtectedRoute;
