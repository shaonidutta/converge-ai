import React, { useState, useEffect } from 'react';
import { 
  Users, Search, Filter, Plus, Edit, Trash2, Eye, 
  Shield, Mail, Phone, Calendar, CheckCircle, XCircle,
  RefreshCw, X, Save, UserPlus, Lock, Unlock
} from 'lucide-react';
import api from '../services/api';

const StaffPage = () => {
  const [staff, setStaff] = useState([]);
  const [roles, setRoles] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showModal, setShowModal] = useState(false);
  const [modalMode, setModalMode] = useState('view'); // 'view', 'edit', 'create'
  const [selectedStaff, setSelectedStaff] = useState(null);
  const [formData, setFormData] = useState({
    employee_id: '',
    first_name: '',
    last_name: '',
    email: '',
    mobile: '',
    role_id: '',
    department: '',
    designation: '',
    password: ''
  });

  const [filters, setFilters] = useState({
    role_id: '',
    department: '',
    is_active: true,
    searchQuery: ''
  });

  const [pagination, setPagination] = useState({
    skip: 0,
    limit: 20,
    total: 0
  });

  useEffect(() => {
    fetchStaff();
    fetchRoles();
  }, [filters, pagination.skip]);

  const fetchStaff = async () => {
    setLoading(true);
    try {
      const params = {
        skip: pagination.skip,
        limit: pagination.limit,
        is_active: filters.is_active
      };

      if (filters.role_id) params.role_id = filters.role_id;
      if (filters.department) params.department = filters.department;

      const response = await api.staff.getStaffList(params);
      setStaff(response.data.items || response.data || []);
      setPagination(prev => ({
        ...prev,
        total: response.data.total || response.data.length || 0
      }));
    } catch (error) {
      console.error('Error fetching staff:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchRoles = async () => {
    try {
      const response = await api.staff.getRoles();
      setRoles(response.data);
    } catch (error) {
      console.error('Error fetching roles:', error);
      // Fallback to empty array on error
      setRoles([]);
    }
  };

  const handleCreate = () => {
    setModalMode('create');
    setFormData({
      employee_id: '',
      first_name: '',
      last_name: '',
      email: '',
      mobile: '',
      role_id: '',
      department: '',
      designation: '',
      password: ''
    });
    setShowModal(true);
  };

  const handleView = (staffMember) => {
    setModalMode('view');
    setSelectedStaff(staffMember);
    setFormData({
      employee_id: staffMember.employee_id,
      first_name: staffMember.first_name,
      last_name: staffMember.last_name,
      email: staffMember.email,
      mobile: staffMember.mobile,
      role_id: staffMember.role?.id || '',
      department: staffMember.department || '',
      designation: staffMember.designation || '',
      password: ''
    });
    setShowModal(true);
  };

  const handleEdit = (staffMember) => {
    setModalMode('edit');
    setSelectedStaff(staffMember);
    setFormData({
      employee_id: staffMember.employee_id,
      first_name: staffMember.first_name,
      last_name: staffMember.last_name,
      email: staffMember.email,
      mobile: staffMember.mobile,
      role_id: staffMember.role?.id || '',
      department: staffMember.department || '',
      designation: staffMember.designation || '',
      password: ''
    });
    setShowModal(true);
  };

  const handleSave = async () => {
    try {
      if (modalMode === 'create') {
        await api.staff.createStaffMember(formData);
      } else if (modalMode === 'edit') {
        await api.staff.updateStaffMember(selectedStaff.id, formData);
      }
      fetchStaff();
      setShowModal(false);
    } catch (error) {
      console.error('Error saving staff:', error);
      alert('Failed to save staff member');
    }
  };

  const handleToggleActive = async (staffMember) => {
    try {
      await api.staff.updateStaffMember(staffMember.id, {
        is_active: !staffMember.is_active
      });
      fetchStaff();
    } catch (error) {
      console.error('Error toggling staff status:', error);
      alert('Failed to update staff status');
    }
  };

  const getRoleBadgeColor = (roleName) => {
    const colors = {
      'ops_admin': 'bg-purple-100 text-purple-700 border-purple-200',
      'ops_manager': 'bg-blue-100 text-blue-700 border-blue-200',
      'ops_staff': 'bg-green-100 text-green-700 border-green-200',
      'system_admin': 'bg-red-100 text-red-700 border-red-200'
    };
    return colors[roleName] || 'bg-gray-100 text-gray-700 border-gray-200';
  };

  const filteredStaff = staff.filter(s => {
    if (!filters.searchQuery) return true;
    const query = filters.searchQuery.toLowerCase();
    return (
      s.first_name?.toLowerCase().includes(query) ||
      s.last_name?.toLowerCase().includes(query) ||
      s.email?.toLowerCase().includes(query) ||
      s.employee_id?.toLowerCase().includes(query)
    );
  });

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Staff Management</h1>
          <p className="text-sm text-gray-600 mt-1">
            {filteredStaff.length} staff members • {filteredStaff.filter(s => s.is_active).length} active
          </p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={fetchStaff}
            disabled={loading}
            className="flex items-center gap-2 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-all duration-200"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </button>
          <button
            onClick={handleCreate}
            className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-[#486581] to-[#5a7a9a] text-white rounded-lg hover:shadow-lg transition-all duration-200 hover:scale-105"
          >
            <UserPlus className="w-4 h-4" />
            Add Staff
          </button>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Search</label>
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input
                type="text"
                value={filters.searchQuery}
                onChange={(e) => setFilters({ ...filters, searchQuery: e.target.value })}
                placeholder="Search by name, email, ID..."
                className="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#486581]"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Role</label>
            <select
              value={filters.role_id}
              onChange={(e) => setFilters({ ...filters, role_id: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#486581]"
            >
              <option value="">All Roles</option>
              {roles.map(role => (
                <option key={role.id} value={role.id}>{role.display_name}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Department</label>
            <input
              type="text"
              value={filters.department}
              onChange={(e) => setFilters({ ...filters, department: e.target.value })}
              placeholder="Filter by department"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#486581]"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Status</label>
            <select
              value={filters.is_active}
              onChange={(e) => setFilters({ ...filters, is_active: e.target.value === 'true' })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#486581]"
            >
              <option value="true">Active</option>
              <option value="false">Inactive</option>
            </select>
          </div>
        </div>
      </div>

      {/* Staff Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {loading ? (
          <div className="col-span-full flex justify-center items-center py-12">
            <RefreshCw className="w-8 h-8 animate-spin text-[#486581]" />
          </div>
        ) : filteredStaff.length === 0 ? (
          <div className="col-span-full text-center py-12 text-gray-500">
            No staff members found
          </div>
        ) : (
          filteredStaff.map((staffMember) => (
            <div
              key={staffMember.id}
              className="bg-white rounded-xl shadow-sm border border-gray-200 p-5 hover:shadow-md transition-all duration-200"
            >
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div className="w-12 h-12 rounded-full bg-gradient-to-br from-[#486581] to-[#5a7a9a] flex items-center justify-center text-white font-semibold text-lg">
                    {staffMember.first_name?.[0]}{staffMember.last_name?.[0]}
                  </div>
                  <div>
                    <h3 className="font-semibold text-gray-900">
                      {staffMember.first_name} {staffMember.last_name}
                    </h3>
                    <p className="text-xs text-gray-500">{staffMember.employee_id}</p>
                  </div>
                </div>
                {staffMember.is_active ? (
                  <CheckCircle className="w-5 h-5 text-green-500" />
                ) : (
                  <XCircle className="w-5 h-5 text-red-500" />
                )}
              </div>

              <div className="space-y-2 mb-4">
                <div className="flex items-center gap-2 text-sm text-gray-600">
                  <Mail className="w-4 h-4" />
                  <span className="truncate">{staffMember.email}</span>
                </div>
                <div className="flex items-center gap-2 text-sm text-gray-600">
                  <Phone className="w-4 h-4" />
                  <span>{staffMember.mobile}</span>
                </div>
                {staffMember.department && (
                  <div className="flex items-center gap-2 text-sm text-gray-600">
                    <Users className="w-4 h-4" />
                    <span>{staffMember.department}</span>
                  </div>
                )}
              </div>

              <div className="flex items-center justify-between pt-3 border-t border-gray-100">
                <span className={`inline-flex items-center gap-1 px-2 py-1 rounded-lg text-xs font-medium border ${getRoleBadgeColor(staffMember.role?.name)}`}>
                  <Shield className="w-3 h-3" />
                  {staffMember.role?.display_name || 'No Role'}
                </span>
                <div className="flex gap-1">
                  <button
                    onClick={() => handleView(staffMember)}
                    className="p-1.5 text-blue-600 hover:bg-blue-50 rounded transition-colors"
                    title="View Details"
                  >
                    <Eye className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => handleEdit(staffMember)}
                    className="p-1.5 text-green-600 hover:bg-green-50 rounded transition-colors"
                    title="Edit"
                  >
                    <Edit className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => handleToggleActive(staffMember)}
                    className={`p-1.5 ${staffMember.is_active ? 'text-red-600 hover:bg-red-50' : 'text-green-600 hover:bg-green-50'} rounded transition-colors`}
                    title={staffMember.is_active ? 'Deactivate' : 'Activate'}
                  >
                    {staffMember.is_active ? <Lock className="w-4 h-4" /> : <Unlock className="w-4 h-4" />}
                  </button>
                </div>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex justify-between items-start mb-6">
                <h2 className="text-xl font-bold text-gray-900">
                  {modalMode === 'create' ? 'Add New Staff' : modalMode === 'edit' ? 'Edit Staff' : 'Staff Details'}
                </h2>
                <button
                  onClick={() => setShowModal(false)}
                  className="p-1 hover:bg-gray-100 rounded transition-colors"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Employee ID *</label>
                  <input
                    type="text"
                    value={formData.employee_id}
                    onChange={(e) => setFormData({ ...formData, employee_id: e.target.value })}
                    disabled={modalMode === 'view' || modalMode === 'edit'}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#486581] disabled:bg-gray-50"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Role *</label>
                  <select
                    value={formData.role_id}
                    onChange={(e) => setFormData({ ...formData, role_id: e.target.value })}
                    disabled={modalMode === 'view'}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#486581] disabled:bg-gray-50"
                  >
                    <option value="">Select Role</option>
                    {roles.map(role => (
                      <option key={role.id} value={role.id}>{role.display_name}</option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">First Name *</label>
                  <input
                    type="text"
                    value={formData.first_name}
                    onChange={(e) => setFormData({ ...formData, first_name: e.target.value })}
                    disabled={modalMode === 'view'}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#486581] disabled:bg-gray-50"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Last Name</label>
                  <input
                    type="text"
                    value={formData.last_name}
                    onChange={(e) => setFormData({ ...formData, last_name: e.target.value })}
                    disabled={modalMode === 'view'}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#486581] disabled:bg-gray-50"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Email *</label>
                  <input
                    type="email"
                    value={formData.email}
                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                    disabled={modalMode === 'view'}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#486581] disabled:bg-gray-50"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Mobile *</label>
                  <input
                    type="tel"
                    value={formData.mobile}
                    onChange={(e) => setFormData({ ...formData, mobile: e.target.value })}
                    disabled={modalMode === 'view'}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#486581] disabled:bg-gray-50"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Department</label>
                  <input
                    type="text"
                    value={formData.department}
                    onChange={(e) => setFormData({ ...formData, department: e.target.value })}
                    disabled={modalMode === 'view'}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#486581] disabled:bg-gray-50"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Designation</label>
                  <input
                    type="text"
                    value={formData.designation}
                    onChange={(e) => setFormData({ ...formData, designation: e.target.value })}
                    disabled={modalMode === 'view'}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#486581] disabled:bg-gray-50"
                  />
                </div>

                {modalMode === 'create' && (
                  <div className="col-span-2">
                    <label className="block text-sm font-medium text-gray-700 mb-1">Password *</label>
                    <input
                      type="password"
                      value={formData.password}
                      onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#486581]"
                    />
                  </div>
                )}
              </div>

              {modalMode !== 'view' && (
                <div className="flex gap-2 mt-6 pt-4 border-t border-gray-200">
                  <button
                    onClick={() => setShowModal(false)}
                    className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={handleSave}
                    className="flex-1 px-4 py-2 bg-gradient-to-r from-[#486581] to-[#5a7a9a] text-white rounded-lg hover:shadow-lg transition-all duration-200"
                  >
                    <Save className="w-4 h-4 inline mr-2" />
                    Save
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default StaffPage;

