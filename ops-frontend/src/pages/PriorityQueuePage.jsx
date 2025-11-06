import React, { useState, useEffect } from 'react';
import { 
  Clock, Filter, Search, AlertCircle, MessageSquare, 
  RefreshCw, Eye, CheckCircle, XCircle, User, Calendar,
  TrendingUp, AlertTriangle, DollarSign, X
} from 'lucide-react';
import api from '../services/api';

const PriorityQueuePage = () => {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedItem, setSelectedItem] = useState(null);
  const [showDetailModal, setShowDetailModal] = useState(false);
  const [pagination, setPagination] = useState({
    skip: 0,
    limit: 20,
    total: 0,
    hasMore: false
  });

  const [filters, setFilters] = useState({
    status: 'pending',
    intentType: 'all',
    priorityMin: null,
    priorityMax: null,
    sortBy: 'priority_score',
    sortOrder: 'desc',
    searchQuery: ''
  });

  useEffect(() => {
    fetchPriorityQueue();
  }, [filters, pagination.skip]);

  const fetchPriorityQueue = async () => {
    setLoading(true);
    try {
      const params = {
        status: filters.status,
        skip: pagination.skip,
        limit: pagination.limit,
        sort_by: filters.sortBy,
        sort_order: filters.sortOrder
      };

      if (filters.intentType && filters.intentType !== 'all') {
        params.intent_type = filters.intentType;
      }
      if (filters.priorityMin) params.priority_min = filters.priorityMin;
      if (filters.priorityMax) params.priority_max = filters.priorityMax;

      const response = await api.dashboard.getPriorityQueue(params);
      setItems(response.data.items || []);
      setPagination(prev => ({
        ...prev,
        total: response.data.total || 0,
        hasMore: response.data.has_more || false
      }));
    } catch (error) {
      console.error('Error fetching priority queue:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleViewDetails = (item) => {
    setSelectedItem(item);
    setShowDetailModal(true);
  };

  const handleReview = async (itemId, action) => {
    try {
      await api.priorityQueue.review(itemId, { action });
      fetchPriorityQueue();
      setShowDetailModal(false);
    } catch (error) {
      console.error('Error reviewing item:', error);
      alert('Failed to review item');
    }
  };

  const getPriorityColor = (score) => {
    if (score >= 80) return 'text-red-600 bg-red-50 border-red-200';
    if (score >= 60) return 'text-orange-600 bg-orange-50 border-orange-200';
    if (score >= 40) return 'text-yellow-600 bg-yellow-50 border-yellow-200';
    return 'text-green-600 bg-green-50 border-green-200';
  };

  const getIntentIcon = (intentType) => {
    switch (intentType) {
      case 'complaint':
        return <AlertCircle className="w-4 h-4" />;
      case 'booking':
        return <Calendar className="w-4 h-4" />;
      case 'refund':
        return <DollarSign className="w-4 h-4" />;
      case 'cancellation':
        return <XCircle className="w-4 h-4" />;
      default:
        return <MessageSquare className="w-4 h-4" />;
    }
  };

  const getIntentColor = (intentType) => {
    switch (intentType) {
      case 'complaint':
        return 'bg-red-100 text-red-700 border-red-200';
      case 'booking':
        return 'bg-blue-100 text-blue-700 border-blue-200';
      case 'refund':
        return 'bg-yellow-100 text-yellow-700 border-yellow-200';
      case 'cancellation':
        return 'bg-gray-100 text-gray-700 border-gray-200';
      default:
        return 'bg-gray-100 text-gray-700 border-gray-200';
    }
  };

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Priority Queue</h1>
          <p className="text-sm text-gray-600 mt-1">
            {pagination.total} items • {items.filter(i => !i.is_reviewed).length} pending review
          </p>
        </div>
        <button
          onClick={fetchPriorityQueue}
          disabled={loading}
          className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-[#486581] to-[#5a7a9a] text-white rounded-lg hover:shadow-lg transition-all duration-200 hover:scale-105 disabled:opacity-50"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          Refresh
        </button>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Status</label>
            <select
              value={filters.status}
              onChange={(e) => setFilters({ ...filters, status: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#486581]"
            >
              <option value="pending">Pending</option>
              <option value="reviewed">Reviewed</option>
              <option value="all">All</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Intent Type</label>
            <select
              value={filters.intentType}
              onChange={(e) => setFilters({ ...filters, intentType: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#486581]"
            >
              <option value="all">All Types</option>
              <option value="complaint">Complaint</option>
              <option value="booking">Booking</option>
              <option value="refund">Refund</option>
              <option value="cancellation">Cancellation</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Sort By</label>
            <select
              value={filters.sortBy}
              onChange={(e) => setFilters({ ...filters, sortBy: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#486581]"
            >
              <option value="priority_score">Priority Score</option>
              <option value="created_at">Created Date</option>
              <option value="confidence_score">Confidence Score</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Order</label>
            <select
              value={filters.sortOrder}
              onChange={(e) => setFilters({ ...filters, sortOrder: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#486581]"
            >
              <option value="desc">Descending</option>
              <option value="asc">Ascending</option>
            </select>
          </div>
        </div>
      </div>

      {/* Priority Queue Table */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">Priority</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">Intent</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">Customer</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">Message</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">Confidence</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">Created</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">Status</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {loading ? (
                <tr>
                  <td colSpan="8" className="px-4 py-8 text-center text-gray-500">
                    <RefreshCw className="w-6 h-6 animate-spin mx-auto mb-2" />
                    Loading priority queue...
                  </td>
                </tr>
              ) : items.length === 0 ? (
                <tr>
                  <td colSpan="8" className="px-4 py-8 text-center text-gray-500">
                    No items in priority queue
                  </td>
                </tr>
              ) : (
                items.map((item) => (
                  <tr key={item.id} className="hover:bg-gray-50 transition-colors">
                    <td className="px-4 py-3">
                      <span className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-semibold border ${getPriorityColor(item.priority_score)}`}>
                        <TrendingUp className="w-3 h-3" />
                        {item.priority_score}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <span className={`inline-flex items-center gap-1 px-2 py-1 rounded-lg text-xs font-medium border ${getIntentColor(item.intent_type)}`}>
                        {getIntentIcon(item.intent_type)}
                        {item.intent_type}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-2">
                        <User className="w-4 h-4 text-gray-400" />
                        <div>
                          <div className="text-sm font-medium text-gray-900">{item.user_name || 'N/A'}</div>
                          <div className="text-xs text-gray-500">{item.user_email || 'N/A'}</div>
                        </div>
                      </div>
                    </td>
                    <td className="px-4 py-3">
                      <p className="text-sm text-gray-700 line-clamp-2 max-w-xs">
                        {item.message_snippet || 'No message'}
                      </p>
                    </td>
                    <td className="px-4 py-3">
                      <span className="text-sm text-gray-700">
                        {(item.confidence_score * 100).toFixed(0)}%
                      </span>
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-600">
                      {new Date(item.created_at).toLocaleDateString()}
                    </td>
                    <td className="px-4 py-3">
                      {item.is_reviewed ? (
                        <span className="inline-flex items-center gap-1 px-2 py-1 bg-green-100 text-green-700 rounded-full text-xs font-medium">
                          <CheckCircle className="w-3 h-3" />
                          Reviewed
                        </span>
                      ) : (
                        <span className="inline-flex items-center gap-1 px-2 py-1 bg-yellow-100 text-yellow-700 rounded-full text-xs font-medium">
                          <Clock className="w-3 h-3" />
                          Pending
                        </span>
                      )}
                    </td>
                    <td className="px-4 py-3">
                      <button
                        onClick={() => handleViewDetails(item)}
                        className="p-1.5 text-blue-600 hover:bg-blue-50 rounded transition-colors"
                        title="View Details"
                      >
                        <Eye className="w-4 h-4" />
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        {pagination.total > pagination.limit && (
          <div className="px-4 py-3 border-t border-gray-200 flex items-center justify-between">
            <div className="text-sm text-gray-700">
              Showing {pagination.skip + 1} to {Math.min(pagination.skip + pagination.limit, pagination.total)} of {pagination.total} items
            </div>
            <div className="flex gap-2">
              <button
                onClick={() => setPagination(prev => ({ ...prev, skip: Math.max(0, prev.skip - prev.limit) }))}
                disabled={pagination.skip === 0}
                className="px-3 py-1 border border-gray-300 rounded-lg text-sm hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Previous
              </button>
              <button
                onClick={() => setPagination(prev => ({ ...prev, skip: prev.skip + prev.limit }))}
                disabled={!pagination.hasMore}
                className="px-3 py-1 border border-gray-300 rounded-lg text-sm hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Next
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Detail Modal - Placeholder for now */}
      {showDetailModal && selectedItem && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex justify-between items-start mb-4">
                <h2 className="text-xl font-bold text-gray-900">Priority Queue Item Details</h2>
                <button
                  onClick={() => setShowDetailModal(false)}
                  className="p-1 hover:bg-gray-100 rounded transition-colors"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>
              
              <div className="space-y-4">
                <div>
                  <label className="text-sm font-medium text-gray-700">Priority Score</label>
                  <p className="text-lg font-semibold text-gray-900">{selectedItem.priority_score}</p>
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-700">Intent Type</label>
                  <p className="text-gray-900">{selectedItem.intent_type}</p>
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-700">Message</label>
                  <p className="text-gray-900">{selectedItem.message_snippet}</p>
                </div>
                
                {!selectedItem.is_reviewed && (
                  <div className="flex gap-2 pt-4">
                    <button
                      onClick={() => handleReview(selectedItem.id, 'resolved')}
                      className="flex-1 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
                    >
                      Mark as Resolved
                    </button>
                    <button
                      onClick={() => handleReview(selectedItem.id, 'escalate')}
                      className="flex-1 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
                    >
                      Escalate
                    </button>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default PriorityQueuePage;

