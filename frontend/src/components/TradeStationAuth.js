import React, { useState, useEffect } from 'react';
import axios from 'axios';

const TradeStationAuth = () => {
  const [authStatus, setAuthStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [authenticating, setAuthenticating] = useState(false);

  const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;
  const API = `${BACKEND_URL}/api`;

  const checkAuthStatus = async () => {
    try {
      setLoading(true);
      // Try local API first, then external
      let response;
      try {
        response = await axios.get(`http://localhost:8001/api/auth/tradestation/status`);
      } catch (localError) {
        console.warn('Local API failed, trying external:', localError.message);
        response = await axios.get(`${API}/auth/tradestation/status`);
      }
      setAuthStatus(response.data);
      setError(null);
    } catch (err) {
      setError(`Failed to check auth status: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const initiateLogin = async () => {
    try {
      // Try local API first
      let response;
      try {
        response = await axios.get(`http://localhost:8001/api/auth/tradestation/login`);
      } catch (localError) {
        console.warn('Local API failed, trying external:', localError.message);
        response = await axios.get(`${API}/auth/tradestation/login`);
      }
      
      const authUrl = response.data.auth_url;
      
      // Open popup window for authentication
      const popup = window.open(
        authUrl,
        'tradestation-auth',
        'width=600,height=700,scrollbars=yes,resizable=yes,left=' + 
        (window.screen.width / 2 - 300) + ',top=' + (window.screen.height / 2 - 350)
      );

      if (!popup) {
        setError('Popup blocked. Please allow popups for this site and try again.');
        return;
      }

      // Listen for auth completion
      const handleMessage = (event) => {
        if (event.data.type === 'TRADESTATION_AUTH_SUCCESS') {
          popup.close();
          checkAuthStatus(); // Refresh status
          window.removeEventListener('message', handleMessage);
          setError(null);
        } else if (event.data.type === 'TRADESTATION_AUTH_ERROR') {
          popup.close();
          setError('Authentication failed: ' + event.data.error);
          window.removeEventListener('message', handleMessage);
        }
      };

      window.addEventListener('message', handleMessage);

      // Check if popup was closed manually
      const checkClosed = setInterval(() => {
        if (popup.closed) {
          clearInterval(checkClosed);
          window.removeEventListener('message', handleMessage);
          checkAuthStatus(); // Check status in case auth completed
        }
      }, 1000);

    } catch (err) {
      setError(`Failed to initiate login: ${err.message}`);
    }
  };

  const logout = async () => {
    try {
      try {
        await axios.delete(`http://localhost:8001/api/auth/tradestation/logout`);
      } catch (localError) {
        await axios.delete(`${API}/auth/tradestation/logout`);
      }
      checkAuthStatus();
    } catch (err) {
      setError(`Failed to logout: ${err.message}`);
    }
  };

  const refreshToken = async () => {
    try {
      try {
        await axios.post(`http://localhost:8001/api/auth/tradestation/refresh`);
      } catch (localError) {
        await axios.post(`${API}/auth/tradestation/refresh`);
      }
      checkAuthStatus();
    } catch (err) {
      setError(`Failed to refresh token: ${err.message}`);
    }
  };

  useEffect(() => {
    checkAuthStatus();
  }, []);

  if (loading) {
    return (
      <div className="bg-gray-900 p-6 rounded-lg border border-gray-700">
        <div className="flex items-center justify-center">
          <div className="animate-spin w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full mr-3"></div>
          <span className="text-gray-300">Checking TradeStation status...</span>
        </div>
      </div>
    );
  }

  const isAuthenticated = authStatus?.authentication?.authenticated;

  return (
    <div className="bg-gray-900 p-6 rounded-lg border border-gray-700">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-xl font-semibold text-white flex items-center">
          📊 TradeStation Connection
        </h3>
        <div className={`px-3 py-1 rounded-full text-sm font-medium ${
          isAuthenticated 
            ? 'bg-green-800 text-green-200' 
            : 'bg-red-800 text-red-200'
        }`}>
          {isAuthenticated ? '✅ Connected' : '❌ Not Connected'}
        </div>
      </div>

      {error && (
        <div className="bg-red-800 border border-red-600 text-red-200 p-3 rounded-lg mb-4">
          <p className="text-sm">{error}</p>
        </div>
      )}

      <div className="space-y-4">
        {/* Status Information */}
        <div className="bg-gray-800 p-4 rounded-lg border border-gray-600">
          <h4 className="text-lg font-medium text-white mb-3">Connection Status</h4>
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <span className="text-gray-400">Environment:</span>
              <span className="text-white ml-2 font-mono">
                {authStatus?.authentication?.environment}
              </span>
            </div>
            <div>
              <span className="text-gray-400">Has Access Token:</span>
              <span className="text-white ml-2">
                {authStatus?.authentication?.has_access_token ? '✅ Yes' : '❌ No'}
              </span>
            </div>
            <div>
              <span className="text-gray-400">Has Refresh Token:</span>
              <span className="text-white ml-2">
                {authStatus?.authentication?.has_refresh_token ? '✅ Yes' : '❌ No'}
              </span>
            </div>
            <div>
              <span className="text-gray-400">Token Expires:</span>
              <span className="text-white ml-2 font-mono text-xs">
                {authStatus?.authentication?.token_expires 
                  ? new Date(authStatus.authentication.token_expires).toLocaleString()
                  : 'Unknown'
                }
              </span>
            </div>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex flex-wrap gap-3">
          {!isAuthenticated ? (
            <button
              onClick={initiateLogin}
              className="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-all flex items-center"
            >
              🔗 Connect to TradeStation
            </button>
          ) : (
            <>
              <button
                onClick={logout}
                className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg font-medium transition-all"
              >
                🚪 Disconnect
              </button>
              
              {authStatus?.authentication?.has_refresh_token && (
                <button
                  onClick={refreshToken}
                  className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg font-medium transition-all"
                >
                  🔄 Refresh Token
                </button>
              )}
            </>
          )}
          
          <button
            onClick={checkAuthStatus}
            className="px-4 py-2 bg-gray-600 hover:bg-gray-700 text-white rounded-lg font-medium transition-all"
          >
            🔍 Check Status
          </button>
        </div>

        {/* Connection Test */}
        {authStatus?.connection_test && (
          <div className="bg-gray-800 p-4 rounded-lg border border-gray-600">
            <h4 className="text-lg font-medium text-white mb-2">Connection Test</h4>
            <div className={`text-sm ${
              authStatus.connection_test.status === 'success' 
                ? 'text-green-400' 
                : authStatus.connection_test.status === 'warning'
                ? 'text-yellow-400'
                : 'text-red-400'
            }`}>
              {authStatus.connection_test.message}
            </div>
            {authStatus.connection_test.accounts_found !== undefined && (
              <div className="text-gray-400 text-sm mt-1">
                Accounts found: {authStatus.connection_test.accounts_found}
              </div>
            )}
          </div>
        )}

        {/* Help Text */}
        <div className="bg-blue-900 p-4 rounded-lg border border-blue-700">
          <h4 className="text-lg font-medium text-blue-200 mb-2">💡 About TradeStation Integration</h4>
          <div className="text-blue-300 text-sm space-y-1">
            <p>• <strong>Real-time data:</strong> Get live market quotes and prices</p>
            <p>• <strong>Professional charts:</strong> Display accurate candlestick data</p>
            <p>• <strong>Account integration:</strong> View your portfolio and balances</p>
            <p>• <strong>Trading capabilities:</strong> Place and manage orders (future)</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TradeStationAuth;