/**
 * LiveCongressFeed Component
 * 
 * Real-time Congressional stock trades from Unusual Whales.
 * Shows trades made by US Congress members.
 * 
 * Usage:
 * ```jsx
 * <LiveCongressFeed maxItems={50} />
 * ```
 */

import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useWebSocketContext } from '../context/WebSocketContext';
import ConnectionStatus from './ConnectionStatus';

const LiveCongressFeed = ({ maxItems = 50, className = '' }) => {
 const navigate = useNavigate();
 const { subscribe, CHANNELS } = useWebSocketContext();
 
 const [trades, setTrades] = useState([]);
 const [filter, setFilter] = useState('all'); // 'all', 'buy', 'sell'

 // Format currency range
 const formatRange = (min, max) => {
 const formatValue = (value) => {
 if (value >= 1000000) return `$${(value / 1000000).toFixed(1)}M`;
 if (value >= 1000) return `$${(value / 1000).toFixed(0)}K`;
 return `$${value}`;
 };
 return `${formatValue(min)} - ${formatValue(max)}`;
 };

 // Format date
 const formatDate = (dateStr) => {
 const date = new Date(dateStr);
 return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
 };

 // Handle new message
 const handleMessage = useCallback((data) => {
 // Expected: { representative, symbol, transaction_type, amount_min, amount_max, transaction_date, disclosure_date, party }
 const newItem = {
 ...data,
 id: `${Date.now()}-${Math.random()}`,
 timestamp: data.disclosure_date || new Date().toISOString()
 };

 setTrades(prev => [newItem, ...prev].slice(0, maxItems));
 }, [maxItems]);

 // Subscribe to congress channel
 useEffect(() => {
 const unsubscribe = subscribe(CHANNELS.CONGRESS, handleMessage);
 return unsubscribe;
 }, [subscribe, CHANNELS.CONGRESS, handleMessage]);

 // Navigate to Builder
 const handleSymbolClick = (symbol) => {
 navigate(`/builder?symbol=${symbol}`);
 };

 // Filter trades
 const filteredTrades = filter === 'all'
 ? trades
 : trades.filter(t => t.transaction_type?.toLowerCase().includes(filter));

 // Get party badge
 const getPartyBadge = (party) => {
 if (!party) return null;
 const colors = {
 'D': 'bg-blue-500/20 text-blue-400',
 'R': 'bg-red-500/20 text-red-400',
 'I': 'bg-gray-500/20 text-gray-400'
 };
 return (
 <span className={`text-lg px-2 py-0.5 rounded font-medium ${colors[party] || colors['I']}`}>
 {party}
 </span>
 );
 };

 // Get transaction badge
 const getTransactionBadge = (type) => {
 const isBuy = type?.toLowerCase().includes('purchase');
 return (
 <span className={`text-lg px-2 py-0.5 rounded font-medium ${
 isBuy 
 ? 'bg-green-500/20 text-green-400' 
 : 'bg-red-500/20 text-red-400'
 }`}>
 {isBuy ? ' BUY' : ' SELL'}
 </span>
 );
 };

 return (
 <div className={`flex flex-col h-full bg-slate-900 rounded-lg border border-slate-700 ${className}`}>
 {/* Header */}
 <div className="flex items-center justify-between p-4 border-b border-slate-700/50">
 <div className="flex items-center gap-3">
 <h3 className="text-3xl font-medium text-[rgb(252, 251, 255)]">🏛️ Congress Trades</h3>
 <ConnectionStatus channel={CHANNELS.CONGRESS} compact />
 </div>

 {/* Controls */}
 <div className="flex items-center gap-3">
 <select
 value={filter}
 onChange={(e) => setFilter(e.target.value)}
 className="px-3 py-1.5 rounded text-lg font-medium bg-slate-800 text-[rgb(252, 251, 255)] border border-slate-600 hover:border-slate-500"
 >
 <option value="all">All Trades</option>
 <option value="buy"> Buys Only</option>
 <option value="sell"> Sells Only</option>
 </select>

 <button
 onClick={() => setTrades([])}
 className="px-3 py-1.5 rounded text-lg font-medium bg-slate-800 text-gray-400 hover:text-[rgb(252, 251, 255)] hover:bg-slate-700"
 >
 🗑️ Clear
 </button>
 </div>
 </div>

 {/* Trades List */}
 <div className="flex-1 overflow-y-auto p-4 space-y-2">
 {filteredTrades.length === 0 ? (
 <div className="flex items-center justify-center h-full text-gray-400">
 <div className="text-center">
 <div className="text-3xl mb-2">🏛️</div>
 <div>Waiting for congressional trades...</div>
 <div className="text-lg mt-1">Disclosures will appear here in real-time</div>
 </div>
 </div>
 ) : (
 filteredTrades.map((trade) => (
 <div
 key={trade.id}
 className="flex flex-col gap-2 p-3 bg-slate-800/50 hover:bg-slate-800 rounded border border-slate-700/30 hover:border-slate-600 transition-all"
 >
 {/* Top row: Representative & Party */}
 <div className="flex items-center gap-3">
 <div className="text-xl font-medium text-[rgb(252, 251, 255)] flex-1">
 {trade.representative}
 </div>
 {getPartyBadge(trade.party)}
 </div>

 {/* Bottom row: Trade details */}
 <div className="flex items-center gap-4">
 {/* Symbol (clickable) */}
 <button
 onClick={() => handleSymbolClick(trade.symbol)}
 className="text-xl font-medium text-blue-400 hover:text-blue-300 hover:underline flex-shrink-0"
 >
 {trade.symbol}
 </button>

 {/* Transaction type */}
 {getTransactionBadge(trade.transaction_type)}

 {/* Amount range */}
 <div className="text-lg text-gray-300 flex-shrink-0">
 {formatRange(trade.amount_min, trade.amount_max)}
 </div>

 {/* Transaction date */}
 <div className="text-lg text-gray-400 ml-auto flex-shrink-0">
 {formatDate(trade.transaction_date)}
 </div>

 {/* Disclosure lag indicator */}
 {(() => {
 const transDate = new Date(trade.transaction_date);
 const discDate = new Date(trade.disclosure_date);
 const lagDays = Math.floor((discDate - transDate) / (1000 * 60 * 60 * 24));
 if (lagDays > 45) {
 return (
 <div className="text-lg px-2 py-0.5 rounded bg-orange-500/20 text-orange-400 font-medium flex-shrink-0">
 LATE ({lagDays}d)
 </div>
 );
 }
 return null;
 })()}
 </div>
 </div>
 ))
 )}
 </div>
 </div>
 );
};

export default LiveCongressFeed;
