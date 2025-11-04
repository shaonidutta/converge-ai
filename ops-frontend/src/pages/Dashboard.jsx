import { useState, useEffect } from "react";
import { 
  Users, 
  MessageSquare, 
  Clock, 
  TrendingUp,
  AlertTriangle,
  CheckCircle,
  XCircle,
  Activity
} from "lucide-react";
import api from "../services/api";

/**
 * Dashboard Component
 * Main operations dashboard with key metrics and overview
 * Features:
 * - Real-time metrics display
 * - Priority queue overview
 * - Recent activity feed
 * - SLA status indicators
 * - Quick action buttons
 */
const Dashboard = () => {
  const [metrics, setMetrics] = useState(null);
  const [priorityQueue, setPriorityQueue] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  /**
   * Fetch dashboard data
   */
  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Fetch metrics and priority queue in parallel
      const [metricsResponse, queueResponse] = await Promise.all([
        api.dashboard.getMetrics(),
        api.dashboard.getPriorityQueue({ limit: 5 })
      ]);

      setMetrics(metricsResponse.data);
      setPriorityQueue(queueResponse.data.items || []);
    } catch (err) {
      console.error("Dashboard data fetch error:", err);
      setError("Failed to load dashboard data");
    } finally {
      setLoading(false);
    }
  };

  /**
   * Load data on component mount
   */
  useEffect(() => {
    fetchDashboardData();
  }, []);

  /**
   * Metric card component
   */
  const MetricCard = ({ title, value, change, icon: Icon, color = "blue" }) => {
    const colorClasses = {
      blue: "bg-blue-50 text-blue-600 border-blue-200",
      green: "bg-green-50 text-green-600 border-green-200",
      yellow: "bg-yellow-50 text-yellow-600 border-yellow-200",
      red: "bg-red-50 text-red-600 border-red-200",
    };

    return (
      <div className="bg-white rounded-lg border border-gray-200 p-6 hover:shadow-md transition-shadow">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm font-medium text-gray-600">{title}</p>
            <p className="text-3xl font-bold text-gray-900 mt-2">{value}</p>
            {change && (
              <p className={`text-sm mt-2 ${change >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                {change >= 0 ? '+' : ''}{change}% from last period
              </p>
            )}
          </div>
          <div className={`p-3 rounded-lg ${colorClasses[color]}`}>
            <Icon className="w-6 h-6" />
          </div>
        </div>
      </div>
    );
  };

  /**
   * Priority queue item component
   */
  const PriorityQueueItem = ({ item }) => {
    const priorityColors = {
      low: "bg-green-100 text-green-800",
      medium: "bg-yellow-100 text-yellow-800",
      high: "bg-orange-100 text-orange-800",
      critical: "bg-red-100 text-red-800",
    };

    return (
      <div className="flex items-center justify-between p-4 bg-white rounded-lg border border-gray-200 hover:shadow-sm transition-shadow">
        <div className="flex-1">
          <h4 className="text-sm font-medium text-gray-900">{item.title}</h4>
          <p className="text-sm text-gray-600 mt-1">{item.description}</p>
          <div className="flex items-center space-x-2 mt-2">
            <span className={`px-2 py-1 rounded-full text-xs font-medium ${priorityColors[item.priority]}`}>
              {item.priority}
            </span>
            <span className="text-xs text-gray-500">{item.created_at}</span>
          </div>
        </div>
        <div className="ml-4">
          <button className="text-primary hover:text-primary-600 text-sm font-medium">
            Review
          </button>
        </div>
      </div>
    );
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <Activity className="w-8 h-8 animate-spin text-primary mx-auto mb-4" />
          <p className="text-gray-600">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <XCircle className="w-8 h-8 text-red-500 mx-auto mb-4" />
          <p className="text-gray-600">{error}</p>
          <button 
            onClick={fetchDashboardData}
            className="mt-4 px-4 py-2 bg-primary text-white rounded-md hover:bg-primary-600 transition-colors"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Welcome Section */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          Operations Dashboard
        </h2>
        <p className="text-gray-600">
          Monitor key metrics, manage priority queue, and oversee operations performance.
        </p>
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <MetricCard
          title="Active Bookings"
          value={metrics?.active_bookings || 0}
          change={metrics?.booking_change}
          icon={Users}
          color="blue"
        />
        <MetricCard
          title="Open Complaints"
          value={metrics?.open_complaints || 0}
          change={metrics?.complaint_change}
          icon={MessageSquare}
          color="yellow"
        />
        <MetricCard
          title="Priority Queue"
          value={metrics?.priority_queue_count || 0}
          change={metrics?.queue_change}
          icon={Clock}
          color="red"
        />
        <MetricCard
          title="SLA Compliance"
          value={`${metrics?.sla_compliance || 0}%`}
          change={metrics?.sla_change}
          icon={TrendingUp}
          color="green"
        />
      </div>

      {/* Priority Queue Section */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-lg font-semibold text-gray-900">
            Priority Queue
          </h3>
          <button className="text-primary hover:text-primary-600 text-sm font-medium">
            View All
          </button>
        </div>
        
        {priorityQueue.length > 0 ? (
          <div className="space-y-4">
            {priorityQueue.map((item, index) => (
              <PriorityQueueItem key={index} item={item} />
            ))}
          </div>
        ) : (
          <div className="text-center py-8">
            <CheckCircle className="w-8 h-8 text-green-500 mx-auto mb-2" />
            <p className="text-gray-600">No items in priority queue</p>
          </div>
        )}
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <button className="bg-white border border-gray-200 rounded-lg p-6 text-left hover:shadow-md transition-shadow">
          <AlertTriangle className="w-8 h-8 text-yellow-500 mb-3" />
          <h4 className="text-lg font-semibold text-gray-900 mb-2">
            Review Alerts
          </h4>
          <p className="text-gray-600 text-sm">
            Check and manage system alerts and notifications
          </p>
        </button>

        <button className="bg-white border border-gray-200 rounded-lg p-6 text-left hover:shadow-md transition-shadow">
          <MessageSquare className="w-8 h-8 text-blue-500 mb-3" />
          <h4 className="text-lg font-semibold text-gray-900 mb-2">
            Manage Complaints
          </h4>
          <p className="text-gray-600 text-sm">
            View and resolve customer complaints
          </p>
        </button>

        <button className="bg-white border border-gray-200 rounded-lg p-6 text-left hover:shadow-md transition-shadow">
          <Users className="w-8 h-8 text-green-500 mb-3" />
          <h4 className="text-lg font-semibold text-gray-900 mb-2">
            Staff Management
          </h4>
          <p className="text-gray-600 text-sm">
            Manage staff roles and permissions
          </p>
        </button>
      </div>
    </div>
  );
};

export default Dashboard;
