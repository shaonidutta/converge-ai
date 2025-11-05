import React, { useState, useEffect } from 'react';
import { X, Calendar, User, AlertTriangle, Filter } from 'lucide-react';
import api from '../../services/api';

const ComplaintFilters = ({ filters, onFilterChange, onClose }) => {
  const [localFilters, setLocalFilters] = useState(filters);
  const [staffList, setStaffList] = useState([]);
  const [complaintTypes, setComplaintTypes] = useState([]);

  useEffect(() => {
    fetchStaffList();
    fetchComplaintTypes();
  }, []);

  const fetchStaffList = async () => {
    try {
      const response = await api.staff.getStaffList({ active: true });
      if (response.data.success) {
        setStaffList(response.data.staff || []);
      }
    } catch (err) {
      console.error('Error fetching staff list:', err);
    }
  };

  const fetchComplaintTypes = async () => {
    // Mock complaint types - in real app, this would come from API
    setComplaintTypes([
      { value: 'service_quality', label: 'Service Quality' },
      { value: 'billing', label: 'Billing Issue' },
      { value: 'no_show', label: 'No Show' },
      { value: 'technical', label: 'Technical Issue' },
      { value: 'staff_behavior', label: 'Staff Behavior' },
      { value: 'other', label: 'Other' }
    ]);
  };

  const handleFilterChange = (key, value) => {
    setLocalFilters(prev => ({
      ...prev,
      [key]: value
    }));
  };

  const handleApplyFilters = () => {
    onFilterChange(localFilters);
  };

  const handleResetFilters = () => {
    const resetFilters = {
      status: 'all',
      priority: 'all',
      complaint_type: 'all',
      assigned_to: null,
      sla_risk: null,
      date_from: null,
      date_to: null,
      sort_by: 'created_at',
      sort_order: 'desc'
    };
    setLocalFilters(resetFilters);
    onFilterChange(resetFilters);
  };

  const formatDateForInput = (dateString) => {
    if (!dateString) return '';
    return new Date(dateString).toISOString().split('T')[0];
  };

  const handleDateChange = (key, value) => {
    const date = value ? new Date(value).toISOString() : null;
    handleFilterChange(key, date);
  };

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-2">
          <Filter className="w-5 h-5 text-gray-600" />
          <h3 className="text-lg font-semibold text-gray-900">Advanced Filters</h3>
        </div>
        <button
          onClick={onClose}
          className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
        >
          <X className="w-4 h-4 text-gray-500" />
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
        {/* Status Filter */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Status
          </label>
          <select
            value={localFilters.status}
            onChange={(e) => handleFilterChange('status', e.target.value)}
            className="w-full p-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
          >
            <option value="all">All Statuses</option>
            <option value="open">Open</option>
            <option value="in_progress">In Progress</option>
            <option value="resolved">Resolved</option>
            <option value="closed">Closed</option>
            <option value="escalated">Escalated</option>
          </select>
        </div>

        {/* Priority Filter */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Priority
          </label>
          <select
            value={localFilters.priority}
            onChange={(e) => handleFilterChange('priority', e.target.value)}
            className="w-full p-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
          >
            <option value="all">All Priorities</option>
            <option value="low">Low</option>
            <option value="medium">Medium</option>
            <option value="high">High</option>
            <option value="critical">Critical</option>
          </select>
        </div>

        {/* Complaint Type Filter */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Complaint Type
          </label>
          <select
            value={localFilters.complaint_type}
            onChange={(e) => handleFilterChange('complaint_type', e.target.value)}
            className="w-full p-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
          >
            <option value="all">All Types</option>
            {complaintTypes.map((type) => (
              <option key={type.value} value={type.value}>
                {type.label}
              </option>
            ))}
          </select>
        </div>

        {/* Assigned To Filter */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Assigned To
          </label>
          <select
            value={localFilters.assigned_to || ''}
            onChange={(e) => handleFilterChange('assigned_to', e.target.value || null)}
            className="w-full p-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
          >
            <option value="">All Staff</option>
            <option value="unassigned">Unassigned</option>
            {staffList.map((staff) => (
              <option key={staff.id} value={staff.id}>
                {staff.name} - {staff.department}
              </option>
            ))}
          </select>
        </div>

        {/* SLA Risk Filter */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            SLA Risk
          </label>
          <select
            value={localFilters.sla_risk === null ? '' : localFilters.sla_risk.toString()}
            onChange={(e) => handleFilterChange('sla_risk', e.target.value === '' ? null : e.target.value === 'true')}
            className="w-full p-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
          >
            <option value="">All Complaints</option>
            <option value="true">SLA Risk Only</option>
            <option value="false">No SLA Risk</option>
          </select>
        </div>

        {/* Date From Filter */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Date From
          </label>
          <input
            type="date"
            value={formatDateForInput(localFilters.date_from)}
            onChange={(e) => handleDateChange('date_from', e.target.value)}
            className="w-full p-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
          />
        </div>

        {/* Date To Filter */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Date To
          </label>
          <input
            type="date"
            value={formatDateForInput(localFilters.date_to)}
            onChange={(e) => handleDateChange('date_to', e.target.value)}
            className="w-full p-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
          />
        </div>

        {/* Sort By Filter */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Sort By
          </label>
          <select
            value={localFilters.sort_by}
            onChange={(e) => handleFilterChange('sort_by', e.target.value)}
            className="w-full p-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
          >
            <option value="created_at">Created Date</option>
            <option value="priority">Priority</option>
            <option value="status">Status</option>
            <option value="response_due_at">Response Due</option>
            <option value="resolution_due_at">Resolution Due</option>
          </select>
        </div>

        {/* Sort Order Filter */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Sort Order
          </label>
          <select
            value={localFilters.sort_order}
            onChange={(e) => handleFilterChange('sort_order', e.target.value)}
            className="w-full p-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
          >
            <option value="desc">Newest First</option>
            <option value="asc">Oldest First</option>
          </select>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex items-center justify-between mt-6 pt-6 border-t border-gray-200">
        <div className="flex items-center space-x-2 text-sm text-gray-600">
          <AlertTriangle className="w-4 h-4" />
          <span>Filters are applied immediately</span>
        </div>
        
        <div className="flex items-center space-x-3">
          <button
            onClick={handleResetFilters}
            className="btn-secondary text-sm px-4 py-2"
          >
            Reset All
          </button>
          <button
            onClick={handleApplyFilters}
            className="btn-primary text-sm px-4 py-2"
          >
            Apply Filters
          </button>
        </div>
      </div>

      {/* Active Filters Summary */}
      <div className="mt-4 pt-4 border-t border-gray-200">
        <div className="flex flex-wrap gap-2">
          {Object.entries(localFilters).map(([key, value]) => {
            if (!value || value === 'all' || value === 'created_at' || value === 'desc') return null;
            
            let displayValue = value;
            if (key === 'assigned_to' && staffList.length > 0) {
              const staff = staffList.find(s => s.id.toString() === value.toString());
              displayValue = staff ? staff.name : value;
            }
            if (key === 'complaint_type' && complaintTypes.length > 0) {
              const type = complaintTypes.find(t => t.value === value);
              displayValue = type ? type.label : value;
            }
            if (key === 'sla_risk') {
              displayValue = value ? 'SLA Risk' : 'No SLA Risk';
            }
            if (key === 'date_from' || key === 'date_to') {
              displayValue = new Date(value).toLocaleDateString();
            }

            return (
              <span
                key={key}
                className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800"
              >
                {key.replace('_', ' ')}: {displayValue}
                <button
                  onClick={() => handleFilterChange(key, key === 'assigned_to' ? null : key === 'sla_risk' ? null : 'all')}
                  className="ml-2 hover:bg-blue-200 rounded-full p-0.5"
                >
                  <X className="w-3 h-3" />
                </button>
              </span>
            );
          })}
        </div>
      </div>
    </div>
  );
};

export default ComplaintFilters;
