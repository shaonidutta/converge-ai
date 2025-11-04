import { useState } from "react";
import { Link, useLocation } from "react-router-dom";
import { 
  LayoutDashboard, 
  AlertTriangle, 
  MessageSquare, 
  Users, 
  Settings, 
  LogOut,
  ChevronLeft,
  ChevronRight,
  Shield,
  BarChart3,
  Clock
} from "lucide-react";
import { useAuth } from "../../context/AuthContext";
import { PermissionGate } from "../ProtectedRoute";

/**
 * Sidebar Component
 * Navigation sidebar for operations dashboard
 * Features:
 * - Collapsible sidebar
 * - Role-based navigation items
 * - Active route highlighting
 * - Professional operations theme
 * - Responsive design
 */
const Sidebar = () => {
  const [isCollapsed, setIsCollapsed] = useState(false);
  const location = useLocation();
  const { staff, logout, role } = useAuth();

  /**
   * Navigation items with permissions
   */
  const navigationItems = [
    {
      name: "Dashboard",
      href: "/dashboard",
      icon: LayoutDashboard,
      permissions: [],
    },
    {
      name: "Priority Queue",
      href: "/priority-queue",
      icon: Clock,
      permissions: ["view_priority_queue"],
    },
    {
      name: "Complaints",
      href: "/complaints",
      icon: MessageSquare,
      permissions: ["view_complaints"],
    },
    {
      name: "Alerts",
      href: "/alerts",
      icon: AlertTriangle,
      permissions: ["view_alerts"],
    },
    {
      name: "Analytics",
      href: "/analytics",
      icon: BarChart3,
      permissions: ["view_analytics"],
    },
    {
      name: "Staff",
      href: "/staff",
      icon: Users,
      permissions: ["manage_staff"],
    },
    {
      name: "Settings",
      href: "/settings",
      icon: Settings,
      permissions: ["manage_settings"],
    },
  ];

  /**
   * Check if route is active
   */
  const isActiveRoute = (href) => {
    if (href === "/dashboard") {
      return location.pathname === "/" || location.pathname === "/dashboard";
    }
    return location.pathname.startsWith(href);
  };

  /**
   * Handle logout
   */
  const handleLogout = async () => {
    try {
      await logout();
    } catch (error) {
      console.error("Logout error:", error);
    }
  };

  return (
    <div className={`bg-gradient-to-b from-gray-900 via-gray-800 to-gray-900 border-r border-gray-700/50 transition-all duration-300 ${
      isCollapsed ? "w-16" : "w-64"
    } flex flex-col h-full shadow-2xl`}>
      {/* Header */}
      <div className="p-4 border-b border-gray-700/50">
        <div className="flex items-center justify-between">
          {!isCollapsed && (
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl flex items-center justify-center shadow-lg">
                <Shield className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-lg font-bold text-white">Operations</h1>
                <p className="text-xs text-gray-400">ConvergeAI</p>
              </div>
            </div>
          )}
          <button
            onClick={() => setIsCollapsed(!isCollapsed)}
            className="p-2 rounded-lg hover:bg-gray-700/50 transition-all duration-200 text-gray-400 hover:text-white"
          >
            {isCollapsed ? (
              <ChevronRight className="w-4 h-4" />
            ) : (
              <ChevronLeft className="w-4 h-4" />
            )}
          </button>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4 space-y-1">
        {navigationItems.map((item) => (
          <PermissionGate
            key={item.name}
            requiredPermissions={item.permissions}
          >
            <Link
              to={item.href}
              className={`flex items-center space-x-3 px-3 py-3 rounded-xl text-sm font-medium transition-all duration-200 ${
                isActiveRoute(item.href)
                  ? "bg-gradient-to-r from-blue-600 to-blue-700 text-white shadow-lg transform scale-[1.02]"
                  : "text-gray-300 hover:bg-gray-700/50 hover:text-white hover:transform hover:scale-[1.01]"
              }`}
              title={isCollapsed ? item.name : undefined}
            >
              <item.icon className="w-5 h-5 flex-shrink-0" />
              {!isCollapsed && <span>{item.name}</span>}
            </Link>
          </PermissionGate>
        ))}
      </nav>

      {/* User Info & Logout */}
      <div className="p-4 border-t border-gray-700/50">
        {!isCollapsed && staff && (
          <div className="mb-4 p-3 bg-gradient-to-r from-gray-800/50 to-gray-700/50 rounded-xl border border-gray-600/30">
            <p className="text-sm font-semibold text-white truncate">
              {staff.name}
            </p>
            <p className="text-xs text-gray-400 truncate">
              {staff.email}
            </p>
            <div className="mt-2">
              <span className="inline-flex items-center px-2.5 py-1 rounded-lg text-xs font-medium bg-gradient-to-r from-blue-500 to-blue-600 text-white shadow-sm">
                {role}
              </span>
            </div>
          </div>
        )}

        <button
          onClick={handleLogout}
          className={`flex items-center space-x-3 w-full px-3 py-3 rounded-xl text-sm font-medium text-red-400 hover:bg-red-900/20 hover:text-red-300 transition-all duration-200 hover:transform hover:scale-[1.01] ${
            isCollapsed ? "justify-center" : ""
          }`}
          title={isCollapsed ? "Logout" : undefined}
        >
          <LogOut className="w-5 h-5 flex-shrink-0" />
          {!isCollapsed && <span>Logout</span>}
        </button>
      </div>
    </div>
  );
};

export default Sidebar;
