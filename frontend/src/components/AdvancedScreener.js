import React, { useState, useEffect, useCallback, useMemo } from 'react';
import axios from 'axios';
import {
  ChevronDown,
  ChevronUp,
  Filter,
  Download,
  RefreshCw,
  Loader,
  TrendingUp,
  TrendingDown
} from 'lucide-react';
import VirtualizedStockTable from './VirtualizedTable';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Memoized Advanced Screener Component
const AdvancedScreener = React.memo(() => {
  const [stocks, setStocks] = useState([]);
  const [filteredStocks, setFilteredStocks] = useState([]);
  const [loading, setLoading] = useState(false);
  const [sectors, setSectors] = useState([]);
  const [sortConfig, setSortConfig] = useState({ key: 'market_cap', direction: 'desc' });
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage] = useState(50); // Increased for virtual scrolling
  const [showFilters, setShowFilters] = useState(false);
  const [useVirtualScrolling, setUseVirtualScrolling] = useState(true);
  
  // Filter states
  const [filters, setFilters] = useState({
    minPrice: '',
    maxPrice: '',
    minMarketCap: '',
    maxMarketCap: '',
    minPE: '',
    maxPE: '',
    minVolume: '',
    sector: 'All',
    minChange: '',
    maxChange: '',
    exchange: 'all'
  });

  useEffect(() => {
    const initializeData = async () => {
      console.log('🔄 Initializing AdvancedScreener data...');
      await fetchSectors();
      await loadScreenerData('all');
    };
    initializeData();
  }, []); // Empty dependency array to run only once

  // Debug effect to monitor state changes
  useEffect(() => {
    console.log('📊 AdvancedScreener State Update:', {
      stocksLength: stocks.length,
      filteredStocksLength: filteredStocks.length,
      loading: loading
    });
  }, [stocks, filteredStocks, loading]);

  // Memoized fetch functions
  const fetchSectors = useCallback(async () => {
    try {
      const response = await axios.get(`${API}/screener/sectors`);
      setSectors(response.data.sectors);
    } catch (error) {
      console.error('Error fetching sectors:', error);
    }
  }, []);

  const loadScreenerData = useCallback(async (exchange = 'all') => {
    console.log('🔄 Loading screener data for exchange:', exchange);
    setLoading(true);
    try {
      const response = await axios.get(`${API}/screener/data?limit=500&exchange=${exchange}`); // Increased limit for virtual scrolling
      console.log('📡 API response received:', {
        status: response.status,
        dataKeys: Object.keys(response.data || {}),
        stocksCount: response.data?.stocks?.length || 0
      });
      
      // Handle the response structure properly - be defensive
      let stocksData = [];
      if (response.data && response.data.stocks && Array.isArray(response.data.stocks)) {
        stocksData = response.data.stocks;
      } else if (response.data && Array.isArray(response.data)) {
        stocksData = response.data;
      } else {
        console.warn('⚠️ Unexpected API response structure:', response.data);
      }
      
      console.log('📊 Extracted stocks data:', stocksData.length, 'items');
      
      // Force update state
      if (stocksData.length > 0) {
        setStocks(stocksData);
        setFilteredStocks(stocksData);
        console.log('✅ State updated successfully with', stocksData.length, 'stocks');
      } else {
        console.warn('⚠️ No stocks data found in response');
        setStocks([]);
        setFilteredStocks([]);
      }
      
    } catch (error) {
      console.error('❌ Error loading screener data:', error);
      setStocks([]);
      setFilteredStocks([]);
    } finally {
      setLoading(false);
    }
  }, []);

  const applyAdvancedFilter = useCallback(async () => {
    setLoading(true);
    try {
      // Convert empty strings to null for API
      const criteria = {};
      if (filters.minPrice) criteria.min_price = parseFloat(filters.minPrice);
      if (filters.maxPrice) criteria.max_price = parseFloat(filters.maxPrice);
      if (filters.minMarketCap) criteria.min_market_cap = parseFloat(filters.minMarketCap);
      if (filters.maxMarketCap) criteria.max_market_cap = parseFloat(filters.maxMarketCap);
      if (filters.minPE) criteria.min_pe = parseFloat(filters.minPE);
      if (filters.maxPE) criteria.max_pe = parseFloat(filters.maxPE);
      if (filters.minVolume) criteria.min_volume = parseInt(filters.minVolume);
      if (filters.sector !== 'All') criteria.sector = filters.sector;
      if (filters.minChange) criteria.min_change = parseFloat(filters.minChange);
      if (filters.maxChange) criteria.max_change = parseFloat(filters.maxChange);

      const response = await axios.post(`${API}/screener/filter`, criteria);
      setFilteredStocks(response.data.stocks || []);
      setCurrentPage(1);
    } catch (error) {
      console.error('Error filtering stocks:', error);
      setFilteredStocks([]);
    } finally {
      setLoading(false);
    }
  }, [filters]);

  const clearFilters = useCallback(() => {
    setFilters({
      minPrice: '',
      maxPrice: '',
      minMarketCap: '',
      maxMarketCap: '',
      minPE: '',
      maxPE: '',
      minVolume: '',
      sector: 'All',
      minChange: '',
      maxChange: '',
      exchange: 'all'
    });
    setFilteredStocks(stocks); // Reset to original stocks data
    setCurrentPage(1);
  }, [stocks]);

  const handleSort = useCallback((key) => {
    let direction = 'asc';
    if (sortConfig.key === key && sortConfig.direction === 'asc') {
      direction = 'desc';
    }
    setSortConfig({ key, direction });
  }, [sortConfig]);

  // Memoized sorted and paginated data
  const getSortedStocks = useCallback(() => {
    const stocksToSort = Array.isArray(filteredStocks) ? filteredStocks : [];
    if (!sortConfig.key || stocksToSort.length === 0) return stocksToSort;

    return [...stocksToSort].sort((a, b) => {
      const aValue = a?.[sortConfig.key];
      const bValue = b?.[sortConfig.key];

      if (aValue === null || aValue === undefined) return 1;
      if (bValue === null || bValue === undefined) return -1;

      if (sortConfig.direction === 'asc') {
        return aValue < bValue ? -1 : aValue > bValue ? 1 : 0;
      } else {
        return aValue > bValue ? -1 : aValue < bValue ? 1 : 0;
      }
    });
  }, [filteredStocks, sortConfig]);

  const sortedStocks = useMemo(() => getSortedStocks(), [getSortedStocks]);
  
  const paginatedStocks = useMemo(() => {
    const startIndex = (currentPage - 1) * itemsPerPage;
    return sortedStocks.slice(startIndex, startIndex + itemsPerPage);
  }, [sortedStocks, currentPage, itemsPerPage]);

  const totalPages = useMemo(() => Math.ceil(sortedStocks.length / itemsPerPage), [sortedStocks.length, itemsPerPage]);

  const exportToCSV = useCallback(() => {
    const stocksToExport = getSortedStocks();
    if (stocksToExport.length === 0) {
      console.warn('No stocks to export');
      return;
    }
    
    const headers = ['Symbol', 'Name', 'Sector', 'Price', 'Change %', 'Volume', 'Market Cap', 'P/E'];
    const csvContent = [
      headers.join(','),
      ...stocksToExport.map(stock => [
        stock.symbol,
        `"${stock.name}"`,
        `"${stock.sector}"`,
        stock.price?.toFixed(2) || '0.00',
        stock.change_percent?.toFixed(2) || '0.00',
        stock.volume || '0',
        stock.market_cap || '',
        stock.pe_ratio?.toFixed(2) || ''
      ].join(','))
    ].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'stock_screener_results.csv';
    a.click();
    window.URL.revokeObjectURL(url);
  }, [getSortedStocks]);

  const SortableHeader = ({ column, children }) => (
    <th 
      className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase cursor-pointer hover:bg-gray-100 transition-colors"
      onClick={() => handleSort(column)}
    >
      <div className="flex items-center space-x-1">
        <span>{children}</span>
        {sortConfig.key === column && (
          sortConfig.direction === 'asc' ? <ChevronUp size={14} /> : <ChevronDown size={14} />
        )}
      </div>
    </th>
  );

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-gray-800">Advanced Stock Screener</h2>
          <p className="text-gray-600">Screen stocks from S&P 500, NASDAQ, and more</p>
        </div>
        <div className="flex space-x-3">
          <button
            onClick={() => setShowFilters(!showFilters)}
            className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 flex items-center space-x-2"
          >
            <Filter size={20} />
            <span>Filters</span>
          </button>
          <button
            onClick={exportToCSV}
            className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 flex items-center space-x-2"
          >
            <Download size={20} />
            <span>Export</span>
          </button>
          <button
            onClick={() => loadScreenerData(filters.exchange)}
            className="bg-gray-600 text-white px-4 py-2 rounded-lg hover:bg-gray-700 flex items-center space-x-2"
          >
            <RefreshCw size={20} />
            <span>Refresh</span>
          </button>
        </div>
      </div>

      {/* Filter Panel */}
      {showFilters && (
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h3 className="text-lg font-semibold mb-4">Filter Criteria</h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {/* Exchange Filter */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Exchange</label>
              <select
                value={filters.exchange}
                onChange={(e) => {
                  const newExchange = e.target.value;
                  setFilters({...filters, exchange: newExchange});
                  loadScreenerData(newExchange); // Reload data when exchange changes
                }}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="all">All Markets</option>
                <option value="sp500">S&P 500</option>
                <option value="nasdaq">NASDAQ</option>
              </select>
            </div>

            {/* Price Range */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Min Price ($)</label>
              <input
                type="number"
                step="0.01"
                value={filters.minPrice}
                onChange={(e) => setFilters({...filters, minPrice: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="0.00"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Max Price ($)</label>
              <input
                type="number"
                step="0.01"
                value={filters.maxPrice}
                onChange={(e) => setFilters({...filters, maxPrice: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="1000.00"
              />
            </div>

            {/* Market Cap Range (in millions) */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Min Market Cap (M)</label>
              <input
                type="number"
                value={filters.minMarketCap}
                onChange={(e) => setFilters({...filters, minMarketCap: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="1000"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Max Market Cap (M)</label>
              <input
                type="number"
                value={filters.maxMarketCap}
                onChange={(e) => setFilters({...filters, maxMarketCap: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="1000000"
              />
            </div>

            {/* P/E Range */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Min P/E</label>
              <input
                type="number"
                step="0.1"
                value={filters.minPE}
                onChange={(e) => setFilters({...filters, minPE: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="5.0"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Max P/E</label>
              <input
                type="number"
                step="0.1"
                value={filters.maxPE}
                onChange={(e) => setFilters({...filters, maxPE: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="50.0"
              />
            </div>

            {/* Sector Filter */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Sector</label>
              <select
                value={filters.sector}
                onChange={(e) => setFilters({...filters, sector: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                {sectors.map(sector => (
                  <option key={sector} value={sector}>{sector}</option>
                ))}
              </select>
            </div>

            {/* Volume Filter */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Min Volume</label>
              <input
                type="number"
                value={filters.minVolume}
                onChange={(e) => setFilters({...filters, minVolume: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="1000000"
              />
            </div>

            {/* Change % Range */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Min Change (%)</label>
              <input
                type="number"
                step="0.1"
                value={filters.minChange}
                onChange={(e) => setFilters({...filters, minChange: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="-10.0"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Max Change (%)</label>
              <input
                type="number"
                step="0.1"
                value={filters.maxChange}
                onChange={(e) => setFilters({...filters, maxChange: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="10.0"
              />
            </div>
          </div>

          <div className="flex justify-end space-x-3 mt-6">
            <button
              onClick={clearFilters}
              className="px-4 py-2 text-gray-600 border border-gray-300 rounded-md hover:bg-gray-50"
            >
              Clear All
            </button>
            <button
              onClick={applyAdvancedFilter}
              className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
            >
              Apply Filters
            </button>
          </div>
        </div>
      )}

      {/* Results Summary with Virtual Scrolling Toggle */}
      <div className="bg-white p-4 rounded-lg shadow-md">
        <div className="flex justify-between items-center">
          <div className="flex items-center space-x-4">
            <span className="text-gray-600">
              Showing {paginatedStocks.length} of {sortedStocks.length} stocks
            </span>
            {loading && <Loader className="animate-spin text-blue-500" size={20} />}
          </div>
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <label className="text-sm text-gray-600">Virtual Scrolling:</label>
              <button
                onClick={() => setUseVirtualScrolling(!useVirtualScrolling)}
                className={`px-3 py-1 rounded-full text-xs font-medium transition-colors ${
                  useVirtualScrolling 
                    ? 'bg-green-100 text-green-700' 
                    : 'bg-gray-100 text-gray-700'
                }`}
              >
                {useVirtualScrolling ? 'ON' : 'OFF'}
              </button>
            </div>
            <div className="flex items-center space-x-2">
              <span className="text-sm text-gray-600">Page {currentPage} of {totalPages}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Results Table or Virtual Scrolling */}
      {useVirtualScrolling && sortedStocks.length > 50 ? (
        <div className="bg-white rounded-lg shadow-md p-4">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-lg font-semibold text-gray-800">
              📊 Virtual Scrolling Mode ({sortedStocks.length} stocks)
            </h3>
            <span className="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded-full">
              Performance Optimized
            </span>
          </div>
          <VirtualizedStockTable 
            stocks={sortedStocks}
            sortConfig={sortConfig}
            onSort={handleSort}
            containerHeight={600}
            itemHeight={60}
          />
        </div>
      ) : (
        /* Traditional Table */
        <div className="bg-white rounded-lg shadow-md overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50">
                <tr>
                  <SortableHeader column="symbol">Symbol</SortableHeader>
                  <SortableHeader column="name">Company</SortableHeader>
                  <SortableHeader column="sector">Sector</SortableHeader>
                  <SortableHeader column="price">Price</SortableHeader>
                  <SortableHeader column="change_percent">Change %</SortableHeader>
                  <SortableHeader column="volume">Volume</SortableHeader>
                  <SortableHeader column="market_cap">Market Cap</SortableHeader>
                  <SortableHeader column="pe_ratio">P/E</SortableHeader>
                  <SortableHeader column="dividend_yield">Div Yield</SortableHeader>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {paginatedStocks.map((stock, index) => (
                  <tr key={stock.symbol} className="hover:bg-gray-50 transition-colors">
                    <td className="px-4 py-3 font-mono font-bold text-blue-600">{stock.symbol}</td>
                    <td className="px-4 py-3">
                      <div>
                        <div className="font-medium truncate max-w-48">{stock.name}</div>
                        <div className="text-xs text-gray-500">{stock.exchange}</div>
                      </div>
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-600">{stock.sector}</td>
                    <td className="px-4 py-3 font-medium">${stock.price?.toFixed(2)}</td>
                    <td className={`px-4 py-3 font-medium flex items-center space-x-1 ${
                      stock.change_percent >= 0 ? 'text-green-600' : 'text-red-600'
                    }`}>
                      {stock.change_percent >= 0 ? <TrendingUp size={14} /> : <TrendingDown size={14} />}
                      <span>{stock.change_percent?.toFixed(2)}%</span>
                    </td>
                    <td className="px-4 py-3 text-sm">{formatNumber(stock.volume)}</td>
                    <td className="px-4 py-3 text-sm">${formatNumber(stock.market_cap)}</td>
                    <td className="px-4 py-3 text-sm">{stock.pe_ratio ? stock.pe_ratio.toFixed(2) : 'N/A'}</td>
                    <td className="px-4 py-3 text-sm">{stock.dividend_yield ? (stock.dividend_yield * 100).toFixed(2) + '%' : 'N/A'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Pagination for Traditional Table */}
          {totalPages > 1 && !useVirtualScrolling && (
            <div className="px-6 py-3 bg-gray-50 border-t">
              <div className="flex justify-between items-center">
                <button
                  onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
                  disabled={currentPage === 1}
                  className="px-3 py-1 text-sm border rounded-md disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-100"
                >
                  Previous
                </button>
                
                <div className="flex space-x-1">
                  {Array.from({length: Math.min(5, totalPages)}, (_, i) => {
                    let page = i + 1;
                    if (totalPages > 5) {
                      if (currentPage > 3) {
                        page = currentPage - 2 + i;
                        if (page > totalPages) page = totalPages - 4 + i;
                      }
                    }
                    
                    return (
                      <button
                        key={page}
                        onClick={() => setCurrentPage(page)}
                        className={`px-3 py-1 text-sm border rounded-md ${
                          currentPage === page 
                            ? 'bg-blue-600 text-white border-blue-600' 
                            : 'hover:bg-gray-100'
                        }`}
                      >
                        {page}
                      </button>
                    );
                  })}
                </div>
                
                <button
                  onClick={() => setCurrentPage(Math.min(totalPages, currentPage + 1))}
                  disabled={currentPage === totalPages}
                  className="px-3 py-1 text-sm border rounded-md disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-100"
                >
                  Next
                </button>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
});

export default AdvancedScreener;