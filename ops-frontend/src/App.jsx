import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';
import MainLayout from './components/layout/MainLayout';
import LoginPage from './pages/LoginPage';
import Dashboard from './pages/Dashboard';
import ComplaintsPage from './pages/ComplaintsPage';

/**
 * Main App Component
 * Root component with routing and context providers
 * Features:
 * - React Router for navigation
 * - Authentication context provider
 * - Protected routes
 * - Layout management
 */
function App() {
  return (
    <Router>
      <AuthProvider>
        <div className="App w-full min-h-screen">
          <Routes>
            {/* Public Routes */}
            <Route path="/login" element={<LoginPage />} />

            {/* Protected Routes */}
            <Route
              path="/"
              element={
                <ProtectedRoute>
                  <MainLayout />
                </ProtectedRoute>
              }
            >
              {/* Dashboard Routes */}
              <Route index element={<Navigate to="/dashboard" replace />} />
              <Route path="dashboard" element={<Dashboard />} />

              {/* Complaints Management */}
              <Route path="complaints" element={<ComplaintsPage />} />

              {/* Placeholder routes for future implementation */}
              <Route path="priority-queue" element={<div className="p-8 text-center text-gray-500">Priority Queue - Coming Soon</div>} />
              <Route path="alerts" element={<div className="p-8 text-center text-gray-500">Alerts - Coming Soon</div>} />
              <Route path="analytics" element={<div className="p-8 text-center text-gray-500">Analytics - Coming Soon</div>} />
              <Route path="staff" element={<div className="p-8 text-center text-gray-500">Staff Management - Coming Soon</div>} />
              <Route path="settings" element={<div className="p-8 text-center text-gray-500">Settings - Coming Soon</div>} />
            </Route>

            {/* Catch all route */}
            <Route path="*" element={<Navigate to="/dashboard" replace />} />
          </Routes>
        </div>
      </AuthProvider>
    </Router>
  );
}

export default App;
