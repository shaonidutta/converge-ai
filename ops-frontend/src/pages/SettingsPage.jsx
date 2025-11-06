import React, { useState, useEffect } from 'react';
import { 
  Settings, Save, RefreshCw, Bell, Shield, Database, 
  Mail, Clock, AlertTriangle, CheckCircle, Globe, Lock,
  Users, FileText, Zap, Eye, EyeOff
} from 'lucide-react';
import api from '../services/api';

const SettingsPage = () => {
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [activeTab, setActiveTab] = useState('general');
  const [showSuccess, setShowSuccess] = useState(false);

  const [settings, setSettings] = useState({
    // General Settings
    siteName: 'ConvergeAI Operations',
    siteUrl: 'https://ops.convergeai.com',
    timezone: 'Asia/Kolkata',
    dateFormat: 'DD/MM/YYYY',
    timeFormat: '24h',

    // Notification Settings
    emailNotifications: true,
    smsNotifications: false,
    pushNotifications: true,
    notificationFrequency: 'realtime',
    
    // Alert Settings
    criticalAlertThreshold: 90,
    highPriorityThreshold: 70,
    autoEscalationTime: 30,
    alertRetentionDays: 90,

    // Security Settings
    sessionTimeout: 30,
    maxLoginAttempts: 5,
    passwordExpiryDays: 90,
    twoFactorAuth: false,
    ipWhitelist: '',

    // Performance Settings
    cacheEnabled: true,
    cacheDuration: 300,
    apiRateLimit: 100,
    maxConcurrentRequests: 50,

    // Data Retention
    logRetentionDays: 365,
    auditLogRetentionDays: 730,
    backupFrequency: 'daily',
    autoBackup: true,

    // Feature Flags
    enableAnalytics: true,
    enableReports: true,
    enablePredictiveAnalytics: false,
    enableAIAssistant: true,
    enableWebSocket: false,
  });

  useEffect(() => {
    fetchSettings();
  }, []);

  const fetchSettings = async () => {
    setLoading(true);
    try {
      // Mock data - replace with actual API call
      // const response = await api.config.getAll();
      // setSettings(response.data);
      console.log('Settings loaded');
    } catch (error) {
      console.error('Error fetching settings:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      // Mock save - replace with actual API call
      // await api.config.updateBulk(settings);
      await new Promise(resolve => setTimeout(resolve, 1000));
      setShowSuccess(true);
      setTimeout(() => setShowSuccess(false), 3000);
    } catch (error) {
      console.error('Error saving settings:', error);
      alert('Failed to save settings');
    } finally {
      setSaving(false);
    }
  };

  const handleChange = (key, value) => {
    setSettings(prev => ({ ...prev, [key]: value }));
  };

  const tabs = [
    { id: 'general', name: 'General', icon: Settings },
    { id: 'notifications', name: 'Notifications', icon: Bell },
    { id: 'alerts', name: 'Alerts', icon: AlertTriangle },
    { id: 'security', name: 'Security', icon: Shield },
    { id: 'performance', name: 'Performance', icon: Zap },
    { id: 'data', name: 'Data & Backup', icon: Database },
    { id: 'features', name: 'Feature Flags', icon: FileText },
  ];

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Settings & Configuration</h1>
          <p className="text-sm text-gray-600 mt-1">
            Manage system settings and configurations
          </p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={fetchSettings}
            disabled={loading}
            className="flex items-center gap-2 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-all duration-200"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </button>
          <button
            onClick={handleSave}
            disabled={saving}
            className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-[#486581] to-[#5a7a9a] text-white rounded-lg hover:shadow-lg transition-all duration-200 hover:scale-105 disabled:opacity-50"
          >
            <Save className={`w-4 h-4 ${saving ? 'animate-pulse' : ''}`} />
            {saving ? 'Saving...' : 'Save Changes'}
          </button>
        </div>
      </div>

      {/* Success Message */}
      {showSuccess && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-4 flex items-center gap-2 text-green-700">
          <CheckCircle className="w-5 h-5" />
          <span className="font-medium">Settings saved successfully!</span>
        </div>
      )}

      {/* Tabs */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200">
        <div className="border-b border-gray-200 px-4">
          <div className="flex gap-1 overflow-x-auto">
            {tabs.map(tab => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center gap-2 px-4 py-3 border-b-2 transition-colors whitespace-nowrap ${
                    activeTab === tab.id
                      ? 'border-[#486581] text-[#486581] font-medium'
                      : 'border-transparent text-gray-600 hover:text-gray-900'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  {tab.name}
                </button>
              );
            })}
          </div>
        </div>

        <div className="p-6">
          {/* General Settings */}
          {activeTab === 'general' && (
            <div className="space-y-4">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">General Settings</h3>
              
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Site Name</label>
                  <input
                    type="text"
                    value={settings.siteName}
                    onChange={(e) => handleChange('siteName', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#486581]"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Site URL</label>
                  <input
                    type="url"
                    value={settings.siteUrl}
                    onChange={(e) => handleChange('siteUrl', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#486581]"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Timezone</label>
                  <select
                    value={settings.timezone}
                    onChange={(e) => handleChange('timezone', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#486581]"
                  >
                    <option value="Asia/Kolkata">Asia/Kolkata (IST)</option>
                    <option value="UTC">UTC</option>
                    <option value="America/New_York">America/New_York (EST)</option>
                    <option value="Europe/London">Europe/London (GMT)</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Date Format</label>
                  <select
                    value={settings.dateFormat}
                    onChange={(e) => handleChange('dateFormat', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#486581]"
                  >
                    <option value="DD/MM/YYYY">DD/MM/YYYY</option>
                    <option value="MM/DD/YYYY">MM/DD/YYYY</option>
                    <option value="YYYY-MM-DD">YYYY-MM-DD</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Time Format</label>
                  <select
                    value={settings.timeFormat}
                    onChange={(e) => handleChange('timeFormat', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#486581]"
                  >
                    <option value="24h">24 Hour</option>
                    <option value="12h">12 Hour (AM/PM)</option>
                  </select>
                </div>
              </div>
            </div>
          )}

          {/* Notification Settings */}
          {activeTab === 'notifications' && (
            <div className="space-y-4">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Notification Settings</h3>
              
              <div className="space-y-3">
                <label className="flex items-center gap-3 p-3 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={settings.emailNotifications}
                    onChange={(e) => handleChange('emailNotifications', e.target.checked)}
                    className="w-4 h-4 text-[#486581] rounded focus:ring-[#486581]"
                  />
                  <div className="flex-1">
                    <div className="font-medium text-gray-900">Email Notifications</div>
                    <div className="text-sm text-gray-600">Receive notifications via email</div>
                  </div>
                </label>

                <label className="flex items-center gap-3 p-3 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={settings.smsNotifications}
                    onChange={(e) => handleChange('smsNotifications', e.target.checked)}
                    className="w-4 h-4 text-[#486581] rounded focus:ring-[#486581]"
                  />
                  <div className="flex-1">
                    <div className="font-medium text-gray-900">SMS Notifications</div>
                    <div className="text-sm text-gray-600">Receive notifications via SMS</div>
                  </div>
                </label>

                <label className="flex items-center gap-3 p-3 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={settings.pushNotifications}
                    onChange={(e) => handleChange('pushNotifications', e.target.checked)}
                    className="w-4 h-4 text-[#486581] rounded focus:ring-[#486581]"
                  />
                  <div className="flex-1">
                    <div className="font-medium text-gray-900">Push Notifications</div>
                    <div className="text-sm text-gray-600">Receive browser push notifications</div>
                  </div>
                </label>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Notification Frequency</label>
                  <select
                    value={settings.notificationFrequency}
                    onChange={(e) => handleChange('notificationFrequency', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#486581]"
                  >
                    <option value="realtime">Real-time</option>
                    <option value="hourly">Hourly Digest</option>
                    <option value="daily">Daily Digest</option>
                  </select>
                </div>
              </div>
            </div>
          )}

          {/* Alert Settings */}
          {activeTab === 'alerts' && (
            <div className="space-y-4">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Alert Configuration</h3>
              
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Critical Alert Threshold (%)</label>
                  <input
                    type="number"
                    value={settings.criticalAlertThreshold}
                    onChange={(e) => handleChange('criticalAlertThreshold', parseInt(e.target.value))}
                    min="0"
                    max="100"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#486581]"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">High Priority Threshold (%)</label>
                  <input
                    type="number"
                    value={settings.highPriorityThreshold}
                    onChange={(e) => handleChange('highPriorityThreshold', parseInt(e.target.value))}
                    min="0"
                    max="100"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#486581]"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Auto-Escalation Time (minutes)</label>
                  <input
                    type="number"
                    value={settings.autoEscalationTime}
                    onChange={(e) => handleChange('autoEscalationTime', parseInt(e.target.value))}
                    min="1"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#486581]"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Alert Retention (days)</label>
                  <input
                    type="number"
                    value={settings.alertRetentionDays}
                    onChange={(e) => handleChange('alertRetentionDays', parseInt(e.target.value))}
                    min="1"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#486581]"
                  />
                </div>
              </div>
            </div>
          )}

          {/* Security Settings */}
          {activeTab === 'security' && (
            <div className="space-y-4">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Security Settings</h3>
              
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Session Timeout (minutes)</label>
                  <input
                    type="number"
                    value={settings.sessionTimeout}
                    onChange={(e) => handleChange('sessionTimeout', parseInt(e.target.value))}
                    min="5"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#486581]"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Max Login Attempts</label>
                  <input
                    type="number"
                    value={settings.maxLoginAttempts}
                    onChange={(e) => handleChange('maxLoginAttempts', parseInt(e.target.value))}
                    min="1"
                    max="10"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#486581]"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Password Expiry (days)</label>
                  <input
                    type="number"
                    value={settings.passwordExpiryDays}
                    onChange={(e) => handleChange('passwordExpiryDays', parseInt(e.target.value))}
                    min="30"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#486581]"
                  />
                </div>

                <div className="flex items-center">
                  <label className="flex items-center gap-3 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={settings.twoFactorAuth}
                      onChange={(e) => handleChange('twoFactorAuth', e.target.checked)}
                      className="w-4 h-4 text-[#486581] rounded focus:ring-[#486581]"
                    />
                    <div>
                      <div className="font-medium text-gray-900">Two-Factor Authentication</div>
                      <div className="text-sm text-gray-600">Require 2FA for all users</div>
                    </div>
                  </label>
                </div>

                <div className="col-span-2">
                  <label className="block text-sm font-medium text-gray-700 mb-1">IP Whitelist (comma-separated)</label>
                  <textarea
                    value={settings.ipWhitelist}
                    onChange={(e) => handleChange('ipWhitelist', e.target.value)}
                    rows="3"
                    placeholder="192.168.1.1, 10.0.0.1"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#486581]"
                  />
                </div>
              </div>
            </div>
          )}

          {/* Performance Settings */}
          {activeTab === 'performance' && (
            <div className="space-y-4">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Performance Settings</h3>
              
              <div className="space-y-3">
                <label className="flex items-center gap-3 p-3 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={settings.cacheEnabled}
                    onChange={(e) => handleChange('cacheEnabled', e.target.checked)}
                    className="w-4 h-4 text-[#486581] rounded focus:ring-[#486581]"
                  />
                  <div className="flex-1">
                    <div className="font-medium text-gray-900">Enable Caching</div>
                    <div className="text-sm text-gray-600">Cache API responses for better performance</div>
                  </div>
                </label>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Cache Duration (seconds)</label>
                    <input
                      type="number"
                      value={settings.cacheDuration}
                      onChange={(e) => handleChange('cacheDuration', parseInt(e.target.value))}
                      min="60"
                      disabled={!settings.cacheEnabled}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#486581] disabled:bg-gray-50"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">API Rate Limit (req/min)</label>
                    <input
                      type="number"
                      value={settings.apiRateLimit}
                      onChange={(e) => handleChange('apiRateLimit', parseInt(e.target.value))}
                      min="10"
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#486581]"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Max Concurrent Requests</label>
                    <input
                      type="number"
                      value={settings.maxConcurrentRequests}
                      onChange={(e) => handleChange('maxConcurrentRequests', parseInt(e.target.value))}
                      min="10"
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#486581]"
                    />
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Data & Backup Settings */}
          {activeTab === 'data' && (
            <div className="space-y-4">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Data Retention & Backup</h3>
              
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Log Retention (days)</label>
                  <input
                    type="number"
                    value={settings.logRetentionDays}
                    onChange={(e) => handleChange('logRetentionDays', parseInt(e.target.value))}
                    min="30"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#486581]"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Audit Log Retention (days)</label>
                  <input
                    type="number"
                    value={settings.auditLogRetentionDays}
                    onChange={(e) => handleChange('auditLogRetentionDays', parseInt(e.target.value))}
                    min="365"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#486581]"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Backup Frequency</label>
                  <select
                    value={settings.backupFrequency}
                    onChange={(e) => handleChange('backupFrequency', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#486581]"
                  >
                    <option value="hourly">Hourly</option>
                    <option value="daily">Daily</option>
                    <option value="weekly">Weekly</option>
                  </select>
                </div>

                <div className="flex items-center">
                  <label className="flex items-center gap-3 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={settings.autoBackup}
                      onChange={(e) => handleChange('autoBackup', e.target.checked)}
                      className="w-4 h-4 text-[#486581] rounded focus:ring-[#486581]"
                    />
                    <div>
                      <div className="font-medium text-gray-900">Auto Backup</div>
                      <div className="text-sm text-gray-600">Enable automatic backups</div>
                    </div>
                  </label>
                </div>
              </div>
            </div>
          )}

          {/* Feature Flags */}
          {activeTab === 'features' && (
            <div className="space-y-4">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Feature Flags</h3>
              
              <div className="space-y-3">
                <label className="flex items-center gap-3 p-3 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={settings.enableAnalytics}
                    onChange={(e) => handleChange('enableAnalytics', e.target.checked)}
                    className="w-4 h-4 text-[#486581] rounded focus:ring-[#486581]"
                  />
                  <div className="flex-1">
                    <div className="font-medium text-gray-900">Enable Analytics</div>
                    <div className="text-sm text-gray-600">Advanced analytics and insights</div>
                  </div>
                </label>

                <label className="flex items-center gap-3 p-3 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={settings.enableReports}
                    onChange={(e) => handleChange('enableReports', e.target.checked)}
                    className="w-4 h-4 text-[#486581] rounded focus:ring-[#486581]"
                  />
                  <div className="flex-1">
                    <div className="font-medium text-gray-900">Enable Reports</div>
                    <div className="text-sm text-gray-600">Report generation and export</div>
                  </div>
                </label>

                <label className="flex items-center gap-3 p-3 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={settings.enablePredictiveAnalytics}
                    onChange={(e) => handleChange('enablePredictiveAnalytics', e.target.checked)}
                    className="w-4 h-4 text-[#486581] rounded focus:ring-[#486581]"
                  />
                  <div className="flex-1">
                    <div className="font-medium text-gray-900">Enable Predictive Analytics</div>
                    <div className="text-sm text-gray-600">AI-powered predictions and forecasting</div>
                  </div>
                </label>

                <label className="flex items-center gap-3 p-3 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={settings.enableAIAssistant}
                    onChange={(e) => handleChange('enableAIAssistant', e.target.checked)}
                    className="w-4 h-4 text-[#486581] rounded focus:ring-[#486581]"
                  />
                  <div className="flex-1">
                    <div className="font-medium text-gray-900">Enable AI Assistant</div>
                    <div className="text-sm text-gray-600">AI-powered assistance and recommendations</div>
                  </div>
                </label>

                <label className="flex items-center gap-3 p-3 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={settings.enableWebSocket}
                    onChange={(e) => handleChange('enableWebSocket', e.target.checked)}
                    className="w-4 h-4 text-[#486581] rounded focus:ring-[#486581]"
                  />
                  <div className="flex-1">
                    <div className="font-medium text-gray-900">Enable WebSocket</div>
                    <div className="text-sm text-gray-600">Real-time updates via WebSocket</div>
                  </div>
                </label>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default SettingsPage;

