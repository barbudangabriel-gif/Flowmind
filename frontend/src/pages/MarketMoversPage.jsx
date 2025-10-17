import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

const API = window.API_BASE || process.env.REACT_APP_BACKEND_URL || "";

/**
 * MarketMoversPage - Full page view of market movers
 * 
 * Features:
 * - Shows top 20 in each category (vs 3 in widget)
 * - Manual refresh button + auto-refresh (30s)
 * - Click ticker → Navigate to Builder
 * - Dark theme only with responsive design
 * - Real-time badge when data is fresh (<60s old)
 */
const MarketMoversPage = () => {
 const navigate = useNavigate();
 const [data, setData] = useState({
 gainers: [],
 losers: [],
 most_active: []
 });
 const [loading, setLoading] = useState(true);
 const [error, setError] = useState(null);
 const [lastUpdate, setLastUpdate] = useState(null);
 const [refreshing, setRefreshing] = useState(false);

 const fetchMarketMovers = async (isManual = false) => {
 if (isManual) setRefreshing(true);
 
 try {
 const response = await fetch(`${API}/api/flow/market-movers`);
 const result = await response.json();
 
 if (result.status === 'success' && result.data) {
 setData(result.data);
 setLastUpdate(new Date());
 setError(null);
 } else {
 setError(result.error || 'Failed to fetch market movers');
 }
 } catch (err) {
 console.error('Error fetching market movers:', err);
 setError(err.message);
 // Fallback to mock data
 setData({
 gainers: [
 { symbol: 'TSLA', price: 250.50, change: 12.50, change_pct: 5.25 },
 { symbol: 'NVDA', price: 485.25, change: 18.75, change_pct: 4.02 },
 { symbol: 'AMD', price: 142.30, change: 5.80, change_pct: 4.25 }
 ],
 losers: [
 { symbol: 'AAPL', price: 178.30, change: -4.20, change_pct: -2.30 },
 { symbol: 'MSFT', price: 378.50, change: -8.50, change_pct: -2.20 }
 ],
 most_active: [
 { symbol: 'SPY', price: 445.80, volume: 85000000, change_pct: 0.50 },
 { symbol: 'QQQ', price: 378.20, volume: 52000000, change_pct: 0.80 }
 ]
 });
 setLastUpdate(new Date());
 } finally {
 setLoading(false);
 setRefreshing(false);
 }
 };

 useEffect(() => {
 fetchMarketMovers();
 
 // Auto-refresh every 30 seconds
 const interval = setInterval(() => fetchMarketMovers(false), 30000);
 
 return () => clearInterval(interval);
 }, []);

 const handleTickerClick = (ticker) => {
 navigate(`/builder?symbol=${ticker}`);
 };

 const isDataFresh = () => {
 if (!lastUpdate) return false;
 const ageSeconds = (new Date() - lastUpdate) / 1000;
 return ageSeconds < 60;
 };

 const renderTable = (stocks, type) => {
 if (stocks.length === 0) {
 return (
 <div className="text-slate-500 text-center py-8">
 No data available
 </div>
 );
 }

 let headerColor = 'text-white';
 let accentColor = 'text-white';
 
 if (type === 'gainers') {
 headerColor = 'text-emerald-400';
 accentColor = 'text-emerald-400';
 } else if (type === 'losers') {
 headerColor = 'text-red-400';
 accentColor = 'text-red-400';
 } else if (type === 'active') {
 headerColor = 'text-blue-400';
 accentColor = 'text-blue-400';
 }

 return (
 <div className="overflow-x-auto">
 <table className="w-full">
 <thead>
 <tr className="border-b border-slate-700">
 <th className="text-left py-3 px-4 text-slate-400 font-semibold text-sm">#</th>
 <th className="text-left py-3 px-4 text-slate-400 font-semibold text-sm">Ticker</th>
 <th className="text-right py-3 px-4 text-slate-400 font-semibold text-sm">Price</th>
 <th className="text-right py-3 px-4 text-slate-400 font-semibold text-sm">Change %</th>
 <th className="text-right py-3 px-4 text-slate-400 font-semibold text-sm">Volume</th>
 </tr>
 </thead>
 <tbody>
 {stocks.slice(0, 20).map((stock, index) => {
 const changePct = stock.change_pct || 0;
 const isPositive = changePct > 0;
 
 return (
 <tr 
 key={stock.ticker}
 onClick={() => handleTickerClick(stock.ticker)}
 className="border-b border-slate-700/50 hover:bg-slate-700/30 cursor-pointer transition-colors"
 >
 <td className="py-3 px-4 text-slate-500 text-sm">{index + 1}</td>
 <td className="py-3 px-4">
 <span className="font-bold text-white">{stock.ticker}</span>
 </td>
 <td className="py-3 px-4 text-right text-slate-300">
 ${stock.price?.toFixed(2) || '0.00'}
 </td>
 <td className={`py-3 px-4 text-right font-semibold ${accentColor}`}>
 {isPositive ? '+' : ''}{changePct.toFixed(2)}%
 </td>
 <td className="py-3 px-4 text-right text-slate-400 text-sm">
 {stock.volume ? (stock.volume / 1000000).toFixed(1) + 'M' : 'N/A'}
 </td>
 </tr>
 );
 })}
 </tbody>
 </table>
 </div>
 );
 };

 if (loading) {
 return (
 <div className="min-h-screen bg-slate-900 p-6">
 <div className="max-w-7xl mx-auto">
 <div className="bg-slate-800 rounded-lg p-6 shadow-lg">
 <div className="h-8 bg-slate-700 rounded w-48 mb-6 animate-pulse"></div>
 <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
 {[1, 2, 3].map(i => (
 <div key={i} className="space-y-3">
 <div className="h-6 bg-slate-700 rounded w-32 animate-pulse"></div>
 <div className="h-64 bg-slate-700 rounded animate-pulse"></div>
 </div>
 ))}
 </div>
 </div>
 </div>
 </div>
 );
 }

 return (
 <div className="min-h-screen bg-slate-900 p-6">
 <div className="max-w-7xl mx-auto">
 {/* Header */}
 <div className="bg-slate-800 rounded-lg p-6 shadow-lg mb-6">
 <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
 <div>
 <h1 className="text-3xl font-bold text-white flex items-center gap-2">
 Market Movers
 </h1>
 <p className="text-slate-400 mt-1">
 Top gainers, losers, and most active stocks
 </p>
 </div>
 <div className="flex items-center gap-4">
 {lastUpdate && (
 <div className="text-sm text-slate-400">
 Updated: {lastUpdate.toLocaleTimeString()}
 {isDataFresh() && (
 <span className="ml-2 inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-emerald-900/30 text-emerald-400 border border-emerald-500/30">
 Live
 </span>
 )}
 </div>
 )}
 <button
 onClick={() => fetchMarketMovers(true)}
 disabled={refreshing}
 className="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-slate-700 disabled:text-slate-500 text-white rounded-lg font-medium transition-colors flex items-center gap-2"
 >
 {refreshing ? (
 <>
 <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
 <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none"></circle>
 <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
 </svg>
 Refreshing...
 </>
 ) : (
 <>
 🔄 Refresh
 </>
 )}
 </button>
 </div>
 </div>
 </div>

 {/* Error State */}
 {error && (
 <div className="bg-red-900/30 border border-red-500/30 rounded-lg p-4 mb-6">
 <div className="flex items-center gap-2 text-red-400">
 <span className="text-xl"></span>
 <span>{error}</span>
 </div>
 </div>
 )}

 {/* Market Movers Grid */}
 <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
 {/* Gainers */}
 <div className="bg-slate-800 rounded-lg p-6 shadow-lg">
 <h2 className="text-xl font-semibold text-emerald-400 mb-4 flex items-center gap-2">
 Top Gainers
 <span className="text-sm text-slate-400 font-medium">
 ({data.gainers.length})
 </span>
 </h2>
 {renderTable(data.gainers, 'gainers')}
 </div>

 {/* Losers */}
 <div className="bg-slate-800 rounded-lg p-6 shadow-lg">
 <h2 className="text-xl font-semibold text-red-400 mb-4 flex items-center gap-2">
 Top Losers
 <span className="text-sm text-slate-400 font-medium">
 ({data.losers.length})
 </span>
 </h2>
 {renderTable(data.losers, 'losers')}
 </div>

 {/* Most Active */}
 <div className="bg-slate-800 rounded-lg p-6 shadow-lg">
 <h2 className="text-xl font-semibold text-blue-400 mb-4 flex items-center gap-2">
 🔵 Most Active
 <span className="text-sm text-slate-400 font-medium">
 ({data.most_active.length})
 </span>
 </h2>
 {renderTable(data.most_active, 'active')}
 </div>
 </div>
 </div>
 </div>
 );
};

export default MarketMoversPage;
