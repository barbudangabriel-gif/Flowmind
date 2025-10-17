import React, { useState, useEffect, useMemo } from 'react';
import useWebSocket from '../hooks/useWebSocket';

/**
 * LiveGexStrikeExpiryFeed - Most granular GEX data visualization
 * 
 * Displays real-time gamma exposure broken down by BOTH strike AND expiration.
 * Perfect for zero-DTE (0DTE) analysis and gamma squeeze detection.
 * 
 * @param {Object} props
 * @param {string} props.ticker - Stock symbol (e.g., "SPY", "TSLA")
 * @param {boolean} props.autoRefresh - Auto-refresh on new data (default: true)
 * @param {string} props.view - Display mode: "heatmap" | "table" | "chart" (default: "heatmap")
 */
export default function LiveGexStrikeExpiryFeed({ 
 ticker = 'SPY', 
 autoRefresh = true,
 view = 'heatmap'
}) {
 const [gexData, setGexData] = useState([]);
 const [selectedExpiry, setSelectedExpiry] = useState(null);
 
 const wsUrl = `/api/stream/ws/gex-strike-expiry/${ticker.toUpperCase()}`;
 const { messages, status, error } = useWebSocket(wsUrl);

 // Process incoming messages
 useEffect(() => {
 if (messages.length > 0 && autoRefresh) {
 const latestMessage = messages[messages.length - 1];
 if (latestMessage?.data) {
 setGexData(prev => {
 // Add new data point
 const updated = [...prev, latestMessage.data];
 // Keep last 1000 data points to prevent memory issues
 return updated.slice(-1000);
 });
 }
 }
 }, [messages, autoRefresh]);

 // Group data by expiry and strike
 const gexMatrix = useMemo(() => {
 const matrix = {};
 
 gexData.forEach(item => {
 const { expiry, strike, net_gex, call_gex, put_gex } = item;
 
 if (!matrix[expiry]) {
 matrix[expiry] = {};
 }
 
 if (!matrix[expiry][strike]) {
 matrix[expiry][strike] = {
 net_gex: 0,
 call_gex: 0,
 put_gex: 0,
 count: 0
 };
 }
 
 // Average if multiple updates for same strike/expiry
 const existing = matrix[expiry][strike];
 existing.net_gex = (existing.net_gex * existing.count + net_gex) / (existing.count + 1);
 existing.call_gex = (existing.call_gex * existing.count + call_gex) / (existing.count + 1);
 existing.put_gex = (existing.put_gex * existing.count + put_gex) / (existing.count + 1);
 existing.count += 1;
 });
 
 return matrix;
 }, [gexData]);

 // Get sorted expiries and strikes
 const expiries = useMemo(() => {
 return Object.keys(gexMatrix).sort();
 }, [gexMatrix]);

 const strikes = useMemo(() => {
 const allStrikes = new Set();
 Object.values(gexMatrix).forEach(expiryData => {
 Object.keys(expiryData).forEach(strike => allStrikes.add(Number(strike)));
 });
 return Array.from(allStrikes).sort((a, b) => a - b);
 }, [gexMatrix]);

 // Calculate color for heatmap
 const getGexColor = (netGex) => {
 if (!netGex) return 'bg-gray-800';
 
 const absGex = Math.abs(netGex);
 const maxGex = Math.max(...gexData.map(d => Math.abs(d.net_gex || 0)));
 const intensity = Math.min(absGex / maxGex, 1);
 
 if (netGex > 0) {
 // Positive GEX (calls) - Green
 const greenShade = Math.floor(intensity * 9);
 return `bg-green-${greenShade}00`;
 } else {
 // Negative GEX (puts) - Red
 const redShade = Math.floor(intensity * 9);
 return `bg-red-${redShade}00`;
 }
 };

 // Format GEX value
 const formatGex = (value) => {
 if (!value) return '0';
 const absValue = Math.abs(value);
 if (absValue >= 1e9) return `${(value / 1e9).toFixed(1)}B`;
 if (absValue >= 1e6) return `${(value / 1e6).toFixed(1)}M`;
 if (absValue >= 1e3) return `${(value / 1e3).toFixed(1)}K`;
 return value.toFixed(0);
 };

 // Render connection status
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

 // Render heatmap view
 const HeatmapView = () => (
 <div className="overflow-x-auto">
 <table className="min-w-full text-sm">
 <thead>
 <tr className="border-b border-gray-700">
 <th className="px-3 py-2 text-left text-gray-400 sticky left-0 bg-gray-900">
 Strike
 </th>
 {expiries.map(expiry => (
 <th 
 key={expiry} 
 className="px-3 py-2 text-center text-gray-400 cursor-pointer hover:bg-gray-800"
 onClick={() => setSelectedExpiry(selectedExpiry === expiry ? null : expiry)}
 >
 {new Date(expiry).toLocaleDateString('en-US', { 
 month: 'short', 
 day: 'numeric' 
 })}
 {selectedExpiry === expiry && ' ✓'}
 </th>
 ))}
 </tr>
 </thead>
 <tbody>
 {strikes.map(strike => (
 <tr key={strike} className="border-b border-gray-800 hover:bg-gray-800">
 <td className="px-3 py-2 font-medium text-gray-300 sticky left-0 bg-gray-900">
 ${strike}
 </td>
 {expiries.map(expiry => {
 const data = gexMatrix[expiry]?.[strike];
 const netGex = data?.net_gex || 0;
 
 return (
 <td 
 key={`${expiry}-${strike}`}
 className={`px-3 py-2 text-center cursor-pointer transition-colors ${
 getGexColor(netGex)
 }`}
 title={`Strike: $${strike}\nExpiry: ${expiry}\nNet GEX: ${formatGex(netGex)}\nCall GEX: ${formatGex(data?.call_gex || 0)}\nPut GEX: ${formatGex(data?.put_gex || 0)}`}
 >
 <span className={netGex ? 'font-semibold' : 'text-gray-600'}>
 {formatGex(netGex)}
 </span>
 </td>
 );
 })}
 </tr>
 ))}
 </tbody>
 </table>
 </div>
 );

 // Render table view
 const TableView = () => (
 <div className="overflow-x-auto">
 <table className="min-w-full text-sm">
 <thead className="border-b border-gray-700">
 <tr>
 <th className="px-3 py-2 text-left text-gray-400">Expiry</th>
 <th className="px-3 py-2 text-right text-gray-400">Strike</th>
 <th className="px-3 py-2 text-right text-gray-400">Net GEX</th>
 <th className="px-3 py-2 text-right text-gray-400">Call GEX</th>
 <th className="px-3 py-2 text-right text-gray-400">Put GEX</th>
 </tr>
 </thead>
 <tbody>
 {gexData.slice(-50).reverse().map((item, idx) => (
 <tr key={idx} className="border-b border-gray-800 hover:bg-gray-800">
 <td className="px-3 py-2 text-gray-300">
 {new Date(item.expiry).toLocaleDateString()}
 </td>
 <td className="px-3 py-2 text-right font-medium">${item.strike}</td>
 <td className={`px-3 py-2 text-right font-semibold ${
 item.net_gex > 0 ? 'text-green-400' : 'text-red-400'
 }`}>
 {formatGex(item.net_gex)}
 </td>
 <td className="px-3 py-2 text-right text-green-300">
 {formatGex(item.call_gex)}
 </td>
 <td className="px-3 py-2 text-right text-red-300">
 {formatGex(item.put_gex)}
 </td>
 </tr>
 ))}
 </tbody>
 </table>
 </div>
 );

 return (
 <div className="bg-gray-900 rounded-lg shadow-lg p-6 text-white">
 {/* Header */}
 <div className="flex items-center justify-between mb-6">
 <div>
 <h2 className="text-2xl font-bold">Gamma Exposure Matrix</h2>
 <p className="text-gray-400 text-sm mt-1">
 {ticker} - Strike × Expiry GEX
 </p>
 </div>
 <StatusIndicator />
 </div>

 {/* View Controls */}
 <div className="flex items-center space-x-4 mb-4">
 <button
 onClick={() => setGexData([])}
 className="px-4 py-2 bg-gray-800 hover:bg-gray-700 rounded text-sm transition-colors"
 >
 Clear Data
 </button>
 <div className="flex space-x-2">
 {['heatmap', 'table'].map(v => (
 <button
 key={v}
 onClick={() => setSelectedExpiry(null) || true}
 className={`px-3 py-1 rounded text-sm transition-colors ${
 view === v 
 ? 'bg-blue-600 text-white' 
 : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
 }`}
 >
 {v.charAt(0).toUpperCase() + v.slice(1)}
 </button>
 ))}
 </div>
 <span className="text-sm text-gray-500">
 {gexData.length} data points
 </span>
 </div>

 {/* Error Message */}
 {error && (
 <div className="bg-red-900/20 border border-red-700 rounded p-4 mb-4">
 <p className="text-red-400 text-sm">{error}</p>
 </div>
 )}

 {/* Content */}
 {status === 'connected' && gexData.length === 0 && (
 <div className="text-center py-12 text-gray-500">
 <p className="text-lg mb-2"> Waiting for GEX data...</p>
 <p className="text-sm">Data will appear during market hours</p>
 </div>
 )}

 {gexData.length > 0 && (
 view === 'heatmap' ? <HeatmapView /> : <TableView />
 )}

 {/* Legend */}
 {gexData.length > 0 && view === 'heatmap' && (
 <div className="mt-4 flex items-center justify-center space-x-6 text-sm text-gray-400">
 <div className="flex items-center space-x-2">
 <div className="w-4 h-4 bg-green-500 rounded"></div>
 <span>Positive GEX (Calls)</span>
 </div>
 <div className="flex items-center space-x-2">
 <div className="w-4 h-4 bg-red-500 rounded"></div>
 <span>Negative GEX (Puts)</span>
 </div>
 </div>
 )}
 </div>
 );
}
