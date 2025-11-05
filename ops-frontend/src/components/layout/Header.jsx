import { useState, useEffect } from "react";
import { Bell, Search, RefreshCw, Wifi, WifiOff } from "lucide-react";
import { useAuth } from "../../context/AuthContext";

/**
 * Header Component
 * Top navigation bar for operations dashboard
 * Features:
 * - Real-time connection status
 * - Notification bell with count
 * - Search functionality
 * - Refresh button
 * - Staff info display
 * - Professional operations theme
 */
const Header = ({ title = "Dashboard", onRefresh = null }) => {
  const { staff } = useAuth();
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const [notificationCount, setNotificationCount] = useState(0);
  const [searchQuery, setSearchQuery] = useState("");
  const [lastUpdated, setLastUpdated] = useState(new Date());

  /**
   * Handle online/offline status
   */
  useEffect(() => {
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  /**
   * Update last updated timestamp
   */
  useEffect(() => {
    const interval = setInterval(() => {
      setLastUpdated(new Date());
    }, 30000); // Update every 30 seconds

    return () => clearInterval(interval);
  }, []);

  /**
   * Handle refresh
   */
  const handleRefresh = () => {
    if (onRefresh) {
      onRefresh();
    }
    setLastUpdated(new Date());
  };

  /**
   * Handle search
   */
  const handleSearch = (e) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      // Implement search functionality
      console.log("Searching for:", searchQuery);
    }
  };

  /**
   * Format last updated time
   */
  const formatLastUpdated = (date) => {
    const now = new Date();
    const diff = Math.floor((now - date) / 1000);

    if (diff < 60) return "Just now";
    if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
    if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
    return date.toLocaleTimeString();
  };

  /**
   * Get staff initials from first_name and last_name
   */
  const getStaffInitials = () => {
    if (!staff) return 'OA'; // Default: Operations Admin

    const firstName = staff.first_name || '';
    const lastName = staff.last_name || '';

    // Get first character of first name and last name
    const firstInitial = firstName.charAt(0).toUpperCase();
    const lastInitial = lastName.charAt(0).toUpperCase();

    // Return both initials if available, otherwise return what we have
    if (firstInitial && lastInitial) {
      return firstInitial + lastInitial;
    } else if (firstInitial) {
      return firstInitial;
    } else if (lastInitial) {
      return lastInitial;
    }

    return 'OA'; // Fallback
  };

  /**
   * Get staff full name
   */
  const getStaffFullName = () => {
    if (!staff) return 'Operations Admin';

    const firstName = staff.first_name || '';
    const lastName = staff.last_name || '';

    if (firstName && lastName) {
      return `${firstName} ${lastName}`;
    } else if (firstName) {
      return firstName;
    } else if (lastName) {
      return lastName;
    }

    return staff.email || 'Operations Admin';
  };

  return (
    <header className="bg-white border-b border-gray-200 px-6 py-4">
      <div className="flex items-center justify-between">
        {/* Left Section - Title and Status */}
        <div className="flex items-center space-x-4">
          <div>
            <h1 className="text-2xl font-semibold text-gray-900">{title}</h1>
            <div className="flex items-center space-x-4 mt-1">
              {/* Connection Status */}
              <div className="flex items-center space-x-1">
                {isOnline ? (
                  <Wifi className="w-4 h-4 text-green-500" />
                ) : (
                  <WifiOff className="w-4 h-4 text-red-500" />
                )}
                <span className={`text-xs ${isOnline ? 'text-green-600' : 'text-red-600'}`}>
                  {isOnline ? 'Online' : 'Offline'}
                </span>
              </div>
              
              {/* Last Updated */}
              <span className="text-xs text-gray-500">
                Updated {formatLastUpdated(lastUpdated)}
              </span>
            </div>
          </div>
        </div>

        {/* Center Section - Search */}
        <div className="flex-1 max-w-md mx-8">
          <form onSubmit={handleSearch} className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
            <input
              type="text"
              placeholder="Search complaints, staff, or queue items..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary focus:border-transparent text-sm"
            />
          </form>
        </div>

        {/* Right Section - Actions and User */}
        <div className="flex items-center space-x-4">
          {/* Refresh Button */}
          {onRefresh && (
            <button
              onClick={handleRefresh}
              className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-md transition-colors"
              title="Refresh data"
            >
              <RefreshCw className="w-5 h-5" />
            </button>
          )}

          {/* Notifications */}
          <div className="relative">
            <button className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-md transition-colors">
              <Bell className="w-5 h-5" />
              {notificationCount > 0 && (
                <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center">
                  {notificationCount > 9 ? '9+' : notificationCount}
                </span>
              )}
            </button>
          </div>

          {/* Staff Info */}
          {staff && (
            <div className="flex items-center space-x-3 pl-4 border-l border-gray-200">
              <div className="text-right">
                <p className="text-sm font-medium text-gray-900">
                  {getStaffFullName()}
                </p>
                <p className="text-xs text-gray-500">
                  {staff.role?.display_name || staff.role?.name || staff.role}
                </p>
              </div>
              <div className="w-8 h-8 bg-primary rounded-full flex items-center justify-center">
                <span className="text-sm font-medium text-white">
                  {getStaffInitials()}
                </span>
              </div>
            </div>
          )}
        </div>
      </div>
    </header>
  );
};

export default Header;
