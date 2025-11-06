import { useState, useEffect } from 'react';
import {
  TrendingUp,
  TrendingDown,
  Calendar,
  Download,
  RefreshCw,
  Filter,
  BarChart3,
  PieChart as PieChartIcon,
  Activity,
  Users,
  AlertTriangle,
  CheckCircle,
  Clock,
  DollarSign
} from 'lucide-react';
import {
  AreaChart,
  Area,
  BarChart,
  Bar,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';
import api from '../services/api';

/**
 * Analytics Page Component
 * Comprehensive analytics dashboard with advanced metrics visualization
 * Features:
 * - Time-range filters (Today, Week, Month, Quarter, Year, Custom)
 * - Multiple chart types (Area, Bar, Line, Pie)
 * - Key performance indicators (KPIs)
 * - Trend analysis with percentage changes
 * - Export functionality
 * - Real-time data refresh
 * - Responsive design
 */
const AnalyticsPage = () => {
  // State management
  const [timeRange, setTimeRange] = useState('week'); // today, week, month, quarter, year, custom
  const [loading, setLoading] = useState(false);
  const [lastUpdated, setLastUpdated] = useState(new Date());
  const [showFilters, setShowFilters] = useState(false);
  const [customDateRange, setCustomDateRange] = useState({ start: '', end: '' });

  // Analytics data state
  const [kpiData, setKpiData] = useState({
    totalBookings: { value: 0, change: 0, trend: 'up' },
    totalRevenue: { value: 0, change: 0, trend: 'up' },
    activeComplaints: { value: 0, change: 0, trend: 'down' },
    avgResolutionTime: { value: 0, change: 0, trend: 'down' },
    customerSatisfaction: { value: 0, change: 0, trend: 'up' },
    staffUtilization: { value: 0, change: 0, trend: 'up' }
  });

  const [trendData, setTrendData] = useState([]);
  const [categoryData, setCategoryData] = useState([]);
  const [statusDistribution, setStatusDistribution] = useState([]);
  const [performanceData, setPerformanceData] = useState([]);

  /**
   * Time range options
   */
  const timeRangeOptions = [
    { value: 'today', label: 'Today' },
    { value: 'week', label: 'This Week' },
    { value: 'month', label: 'This Month' },
    { value: 'quarter', label: 'This Quarter' },
    { value: 'year', label: 'This Year' },
    { value: 'custom', label: 'Custom Range' }
  ];

  /**
   * Chart colors
   */
  const COLORS = {
    primary: '#486581',
    secondary: '#6B7FA8',
    success: '#10B981',
    warning: '#F59E0B',
    danger: '#EF4444',
    info: '#3B82F6',
    purple: '#8B5CF6',
    pink: '#EC4899'
  };

  const PIE_COLORS = [COLORS.primary, COLORS.secondary, COLORS.success, COLORS.warning, COLORS.danger, COLORS.info];

  /**
   * Fetch analytics data from backend APIs
   */
  const fetchAnalyticsData = async () => {
    setLoading(true);
    try {
      // Prepare query parameters
      const params = {
        time_range: timeRange,
        ...(timeRange === 'custom' && customDateRange.start && customDateRange.end && {
          start_date: customDateRange.start,
          end_date: customDateRange.end
        })
      };

      // Fetch all analytics data in parallel
      const [kpisResponse, trendsResponse, categoriesResponse, statusResponse, performanceResponse] = await Promise.all([
        api.analytics.getKPIs(params),
        api.analytics.getTrends(params),
        api.analytics.getCategories(params),
        api.analytics.getStatus(params),
        api.analytics.getPerformance(params)
      ]);

      // Update KPI data
      const kpis = kpisResponse.data;
      setKpiData({
        totalBookings: kpis.total_bookings,
        totalRevenue: kpis.total_revenue,
        activeComplaints: kpis.active_complaints,
        avgResolutionTime: kpis.avg_resolution_time,
        customerSatisfaction: kpis.customer_satisfaction,
        staffUtilization: kpis.staff_utilization
      });

      // Update trend data
      setTrendData(trendsResponse.data.data || []);

      // Update category data
      setCategoryData(categoriesResponse.data.data || []);

      // Update status distribution
      setStatusDistribution(statusResponse.data.data || []);

      // Update performance data
      setPerformanceData(performanceResponse.data.data || []);

      setLastUpdated(new Date());
    } catch (error) {
      console.error('Error fetching analytics data:', error);
      // Show error notification to user
      alert('Failed to fetch analytics data. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  /**
   * Handle time range change
   */
  const handleTimeRangeChange = (range) => {
    setTimeRange(range);
    if (range !== 'custom') {
      fetchAnalyticsData();
    }
  };

  /**
   * Handle custom date range apply
   */
  const handleCustomRangeApply = () => {
    if (customDateRange.start && customDateRange.end) {
      fetchAnalyticsData();
      setShowFilters(false);
    }
  };

  /**
   * Handle export
   */
  const handleExport = (format) => {
    console.log(`Exporting analytics data as ${format}`);
    // TODO: Implement export functionality
  };

  /**
   * Handle refresh
   */
  const handleRefresh = () => {
    fetchAnalyticsData();
  };

  /**
   * Format currency
   */
  const formatCurrency = (value) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0
    }).format(value);
  };

  /**
   * Format number
   */
  const formatNumber = (value) => {
    return new Intl.NumberFormat('en-IN').format(value);
  };

  /**
   * Get trend icon
   */
  const getTrendIcon = (trend) => {
    return trend === 'up' ? (
      <TrendingUp className="w-4 h-4 text-green-500" />
    ) : (
      <TrendingDown className="w-4 h-4 text-red-500" />
    );
  };

  /**
   * Get trend color
   */
  const getTrendColor = (trend, change) => {
    if (trend === 'up') {
      return change > 0 ? 'text-green-600' : 'text-red-600';
    } else {
      return change < 0 ? 'text-green-600' : 'text-red-600';
    }
  };

  // Fetch data on mount and time range change
  useEffect(() => {
    fetchAnalyticsData();
  }, []);

  return (
    <div className="min-h-full bg-gray-50">
      {/* Page Header */}
      <div className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Analytics & Insights</h1>
            <p className="text-sm text-gray-500 mt-1">
              Last updated: {lastUpdated.toLocaleTimeString()}
            </p>
          </div>
          <button
            onClick={handleRefresh}
            disabled={loading}
            className={`p-2 text-gray-600 hover:bg-gray-100 rounded-md transition-colors ${loading ? 'animate-spin' : ''}`}
            title="Refresh Data"
          >
            <RefreshCw className="w-5 h-5" />
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div className="p-6">
        {/* Filters Bar */}
        <div className="mb-6 bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <div className="flex items-center justify-between flex-wrap gap-4">
            {/* Time Range Selector */}
            <div className="flex items-center space-x-2">
              <Calendar className="w-5 h-5 text-gray-400" />
              <div className="flex space-x-2">
                {timeRangeOptions.map((option) => (
                  <button
                    key={option.value}
                    onClick={() => handleTimeRangeChange(option.value)}
                    className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                      timeRange === option.value
                        ? 'bg-primary text-white'
                        : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                    }`}
                  >
                    {option.label}
                  </button>
                ))}
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex items-center space-x-2">
              <button
                onClick={() => setShowFilters(!showFilters)}
                className="p-2 text-gray-600 hover:bg-gray-100 rounded-md transition-colors"
                title="Advanced Filters"
              >
                <Filter className="w-5 h-5" />
              </button>
              <button
                onClick={() => handleExport('pdf')}
                className="px-4 py-2 bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200 transition-colors flex items-center space-x-2"
              >
                <Download className="w-4 h-4" />
                <span className="text-sm font-medium">Export</span>
              </button>
              <button
                onClick={handleRefresh}
                className={`p-2 text-gray-600 hover:bg-gray-100 rounded-md transition-colors ${loading ? 'animate-spin' : ''}`}
                title="Refresh"
              >
                <RefreshCw className="w-5 h-5" />
              </button>
            </div>
          </div>

          {/* Custom Date Range */}
          {showFilters && timeRange === 'custom' && (
            <div className="mt-4 pt-4 border-t border-gray-200">
              <div className="flex items-center space-x-4">
                <div className="flex-1">
                  <label className="block text-sm font-medium text-gray-700 mb-1">Start Date</label>
                  <input
                    type="date"
                    value={customDateRange.start}
                    onChange={(e) => setCustomDateRange({ ...customDateRange, start: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary focus:border-transparent"
                  />
                </div>
                <div className="flex-1">
                  <label className="block text-sm font-medium text-gray-700 mb-1">End Date</label>
                  <input
                    type="date"
                    value={customDateRange.end}
                    onChange={(e) => setCustomDateRange({ ...customDateRange, end: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary focus:border-transparent"
                  />
                </div>
                <div className="pt-6">
                  <button
                    onClick={handleCustomRangeApply}
                    className="px-6 py-2 bg-primary text-white rounded-md hover:bg-primary/90 transition-colors"
                  >
                    Apply
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* KPI Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-6">
          {/* Total Bookings */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="p-3 bg-blue-50 rounded-lg">
                <BarChart3 className="w-6 h-6 text-blue-600" />
              </div>
              {getTrendIcon(kpiData.totalBookings.trend)}
            </div>
            <h3 className="text-sm font-medium text-gray-600 mb-1">Total Bookings</h3>
            <p className="text-3xl font-bold text-gray-900 mb-2">{formatNumber(kpiData.totalBookings.value)}</p>
            <p className={`text-sm font-medium ${getTrendColor(kpiData.totalBookings.trend, kpiData.totalBookings.change)}`}>
              {kpiData.totalBookings.change > 0 ? '+' : ''}{kpiData.totalBookings.change}% from last period
            </p>
          </div>

          {/* Total Revenue */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="p-3 bg-green-50 rounded-lg">
                <DollarSign className="w-6 h-6 text-green-600" />
              </div>
              {getTrendIcon(kpiData.totalRevenue.trend)}
            </div>
            <h3 className="text-sm font-medium text-gray-600 mb-1">Total Revenue</h3>
            <p className="text-3xl font-bold text-gray-900 mb-2">{formatCurrency(kpiData.totalRevenue.value)}</p>
            <p className={`text-sm font-medium ${getTrendColor(kpiData.totalRevenue.trend, kpiData.totalRevenue.change)}`}>
              {kpiData.totalRevenue.change > 0 ? '+' : ''}{kpiData.totalRevenue.change}% from last period
            </p>
          </div>

          {/* Active Complaints */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="p-3 bg-red-50 rounded-lg">
                <AlertTriangle className="w-6 h-6 text-red-600" />
              </div>
              {getTrendIcon(kpiData.activeComplaints.trend)}
            </div>
            <h3 className="text-sm font-medium text-gray-600 mb-1">Active Complaints</h3>
            <p className="text-3xl font-bold text-gray-900 mb-2">{formatNumber(kpiData.activeComplaints.value)}</p>
            <p className={`text-sm font-medium ${getTrendColor(kpiData.activeComplaints.trend, kpiData.activeComplaints.change)}`}>
              {kpiData.activeComplaints.change > 0 ? '+' : ''}{kpiData.activeComplaints.change}% from last period
            </p>
          </div>

          {/* Avg Resolution Time */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="p-3 bg-yellow-50 rounded-lg">
                <Clock className="w-6 h-6 text-yellow-600" />
              </div>
              {getTrendIcon(kpiData.avgResolutionTime.trend)}
            </div>
            <h3 className="text-sm font-medium text-gray-600 mb-1">Avg Resolution Time</h3>
            <p className="text-3xl font-bold text-gray-900 mb-2">{kpiData.avgResolutionTime.value}h</p>
            <p className={`text-sm font-medium ${getTrendColor(kpiData.avgResolutionTime.trend, kpiData.avgResolutionTime.change)}`}>
              {kpiData.avgResolutionTime.change > 0 ? '+' : ''}{kpiData.avgResolutionTime.change}% from last period
            </p>
          </div>

          {/* Customer Satisfaction */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="p-3 bg-purple-50 rounded-lg">
                <CheckCircle className="w-6 h-6 text-purple-600" />
              </div>
              {getTrendIcon(kpiData.customerSatisfaction.trend)}
            </div>
            <h3 className="text-sm font-medium text-gray-600 mb-1">Customer Satisfaction</h3>
            <p className="text-3xl font-bold text-gray-900 mb-2">{kpiData.customerSatisfaction.value}/5.0</p>
            <p className={`text-sm font-medium ${getTrendColor(kpiData.customerSatisfaction.trend, kpiData.customerSatisfaction.change)}`}>
              {kpiData.customerSatisfaction.change > 0 ? '+' : ''}{kpiData.customerSatisfaction.change}% from last period
            </p>
          </div>

          {/* Staff Utilization */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="p-3 bg-indigo-50 rounded-lg">
                <Users className="w-6 h-6 text-indigo-600" />
              </div>
              {getTrendIcon(kpiData.staffUtilization.trend)}
            </div>
            <h3 className="text-sm font-medium text-gray-600 mb-1">Staff Utilization</h3>
            <p className="text-3xl font-bold text-gray-900 mb-2">{kpiData.staffUtilization.value}%</p>
            <p className={`text-sm font-medium ${getTrendColor(kpiData.staffUtilization.trend, kpiData.staffUtilization.change)}`}>
              {kpiData.staffUtilization.change > 0 ? '+' : ''}{kpiData.staffUtilization.change}% from last period
            </p>
          </div>
        </div>

        {/* Charts Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
          {/* Bookings & Revenue Trend */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Bookings & Revenue Trend</h3>
            <ResponsiveContainer width="100%" height={300}>
              <AreaChart data={trendData}>
                <defs>
                  <linearGradient id="colorBookings" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor={COLORS.primary} stopOpacity={0.8}/>
                    <stop offset="95%" stopColor={COLORS.primary} stopOpacity={0}/>
                  </linearGradient>
                  <linearGradient id="colorRevenue" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor={COLORS.success} stopOpacity={0.8}/>
                    <stop offset="95%" stopColor={COLORS.success} stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis dataKey="date" stroke="#9CA3AF" style={{ fontSize: '12px' }} />
                <YAxis stroke="#9CA3AF" style={{ fontSize: '12px' }} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#fff',
                    border: '1px solid #e5e7eb',
                    borderRadius: '8px',
                    boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
                  }}
                />
                <Legend />
                <Area
                  type="monotone"
                  dataKey="bookings"
                  stroke={COLORS.primary}
                  fillOpacity={1}
                  fill="url(#colorBookings)"
                  name="Bookings"
                />
                <Area
                  type="monotone"
                  dataKey="revenue"
                  stroke={COLORS.success}
                  fillOpacity={1}
                  fill="url(#colorRevenue)"
                  name="Revenue (₹100s)"
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>

          {/* Service Category Distribution */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Service Category Distribution</h3>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={categoryData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percentage }) => `${name} ${percentage}%`}
                  outerRadius={100}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {categoryData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={PIE_COLORS[index % PIE_COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#fff',
                    border: '1px solid #e5e7eb',
                    borderRadius: '8px',
                    boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
                  }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Additional Charts */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Booking Status Distribution */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Booking Status Distribution</h3>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={statusDistribution}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis dataKey="name" stroke="#9CA3AF" style={{ fontSize: '12px' }} />
                <YAxis stroke="#9CA3AF" style={{ fontSize: '12px' }} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#fff',
                    border: '1px solid #e5e7eb',
                    borderRadius: '8px',
                    boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
                  }}
                />
                <Bar dataKey="value" radius={[8, 8, 0, 0]}>
                  {statusDistribution.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* Performance Metrics */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Performance vs Target</h3>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={performanceData} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis type="number" domain={[0, 100]} stroke="#9CA3AF" style={{ fontSize: '12px' }} />
                <YAxis dataKey="metric" type="category" width={120} stroke="#9CA3AF" style={{ fontSize: '12px' }} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#fff',
                    border: '1px solid #e5e7eb',
                    borderRadius: '8px',
                    boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
                  }}
                />
                <Legend />
                <Bar dataKey="current" fill={COLORS.primary} radius={[0, 4, 4, 0]} name="Current" />
                <Bar dataKey="target" fill={COLORS.secondary} radius={[0, 4, 4, 0]} name="Target" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AnalyticsPage;

