import React, { useState, useEffect } from 'react';
import { 
  FileText, Download, Calendar, Filter, TrendingUp, 
  Users, DollarSign, AlertCircle, Clock, CheckCircle,
  FileSpreadsheet, FilePdf, Send, Plus, Edit, Trash2
} from 'lucide-react';
import api from '../services/api';

const ReportsPage = () => {
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedReport, setSelectedReport] = useState(null);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [filters, setFilters] = useState({
    reportType: 'all',
    dateRange: 'month',
    startDate: '',
    endDate: ''
  });

  // Pre-built report templates
  const reportTemplates = [
    {
      id: 'bookings-summary',
      name: 'Bookings Summary Report',
      description: 'Comprehensive overview of all bookings with revenue analysis',
      icon: FileText,
      color: 'blue',
      metrics: ['Total Bookings', 'Revenue', 'Avg Order Value', 'Completion Rate']
    },
    {
      id: 'complaints-analysis',
      name: 'Complaints Analysis Report',
      description: 'Detailed analysis of complaints with resolution metrics',
      icon: AlertCircle,
      color: 'red',
      metrics: ['Total Complaints', 'Resolution Time', 'Satisfaction Score', 'Open Issues']
    },
    {
      id: 'staff-performance',
      name: 'Staff Performance Report',
      description: 'Staff productivity and performance metrics',
      icon: Users,
      color: 'green',
      metrics: ['Staff Utilization', 'Tasks Completed', 'Response Time', 'Customer Rating']
    },
    {
      id: 'revenue-analysis',
      name: 'Revenue Analysis Report',
      description: 'Financial performance and revenue trends',
      icon: DollarSign,
      color: 'yellow',
      metrics: ['Total Revenue', 'Growth Rate', 'Top Services', 'Payment Methods']
    },
    {
      id: 'operational-efficiency',
      name: 'Operational Efficiency Report',
      description: 'Overall operational metrics and KPIs',
      icon: TrendingUp,
      color: 'purple',
      metrics: ['Efficiency Score', 'Resource Utilization', 'Turnaround Time', 'Quality Score']
    },
    {
      id: 'sla-compliance',
      name: 'SLA Compliance Report',
      description: 'Service level agreement compliance tracking',
      icon: Clock,
      color: 'indigo',
      metrics: ['SLA Met', 'Average Response Time', 'Escalations', 'Breach Rate']
    }
  ];

  const [selectedTemplate, setSelectedTemplate] = useState(null);

  useEffect(() => {
    fetchReports();
  }, [filters]);

  const fetchReports = async () => {
    setLoading(true);
    try {
      // Mock data for now - will be replaced with real API
      const mockReports = [
        {
          id: 1,
          name: 'Monthly Bookings Report - December 2024',
          type: 'bookings-summary',
          createdAt: '2024-12-01T10:00:00Z',
          createdBy: 'Operations Admin',
          status: 'completed',
          format: 'pdf'
        },
        {
          id: 2,
          name: 'Complaints Analysis - Q4 2024',
          type: 'complaints-analysis',
          createdAt: '2024-12-15T14:30:00Z',
          createdBy: 'Operations Admin',
          status: 'completed',
          format: 'excel'
        }
      ];
      setReports(mockReports);
    } catch (error) {
      console.error('Error fetching reports:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateReport = async (template, format) => {
    setLoading(true);
    try {
      // Call API to generate report
      const response = await api.reports.generate({
        templateId: template.id,
        format: format,
        filters: filters
      });
      
      // Download the generated report
      const blob = new Blob([response.data], { 
        type: format === 'pdf' ? 'application/pdf' : 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' 
      });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `${template.name}-${new Date().toISOString().split('T')[0]}.${format}`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      
      fetchReports();
    } catch (error) {
      console.error('Error generating report:', error);
      alert('Failed to generate report. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleExportReport = (reportId, format) => {
    // Mock export functionality
    console.log(`Exporting report ${reportId} as ${format}`);
    alert(`Report exported as ${format.toUpperCase()}`);
  };

  const handleScheduleReport = (template) => {
    // Mock schedule functionality
    console.log('Scheduling report:', template);
    alert('Report scheduling feature coming soon!');
  };

  const getColorClasses = (color) => {
    const colors = {
      blue: 'bg-blue-500/10 text-blue-600 border-blue-500/20',
      red: 'bg-red-500/10 text-red-600 border-red-500/20',
      green: 'bg-green-500/10 text-green-600 border-green-500/20',
      yellow: 'bg-yellow-500/10 text-yellow-600 border-yellow-500/20',
      purple: 'bg-purple-500/10 text-purple-600 border-purple-500/20',
      indigo: 'bg-indigo-500/10 text-indigo-600 border-indigo-500/20'
    };
    return colors[color] || colors.blue;
  };

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Reports & Analytics</h1>
          <p className="text-sm text-gray-600 mt-1">Generate and download comprehensive reports</p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-[#486581] to-[#5a7a9a] text-white rounded-lg hover:shadow-lg transition-all duration-200 hover:scale-105"
        >
          <Plus className="w-4 h-4" />
          Custom Report
        </button>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4">
        <div className="flex items-center gap-4 flex-wrap">
          <div className="flex items-center gap-2">
            <Filter className="w-4 h-4 text-gray-500" />
            <span className="text-sm font-medium text-gray-700">Filters:</span>
          </div>
          
          <select
            value={filters.dateRange}
            onChange={(e) => setFilters({ ...filters, dateRange: e.target.value })}
            className="px-3 py-1.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#486581]"
          >
            <option value="today">Today</option>
            <option value="week">This Week</option>
            <option value="month">This Month</option>
            <option value="quarter">This Quarter</option>
            <option value="year">This Year</option>
            <option value="custom">Custom Range</option>
          </select>

          {filters.dateRange === 'custom' && (
            <>
              <input
                type="date"
                value={filters.startDate}
                onChange={(e) => setFilters({ ...filters, startDate: e.target.value })}
                className="px-3 py-1.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#486581]"
              />
              <span className="text-gray-500">to</span>
              <input
                type="date"
                value={filters.endDate}
                onChange={(e) => setFilters({ ...filters, endDate: e.target.value })}
                className="px-3 py-1.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#486581]"
              />
            </>
          )}
        </div>
      </div>

      {/* Report Templates */}
      <div>
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Report Templates</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {reportTemplates.map((template) => {
            const Icon = template.icon;
            return (
              <div
                key={template.id}
                className="bg-white rounded-xl shadow-sm border border-gray-200 p-5 hover:shadow-md transition-all duration-200 hover:scale-[1.02]"
              >
                <div className="flex items-start gap-3 mb-3">
                  <div className={`p-2.5 rounded-lg border ${getColorClasses(template.color)}`}>
                    <Icon className="w-5 h-5" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <h3 className="font-semibold text-gray-900 text-sm truncate">{template.name}</h3>
                    <p className="text-xs text-gray-600 mt-1 line-clamp-2">{template.description}</p>
                  </div>
                </div>

                <div className="space-y-2 mb-4">
                  <p className="text-xs font-medium text-gray-700">Includes:</p>
                  <div className="flex flex-wrap gap-1.5">
                    {template.metrics.map((metric, idx) => (
                      <span
                        key={idx}
                        className="px-2 py-0.5 bg-gray-100 text-gray-700 rounded text-xs"
                      >
                        {metric}
                      </span>
                    ))}
                  </div>
                </div>

                <div className="flex gap-2">
                  <button
                    onClick={() => handleGenerateReport(template, 'pdf')}
                    disabled={loading}
                    className="flex-1 flex items-center justify-center gap-1.5 px-3 py-2 bg-red-50 text-red-600 rounded-lg hover:bg-red-100 transition-colors text-xs font-medium disabled:opacity-50"
                  >
                    <FilePdf className="w-3.5 h-3.5" />
                    PDF
                  </button>
                  <button
                    onClick={() => handleGenerateReport(template, 'excel')}
                    disabled={loading}
                    className="flex-1 flex items-center justify-center gap-1.5 px-3 py-2 bg-green-50 text-green-600 rounded-lg hover:bg-green-100 transition-colors text-xs font-medium disabled:opacity-50"
                  >
                    <FileSpreadsheet className="w-3.5 h-3.5" />
                    Excel
                  </button>
                  <button
                    onClick={() => handleScheduleReport(template)}
                    className="px-3 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
                    title="Schedule Report"
                  >
                    <Send className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Recent Reports */}
      <div>
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Recent Reports</h2>
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50 border-b border-gray-200">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">Report Name</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">Type</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">Created</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">Created By</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">Status</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {reports.length === 0 ? (
                  <tr>
                    <td colSpan="6" className="px-4 py-8 text-center text-gray-500">
                      No reports generated yet. Create your first report using the templates above.
                    </td>
                  </tr>
                ) : (
                  reports.map((report) => (
                    <tr key={report.id} className="hover:bg-gray-50 transition-colors">
                      <td className="px-4 py-3 text-sm text-gray-900">{report.name}</td>
                      <td className="px-4 py-3 text-sm text-gray-600">{report.type}</td>
                      <td className="px-4 py-3 text-sm text-gray-600">
                        {new Date(report.createdAt).toLocaleDateString()}
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-600">{report.createdBy}</td>
                      <td className="px-4 py-3">
                        <span className="inline-flex items-center gap-1 px-2 py-1 bg-green-100 text-green-700 rounded-full text-xs font-medium">
                          <CheckCircle className="w-3 h-3" />
                          {report.status}
                        </span>
                      </td>
                      <td className="px-4 py-3">
                        <div className="flex items-center gap-2">
                          <button
                            onClick={() => handleExportReport(report.id, report.format)}
                            className="p-1.5 text-blue-600 hover:bg-blue-50 rounded transition-colors"
                            title="Download"
                          >
                            <Download className="w-4 h-4" />
                          </button>
                          <button
                            className="p-1.5 text-gray-600 hover:bg-gray-100 rounded transition-colors"
                            title="Delete"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ReportsPage;

