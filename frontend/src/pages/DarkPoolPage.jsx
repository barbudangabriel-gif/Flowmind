import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Plot from 'react-plotly.js';

const API = window.API_BASE || process.env.REACT_APP_BACKEND_URL || "";

/**
 * DarkPoolPage - Dark pool activity tracker
 * 
 * Features:
 * - Volume chart (Plotly): Dark pool vs lit exchange
 * - Recent prints table with large print highlights
 * - Filter by ticker, minimum volume
 * - Real-time updates (10s polling)
 * - Click ticker → Navigate to Builder
 * - Dark theme with purple/blue accents
 */
const DarkPoolPage = () => {
  const navigate = useNavigate();
  const [prints, setPrints] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [tickerFilter, setTickerFilter] = useState('');
  const [minVolume, setMinVolume] = useState('');

  const fetchDarkPool = async () => {
    try {
      const params = new URLSearchParams();
      if (tickerFilter) params.append('ticker', tickerFilter);
      if (minVolume) params.append('min_volume', minVolume);
      params.append('limit', 100);
      
      const response = await fetch(`${API}/api/flow/dark-pool?${params}`);
      const result = await response.json();
      
      if (result.status === 'success') {
        setPrints(result.data || []);
        setError(null);
      } else {
        setError(result.error || 'Failed to fetch dark pool data');
      }
    } catch (err) {
      console.error('Error fetching dark pool data:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDarkPool();
    
    // Auto-refresh every 10 seconds
    const interval = setInterval(fetchDarkPool, 10000);
    
    return () => clearInterval(interval);
  }, [tickerFilter, minVolume]);

  const handleTickerClick = (ticker) => {
    navigate(`/builder?symbol=${ticker}`);
  };

  // Prepare chart data
  const getChartData = () => {
    if (prints.length === 0) return null;

    const timestamps = prints.map(p => new Date(p.timestamp).toLocaleTimeString());
    const volumes = prints.map(p => p.volume || 0);
    
    // Mock lit exchange volume (in reality, would come from API)
    const litVolumes = volumes.map(v => v * 1.5);

    return {
      timestamps,
      darkPoolVolumes: volumes,
      litVolumes
    };
  };

  const chartData = getChartData();

  if (loading && prints.length === 0) {
    return (
      <div className="min-h-screen bg-slate-900 p-6">
        <div className="max-w-7xl mx-auto">
          <div className="bg-slate-800 rounded-lg p-6 shadow-lg">
            <div className="h-8 bg-slate-700 rounded w-64 mb-6 animate-pulse"></div>
            <div className="h-96 bg-slate-700 rounded animate-pulse"></div>
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
            🌊 Dark Pool Activity
          </h1>
          <p className="text-slate-400 mt-1">
            Off-exchange trades and large block prints
          </p>
        </div>

        {/* Filters */}
        <div className="bg-slate-800 rounded-lg p-6 shadow-lg">
          <h2 className="text-lg font-semibold text-white mb-4">🔍 Filters</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-slate-400 text-sm mb-2">Symbol</label>
              <input
                type="text"
                value={tickerFilter}
                onChange={(e) => setTickerFilter(e.target.value.toUpperCase())}
                placeholder="e.g., SPY"
                className="w-full bg-slate-700 border border-slate-600 rounded px-3 py-2 text-white placeholder-slate-500 focus:outline-none focus:border-purple-500"
              />
            </div>
            <div>
              <label className="block text-slate-400 text-sm mb-2">Min Volume</label>
              <input
                type="number"
                value={minVolume}
                onChange={(e) => setMinVolume(e.target.value)}
                placeholder="e.g., 10000"
                className="w-full bg-slate-700 border border-slate-600 rounded px-3 py-2 text-white placeholder-slate-500 focus:outline-none focus:border-purple-500"
              />
            </div>
            <div className="flex items-end gap-2">
              <button
                onClick={() => {
                  setTickerFilter('');
                  setMinVolume('');
                }}
                className="flex-1 px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded font-medium transition-colors"
              >
                Clear
              </button>
              <button
                onClick={fetchDarkPool}
                className="flex-1 px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded font-medium transition-colors"
              >
                🔄 Refresh
              </button>
            </div>
          </div>
        </div>

        {/* Error State */}
        {error && (
          <div className="bg-red-900/30 border border-red-500/30 rounded-lg p-4">
            <div className="flex items-center gap-2 text-red-400">
              <span className="text-xl">⚠️</span>
              <span>{error}</span>
            </div>
          </div>
        )}

        {/* Volume Chart */}
        {chartData && chartData.timestamps.length > 0 && (
          <div className="bg-slate-800 rounded-lg p-6 shadow-lg">
            <h2 className="text-lg font-semibold text-white mb-4">
              📊 Volume Chart
            </h2>
            <Plot
              data={[
                {
                  x: chartData.timestamps,
                  y: chartData.darkPoolVolumes,
                  type: 'bar',
                  name: 'Dark Pool',
                  marker: { color: '#a78bfa' }
                },
                {
                  x: chartData.timestamps,
                  y: chartData.litVolumes,
                  type: 'bar',
                  name: 'Lit Exchange',
                  marker: { color: '#60a5fa' }
                }
              ]}
              layout={{
                barmode: 'stack',
                paper_bgcolor: '#1e293b',
                plot_bgcolor: '#1e293b',
                font: { color: '#cbd5e1' },
                xaxis: { 
                  title: 'Time',
                  color: '#cbd5e1',
                  gridcolor: '#334155'
                },
                yaxis: { 
                  title: 'Volume',
                  color: '#cbd5e1',
                  gridcolor: '#334155'
                },
                legend: {
                  x: 0,
                  y: 1.1,
                  orientation: 'h'
                },
                margin: { t: 20, r: 20, b: 60, l: 80 }
              }}
              config={{ displayModeBar: false }}
              style={{ width: '100%', height: '400px' }}
            />
          </div>
        )}

        {/* Recent Prints Table */}
        <div className="bg-slate-800 rounded-lg p-6 shadow-lg">
          <h2 className="text-lg font-semibold text-white mb-4">
            📋 Recent Dark Pool Prints ({prints.length})
          </h2>
          
          {prints.length === 0 ? (
            <div className="text-slate-500 text-center py-8">
              No dark pool prints found. Try adjusting filters.
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-slate-700">
                    <th className="text-left py-3 px-4 text-slate-400 font-semibold text-sm">Time</th>
                    <th className="text-left py-3 px-4 text-slate-400 font-semibold text-sm">Ticker</th>
                    <th className="text-right py-3 px-4 text-slate-400 font-semibold text-sm">Volume</th>
                    <th className="text-right py-3 px-4 text-slate-400 font-semibold text-sm">Price</th>
                    <th className="text-right py-3 px-4 text-slate-400 font-semibold text-sm">Notional</th>
                  </tr>
                </thead>
                <tbody>
                  {prints.map((print, index) => {
                    const isLargePrint = print.notional > 10000000; // >$10M
                    
                    return (
                      <tr 
                        key={index}
                        className={`border-b border-slate-700/50 hover:bg-slate-700/30 transition-colors ${isLargePrint ? 'bg-yellow-900/10' : ''}`}
                      >
                        <td className="py-3 px-4 text-slate-300 text-sm">
                          {new Date(print.timestamp).toLocaleTimeString()}
                        </td>
                        <td 
                          className="py-3 px-4 text-purple-400 font-bold cursor-pointer hover:text-purple-300"
                          onClick={() => handleTickerClick(print.ticker)}
                        >
                          {print.ticker}
                          {isLargePrint && (
                            <span className="ml-2 text-yellow-400">🔥</span>
                          )}
                        </td>
                        <td className="py-3 px-4 text-right text-white font-medium">
                          {(print.volume || 0).toLocaleString()}
                        </td>
                        <td className="py-3 px-4 text-right text-slate-300">
                          ${(print.price || 0).toFixed(2)}
                        </td>
                        <td className="py-3 px-4 text-right text-white font-bold">
                          ${((print.notional || 0) / 1000000).toFixed(1)}M
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Legend */}
        <div className="bg-slate-800 rounded-lg p-4 shadow-lg">
          <div className="flex items-center gap-6 text-sm">
            <div className="flex items-center gap-2">
              <span className="text-yellow-400 text-xl">🔥</span>
              <span className="text-slate-400">Large Print (&gt;$10M)</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 bg-purple-500 rounded"></div>
              <span className="text-slate-400">Dark Pool Volume</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 bg-blue-500 rounded"></div>
              <span className="text-slate-400">Lit Exchange Volume</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DarkPoolPage;
