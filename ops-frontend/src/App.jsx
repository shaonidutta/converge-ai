import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';
import MainLayout from './components/layout/MainLayout';
import LoginPage from './pages/LoginPage';
import Dashboard from './pages/Dashboard';
import ComplaintsPage from './pages/ComplaintsPage';
import AnalyticsPage from './pages/AnalyticsPage';
import ReportsPage from './pages/ReportsPage';
import PriorityQueuePage from './pages/PriorityQueuePage';
import StaffPage from './pages/StaffPage';
import SettingsPage from './pages/SettingsPage';
import AlertsPage from './pages/AlertsPage';

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

              {/* Analytics & Reporting */}
              <Route path="analytics" element={<AnalyticsPage />} />
              <Route path="reports" element={<ReportsPage />} />

              {/* Priority Queue */}
              <Route path="priority-queue" element={<PriorityQueuePage />} />

              {/* Staff Management */}
              <Route path="staff" element={<StaffPage />} />

              {/* Settings & Configuration */}
              <Route path="settings" element={<SettingsPage />} />

              {/* Alerts & Notifications */}
              <Route path="alerts" element={<AlertsPage />} />
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
