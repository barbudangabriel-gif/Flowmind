import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

const API = window.API_BASE || process.env.REACT_APP_BACKEND_URL || "";

/**
 * CongressTradesPage - Congressional trading activity tracker
 * 
 * Features:
 * - Table showing politician stock trades
 * - Filters: politician, party, transaction type, date range
 * - Summary cards: total buy/sell, this week count, most active
 * - Party badges: blue (D), red (R), purple (I)
 * - Click ticker → Navigate to Builder
 * - Dark theme only with responsive design
 */
const CongressTradesPage = () => {
 const navigate = useNavigate();
 const [trades, setTrades] = useState([]);
 const [loading, setLoading] = useState(true);
 const [error, setError] = useState(null);
 
 // Filters
 const [tickerFilter, setTickerFilter] = useState('');
 const [politicianFilter, setPoliticianFilter] = useState('');
 const [partyFilter, setPartyFilter] = useState('');
 const [typeFilter, setTypeFilter] = useState('');
 const [limit, setLimit] = useState(100);

 const fetchCongressTrades = async () => {
 setLoading(true);
 
 try {
 const params = new URLSearchParams();
 if (tickerFilter) params.append('ticker', tickerFilter);
 if (politicianFilter) params.append('politician', politicianFilter);
 if (partyFilter) params.append('party', partyFilter);
 if (typeFilter) params.append('transaction_type', typeFilter);
 params.append('limit', limit);
 
 const response = await fetch(`${API}/api/flow/congress-trades?${params}`);
 const result = await response.json();
 
 if (result.status === 'success') {
 setTrades(result.data || []);
 setError(null);
 } else {
 setError(result.error || 'Failed to fetch congress trades');
 }
 } catch (err) {
 console.error('Error fetching congress trades:', err);
 setError(err.message);
 // Fallback to mock data
 setTrades([
 { ticker: 'NVDA', politician: 'Nancy Pelosi', party: 'D', transaction_type: 'BUY', amount: 500000, date: '2025-10-15' },
 { ticker: 'MSFT', politician: 'Josh Gottheimer', party: 'D', transaction_type: 'BUY', amount: 250000, date: '2025-10-14' },
 { ticker: 'TSLA', politician: 'Mark Green', party: 'R', transaction_type: 'SELL', amount: 150000, date: '2025-10-13' }
 ]);
 } finally {
 setLoading(false);
 }
 };

 useEffect(() => {
 fetchCongressTrades();
 }, [tickerFilter, politicianFilter, partyFilter, typeFilter, limit]);

 const handleTickerClick = (ticker) => {
 navigate(`/builder?symbol=${ticker}`);
 };

 const getPartyBadge = (party) => {
 const colors = {
 'D': 'bg-blue-900/30 text-blue-400 border-blue-500/30',
 'R': 'bg-red-900/30 text-red-400 border-red-500/30',
 'I': 'bg-purple-900/30 text-purple-400 border-purple-500/30'
 };
 
 return (
 <span className={`inline-flex items-center px-2 py-1 rounded text-xs font-medium border ${colors[party] || 'bg-slate-700 text-slate-300 border-slate-600'}`}>
 {party === 'D' ? 'Democrat' : party === 'R' ? 'Republican' : 'Independent'}
 </span>
 );
 };

 const getTypeBadge = (type) => {
 const isBuy = type === 'BUY';
 return (
 <span className={`inline-flex items-center px-2 py-1 rounded text-xs font-bold ${isBuy ? 'bg-emerald-900/30 text-emerald-400 border border-emerald-500/30' : 'bg-red-900/30 text-red-400 border border-red-500/30'}`}>
 {type}
 </span>
 );
 };

 // Calculate summary stats
 const totalBuy = trades.filter(t => t.type === 'BUY').length;
 const totalSell = trades.filter(t => t.type === 'SELL').length;
 const thisWeek = trades.filter(t => {
 const tradeDate = new Date(t.date);
 const weekAgo = new Date();
 weekAgo.setDate(weekAgo.getDate() - 7);
 return tradeDate >= weekAgo;
 }).length;
 
 // Most active politician
 const politicianCounts = {};
 trades.forEach(t => {
 politicianCounts[t.politician_name] = (politicianCounts[t.politician_name] || 0) + 1;
 });
 const mostActive = Object.keys(politicianCounts).length > 0
 ? Object.entries(politicianCounts).sort((a, b) => b[1] - a[1])[0][0]
 : 'N/A';

 if (loading && trades.length === 0) {
 return (
 <div className="min-h-screen bg-slate-900 p-6">
 <div className="max-w-7xl mx-auto">
 <div className="bg-slate-800 rounded-lg p-6 shadow-lg">
 <div className="h-8 bg-slate-700 rounded w-64 mb-6 animate-pulse"></div>
 <div className="h-64 bg-slate-700 rounded animate-pulse"></div>
 </div>
 </div>
 </div>
 );
 }

 return (
 <div className="min-h-screen bg-slate-900 p-6">
 <div className="max-w-7xl mx-auto space-y-6">
 {/* Header */}
 <div className="bg-slate-800 rounded-lg p-6 shadow-lg">
 <h1 className="text-3xl font-bold text-white flex items-center gap-2">
 🏛️ Congress Trading Activity
 </h1>
 <p className="text-slate-400 mt-1">
 Track stock purchases and sales by members of Congress
 </p>
 </div>

 {/* Summary Cards */}
 <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
 <div className="bg-slate-800 rounded-lg p-4 shadow-lg">
 <div className="text-slate-400 text-sm mb-1">Total Buy</div>
 <div className="text-2xl font-bold text-emerald-400">{totalBuy}</div>
 </div>
 <div className="bg-slate-800 rounded-lg p-4 shadow-lg">
 <div className="text-slate-400 text-sm mb-1">Total Sell</div>
 <div className="text-2xl font-bold text-red-400">{totalSell}</div>
 </div>
 <div className="bg-slate-800 rounded-lg p-4 shadow-lg">
 <div className="text-slate-400 text-sm mb-1">This Week</div>
 <div className="text-2xl font-bold text-blue-400">{thisWeek}</div>
 </div>
 <div className="bg-slate-800 rounded-lg p-4 shadow-lg">
 <div className="text-slate-400 text-sm mb-1">Most Active</div>
 <div className="text-lg font-bold text-white truncate">{mostActive}</div>
 </div>
 </div>

 {/* Filters */}
 <div className="bg-slate-800 rounded-lg p-6 shadow-lg">
 <h2 className="text-lg font-semibold text-white mb-4"> Filters</h2>
 <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
 <div>
 <label className="block text-slate-400 text-sm mb-2">Ticker</label>
 <input
 type="text"
 value={tickerFilter}
 onChange={(e) => setTickerFilter(e.target.value.toUpperCase())}
 placeholder="e.g., NVDA"
 className="w-full bg-slate-700 border border-slate-600 rounded px-3 py-2 text-white placeholder-slate-500 focus:outline-none focus:border-blue-500"
 />
 </div>
 <div>
 <label className="block text-slate-400 text-sm mb-2">Politician</label>
 <input
 type="text"
 value={politicianFilter}
 onChange={(e) => setPoliticianFilter(e.target.value)}
 placeholder="e.g., Pelosi"
 className="w-full bg-slate-700 border border-slate-600 rounded px-3 py-2 text-white placeholder-slate-500 focus:outline-none focus:border-blue-500"
 />
 </div>
 <div>
 <label className="block text-slate-400 text-sm mb-2">Party</label>
 <select
 value={partyFilter}
 onChange={(e) => setPartyFilter(e.target.value)}
 className="w-full bg-slate-700 border border-slate-600 rounded px-3 py-2 text-white focus:outline-none focus:border-blue-500"
 >
 <option value="">All</option>
 <option value="D">Democrat</option>
 <option value="R">Republican</option>
 <option value="I">Independent</option>
 </select>
 </div>
 <div>
 <label className="block text-slate-400 text-sm mb-2">Transaction Type</label>
 <select
 value={typeFilter}
 onChange={(e) => setTypeFilter(e.target.value)}
 className="w-full bg-slate-700 border border-slate-600 rounded px-3 py-2 text-white focus:outline-none focus:border-blue-500"
 >
 <option value="">All</option>
 <option value="BUY">Buy</option>
 <option value="SELL">Sell</option>
 <option value="EXCHANGE">Exchange</option>
 </select>
 </div>
 </div>
 <div className="mt-4 flex gap-2">
 <button
 onClick={() => {
 setTickerFilter('');
 setPoliticianFilter('');
 setPartyFilter('');
 setTypeFilter('');
 }}
 className="px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded font-medium transition-colors"
 >
 Clear Filters
 </button>
 <button
 onClick={fetchCongressTrades}
 className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded font-medium transition-colors"
 >
 🔄 Refresh
 </button>
 </div>
 </div>

 {/* Error State */}
 {error && (
 <div className="bg-red-900/30 border border-red-500/30 rounded-lg p-4">
 <div className="flex items-center gap-2 text-red-400">
 <span className="text-xl"></span>
 <span>{error}</span>
 </div>
 </div>
 )}

 {/* Trades Table */}
 <div className="bg-slate-800 rounded-lg p-6 shadow-lg">
 <h2 className="text-lg font-semibold text-white mb-4">
 Trades ({trades.length})
 </h2>
 
 {trades.length === 0 ? (
 <div className="text-slate-500 text-center py-8">
 No trades found. Try adjusting filters.
 </div>
 ) : (
 <div className="overflow-x-auto">
 <table className="w-full">
 <thead>
 <tr className="border-b border-slate-700">
 <th className="text-left py-3 px-4 text-slate-400 font-semibold text-sm">Date</th>
 <th className="text-left py-3 px-4 text-slate-400 font-semibold text-sm">Politician</th>
 <th className="text-left py-3 px-4 text-slate-400 font-semibold text-sm">Party</th>
 <th className="text-left py-3 px-4 text-slate-400 font-semibold text-sm">Ticker</th>
 <th className="text-left py-3 px-4 text-slate-400 font-semibold text-sm">Type</th>
 <th className="text-left py-3 px-4 text-slate-400 font-semibold text-sm">Amount</th>
 <th className="text-right py-3 px-4 text-slate-400 font-semibold text-sm">Price</th>
 </tr>
 </thead>
 <tbody>
 {trades.map((trade, index) => (
 <tr 
 key={index}
 className="border-b border-slate-700/50 hover:bg-slate-700/30 transition-colors"
 >
 <td className="py-3 px-4 text-slate-300 text-sm">
 {new Date(trade.date).toLocaleDateString()}
 </td>
 <td className="py-3 px-4 text-white font-medium">
 {trade.politician_name}
 </td>
 <td className="py-3 px-4">
 {getPartyBadge(trade.party)}
 </td>
 <td 
 className="py-3 px-4 text-blue-400 font-bold cursor-pointer hover:text-blue-300"
 onClick={() => handleTickerClick(trade.ticker)}
 >
 {trade.ticker}
 </td>
 <td className="py-3 px-4">
 {getTypeBadge(trade.type)}
 </td>
 <td className="py-3 px-4 text-slate-300 text-sm">
 {trade.amount}
 </td>
 <td className="py-3 px-4 text-right text-slate-300">
 {trade.price ? `$${trade.price.toFixed(2)}` : 'N/A'}
 </td>
 </tr>
 ))}
 </tbody>
 </table>
 </div>
 )}
 </div>
 </div>
 </div>
 );
};

export default CongressTradesPage;
