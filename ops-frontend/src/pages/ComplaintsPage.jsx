import React, { useState, useEffect, useCallback } from 'react';
import { 
  Search, Filter, RefreshCw, Eye, UserCheck, CheckCircle, 
  Clock, AlertTriangle, MessageSquare, Calendar, User,
  ChevronDown, ChevronRight, X, Plus, Edit3, FileText
} from 'lucide-react';
import api from '../services/api';
import ComplaintDetailModal from '../components/complaints/ComplaintDetailModal';
import ComplaintFilters from '../components/complaints/ComplaintFilters';
import ComplaintStatusBadge from '../components/complaints/ComplaintStatusBadge';
import ComplaintPriorityBadge from '../components/complaints/ComplaintPriorityBadge';

const ComplaintsPage = () => {
  // State management
  const [complaints, setComplaints] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedComplaint, setSelectedComplaint] = useState(null);
  const [showDetailModal, setShowDetailModal] = useState(false);
  const [showFilters, setShowFilters] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalComplaints, setTotalComplaints] = useState(0);
  const [lastUpdated, setLastUpdated] = useState(new Date());

  // Filter state
  const [filters, setFilters] = useState({
    status: 'all',
    priority: 'all',
    complaint_type: 'all',
    assigned_to: null,
    sla_risk: null,
    date_from: null,
    date_to: null,
    sort_by: 'created_at',
    sort_order: 'desc'
  });

  // Fetch complaints data
  const fetchComplaints = useCallback(async (page = 1, searchQuery = '', filterParams = {}) => {
    try {
      setLoading(true);
      setError(null);

      const params = {
        skip: (page - 1) * 20,
        limit: 20,
        ...filterParams,
        ...(searchQuery && { search: searchQuery })
      };

      // Remove null/undefined values
      Object.keys(params).forEach(key => {
        if (params[key] === null || params[key] === undefined || params[key] === 'all') {
          delete params[key];
        }
      });

      const response = await api.complaints.getComplaints(params);

      // Handle both success format and direct format
      if (response.data.success || response.data.complaints) {
        setComplaints(response.data.complaints || []);
        setTotalComplaints(response.data.total || 0);
        setTotalPages(Math.ceil((response.data.total || 0) / 20));
        setLastUpdated(new Date());
      } else {
        throw new Error(response.data.message || 'Failed to fetch complaints');
      }
    } catch (err) {
      console.error('Error fetching complaints:', err);
      setError(err.message || 'Failed to load complaints');
      setComplaints([]);
    } finally {
      setLoading(false);
    }
  }, []);

  // Initial load
  useEffect(() => {
    fetchComplaints(currentPage, searchTerm, filters);
  }, [fetchComplaints, currentPage, filters]);

  // Search handler
  const handleSearch = useCallback((query) => {
    setSearchTerm(query);
    setCurrentPage(1);
    fetchComplaints(1, query, filters);
  }, [fetchComplaints, filters]);

  // Filter handler
  const handleFilterChange = useCallback((newFilters) => {
    setFilters(newFilters);
    setCurrentPage(1);
    fetchComplaints(1, searchTerm, newFilters);
  }, [fetchComplaints, searchTerm]);

  // View complaint details
  const handleViewComplaint = async (complaintId) => {
    try {
      const response = await api.complaints.getComplaint(complaintId);
      // Backend returns ComplaintResponse directly, not wrapped in {success: true, complaint: {...}}
      if (response.data) {
        setSelectedComplaint(response.data);
        setShowDetailModal(true);
      }
    } catch (err) {
      console.error('Error fetching complaint details:', err);
    }
  };

  // Refresh data
  const handleRefresh = () => {
    fetchComplaints(currentPage, searchTerm, filters);
  };

  // Pagination
  const handlePageChange = (page) => {
    setCurrentPage(page);
  };

  // Get priority color
  const getPriorityColor = (priority) => {
    const colors = {
      low: 'text-green-600 bg-green-50 border-green-200',
      medium: 'text-yellow-600 bg-yellow-50 border-yellow-200',
      high: 'text-orange-600 bg-orange-50 border-orange-200',
      critical: 'text-red-600 bg-red-50 border-red-200'
    };
    return colors[priority] || colors.medium;
  };

  // Get status color
  const getStatusColor = (status) => {
    const colors = {
      open: 'text-blue-600 bg-blue-50 border-blue-200',
      in_progress: 'text-yellow-600 bg-yellow-50 border-yellow-200',
      resolved: 'text-green-600 bg-green-50 border-green-200',
      closed: 'text-gray-600 bg-gray-50 border-gray-200',
      escalated: 'text-red-600 bg-red-50 border-red-200'
    };
    return colors[status] || colors.open;
  };

  // Format date
  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  // Loading state
  if (loading && complaints.length === 0) {
    return (
      <div className="min-h-full bg-transparent">
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <RefreshCw className="w-8 h-8 animate-spin text-blue-600 mx-auto mb-4" />
            <p className="text-gray-600">Loading complaints...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-full bg-transparent">
      {/* Header Section */}
      <div className="bg-gradient-to-r from-white via-blue-50/30 to-indigo-50/20 border-b border-gray-200/50 backdrop-blur-sm">
        <div className="px-6 py-6">
          <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between space-y-4 lg:space-y-0">
            <div className="flex-1">
              <h1 className="text-2xl font-bold bg-gradient-to-r from-gray-900 via-blue-900 to-indigo-900 bg-clip-text text-transparent">
                Complaints Management
              </h1>
              <p className="text-gray-600 text-base mt-1">
                Manage and resolve customer complaints efficiently
              </p>
            </div>
            
            <div className="flex items-center space-x-4">
              <div className="text-right">
                <p className="text-xs font-medium text-gray-700">Last updated</p>
                <p className="text-base font-semibold text-blue-600">
                  {lastUpdated.toLocaleTimeString()}
                </p>
              </div>
              <button
                onClick={handleRefresh}
                className="btn-primary flex items-center space-x-2 group text-sm px-3 py-2"
                disabled={loading}
              >
                <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : 'group-hover:rotate-180'} transition-transform duration-300`} />
                <span>Refresh</span>
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Search and Filters Section */}
      <div className="px-6 py-4 bg-white border-b border-gray-200/50">
        <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between space-y-4 lg:space-y-0">
          <div className="flex items-center space-x-4 flex-1">
            <div className="relative flex-1 max-w-md">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input
                type="text"
                placeholder="Search complaints by subject, description, or user..."
                value={searchTerm}
                onChange={(e) => handleSearch(e.target.value)}
                className="w-full pl-10 pr-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
              />
            </div>
            <button
              onClick={() => setShowFilters(!showFilters)}
              className={`flex items-center space-x-2 px-4 py-2.5 rounded-lg font-medium transition-all duration-200 text-sm ${
                showFilters ? 'btn-primary' : 'btn-secondary'
              }`}
            >
              <Filter className="w-4 h-4" />
              <span>Filters</span>
              {showFilters ? <ChevronDown className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
            </button>
          </div>
          
          <div className="flex items-center space-x-4">
            <div className="text-sm text-gray-600">
              <span className="font-medium">{totalComplaints}</span> complaints found
            </div>
          </div>
        </div>

        {/* Filters Panel */}
        {showFilters && (
          <div className="mt-4 pt-4 border-t border-gray-200/50">
            <ComplaintFilters
              filters={filters}
              onFilterChange={handleFilterChange}
              onClose={() => setShowFilters(false)}
            />
          </div>
        )}
      </div>

      {/* Error State */}
      {error && (
        <div className="px-6 py-4">
          <div className="bg-red-50 border border-red-200 rounded-lg p-4">
            <div className="flex items-center space-x-3">
              <AlertTriangle className="w-5 h-5 text-red-600" />
              <div>
                <p className="text-red-800 font-medium">Error loading complaints</p>
                <p className="text-red-600 text-sm mt-1">{error}</p>
              </div>
            </div>
            <button
              onClick={handleRefresh}
              className="mt-3 btn-primary text-sm px-4 py-2"
            >
              Try Again
            </button>
          </div>
        </div>
      )}

      {/* Complaints List */}
      <div className="px-6 py-4">
        {complaints.length === 0 && !loading ? (
          <div className="text-center py-12">
            <MessageSquare className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No complaints found</h3>
            <p className="text-gray-600">
              {searchTerm || Object.values(filters).some(f => f && f !== 'all') 
                ? 'Try adjusting your search or filters' 
                : 'No complaints have been submitted yet'}
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            {complaints.map((complaint) => (
              <ComplaintCard
                key={complaint.id}
                complaint={complaint}
                onView={() => handleViewComplaint(complaint.id)}
                getPriorityColor={getPriorityColor}
                getStatusColor={getStatusColor}
                formatDate={formatDate}
              />
            ))}
          </div>
        )}
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="px-6 py-4 border-t border-gray-200/50">
          <div className="flex items-center justify-between">
            <div className="text-sm text-gray-600">
              Showing {((currentPage - 1) * 20) + 1} to {Math.min(currentPage * 20, totalComplaints)} of {totalComplaints} complaints
            </div>
            <div className="flex items-center space-x-2">
              <button
                onClick={() => handlePageChange(currentPage - 1)}
                disabled={currentPage === 1}
                className="px-3 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Previous
              </button>
              {[...Array(Math.min(5, totalPages))].map((_, i) => {
                const page = i + 1;
                return (
                  <button
                    key={page}
                    onClick={() => handlePageChange(page)}
                    className={`px-3 py-2 text-sm font-medium rounded-md ${
                      currentPage === page
                        ? 'bg-blue-600 text-white'
                        : 'text-gray-700 bg-white border border-gray-300 hover:bg-gray-50'
                    }`}
                  >
                    {page}
                  </button>
                );
              })}
              <button
                onClick={() => handlePageChange(currentPage + 1)}
                disabled={currentPage === totalPages}
                className="px-3 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Next
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Complaint Detail Modal */}
      {showDetailModal && selectedComplaint && (
        <ComplaintDetailModal
          complaint={selectedComplaint}
          onClose={() => {
            setShowDetailModal(false);
            setSelectedComplaint(null);
          }}
          onUpdate={() => {
            handleRefresh();
            setShowDetailModal(false);
            setSelectedComplaint(null);
          }}
        />
      )}
    </div>
  );
};

// Complaint Card Component
const ComplaintCard = ({ complaint, onView, getPriorityColor, getStatusColor, formatDate }) => {
  return (
    <div className="bg-gradient-to-r from-white via-white to-gray-50/30 rounded-xl border border-gray-200/60 hover:shadow-lg hover:border-gray-300/60 transition-all duration-200 group hover:scale-[1.01]">
      <div className="p-4">
        <div className="flex items-start justify-between">
          <div className="flex-1 min-w-0">
            <div className="flex items-center space-x-3 mb-2">
              <h3 className="text-base font-semibold text-gray-900 group-hover:text-blue-600 transition-colors truncate">
                #{complaint.id} - {complaint.subject}
              </h3>
              <div className="flex items-center space-x-2">
                <span className={`px-2 py-1 rounded-md text-xs font-medium border ${getPriorityColor(complaint.priority)}`}>
                  {complaint.priority.toUpperCase()}
                </span>
                <span className={`px-2 py-1 rounded-md text-xs font-medium border ${getStatusColor(complaint.status)}`}>
                  {complaint.status.replace('_', ' ').toUpperCase()}
                </span>
                {complaint.sla_breach_risk && (
                  <span className="px-2 py-1 rounded-md text-xs font-medium bg-red-100 text-red-700 border border-red-200">
                    SLA RISK
                  </span>
                )}
              </div>
            </div>
            
            <p className="text-sm text-gray-600 mb-3 line-clamp-2">
              {complaint.description}
            </p>
            
            <div className="flex items-center space-x-6 text-xs text-gray-500">
              <div className="flex items-center space-x-1">
                <User className="w-3 h-3" />
                <span>{complaint.user_info?.name || 'Unknown User'}</span>
              </div>
              <div className="flex items-center space-x-1">
                <Calendar className="w-3 h-3" />
                <span>{formatDate(complaint.created_at)}</span>
              </div>
              {complaint.assigned_to_staff && (
                <div className="flex items-center space-x-1">
                  <UserCheck className="w-3 h-3" />
                  <span>Assigned to {complaint.assigned_to_staff.name}</span>
                </div>
              )}
              {complaint.updates_count > 0 && (
                <div className="flex items-center space-x-1">
                  <MessageSquare className="w-3 h-3" />
                  <span>{complaint.updates_count} updates</span>
                </div>
              )}
            </div>
          </div>
          
          <div className="ml-4 flex-shrink-0">
            <button
              onClick={onView}
              className="btn-primary text-sm px-4 py-2 flex items-center space-x-2"
            >
              <Eye className="w-4 h-4" />
              <span>View</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ComplaintsPage;
