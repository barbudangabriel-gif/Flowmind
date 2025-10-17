import React, { useState, useEffect, useMemo, useCallback } from 'react';
import { FixedSizeList as List } from 'react-window';
import { TrendingUp, TrendingDown } from 'lucide-react';

// Virtualized Table Component for Large Data Sets
const VirtualizedStockTable = ({ stocks, itemHeight = 60, containerHeight = 400, sortConfig, onSort }) => {
 
 // Memoized format function
 const formatNumber = useCallback((num) => {
 if (num === null || num === undefined) return 'N/A';
 if (num >= 1e12) return (num / 1e12).toFixed(1) + 'T';
 if (num >= 1e9) return (num / 1e9).toFixed(1) + 'B';
 if (num >= 1e6) return (num / 1e6).toFixed(1) + 'M';
 if (num >= 1e3) return (num / 1e3).toFixed(1) + 'K';
 return num.toFixed(2);
 }, []);

 // Memoized sort function
 const sortedStocks = useMemo(() => {
 if (!sortConfig.key || stocks.length === 0) return stocks;

 return [...stocks].sort((a, b) => {
 const aValue = a[sortConfig.key];
 const bValue = b[sortConfig.key];

 if (aValue === null || aValue === undefined) return 1;
 if (bValue === null || bValue === undefined) return -1;

 if (sortConfig.direction === 'asc') {
 return aValue < bValue ? -1 : aValue > bValue ? 1 : 0;
 } else {
 return aValue > bValue ? -1 : aValue < bValue ? 1 : 0;
 }
 });
 }, [stocks, sortConfig]);

 // Memoized Row Component
 const MemoizedStockRow = React.memo(({ index, style, data }) => {
 const stock = data[index];
 if (!stock) return null;

 return (
 <div 
 style={style}
 className="flex items-center px-4 border-b border-gray-100 hover:bg-blue-50 transition-colors duration-200"
 >
 {/* Symbol */}
 <div className="w-20 flex-shrink-0">
 <span className="font-mono font-medium text-blue-600 text-xl">{stock.symbol}</span>
 </div>

 {/* Company Name */}
 <div className="w-48 flex-shrink-0 px-2">
 <div className="truncate">
 <div className="font-medium text-xl text-gray-900 truncate">{stock.name}</div>
 <div className="text-lg text-gray-500">{stock.exchange}</div>
 </div>
 </div>

 {/* Sector */}
 <div className="w-32 flex-shrink-0 px-2">
 <span className="text-xl text-gray-600 truncate">{stock.sector}</span>
 </div>

 {/* Price */}
 <div className="w-24 flex-shrink-0 px-2 text-right">
 <span className="font-medium text-xl">${stock.price?.toFixed(2)}</span>
 </div>

 {/* Change % */}
 <div className="w-28 flex-shrink-0 px-2">
 <div className={`flex items-center space-x-1 text-xl font-medium ${
 stock.change_percent >= 0 ? 'text-green-600' : 'text-red-600'
 }`}>
 {stock.change_percent >= 0 ? <TrendingUp size={14} /> : <TrendingDown size={14} />}
 <span>{stock.change_percent?.toFixed(2)}%</span>
 </div>
 </div>

 {/* Volume */}
 <div className="w-24 flex-shrink-0 px-2 text-right">
 <span className="text-xl">{formatNumber(stock.volume)}</span>
 </div>

 {/* Market Cap */}
 <div className="w-28 flex-shrink-0 px-2 text-right">
 <span className="text-xl">${formatNumber(stock.market_cap)}</span>
 </div>

 {/* P/E Ratio */}
 <div className="w-20 flex-shrink-0 px-2 text-right">
 <span className="text-xl">{stock.pe_ratio ? stock.pe_ratio.toFixed(2) : 'N/A'}</span>
 </div>

 {/* Dividend Yield */}
 <div className="w-24 flex-shrink-0 px-2 text-right">
 <span className="text-xl">
 {stock.dividend_yield ? (stock.dividend_yield * 100).toFixed(2) + '%' : 'N/A'}
 </span>
 </div>
 </div>
 );
 });

 // Sortable Header Component
 const SortableHeader = ({ column, children, width, className = "" }) => (
 <div 
 className={`${width} flex-shrink-0 px-2 py-3 text-left text-lg font-medium text-gray-500 uppercase cursor-pointer hover:bg-gray-100 transition-colors ${className}`}
 onClick={() => onSort && onSort(column)}
 >
 <div className="flex items-center space-x-1">
 <span>{children}</span>
 {sortConfig.key === column && (
 <span className="text-blue-600">
 {sortConfig.direction === 'asc' ? '↑' : '↓'}
 </span>
 )}
 </div>
 </div>
 );

 if (stocks.length === 0) {
 return (
 <div className="bg-white rounded-lg shadow-md p-8 text-center">
 <p className="text-gray-500">No stocks to display</p>
 </div>
 );
 }

 return (
 <div className="bg-white rounded-lg shadow-md overflow-hidden">
 {/* Header */}
 <div className="flex items-center px-4 py-3 bg-gray-50 border-b border-gray-200">
 <SortableHeader column="symbol" width="w-20">Symbol</SortableHeader>
 <SortableHeader column="name" width="w-48" className="px-2">Company</SortableHeader>
 <SortableHeader column="sector" width="w-32" className="px-2">Sector</SortableHeader>
 <SortableHeader column="price" width="w-24" className="px-2 text-right">Price</SortableHeader>
 <SortableHeader column="change_percent" width="w-28" className="px-2">Change %</SortableHeader>
 <SortableHeader column="volume" width="w-24" className="px-2 text-right">Volume</SortableHeader>
 <SortableHeader column="market_cap" width="w-28" className="px-2 text-right">Market Cap</SortableHeader>
 <SortableHeader column="pe_ratio" width="w-20" className="px-2 text-right">P/E</SortableHeader>
 <SortableHeader column="dividend_yield" width="w-24" className="px-2 text-right">Div Yield</SortableHeader>
 </div>

 {/* Virtualized List */}
 <List
 height={containerHeight}
 itemCount={sortedStocks.length}
 itemSize={itemHeight}
 itemData={sortedStocks}
 overscanCount={5}
 className="custom-scrollbar"
 >
 {MemoizedStockRow}
 </List>
 </div>
 );
};

export default VirtualizedStockTable;