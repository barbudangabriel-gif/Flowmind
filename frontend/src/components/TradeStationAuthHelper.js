import React, { useState } from 'react';
import axios from 'axios';

const TradeStationAuthHelper = () => {
 const [authStatus, setAuthStatus] = useState(null);
 const [loading, setLoading] = useState(false);

 const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;
 const API = `${BACKEND_URL}/api`;

 const checkAuthStatus = async () => {
 try {
 setLoading(true);
 const response = await axios.get(`${API}/auth/tradestation/status`);
 setAuthStatus(response.data);
 } catch (err) {
 console.error('Auth status check failed:', err);
 } finally {
 setLoading(false);
 }
 };

 const startAuthentication = async () => {
 try {
 const response = await axios.get(`${API}/auth/tradestation/login`);
 
 if (response.data.auth_url) {
 // Open TradeStation OAuth în same window
 window.location.href = response.data.auth_url;
 }
 } catch (err) {
 console.error('Auth initiation failed:', err);
 }
 };

 return (
 <div className="min-h-screen bg-gray-50 dark:bg-gray-900 text-gray-900 dark:text-[rgb(252, 251, 255)]">
 <div className="max-w-2xl mx-auto p-6">
 <div className="bg-white dark:bg-gray-800 rounded-lg shadow border p-6">
 <h1 className="text-2xl font-medium mb-4 flex items-center gap-3">
 <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-indigo-600 rounded-lg flex items-center justify-center text-[rgb(252, 251, 255)]">
 🏛️
 </div>
 TradeStation Authentication
 </h1>
 
 <p className="text-gray-600 dark:text-gray-400 mb-6">
 Connect to TradeStation pentru live market data și trading capabilities.
 </p>

 <div className="space-y-4">
 <button
 onClick={checkAuthStatus}
 disabled={loading}
 className="w-full px-4 py-2 bg-blue-600 text-[rgb(252, 251, 255)] rounded-lg hover:bg-blue-700 disabled:opacity-50"
 >
 {loading ? '⏳ Checking...' : ' Check Status'}
 </button>

 {authStatus && (
 <div className={`p-4 rounded-lg ${
 authStatus.authenticated 
 ? 'bg-green-100 dark:bg-green-900/20 border border-green-300 dark:border-green-700' 
 : 'bg-yellow-100 dark:bg-yellow-900/20 border border-yellow-300 dark:border-yellow-700'
 }`}>
 <div className="font-medium">
 Status: {authStatus.authenticated ? ' Authenticated' : ' Not Authenticated'}
 </div>
 {authStatus.authenticated && (
 <div className="text-xl mt-1">
 Expires in: {authStatus.expires_in} seconds
 </div>
 )}
 </div>
 )}

 {!authStatus?.authenticated && (
 <button
 onClick={startAuthentication}
 className="w-full px-4 py-2 bg-green-600 text-[rgb(252, 251, 255)] rounded-lg hover:bg-green-700"
 >
 🔗 Start TradeStation Authentication
 </button>
 )}
 </div>

 <div className="mt-6 text-xl text-gray-500 dark:text-gray-400">
 <h3 className="font-medium mb-2">What you'll get:</h3>
 <ul className="space-y-1">
 <li>• <strong>Live Market Data</strong> - Real-time quotes și charts</li>
 <li>• <strong>Account Access</strong> - Mindfolio și balance data</li>
 <li>• <strong>Trading Capabilities</strong> - Place și manage orders</li>
 </ul>
 </div>
 </div>
 </div>
 </div>
 );
};

export default TradeStationAuthHelper;