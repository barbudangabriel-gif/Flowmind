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
      const response = await axios.get(`${API}/auth/tradestation/status`);
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
      setAuthenticating(true);
      
      // NU mai folosim popup - redirect direct în aceeași fereastră
      console.log('🔗 Initiating direct redirect authentication (no popup)');
      
      const response = await axios.get(`${API}/auth/tradestation/login`);
      const authUrl = response.data.auth_url;
      
      console.log('🚀 Redirecting to TradeStation:', authUrl);
      
      // Salvează starea că suntem în proces de autentificare
      localStorage.setItem('ts_auth_in_progress', 'true');
      localStorage.setItem('ts_auth_started', Date.now().toString());
      
      // Redirect direct în aceeași fereastră (nu popup)
      window.location.href = authUrl;
      
    } catch (err) {
      console.error('❌ Login initiation failed:', err);
      setError(`Failed to initiate login: ${err.message}`);
      setAuthenticating(false);
    }
  };

  const logout = async () => {
    try {
      await axios.delete(`${API}/auth/tradestation/logout`);
      checkAuthStatus();
    } catch (err) {
      setError(`Failed to logout: ${err.message}`);
    }
  };

  const refreshToken = async () => {
    try {
      await axios.post(`${API}/auth/tradestation/refresh`);
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
          <p className="text-sm mb-2">{error}</p>
          {error.includes('Click here to authenticate manually:') && (
            <button
              onClick={() => {
                const url = error.split('Click here to authenticate manually: ')[1];
                if (url) {
                  window.open(url, '_blank');
                  setError('Please complete authentication in the new tab and then click "Check Status" below.');
                }
              }}
              className="px-3 py-1 bg-red-600 hover:bg-red-700 text-white rounded text-xs font-medium transition-all"
            >
              🔗 Open Authentication Page
            </button>
          )}
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
            <>
              <button
                onClick={initiateLogin}
                disabled={authenticating}
                className={`px-6 py-3 rounded-lg font-medium transition-all flex items-center ${
                  authenticating 
                    ? 'bg-gray-600 cursor-not-allowed text-gray-400' 
                    : 'bg-blue-600 hover:bg-blue-700 text-white'
                }`}
              >
                {authenticating ? (
                  <>
                    <div className="animate-spin w-5 h-5 border-2 border-gray-400 border-t-transparent rounded-full mr-2"></div>
                    Authenticating...
                  </>
                ) : (
                  <>🔗 Connect to TradeStation</>
                )}
              </button>
              
              <button
                onClick={() => {
                  const testPopup = window.open('about:blank', 'test-popup', 'width=300,height=200');
                  setTimeout(() => {
                    if (testPopup && !testPopup.closed) {
                      testPopup.close();
                      setError(null);
                      alert('✅ Popup test successful! You can now authenticate.');
                    } else {
                      setError('❌ Popup test failed. Please ensure popups are allowed in your browser settings.');
                    }
                  }, 1000);
                }}
                className="px-4 py-2 bg-yellow-600 hover:bg-yellow-700 text-white rounded-lg font-medium transition-all text-sm"
              >
                🧪 Test Popup
              </button>
              
              <button
                onClick={async () => {
                  try {
                    const response = await axios.get(`${API}/auth/tradestation/login`);
                    const authUrl = response.data.auth_url;
                    window.location.href = authUrl; // Redirect în aceeași fereastră
                  } catch (err) {
                    setError(`Failed to get auth URL: ${err.message}`);
                  }
                }}
                className="px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg font-medium transition-all text-sm"
              >
                🔄 Direct Login
              </button>
            </>
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