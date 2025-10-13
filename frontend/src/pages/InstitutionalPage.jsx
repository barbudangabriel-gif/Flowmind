import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import Plot from 'react-plotly.js';

const API = window.API_BASE || process.env.REACT_APP_BACKEND_URL || "";

/**
 * InstitutionalPage - Institutional holdings tracker (13F filings)
 * 
 * Features:
 * - Ticker search/selector
 * - Quarter selector (dropdown)
 * - Summary cards: total ownership %, change QoQ, top holder
 * - Ownership pie chart (Plotly)
 * - Top holders table with change % color-coded
 * - Dark theme with colorful pie chart
 */
const InstitutionalPage = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const [ticker, setTicker] = useState(searchParams.get('ticker') || 'TSLA');
  const [quarter, setQuarter] = useState('');
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchInstitutional = async () => {
    if (!ticker) return;
    
    setLoading(true);
    
    try {
      const params = new URLSearchParams();
      if (quarter) params.append('quarter', quarter);
      
      const response = await fetch(`${API}/api/flow/institutional/${ticker}?${params}`);
      const result = await response.json();
      
      if (result.status === 'success') {
        setData(result.data);
        setError(null);
      } else {
        setError(result.error || 'Failed to fetch institutional data');
      }
    } catch (err) {
      console.error('Error fetching institutional data:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchInstitutional();
  }, [ticker, quarter]);

  const handleTickerSubmit = (e) => {
    e.preventDefault();
    setSearchParams({ ticker });
  };

  // Prepare pie chart data
  const getPieChartData = () => {
    if (!data || !data.holdings || data.holdings.length === 0) return null;

    const topHolders = data.holdings.slice(0, 5);
    const labels = topHolders.map(h => h.institution);
    const values = topHolders.map(h => (h.value || 0) / 1000000000); // Convert to billions
    
    return { labels, values };
  };

  const pieData = getPieChartData();

  if (loading) {
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
            🏢 Institutional Holdings
          </h1>
          <p className="text-slate-400 mt-1">
            13F filings - Track institutional ownership and changes
          </p>
        </div>

        {/* Ticker Selector */}
        <div className="bg-slate-800 rounded-lg p-6 shadow-lg">
          <form onSubmit={handleTickerSubmit} className="flex gap-4">
            <div className="flex-1">
              <label className="block text-slate-400 text-sm mb-2">Ticker Symbol</label>
              <input
                type="text"
                value={ticker}
                onChange={(e) => setTicker(e.target.value.toUpperCase())}
                placeholder="e.g., TSLA"
                className="w-full bg-slate-700 border border-slate-600 rounded px-4 py-2 text-white placeholder-slate-500 focus:outline-none focus:border-blue-500"
              />
            </div>
            <div className="flex-1">
              <label className="block text-slate-400 text-sm mb-2">Quarter (Optional)</label>
              <input
                type="text"
                value={quarter}
                onChange={(e) => setQuarter(e.target.value)}
                placeholder="e.g., 2025Q3"
                className="w-full bg-slate-700 border border-slate-600 rounded px-4 py-2 text-white placeholder-slate-500 focus:outline-none focus:border-blue-500"
              />
            </div>
            <div className="flex items-end">
              <button
                type="submit"
                className="px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded font-medium transition-colors"
              >
                🔍 Search
              </button>
            </div>
          </form>
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

        {/* Summary Cards */}
        {data && (
          <>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-slate-800 rounded-lg p-4 shadow-lg">
                <div className="text-slate-400 text-sm mb-1">Total Institutional Ownership</div>
                <div className="text-3xl font-bold text-blue-400">
                  {data.total_ownership_pct ? `${data.total_ownership_pct.toFixed(1)}%` : 'N/A'}
                </div>
              </div>
              <div className="bg-slate-800 rounded-lg p-4 shadow-lg">
                <div className="text-slate-400 text-sm mb-1">Change QoQ</div>
                <div className={`text-3xl font-bold ${data.change_qoq_pct > 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                  {data.change_qoq_pct ? `${data.change_qoq_pct > 0 ? '+' : ''}${data.change_qoq_pct.toFixed(1)}%` : 'N/A'}
                </div>
              </div>
              <div className="bg-slate-800 rounded-lg p-4 shadow-lg">
                <div className="text-slate-400 text-sm mb-1">Top Holder</div>
                <div className="text-xl font-bold text-white truncate">
                  {data.top_holder || 'N/A'}
                </div>
              </div>
            </div>

            {/* Pie Chart */}
            {pieData && pieData.labels.length > 0 && (
              <div className="bg-slate-800 rounded-lg p-6 shadow-lg">
                <h2 className="text-lg font-semibold text-white mb-4">
                  📊 Ownership Breakdown
                </h2>
                <Plot
                  data={[
                    {
                      labels: pieData.labels,
                      values: pieData.values,
                      type: 'pie',
                      marker: {
                        colors: ['#60a5fa', '#a78bfa', '#f472b6', '#fb923c', '#34d399']
                      },
                      textinfo: 'label+percent',
                      textposition: 'auto',
                      hovertemplate: '<b>%{label}</b><br>$%{value:.1f}B<extra></extra>'
                    }
                  ]}
                  layout={{
                    paper_bgcolor: '#1e293b',
                    plot_bgcolor: '#1e293b',
                    font: { color: '#cbd5e1', size: 12 },
                    showlegend: true,
                    legend: {
                      x: 0,
                      y: -0.1,
                      orientation: 'h'
                    },
                    margin: { t: 20, r: 20, b: 80, l: 20 }
                  }}
                  config={{ displayModeBar: false }}
                  style={{ width: '100%', height: '400px' }}
                />
              </div>
            )}

            {/* Top Holders Table */}
            <div className="bg-slate-800 rounded-lg p-6 shadow-lg">
              <h2 className="text-lg font-semibold text-white mb-4">
                📋 Top Institutional Holders ({data.holdings?.length || 0})
              </h2>
              
              {!data.holdings || data.holdings.length === 0 ? (
                <div className="text-slate-500 text-center py-8">
                  No institutional holdings data available
                </div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b border-slate-700">
                        <th className="text-left py-3 px-4 text-slate-400 font-semibold text-sm">Institution</th>
                        <th className="text-right py-3 px-4 text-slate-400 font-semibold text-sm">Shares</th>
                        <th className="text-right py-3 px-4 text-slate-400 font-semibold text-sm">Value</th>
                        <th className="text-right py-3 px-4 text-slate-400 font-semibold text-sm">Change %</th>
                        <th className="text-right py-3 px-4 text-slate-400 font-semibold text-sm">Filed</th>
                      </tr>
                    </thead>
                    <tbody>
                      {data.holdings.map((holding, index) => {
                        const changePct = holding.change_pct || 0;
                        const isPositive = changePct > 0;
                        
                        return (
                          <tr 
                            key={index}
                            className="border-b border-slate-700/50 hover:bg-slate-700/30 transition-colors"
                          >
                            <td className="py-3 px-4 text-white font-medium">
                              {holding.institution}
                            </td>
                            <td className="py-3 px-4 text-right text-slate-300">
                              {((holding.shares || 0) / 1000000).toFixed(1)}M
                            </td>
                            <td className="py-3 px-4 text-right text-slate-300">
                              ${((holding.value || 0) / 1000000000).toFixed(1)}B
                            </td>
                            <td className={`py-3 px-4 text-right font-bold ${isPositive ? 'text-emerald-400' : changePct < 0 ? 'text-red-400' : 'text-slate-400'}`}>
                              {changePct !== 0 && (isPositive ? '+' : '')}{changePct.toFixed(1)}%
                            </td>
                            <td className="py-3 px-4 text-right text-slate-400 text-sm">
                              {holding.filed_date ? new Date(holding.filed_date).toLocaleDateString() : 'N/A'}
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              )}
            </div>

            {/* Info Box */}
            <div className="bg-blue-900/20 border border-blue-500/30 rounded-lg p-4">
              <div className="flex items-start gap-2 text-blue-400">
                <span className="text-xl">ℹ️</span>
                <div className="text-sm">
                  <p className="font-semibold mb-1">About 13F Filings</p>
                  <p className="text-blue-300/80">
                    Institutional investment managers with over $100M in assets must file Form 13F quarterly,
                    disclosing their holdings. Data is typically filed 45 days after quarter-end.
                  </p>
                </div>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default InstitutionalPage;
