import React, { useState } from 'react';

export default function FlowFiltersPanel({ value, onChange }) {
 const [isExpanded, setIsExpanded] = useState(false);

 const updateFilter = (key, val) => {
 onChange({ ...value, [key]: val });
 };

 const handleTickersChange = (text) => {
 const tickers = text.split(',').map(t => t.trim().toUpperCase()).filter(t => t);
 updateFilter('tickers', tickers.length > 0 ? tickers : undefined);
 };

 return (
 <div className="bg-white rounded-2xl shadow">
 <div 
 className="px-4 py-3 border-b border-gray-200 cursor-pointer flex items-center justify-between"
 onClick={() => setIsExpanded(!isExpanded)}
 >
 <h3 className="text-3xl font-medium text-gray-900">Filters</h3>
 <button className="text-gray-500 hover:text-gray-700">
 {isExpanded ? '▼' : '▶'}
 </button>
 </div>
 
 {isExpanded && (
 <div className="p-4 space-y-4">
 {/* Tickers */}
 <div>
 <label className="block text-xl font-medium text-gray-700 mb-1">
 Tickers (comma-separated)
 </label>
 <input
 type="text"
 className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
 placeholder="TSLA, AAPL, NVDA"
 value={(value.tickers || []).join(', ')}
 onChange={(e) => handleTickersChange(e.target.value)}
 />
 </div>

 {/* Clear Filters */}
 <div className="pt-2">
 <button
 onClick={() => onChange({})}
 className="px-4 py-2 text-xl font-medium text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-gray-500"
 >
 Clear All Filters
 </button>
 </div>
 </div>
 )}
 </div>
 );
}