import { Navigate, useLocation } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { Loader2 } from "lucide-react";

/**
 * ProtectedRoute Component
 * Handles route protection based on authentication and permissions
 * Features:
 * - Authentication check
 * - Role-based access control
 * - Permission-based access control
 * - Loading states
 * - Redirect to login if unauthorized
 */
const ProtectedRoute = ({ 
  children, 
  requiredRole = null, 
  requiredPermissions = [], 
  requireAll = false 
}) => {
  const { isLoggedIn, loading, role, hasAnyPermission, hasAllPermissions } = useAuth();
  const location = useLocation();

  // Show loading spinner while checking authentication
  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="w-8 h-8 animate-spin text-primary mx-auto mb-4" />
          <p className="text-gray-600">Verifying access...</p>
        </div>
      </div>
    );
  }

  // Redirect to login if not authenticated
  if (!isLoggedIn) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  // Check role-based access
  if (requiredRole && role !== requiredRole && role !== 'admin') {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center max-w-md mx-auto p-8">
          <div className="bg-red-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
            <svg className="w-8 h-8 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
            </svg>
          </div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Access Denied</h2>
          <p className="text-gray-600 mb-4">
            You do not have the required role ({requiredRole}) to access this page.
          </p>
          <p className="text-sm text-gray-500">
            Contact your administrator if you believe this is an error.
          </p>
        </div>
      </div>
    );
  }

  // Check permission-based access
  if (requiredPermissions.length > 0) {
    const hasAccess = requireAll 
      ? hasAllPermissions(requiredPermissions)
      : hasAnyPermission(requiredPermissions);

    if (!hasAccess && role !== 'admin') {
      return (
        <div className="min-h-screen bg-gray-50 flex items-center justify-center">
          <div className="text-center max-w-md mx-auto p-8">
            <div className="bg-amber-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
              <svg className="w-8 h-8 text-amber-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
              </svg>
            </div>
            <h2 className="text-2xl font-bold text-gray-900 mb-2">Insufficient Permissions</h2>
            <p className="text-gray-600 mb-4">
              You do not have the required permissions to access this page.
            </p>
            <div className="bg-gray-50 rounded-md p-3 mb-4">
              <p className="text-sm text-gray-700 font-medium mb-1">Required permissions:</p>
              <ul className="text-sm text-gray-600 space-y-1">
                {requiredPermissions.map((permission, index) => (
                  <li key={index} className="flex items-center">
                    <span className="w-1.5 h-1.5 bg-gray-400 rounded-full mr-2"></span>
                    {permission}
                  </li>
                ))}
              </ul>
              {requireAll && (
                <p className="text-xs text-gray-500 mt-2">
                  All permissions are required
                </p>
              )}
            </div>
            <p className="text-sm text-gray-500">
              Contact your administrator to request access.
            </p>
          </div>
        </div>
      );
    }
  }

  // User has access, render the protected component
  return children;
};

/**
 * Higher-order component for protecting routes
 * @param {Object} options - Protection options
 * @returns {Function} Protected component wrapper
 */
export const withProtection = (options = {}) => {
  return (Component) => {
    return (props) => (
      <ProtectedRoute {...options}>
        <Component {...props} />
      </ProtectedRoute>
    );
  };
};

/**
 * Permission-based component wrapper
 * Conditionally renders children based on permissions
 */
export const PermissionGate = ({ 
  children, 
  requiredPermissions = [], 
  requiredRole = null,
  requireAll = false,
  fallback = null 
}) => {
  const { role, hasAnyPermission, hasAllPermissions } = useAuth();

  // Check role
  if (requiredRole && role !== requiredRole && role !== 'admin') {
    return fallback;
  }

  // Check permissions
  if (requiredPermissions.length > 0) {
    const hasAccess = requireAll 
      ? hasAllPermissions(requiredPermissions)
      : hasAnyPermission(requiredPermissions);

    if (!hasAccess && role !== 'admin') {
      return fallback;
    }
  }

  return children;
};

export default ProtectedRoute;
