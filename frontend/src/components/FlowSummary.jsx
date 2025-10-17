import React from 'react';
import { useNavigate } from 'react-router-dom';

export default function FlowSummary({ bullish, bearish }) {
 const navigate = useNavigate();
 // Transform API data to display format
 const transformData = (items) => {
 return (items || []).map(item => ({
 symbol: item.symbol,
 count: item.trades || 0,
 premium: item.net_premium || item.bull_premium || item.bear_premium || 0,
 sweeps_pct: item.sweeps_pct || 0,
 blocks_pct: item.blocks_pct || 0
 }));
 };

 const bullishData = transformData(bullish);
 const bearishData = transformData(bearish);

 return (
 <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
 {[
 { label: 'Bullish', data: bullishData, bgColor: 'bg-green-50', textColor: 'text-green-700' },
 { label: 'Bearish', data: bearishData, bgColor: 'bg-red-50', textColor: 'text-red-700' }
 ].map(({ label, data, bgColor, textColor }) => (
 <div key={label} className="bg-white rounded-2xl shadow">
 <div className={`px-4 py-3 font-medium ${bgColor} ${textColor} rounded-t-2xl`}>
 {label} Flow ({data.length} symbols)
 </div>
 <div className="max-h-[520px] overflow-auto divide-y">
 {data.length === 0 ? (
 <div className="px-4 py-8 text-center text-gray-500">
 No {label.toLowerCase()} flow data available
 </div>
 ) : (
 data.map((r, index) => (
 <div key={r.symbol || index} className="flex items-center justify-between px-4 py-3 hover:bg-gray-50">
 <div className="flex items-center space-x-3">
 <button
 className="font-medium text-gray-900 hover:text-blue-600 hover:underline transition-colors"
 onClick={() => navigate(`/flow/live?symbol=${encodeURIComponent(r.symbol)}`)}
 >
 {r.symbol}
 </button>
 <span className="text-xl text-gray-500">({r.count} trades)</span>
 {r.sweeps_pct > 0 && (
 <span className="text-lg bg-blue-100 text-blue-800 px-2 py-0.5 rounded">
 {Math.round(r.sweeps_pct * 100)}% sweeps
 </span>
 )}
 </div>
 <span className="tabular-nums font-medium text-gray-900">
 ${(r.premium || 0).toLocaleString()}
 </span>
 </div>
 ))
 )}
 </div>
 </div>
 ))}
 </div>
 );
}