/**
 * WebSocket Context Provider
 * 
 * Global WebSocket state management with multi-channel support.
 * Provides centralized connection management for all live feeds.
 * 
 * Usage:
 * ```jsx
 * // Wrap app with provider
 * <WebSocketProvider>
 *   <App />
 * </WebSocketProvider>
 * 
 * // Use in components
 * const { subscribe, unsubscribe, connectionStatus } = useWebSocketContext();
 * 
 * useEffect(() => {
 *   const unsubscribe = subscribe('flow-alerts', (message) => {
 *     console.log('Flow alert:', message);
 *   });
 *   return unsubscribe;
 * }, []);
 * ```
 */

import React, { createContext, useContext, useState, useCallback, useRef, useEffect } from 'react';
import { WS_STATUS } from '../hooks/useWebSocket';

// Create context
const WebSocketContext = createContext(null);

// Available channels
export const CHANNELS = {
  FLOW: 'flow-alerts',
  MARKET_MOVERS: 'market-movers',
  DARK_POOL: 'dark-pool',
  CONGRESS: 'congress'
};

// Channel endpoint mapping
const CHANNEL_ENDPOINTS = {
  [CHANNELS.FLOW]: '/api/stream/ws/flow',
  [CHANNELS.MARKET_MOVERS]: '/api/stream/ws/market-movers',
  [CHANNELS.DARK_POOL]: '/api/stream/ws/dark-pool',
  [CHANNELS.CONGRESS]: '/api/stream/ws/congress'
};

/**
 * WebSocket Provider Component
 */
export const WebSocketProvider = ({ children }) => {
  // State for each channel
  const [connections, setConnections] = useState({
    [CHANNELS.FLOW]: { status: WS_STATUS.DISCONNECTED, error: null, messageCount: 0 },
    [CHANNELS.MARKET_MOVERS]: { status: WS_STATUS.DISCONNECTED, error: null, messageCount: 0 },
    [CHANNELS.DARK_POOL]: { status: WS_STATUS.DISCONNECTED, error: null, messageCount: 0 },
    [CHANNELS.CONGRESS]: { status: WS_STATUS.DISCONNECTED, error: null, messageCount: 0 }
  });

  // Global connection status
  const [globalStatus, setGlobalStatus] = useState(WS_STATUS.DISCONNECTED);
  const [isEnabled, setIsEnabled] = useState(true);

  // Refs for WebSocket connections
  const wsRefs = useRef({});
  
  // Refs for message subscribers (channel -> array of callbacks)
  const subscribersRef = useRef({
    [CHANNELS.FLOW]: [],
    [CHANNELS.MARKET_MOVERS]: [],
    [CHANNELS.DARK_POOL]: [],
    [CHANNELS.CONGRESS]: []
  });

  /**
   * Update connection status for a channel
   */
  const updateChannelStatus = useCallback((channel, updates) => {
    setConnections(prev => ({
      ...prev,
      [channel]: { ...prev[channel], ...updates }
    }));
  }, []);

  /**
   * Connect to a specific channel
   */
  const connectToChannel = useCallback((channel) => {
    if (!isEnabled) {
      console.log(`[WebSocketContext] WebSocket disabled, not connecting to ${channel}`);
      return;
    }

    const endpoint = CHANNEL_ENDPOINTS[channel];
    if (!endpoint) {
      console.error(`[WebSocketContext] Invalid channel: ${channel}`);
      return;
    }

    // Don't reconnect if already connected
    const ws = wsRefs.current[channel];
    if (ws && (ws.readyState === WebSocket.OPEN || ws.readyState === WebSocket.CONNECTING)) {
      console.log(`[WebSocketContext] Already connected/connecting to ${channel}`);
      return;
    }

    // Build WebSocket URL
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = process.env.REACT_APP_BACKEND_URL?.replace(/^https?:\/\//, '') || window.location.host;
    const wsUrl = `${protocol}//${host}${endpoint}`;

    console.log(`[WebSocketContext] Connecting to ${channel}:`, wsUrl);
    updateChannelStatus(channel, { status: WS_STATUS.CONNECTING, error: null });

    try {
      const newWs = new WebSocket(wsUrl);
      wsRefs.current[channel] = newWs;

      newWs.onopen = () => {
        console.log(`[WebSocketContext] ✅ Connected to ${channel}`);
        updateChannelStatus(channel, { status: WS_STATUS.CONNECTED, error: null });
      };

      newWs.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data);
          
          // Update message count
          updateChannelStatus(channel, { 
            messageCount: connections[channel]?.messageCount + 1 || 1 
          });

          // Notify all subscribers
          const subscribers = subscribersRef.current[channel] || [];
          subscribers.forEach(callback => {
            try {
              callback(message);
            } catch (err) {
              console.error(`[WebSocketContext] Subscriber callback error:`, err);
            }
          });
        } catch (err) {
          console.error(`[WebSocketContext] Failed to parse message from ${channel}:`, err);
        }
      };

      newWs.onclose = (event) => {
        console.log(`[WebSocketContext] Disconnected from ${channel}:`, event.code, event.reason);
        updateChannelStatus(channel, { 
          status: WS_STATUS.DISCONNECTED, 
          error: event.reason || 'Connection closed' 
        });
        wsRefs.current[channel] = null;
      };

      newWs.onerror = (event) => {
        console.error(`[WebSocketContext] Error on ${channel}:`, event);
        updateChannelStatus(channel, { 
          status: WS_STATUS.ERROR, 
          error: 'WebSocket error' 
        });
      };

    } catch (err) {
      console.error(`[WebSocketContext] Failed to create WebSocket for ${channel}:`, err);
      updateChannelStatus(channel, { 
        status: WS_STATUS.ERROR, 
        error: err.message 
      });
    }
  }, [isEnabled, updateChannelStatus, connections]);

  /**
   * Disconnect from a specific channel
   */
  const disconnectFromChannel = useCallback((channel) => {
    const ws = wsRefs.current[channel];
    if (ws) {
      console.log(`[WebSocketContext] Disconnecting from ${channel}`);
      ws.close(1000, 'User initiated disconnect');
      wsRefs.current[channel] = null;
      updateChannelStatus(channel, { status: WS_STATUS.DISCONNECTED });
    }
  }, [updateChannelStatus]);

  /**
   * Subscribe to a channel with a message callback
   * Returns unsubscribe function
   */
  const subscribe = useCallback((channel, callback) => {
    if (!CHANNEL_ENDPOINTS[channel]) {
      console.error(`[WebSocketContext] Invalid channel: ${channel}`);
      return () => {};
    }

    console.log(`[WebSocketContext] New subscriber for ${channel}`);

    // Add subscriber
    subscribersRef.current[channel].push(callback);

    // Connect if not already connected
    if (!wsRefs.current[channel] || wsRefs.current[channel].readyState !== WebSocket.OPEN) {
      connectToChannel(channel);
    }

    // Return unsubscribe function
    return () => {
      console.log(`[WebSocketContext] Unsubscribing from ${channel}`);
      const subscribers = subscribersRef.current[channel];
      const index = subscribers.indexOf(callback);
      if (index > -1) {
        subscribers.splice(index, 1);
      }

      // Disconnect if no more subscribers
      if (subscribers.length === 0) {
        console.log(`[WebSocketContext] No more subscribers for ${channel}, disconnecting`);
        disconnectFromChannel(channel);
      }
    };
  }, [connectToChannel, disconnectFromChannel]);

  /**
   * Reconnect to a specific channel
   */
  const reconnect = useCallback((channel) => {
    console.log(`[WebSocketContext] Manual reconnect requested for ${channel}`);
    disconnectFromChannel(channel);
    setTimeout(() => connectToChannel(channel), 100);
  }, [connectToChannel, disconnectFromChannel]);

  /**
   * Reconnect all active channels
   */
  const reconnectAll = useCallback(() => {
    console.log(`[WebSocketContext] Reconnecting all channels`);
    Object.keys(wsRefs.current).forEach(channel => {
      if (subscribersRef.current[channel]?.length > 0) {
        reconnect(channel);
      }
    });
  }, [reconnect]);

  /**
   * Enable/disable WebSocket connections
   */
  const setEnabled = useCallback((enabled) => {
    console.log(`[WebSocketContext] WebSocket ${enabled ? 'enabled' : 'disabled'}`);
    setIsEnabled(enabled);

    if (!enabled) {
      // Disconnect all
      Object.keys(CHANNELS).forEach(key => {
        disconnectFromChannel(CHANNELS[key]);
      });
    } else {
      // Reconnect channels with subscribers
      Object.keys(CHANNELS).forEach(key => {
        const channel = CHANNELS[key];
        if (subscribersRef.current[channel]?.length > 0) {
          connectToChannel(channel);
        }
      });
    }
  }, [connectToChannel, disconnectFromChannel]);

  /**
   * Get connection stats
   */
  const getStats = useCallback(() => {
    const stats = {};
    Object.keys(CHANNELS).forEach(key => {
      const channel = CHANNELS[key];
      stats[channel] = {
        status: connections[channel]?.status || WS_STATUS.DISCONNECTED,
        messageCount: connections[channel]?.messageCount || 0,
        subscribers: subscribersRef.current[channel]?.length || 0,
        error: connections[channel]?.error || null
      };
    });
    return stats;
  }, [connections]);

  /**
   * Update global status based on individual channel statuses
   */
  useEffect(() => {
    const statuses = Object.values(connections).map(c => c.status);
    
    if (statuses.includes(WS_STATUS.CONNECTED)) {
      setGlobalStatus(WS_STATUS.CONNECTED);
    } else if (statuses.includes(WS_STATUS.CONNECTING) || statuses.includes(WS_STATUS.RECONNECTING)) {
      setGlobalStatus(WS_STATUS.CONNECTING);
    } else if (statuses.includes(WS_STATUS.ERROR)) {
      setGlobalStatus(WS_STATUS.ERROR);
    } else {
      setGlobalStatus(WS_STATUS.DISCONNECTED);
    }
  }, [connections]);

  /**
   * Cleanup on unmount
   */
  useEffect(() => {
    return () => {
      console.log('[WebSocketContext] Cleaning up - disconnecting all channels');
      Object.keys(CHANNELS).forEach(key => {
        const ws = wsRefs.current[CHANNELS[key]];
        if (ws) {
          ws.close(1000, 'Provider unmounted');
        }
      });
    };
  }, []);

  // Context value
  const value = {
    // Channel management
    subscribe,
    reconnect,
    reconnectAll,
    
    // Status
    connections,
    globalStatus,
    isEnabled,
    setEnabled,
    
    // Stats
    getStats,
    
    // Constants
    CHANNELS
  };

  return (
    <WebSocketContext.Provider value={value}>
      {children}
    </WebSocketContext.Provider>
  );
};

/**
 * Hook to use WebSocket context
 */
export const useWebSocketContext = () => {
  const context = useContext(WebSocketContext);
  if (!context) {
    throw new Error('useWebSocketContext must be used within WebSocketProvider');
  }
  return context;
};

export default WebSocketContext;
