/**
 * LiveMarketMovers Component
 * 
 * Real-time market movers from Unusual Whales.
 * Shows stocks with significant price/volume changes.
 * 
 * Usage:
 * ```jsx
 * <LiveMarketMovers maxItems={50} />
 * ```
 */

import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useWebSocketContext } from '../context/WebSocketContext';
import ConnectionStatus from './ConnectionStatus';

const LiveMarketMovers = ({ maxItems = 50, className = '' }) => {
 const navigate = useNavigate();
 const { subscribe, CHANNELS } = useWebSocketContext();
 
 const [movers, setMovers] = useState([]);
 const [filter, setFilter] = useState('all'); // 'all', 'gainers', 'losers'

 // Format percentage
 const formatPercent = (value) => {
 const sign = value >= 0 ? '+' : '';
 return `${sign}${value.toFixed(2)}%`;
 };

 // Format price
 const formatPrice = (value) => `$${value.toFixed(2)}`;

 // Format volume
 const formatVolume = (value) => {
 if (value >= 1000000) return `${(value / 1000000).toFixed(1)}M`;
 if (value >= 1000) return `${(value / 1000).toFixed(0)}K`;
 return value.toString();
 };

 // Handle new message
 const handleMessage = useCallback((data) => {
 // Expected: { symbol, price, change, changePercent, volume, timestamp }
 const newItem = {
 ...data,
 id: `${data.symbol}-${Date.now()}`,
 timestamp: data.timestamp || new Date().toISOString()
 };

 setMovers(prev => {
 // Update if exists, otherwise add
 const existing = prev.findIndex(m => m.symbol === newItem.symbol);
 if (existing >= 0) {
 const updated = [...prev];
 updated[existing] = newItem;
 return updated.sort((a, b) => Math.abs(b.changePercent) - Math.abs(a.changePercent));
 }
 return [newItem, ...prev].slice(0, maxItems)
 .sort((a, b) => Math.abs(b.changePercent) - Math.abs(a.changePercent));
 });
 }, [maxItems]);

 // Subscribe to market-movers channel
 useEffect(() => {
 const unsubscribe = subscribe(CHANNELS.MARKET_MOVERS, handleMessage);
 return unsubscribe;
 }, [subscribe, CHANNELS.MARKET_MOVERS, handleMessage]);

 // Navigate to Builder
 const handleSymbolClick = (symbol) => {
 navigate(`/builder?symbol=${symbol}`);
 };

 // Filter movers
 const filteredMovers = filter === 'all' 
 ? movers
 : filter === 'gainers'
 ? movers.filter(m => m.changePercent > 0)
 : movers.filter(m => m.changePercent < 0);

 return (
 <div className={`flex flex-col h-full bg-slate-900 rounded-lg border border-slate-700 ${className}`}>
 {/* Header */}
 <div className="flex items-center justify-between p-4 border-b border-slate-700/50">
 <div className="flex items-center gap-3">
 <h3 className="text-3xl font-medium text-[rgb(252, 251, 255)]"> Market Movers</h3>
 <ConnectionStatus channel={CHANNELS.MARKET_MOVERS} compact />
 </div>

 {/* Controls */}
 <div className="flex items-center gap-3">
 <select
 value={filter}
 onChange={(e) => setFilter(e.target.value)}
 className="px-3 py-1.5 rounded text-lg font-medium bg-slate-800 text-[rgb(252, 251, 255)] border border-slate-600 hover:border-slate-500"
 >
 <option value="all">All Movers</option>
 <option value="gainers"> Gainers</option>
 <option value="losers"> Losers</option>
 </select>

 <button
 onClick={() => setMovers([])}
 className="px-3 py-1.5 rounded text-lg font-medium bg-slate-800 text-gray-400 hover:text-[rgb(252, 251, 255)] hover:bg-slate-700"
 >
 🗑️ Clear
 </button>
 </div>
 </div>

 {/* Movers List */}
 <div className="flex-1 overflow-y-auto p-4 space-y-2">
 {filteredMovers.length === 0 ? (
 <div className="flex items-center justify-center h-full text-gray-400">
 <div className="text-center">
 <div className="text-3xl mb-2"></div>
 <div>Waiting for market movers data...</div>
 </div>
 </div>
 ) : (
 filteredMovers.map((mover) => (
 <div
 key={mover.id}
 className="flex items-center gap-4 p-3 bg-slate-800/50 hover:bg-slate-800 rounded border border-slate-700/30 hover:border-slate-600 transition-all"
 >
 {/* Symbol (clickable) */}
 <button
 onClick={() => handleSymbolClick(mover.symbol)}
 className="text-xl font-medium text-blue-400 hover:text-blue-300 hover:underline w-16 flex-shrink-0"
 >
 {mover.symbol}
 </button>

 {/* Price */}
 <div className="text-xl text-[rgb(252, 251, 255)] font-medium flex-shrink-0">
 {formatPrice(mover.price)}
 </div>

 {/* Change */}
 <div className={`text-xl font-medium flex-shrink-0 ${
 mover.changePercent >= 0 ? 'text-green-400' : 'text-red-400'
 }`}>
 {formatPercent(mover.changePercent)}
 </div>

 {/* Volume */}
 <div className="text-lg text-gray-400 flex-shrink-0">
 Vol: {formatVolume(mover.volume)}
 </div>

 {/* Change bar */}
 <div className="flex-1 ml-4">
 <div className="h-2 bg-slate-700 rounded-full overflow-hidden">
 <div
 className={`h-full ${
 mover.changePercent >= 0 ? 'bg-green-500' : 'bg-red-500'
 }`}
 style={{ 
 width: `${Math.min(Math.abs(mover.changePercent) * 2, 100)}%` 
 }}
 />
 </div>
 </div>
 </div>
 ))
 )}
 </div>
 </div>
 );
};

export default LiveMarketMovers;
