import React, { useState, useEffect } from 'react';
import useWebSocket from '../../hooks/useWebSocket';

/**
 * GammaExposureFeed - Real-time Gamma Exposure (GEX) Tracking
 * 
 * VERIFIED CHANNEL: gex:{TICKER}
 * 
 * Displays live gamma exposure updates for selected tickers.
 * Shows total GEX, call/put split, zero gamma level, and strike breakdown.
 */
const GammaExposureFeed = ({ defaultTicker = 'SPY' }) => {
 const [selectedTicker, setSelectedTicker] = useState(defaultTicker);
 const [gexData, setGexData] = useState(null);
 const [messageHistory, setMessageHistory] = useState([]);
 const [isPaused, setIsPaused] = useState(false);
 
 // Popular tickers for GEX tracking
 const availableTickers = ['SPY', 'QQQ', 'TSLA', 'AAPL', 'NVDA', 'AMZN', 'MSFT', 'GOOGL'];
 
 // WebSocket connection for selected ticker
 const endpoint = `/api/stream/ws/gex/${selectedTicker}`;
 const { messages, connected, error } = useWebSocket(endpoint);

 // Process incoming messages
 useEffect(() => {
 if (messages.length === 0 || isPaused) return;
 
 const latestMessage = messages[messages.length - 1];
 
 try {
 // Parse message
 const data = typeof latestMessage === 'string' 
 ? JSON.parse(latestMessage) 
 : latestMessage;
 
 // Update current GEX data
 if (data.data) {
 setGexData(data.data);
 
 // Add to history (keep last 20)
 setMessageHistory(prev => [
 { ...data, receivedAt: new Date().toISOString() },
 ...prev.slice(0, 19)
 ]);
 }
 } catch (err) {
 console.error('Failed to parse GEX message:', err);
 }
 }, [messages, isPaused]);

 // Reset data when ticker changes
 useEffect(() => {
 setGexData(null);
 setMessageHistory([]);
 }, [selectedTicker]);

 // Format large numbers
 const formatGex = (value) => {
 if (!value) return 'N/A';
 if (Math.abs(value) >= 1e9) return `${(value / 1e9).toFixed(2)}B`;
 if (Math.abs(value) >= 1e6) return `${(value / 1e6).toFixed(2)}M`;
 if (Math.abs(value) >= 1e3) return `${(value / 1e3).toFixed(2)}K`;
 return value.toFixed(0);
 };

 return (
 <div className="bg-gray-900 rounded-lg shadow-lg border border-gray-800 p-6">
 {/* Header */}
 <div className="flex items-center justify-between mb-4">
 <div className="flex items-center gap-3">
 <h2 className="text-xl font-medium text-[rgb(252, 251, 255)]">
 Gamma Exposure Tracker
 </h2>
 <span className={`px-2 py-1 rounded text-lg font-medium ${
 connected ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'
 }`}>
 {connected ? '● LIVE' : '○ Disconnected'}
 </span>
 <span className="px-2 py-1 rounded text-lg font-medium bg-blue-500/20 text-blue-400">
 VERIFIED
 </span>
 </div>
 
 <div className="flex items-center gap-2">
 {/* Ticker Selector */}
 <select
 value={selectedTicker}
 onChange={(e) => setSelectedTicker(e.target.value)}
 className="bg-gray-800 text-[rgb(252, 251, 255)] border border-gray-700 rounded px-3 py-1 text-xl focus:outline-none focus:ring-2 focus:ring-blue-500"
 >
 {availableTickers.map(ticker => (
 <option key={ticker} value={ticker}>{ticker}</option>
 ))}
 </select>
 
 {/* Pause Button */}
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
 </div>

 {/* Error Display */}
 {error && (
 <div className="bg-red-500/10 border border-red-500/30 rounded p-3 mb-4">
 <p className="text-red-400 text-xl"> {error}</p>
 </div>
 )}

 {/* Current GEX Summary */}
 {gexData ? (
 <div className="space-y-4">
 {/* Main Stats */}
 <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
 {/* Total GEX */}
 <div className="bg-gray-800 rounded-lg p-4">
 <div className="text-gray-400 text-lg uppercase mb-1">Total GEX</div>
 <div className={`text-2xl font-medium ${
 gexData.total_gex >= 0 ? 'text-green-400' : 'text-red-400'
 }`}>
 {formatGex(gexData.total_gex)}
 </div>
 </div>

 {/* Call GEX */}
 <div className="bg-gray-800 rounded-lg p-4">
 <div className="text-gray-400 text-lg uppercase mb-1">Call GEX</div>
 <div className="text-2xl font-medium text-green-400">
 {formatGex(gexData.call_gex)}
 </div>
 </div>

 {/* Put GEX */}
 <div className="bg-gray-800 rounded-lg p-4">
 <div className="text-gray-400 text-lg uppercase mb-1">Put GEX</div>
 <div className="text-2xl font-medium text-red-400">
 {formatGex(gexData.put_gex)}
 </div>
 </div>

 {/* Zero Gamma Level */}
 <div className="bg-gray-800 rounded-lg p-4">
 <div className="text-gray-400 text-lg uppercase mb-1">Zero Gamma</div>
 <div className="text-2xl font-medium text-blue-400">
 {gexData.zero_gamma_level ? `$${gexData.zero_gamma_level.toFixed(2)}` : 'N/A'}
 </div>
 </div>
 </div>

 {/* Strike Breakdown */}
 {gexData.strikes && gexData.strikes.length > 0 && (
 <div className="bg-gray-800 rounded-lg p-4">
 <h3 className="text-xl font-medium text-gray-300 mb-3">
 Strike Breakdown (Top 10)
 </h3>
 <div className="space-y-2 max-h-64 overflow-y-auto">
 {gexData.strikes.slice(0, 10).map((strike, idx) => (
 <div
 key={idx}
 className="flex items-center justify-between py-2 border-b border-gray-700 last:border-0"
 >
 <span className="text-gray-300 font-medium">
 ${strike.strike}
 </span>
 <div className="flex items-center gap-3">
 <div className="w-32 h-2 bg-gray-700 rounded-full overflow-hidden">
 <div
 className={`h-full ${
 strike.gex >= 0 ? 'bg-green-500' : 'bg-red-500'
 }`}
 style={{
 width: `${Math.min(Math.abs(strike.gex) / Math.max(...gexData.strikes.map(s => Math.abs(s.gex))) * 100, 100)}%`
 }}
 />
 </div>
 <span className={`text-xl font-mono ${
 strike.gex >= 0 ? 'text-green-400' : 'text-red-400'
 }`}>
 {formatGex(strike.gex)}
 </span>
 </div>
 </div>
 ))}
 </div>
 </div>
 )}
 </div>
 ) : (
 <div className="text-center py-12">
 <div className="text-gray-500 mb-2">
 {connected ? '⏳ Waiting for GEX data...' : '🔌 Connect to start streaming'}
 </div>
 <div className="text-lg text-gray-600">
 Channel: gex:{selectedTicker}
 </div>
 </div>
 )}

 {/* Message History */}
 <div className="mt-6 pt-4 border-t border-gray-800">
 <div className="flex items-center justify-between mb-2">
 <h3 className="text-xl font-medium text-gray-400">
 📜 Update History
 </h3>
 <span className="text-lg text-gray-600">
 {messageHistory.length} updates
 </span>
 </div>
 <div className="space-y-1 max-h-32 overflow-y-auto">
 {messageHistory.slice(0, 10).map((msg, idx) => (
 <div
 key={idx}
 className="text-lg text-gray-500 font-mono flex items-center justify-between py-1"
 >
 <span>{new Date(msg.receivedAt).toLocaleTimeString()}</span>
 <span>
 {msg.data?.ticker} - Total: {formatGex(msg.data?.total_gex)}
 </span>
 </div>
 ))}
 {messageHistory.length === 0 && (
 <div className="text-lg text-gray-600 text-center py-2">
 No updates yet
 </div>
 )}
 </div>
 </div>
 </div>
 );
};

export default GammaExposureFeed;
