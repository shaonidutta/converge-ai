import React from 'react';
import { 
  Clock, AlertTriangle, CheckCircle, XCircle, 
  ArrowUp, Pause, Play 
} from 'lucide-react';

const ComplaintStatusBadge = ({ status, size = 'md', showIcon = true }) => {
  // Status configurations
  const statusConfig = {
    open: {
      label: 'Open',
      icon: Clock,
      colors: {
        sm: 'text-blue-600 bg-blue-50 border-blue-200',
        md: 'text-blue-700 bg-blue-100 border-blue-300',
        lg: 'text-blue-800 bg-blue-200 border-blue-400'
      }
    },
    in_progress: {
      label: 'In Progress',
      icon: Play,
      colors: {
        sm: 'text-yellow-600 bg-yellow-50 border-yellow-200',
        md: 'text-yellow-700 bg-yellow-100 border-yellow-300',
        lg: 'text-yellow-800 bg-yellow-200 border-yellow-400'
      }
    },
    resolved: {
      label: 'Resolved',
      icon: CheckCircle,
      colors: {
        sm: 'text-green-600 bg-green-50 border-green-200',
        md: 'text-green-700 bg-green-100 border-green-300',
        lg: 'text-green-800 bg-green-200 border-green-400'
      }
    },
    closed: {
      label: 'Closed',
      icon: XCircle,
      colors: {
        sm: 'text-gray-600 bg-gray-50 border-gray-200',
        md: 'text-gray-700 bg-gray-100 border-gray-300',
        lg: 'text-gray-800 bg-gray-200 border-gray-400'
      }
    },
    escalated: {
      label: 'Escalated',
      icon: ArrowUp,
      colors: {
        sm: 'text-red-600 bg-red-50 border-red-200',
        md: 'text-red-700 bg-red-100 border-red-300',
        lg: 'text-red-800 bg-red-200 border-red-400'
      }
    },
    on_hold: {
      label: 'On Hold',
      icon: Pause,
      colors: {
        sm: 'text-purple-600 bg-purple-50 border-purple-200',
        md: 'text-purple-700 bg-purple-100 border-purple-300',
        lg: 'text-purple-800 bg-purple-200 border-purple-400'
      }
    }
  };

  // Size configurations
  const sizeConfig = {
    xs: {
      padding: 'px-2 py-0.5',
      text: 'text-xs',
      icon: 'w-3 h-3'
    },
    sm: {
      padding: 'px-2.5 py-1',
      text: 'text-xs',
      icon: 'w-3 h-3'
    },
    md: {
      padding: 'px-3 py-1.5',
      text: 'text-sm',
      icon: 'w-4 h-4'
    },
    lg: {
      padding: 'px-4 py-2',
      text: 'text-base',
      icon: 'w-5 h-5'
    }
  };

  // Get configuration
  const config = statusConfig[status] || statusConfig.open;
  const sizeConf = sizeConfig[size] || sizeConfig.md;
  const colors = config.colors[size] || config.colors.md;
  const Icon = config.icon;

  return (
    <span className={`
      inline-flex items-center font-medium rounded-full border
      ${colors}
      ${sizeConf.padding}
      ${sizeConf.text}
      transition-all duration-200
    `}>
      {showIcon && (
        <Icon className={`${sizeConf.icon} ${size === 'xs' || size === 'sm' ? 'mr-1' : 'mr-1.5'}`} />
      )}
      {config.label}
    </span>
  );
};

export default ComplaintStatusBadge;
