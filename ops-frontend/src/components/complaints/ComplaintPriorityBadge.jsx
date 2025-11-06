import React from 'react';
import { 
  ArrowDown, Minus, ArrowUp, AlertTriangle 
} from 'lucide-react';

const ComplaintPriorityBadge = ({ priority, size = 'md', showIcon = true }) => {
  // Priority configurations
  const priorityConfig = {
    low: {
      label: 'Low',
      icon: ArrowDown,
      colors: {
        sm: 'text-green-600 bg-green-50 border-green-200',
        md: 'text-green-700 bg-green-100 border-green-300',
        lg: 'text-green-800 bg-green-200 border-green-400'
      }
    },
    medium: {
      label: 'Medium',
      icon: Minus,
      colors: {
        sm: 'text-yellow-600 bg-yellow-50 border-yellow-200',
        md: 'text-yellow-700 bg-yellow-100 border-yellow-300',
        lg: 'text-yellow-800 bg-yellow-200 border-yellow-400'
      }
    },
    high: {
      label: 'High',
      icon: ArrowUp,
      colors: {
        sm: 'text-orange-600 bg-orange-50 border-orange-200',
        md: 'text-orange-700 bg-orange-100 border-orange-300',
        lg: 'text-orange-800 bg-orange-200 border-orange-400'
      }
    },
    critical: {
      label: 'Critical',
      icon: AlertTriangle,
      colors: {
        sm: 'text-red-600 bg-red-50 border-red-200',
        md: 'text-red-700 bg-red-100 border-red-300',
        lg: 'text-red-800 bg-red-200 border-red-400'
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
  const config = priorityConfig[priority] || priorityConfig.medium;
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

export default ComplaintPriorityBadge;
