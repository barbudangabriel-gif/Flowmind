/**
 * FlowMind API Client with Robust Token Refresh
 * Implements queue-based refresh to prevent refresh storms
 * Auto-retries failed requests after token refresh
 */
import axios from "axios";

// Base API configuration
const api = axios.create({ 
  baseURL: process.env.REACT_APP_BACKEND_URL || "http://localhost:8001/api", 
  timeout: 8000 
});

// Token refresh state management
let isRefreshing = false;
let refreshQueue = [];

// Queue management functions
function enqueueRequest(resolver) { 
  refreshQueue.push(resolver); 
}

function flushQueue(token) {
  const currentQueue = [...refreshQueue];
  refreshQueue = [];
  
  currentQueue.forEach(resolver => {
    try {
      resolver(token);
    } catch (error) {
      console.error('Queue resolver error:', error);
    }
  });
}

// Request interceptor - add token to all requests
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("ts_access_token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    // Add user identification for testing
    const userId = localStorage.getItem("ts_user_id") || "demo-user";
    config.headers["X-User-ID"] = userId;
    
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor - handle 401 with smart refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const { config, response } = error;
    
    // Only handle 401 errors that haven't been retried yet
    if (!response || response.status !== 401 || config.__retry) {
      return Promise.reject(error);
    }
    
    console.log('🔄 401 detected, handling token refresh...');
    
    // If not already refreshing, start the refresh process
    if (!isRefreshing) {
      isRefreshing = true;
      console.log('🔄 Starting token refresh process...');
      
      try {
        // Call refresh endpoint
        const refreshResponse = await axios.post('/api/auth/tradestation/refresh');
        
        if (refreshResponse.data?.ok) {
          console.log('✅ Token refresh successful');
          
          // Get updated token status (in real implementation, token might be returned directly)
          const statusResponse = await axios.get('/api/auth/tradestation/status');
          
          if (statusResponse.data?.authenticated) {
            // In production, you might get the new token directly from refresh response
            // For now, we assume the token is managed server-side
            const newToken = localStorage.getItem("ts_access_token"); // Or from refresh response
            
            console.log('✅ New token available, processing queue...');
            flushQueue(newToken || 'refreshed');
          } else {
            console.warn('⚠️  Refresh succeeded but not authenticated');
            flushQueue('');
          }
        } else {
          console.error('❌ Token refresh failed:', refreshResponse.data);
          flushQueue('');
        }
        
      } catch (refreshError) {
        console.error('❌ Token refresh error:', refreshError);
        flushQueue('');
      } finally {
        isRefreshing = false;
        console.log('🔄 Token refresh process completed');
      }
    }
    
    // Queue this request for retry after refresh
    return new Promise((resolve, reject) => {
      enqueueRequest(async (newToken) => {
        if (!newToken) {
          console.log('❌ No token after refresh, rejecting request');
          reject(error);
          return;
        }
        
        // Retry the original request
        console.log('🔄 Retrying original request...');
        config.__retry = true;
        
        if (newToken !== 'refreshed') {
          config.headers.Authorization = `Bearer ${newToken}`;
        }
        
        try {
          const retryResponse = await api(config);
          console.log('✅ Request retry successful');
          resolve(retryResponse);
        } catch (retryError) {
          console.error('❌ Request retry failed:', retryError);
          reject(retryError);
        }
      });
    });
  }
);

// Helper functions for token management
export const tokenManager = {
  /**
   * Set access token in localStorage
   */
  setToken: (token) => {
    if (token) {
      localStorage.setItem("ts_access_token", token);
      console.log('✅ Access token stored');
    }
  },
  
  /**
   * Get current access token
   */
  getToken: () => {
    return localStorage.getItem("ts_access_token");
  },
  
  /**
   * Clear stored token
   */
  clearToken: () => {
    localStorage.removeItem("ts_access_token");
    console.log('🗑️  Access token cleared');
  },
  
  /**
   * Set user ID for multi-user support
   */
  setUserId: (userId) => {
    localStorage.setItem("ts_user_id", userId);
  },
  
  /**
   * Get current user ID
   */
  getUserId: () => {
    return localStorage.getItem("ts_user_id") || "demo-user";
  },
  
  /**
   * Check if user is authenticated
   */
  isAuthenticated: async () => {
    try {
      const response = await api.get('/auth/tradestation/status');
      return response.data?.authenticated || false;
    } catch (error) {
      console.error('Authentication check failed:', error);
      return false;
    }
  },
  
  /**
   * Get token expiration info
   */
  getTokenInfo: async () => {
    try {
      const response = await api.get('/auth/tradestation/status');
      return response.data;
    } catch (error) {
      console.error('Token info check failed:', error);
      return { authenticated: false, expires_in: 0 };
    }
  },
  
  /**
   * Force token refresh
   */
  forceRefresh: async () => {
    try {
      const response = await api.post('/auth/tradestation/refresh');
      return response.data?.ok || false;
    } catch (error) {
      console.error('Force refresh failed:', error);
      return false;
    }
  }
};

// Export configured API instance
export default api;