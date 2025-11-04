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
    <div className={`bg-white border-r border-gray-200 transition-all duration-300 ${
      isCollapsed ? "w-16" : "w-64"
    } flex flex-col h-full`}>
      {/* Header */}
      <div className="p-4 border-b border-gray-200">
        <div className="flex items-center justify-between">
          {!isCollapsed && (
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center">
                <Shield className="w-5 h-5 text-white" />
              </div>
              <div>
                <h1 className="text-lg font-semibold text-gray-900">Operations</h1>
                <p className="text-xs text-gray-500">ConvergeAI</p>
              </div>
            </div>
          )}
          <button
            onClick={() => setIsCollapsed(!isCollapsed)}
            className="p-1.5 rounded-md hover:bg-gray-100 transition-colors"
          >
            {isCollapsed ? (
              <ChevronRight className="w-4 h-4 text-gray-600" />
            ) : (
              <ChevronLeft className="w-4 h-4 text-gray-600" />
            )}
          </button>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4 space-y-2">
        {navigationItems.map((item) => (
          <PermissionGate
            key={item.name}
            requiredPermissions={item.permissions}
          >
            <Link
              to={item.href}
              className={`flex items-center space-x-3 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                isActiveRoute(item.href)
                  ? "bg-primary text-white"
                  : "text-gray-700 hover:bg-gray-100 hover:text-gray-900"
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
      <div className="p-4 border-t border-gray-200">
        {!isCollapsed && staff && (
          <div className="mb-3 p-3 bg-gray-50 rounded-md">
            <p className="text-sm font-medium text-gray-900 truncate">
              {staff.name}
            </p>
            <p className="text-xs text-gray-500 truncate">
              {staff.email}
            </p>
            <div className="mt-1">
              <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-800">
                {role}
              </span>
            </div>
          </div>
        )}
        
        <button
          onClick={handleLogout}
          className={`flex items-center space-x-3 w-full px-3 py-2 rounded-md text-sm font-medium text-red-700 hover:bg-red-50 hover:text-red-900 transition-colors ${
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
