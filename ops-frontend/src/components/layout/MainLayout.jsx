import { Outlet } from "react-router-dom";
import Sidebar from "./Sidebar";
import Header from "./Header";

/**
 * MainLayout Component
 * Main layout wrapper for the operations dashboard
 * Features:
 * - Responsive sidebar layout
 * - Header with navigation
 * - Content area with outlet for pages
 * - Professional operations theme
 * - Proper spacing and structure
 */
const MainLayout = ({ title, onRefresh }) => {
  return (
    <div className="h-screen flex bg-gradient-to-br from-slate-50 via-blue-50/30 to-indigo-50/20">
      {/* Sidebar */}
      <Sidebar />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Header */}
        <Header title={title} onRefresh={onRefresh} />

        {/* Page Content - Full width with minimal padding */}
        <main className="flex-1 overflow-auto bg-transparent">
          <div className="min-h-full">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  );
};

export default MainLayout;
