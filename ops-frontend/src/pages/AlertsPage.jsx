import React, { useState, useEffect } from 'react';
import { 
  Bell, AlertTriangle, AlertCircle, Info, CheckCircle, 
  X, Eye, Trash2, RefreshCw, Filter, Clock, TrendingUp,
  Users, DollarSign, Calendar, Settings
} from 'lucide-react';
import api from '../services/api';

const AlertsPage = () => {
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedAlert, setSelectedAlert] = useState(null);
  const [showDetailModal, setShowDetailModal] = useState(false);

  const [filters, setFilters] = useState({
    severity: 'all',
    status: 'unread',
    type: 'all'
  });

  useEffect(() => {
    fetchAlerts();
  }, [filters]);

  const fetchAlerts = async () => {
    setLoading(true);
    try {
      // Build query parameters
      const params = {
        unread_only: filters.status === 'unread',
        page: 1,
        page_size: 50
      };

      if (filters.severity !== 'all') {
        params.severities = filters.severity;
      }

      if (filters.type !== 'all') {
        params.alert_types = filters.type;
      }

      const response = await api.alerts.getList(params);
      setAlerts(response.data.alerts || []);
    } catch (error) {
      console.error('Error fetching alerts:', error);
      setAlerts([]);
    } finally {
      setLoading(false);
    }
  };

  const handleMarkAsRead = async (alertId) => {
    try {
      await api.alerts.markAsRead(alertId);
      // Update local state
      setAlerts(alerts.map(a => a.id === alertId ? { ...a, is_read: true } : a));
    } catch (error) {
      console.error('Error marking alert as read:', error);
      alert('Failed to mark alert as read. Please try again.');
    }
  };

  const handleDismiss = async (alertId) => {
    try {
      await api.alerts.dismiss(alertId);
      // Remove from local state
      setAlerts(alerts.filter(a => a.id !== alertId));
    } catch (error) {
      console.error('Error dismissing alert:', error);
      alert('Failed to dismiss alert. Please try again.');
    }
  };

  const handleViewDetails = (alert) => {
    setSelectedAlert(alert);
    setShowDetailModal(true);
    if (!alert.is_read) {
      handleMarkAsRead(alert.id);
    }
  };

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'critical':
        return 'bg-red-100 text-red-700 border-red-200';
      case 'high':
        return 'bg-orange-100 text-orange-700 border-orange-200';
      case 'medium':
        return 'bg-yellow-100 text-yellow-700 border-yellow-200';
      case 'low':
        return 'bg-blue-100 text-blue-700 border-blue-200';
      case 'info':
        return 'bg-green-100 text-green-700 border-green-200';
      default:
        return 'bg-gray-100 text-gray-700 border-gray-200';
    }
  };

  const getSeverityIcon = (severity) => {
    switch (severity) {
      case 'critical':
        return <AlertTriangle className="w-4 h-4" />;
      case 'high':
        return <AlertCircle className="w-4 h-4" />;
      case 'medium':
        return <Bell className="w-4 h-4" />;
      case 'low':
        return <Info className="w-4 h-4" />;
      case 'info':
        return <CheckCircle className="w-4 h-4" />;
      default:
        return <Bell className="w-4 h-4" />;
    }
  };

  const getTypeIcon = (type) => {
    switch (type) {
      case 'complaint':
        return <AlertCircle className="w-5 h-5" />;
      case 'sla':
        return <Clock className="w-5 h-5" />;
      case 'revenue':
        return <DollarSign className="w-5 h-5" />;
      case 'staff':
        return <Users className="w-5 h-5" />;
      case 'system':
        return <Settings className="w-5 h-5" />;
      default:
        return <Bell className="w-5 h-5" />;
    }
  };

  const getTimeAgo = (dateString) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    return `${diffDays}d ago`;
  };

  const unreadCount = alerts.filter(a => !a.is_read).length;

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Alerts & Notifications</h1>
          <p className="text-sm text-gray-600 mt-1">
            {alerts.length} total alerts • {unreadCount} unread
          </p>
        </div>
        <button
          onClick={fetchAlerts}
          disabled={loading}
          className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-[#486581] to-[#5a7a9a] text-white rounded-lg hover:shadow-lg transition-all duration-200 hover:scale-105 disabled:opacity-50"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          Refresh
        </button>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Severity</label>
            <select
              value={filters.severity}
              onChange={(e) => setFilters({ ...filters, severity: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#486581]"
            >
              <option value="all">All Severities</option>
              <option value="critical">Critical</option>
              <option value="high">High</option>
              <option value="medium">Medium</option>
              <option value="low">Low</option>
              <option value="info">Info</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Status</label>
            <select
              value={filters.status}
              onChange={(e) => setFilters({ ...filters, status: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#486581]"
            >
              <option value="all">All Status</option>
              <option value="unread">Unread</option>
              <option value="read">Read</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Type</label>
            <select
              value={filters.type}
              onChange={(e) => setFilters({ ...filters, type: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#486581]"
            >
              <option value="all">All Types</option>
              <option value="complaint">Complaint</option>
              <option value="sla">SLA</option>
              <option value="revenue">Revenue</option>
              <option value="staff">Staff</option>
              <option value="system">System</option>
            </select>
          </div>
        </div>
      </div>

      {/* Alerts List */}
      <div className="space-y-3">
        {loading ? (
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-8 text-center">
            <RefreshCw className="w-8 h-8 animate-spin mx-auto mb-2 text-[#486581]" />
            <p className="text-gray-500">Loading alerts...</p>
          </div>
        ) : alerts.length === 0 ? (
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-8 text-center">
            <Bell className="w-12 h-12 mx-auto mb-3 text-gray-400" />
            <p className="text-gray-500">No alerts found</p>
          </div>
        ) : (
          alerts.map((alert) => (
            <div
              key={alert.id}
              className={`bg-white rounded-xl shadow-sm border transition-all duration-200 hover:shadow-md ${
                !alert.is_read ? 'border-[#486581] border-l-4' : 'border-gray-200'
              }`}
            >
              <div className="p-4">
                <div className="flex items-start gap-4">
                  <div className={`p-3 rounded-lg ${getSeverityColor(alert.severity)}`}>
                    {getTypeIcon(alert.type)}
                  </div>

                  <div className="flex-1 min-w-0">
                    <div className="flex items-start justify-between gap-2 mb-2">
                      <div className="flex-1">
                        <h3 className="font-semibold text-gray-900 mb-1">{alert.title}</h3>
                        <p className="text-sm text-gray-600">{alert.message}</p>
                      </div>
                      <span className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium border whitespace-nowrap ${getSeverityColor(alert.severity)}`}>
                        {getSeverityIcon(alert.severity)}
                        {alert.severity}
                      </span>
                    </div>

                    <div className="flex items-center gap-4 text-xs text-gray-500">
                      <span className="flex items-center gap-1">
                        <Clock className="w-3 h-3" />
                        {getTimeAgo(alert.created_at)}
                      </span>
                      <span className="capitalize">{alert.type}</span>
                      {!alert.is_read && (
                        <span className="px-2 py-0.5 bg-blue-100 text-blue-700 rounded-full font-medium">
                          New
                        </span>
                      )}
                    </div>
                  </div>

                  <div className="flex gap-1">
                    <button
                      onClick={() => handleViewDetails(alert)}
                      className="p-2 text-blue-600 hover:bg-blue-50 rounded transition-colors"
                      title="View Details"
                    >
                      <Eye className="w-4 h-4" />
                    </button>
                    <button
                      onClick={() => handleDismiss(alert.id)}
                      className="p-2 text-red-600 hover:bg-red-50 rounded transition-colors"
                      title="Dismiss"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Detail Modal */}
      {showDetailModal && selectedAlert && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex justify-between items-start mb-6">
                <div className="flex items-start gap-3">
                  <div className={`p-3 rounded-lg ${getSeverityColor(selectedAlert.severity)}`}>
                    {getTypeIcon(selectedAlert.type)}
                  </div>
                  <div>
                    <h2 className="text-xl font-bold text-gray-900">{selectedAlert.title}</h2>
                    <p className="text-sm text-gray-600 mt-1">{getTimeAgo(selectedAlert.created_at)}</p>
                  </div>
                </div>
                <button
                  onClick={() => setShowDetailModal(false)}
                  className="p-1 hover:bg-gray-100 rounded transition-colors"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>

              <div className="space-y-4">
                <div>
                  <label className="text-sm font-medium text-gray-700">Message</label>
                  <p className="text-gray-900 mt-1">{selectedAlert.message}</p>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="text-sm font-medium text-gray-700">Severity</label>
                    <span className={`inline-flex items-center gap-1 px-2 py-1 rounded-lg text-xs font-medium border mt-1 ${getSeverityColor(selectedAlert.severity)}`}>
                      {getSeverityIcon(selectedAlert.severity)}
                      {selectedAlert.severity}
                    </span>
                  </div>

                  <div>
                    <label className="text-sm font-medium text-gray-700">Type</label>
                    <p className="text-gray-900 mt-1 capitalize">{selectedAlert.type}</p>
                  </div>

                  <div>
                    <label className="text-sm font-medium text-gray-700">Status</label>
                    <p className="text-gray-900 mt-1 capitalize">{selectedAlert.is_read ? 'Read' : 'Unread'}</p>
                  </div>

                  <div>
                    <label className="text-sm font-medium text-gray-700">Created</label>
                    <p className="text-gray-900 mt-1">{new Date(selectedAlert.created_at).toLocaleString()}</p>
                  </div>
                </div>

                {selectedAlert.metadata && Object.keys(selectedAlert.metadata).length > 0 && (
                  <div>
                    <label className="text-sm font-medium text-gray-700">Additional Information</label>
                    <div className="mt-2 bg-gray-50 rounded-lg p-3 space-y-1">
                      {Object.entries(selectedAlert.metadata).map(([key, value]) => (
                        <div key={key} className="flex justify-between text-sm">
                          <span className="text-gray-600 capitalize">{key.replace(/_/g, ' ')}:</span>
                          <span className="text-gray-900 font-medium">{value}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                <div className="flex gap-2 pt-4 border-t border-gray-200">
                  <button
                    onClick={() => {
                      handleDismiss(selectedAlert.id);
                      setShowDetailModal(false);
                    }}
                    className="flex-1 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
                  >
                    Dismiss Alert
                  </button>
                  <button
                    onClick={() => setShowDetailModal(false)}
                    className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
                  >
                    Close
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AlertsPage;

