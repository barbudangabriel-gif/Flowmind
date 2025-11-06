import React from 'react';
import { useWebSocketContext } from '../context/WebSocketContext';
import LiveFlowFeed from '../components/streaming/LiveFlowFeed';
import GammaExposureFeed from '../components/streaming/GammaExposureFeed';
import OptionTradesFeed from '../components/streaming/OptionTradesFeed';
import LiveMarketMovers from '../components/streaming/LiveMarketMovers';
import LiveDarkPool from '../components/streaming/LiveDarkPool';
import LiveCongressFeed from '../components/streaming/LiveCongressFeed';
import ConnectionStatus from '../components/streaming/ConnectionStatus';

const API = process.env.REACT_APP_BACKEND_URL || '';

/**
 * 📡 Streaming Dashboard
 * 
 * Central hub for all real-time WebSocket feeds.
 * 
 * Core Feeds (Always Visible):
 * - Options Flow Alerts
 * - Gamma Exposure Tracking
 * - Live Option Trades (NEW!)
 * 
 * Experimental Feeds (Toggle Required):
 * - Market Movers
 * - Dark Pool Activity
 * - Congress Trades
 */
const StreamingDashboard = () => {
 const {
 globalStatus,
 experimentalFeedsEnabled,
 toggleExperimentalFeeds,
 getStats
 } = useWebSocketContext();

 const stats = getStats();

 return (
 <div className="min-h-screen bg-gray-950 p-6">
 {/* Header */}
 <div className="mb-6">
 <div className="flex items-center justify-between">
 <div>
 <h1 className="text-xl font-bold text-white mb-2">
 📡 Live Data Streams
 </h1>
 <p className="text-gray-400">
 Real-time market data powered by Unusual Whales WebSocket API
 </p>
 </div>
 
 <div className="flex items-center gap-4">
 {/* TradeStation Auth Button - Now uses backend API */}
 <button
 onClick={async () => {
 try {
 const response = await fetch(`${API}/api/auth/tradestation/login`);
 const data = await response.json();
 window.location.href = data.auth_url;
 } catch (err) {
 console.error('Failed to initiate auth:', err);
 }
 }}
 className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors font-medium"
 >
 🔗 Connect TradeStation
 </button>
 
 {/* Global Status */}
 <ConnectionStatus variant="detailed" />
 </div>
 </div>
 </div>

 {/* Experimental Feeds Toggle */}
 <div className="mb-6 bg-gray-900 border border-gray-800 rounded-lg p-4">
 <div className="flex items-start justify-between">
 <div className="flex-1">
 <div className="flex items-center gap-2 mb-2">
 <h3 className="text-sm font-semibold text-white">
 🧪 Experimental Data Feeds
 </h3>
 <span className="text-xs bg-yellow-500/20 text-yellow-400 px-2 py-1 rounded">
 BETA
 </span>
 </div>
 <p className="text-sm text-gray-400">
 Enable experimental channels (Market Movers, Dark Pool, Congress).
 These channels are not officially verified and may not receive updates.
 </p>
 </div>
 
 <label className="relative inline-flex items-center cursor-pointer ml-4">
 <input
 type="checkbox"
 checked={experimentalFeedsEnabled}
 onChange={(e) => toggleExperimentalFeeds(e.target.checked)}
 className="sr-only peer"
 />
 <div className="w-11 h-6 bg-gray-700 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-800 rounded-full peer peer-checked:after:translate-x-full rtl:peer-checked:after:-translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:start-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
 <span className="ms-3 text-sm font-medium text-gray-300">
 {experimentalFeedsEnabled ? 'Enabled' : 'Disabled'}
 </span>
 </label>
 </div>
 </div>

 {/* Core Feeds - Always Visible */}
 <div className="space-y-6 mb-6">
 <div className="bg-gray-900/50 border border-green-500/30 rounded-lg p-1">
 <div className="bg-gray-900 rounded p-4">
 <div className="flex items-center gap-2 mb-4">
 <span className="text-xs bg-green-500/20 text-green-400 px-2 py-1 rounded font-semibold">
 VERIFIED CHANNEL
 </span>
 <span className="text-xs text-gray-500">
 Connected: {stats['flow-alerts']?.messageCount || 0} messages received
 </span>
 </div>
 <LiveFlowFeed />
 </div>
 </div>

 <div className="bg-gray-900/50 border border-green-500/30 rounded-lg p-1">
 <div className="bg-gray-900 rounded p-4">
 <div className="flex items-center gap-2 mb-4">
 <span className="text-xs bg-green-500/20 text-green-400 px-2 py-1 rounded font-semibold">
 VERIFIED CHANNEL
 </span>
 <span className="text-xs text-gray-500">
 Real-time gamma exposure tracking
 </span>
 </div>
 <GammaExposureFeed defaultTicker="SPY" />
 </div>
 </div>

 <div className="bg-gray-900/50 border border-green-500/30 rounded-lg p-1">
 <div className="bg-gray-900 rounded p-4">
 <div className="flex items-center gap-2 mb-4">
 <span className="text-xs bg-green-500/20 text-green-400 px-2 py-1 rounded font-semibold">
 VERIFIED CHANNEL
 </span>
 <span className="text-xs text-gray-500">
 Live option trades stream
 </span>
 </div>
 <OptionTradesFeed defaultTicker="TSLA" />
 </div>
 </div>
 </div>

 {/* Experimental Feeds - Conditional */}
 {experimentalFeedsEnabled && (
 <div className="space-y-6">
 <div className="bg-gray-900 border border-gray-800 rounded-lg p-4">
 <div className="text-center text-gray-400 mb-4">
 <div className="text-sm font-semibold mb-1">
 Experimental Channels Below
 </div>
 <div className="text-xs">
 These channels may not receive data or could have different names.
 They are provided for testing and exploration.
 </div>
 </div>
 </div>

 <div className="bg-gray-900/50 border border-yellow-500/30 rounded-lg p-1">
 <div className="bg-gray-900 rounded p-4">
 <div className="flex items-center gap-2 mb-4">
 <span className="text-xs bg-yellow-500/20 text-yellow-400 px-2 py-1 rounded font-semibold">
 EXPERIMENTAL
 </span>
 <span className="text-xs text-gray-500">
 Status: {stats['market-movers']?.status || 'disconnected'}
 </span>
 </div>
 <LiveMarketMovers />
 </div>
 </div>

 <div className="bg-gray-900/50 border border-yellow-500/30 rounded-lg p-1">
 <div className="bg-gray-900 rounded p-4">
 <div className="flex items-center gap-2 mb-4">
 <span className="text-xs bg-yellow-500/20 text-yellow-400 px-2 py-1 rounded font-semibold">
 EXPERIMENTAL
 </span>
 <span className="text-xs text-gray-500">
 Status: {stats['dark-pool']?.status || 'disconnected'}
 </span>
 </div>
 <LiveDarkPool />
 </div>
 </div>

 <div className="bg-gray-900/50 border border-yellow-500/30 rounded-lg p-1">
 <div className="bg-gray-900 rounded p-4">
 <div className="flex items-center gap-2 mb-4">
 <span className="text-xs bg-yellow-500/20 text-yellow-400 px-2 py-1 rounded font-semibold">
 EXPERIMENTAL
 </span>
 <span className="text-xs text-gray-500">
 Status: {stats['congress']?.status || 'disconnected'}
 </span>
 </div>
 <LiveCongressFeed />
 </div>
 </div>
 </div>
 )}

 {/* Footer Info */}
 <div className="mt-8 text-center text-xs text-gray-600">
 <p>
 Streaming powered by Unusual Whales WebSocket API • 
 <a
 href="https://api.unusualwhales.com/docs"
 target="_blank"
 rel="noopener noreferrer"
 className="text-blue-400 hover:text-blue-300 ml-1"
 >
 API Documentation ↗
 </a>
 </p>
 <p className="mt-1">
 Connection Limits: 3 concurrent WebSockets • 120 req/min • 15K REST hits/day
 </p>
 </div>
 </div>
 );
};

export default StreamingDashboard;
