import React, { useState, useEffect, useMemo } from 'react';
import useWebSocket from '../hooks/useWebSocket';

/**
 * LiveLitTradesFeed - Exchange-based (visible) trades feed
 * 
 * Displays real-time lit trades from public exchanges (NASDAQ, NYSE, etc.)
 * Opposite of dark pool - these are transparent, public executions.
 * 
 * @param {Object} props
 * @param {string} props.ticker - Stock symbol (e.g., "TSLA", "SPY")
 * @param {number} props.maxTrades - Maximum trades to display (default: 100)
 * @param {boolean} props.autoScroll - Auto-scroll to latest (default: true)
 */
export default function LiveLitTradesFeed({ 
 ticker = 'SPY', 
 maxTrades = 100,
 autoScroll = true
}) {
 const [trades, setTrades] = useState([]);
 const [stats, setStats] = useState({
 totalVolume: 0,
 totalValue: 0,
 tradeCount: 0,
 avgPrice: 0,
 exchanges: {}
 });
 
 const wsUrl = `/api/stream/ws/lit-trades/${ticker.toUpperCase()}`;
 const { messages, status, error } = useWebSocket(wsUrl);

 // Process incoming trades
 useEffect(() => {
 if (messages.length > 0) {
 const latestMessage = messages[messages.length - 1];
 if (latestMessage?.data) {
 const trade = latestMessage.data;
 
 setTrades(prev => {
 const updated = [trade, ...prev].slice(0, maxTrades);
 return updated;
 });
 
 // Update stats
 setStats(prev => {
 const newVolume = prev.totalVolume + (trade.size || 0);
 const newValue = prev.totalValue + ((trade.price || 0) * (trade.size || 0));
 const newCount = prev.tradeCount + 1;
 
 const exchanges = { ...prev.exchanges };
 const exchange = trade.exchange || 'UNKNOWN';
 exchanges[exchange] = (exchanges[exchange] || 0) + 1;
 
 return {
 totalVolume: newVolume,
 totalValue: newValue,
 tradeCount: newCount,
 avgPrice: newCount > 0 ? newValue / newVolume : 0,
 exchanges
 };
 });
 }
 }
 }, [messages, maxTrades]);

 // Format numbers
 const formatNumber = (num) => {
 if (num >= 1e9) return `${(num / 1e9).toFixed(2)}B`;
 if (num >= 1e6) return `${(num / 1e6).toFixed(2)}M`;
 if (num >= 1e3) return `${(num / 1e3).toFixed(2)}K`;
 return num.toFixed(0);
 };

 // Exchange color mapping
 const getExchangeColor = (exchange) => {
 const colors = {
 'NASDAQ': 'bg-blue-600',
 'NYSE': 'bg-purple-600',
 'ARCA': 'bg-green-600',
 'BATS': 'bg-yellow-600',
 'IEX': 'bg-cyan-600'
 };
 return colors[exchange] || 'bg-gray-600';
 };

 // Tape color
 const getTapeColor = (tape) => {
 const colors = {
 'A': 'text-purple-400', // NYSE
 'B': 'text-green-400', // Regional
 'C': 'text-blue-400' // NASDAQ
 };
 return colors[tape] || 'text-gray-400';
 };

 // Status indicator
 const StatusIndicator = () => (
 <div className="flex items-center space-x-2">
 <div className={`w-3 h-3 rounded-full ${
 status === 'connected' ? 'bg-green-500' : 
 status === 'connecting' ? 'bg-yellow-500 animate-pulse' : 
 'bg-red-500'
 }`}></div>
 <span className="text-sm text-gray-400">
 {status === 'connected' ? 'Live' : 
 status === 'connecting' ? 'Connecting...' : 
 'Disconnected'}
 </span>
 </div>
 );

 // Top exchanges
 const topExchanges = useMemo(() => {
 return Object.entries(stats.exchanges)
 .sort(([, a], [, b]) => b - a)
 .slice(0, 5);
 }, [stats.exchanges]);

 return (
 <div className="bg-gray-900 rounded-lg shadow-lg p-6 text-white">
 {/* Header */}
 <div className="flex items-center justify-between mb-6">
 <div>
 <h2 className="text-lg font-bold flex items-center space-x-2">
 <span> Lit Trades</span>
 <span className="text-blue-400">{ticker}</span>
 </h2>
 <p className="text-gray-400 text-sm mt-1">
 Exchange-based visible trades
 </p>
 </div>
 <StatusIndicator />
 </div>

 {/* Stats Cards */}
 <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
 <div className="bg-gray-800 rounded p-4">
 <div className="text-gray-400 text-xs uppercase mb-1">Total Volume</div>
 <div className="text-lg font-bold text-green-400">
 {formatNumber(stats.totalVolume)}
 </div>
 </div>
 <div className="bg-gray-800 rounded p-4">
 <div className="text-gray-400 text-xs uppercase mb-1">Total Value</div>
 <div className="text-lg font-bold text-blue-400">
 ${formatNumber(stats.totalValue)}
 </div>
 </div>
 <div className="bg-gray-800 rounded p-4">
 <div className="text-gray-400 text-xs uppercase mb-1">Trade Count</div>
 <div className="text-lg font-bold text-purple-400">
 {formatNumber(stats.tradeCount)}
 </div>
 </div>
 <div className="bg-gray-800 rounded p-4">
 <div className="text-gray-400 text-xs uppercase mb-1">Avg Price</div>
 <div className="text-lg font-bold text-yellow-400">
 ${stats.avgPrice.toFixed(2)}
 </div>
 </div>
 </div>

 {/* Top Exchanges */}
 {topExchanges.length > 0 && (
 <div className="mb-6">
 <h3 className="text-sm font-semibold text-gray-400 mb-3">Top Exchanges</h3>
 <div className="flex flex-wrap gap-2">
 {topExchanges.map(([exchange, count]) => (
 <div 
 key={exchange}
 className={`px-3 py-1 rounded-full text-sm font-medium ${getExchangeColor(exchange)}`}
 >
 {exchange}: {count}
 </div>
 ))}
 </div>
 </div>
 )}

 {/* Error Message */}
 {error && (
 <div className="bg-red-900/20 border border-red-700 rounded p-4 mb-4">
 <p className="text-red-400 text-sm">{error}</p>
 </div>
 )}

 {/* Waiting State */}
 {status === 'connected' && trades.length === 0 && (
 <div className="text-center py-12 text-gray-500">
 <p className="text-sm mb-2"> Waiting for lit trades...</p>
 <p className="text-sm">Data will appear during market hours</p>
 </div>
 )}

 {/* Trades Table */}
 {trades.length > 0 && (
 <div className="overflow-x-auto">
 <table className="min-w-full text-sm">
 <thead className="border-b border-gray-700 sticky top-0 bg-gray-900">
 <tr>
 <th className="px-3 py-2 text-left text-gray-400">Time</th>
 <th className="px-3 py-2 text-right text-gray-400">Price</th>
 <th className="px-3 py-2 text-right text-gray-400">Size</th>
 <th className="px-3 py-2 text-right text-gray-400">Value</th>
 <th className="px-3 py-2 text-center text-gray-400">Exchange</th>
 <th className="px-3 py-2 text-center text-gray-400">Tape</th>
 <th className="px-3 py-2 text-left text-gray-400">Conditions</th>
 </tr>
 </thead>
 <tbody>
 {trades.map((trade, idx) => {
 const value = (trade.price || 0) * (trade.size || 0);
 const time = trade.timestamp ? 
 new Date(trade.timestamp).toLocaleTimeString() : 
 '--:--:--';
 
 return (
 <tr 
 key={idx} 
 className="border-b border-gray-800 hover:bg-gray-800 transition-colors"
 >
 <td className="px-3 py-2 text-gray-300 font-mono text-xs">
 {time}
 </td>
 <td className="px-3 py-2 text-right font-semibold">
 ${trade.price?.toFixed(2)}
 </td>
 <td className="px-3 py-2 text-right text-green-400">
 {formatNumber(trade.size)}
 </td>
 <td className="px-3 py-2 text-right text-blue-400">
 ${formatNumber(value)}
 </td>
 <td className="px-3 py-2 text-center">
 <span className={`px-2 py-1 rounded text-xs font-medium ${
 getExchangeColor(trade.exchange)
 }`}>
 {trade.exchange || 'N/A'}
 </span>
 </td>
 <td className={`px-3 py-2 text-center font-bold ${
 getTapeColor(trade.tape)
 }`}>
 {trade.tape || '-'}
 </td>
 <td className="px-3 py-2 text-gray-400 text-xs">
 {trade.conditions?.join(', ') || '-'}
 </td>
 </tr>
 );
 })}
 </tbody>
 </table>
 </div>
 )}

 {/* Legend */}
 {trades.length > 0 && (
 <div className="mt-4 pt-4 border-t border-gray-800">
 <div className="text-xs text-gray-500 space-y-1">
 <p><strong>Tape:</strong> A = NYSE, B = Regional, C = NASDAQ</p>
 <p><strong>Conditions:</strong> @ = Regular, F = Sweep, T = Extended Hours, Z = Out of Sequence</p>
 </div>
 </div>
 )}
 </div>
 );
}
