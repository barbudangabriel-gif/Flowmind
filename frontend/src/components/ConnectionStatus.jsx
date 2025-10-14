/**
 * ConnectionStatus Component
 * 
 * Visual indicator for WebSocket connection health.
 * Shows connection status with color-coded indicators.
 * 
 * Usage:
 * ```jsx
 * <ConnectionStatus channel="flow-alerts" />
 * // Or for global status:
 * <ConnectionStatus />
 * ```
 */

import React from 'react';
import { useWebSocketContext } from '../context/WebSocketContext';
import { WS_STATUS } from '../hooks/useWebSocket';

const ConnectionStatus = ({ channel = null, compact = false, className = '' }) => {
  // Safely try to get WebSocket context
  let contextValue;
  try {
    contextValue = useWebSocketContext();
  } catch (err) {
    // Context not available - show disconnected
    const config = {
      label: 'Offline',
      icon: '⚪',
      color: 'text-gray-400',
      bgColor: 'bg-gray-500/10',
      borderColor: 'border-gray-500/30',
      pulse: false
    };
    
    if (compact) {
      return (
        <div className={`inline-flex items-center gap-1.5 ${className}`}>
          <span className="text-sm">{config.icon}</span>
          <span className={`text-xs font-medium ${config.color}`}>{config.label}</span>
        </div>
      );
    }
    
    return (
      <div className={`inline-flex items-center gap-2 px-3 py-1.5 rounded-lg border ${config.bgColor} ${config.borderColor} ${className}`}>
        <span className="text-sm">{config.icon}</span>
        <span className={`text-xs font-semibold tracking-wide uppercase ${config.color}`}>{config.label}</span>
      </div>
    );
  }

  const { connections, globalStatus } = contextValue;

  // Use channel-specific status or global status
  const status = channel ? connections[channel]?.status : globalStatus;
  const error = channel ? connections[channel]?.error : null;

  // Status configuration
  const statusConfig = {
    [WS_STATUS.CONNECTED]: {
      label: 'LIVE',
      icon: '🟢',
      color: 'text-green-400',
      bgColor: 'bg-green-500/10',
      borderColor: 'border-green-500/30',
      pulse: true
    },
    [WS_STATUS.CONNECTING]: {
      label: 'Connecting',
      icon: '🟡',
      color: 'text-yellow-400',
      bgColor: 'bg-yellow-500/10',
      borderColor: 'border-yellow-500/30',
      pulse: false
    },
    [WS_STATUS.RECONNECTING]: {
      label: 'Reconnecting',
      icon: '🟡',
      color: 'text-yellow-400',
      bgColor: 'bg-yellow-500/10',
      borderColor: 'border-yellow-500/30',
      pulse: false
    },
    [WS_STATUS.DISCONNECTED]: {
      label: 'Offline',
      icon: '⚪',
      color: 'text-gray-400',
      bgColor: 'bg-gray-500/10',
      borderColor: 'border-gray-500/30',
      pulse: false
    },
    [WS_STATUS.ERROR]: {
      label: 'Error',
      icon: '🔴',
      color: 'text-red-400',
      bgColor: 'bg-red-500/10',
      borderColor: 'border-red-500/30',
      pulse: false
    }
  };

  const config = statusConfig[status] || statusConfig[WS_STATUS.DISCONNECTED];

  if (compact) {
    // Compact mode - just icon and label
    return (
      <div className={`inline-flex items-center gap-1.5 ${className}`}>
        <span className={`text-sm ${config.pulse ? 'animate-pulse' : ''}`}>
          {config.icon}
        </span>
        <span className={`text-xs font-medium ${config.color}`}>
          {config.label}
        </span>
      </div>
    );
  }

  // Full mode - badge with background
  return (
    <div 
      className={`
        inline-flex items-center gap-2 px-3 py-1.5 rounded-lg border
        ${config.bgColor} ${config.borderColor}
        ${className}
      `}
      title={error || `Connection status: ${config.label}`}
    >
      {/* Status icon with pulse animation */}
      <span className={`text-sm ${config.pulse ? 'animate-pulse' : ''}`}>
        {config.icon}
      </span>
      
      {/* Status label */}
      <span className={`text-xs font-semibold tracking-wide uppercase ${config.color}`}>
        {config.label}
      </span>

      {/* Error message (if any) */}
      {error && (
        <span className="text-xs text-gray-400 ml-1">
          ({error})
        </span>
      )}
    </div>
  );
};

/**
 * Multi-Channel Connection Status
 * Shows status for all channels in a compact grid
 */
export const MultiChannelStatus = ({ className = '' }) => {
  // Safely try to get WebSocket context
  let contextValue;
  try {
    contextValue = useWebSocketContext();
  } catch (err) {
    // Context not available
    return null;
  }

  const { connections, CHANNELS } = contextValue;

  const channelLabels = {
    [CHANNELS.FLOW]: 'Flow',
    [CHANNELS.MARKET_MOVERS]: 'Movers',
    [CHANNELS.DARK_POOL]: 'Dark Pool',
    [CHANNELS.CONGRESS]: 'Congress'
  };

  return (
    <div className={`flex flex-wrap gap-2 ${className}`}>
      {Object.entries(channelLabels).map(([channel, label]) => (
        <div key={channel} className="flex items-center gap-1.5">
          <span className="text-xs text-gray-400">{label}:</span>
          <ConnectionStatus channel={channel} compact />
        </div>
      ))}
    </div>
  );
};

/**
 * Connection Status Header
 * Full-width header bar showing connection status
 */
export const ConnectionStatusBar = () => {
  // Safely try to get WebSocket context
  let contextValue;
  try {
    contextValue = useWebSocketContext();
  } catch (err) {
    // Context not available - WebSocket not initialized
    return null;
  }

  const { globalStatus, connections, getStats } = contextValue;

  const stats = getStats();
  const connectedCount = Object.values(stats).filter(s => s.status === WS_STATUS.CONNECTED).length;
  const totalMessages = Object.values(stats).reduce((sum, s) => sum + s.messageCount, 0);

  // Don't show if all disconnected and no messages received
  if (connectedCount === 0 && totalMessages === 0) {
    return null;
  }

  return (
    <div className="w-full bg-slate-800/50 border-b border-slate-700/50 px-4 py-2">
      <div className="flex items-center justify-between max-w-7xl mx-auto">
        {/* Left: Global status */}
        <div className="flex items-center gap-4">
          <ConnectionStatus />
          <span className="text-xs text-gray-400">
            {connectedCount} of 4 channels active
          </span>
        </div>

        {/* Right: Stats */}
        <div className="flex items-center gap-4 text-xs text-gray-400">
          <span>
            📨 {totalMessages.toLocaleString()} messages
          </span>
        </div>
      </div>
    </div>
  );
};

export default ConnectionStatus;
