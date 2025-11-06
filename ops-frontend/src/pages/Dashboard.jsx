import { useState, useEffect, useCallback } from "react";
import { useNavigate } from "react-router-dom";
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
  const navigate = useNavigate();
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
      blue: {
        gradient: "from-blue-500 to-blue-600",
        bg: "bg-gradient-to-br from-blue-50 via-blue-50 to-blue-100/50",
        text: "text-blue-600",
        icon: "text-white"
      },
      green: {
        gradient: "from-emerald-500 to-emerald-600",
        bg: "bg-gradient-to-br from-emerald-50 via-emerald-50 to-emerald-100/50",
        text: "text-emerald-600",
        icon: "text-white"
      },
      yellow: {
        gradient: "from-amber-500 to-amber-600",
        bg: "bg-gradient-to-br from-amber-50 via-amber-50 to-amber-100/50",
        text: "text-amber-600",
        icon: "text-white"
      },
      red: {
        gradient: "from-red-500 to-red-600",
        bg: "bg-gradient-to-br from-red-50 via-red-50 to-red-100/50",
        text: "text-red-600",
        icon: "text-white"
      },
    };

    const colors = colorClasses[color];

    return (
      <div className="bg-gradient-to-br from-white via-white to-gray-50/30 p-4 rounded-xl border border-gray-200/60 shadow-lg hover:shadow-xl transition-all duration-300 hover:border-gray-300/60 hover:scale-[1.02] group cursor-pointer">
        <div className="flex items-center justify-between">
          <div className="flex-1 min-w-0">
            <p className="text-xs font-medium text-gray-600 uppercase tracking-wide mb-1">{title}</p>
            <p className="text-2xl font-bold text-gray-900 mt-1 group-hover:scale-105 transition-transform duration-200 truncate">{value}</p>
            {change && (
              <p className={`text-xs mt-1.5 flex items-center ${change >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                <TrendingUp className="w-3 h-3 mr-1" />
                {change >= 0 ? '+' : ''}{change}% from last period
              </p>
            )}
          </div>
          <div className={`p-3 rounded-xl bg-gradient-to-br ${colors.gradient} shadow-md group-hover:shadow-lg transition-all duration-200 group-hover:scale-105 flex-shrink-0 ml-3`}>
            <Icon className={`w-6 h-6 ${colors.icon}`} />
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
      low: {
        bg: "bg-gradient-to-r from-green-100 to-green-200",
        text: "text-green-800",
        border: "border-green-300",
        icon: "text-green-600"
      },
      medium: {
        bg: "bg-gradient-to-r from-yellow-100 to-yellow-200",
        text: "text-yellow-800",
        border: "border-yellow-300",
        icon: "text-yellow-600"
      },
      high: {
        bg: "bg-gradient-to-r from-orange-100 to-orange-200",
        text: "text-orange-800",
        border: "border-orange-300",
        icon: "text-orange-600"
      },
      critical: {
        bg: "bg-gradient-to-r from-red-100 to-red-200",
        text: "text-red-800",
        border: "border-red-300",
        icon: "text-red-600"
      },
    };

    const colors = priorityColors[item.priority] || priorityColors.medium;

    return (
      <div className="flex items-center justify-between p-4 bg-gradient-to-r from-white via-white to-gray-50/30 rounded-xl border border-gray-200/60 hover:shadow-lg hover:border-gray-300/60 transition-all duration-200 group hover:scale-[1.01]">
        <div className="flex items-center space-x-4 flex-1">
          <div className={`p-3 rounded-xl ${colors.bg} ${colors.border} border shadow-sm`}>
            <Clock className={`w-5 h-5 ${colors.icon}`} />
          </div>
          <div className="flex-1 min-w-0">
            <h4 className="text-base font-semibold text-gray-900 group-hover:text-blue-600 transition-colors truncate">{item.title}</h4>
            <p className="text-sm text-gray-600 mt-1 leading-relaxed line-clamp-2">{item.description}</p>
            <div className="flex items-center space-x-3 mt-2">
              <span className={`px-2.5 py-1 rounded-lg text-xs font-semibold uppercase tracking-wide ${colors.bg} ${colors.text} border ${colors.border}`}>
                {item.priority}
              </span>
              <span className="text-xs text-gray-500 font-medium">{item.created_at}</span>
            </div>
          </div>
        </div>
        <div className="ml-4 flex-shrink-0">
          <button className="btn-primary text-sm px-4 py-2">
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
      <div className="bg-gradient-to-br from-white via-white to-gray-50/30 p-4 rounded-xl border border-gray-200/60 shadow-lg hover:shadow-xl transition-all duration-300 hover:border-gray-300/60">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-lg font-bold text-gray-900">Complaints by Priority</h3>
            <p className="text-xs text-gray-500 mt-0.5">Distribution of complaint priorities</p>
          </div>
          <div className="p-2 bg-gradient-to-br from-purple-500 to-purple-600 rounded-lg shadow-md">
            <PieChart className="w-5 h-5 text-white" />
          </div>
        </div>
        <ResponsiveContainer width="100%" height={280}>
          <RechartsPieChart>
            <Pie
              data={data}
              cx="50%"
              cy="50%"
              innerRadius={60}
              outerRadius={95}
              paddingAngle={2}
              dataKey="value"
            >
              {data.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} />
              ))}
            </Pie>
            <Tooltip
              formatter={(value) => [value, 'Count']}
              contentStyle={{
                backgroundColor: 'rgba(255, 255, 255, 0.95)',
                border: 'none',
                borderRadius: '8px',
                boxShadow: '0 4px 12px rgba(0, 0, 0, 0.1)',
                fontSize: '12px'
              }}
            />
          </RechartsPieChart>
        </ResponsiveContainer>
        <div className="flex flex-wrap gap-2 mt-4">
          {data.map((item, index) => (
            <div key={index} className="flex items-center space-x-2 bg-gray-50/50 px-2 py-1.5 rounded-md">
              <div
                className="w-3 h-3 rounded-full shadow-sm"
                style={{ backgroundColor: item.color }}
              ></div>
              <span className="text-xs font-medium text-gray-700">{item.name}: <span className="font-bold">{item.value}</span></span>
            </div>
          ))}
        </div>
      </div>
    );
  };

  const ComplaintsStatusChart = () => {
    const data = getComplaintsByStatusData();

    return (
      <div className="bg-gradient-to-br from-white via-white to-gray-50/30 p-4 rounded-xl border border-gray-200/60 shadow-lg hover:shadow-xl transition-all duration-300 hover:border-gray-300/60">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-lg font-bold text-gray-900">Complaints by Status</h3>
            <p className="text-xs text-gray-500 mt-0.5">Current status distribution</p>
          </div>
          <div className="p-2 bg-gradient-to-br from-indigo-500 to-indigo-600 rounded-lg shadow-md">
            <BarChart3 className="w-5 h-5 text-white" />
          </div>
        </div>
        <ResponsiveContainer width="100%" height={280}>
          <BarChart data={data} margin={{ top: 15, right: 20, left: 15, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" opacity={0.5} />
            <XAxis
              dataKey="name"
              tick={{ fontSize: 11, fill: '#6b7280' }}
              axisLine={{ stroke: '#d1d5db' }}
            />
            <YAxis
              tick={{ fontSize: 11, fill: '#6b7280' }}
              axisLine={{ stroke: '#d1d5db' }}
            />
            <Tooltip
              formatter={(value) => [value, 'Count']}
              contentStyle={{
                backgroundColor: 'rgba(255, 255, 255, 0.95)',
                border: 'none',
                borderRadius: '8px',
                boxShadow: '0 4px 12px rgba(0, 0, 0, 0.1)',
                fontSize: '12px'
              }}
            />
            <Bar
              dataKey="value"
              fill="#486581"
              radius={[4, 4, 0, 0]}
            />
          </BarChart>
        </ResponsiveContainer>
      </div>
    );
  };

  const RevenueChart = () => {
    const data = getRevenueData();

    return (
      <div className="bg-gradient-to-br from-white via-white to-gray-50/30 p-4 rounded-xl border border-gray-200/60 shadow-lg hover:shadow-xl transition-all duration-300 hover:border-gray-300/60">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-lg font-bold text-gray-900">Revenue by Status</h3>
            <p className="text-xs text-gray-500 mt-0.5">Revenue distribution across booking statuses</p>
          </div>
          <div className="p-2 bg-gradient-to-br from-emerald-500 to-emerald-600 rounded-lg shadow-md">
            <TrendingUp className="w-5 h-5 text-white" />
          </div>
        </div>
        <ResponsiveContainer width="100%" height={280}>
          <AreaChart data={data} margin={{ top: 15, right: 20, left: 15, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" opacity={0.5} />
            <XAxis
              dataKey="name"
              tick={{ fontSize: 11, fill: '#6b7280' }}
              axisLine={{ stroke: '#d1d5db' }}
            />
            <YAxis
              tick={{ fontSize: 11, fill: '#6b7280' }}
              axisLine={{ stroke: '#d1d5db' }}
            />
            <Tooltip
              formatter={(value) => [`₹${value.toLocaleString()}`, 'Revenue']}
              contentStyle={{
                backgroundColor: 'rgba(255, 255, 255, 0.95)',
                border: 'none',
                borderRadius: '8px',
                boxShadow: '0 4px 12px rgba(0, 0, 0, 0.1)',
                fontSize: '12px'
              }}
            />
            <Area
              type="monotone"
              dataKey="value"
              stroke="#10B981"
              fill="url(#areaGradient)"
              strokeWidth={2}
            />
            <defs>
              <linearGradient id="areaGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#10B981" stopOpacity={0.4} />
                <stop offset="100%" stopColor="#10B981" stopOpacity={0.1} />
              </linearGradient>
            </defs>
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
    <div className="min-h-full bg-transparent">
      {/* Professional Header Section */}
      <div className="bg-gradient-to-r from-white via-blue-50/30 to-indigo-50/20 border-b border-gray-200/50 backdrop-blur-sm">
        <div className="px-6 py-6">
          <div className="flex items-center justify-between">
            <div className="space-y-1">
              <h1 className="text-2xl font-bold bg-gradient-to-r from-gray-900 via-blue-900 to-indigo-900 bg-clip-text text-transparent">
                Operations Dashboard
              </h1>
              <p className="text-gray-600 text-base">
                Monitor key metrics, manage priority queue, and oversee operations performance.
              </p>
            </div>
            <div className="flex items-center space-x-4">
              <div className="text-right">
                <p className="text-xs font-medium text-gray-700">Last updated</p>
                <p className="text-base font-semibold text-blue-600">
                  {lastUpdated.toLocaleTimeString()}
                </p>
              </div>
              <div className="flex items-center space-x-2">
                <button
                  onClick={() => fetchDashboardData()}
                  className="btn-primary flex items-center space-x-2 group text-sm px-3 py-2"
                >
                  <RefreshCw className="w-4 h-4 group-hover:rotate-180 transition-transform duration-300" />
                  <span>Refresh</span>
                </button>
                <button
                  onClick={() => setAutoRefresh(!autoRefresh)}
                  className={`flex items-center space-x-2 px-3 py-2 rounded-lg font-medium transition-all duration-200 text-sm ${
                    autoRefresh
                      ? 'btn-success'
                      : 'btn-secondary'
                  }`}
                >
                  <Activity className={`w-4 h-4 ${autoRefresh ? 'animate-pulse text-white' : 'text-gray-600'}`} />
                  <span>{autoRefresh ? 'Auto-refresh ON' : 'Auto-refresh OFF'}</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Enhanced Metrics Grid */}
      <div className="px-6 py-4">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
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
      </div>

      {/* Enhanced Charts Section */}
      <div className="px-6 pb-4">
        <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-4">
          <ComplaintsPriorityChart />
          <ComplaintsStatusChart />
          <RevenueChart />
        </div>
      </div>

      {/* Enhanced Priority Queue Section */}
      <div className="px-6 pb-8">
        <div className="dashboard-card-elevated p-6">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h3 className="text-xl font-bold text-gray-900">Priority Queue</h3>
              <p className="text-sm text-gray-500 mt-1">High-priority items requiring immediate attention</p>
            </div>
            <button
              className="btn-primary"
              onClick={() => navigate('/priority-queue')}
            >
              View All
            </button>
          </div>

          {priorityQueue.length > 0 ? (
            <div className="space-y-3">
              {priorityQueue.map((item, index) => (
                <PriorityQueueItem key={index} item={item} />
              ))}
            </div>
          ) : (
            <div className="text-center py-12">
              <div className="p-4 bg-gradient-to-br from-green-500 to-green-600 rounded-2xl w-16 h-16 mx-auto mb-4 flex items-center justify-center">
                <CheckCircle className="w-8 h-8 text-white" />
              </div>
              <p className="text-gray-600 text-lg font-medium">No items in priority queue</p>
              <p className="text-gray-500 text-sm mt-1">All high-priority items have been resolved</p>
            </div>
          )}
        </div>
      </div>

      {/* Enhanced Quick Actions */}
      <div className="px-6 pb-8">
        <div className="mb-6">
          <h3 className="text-xl font-bold text-gray-900 mb-2">Quick Actions</h3>
          <p className="text-sm text-gray-500">Access frequently used operations and management tools</p>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <button
            className="dashboard-card-elevated p-6 text-left group hover:scale-[1.02] transition-all duration-200"
            onClick={() => navigate('/alerts')}
          >
            <div className="p-4 bg-gradient-to-br from-amber-500 to-amber-600 rounded-2xl w-16 h-16 mb-4 flex items-center justify-center group-hover:shadow-xl transition-shadow">
              <AlertTriangle className="w-8 h-8 text-white" />
            </div>
            <h4 className="text-xl font-bold text-gray-900 mb-2">
              Review Alerts
            </h4>
            <p className="text-gray-600">
              Check and manage system alerts and notifications
            </p>
          </button>

          <button
            className="dashboard-card-elevated p-6 text-left group hover:scale-[1.02] transition-all duration-200"
            onClick={() => navigate('/complaints')}
          >
            <div className="p-4 bg-gradient-to-br from-blue-500 to-blue-600 rounded-2xl w-16 h-16 mb-4 flex items-center justify-center group-hover:shadow-xl transition-shadow">
              <MessageSquare className="w-8 h-8 text-white" />
            </div>
            <h4 className="text-xl font-bold text-gray-900 mb-2">
              Manage Complaints
            </h4>
            <p className="text-gray-600">
              View and resolve customer complaints
            </p>
          </button>

          <button
            className="dashboard-card-elevated p-6 text-left group hover:scale-[1.02] transition-all duration-200"
            onClick={() => navigate('/staff')}
          >
            <div className="p-4 bg-gradient-to-br from-emerald-500 to-emerald-600 rounded-2xl w-16 h-16 mb-4 flex items-center justify-center group-hover:shadow-xl transition-shadow">
              <Users className="w-8 h-8 text-white" />
            </div>
            <h4 className="text-xl font-bold text-gray-900 mb-2">
              Staff Management
            </h4>
            <p className="text-gray-600">
              Manage staff roles and permissions
            </p>
          </button>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
