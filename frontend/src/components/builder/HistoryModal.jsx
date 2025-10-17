// components/builder/HistoryModal.jsx
import React, { useState, useEffect } from 'react';

export default function HistoryModal({ symbol, expiry, open, onClose }) {
 const [data, setData] = useState(null);
 const [loading, setLoading] = useState(false);
 const [timeframe, setTimeframe] = useState('1M');
 const [chartType, setChartType] = useState('line');

 useEffect(() => {
 if (!open || !symbol || !expiry) return;
 
 let alive = true;
 (async () => {
 setLoading(true);
 try {
 const response = await fetch(`/api/builder/history?symbol=${symbol}&expiry=${expiry}&timeframe=${timeframe}`);
 const result = await response.json();
 
 if (alive) {
 if (result && result.underlying) {
 setData(result);
 } else {
 // Fallback demo data
 const now = Date.now();
 const days = timeframe === '1D' ? 1 : timeframe === '1W' ? 7 : timeframe === '2W' ? 14 : timeframe === '1M' ? 30 : timeframe === '3M' ? 90 : 180;
 const demoData = {
 underlying: Array.from({length: days}, (_, i) => ({
 t: now - (days - i) * 24 * 60 * 60 * 1000,
 p: 250 + Math.sin(i * 0.1) * 20 + (Math.random() - 0.5) * 10
 })),
 strategy: Array.from({length: days}, (_, i) => ({
 t: now - (days - i) * 24 * 60 * 60 * 1000,
 p: 50 + Math.sin(i * 0.15) * 30 + (Math.random() - 0.5) * 15
 })),
 iv: Array.from({length: days}, (_, i) => ({
 t: now - (days - i) * 24 * 60 * 60 * 1000,
 iv: 0.35 + Math.sin(i * 0.2) * 0.15 + (Math.random() - 0.5) * 0.05
 })),
 demo: true
 };
 setData(demoData);
 }
 }
 } catch (error) {
 console.error('History fetch error:', error);
 if (alive) setData(null);
 } finally {
 if (alive) setLoading(false);
 }
 })();
 
 return () => { alive = false; };
 }, [open, symbol, expiry, timeframe]);

 if (!open) return null;

 return (
 <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
 <div className="bg-white rounded-2xl shadow-xl max-w-4xl w-full max-h-[90vh] overflow-hidden">
 {/* Header */}
 <div className="flex items-center justify-between p-4 border-b">
 <div>
 <h2 className="text-3xl font-medium">Historical Chart</h2>
 <p className="text-xl text-slate-500">{symbol} • {expiry}</p>
 </div>
 <div className="flex items-center gap-4">
 {/* Timeframe buttons */}
 <div className="flex gap-1">
 {['1D', '1W', '2W', '1M', '3M', 'All'].map(tf => (
 <button
 key={tf}
 onClick={() => setTimeframe(tf)}
 className={`px-2 py-1 text-lg rounded ${
 timeframe === tf ? 'bg-blue-500 text-[rgb(252, 251, 255)]' : 'bg-slate-100 hover:bg-slate-200'
 }`}
 >
 {tf}
 </button>
 ))}
 </div>
 
 {/* Chart type toggle */}
 <div className="flex gap-1">
 <button
 onClick={() => setChartType('line')}
 className={`px-2 py-1 text-lg rounded ${
 chartType === 'line' ? 'bg-blue-500 text-[rgb(252, 251, 255)]' : 'bg-slate-100 hover:bg-slate-200'
 }`}
 >
 Line
 </button>
 <button
 onClick={() => setChartType('candle')}
 className={`px-2 py-1 text-lg rounded ${
 chartType === 'candle' ? 'bg-blue-500 text-[rgb(252, 251, 255)]' : 'bg-slate-100 hover:bg-slate-200'
 }`}
 >
 Candle
 </button>
 </div>
 
 <button onClick={onClose} className="text-slate-400 hover:text-slate-600">
 <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
 <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
 </svg>
 </button>
 </div>
 </div>

 {/* Content */}
 <div className="p-4">
 {loading ? (
 <div className="flex items-center justify-center h-64">
 <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
 </div>
 ) : data ? (
 <div className="space-y-4">
 {data.demo && (
 <div className="bg-amber-50 border border-amber-200 rounded-lg p-3">
 <div className="flex items-center gap-2">
 <span className="text-amber-600"></span>
 <span className="text-xl font-medium text-amber-800">DEMO SERIES</span>
 <span className="text-lg text-amber-600">Historical data not available - showing simulated data</span>
 </div>
 </div>
 )}
 
 {/* Strategy Chart */}
 <div className="bg-slate-50 rounded-lg p-4 h-48">
 <div className="text-xl font-medium text-slate-700 mb-2">Strategy P/L</div>
 <svg className="w-full h-full" viewBox="0 0 400 120">
 <StrategyChart data={data.strategy} type={chartType} />
 </svg>
 </div>
 
 {/* Underlying + IV Chart */}
 <div className="bg-slate-50 rounded-lg p-4 h-48">
 <div className="text-xl font-medium text-slate-700 mb-2">Underlying Price & IV Movement</div>
 <svg className="w-full h-full" viewBox="0 0 400 120">
 <UnderlyingChart data={data.underlying} />
 <IvLine data={data.iv} />
 </svg>
 </div>
 </div>
 ) : (
 <div className="flex items-center justify-center h-64 text-slate-500">
 No historical data available
 </div>
 )}
 </div>
 </div>
 </div>
 );
}

function StrategyChart({ data, type }) {
 if (!data || !data.length) return null;
 
 const minPrice = Math.min(...data.map(d => d.p));
 const maxPrice = Math.max(...data.map(d => d.p));
 const range = maxPrice - minPrice || 1;
 
 const points = data.map((d, i) => {
 const x = (i / (data.length - 1)) * 380 + 10;
 const y = 100 - ((d.p - minPrice) / range) * 80;
 return `${x},${y}`;
 }).join(' ');
 
 return (
 <g>
 <polyline
 points={points}
 fill="none"
 stroke="#10b981"
 strokeWidth="2"
 />
 <line x1="10" y1="60" x2="390" y2="60" stroke="#64748b" strokeWidth="1" strokeDasharray="2,2" />
 </g>
 );
}

function UnderlyingChart({ data }) {
 if (!data || !data.length) return null;
 
 const minPrice = Math.min(...data.map(d => d.p));
 const maxPrice = Math.max(...data.map(d => d.p));
 const range = maxPrice - minPrice || 1;
 
 const points = data.map((d, i) => {
 const x = (i / (data.length - 1)) * 380 + 10;
 const y = 100 - ((d.p - minPrice) / range) * 80;
 return `${x},${y}`;
 }).join(' ');
 
 return (
 <polyline
 points={points}
 fill="none"
 stroke="#3b82f6"
 strokeWidth="2"
 />
 );
}

function IvLine({ data }) {
 if (!data || !data.length) return null;
 
 const minIv = Math.min(...data.map(d => d.iv));
 const maxIv = Math.max(...data.map(d => d.iv));
 const range = maxIv - minIv || 0.1;
 
 const points = data.map((d, i) => {
 const x = (i / (data.length - 1)) * 380 + 10;
 const y = 100 - ((d.iv - minIv) / range) * 20; // Use bottom 20% for IV
 return `${x},${y}`;
 }).join(' ');
 
 return (
 <polyline
 points={points}
 fill="none"
 stroke="#a855f7"
 strokeWidth="2"
 opacity="0.7"
 />
 );
}