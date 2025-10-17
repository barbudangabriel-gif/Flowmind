import React, { useState, useEffect } from 'react';
import useWebSocket from '../../hooks/useWebSocket';

/**
 * 🌊 LiveDarkPool - Real-time Dark Pool Activity Feed
 * 
 * EXPERIMENTAL CHANNEL: dark_pool
 * 
 * Features REST API fallback when WebSocket unavailable:
 * - WebSocket: Real-time updates (if channel exists)
 * - REST Fallback: Polling every 60s
 */
const LiveDarkPool = () => {
 const [darkPoolTrades, setDarkPoolTrades] = useState([]);
 const [dataSource, setDataSource] = useState('none');
 const [lastUpdate, setLastUpdate] = useState(null);
 const [isPaused, setIsPaused] = useState(false);
 
 // WebSocket connection
 const endpoint = `/api/stream/ws/dark-pool`;
 const { messages, connected, error } = useWebSocket(endpoint);

 // REST API fallback polling
 useEffect(() => {
 if (connected && !error) {
 setDataSource('websocket');
 return;
 }
 
 if (isPaused) return;
 
 setDataSource('rest');
 
 const fetchDarkPool = async () => {
 try {
 const response = await fetch('/api/dark-pool?limit=50');
 if (response.ok) {
 const data = await response.json();
 // Filter recent trades (< 5min old)
 const now = new Date();
 const recentTrades = (data.data || data).filter(trade => {
 const tradeTime = new Date(trade.timestamp || trade.date);
 return (now - tradeTime) / 1000 < 300; // 5 minutes
 });
 setDarkPoolTrades(recentTrades);
 setLastUpdate(new Date().toISOString());
 }
 } catch (err) {
 console.error('REST fallback error:', err);
 }
 };
 
 fetchDarkPool();
 const interval = setInterval(fetchDarkPool, 60000); // 60s
 
 return () => clearInterval(interval);
 }, [connected, error, isPaused]);

 // Process WebSocket messages
 useEffect(() => {
 if (messages.length === 0 || isPaused) return;
 
 const latestMessage = messages[messages.length - 1];
 
 try {
 const data = typeof latestMessage === 'string' 
 ? JSON.parse(latestMessage) 
 : latestMessage;
 
 if (data.data) {
 // Add to beginning, keep last 50
 setDarkPoolTrades(prev => [data.data, ...prev.slice(0, 49)]);
 setLastUpdate(data.timestamp || new Date().toISOString());
 setDataSource('websocket');
 }
 } catch (err) {
 console.error('Failed to parse dark pool message:', err);
 }
 }, [messages, isPaused]);

 // Format large numbers
 const formatSize = (value) => {
 if (!value) return 'N/A';
 if (value >= 1e6) return `${(value / 1e6).toFixed(2)}M`;
 if (value >= 1e3) return `${(value / 1e3).toFixed(2)}K`;
 return value.toFixed(0);
 };

 // Format value
 const formatValue = (value) => {
 if (!value) return 'N/A';
 if (value >= 1e6) return `$${(value / 1e6).toFixed(2)}M`;
 if (value >= 1e3) return `$${(value / 1e3).toFixed(2)}K`;
 return `$${value.toFixed(2)}`;
 };

 return (
 <div className="bg-gray-900 rounded-lg shadow-lg border border-gray-800 p-6">
 {/* Header */}
 <div className="flex items-center justify-between mb-4">
 <div className="flex items-center gap-3">
 <h2 className="text-xl font-medium text-[rgb(252, 251, 255)]">
 🌊 Dark Pool Activity
 </h2>
 
 {dataSource === 'websocket' && (
 <span className="px-2 py-1 rounded text-lg font-medium bg-green-500/20 text-green-400">
 ● WebSocket
 </span>
 )}
 {dataSource === 'rest' && (
 <span className="px-2 py-1 rounded text-lg font-medium bg-blue-500/20 text-blue-400">
 🔄 REST (60s)
 </span>
 )}
 {dataSource === 'none' && (
 <span className="px-2 py-1 rounded text-lg font-medium bg-gray-500/20 text-gray-400">
 ○ No Data
 </span>
 )}
 
 <span className="px-2 py-1 rounded text-lg font-medium bg-yellow-500/20 text-yellow-400">
 EXPERIMENTAL
 </span>
 </div>
 
 <button
 onClick={() => setIsPaused(!isPaused)}
 className={`px-3 py-1 rounded text-xl font-medium transition-colors ${
 isPaused 
 ? 'bg-yellow-500/20 text-yellow-400 hover:bg-yellow-500/30' 
 : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
 }`}
 >
 {isPaused ? '▶ Resume' : '⏸ Pause'}
 </button>
 </div>

 {/* Warning */}
 {error && (
 <div className="bg-yellow-500/10 border border-yellow-500/30 rounded p-3 mb-4">
 <p className="text-yellow-400 text-lg">
 WebSocket unavailable. Using REST API fallback (updates every 60s)
 </p>
 </div>
 )}

 {/* Trades List */}
 {darkPoolTrades.length > 0 ? (
 <div className="bg-gray-800 rounded-lg p-4 max-h-96 overflow-y-auto">
 <div className="space-y-2">
 {darkPoolTrades.map((trade, idx) => (
 <div
 key={idx}
 className="flex items-center justify-between py-2 border-b border-gray-700 last:border-0"
 >
 <div className="flex-1">
 <div className="flex items-center gap-2">
 <span className="font-medium text-[rgb(252, 251, 255)]">
 {trade.ticker || trade.symbol}
 </span>
 {trade.size && (
 <span className="text-lg bg-blue-500/20 text-blue-400 px-2 py-0.5 rounded">
 {formatSize(trade.size)} shares
 </span>
 )}
 </div>
 <div className="text-lg text-gray-500 mt-1">
 {new Date(trade.timestamp || trade.date).toLocaleTimeString()}
 </div>
 </div>
 
 <div className="text-right">
 <div className="font-mono text-xl text-gray-300">
 ${trade.price?.toFixed(2)}
 </div>
 {trade.value && (
 <div className="text-xl font-medium text-purple-400">
 {formatValue(trade.value)}
 </div>
 )}
 </div>
 </div>
 ))}
 </div>
 </div>
 ) : (
 <div className="text-center py-12">
 <div className="text-gray-500 mb-2">
 {dataSource === 'none' ? '🔌 Connecting...' : '⏳ Waiting for dark pool trades...'}
 </div>
 <div className="text-lg text-gray-600">
 {dataSource === 'rest' ? 'REST polling active (60s interval)' : 'WebSocket channel: dark_pool'}
 </div>
 </div>
 )}

 {/* Stats Footer */}
 {darkPoolTrades.length > 0 && (
 <div className="mt-4 pt-4 border-t border-gray-800 flex items-center justify-between text-lg text-gray-600">
 <span>{darkPoolTrades.length} recent trades</span>
 {lastUpdate && <span>Last update: {new Date(lastUpdate).toLocaleTimeString()}</span>}
 </div>
 )}
 </div>
 );
};

export default LiveDarkPool;
