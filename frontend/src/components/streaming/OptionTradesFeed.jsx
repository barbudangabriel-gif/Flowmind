import React, { useState, useEffect } from 'react';
import useWebSocket from '../../hooks/useWebSocket';

/**
 * 📊 OptionTradesFeed - Real-time Option Trades Stream
 * 
 * ✅ VERIFIED CHANNEL: option_trades:{TICKER}
 * 
 * Displays live option trades for selected ticker with filtering and analysis.
 * Shows strike, expiry, type, side, price, quantity, premium.
 */
const OptionTradesFeed = ({ defaultTicker = 'TSLA' }) => {
  const [selectedTicker, setSelectedTicker] = useState(defaultTicker);
  const [trades, setTrades] = useState([]);
  const [isPaused, setIsPaused] = useState(false);
  const [filters, setFilters] = useState({
    minPremium: 0,
    type: 'ALL', // ALL, CALL, PUT
    side: 'ALL', // ALL, BUY, SELL
  });
  
  // Popular tickers for options trading
  const availableTickers = ['TSLA', 'AAPL', 'NVDA', 'SPY', 'QQQ', 'AMZN', 'MSFT', 'META'];
  
  // WebSocket connection for selected ticker
  const endpoint = `/api/stream/ws/option-trades/${selectedTicker}`;
  const { messages, connected, error } = useWebSocket(endpoint);

  // Process incoming messages
  useEffect(() => {
    if (messages.length === 0 || isPaused) return;
    
    const latestMessage = messages[messages.length - 1];
    
    try {
      // Parse message
      const data = typeof latestMessage === 'string' 
        ? JSON.parse(latestMessage) 
        : latestMessage;
      
      // Extract trade data
      if (data.data) {
        const trade = {
          ...data.data,
          receivedAt: new Date().toISOString(),
          id: `${data.data.ticker}-${Date.now()}-${Math.random()}`
        };
        
        // Apply filters
        const passesFilters = (
          trade.premium >= filters.minPremium &&
          (filters.type === 'ALL' || trade.type === filters.type) &&
          (filters.side === 'ALL' || trade.side === filters.side)
        );
        
        if (passesFilters) {
          // Add to trades list (keep last 50)
          setTrades(prev => [trade, ...prev.slice(0, 49)]);
        }
      }
    } catch (err) {
      console.error('Failed to parse trade message:', err);
    }
  }, [messages, isPaused, filters]);

  // Reset trades when ticker changes
  useEffect(() => {
    setTrades([]);
  }, [selectedTicker]);

  // Format premium
  const formatPremium = (value) => {
    if (!value) return 'N/A';
    if (value >= 1e6) return `$${(value / 1e6).toFixed(2)}M`;
    if (value >= 1e3) return `$${(value / 1e3).toFixed(1)}K`;
    return `$${value.toFixed(0)}`;
  };

  // Format date/time
  const formatTime = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    });
  };

  // Calculate statistics
  const stats = trades.length > 0 ? {
    totalPremium: trades.reduce((sum, t) => sum + (t.premium || 0), 0),
    callCount: trades.filter(t => t.type === 'CALL').length,
    putCount: trades.filter(t => t.type === 'PUT').length,
    buyCount: trades.filter(t => t.side === 'BUY').length,
    sellCount: trades.filter(t => t.side === 'SELL').length,
  } : null;

  return (
    <div className="bg-gray-900 rounded-lg shadow-lg border border-gray-800 p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <h2 className="text-xl font-bold text-white">
            📊 Live Option Trades
          </h2>
          <span className={`px-2 py-1 rounded text-xs font-semibold ${
            connected ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'
          }`}>
            {connected ? '● LIVE' : '○ Disconnected'}
          </span>
          <span className="px-2 py-1 rounded text-xs font-semibold bg-blue-500/20 text-blue-400">
            ✅ VERIFIED
          </span>
        </div>
        
        <div className="flex items-center gap-2">
          {/* Ticker Selector */}
          <select
            value={selectedTicker}
            onChange={(e) => setSelectedTicker(e.target.value)}
            className="bg-gray-800 text-white border border-gray-700 rounded px-3 py-1 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            {availableTickers.map(ticker => (
              <option key={ticker} value={ticker}>{ticker}</option>
            ))}
          </select>
          
          {/* Pause Button */}
          <button
            onClick={() => setIsPaused(!isPaused)}
            className={`px-3 py-1 rounded text-sm font-medium transition-colors ${
              isPaused 
                ? 'bg-yellow-500/20 text-yellow-400 hover:bg-yellow-500/30' 
                : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
            }`}
          >
            {isPaused ? '▶ Resume' : '⏸ Pause'}
          </button>
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <div className="bg-red-500/10 border border-red-500/30 rounded p-3 mb-4">
          <p className="text-red-400 text-sm">⚠️ {error}</p>
        </div>
      )}

      {/* Filters */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-3 mb-4">
        <div>
          <label className="block text-xs text-gray-400 mb-1">Min Premium</label>
          <input
            type="number"
            value={filters.minPremium}
            onChange={(e) => setFilters(prev => ({ ...prev, minPremium: Number(e.target.value) }))}
            placeholder="0"
            className="w-full bg-gray-800 text-white border border-gray-700 rounded px-3 py-1 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
        
        <div>
          <label className="block text-xs text-gray-400 mb-1">Type</label>
          <select
            value={filters.type}
            onChange={(e) => setFilters(prev => ({ ...prev, type: e.target.value }))}
            className="w-full bg-gray-800 text-white border border-gray-700 rounded px-3 py-1 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="ALL">All Types</option>
            <option value="CALL">Calls Only</option>
            <option value="PUT">Puts Only</option>
          </select>
        </div>
        
        <div>
          <label className="block text-xs text-gray-400 mb-1">Side</label>
          <select
            value={filters.side}
            onChange={(e) => setFilters(prev => ({ ...prev, side: e.target.value }))}
            className="w-full bg-gray-800 text-white border border-gray-700 rounded px-3 py-1 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="ALL">All Sides</option>
            <option value="BUY">Buys Only</option>
            <option value="SELL">Sells Only</option>
          </select>
        </div>
      </div>

      {/* Statistics */}
      {stats && (
        <div className="grid grid-cols-2 md:grid-cols-5 gap-3 mb-4">
          <div className="bg-gray-800 rounded p-3">
            <div className="text-xs text-gray-400">Total Premium</div>
            <div className="text-lg font-bold text-white">{formatPremium(stats.totalPremium)}</div>
          </div>
          <div className="bg-gray-800 rounded p-3">
            <div className="text-xs text-gray-400">Calls</div>
            <div className="text-lg font-bold text-green-400">{stats.callCount}</div>
          </div>
          <div className="bg-gray-800 rounded p-3">
            <div className="text-xs text-gray-400">Puts</div>
            <div className="text-lg font-bold text-red-400">{stats.putCount}</div>
          </div>
          <div className="bg-gray-800 rounded p-3">
            <div className="text-xs text-gray-400">Buys</div>
            <div className="text-lg font-bold text-green-400">{stats.buyCount}</div>
          </div>
          <div className="bg-gray-800 rounded p-3">
            <div className="text-xs text-gray-400">Sells</div>
            <div className="text-lg font-bold text-red-400">{stats.sellCount}</div>
          </div>
        </div>
      )}

      {/* Trades List */}
      {trades.length > 0 ? (
        <div className="bg-gray-800 rounded-lg overflow-hidden">
          <div className="overflow-x-auto max-h-96 overflow-y-auto">
            <table className="w-full text-sm">
              <thead className="bg-gray-700 sticky top-0">
                <tr>
                  <th className="px-3 py-2 text-left text-xs font-semibold text-gray-300">Time</th>
                  <th className="px-3 py-2 text-left text-xs font-semibold text-gray-300">Strike</th>
                  <th className="px-3 py-2 text-left text-xs font-semibold text-gray-300">Expiry</th>
                  <th className="px-3 py-2 text-center text-xs font-semibold text-gray-300">Type</th>
                  <th className="px-3 py-2 text-center text-xs font-semibold text-gray-300">Side</th>
                  <th className="px-3 py-2 text-right text-xs font-semibold text-gray-300">Price</th>
                  <th className="px-3 py-2 text-right text-xs font-semibold text-gray-300">Qty</th>
                  <th className="px-3 py-2 text-right text-xs font-semibold text-gray-300">Premium</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-700">
                {trades.map((trade) => (
                  <tr key={trade.id} className="hover:bg-gray-750 transition-colors">
                    <td className="px-3 py-2 text-gray-400 font-mono text-xs">
                      {formatTime(trade.receivedAt)}
                    </td>
                    <td className="px-3 py-2 text-white font-semibold">
                      ${trade.strike}
                    </td>
                    <td className="px-3 py-2 text-gray-300 text-xs">
                      {trade.expiry}
                    </td>
                    <td className="px-3 py-2 text-center">
                      <span className={`px-2 py-0.5 rounded text-xs font-semibold ${
                        trade.type === 'CALL' 
                          ? 'bg-green-500/20 text-green-400' 
                          : 'bg-red-500/20 text-red-400'
                      }`}>
                        {trade.type}
                      </span>
                    </td>
                    <td className="px-3 py-2 text-center">
                      <span className={`px-2 py-0.5 rounded text-xs font-semibold ${
                        trade.side === 'BUY' 
                          ? 'bg-green-500/20 text-green-400' 
                          : 'bg-red-500/20 text-red-400'
                      }`}>
                        {trade.side}
                      </span>
                    </td>
                    <td className="px-3 py-2 text-right text-white font-mono">
                      ${trade.price?.toFixed(2)}
                    </td>
                    <td className="px-3 py-2 text-right text-gray-300">
                      {trade.quantity}
                    </td>
                    <td className="px-3 py-2 text-right text-white font-semibold">
                      {formatPremium(trade.premium)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      ) : (
        <div className="text-center py-12">
          <div className="text-gray-500 mb-2">
            {connected ? '⏳ Waiting for option trades...' : '🔌 Connect to start streaming'}
          </div>
          <div className="text-xs text-gray-600">
            Channel: option_trades:{selectedTicker}
          </div>
          <div className="text-xs text-gray-600 mt-1">
            {trades.length} trades received
          </div>
        </div>
      )}

      {/* Footer */}
      <div className="mt-4 pt-3 border-t border-gray-800 flex items-center justify-between text-xs text-gray-500">
        <span>Showing last {trades.length} trades (max 50)</span>
        <button
          onClick={() => setTrades([])}
          className="text-gray-400 hover:text-white transition-colors"
        >
          Clear All
        </button>
      </div>
    </div>
  );
};

export default OptionTradesFeed;
