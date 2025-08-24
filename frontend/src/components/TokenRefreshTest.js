/**
 * TradeStation Token Refresh Test Component
 * Tests the robust token refresh system
 */
import React, { useState, useEffect } from 'react';
import api, { tokenManager } from '../lib/api';

const TokenRefreshTest = () => {
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(false);
  const [logs, setLogs] = useState([]);

  const addLog = (message, type = 'info') => {
    const timestamp = new Date().toLocaleTimeString();
    setLogs(prev => [...prev, { timestamp, message, type }]);
  };

  const clearLogs = () => setLogs([]);

  const initTestToken = async () => {
    setLoading(true);
    try {
      addLog('🔧 Initializing test token with 10 second expiry...', 'info');
      
      // Set a test user ID
      tokenManager.setUserId('test-user');
      
      const response = await api.post('/auth/tradestation/init', {
        access_token: 'TEST_ACCESS_TOKEN_' + Date.now(),
        refresh_token: 'TEST_REFRESH_TOKEN_' + Date.now(),
        expires_in: 10
      });
      
      if (response.data.ok) {
        addLog('✅ Test token initialized successfully', 'success');
        checkStatus();
      } else {
        addLog('❌ Failed to initialize test token', 'error');
      }
    } catch (error) {
      addLog(`❌ Init error: ${error.message}`, 'error');
    } finally {
      setLoading(false);
    }
  };

  const checkStatus = async () => {
    try {
      const response = await api.get('/auth/tradestation/status');
      setStatus(response.data);
      
      const { authenticated, expires_in, status: tokenStatus } = response.data;
      addLog(`📊 Status: ${authenticated ? 'authenticated' : 'not authenticated'}, expires in ${expires_in}s (${tokenStatus})`, 'info');
    } catch (error) {
      addLog(`❌ Status check error: ${error.message}`, 'error');
    }
  };

  const testRefresh = async () => {
    setLoading(true);
    try {
      addLog('🔄 Testing manual token refresh...', 'info');
      
      const response = await api.post('/auth/tradestation/refresh');
      
      if (response.data.ok) {
        addLog('✅ Token refresh successful', 'success');
        checkStatus();
      } else {
        addLog('❌ Token refresh failed', 'error');
      }
    } catch (error) {
      addLog(`❌ Refresh error: ${error.message}`, 'error');
    } finally {
      setLoading(false);
    }
  };

  const testConcurrentRequests = async () => {
    setLoading(true);
    try {
      addLog('🚀 Testing 5 concurrent requests (should trigger single refresh)...', 'info');
      
      // Make 5 concurrent requests - should only trigger one refresh
      const promises = Array(5).fill().map((_, i) => 
        api.get('/auth/tradestation/status').then(() => `Request ${i + 1} success`)
      );
      
      const results = await Promise.allSettled(promises);
      const successful = results.filter(r => r.status === 'fulfilled').length;
      
      addLog(`✅ Concurrent test: ${successful}/5 requests successful`, 'success');
    } catch (error) {
      addLog(`❌ Concurrent test error: ${error.message}`, 'error');
    } finally {
      setLoading(false);
    }
  };

  const testTokenValidation = async () => {
    setLoading(true);
    try {
      addLog('🔍 Testing token validation (auto-refresh if needed)...', 'info');
      
      const response = await api.get('/auth/tradestation/validate');
      
      if (response.data.valid) {
        addLog(`✅ Token validation: ${response.data.message}`, 'success');
      } else {
        addLog(`❌ Token validation failed: ${response.data.error}`, 'error');
      }
    } catch (error) {
      addLog(`❌ Validation error: ${error.message}`, 'error');
    } finally {
      setLoading(false);
    }
  };

  // Auto-refresh status every 2 seconds
  useEffect(() => {
    const interval = setInterval(checkStatus, 2000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="max-w-4xl mx-auto p-6 bg-gray-900 text-white rounded-lg">
      <h1 className="text-2xl font-bold mb-6">🔧 TradeStation Token Refresh Test</h1>
      
      {/* Status Display */}
      <div className="bg-gray-800 p-4 rounded-lg mb-6">
        <h2 className="text-lg font-semibold mb-3">Current Status</h2>
        {status ? (
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <span className="text-gray-400">Authenticated:</span>
              <span className={`ml-2 ${status.authenticated ? 'text-green-400' : 'text-red-400'}`}>
                {status.authenticated ? '✅ Yes' : '❌ No'}
              </span>
            </div>
            <div>
              <span className="text-gray-400">Expires in:</span>
              <span className={`ml-2 font-mono ${status.expires_in <= 60 ? 'text-yellow-400' : 'text-green-400'}`}>
                {status.expires_in}s
              </span>
            </div>
            <div>
              <span className="text-gray-400">Status:</span>
              <span className="ml-2 text-blue-400">{status.status}</span>
            </div>
            <div>
              <span className="text-gray-400">Needs refresh:</span>
              <span className={`ml-2 ${status.needs_refresh ? 'text-yellow-400' : 'text-green-400'}`}>
                {status.needs_refresh ? '⚠️ Yes' : '✅ No'}
              </span>
            </div>
          </div>
        ) : (
          <p className="text-gray-400">No status available</p>
        )}
      </div>
      
      {/* Test Buttons */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <button
          onClick={initTestToken}
          disabled={loading}
          className="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 rounded-lg transition-colors"
        >
          🔧 Init Token
        </button>
        
        <button
          onClick={checkStatus}
          disabled={loading}
          className="px-4 py-2 bg-green-600 hover:bg-green-700 disabled:bg-gray-600 rounded-lg transition-colors"
        >
          📊 Check Status
        </button>
        
        <button
          onClick={testRefresh}
          disabled={loading}
          className="px-4 py-2 bg-yellow-600 hover:bg-yellow-700 disabled:bg-gray-600 rounded-lg transition-colors"
        >
          🔄 Force Refresh
        </button>
        
        <button
          onClick={testConcurrentRequests}
          disabled={loading}
          className="px-4 py-2 bg-purple-600 hover:bg-purple-700 disabled:bg-gray-600 rounded-lg transition-colors"
        >
          🚀 Concurrent Test
        </button>
      </div>
      
      <div className="grid grid-cols-2 gap-4 mb-6">
        <button
          onClick={testTokenValidation}
          disabled={loading}
          className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 disabled:bg-gray-600 rounded-lg transition-colors"
        >
          🔍 Test Validation
        </button>
        
        <button
          onClick={clearLogs}
          className="px-4 py-2 bg-red-600 hover:bg-red-700 rounded-lg transition-colors"
        >
          🗑️ Clear Logs
        </button>
      </div>
      
      {loading && (
        <div className="text-center mb-4">
          <div className="inline-flex items-center">
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
            Processing...
          </div>
        </div>
      )}
      
      {/* Logs */}
      <div className="bg-black rounded-lg p-4 h-64 overflow-y-auto font-mono text-sm">
        <div className="flex justify-between items-center mb-2">
          <h3 className="text-green-400">Console Logs</h3>
          <span className="text-gray-500">{logs.length} entries</span>
        </div>
        <div className="space-y-1">
          {logs.map((log, index) => (
            <div key={index} className={`
              ${log.type === 'error' ? 'text-red-400' : 
                log.type === 'success' ? 'text-green-400' : 
                'text-gray-300'}
            `}>
              <span className="text-gray-500">[{log.timestamp}]</span> {log.message}
            </div>
          ))}
          {logs.length === 0 && (
            <p className="text-gray-500">No logs yet. Start a test to see activity.</p>
          )}
        </div>
      </div>
    </div>
  );
};

export default TokenRefreshTest;