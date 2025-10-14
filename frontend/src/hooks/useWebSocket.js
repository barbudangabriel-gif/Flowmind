/**
 * useWebSocket Hook
 * 
 * React hook for WebSocket connection management with auto-reconnect,
 * message handling, and connection status tracking.
 * 
 * Features:
 * - Auto-connect on mount
 * - Auto-reconnect with exponential backoff
 * - Connection status tracking (connecting, connected, disconnected, error)
 * - Message callback handling
 * - Graceful cleanup on unmount
 * 
 * Usage:
 * ```jsx
 * const { 
 *   isConnected, 
 *   lastMessage, 
 *   error,
 *   connectionStatus 
 * } = useWebSocket('/api/stream/ws/flow', (message) => {
 *   console.log('Received:', message);
 * });
 * ```
 */

import { useState, useEffect, useRef, useCallback } from 'react';

// Connection status constants
export const WS_STATUS = {
  CONNECTING: 'connecting',
  CONNECTED: 'connected',
  DISCONNECTED: 'disconnected',
  ERROR: 'error',
  RECONNECTING: 'reconnecting'
};

// Reconnection configuration
const RECONNECT_CONFIG = {
  maxAttempts: 5,
  initialDelay: 1000,      // 1 second
  maxDelay: 30000,         // 30 seconds
  backoffMultiplier: 2     // Exponential backoff
};

export const useWebSocket = (endpoint, onMessage, options = {}) => {
  // Options with defaults
  const {
    autoConnect = true,
    reconnect = true,
    reconnectAttempts = RECONNECT_CONFIG.maxAttempts,
    reconnectDelay = RECONNECT_CONFIG.initialDelay,
    onOpen = null,
    onClose = null,
    onError = null
  } = options;

  // State
  const [connectionStatus, setConnectionStatus] = useState(WS_STATUS.DISCONNECTED);
  const [lastMessage, setLastMessage] = useState(null);
  const [error, setError] = useState(null);
  const [reconnectAttempt, setReconnectAttempt] = useState(0);

  // Refs (don't trigger re-renders)
  const wsRef = useRef(null);
  const reconnectTimeoutRef = useRef(null);
  const reconnectAttemptsRef = useRef(0);
  const shouldReconnectRef = useRef(true);

  // Computed derived state
  const isConnected = connectionStatus === WS_STATUS.CONNECTED;
  const isConnecting = connectionStatus === WS_STATUS.CONNECTING || connectionStatus === WS_STATUS.RECONNECTING;

  /**
   * Calculate reconnection delay with exponential backoff
   */
  const getReconnectDelay = useCallback(() => {
    const attempt = reconnectAttemptsRef.current;
    const delay = Math.min(
      reconnectDelay * Math.pow(RECONNECT_CONFIG.backoffMultiplier, attempt),
      RECONNECT_CONFIG.maxDelay
    );
    return delay;
  }, [reconnectDelay]);

  /**
   * Connect to WebSocket
   */
  const connect = useCallback(() => {
    // Don't connect if already connected or connecting
    if (wsRef.current?.readyState === WebSocket.OPEN || 
        wsRef.current?.readyState === WebSocket.CONNECTING) {
      return;
    }

    // Build WebSocket URL
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = process.env.REACT_APP_BACKEND_URL?.replace(/^https?:\/\//, '') || window.location.host;
    const wsUrl = `${protocol}//${host}${endpoint}`;

    console.log('[useWebSocket] Connecting to:', wsUrl);
    setConnectionStatus(
      reconnectAttemptsRef.current > 0 ? WS_STATUS.RECONNECTING : WS_STATUS.CONNECTING
    );
    setError(null);

    try {
      // Create WebSocket connection
      const ws = new WebSocket(wsUrl);
      wsRef.current = ws;

      // Connection opened
      ws.onopen = () => {
        console.log('[useWebSocket] Connected to:', endpoint);
        setConnectionStatus(WS_STATUS.CONNECTED);
        setError(null);
        reconnectAttemptsRef.current = 0;
        setReconnectAttempt(0);
        shouldReconnectRef.current = true;

        // Call user's onOpen callback
        if (onOpen) {
          onOpen();
        }
      };

      // Message received
      ws.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data);
          setLastMessage(message);

          // Call user's message handler
          if (onMessage) {
            onMessage(message);
          }
        } catch (err) {
          console.error('[useWebSocket] Failed to parse message:', err);
        }
      };

      // Connection closed
      ws.onclose = (event) => {
        console.log('[useWebSocket] Connection closed:', event.code, event.reason);
        setConnectionStatus(WS_STATUS.DISCONNECTED);
        wsRef.current = null;

        // Call user's onClose callback
        if (onClose) {
          onClose(event);
        }

        // Attempt reconnection if enabled and not explicitly closed
        if (reconnect && shouldReconnectRef.current) {
          if (reconnectAttemptsRef.current < reconnectAttempts) {
            const delay = getReconnectDelay();
            reconnectAttemptsRef.current += 1;
            setReconnectAttempt(reconnectAttemptsRef.current);

            console.log(
              `[useWebSocket] Reconnecting in ${delay}ms (attempt ${reconnectAttemptsRef.current}/${reconnectAttempts})`
            );

            reconnectTimeoutRef.current = setTimeout(() => {
              connect();
            }, delay);
          } else {
            console.error('[useWebSocket] Max reconnection attempts reached');
            setError('Failed to reconnect after multiple attempts');
            setConnectionStatus(WS_STATUS.ERROR);
          }
        }
      };

      // Error occurred
      ws.onerror = (event) => {
        console.error('[useWebSocket] WebSocket error:', event);
        const errorMsg = 'WebSocket connection error';
        setError(errorMsg);

        // Call user's onError callback
        if (onError) {
          onError(event);
        }
      };

    } catch (err) {
      console.error('[useWebSocket] Failed to create WebSocket:', err);
      setError(err.message);
      setConnectionStatus(WS_STATUS.ERROR);
    }
  }, [endpoint, reconnect, reconnectAttempts, onMessage, onOpen, onClose, onError, getReconnectDelay]);

  /**
   * Disconnect from WebSocket
   */
  const disconnect = useCallback(() => {
    console.log('[useWebSocket] Disconnecting...');
    shouldReconnectRef.current = false;

    // Clear reconnection timeout
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }

    // Close WebSocket connection
    if (wsRef.current) {
      wsRef.current.close(1000, 'Client initiated disconnect');
      wsRef.current = null;
    }

    setConnectionStatus(WS_STATUS.DISCONNECTED);
    reconnectAttemptsRef.current = 0;
    setReconnectAttempt(0);
  }, []);

  /**
   * Manually trigger reconnection
   */
  const reconnectManually = useCallback(() => {
    console.log('[useWebSocket] Manual reconnection triggered');
    disconnect();
    reconnectAttemptsRef.current = 0;
    setReconnectAttempt(0);
    shouldReconnectRef.current = true;
    setTimeout(connect, 100);
  }, [connect, disconnect]);

  /**
   * Send message to WebSocket (if connected)
   */
  const sendMessage = useCallback((data) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      const message = typeof data === 'string' ? data : JSON.stringify(data);
      wsRef.current.send(message);
      return true;
    } else {
      console.warn('[useWebSocket] Cannot send message - not connected');
      return false;
    }
  }, []);

  /**
   * Effect: Auto-connect on mount
   */
  useEffect(() => {
    if (autoConnect) {
      connect();
    }

    // Cleanup on unmount
    return () => {
      shouldReconnectRef.current = false;
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      if (wsRef.current) {
        wsRef.current.close(1000, 'Component unmounted');
      }
    };
  }, [autoConnect, connect]);

  /**
   * Effect: Handle visibility change (reconnect when tab becomes visible)
   */
  useEffect(() => {
    const handleVisibilityChange = () => {
      if (document.visibilityState === 'visible') {
        // Tab became visible - check connection
        if (wsRef.current?.readyState !== WebSocket.OPEN && shouldReconnectRef.current) {
          console.log('[useWebSocket] Tab visible - checking connection...');
          reconnectManually();
        }
      }
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);
    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange);
    };
  }, [reconnectManually]);

  /**
   * Effect: Handle online/offline events
   */
  useEffect(() => {
    const handleOnline = () => {
      console.log('[useWebSocket] Network online - reconnecting...');
      if (shouldReconnectRef.current) {
        reconnectManually();
      }
    };

    const handleOffline = () => {
      console.log('[useWebSocket] Network offline');
      setConnectionStatus(WS_STATUS.DISCONNECTED);
      setError('Network offline');
    };

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, [reconnectManually]);

  // Return hook interface
  return {
    // Connection state
    isConnected,
    isConnecting,
    connectionStatus,
    error,
    
    // Data
    lastMessage,
    
    // Reconnection info
    reconnectAttempt,
    maxReconnectAttempts: reconnectAttempts,
    
    // Control methods
    connect,
    disconnect,
    reconnect: reconnectManually,
    sendMessage,
    
    // Raw WebSocket reference (use with caution)
    ws: wsRef.current
  };
};

export default useWebSocket;
