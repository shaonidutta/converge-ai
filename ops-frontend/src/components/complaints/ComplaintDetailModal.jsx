import React, { useState, useEffect } from 'react';
import { 
  X, User, Calendar, Clock, AlertTriangle, CheckCircle, 
  UserCheck, MessageSquare, Edit3, Save, FileText, Phone,
  Mail, MapPin, Package, DollarSign, RefreshCw, Plus
} from 'lucide-react';
import { api } from '../../services/api';

const ComplaintDetailModal = ({ complaint, onClose, onUpdate }) => {
  const [loading, setLoading] = useState(false);
  const [updates, setUpdates] = useState([]);
  const [showUpdateForm, setShowUpdateForm] = useState(false);
  const [showAssignForm, setShowAssignForm] = useState(false);
  const [showResolveForm, setShowResolveForm] = useState(false);
  const [newUpdate, setNewUpdate] = useState('');
  const [isInternal, setIsInternal] = useState(false);
  const [assignToStaff, setAssignToStaff] = useState('');
  const [assignNotes, setAssignNotes] = useState('');
  const [resolutionText, setResolutionText] = useState('');
  const [resolutionStatus, setResolutionStatus] = useState('resolved');
  const [staffList, setStaffList] = useState([]);

  // Fetch complaint updates
  useEffect(() => {
    if (complaint?.id) {
      fetchUpdates();
      fetchStaffList();
    }
  }, [complaint?.id]);

  const fetchUpdates = async () => {
    try {
      const response = await api.complaints.getUpdates(complaint.id);
      if (response.data.success) {
        setUpdates(response.data.updates || []);
      }
    } catch (err) {
      console.error('Error fetching updates:', err);
    }
  };

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

  // Add update
  const handleAddUpdate = async () => {
    if (!newUpdate.trim()) return;

    try {
      setLoading(true);
      const response = await api.complaints.addUpdate(complaint.id, {
        comment: newUpdate,
        is_internal: isInternal
      });

      if (response.data.success) {
        setNewUpdate('');
        setIsInternal(false);
        setShowUpdateForm(false);
        await fetchUpdates();
      }
    } catch (err) {
      console.error('Error adding update:', err);
    } finally {
      setLoading(false);
    }
  };

  // Assign complaint
  const handleAssign = async () => {
    if (!assignToStaff) return;

    try {
      setLoading(true);
      const response = await api.complaints.assign(complaint.id, {
        assigned_to_staff_id: parseInt(assignToStaff),
        notes: assignNotes
      });

      if (response.data.success) {
        setAssignToStaff('');
        setAssignNotes('');
        setShowAssignForm(false);
        onUpdate();
      }
    } catch (err) {
      console.error('Error assigning complaint:', err);
    } finally {
      setLoading(false);
    }
  };

  // Resolve complaint
  const handleResolve = async () => {
    if (!resolutionText.trim()) return;

    try {
      setLoading(true);
      const response = await api.complaints.resolve(complaint.id, {
        resolution: resolutionText,
        status: resolutionStatus
      });

      if (response.data.success) {
        setResolutionText('');
        setResolutionStatus('resolved');
        setShowResolveForm(false);
        onUpdate();
      }
    } catch (err) {
      console.error('Error resolving complaint:', err);
    } finally {
      setLoading(false);
    }
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

  if (!complaint) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white p-6">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-xl font-bold">Complaint #{complaint.id}</h2>
              <p className="text-blue-100 mt-1">{complaint.subject}</p>
            </div>
            <button
              onClick={onClose}
              className="p-2 hover:bg-white/20 rounded-lg transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
          
          <div className="flex items-center space-x-4 mt-4">
            <span className={`px-3 py-1 rounded-full text-sm font-medium ${getPriorityColor(complaint.priority)} bg-white/20 text-white border-white/30`}>
              {complaint.priority.toUpperCase()} PRIORITY
            </span>
            <span className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(complaint.status)} bg-white/20 text-white border-white/30`}>
              {complaint.status.replace('_', ' ').toUpperCase()}
            </span>
            {complaint.sla_breach_risk && (
              <span className="px-3 py-1 rounded-full text-sm font-medium bg-red-500/20 text-white border border-red-300/30">
                <AlertTriangle className="w-4 h-4 inline mr-1" />
                SLA RISK
              </span>
            )}
          </div>
        </div>

        {/* Content */}
        <div className="flex h-[calc(90vh-140px)]">
          {/* Left Panel - Complaint Details */}
          <div className="flex-1 p-6 overflow-y-auto border-r border-gray-200">
            {/* Description */}
            <div className="mb-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-3">Description</h3>
              <div className="bg-gray-50 rounded-lg p-4">
                <p className="text-gray-700 leading-relaxed">{complaint.description}</p>
              </div>
            </div>

            {/* Customer Information */}
            <div className="mb-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-3">Customer Information</h3>
              <div className="bg-gray-50 rounded-lg p-4 space-y-3">
                <div className="flex items-center space-x-3">
                  <User className="w-4 h-4 text-gray-500" />
                  <span className="font-medium text-gray-900">{complaint.user_info?.name || 'N/A'}</span>
                </div>
                <div className="flex items-center space-x-3">
                  <Mail className="w-4 h-4 text-gray-500" />
                  <span className="text-gray-700">{complaint.user_info?.email || 'N/A'}</span>
                </div>
                <div className="flex items-center space-x-3">
                  <Phone className="w-4 h-4 text-gray-500" />
                  <span className="text-gray-700">{complaint.user_info?.mobile || 'N/A'}</span>
                </div>
              </div>
            </div>

            {/* Booking Information */}
            {complaint.booking_info && (
              <div className="mb-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-3">Related Booking</h3>
                <div className="bg-gray-50 rounded-lg p-4 space-y-3">
                  <div className="flex items-center space-x-3">
                    <Package className="w-4 h-4 text-gray-500" />
                    <span className="font-medium text-gray-900">Order #{complaint.booking_info.order_id}</span>
                  </div>
                  <div className="flex items-center space-x-3">
                    <DollarSign className="w-4 h-4 text-gray-500" />
                    <span className="text-gray-700">₹{complaint.booking_info.total_amount?.toLocaleString()}</span>
                  </div>
                  <div className="flex items-center space-x-3">
                    <Calendar className="w-4 h-4 text-gray-500" />
                    <span className="text-gray-700">{formatDate(complaint.booking_info.scheduled_date)}</span>
                  </div>
                </div>
              </div>
            )}

            {/* Assignment Information */}
            {complaint.assigned_to_staff && (
              <div className="mb-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-3">Assignment</h3>
                <div className="bg-gray-50 rounded-lg p-4 space-y-3">
                  <div className="flex items-center space-x-3">
                    <UserCheck className="w-4 h-4 text-gray-500" />
                    <span className="font-medium text-gray-900">{complaint.assigned_to_staff.name}</span>
                  </div>
                  <div className="flex items-center space-x-3">
                    <Clock className="w-4 h-4 text-gray-500" />
                    <span className="text-gray-700">Assigned on {formatDate(complaint.assigned_at)}</span>
                  </div>
                </div>
              </div>
            )}

            {/* Resolution */}
            {complaint.resolution && (
              <div className="mb-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-3">Resolution</h3>
                <div className="bg-green-50 rounded-lg p-4">
                  <p className="text-gray-700 leading-relaxed">{complaint.resolution}</p>
                  {complaint.resolved_at && (
                    <div className="flex items-center space-x-2 mt-3 text-sm text-gray-600">
                      <CheckCircle className="w-4 h-4 text-green-600" />
                      <span>Resolved on {formatDate(complaint.resolved_at)}</span>
                      {complaint.resolved_by_staff && (
                        <span>by {complaint.resolved_by_staff.name}</span>
                      )}
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Action Buttons */}
            <div className="flex flex-wrap gap-3">
              {complaint.status !== 'resolved' && complaint.status !== 'closed' && (
                <>
                  <button
                    onClick={() => setShowUpdateForm(true)}
                    className="btn-primary text-sm px-4 py-2 flex items-center space-x-2"
                  >
                    <Plus className="w-4 h-4" />
                    <span>Add Update</span>
                  </button>
                  
                  {!complaint.assigned_to_staff && (
                    <button
                      onClick={() => setShowAssignForm(true)}
                      className="btn-secondary text-sm px-4 py-2 flex items-center space-x-2"
                    >
                      <UserCheck className="w-4 h-4" />
                      <span>Assign</span>
                    </button>
                  )}
                  
                  <button
                    onClick={() => setShowResolveForm(true)}
                    className="btn-success text-sm px-4 py-2 flex items-center space-x-2"
                  >
                    <CheckCircle className="w-4 h-4" />
                    <span>Resolve</span>
                  </button>
                </>
              )}
            </div>
          </div>

          {/* Right Panel - Updates */}
          <div className="w-96 p-6 overflow-y-auto bg-gray-50">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900">Updates & Notes</h3>
              <button
                onClick={fetchUpdates}
                className="p-2 hover:bg-gray-200 rounded-lg transition-colors"
              >
                <RefreshCw className="w-4 h-4 text-gray-600" />
              </button>
            </div>

            {/* Updates List */}
            <div className="space-y-4">
              {updates.map((update, index) => (
                <div key={index} className="bg-white rounded-lg p-4 shadow-sm">
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex items-center space-x-2">
                      <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                        <span className="text-xs font-medium text-blue-600">
                          {update.staff_info?.name?.charAt(0) || 'S'}
                        </span>
                      </div>
                      <div>
                        <p className="text-sm font-medium text-gray-900">
                          {update.staff_info?.name || 'System'}
                        </p>
                        <p className="text-xs text-gray-500">
                          {formatDate(update.created_at)}
                        </p>
                      </div>
                    </div>
                    {update.is_internal && (
                      <span className="px-2 py-1 bg-yellow-100 text-yellow-700 text-xs rounded-full">
                        Internal
                      </span>
                    )}
                  </div>
                  <p className="text-sm text-gray-700 leading-relaxed">
                    {update.comment}
                  </p>
                </div>
              ))}
              
              {updates.length === 0 && (
                <div className="text-center py-8">
                  <MessageSquare className="w-8 h-8 text-gray-400 mx-auto mb-2" />
                  <p className="text-gray-500 text-sm">No updates yet</p>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Update Form Modal */}
        {showUpdateForm && (
          <div className="absolute inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4">
            <div className="bg-white rounded-lg p-6 w-full max-w-md">
              <h3 className="text-lg font-semibold mb-4">Add Update</h3>
              <textarea
                value={newUpdate}
                onChange={(e) => setNewUpdate(e.target.value)}
                placeholder="Enter update or note..."
                className="w-full h-32 p-3 border border-gray-300 rounded-lg resize-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
              <div className="flex items-center mt-4 mb-4">
                <input
                  type="checkbox"
                  id="internal"
                  checked={isInternal}
                  onChange={(e) => setIsInternal(e.target.checked)}
                  className="mr-2"
                />
                <label htmlFor="internal" className="text-sm text-gray-700">
                  Internal note (not visible to customer)
                </label>
              </div>
              <div className="flex space-x-3">
                <button
                  onClick={handleAddUpdate}
                  disabled={loading || !newUpdate.trim()}
                  className="btn-primary flex-1 text-sm py-2 disabled:opacity-50"
                >
                  {loading ? 'Adding...' : 'Add Update'}
                </button>
                <button
                  onClick={() => setShowUpdateForm(false)}
                  className="btn-secondary flex-1 text-sm py-2"
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Assign Form Modal */}
        {showAssignForm && (
          <div className="absolute inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4">
            <div className="bg-white rounded-lg p-6 w-full max-w-md">
              <h3 className="text-lg font-semibold mb-4">Assign Complaint</h3>
              <select
                value={assignToStaff}
                onChange={(e) => setAssignToStaff(e.target.value)}
                className="w-full p-3 border border-gray-300 rounded-lg mb-4 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="">Select staff member...</option>
                {staffList.map((staff) => (
                  <option key={staff.id} value={staff.id}>
                    {staff.name} - {staff.department}
                  </option>
                ))}
              </select>
              <textarea
                value={assignNotes}
                onChange={(e) => setAssignNotes(e.target.value)}
                placeholder="Assignment notes (optional)..."
                className="w-full h-24 p-3 border border-gray-300 rounded-lg resize-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
              <div className="flex space-x-3 mt-4">
                <button
                  onClick={handleAssign}
                  disabled={loading || !assignToStaff}
                  className="btn-primary flex-1 text-sm py-2 disabled:opacity-50"
                >
                  {loading ? 'Assigning...' : 'Assign'}
                </button>
                <button
                  onClick={() => setShowAssignForm(false)}
                  className="btn-secondary flex-1 text-sm py-2"
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Resolve Form Modal */}
        {showResolveForm && (
          <div className="absolute inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4">
            <div className="bg-white rounded-lg p-6 w-full max-w-md">
              <h3 className="text-lg font-semibold mb-4">Resolve Complaint</h3>
              <select
                value={resolutionStatus}
                onChange={(e) => setResolutionStatus(e.target.value)}
                className="w-full p-3 border border-gray-300 rounded-lg mb-4 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="resolved">Resolved</option>
                <option value="closed">Closed</option>
              </select>
              <textarea
                value={resolutionText}
                onChange={(e) => setResolutionText(e.target.value)}
                placeholder="Enter resolution details..."
                className="w-full h-32 p-3 border border-gray-300 rounded-lg resize-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
              <div className="flex space-x-3 mt-4">
                <button
                  onClick={handleResolve}
                  disabled={loading || !resolutionText.trim()}
                  className="btn-success flex-1 text-sm py-2 disabled:opacity-50"
                >
                  {loading ? 'Resolving...' : 'Resolve'}
                </button>
                <button
                  onClick={() => setShowResolveForm(false)}
                  className="btn-secondary flex-1 text-sm py-2"
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ComplaintDetailModal;
