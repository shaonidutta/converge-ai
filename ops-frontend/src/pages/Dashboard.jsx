import { useState, useEffect, useCallback } from "react";
import {
  Users,
  MessageSquare,
  Clock,
  TrendingUp,
  AlertTriangle,
  CheckCircle,
  XCircle,
  Activity,
  RefreshCw,
  BarChart3,
  PieChart
} from "lucide-react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart as RechartsPieChart,
  Pie,
  Cell,
  LineChart,
  Line,
  Area,
  AreaChart
} from 'recharts';
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
  const [lastUpdated, setLastUpdated] = useState(new Date());
  const [autoRefresh, setAutoRefresh] = useState(true);

  /**
   * Fetch dashboard data
   */
  const fetchDashboardData = useCallback(async (showLoading = true) => {
    try {
      if (showLoading) setLoading(true);
      setError(null);

      // Fetch metrics and priority queue in parallel
      const [metricsResponse, queueResponse] = await Promise.all([
        api.dashboard.getMetrics(),
        api.dashboard.getPriorityQueue({ limit: 5 })
      ]);

      setMetrics(metricsResponse.data);
      setPriorityQueue(queueResponse.data.items || []);
      setLastUpdated(new Date());
    } catch (err) {
      console.error("Dashboard data fetch error:", err);
      setError("Failed to load dashboard data");
    } finally {
      if (showLoading) setLoading(false);
    }
  }, []);

  /**
   * Load data on component mount
   */
  useEffect(() => {
    fetchDashboardData();
  }, [fetchDashboardData]);

  /**
   * Auto-refresh functionality
   */
  useEffect(() => {
    if (!autoRefresh) return;

    const interval = setInterval(() => {
      fetchDashboardData(false); // Don't show loading spinner for auto-refresh
    }, 30000); // Refresh every 30 seconds

    return () => clearInterval(interval);
  }, [autoRefresh, fetchDashboardData]);

  /**
   * Process chart data
   */
  const getComplaintsByPriorityData = () => {
    if (!metrics?.complaints?.by_priority) return [];

    const priorities = metrics.complaints.by_priority;
    return [
      { name: 'Low', value: priorities.low || 0, color: '#10B981' },
      { name: 'Medium', value: priorities.medium || 0, color: '#F59E0B' },
      { name: 'High', value: priorities.high || 0, color: '#EF4444' },
      { name: 'Critical', value: priorities.critical || 0, color: '#DC2626' }
    ];
  };

  const getComplaintsByStatusData = () => {
    if (!metrics?.complaints?.by_status) return [];

    const status = metrics.complaints.by_status;
    return [
      { name: 'Open', value: status.open || 0 },
      { name: 'In Progress', value: status.in_progress || 0 },
      { name: 'Resolved', value: status.resolved || 0 },
      { name: 'Closed', value: status.closed || 0 }
    ];
  };

  const getRevenueData = () => {
    if (!metrics?.revenue?.by_status) return [];

    const revenue = metrics.revenue.by_status;
    return [
      { name: 'Confirmed', value: Math.round(revenue.confirmed || 0) },
      { name: 'Completed', value: Math.round(revenue.completed || 0) },
      { name: 'Cancelled', value: Math.round(revenue.cancelled || 0) }
    ];
  };

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

  /**
   * Chart components
   */
  const ComplaintsPriorityChart = () => {
    const data = getComplaintsByPriorityData();

    return (
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900">Complaints by Priority</h3>
          <PieChart className="w-5 h-5 text-gray-400" />
        </div>
        <ResponsiveContainer width="100%" height={300}>
          <RechartsPieChart>
            <Pie
              data={data}
              cx="50%"
              cy="50%"
              innerRadius={60}
              outerRadius={100}
              paddingAngle={5}
              dataKey="value"
            >
              {data.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} />
              ))}
            </Pie>
            <Tooltip formatter={(value) => [value, 'Count']} />
          </RechartsPieChart>
        </ResponsiveContainer>
        <div className="flex flex-wrap gap-4 mt-4">
          {data.map((item, index) => (
            <div key={index} className="flex items-center space-x-2">
              <div
                className="w-3 h-3 rounded-full"
                style={{ backgroundColor: item.color }}
              ></div>
              <span className="text-sm text-gray-600">{item.name}: {item.value}</span>
            </div>
          ))}
        </div>
      </div>
    );
  };

  const ComplaintsStatusChart = () => {
    const data = getComplaintsByStatusData();

    return (
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900">Complaints by Status</h3>
          <BarChart3 className="w-5 h-5 text-gray-400" />
        </div>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={data}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" />
            <YAxis />
            <Tooltip />
            <Bar dataKey="value" fill="#486581" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    );
  };

  const RevenueChart = () => {
    const data = getRevenueData();

    return (
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900">Revenue by Status</h3>
          <TrendingUp className="w-5 h-5 text-gray-400" />
        </div>
        <ResponsiveContainer width="100%" height={300}>
          <AreaChart data={data}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" />
            <YAxis />
            <Tooltip formatter={(value) => [`₹${value.toLocaleString()}`, 'Revenue']} />
            <Area
              type="monotone"
              dataKey="value"
              stroke="#486581"
              fill="#486581"
              fillOpacity={0.3}
            />
          </AreaChart>
        </ResponsiveContainer>
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
      {/* Welcome Section with Auto-refresh Controls */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold text-gray-900 mb-2">
              Operations Dashboard
            </h2>
            <p className="text-gray-600">
              Monitor key metrics, manage priority queue, and oversee operations performance.
            </p>
          </div>
          <div className="flex items-center space-x-4">
            <div className="text-sm text-gray-500">
              Last updated: {lastUpdated.toLocaleTimeString()}
            </div>
            <button
              onClick={() => fetchDashboardData()}
              className="flex items-center space-x-2 px-3 py-2 bg-primary text-white rounded-md hover:bg-primary-600 transition-colors"
            >
              <RefreshCw className="w-4 h-4" />
              <span>Refresh</span>
            </button>
            <button
              onClick={() => setAutoRefresh(!autoRefresh)}
              className={`flex items-center space-x-2 px-3 py-2 rounded-md transition-colors ${
                autoRefresh
                  ? 'bg-green-100 text-green-700 hover:bg-green-200'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              <Activity className={`w-4 h-4 ${autoRefresh ? 'animate-pulse' : ''}`} />
              <span>{autoRefresh ? 'Auto-refresh ON' : 'Auto-refresh OFF'}</span>
            </button>
          </div>
        </div>
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <MetricCard
          title="Active Bookings"
          value={metrics?.realtime?.active_bookings || 0}
          change={metrics?.bookings?.growth_rate}
          icon={Users}
          color="blue"
        />
        <MetricCard
          title="Open Complaints"
          value={metrics?.complaints?.unresolved || 0}
          change={null}
          icon={MessageSquare}
          color="yellow"
        />
        <MetricCard
          title="Priority Queue"
          value={priorityQueue.length || 0}
          change={null}
          icon={Clock}
          color="red"
        />
        <MetricCard
          title="SLA Compliance"
          value={`${Math.round(metrics?.sla?.compliance_rate || 0)}%`}
          change={null}
          icon={TrendingUp}
          color="green"
        />
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
        <ComplaintsPriorityChart />
        <ComplaintsStatusChart />
        <RevenueChart />
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
