import React, { useState, useEffect } from 'react';
import useWebSocket from '../../hooks/useWebSocket';

/**
 * LiveMarketMovers - Real-time Market Movers Feed
 * 
 * EXPERIMENTAL CHANNEL: market_movers
 * 
 * Features REST API fallback when WebSocket unavailable:
 * - WebSocket: Real-time updates (if channel exists)
 * - REST Fallback: Polling every 30s
 */
const LiveMarketMovers = () => {
 const [moversData, setMoversData] = useState({ gainers: [], losers: [] });
 const [dataSource, setDataSource] = useState('none'); // 'websocket' | 'rest' | 'none'
 const [lastUpdate, setLastUpdate] = useState(null);
 const [isPaused, setIsPaused] = useState(false);
 
 // WebSocket connection
 const endpoint = `/api/stream/ws/market-movers`;
 const { messages, connected, error } = useWebSocket(endpoint);

 // REST API fallback polling
 useEffect(() => {
 // Only use REST fallback if WebSocket not connected or has errors
 if (connected && !error) {
 setDataSource('websocket');
 return; // WebSocket working, don't poll
 }
 
 if (isPaused) return;
 
 // REST fallback polling
 setDataSource('rest');
 
 const fetchMarketMovers = async () => {
 try {
 const response = await fetch('/api/market/movers');
 if (response.ok) {
 const data = await response.json();
 setMoversData(data);
 setLastUpdate(new Date().toISOString());
 }
 } catch (err) {
 console.error('REST fallback error:', err);
 }
 };
 
 // Initial fetch
 fetchMarketMovers();
 
 // Poll every 30 seconds
 const interval = setInterval(fetchMarketMovers, 30000);
 
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
 setMoversData(data.data);
 setLastUpdate(data.timestamp || new Date().toISOString());
 setDataSource('websocket');
 }
 } catch (err) {
 console.error('Failed to parse market movers message:', err);
 }
 }, [messages, isPaused]);

 // Format percentage
 const formatPercent = (value) => {
 if (!value) return 'N/A';
 const sign = value >= 0 ? '+' : '';
 return `${sign}${value.toFixed(2)}%`;
 };

 // Render mover row
 const renderMover = (mover, idx, type) => (
 <div
 key={idx}
 className="flex items-center justify-between py-3 border-b border-gray-800 last:border-0"
 >
 <div className="flex-1">
 <div className="font-medium text-[rgb(252, 251, 255)]">{mover.ticker || mover.symbol}</div>
 <div className="text-lg text-gray-500">{mover.name}</div>
 </div>
 
 <div className="text-right">
 <div className="font-mono text-xl text-gray-300">
 ${mover.price?.toFixed(2)}
 </div>
 <div className={`text-xl font-medium ${
 type === 'gainer' ? 'text-green-400' : 'text-red-400'
 }`}>
 {formatPercent(mover.change_percent)}
 </div>
 </div>
 </div>
 );

 return (
 <div className="bg-gray-900 rounded-lg shadow-lg border border-gray-800 p-6">
 {/* Header */}
 <div className="flex items-center justify-between mb-4">
 <div className="flex items-center gap-3">
 <h2 className="text-xl font-medium text-[rgb(252, 251, 255)]">
 Market Movers
 </h2>
 
 {/* Data Source Indicator */}
 {dataSource === 'websocket' && (
 <span className="px-2 py-1 rounded text-lg font-medium bg-green-500/20 text-green-400">
 ● WebSocket
 </span>
 )}
 {dataSource === 'rest' && (
 <span className="px-2 py-1 rounded text-lg font-medium bg-blue-500/20 text-blue-400">
 🔄 REST (30s)
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
 WebSocket unavailable. Using REST API fallback (updates every 30s)
 </p>
 </div>
 )}

 {/* Content */}
 {moversData.gainers?.length > 0 || moversData.losers?.length > 0 ? (
 <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
 {/* Gainers */}
 <div className="bg-gray-800 rounded-lg p-4">
 <h3 className="text-xl font-medium text-green-400 mb-3 flex items-center gap-2">
 Top Gainers
 <span className="text-lg text-gray-500">({moversData.gainers?.length || 0})</span>
 </h3>
 <div className="space-y-1">
 {(moversData.gainers || []).slice(0, 10).map((mover, idx) =>
 renderMover(mover, idx, 'gainer')
 )}
 </div>
 </div>

 {/* Losers */}
 <div className="bg-gray-800 rounded-lg p-4">
 <h3 className="text-xl font-medium text-red-400 mb-3 flex items-center gap-2">
 Top Losers
 <span className="text-lg text-gray-500">({moversData.losers?.length || 0})</span>
 </h3>
 <div className="space-y-1">
 {(moversData.losers || []).slice(0, 10).map((mover, idx) =>
 renderMover(mover, idx, 'loser')
 )}
 </div>
 </div>
 </div>
 ) : (
 <div className="text-center py-12">
 <div className="text-gray-500 mb-2">
 {dataSource === 'none' ? '🔌 Connecting...' : '⏳ Waiting for data...'}
 </div>
 <div className="text-lg text-gray-600">
 {dataSource === 'rest' ? 'REST polling active (30s interval)' : 'WebSocket channel: market_movers'}
 </div>
 </div>
 )}

 {/* Last Update */}
 {lastUpdate && (
 <div className="mt-4 pt-4 border-t border-gray-800 text-lg text-gray-600 text-center">
 Last update: {new Date(lastUpdate).toLocaleTimeString()}
 </div>
 )}
 </div>
 );
};

export default LiveMarketMovers;
