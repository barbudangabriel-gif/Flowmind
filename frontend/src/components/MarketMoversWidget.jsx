import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

const API = window.API_BASE || process.env.REACT_APP_BACKEND_URL || "";

/**
 * MarketMoversWidget - Dashboard widget showing top gainers, losers, and most active stocks
 * 
 * Features:
 * - Three columns: Gainers (green), Losers (red), Most Active (blue)
 * - Auto-refresh every 30 seconds
 * - Click ticker → Navigate to Builder
 * - Click "View All" → Navigate to full MarketMoversPage
 * - Dark theme only with responsive design
 */
const MarketMoversWidget = () => {
  const navigate = useNavigate();
  const [data, setData] = useState({
    gainers: [],
    losers: [],
    most_active: []
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastUpdate, setLastUpdate] = useState(null);

  const fetchMarketMovers = async () => {
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
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMarketMovers();
    
    // Auto-refresh every 30 seconds
    const interval = setInterval(fetchMarketMovers, 30000);
    
    return () => clearInterval(interval);
  }, []);

  const handleTickerClick = (ticker) => {
    navigate(`/builder?symbol=${ticker}`);
  };

  const handleViewAll = () => {
    navigate('/market-movers');
  };

  if (loading) {
    return (
      <div className="bg-slate-800 rounded-lg p-6 shadow-lg">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold text-white flex items-center">
            📈 Market Movers
          </h2>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {[1, 2, 3].map(i => (
            <div key={i} className="space-y-3">
              <div className="h-6 bg-slate-700 rounded animate-pulse"></div>
              <div className="h-16 bg-slate-700 rounded animate-pulse"></div>
              <div className="h-16 bg-slate-700 rounded animate-pulse"></div>
              <div className="h-16 bg-slate-700 rounded animate-pulse"></div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-slate-800 rounded-lg p-6 shadow-lg">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold text-white flex items-center">
            📈 Market Movers
          </h2>
        </div>
        <div className="text-red-400 text-center py-8">
          <p>⚠️ {error}</p>
          <button 
            onClick={fetchMarketMovers}
            className="mt-4 px-4 py-2 bg-slate-700 hover:bg-slate-600 rounded text-white"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  const renderStock = (stock, type) => {
    const changePct = stock.change_pct || 0;
    const isPositive = changePct > 0;
    
    let bgColor = 'bg-slate-700';
    let textColor = 'text-white';
    
    if (type === 'gainer') {
      bgColor = 'bg-emerald-900/30 border border-emerald-500/30';
      textColor = 'text-emerald-400';
    } else if (type === 'loser') {
      bgColor = 'bg-red-900/30 border border-red-500/30';
      textColor = 'text-red-400';
    } else if (type === 'active') {
      bgColor = 'bg-blue-900/30 border border-blue-500/30';
      textColor = 'text-blue-400';
    }

    return (
      <div 
        key={stock.ticker}
        onClick={() => handleTickerClick(stock.ticker)}
        className={`${bgColor} rounded-lg p-3 cursor-pointer hover:opacity-80 transition-opacity`}
      >
        <div className="flex justify-between items-start mb-1">
          <span className="font-bold text-white">{stock.ticker}</span>
          <span className={`text-sm font-semibold ${textColor}`}>
            {isPositive ? '+' : ''}{changePct.toFixed(2)}%
          </span>
        </div>
        <div className="text-slate-300 text-sm">
          ${stock.price?.toFixed(2) || '0.00'}
        </div>
        {stock.volume && (
          <div className="text-slate-400 text-xs mt-1">
            Vol: {(stock.volume / 1000000).toFixed(1)}M
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="bg-slate-800 rounded-lg p-6 shadow-lg">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-semibold text-white flex items-center">
          📈 Market Movers
          {lastUpdate && (
            <span className="ml-3 text-xs text-slate-400">
              Updated {lastUpdate.toLocaleTimeString()}
            </span>
          )}
        </h2>
        <button
          onClick={handleViewAll}
          className="text-blue-400 hover:text-blue-300 text-sm font-medium"
        >
          View All →
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Gainers Column */}
        <div className="space-y-3">
          <h3 className="text-emerald-400 font-semibold text-sm uppercase tracking-wide">
            🟢 Top Gainers
          </h3>
          {data.gainers.slice(0, 3).map(stock => renderStock(stock, 'gainer'))}
          {data.gainers.length === 0 && (
            <div className="text-slate-500 text-sm text-center py-4">
              No gainers
            </div>
          )}
        </div>

        {/* Losers Column */}
        <div className="space-y-3">
          <h3 className="text-red-400 font-semibold text-sm uppercase tracking-wide">
            🔴 Top Losers
          </h3>
          {data.losers.slice(0, 3).map(stock => renderStock(stock, 'loser'))}
          {data.losers.length === 0 && (
            <div className="text-slate-500 text-sm text-center py-4">
              No losers
            </div>
          )}
        </div>

        {/* Most Active Column */}
        <div className="space-y-3">
          <h3 className="text-blue-400 font-semibold text-sm uppercase tracking-wide">
            🔵 Most Active
          </h3>
          {data.most_active.slice(0, 3).map(stock => renderStock(stock, 'active'))}
          {data.most_active.length === 0 && (
            <div className="text-slate-500 text-sm text-center py-4">
              No data
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default MarketMoversWidget;
