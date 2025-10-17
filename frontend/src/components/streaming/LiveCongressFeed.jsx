import React, { useState, useEffect } from 'react';
import useWebSocket from '../../hooks/useWebSocket';

/**
 * 🏛️ LiveCongressFeed - Real-time Congress Trade Filings
 * 
 * EXPERIMENTAL CHANNEL: congress_trades
 * 
 * Features REST API fallback when WebSocket unavailable:
 * - WebSocket: Real-time updates (if channel exists)
 * - REST Fallback: Polling every 5 minutes (filings have delay anyway)
 */
const LiveCongressFeed = () => {
 const [congressTrades, setCongressTrades] = useState([]);
 const [dataSource, setDataSource] = useState('none');
 const [lastUpdate, setLastUpdate] = useState(null);
 const [isPaused, setIsPaused] = useState(false);
 
 // WebSocket connection
 const endpoint = `/api/stream/ws/congress`;
 const { messages, connected, error } = useWebSocket(endpoint);

 // REST API fallback polling
 useEffect(() => {
 if (connected && !error) {
 setDataSource('websocket');
 return;
 }
 
 if (isPaused) return;
 
 setDataSource('rest');
 
 const fetchCongressTrades = async () => {
 try {
 const response = await fetch('/api/congress-trades?limit=20');
 if (response.ok) {
 const data = await response.json();
 setCongressTrades(data.data || data);
 setLastUpdate(new Date().toISOString());
 }
 } catch (err) {
 console.error('REST fallback error:', err);
 }
 };
 
 fetchCongressTrades();
 const interval = setInterval(fetchCongressTrades, 300000); // 5 minutes
 
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
 // Add to beginning, keep last 20
 setCongressTrades(prev => [data.data, ...prev.slice(0, 19)]);
 setLastUpdate(data.timestamp || new Date().toISOString());
 setDataSource('websocket');
 }
 } catch (err) {
 console.error('Failed to parse congress trade message:', err);
 }
 }, [messages, isPaused]);

 // Format value range
 const formatRange = (min, max) => {
 if (!min && !max) return 'Unknown';
 const formatNum = (val) => {
 if (val >= 1e6) return `$${(val / 1e6).toFixed(1)}M`;
 if (val >= 1e3) return `$${(val / 1e3).toFixed(0)}K`;
 return `$${val}`;
 };
 if (min && max) return `${formatNum(min)} - ${formatNum(max)}`;
 if (min) return `${formatNum(min)}+`;
 return formatNum(max);
 };

 return (
 <div className="bg-gray-900 rounded-lg shadow-lg border border-gray-800 p-6">
 {/* Header */}
 <div className="flex items-center justify-between mb-4">
 <div className="flex items-center gap-3">
 <h2 className="text-xl font-medium text-[rgb(252, 251, 255)]">
 🏛️ Congress Trades
 </h2>
 
 {dataSource === 'websocket' && (
 <span className="px-2 py-1 rounded text-lg font-medium bg-green-500/20 text-green-400">
 ● WebSocket
 </span>
 )}
 {dataSource === 'rest' && (
 <span className="px-2 py-1 rounded text-lg font-medium bg-blue-500/20 text-blue-400">
 🔄 REST (5min)
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

 {/* Info Note */}
 <div className="bg-blue-500/10 border border-blue-500/30 rounded p-3 mb-4">
 <p className="text-blue-400 text-lg">
 Congress trade filings are not real-time. Trades reported with 30-45 day delay.
 </p>
 </div>

 {/* Warning */}
 {error && (
 <div className="bg-yellow-500/10 border border-yellow-500/30 rounded p-3 mb-4">
 <p className="text-yellow-400 text-lg">
 WebSocket unavailable. Using REST API fallback (updates every 5 min)
 </p>
 </div>
 )}

 {/* Trades List */}
 {congressTrades.length > 0 ? (
 <div className="bg-gray-800 rounded-lg p-4 max-h-96 overflow-y-auto">
 <div className="space-y-3">
 {congressTrades.map((trade, idx) => (
 <div
 key={idx}
 className="bg-gray-900 rounded p-3 border border-gray-700"
 >
 <div className="flex items-start justify-between mb-2">
 <div className="flex-1">
 <div className="flex items-center gap-2 mb-1">
 <span className="font-medium text-[rgb(252, 251, 255)]">
 {trade.representative || trade.name}
 </span>
 {trade.party && (
 <span className={`text-lg px-2 py-0.5 rounded ${
 trade.party === 'Republican' ? 'bg-red-500/20 text-red-400' :
 trade.party === 'Democrat' ? 'bg-blue-500/20 text-blue-400' :
 'bg-gray-500/20 text-gray-400'
 }`}>
 {trade.party}
 </span>
 )}
 </div>
 <div className="text-lg text-gray-500">
 {trade.state} • {trade.chamber || 'House'}
 </div>
 </div>
 
 <div className="text-right">
 <div className={`text-xl font-medium ${
 trade.type === 'purchase' ? 'text-green-400' : 'text-red-400'
 }`}>
 {trade.type === 'purchase' ? 'BUY' : 'SELL'}
 </div>
 </div>
 </div>
 
 <div className="flex items-center justify-between pt-2 border-t border-gray-800">
 <div>
 <div className="font-medium text-[rgb(252, 251, 255)]">
 {trade.ticker || trade.asset}
 </div>
 <div className="text-lg text-gray-500">
 {formatRange(trade.amount_min, trade.amount_max)}
 </div>
 </div>
 
 <div className="text-right text-lg text-gray-500">
 {trade.transaction_date && (
 <div>Trade: {new Date(trade.transaction_date).toLocaleDateString()}</div>
 )}
 {trade.filed_date && (
 <div>Filed: {new Date(trade.filed_date).toLocaleDateString()}</div>
 )}
 </div>
 </div>
 </div>
 ))}
 </div>
 </div>
 ) : (
 <div className="text-center py-12">
 <div className="text-gray-500 mb-2">
 {dataSource === 'none' ? '🔌 Connecting...' : '⏳ Waiting for congress trade filings...'}
 </div>
 <div className="text-lg text-gray-600">
 {dataSource === 'rest' ? 'REST polling active (5min interval)' : 'WebSocket channel: congress_trades'}
 </div>
 </div>
 )}

 {/* Stats Footer */}
 {congressTrades.length > 0 && (
 <div className="mt-4 pt-4 border-t border-gray-800 flex items-center justify-between text-lg text-gray-600">
 <span>{congressTrades.length} recent filings</span>
 {lastUpdate && <span>Last update: {new Date(lastUpdate).toLocaleTimeString()}</span>}
 </div>
 )}
 </div>
 );
};

export default LiveCongressFeed;
