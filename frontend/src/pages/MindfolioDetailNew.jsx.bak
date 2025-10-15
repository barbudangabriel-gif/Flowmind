import React, { useState, useEffect } from "react";
import { useParams } from "react-router-dom";
import { mfClient } from "../services/mindfolioClient";
import { Line, Bar } from "react-chartjs-2";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

export default function MindfolioDetailNew() {
  const { id } = useParams();
  const [mindfolio, setMindfolio] = useState(null);
  const [activeTab, setActiveTab] = useState("SUMMARY");
  const [timeRange, setTimeRange] = useState("1M");
  const [chartData, setChartData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedGreek, setSelectedGreek] = useState("Delta");
  const [isDashboardExpanded, setIsDashboardExpanded] = useState(false);

  useEffect(() => {
    loadMindfolio();
  }, [id]);

  useEffect(() => {
    if (activeTab === "SUMMARY") {
      loadChartData();
    }
  }, [timeRange, activeTab]);

  const loadMindfolio = async () => {
    try {
      const data = await mfClient.get(id);
      setMindfolio(data);
    } catch (err) {
      console.error("Failed to load mindfolio:", err);
    } finally {
      setLoading(false);
    }
  };

  const loadChartData = async () => {
    // Mock data - replace with real API call
    // GET /api/mindfolio/:id/performance?range=1M
    const mockData = generateMockChartData(timeRange);
    setChartData(mockData);
  };

  const generateMockChartData = (range) => {
    const points = range === "1M" ? 30 : range === "6M" ? 180 : range === "YTD" ? 250 : 365;
    const labels = [];
    const cashData = [];
    const stocksData = [];
    const optionsData = [];

    let baseCash = 25000;
    let baseStocks = 45000;
    let baseOptions = 15000;

    for (let i = 0; i < points; i++) {
      const date = new Date();
      date.setDate(date.getDate() - (points - i));
      labels.push(date.toISOString().split('T')[0]);

      // Simulate gradual growth with some volatility
      cashData.push(baseCash + (i * 50) + (Math.random() * 500 - 250));
      stocksData.push(baseStocks + (i * 100) + (Math.random() * 1000 - 500));
      optionsData.push(baseOptions + (i * 30) + (Math.random() * 300 - 150));
    }

    return {
      labels,
      datasets: [
        {
          label: "Cash",
          data: cashData,
          borderColor: "rgb(34, 197, 94)",
          backgroundColor: "rgba(34, 197, 94, 0.1)",
          fill: true,
          tension: 0.4
        },
        {
          label: "Stocks",
          data: stocksData,
          borderColor: "rgb(59, 130, 246)",
          backgroundColor: "rgba(59, 130, 246, 0.1)",
          fill: true,
          tension: 0.4
        },
        {
          label: "Options",
          data: optionsData,
          borderColor: "rgb(168, 85, 247)",
          backgroundColor: "rgba(168, 85, 247, 0.1)",
          fill: true,
          tension: 0.4
        }
      ]
    };
  };

  const generateROIChartData = () => {
    const points = 30; // Last 30 days
    const labels = [];
    const roiData = [];
    
    let roi = 0;
    for (let i = 0; i < points; i++) {
      const date = new Date();
      date.setDate(date.getDate() - (points - i));
      labels.push(date.toISOString().split('T')[0]);
      
      // Simulate gradual ROI growth
      roi += (Math.random() * 0.5 - 0.1); // Random daily change
      roiData.push(roi);
    }
    
    return {
      labels,
      datasets: [{
        label: "ROI %",
        data: roiData,
        borderColor: "rgb(34, 197, 94)",
        backgroundColor: (context) => {
          const ctx = context.chart.ctx;
          const gradient = ctx.createLinearGradient(0, 0, 0, 200);
          gradient.addColorStop(0, 'rgba(34, 197, 94, 0.3)');
          gradient.addColorStop(1, 'rgba(34, 197, 94, 0)');
          return gradient;
        },
        fill: true,
        tension: 0.4,
        pointRadius: 0,
        pointHoverRadius: 4
      }]
    };
  };

  if (loading) {
    return (
      <div className="p-8">
        <div className="text-white">Loading...</div>
      </div>
    );
  }

  if (!mindfolio) {
    return (
      <div className="p-8">
        <div className="text-red-400">Mindfolio not found</div>
      </div>
    );
  }

  // Calculate current values
  const currentCash = mindfolio.cash_balance || 25000;
  const currentStocks = 48500; // TODO: Calculate from positions
  const currentOptions = 16200; // TODO: Calculate from positions
  const totalValue = currentCash + currentStocks + currentOptions;
  
  // Calculate allocation percentages
  const cashPct = ((currentCash / totalValue) * 100).toFixed(1);
  const stocksPct = ((currentStocks / totalValue) * 100).toFixed(1);
  const optionsPct = ((currentOptions / totalValue) * 100).toFixed(1);

  // Drawdown calculation (mock)
  const initialValue = 85000;
  const drawdown = ((totalValue - initialValue) / initialValue * 100).toFixed(2);
  const isPositive = drawdown >= 0;

  const tabs = ["SUMMARY", "STOCKS", "OPTIONS", "DIVIDEND"];

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    interaction: {
      mode: 'index',
      intersect: false,
    },
    plugins: {
      legend: {
        position: 'bottom',
        labels: {
          color: '#94a3b8',
          padding: 15,
          font: { size: 12 }
        }
      },
      tooltip: {
        backgroundColor: 'rgba(15, 23, 42, 0.9)',
        titleColor: '#f1f5f9',
        bodyColor: '#cbd5e1',
        borderColor: '#334155',
        borderWidth: 1,
        padding: 12,
        displayColors: true,
        callbacks: {
          label: function(context) {
            return `${context.dataset.label}: $${context.parsed.y.toLocaleString()}`;
          },
          footer: function(tooltipItems) {
            const total = tooltipItems.reduce((sum, item) => sum + item.parsed.y, 0);
            return `Total: $${total.toLocaleString()}`;
          }
        }
      }
    },
    scales: {
      x: {
        grid: { color: '#1e293b', drawBorder: false },
        ticks: { color: '#64748b', maxRotation: 0 }
      },
      y: {
        grid: { color: '#1e293b', drawBorder: false },
        ticks: {
          color: '#64748b',
          callback: function(value) {
            return '$' + (value / 1000).toFixed(0) + 'k';
          }
        }
      }
    }
  };

  return (
    <div className="p-8 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white mb-1">{mindfolio.name}</h1>
          <p className="text-gray-400 text-sm">Mindfolio ID: {mindfolio.id}</p>
        </div>
        <div className="flex gap-3">
          <button className="px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-lg transition">
            Edit
          </button>
          <button className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg transition">
            + Add Position
          </button>
        </div>
      </div>

      {/* Tabs Navigation */}
      <div className="border-b border-slate-700">
        <div className="flex gap-1">
          {tabs.map(tab => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`px-6 py-3 font-medium transition ${
                activeTab === tab
                  ? 'text-white border-b-2 border-blue-500'
                  : 'text-gray-400 hover:text-gray-300'
              }`}
            >
              {tab}
            </button>
          ))}
        </div>
      </div>

      {/* Tab Content */}
      {activeTab === "SUMMARY" && (
        <div className="space-y-6">
          {/* Money Management & Risk Management Dashboard */}
          <div className="bg-slate-800/50 border border-slate-700 rounded-lg">
            {/* Dashboard Header */}
            <div className="flex items-center justify-between p-6 border-b border-slate-700">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-full bg-blue-500/20 flex items-center justify-center">
                  <span className="text-2xl">🛡️</span>
                </div>
                <div>
                  <h2 className="text-xl font-bold text-white">Money & Risk Management</h2>
                  <p className="text-sm text-gray-400">Portfolio health and risk metrics</p>
                </div>
              </div>
              <button 
                onClick={() => setIsDashboardExpanded(!isDashboardExpanded)}
                className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg transition flex items-center gap-2"
              >
                {isDashboardExpanded ? (
                  <>
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                    Collapse
                  </>
                ) : (
                  <>
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4" />
                    </svg>
                    Expand Full View
                  </>
                )}
              </button>
            </div>

            {/* Dashboard Content */}
            <div className="p-6 space-y-6">
              {/* Top Row - Key Metrics */}
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                {/* Portfolio Health Score */}
                <div className="bg-slate-700/30 rounded-lg p-4">
                  <div className="text-sm text-gray-400 mb-1">Portfolio Health</div>
                  <div className="flex items-baseline gap-2">
                    <div className="text-3xl font-bold text-green-400">87</div>
                    <div className="text-sm text-gray-400">/100</div>
                  </div>
                  <div className="text-xs text-green-400 mt-1">Excellent ✓</div>
                </div>

                {/* Sharpe Ratio */}
                <div className="bg-slate-700/30 rounded-lg p-4">
                  <div className="text-sm text-gray-400 mb-1">Sharpe Ratio</div>
                  <div className="text-3xl font-bold text-white">2.4</div>
                  <div className="text-xs text-green-400 mt-1">Above average</div>
                </div>

                {/* Max Drawdown */}
                <div className="bg-slate-700/30 rounded-lg p-4">
                  <div className="text-sm text-gray-400 mb-1">Max Drawdown</div>
                  <div className="text-3xl font-bold text-yellow-400">-8.2%</div>
                  <div className="text-xs text-gray-400 mt-1">Within limits</div>
                </div>

                {/* VaR (95%) */}
                <div className="bg-slate-700/30 rounded-lg p-4">
                  <div className="text-sm text-gray-400 mb-1">VaR (95%)</div>
                  <div className="text-3xl font-bold text-white">$2,450</div>
                  <div className="text-xs text-gray-400 mt-1">Daily risk at 95%</div>
                </div>
              </div>

              {/* Conditional Expanded Content */}
              {isDashboardExpanded && (
                <>
                  {/* Buying Power & Margin */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {/* Buying Power Utilization */}
                    <div className="bg-slate-700/30 rounded-lg p-5">
                      <h3 className="text-white font-semibold mb-4 flex items-center gap-2">
                        <span>💰</span> Buying Power Utilization
                      </h3>
                      <div className="space-y-3">
                        <div>
                          <div className="flex justify-between text-sm mb-1">
                            <span className="text-gray-400">Total Buying Power</span>
                            <span className="text-white font-medium">$100,000</span>
                          </div>
                          <div className="flex justify-between text-sm mb-1">
                            <span className="text-gray-400">Used</span>
                            <span className="text-white font-medium">$68,500 (68.5%)</span>
                          </div>
                          <div className="w-full bg-slate-600 rounded-full h-3">
                            <div className="bg-blue-500 h-3 rounded-full" style={{ width: '68.5%' }}></div>
                          </div>
                        </div>
                        <div className="pt-3 border-t border-slate-600">
                          <div className="flex justify-between text-sm">
                            <span className="text-gray-400">Available</span>
                            <span className="text-green-400 font-medium">$31,500</span>
                          </div>
                        </div>
                      </div>
                    </div>

                    {/* Margin Requirements */}
                    <div className="bg-slate-700/30 rounded-lg p-5">
                      <h3 className="text-white font-semibold mb-4 flex items-center gap-2">
                        <span>📊</span> Margin Requirements
                      </h3>
                      <div className="space-y-3">
                        <div className="flex justify-between">
                          <span className="text-gray-400 text-sm">Initial Margin</span>
                          <span className="text-white font-medium">$45,000</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-400 text-sm">Maintenance Margin</span>
                          <span className="text-white font-medium">$32,000</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-400 text-sm">Current Equity</span>
                          <span className="text-green-400 font-medium">$89,700</span>
                        </div>
                        <div className="flex justify-between pt-3 border-t border-slate-600">
                          <span className="text-gray-400 text-sm">Margin Cushion</span>
                          <span className="text-green-400 font-bold">$57,700 (180%)</span>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Risk Limits */}
                  <div className="bg-slate-700/30 rounded-lg p-5">
                    <h3 className="text-white font-semibold mb-4 flex items-center gap-2">
                      <span>⚠️</span> Risk Limits & Compliance
                    </h3>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      {/* Daily Risk */}
                      <div>
                        <div className="text-sm text-gray-400 mb-2">Daily Loss Limit</div>
                        <div className="flex items-baseline gap-2 mb-1">
                          <span className="text-white font-bold">-$450</span>
                          <span className="text-gray-400 text-sm">/ $2,000</span>
                        </div>
                        <div className="w-full bg-slate-600 rounded-full h-2">
                          <div className="bg-green-500 h-2 rounded-full" style={{ width: '22.5%' }}></div>
                        </div>
                        <div className="text-xs text-green-400 mt-1">22.5% used ✓</div>
                      </div>

                      {/* Weekly Risk */}
                      <div>
                        <div className="text-sm text-gray-400 mb-2">Weekly Loss Limit</div>
                        <div className="flex items-baseline gap-2 mb-1">
                          <span className="text-white font-bold">-$1,250</span>
                          <span className="text-gray-400 text-sm">/ $8,000</span>
                        </div>
                        <div className="w-full bg-slate-600 rounded-full h-2">
                          <div className="bg-green-500 h-2 rounded-full" style={{ width: '15.6%' }}></div>
                        </div>
                        <div className="text-xs text-green-400 mt-1">15.6% used ✓</div>
                      </div>

                      {/* Monthly Risk */}
                      <div>
                        <div className="text-sm text-gray-400 mb-2">Monthly Loss Limit</div>
                        <div className="flex items-baseline gap-2 mb-1">
                          <span className="text-white font-bold">+$3,200</span>
                          <span className="text-gray-400 text-sm">/ $15,000</span>
                        </div>
                        <div className="w-full bg-slate-600 rounded-full h-2">
                          <div className="bg-green-500 h-2 rounded-full" style={{ width: '21.3%' }}></div>
                        </div>
                        <div className="text-xs text-green-400 mt-1">Profit! +21.3% ✓</div>
                      </div>
                    </div>
                  </div>

                  {/* Concentration Risk & Correlation Matrix */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {/* Concentration Risk */}
                    <div className="bg-slate-700/30 rounded-lg p-5">
                      <h3 className="text-white font-semibold mb-4 flex items-center gap-2">
                        <span>🎯</span> Concentration Risk
                      </h3>
                      <div className="space-y-3">
                        {[
                          { symbol: 'TSLA', pct: 18, color: 'bg-red-500' },
                          { symbol: 'AAPL', pct: 15, color: 'bg-yellow-500' },
                          { symbol: 'SPY', pct: 12, color: 'bg-green-500' },
                          { symbol: 'NVDA', pct: 10, color: 'bg-green-500' },
                          { symbol: 'Other', pct: 45, color: 'bg-gray-500' }
                        ].map((item, idx) => (
                          <div key={idx}>
                            <div className="flex justify-between text-sm mb-1">
                              <span className="text-gray-400">{item.symbol}</span>
                              <span className="text-white">{item.pct}%</span>
                            </div>
                            <div className="w-full bg-slate-600 rounded-full h-2">
                              <div className={`${item.color} h-2 rounded-full`} style={{ width: `${item.pct}%` }}></div>
                            </div>
                          </div>
                        ))}
                      </div>
                      <div className="mt-4 p-3 bg-yellow-500/10 border border-yellow-500/30 rounded text-xs text-yellow-400">
                        ⚠️ TSLA concentration above 15% threshold
                      </div>
                    </div>

                    {/* Correlation Matrix Preview */}
                    <div className="bg-slate-700/30 rounded-lg p-5">
                      <h3 className="text-white font-semibold mb-4 flex items-center gap-2">
                        <span>🔗</span> Position Correlation
                      </h3>
                      <div className="grid grid-cols-4 gap-2 text-xs">
                        <div className="text-gray-400"></div>
                        <div className="text-gray-400 text-center">TSLA</div>
                        <div className="text-gray-400 text-center">AAPL</div>
                        <div className="text-gray-400 text-center">SPY</div>
                        
                        <div className="text-gray-400">TSLA</div>
                        <div className="bg-green-500/30 text-white text-center rounded py-1">1.00</div>
                        <div className="bg-yellow-500/30 text-white text-center rounded py-1">0.65</div>
                        <div className="bg-green-500/30 text-white text-center rounded py-1">0.72</div>
                        
                        <div className="text-gray-400">AAPL</div>
                        <div className="bg-yellow-500/30 text-white text-center rounded py-1">0.65</div>
                        <div className="bg-green-500/30 text-white text-center rounded py-1">1.00</div>
                        <div className="bg-yellow-500/30 text-white text-center rounded py-1">0.68</div>
                        
                        <div className="text-gray-400">SPY</div>
                        <div className="bg-green-500/30 text-white text-center rounded py-1">0.72</div>
                        <div className="bg-yellow-500/30 text-white text-center rounded py-1">0.68</div>
                        <div className="bg-green-500/30 text-white text-center rounded py-1">1.00</div>
                      </div>
                      <div className="mt-4 text-xs text-gray-400">
                        <div className="flex gap-3">
                          <span className="flex items-center gap-1">
                            <div className="w-3 h-3 bg-green-500/30 rounded"></div> Low (&lt;0.5)
                          </span>
                          <span className="flex items-center gap-1">
                            <div className="w-3 h-3 bg-yellow-500/30 rounded"></div> Medium (0.5-0.7)
                          </span>
                          <span className="flex items-center gap-1">
                            <div className="w-3 h-3 bg-red-500/30 rounded"></div> High (&gt;0.7)
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Position Sizing Analysis */}
                  <div className="bg-slate-700/30 rounded-lg p-5">
                    <h3 className="text-white font-semibold mb-4 flex items-center gap-2">
                      <span>📐</span> Position Sizing Analysis
                    </h3>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      <div>
                        <div className="text-sm text-gray-400 mb-1">Average Position Size</div>
                        <div className="text-2xl font-bold text-white">$5,240</div>
                        <div className="text-xs text-gray-400">Across 12 positions</div>
                      </div>
                      <div>
                        <div className="text-sm text-gray-400 mb-1">Largest Position</div>
                        <div className="text-2xl font-bold text-yellow-400">$9,200</div>
                        <div className="text-xs text-gray-400">TSLA (18% of portfolio)</div>
                      </div>
                      <div>
                        <div className="text-sm text-gray-400 mb-1">Smallest Position</div>
                        <div className="text-2xl font-bold text-white">$2,100</div>
                        <div className="text-xs text-gray-400">AMD (4% of portfolio)</div>
                      </div>
                    </div>
                  </div>
                </>
              )}
            </div>
          </div>

          {/* Chart Card */}
          <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-6">
            {/* Chart Header - Allocation & Current Value */}
            <div className="flex items-start justify-between mb-6">
              {/* Left: Allocation Breakdown */}
              <div className="space-y-2">
                <div className="text-sm text-gray-400 font-medium">Current Allocation</div>
                <div className="flex gap-4">
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 rounded-full bg-green-500"></div>
                    <span className="text-white font-medium">${(currentCash/1000).toFixed(1)}k</span>
                    <span className="text-gray-400 text-sm">({cashPct}%)</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 rounded-full bg-blue-500"></div>
                    <span className="text-white font-medium">${(currentStocks/1000).toFixed(1)}k</span>
                    <span className="text-gray-400 text-sm">({stocksPct}%)</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 rounded-full bg-purple-500"></div>
                    <span className="text-white font-medium">${(currentOptions/1000).toFixed(1)}k</span>
                    <span className="text-gray-400 text-sm">({optionsPct}%)</span>
                  </div>
                </div>
              </div>

              {/* Right: Total Value with Drawdown */}
              <div className="text-right">
                <div className="text-sm text-gray-400 font-medium mb-1">Total Value</div>
                <div className="text-3xl font-bold text-white">${(totalValue/1000).toFixed(1)}k</div>
                <div className={`text-sm font-medium ${isPositive ? 'text-green-400' : 'text-red-400'}`}>
                  {isPositive ? '+' : ''}{drawdown}% {isPositive ? '↑' : '↓'}
                </div>
              </div>
            </div>

            {/* Time Range Selector */}
            <div className="flex justify-start gap-2 mb-4">
              {["1M", "6M", "YTD", "ALL"].map(range => (
                <button
                  key={range}
                  onClick={() => setTimeRange(range)}
                  className={`px-4 py-1.5 rounded text-sm font-medium transition ${
                    timeRange === range
                      ? 'bg-blue-600 text-white'
                      : 'bg-slate-700/50 text-gray-400 hover:bg-slate-700 hover:text-gray-300'
                  }`}
                >
                  {range}
                </button>
              ))}
            </div>

            {/* Chart */}
            <div className="h-96">
              {chartData && <Line data={chartData} options={chartOptions} />}
            </div>
          </div>

          {/* Summary Stats Grid */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Cash */}
            <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-6">
              <div className="flex items-center gap-3 mb-3">
                <div className="w-10 h-10 rounded-full bg-green-500/20 flex items-center justify-center">
                  <span className="text-2xl">💵</span>
                </div>
                <div>
                  <div className="text-sm text-gray-400">Cash</div>
                  <div className="text-2xl font-bold text-white">${(currentCash/1000).toFixed(1)}k</div>
                </div>
              </div>
              <div className="text-sm text-gray-400">
                {cashPct}% of portfolio • Available for trading
              </div>
            </div>

            {/* Stocks */}
            <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-6">
              <div className="flex items-center gap-3 mb-3">
                <div className="w-10 h-10 rounded-full bg-blue-500/20 flex items-center justify-center">
                  <span className="text-2xl">📈</span>
                </div>
                <div>
                  <div className="text-sm text-gray-400">Stocks</div>
                  <div className="text-2xl font-bold text-white">${(currentStocks/1000).toFixed(1)}k</div>
                </div>
              </div>
              <div className="text-sm text-gray-400">
                {stocksPct}% of portfolio • 8 positions
              </div>
            </div>

            {/* Options */}
            <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-6">
              <div className="flex items-center gap-3 mb-3">
                <div className="w-10 h-10 rounded-full bg-purple-500/20 flex items-center justify-center">
                  <span className="text-2xl">⚡</span>
                </div>
                <div>
                  <div className="text-sm text-gray-400">Options</div>
                  <div className="text-2xl font-bold text-white">${(currentOptions/1000).toFixed(1)}k</div>
                </div>
              </div>
              <div className="text-sm text-gray-400">
                {optionsPct}% of portfolio • 12 contracts
              </div>
            </div>
          </div>

          {/* Module Allocation */}
          {mindfolio.modules && mindfolio.modules.length > 0 && (
            <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-6">
              <h3 className="text-xl font-semibold text-white mb-4">Module Allocation</h3>
              <div className="space-y-3">
                {mindfolio.modules.map((module, idx) => (
                  <div key={idx} className="flex items-center justify-between p-4 bg-slate-700/30 rounded-lg">
                    <div className="flex items-center gap-3">
                      <div className="text-2xl">
                        {module.module === "IV_SERVICE" ? "🤖" : 
                         module.module === "SELL_PUTS_ENGINE" ? "💰" :
                         module.module === "COVERED_CALLS_ENGINE" ? "📞" :
                         module.module === "GAMMA_SCALPER" ? "⚡" : "🎯"}
                      </div>
                      <div>
                        <div className="text-white font-medium">{module.module.replace(/_/g, ' ')}</div>
                        <div className="text-sm text-gray-400">
                          Max Risk: ${module.max_risk_per_trade} • Daily Limit: ${module.daily_loss_limit}
                        </div>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="text-white font-bold">${(module.budget/1000).toFixed(1)}k</div>
                      <div className="text-sm text-gray-400">
                        {((module.budget / mindfolio.cash_balance) * 100).toFixed(1)}% allocated
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Statistics Cards Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* ROI per Account Card */}
            <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-white">ROI per Account</h3>
                <button className="text-gray-400 hover:text-white transition">
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4" />
                  </svg>
                </button>
              </div>
              <div className="mb-3">
                <div className="text-3xl font-bold text-green-400">+{roiPct}%</div>
                <div className="text-sm text-gray-400">Current ROI</div>
              </div>
              <div className="h-48">
                <Line 
                  data={generateROIChartData()}
                  options={{
                    ...chartOptions,
                    plugins: {
                      legend: { display: false },
                      tooltip: {
                        backgroundColor: 'rgba(15, 23, 42, 0.9)',
                        borderColor: 'rgba(148, 163, 184, 0.2)',
                        borderWidth: 1,
                        padding: 12,
                        callbacks: {
                          label: (context) => `ROI: ${context.parsed.y.toFixed(2)}%`
                        }
                      }
                    },
                    scales: {
                      y: {
                        ...chartOptions.scales.y,
                        ticks: {
                          ...chartOptions.scales.y.ticks,
                          callback: (value) => `${value}%`
                        }
                      }
                    }
                  }}
                />
              </div>
            </div>

            {/* Daily Realized P/L Calendar Card */}
            <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-white">Daily Realized Profit/Loss</h3>
                <button className="text-gray-400 hover:text-white transition">
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4" />
                  </svg>
                </button>
              </div>
              <div className="mb-3">
                <div className="flex items-center justify-between">
                  <div>
                    <div className="text-sm text-gray-400">This Month</div>
                    <div className="text-2xl font-bold text-green-400">+$2,450</div>
                  </div>
                  <div className="text-right">
                    <div className="text-sm text-gray-400">Avg Daily</div>
                    <div className="text-lg font-bold text-white">+$122</div>
                  </div>
                </div>
              </div>
              <div className="grid grid-cols-7 gap-1">
                {/* Calendar heatmap - 28 days (4 weeks) */}
                {Array.from({ length: 28 }).map((_, i) => {
                  const pnl = (Math.random() - 0.4) * 500; // Random P/L
                  const intensity = Math.min(Math.abs(pnl) / 250, 1);
                  const bgColor = pnl >= 0 
                    ? `rgba(34, 197, 94, ${intensity * 0.6})` 
                    : `rgba(239, 68, 68, ${intensity * 0.6})`;
                  return (
                    <div
                      key={i}
                      className="aspect-square rounded cursor-pointer hover:ring-2 hover:ring-blue-500 transition"
                      style={{ backgroundColor: bgColor }}
                      title={`Day ${i+1}: ${pnl >= 0 ? '+' : ''}$${pnl.toFixed(0)}`}
                    />
                  );
                })}
              </div>
              <div className="mt-3 flex items-center justify-between text-xs text-gray-400">
                <span>🟢 Profit</span>
                <span>🔴 Loss</span>
              </div>
            </div>

            {/* Distribution of Daily Realized PnL Card */}
            <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-white">Distribution of Daily Realized PnL</h3>
                <button className="text-gray-400 hover:text-white transition">
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4" />
                  </svg>
                </button>
              </div>
              <div className="h-64">
                <Bar 
                  data={{
                    labels: ['-$1k+', '-$500', '-$250', '-$100', '$0', '$100', '$250', '$500', '$1k+'],
                    datasets: [{
                      label: 'Days',
                      data: [2, 5, 8, 12, 15, 20, 18, 10, 5],
                      backgroundColor: (context) => {
                        const index = context.dataIndex;
                        if (index < 4) return 'rgba(239, 68, 68, 0.8)'; // Red for losses
                        if (index === 4) return 'rgba(148, 163, 184, 0.8)'; // Gray for breakeven
                        return 'rgba(34, 197, 94, 0.8)'; // Green for profits
                      },
                      borderColor: (context) => {
                        const index = context.dataIndex;
                        if (index < 4) return 'rgb(239, 68, 68)';
                        if (index === 4) return 'rgb(148, 163, 184)';
                        return 'rgb(34, 197, 94)';
                      },
                      borderWidth: 1
                    }]
                  }}
                  options={{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                      legend: { display: false },
                      tooltip: {
                        backgroundColor: 'rgba(15, 23, 42, 0.9)',
                        borderColor: 'rgba(148, 163, 184, 0.2)',
                        borderWidth: 1,
                        padding: 12,
                        callbacks: {
                          label: (context) => `${context.parsed.y} days`
                        }
                      }
                    },
                    scales: {
                      x: {
                        grid: { color: 'rgba(148, 163, 184, 0.1)' },
                        ticks: { color: 'rgb(148, 163, 184)', font: { size: 11 } }
                      },
                      y: {
                        grid: { color: 'rgba(148, 163, 184, 0.1)' },
                        ticks: { color: 'rgb(148, 163, 184)' },
                        title: { display: true, text: 'Number of Days', color: 'rgb(148, 163, 184)' }
                      }
                    }
                  }}
                />
              </div>
            </div>

            {/* Distribution of Daily Returns Card */}
            <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-white">Distribution of Daily Returns</h3>
                <button className="text-gray-400 hover:text-white transition">
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4" />
                  </svg>
                </button>
              </div>
              <div className="mb-3">
                <label className="text-sm text-gray-400 mb-1 block">From:</label>
                <input 
                  type="date"
                  className="w-full bg-slate-700/50 border border-slate-600 rounded px-3 py-2 text-white text-sm"
                  defaultValue="2025-01-01"
                />
              </div>
              <div className="h-56">
                <Bar 
                  data={{
                    labels: ['-5%+', '-3%', '-2%', '-1%', '0%', '+1%', '+2%', '+3%', '+5%+'],
                    datasets: [{
                      label: 'Days',
                      data: [1, 4, 7, 15, 18, 22, 16, 8, 4],
                      backgroundColor: (context) => {
                        const index = context.dataIndex;
                        if (index < 4) return 'rgba(239, 68, 68, 0.8)';
                        if (index === 4) return 'rgba(148, 163, 184, 0.8)';
                        return 'rgba(34, 197, 94, 0.8)';
                      },
                      borderColor: (context) => {
                        const index = context.dataIndex;
                        if (index < 4) return 'rgb(239, 68, 68)';
                        if (index === 4) return 'rgb(148, 163, 184)';
                        return 'rgb(34, 197, 94)';
                      },
                      borderWidth: 1
                    }]
                  }}
                  options={{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                      legend: { display: false },
                      tooltip: {
                        backgroundColor: 'rgba(15, 23, 42, 0.9)',
                        borderColor: 'rgba(148, 163, 184, 0.2)',
                        borderWidth: 1,
                        padding: 12,
                        callbacks: {
                          label: (context) => `${context.parsed.y} days`
                        }
                      }
                    },
                    scales: {
                      x: {
                        grid: { color: 'rgba(148, 163, 184, 0.1)' },
                        ticks: { color: 'rgb(148, 163, 184)', font: { size: 11 } }
                      },
                      y: {
                        grid: { color: 'rgba(148, 163, 184, 0.1)' },
                        ticks: { color: 'rgb(148, 163, 184)' },
                        title: { display: true, text: 'Number of Days', color: 'rgb(148, 163, 184)' }
                      }
                    }
                  }}
                />
              </div>
            </div>
          </div>

          {/* Commissions & Fees Card - Full Width */}
          <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-white">Commissions & Fees</h3>
              <button className="text-gray-400 hover:text-white transition">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4" />
                </svg>
              </button>
            </div>
            <div className="h-64">
              <Bar 
                data={{
                  labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
                  datasets: [{
                    label: 'Total Fees',
                    data: [125, 180, 145, 210, 165, 190, 220, 175, 195, 240, 185, 205],
                    backgroundColor: 'rgba(239, 68, 68, 0.8)',
                    borderColor: 'rgb(239, 68, 68)',
                    borderWidth: 1
                  }]
                }}
                options={{
                  responsive: true,
                  maintainAspectRatio: false,
                  plugins: {
                    legend: { display: false },
                    tooltip: {
                      backgroundColor: 'rgba(15, 23, 42, 0.9)',
                      borderColor: 'rgba(148, 163, 184, 0.2)',
                      borderWidth: 1,
                      padding: 12,
                      callbacks: {
                        label: (context) => {
                          const commissions = (Math.random() * 100 + 50).toFixed(2);
                          const fees = (context.parsed.y - commissions).toFixed(2);
                          return [
                            `Total: $${context.parsed.y}`,
                            `Commissions: $${commissions}`,
                            `Fees: $${fees}`
                          ];
                        }
                      }
                    }
                  },
                  scales: {
                    x: {
                      grid: { color: 'rgba(148, 163, 184, 0.1)' },
                      ticks: { color: 'rgb(148, 163, 184)' }
                    },
                    y: {
                      position: 'left',
                      grid: { color: 'rgba(148, 163, 184, 0.1)' },
                      ticks: { 
                        color: 'rgb(148, 163, 184)',
                        callback: (value) => `$${value}`
                      },
                      title: { display: true, text: 'Amount ($)', color: 'rgb(148, 163, 184)' }
                    }
                  }
                }}
              />
            </div>
            <div className="mt-4 flex items-center justify-center gap-6 text-sm">
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full bg-red-500"></div>
                <span className="text-gray-400">Commissions</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full bg-red-400"></div>
                <span className="text-gray-400">Fees</span>
              </div>
            </div>
          </div>

          {/* Options Charts Section Title */}
          <div className="mt-8">
            <h2 className="text-2xl font-bold text-white mb-6">Options Charts</h2>
          </div>

          {/* Profit/Loss by Sector & Market Cap */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Profit/Loss by Sector */}
            <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-white">Profit/Loss by Sector</h3>
                <button className="text-gray-400 hover:text-white transition">
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4" />
                  </svg>
                </button>
              </div>
              <div className="h-80">
                <Bar 
                  data={{
                    labels: ['Technology', 'Healthcare', 'Finance', 'Energy', 'Consumer', 'Industrial'],
                    datasets: [{
                      label: 'P/L',
                      data: [2500, 1800, -800, 1200, 3200, -500],
                      backgroundColor: (context) => {
                        const value = context.parsed.x;
                        return value >= 0 ? 'rgba(34, 197, 94, 0.8)' : 'rgba(239, 68, 68, 0.8)';
                      },
                      borderColor: (context) => {
                        const value = context.parsed.x;
                        return value >= 0 ? 'rgb(34, 197, 94)' : 'rgb(239, 68, 68)';
                      },
                      borderWidth: 1
                    }]
                  }}
                  options={{
                    indexAxis: 'y',
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                      legend: { display: false },
                      tooltip: {
                        backgroundColor: 'rgba(15, 23, 42, 0.9)',
                        borderColor: 'rgba(148, 163, 184, 0.2)',
                        borderWidth: 1,
                        padding: 12,
                        callbacks: {
                          label: (context) => `P/L: $${context.parsed.x.toLocaleString()}`
                        }
                      }
                    },
                    scales: {
                      x: {
                        grid: { color: 'rgba(148, 163, 184, 0.1)' },
                        ticks: { 
                          color: 'rgb(148, 163, 184)',
                          callback: (value) => `$${value/1000}k`
                        }
                      },
                      y: {
                        grid: { display: false },
                        ticks: { color: 'rgb(148, 163, 184)' }
                      }
                    }
                  }}
                />
              </div>
            </div>

            {/* Profit/Loss by Market Cap */}
            <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-white">Profit/Loss by Market Cap</h3>
                <button className="text-gray-400 hover:text-white transition">
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4" />
                  </svg>
                </button>
              </div>
              <div className="h-80">
                <Bar 
                  data={{
                    labels: ['Mega Cap', 'Large Cap', 'Mid Cap'],
                    datasets: [{
                      label: 'P/L',
                      data: [4500, 2800, -1200],
                      backgroundColor: (context) => {
                        const value = context.parsed.x;
                        return value >= 0 ? 'rgba(34, 197, 94, 0.8)' : 'rgba(239, 68, 68, 0.8)';
                      },
                      borderColor: (context) => {
                        const value = context.parsed.x;
                        return value >= 0 ? 'rgb(34, 197, 94)' : 'rgb(239, 68, 68)';
                      },
                      borderWidth: 1
                    }]
                  }}
                  options={{
                    indexAxis: 'y',
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                      legend: { display: false },
                      tooltip: {
                        backgroundColor: 'rgba(15, 23, 42, 0.9)',
                        borderColor: 'rgba(148, 163, 184, 0.2)',
                        borderWidth: 1,
                        padding: 12,
                        callbacks: {
                          label: (context) => `P/L: $${context.parsed.x.toLocaleString()}`
                        }
                      }
                    },
                    scales: {
                      x: {
                        grid: { color: 'rgba(148, 163, 184, 0.1)' },
                        ticks: { 
                          color: 'rgb(148, 163, 184)',
                          callback: (value) => `$${value/1000}k`
                        }
                      },
                      y: {
                        grid: { display: false },
                        ticks: { color: 'rgb(148, 163, 184)', font: { size: 14 } }
                      }
                    }
                  }}
                />
              </div>
            </div>
          </div>

          {/* Profit/Loss by Ticker - Full Width */}
          <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-white">Profit/Loss by Ticker</h3>
              <button className="text-gray-400 hover:text-white transition">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4" />
                </svg>
              </button>
            </div>
            <div className="h-96">
              <Bar 
                data={{
                  labels: ['TSLA', 'AAPL', 'NVDA', 'MSFT', 'GOOGL', 'META', 'AMZN', 'NFLX', 'AMD', 'INTC'],
                  datasets: [{
                    label: 'P/L',
                    data: [3500, 2200, -1500, 1800, 2800, -800, 1200, 900, -600, 1500],
                    backgroundColor: (context) => {
                      const value = context.parsed.x;
                      return value >= 0 ? 'rgba(34, 197, 94, 0.8)' : 'rgba(239, 68, 68, 0.8)';
                    },
                    borderColor: (context) => {
                      const value = context.parsed.x;
                      return value >= 0 ? 'rgb(34, 197, 94)' : 'rgb(239, 68, 68)';
                    },
                    borderWidth: 1
                  }]
                }}
                options={{
                  indexAxis: 'y',
                  responsive: true,
                  maintainAspectRatio: false,
                  plugins: {
                    legend: { display: false },
                    tooltip: {
                      backgroundColor: 'rgba(15, 23, 42, 0.9)',
                      borderColor: 'rgba(148, 163, 184, 0.2)',
                      borderWidth: 1,
                      padding: 12,
                      callbacks: {
                        label: (context) => {
                          const value = context.parsed.x;
                          return `P/L: ${value >= 0 ? '+' : ''}$${value.toLocaleString()}`;
                        }
                      }
                    }
                  },
                  scales: {
                    x: {
                      grid: { color: 'rgba(148, 163, 184, 0.1)' },
                      ticks: { 
                        color: 'rgb(148, 163, 184)',
                        callback: (value) => `${value >= 0 ? '+' : ''}$${Math.abs(value)/1000}k`
                      }
                    },
                    y: {
                      grid: { display: false },
                      ticks: { color: 'rgb(148, 163, 184)', font: { size: 13, weight: 'bold' } }
                    }
                  }
                }}
              />
            </div>
          </div>

          {/* Profit/Loss by Strategy - Full Width */}
          <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-white">Profit/Loss by Strategy</h3>
              <button className="text-gray-400 hover:text-white transition">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4" />
                </svg>
              </button>
            </div>
            <div className="h-96">
              <Bar 
                data={{
                  labels: ['Iron Condor', 'Bull Call Spread', 'Covered Call', 'Cash Secured Put', 'Straddle', 'Strangle', 'Butterfly', 'Calendar Spread'],
                  datasets: [{
                    label: 'P/L',
                    data: [4200, 2800, 3500, -1200, 1800, -900, 1500, 2200],
                    backgroundColor: (context) => {
                      const value = context.parsed.x;
                      return value >= 0 ? 'rgba(34, 197, 94, 0.8)' : 'rgba(239, 68, 68, 0.8)';
                    },
                    borderColor: (context) => {
                      const value = context.parsed.x;
                      return value >= 0 ? 'rgb(34, 197, 94)' : 'rgb(239, 68, 68)';
                    },
                    borderWidth: 1
                  }]
                }}
                options={{
                  indexAxis: 'y',
                  responsive: true,
                  maintainAspectRatio: false,
                  plugins: {
                    legend: { display: false },
                    tooltip: {
                      backgroundColor: 'rgba(15, 23, 42, 0.9)',
                      borderColor: 'rgba(148, 163, 184, 0.2)',
                      borderWidth: 1,
                      padding: 12,
                      callbacks: {
                        label: (context) => {
                          const value = context.parsed.x;
                          return `P/L: ${value >= 0 ? '+' : ''}$${value.toLocaleString()}`;
                        }
                      }
                    }
                  },
                  scales: {
                    x: {
                      grid: { color: 'rgba(148, 163, 184, 0.1)' },
                      ticks: { 
                        color: 'rgb(148, 163, 184)',
                        callback: (value) => `${value >= 0 ? '+' : ''}$${Math.abs(value)/1000}k`
                      }
                    },
                    y: {
                      grid: { display: false },
                      ticks: { color: 'rgb(148, 163, 184)', font: { size: 12 } }
                    }
                  }
                }}
              />
            </div>
          </div>

          {/* Profit/Loss by Options Liquidity & Holding Period */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Profit/Loss by Options Liquidity */}
            <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-white">Profit/Loss by Options Liquidity</h3>
                <button className="text-gray-400 hover:text-white transition">
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4" />
                  </svg>
                </button>
              </div>
              <div className="h-80">
                <Bar 
                  data={{
                    labels: ['High Liquidity', 'Medium Liquidity', 'Low Liquidity'],
                    datasets: [{
                      label: 'P/L',
                      data: [4800, 2200, -1500],
                      backgroundColor: (context) => {
                        const value = context.parsed.x;
                        return value >= 0 ? 'rgba(34, 197, 94, 0.8)' : 'rgba(239, 68, 68, 0.8)';
                      },
                      borderColor: (context) => {
                        const value = context.parsed.x;
                        return value >= 0 ? 'rgb(34, 197, 94)' : 'rgb(239, 68, 68)';
                      },
                      borderWidth: 1
                    }]
                  }}
                  options={{
                    indexAxis: 'y',
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                      legend: { display: false },
                      tooltip: {
                        backgroundColor: 'rgba(15, 23, 42, 0.9)',
                        borderColor: 'rgba(148, 163, 184, 0.2)',
                        borderWidth: 1,
                        padding: 12,
                        callbacks: {
                          label: (context) => `P/L: $${context.parsed.x.toLocaleString()}`
                        }
                      }
                    },
                    scales: {
                      x: {
                        grid: { color: 'rgba(148, 163, 184, 0.1)' },
                        ticks: { 
                          color: 'rgb(148, 163, 184)',
                          callback: (value) => `$${value/1000}k`
                        }
                      },
                      y: {
                        grid: { display: false },
                        ticks: { color: 'rgb(148, 163, 184)', font: { size: 14 } }
                      }
                    }
                  }}
                />
              </div>
            </div>

            {/* Profit/Loss by Holding Period */}
            <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-white">Profit/Loss by Holding Period</h3>
                <button className="text-gray-400 hover:text-white transition">
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4" />
                  </svg>
                </button>
              </div>
              <div className="h-80">
                <Bar 
                  data={{
                    labels: ['Day 1', 'Day 2', 'Day 3', 'Day 4', 'Day 5', 'Day 6', 'Day 7', 'Day 8', 'Day 9', 'Day 10'],
                    datasets: [
                      {
                        type: 'bar',
                        label: 'Daily P/L',
                        data: [200, -150, 300, 180, -220, 350, 120, -180, 280, 400],
                        backgroundColor: (context) => {
                          const value = context.parsed.y;
                          return value >= 0 ? 'rgba(34, 197, 94, 0.8)' : 'rgba(239, 68, 68, 0.8)';
                        },
                        borderColor: (context) => {
                          const value = context.parsed.y;
                          return value >= 0 ? 'rgb(34, 197, 94)' : 'rgb(239, 68, 68)';
                        },
                        borderWidth: 1,
                        order: 2
                      },
                      {
                        type: 'line',
                        label: 'Cumulative P/L',
                        data: [200, 50, 350, 530, 310, 660, 780, 600, 880, 1280],
                        borderColor: 'rgb(148, 163, 184)',
                        backgroundColor: 'rgba(148, 163, 184, 0.1)',
                        borderWidth: 2,
                        pointRadius: 4,
                        pointBackgroundColor: 'rgb(148, 163, 184)',
                        pointBorderColor: 'rgb(148, 163, 184)',
                        tension: 0.3,
                        order: 1
                      }
                    ]
                  }}
                  options={{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                      legend: { 
                        display: true,
                        position: 'top',
                        labels: {
                          color: 'rgb(148, 163, 184)',
                          font: { size: 12 },
                          usePointStyle: true
                        }
                      },
                      tooltip: {
                        backgroundColor: 'rgba(15, 23, 42, 0.9)',
                        borderColor: 'rgba(148, 163, 184, 0.2)',
                        borderWidth: 1,
                        padding: 12,
                        callbacks: {
                          label: (context) => {
                            const label = context.dataset.label;
                            const value = context.parsed.y;
                            return `${label}: ${value >= 0 ? '+' : ''}$${value}`;
                          }
                        }
                      }
                    },
                    scales: {
                      x: {
                        grid: { color: 'rgba(148, 163, 184, 0.1)' },
                        ticks: { color: 'rgb(148, 163, 184)' }
                      },
                      y: {
                        grid: { color: 'rgba(148, 163, 184, 0.1)' },
                        ticks: { 
                          color: 'rgb(148, 163, 184)',
                          callback: (value) => `$${value}`
                        },
                        title: { display: true, text: 'P/L ($)', color: 'rgb(148, 163, 184)' }
                      }
                    }
                  }}
                />
              </div>
            </div>
          </div>

          {/* Profit/Loss by Time Opened & Greeks */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Profit/Loss by Time Opened */}
            <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-white">Profit/Loss by Time Opened</h3>
                <button className="text-gray-400 hover:text-white transition">
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4" />
                  </svg>
                </button>
              </div>
              <div className="h-80">
                <Bar 
                  data={{
                    labels: ['9:30', '9:40', '9:50', '10:00', '10:10', '10:20', '10:30', '10:40', '10:50', '11:00', 
                             '11:10', '11:20', '11:30', '11:40', '11:50', '12:00', '12:10', '12:20', '12:30', '12:40',
                             '12:50', '13:00', '13:10', '13:20', '13:30', '13:40', '13:50', '14:00', '14:10', '14:20',
                             '14:30', '14:40', '14:50', '15:00', '15:10', '15:20', '15:30', '15:40', '15:50', '16:00'],
                    datasets: [{
                      label: 'P/L by Open Time',
                      data: [150, -80, 220, 180, -120, 290, 160, -90, 240, 310, 
                             -140, 190, 270, 130, -160, 200, 250, -110, 180, 320,
                             -170, 210, 280, 150, -130, 230, 190, 260, -150, 210,
                             180, -120, 240, 270, 190, -140, 220, 250, 180, 300],
                      backgroundColor: (context) => {
                        const value = context.parsed.y;
                        return value >= 0 ? 'rgba(34, 197, 94, 0.8)' : 'rgba(239, 68, 68, 0.8)';
                      },
                      borderColor: (context) => {
                        const value = context.parsed.y;
                        return value >= 0 ? 'rgb(34, 197, 94)' : 'rgb(239, 68, 68)';
                      },
                      borderWidth: 1
                    }]
                  }}
                  options={{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                      legend: { display: false },
                      tooltip: {
                        backgroundColor: 'rgba(15, 23, 42, 0.9)',
                        borderColor: 'rgba(148, 163, 184, 0.2)',
                        borderWidth: 1,
                        padding: 12,
                        callbacks: {
                          label: (context) => {
                            const value = context.parsed.y;
                            return `P/L: ${value >= 0 ? '+' : ''}$${value}`;
                          }
                        }
                      }
                    },
                    scales: {
                      x: {
                        grid: { color: 'rgba(148, 163, 184, 0.1)' },
                        ticks: { 
                          color: 'rgb(148, 163, 184)',
                          maxRotation: 45,
                          minRotation: 45,
                          font: { size: 9 }
                        }
                      },
                      y: {
                        grid: { color: 'rgba(148, 163, 184, 0.1)' },
                        ticks: { 
                          color: 'rgb(148, 163, 184)',
                          callback: (value) => `$${value}`
                        },
                        title: { display: true, text: 'P/L ($)', color: 'rgb(148, 163, 184)' }
                      }
                    }
                  }}
                />
              </div>
            </div>

            {/* Profit/Loss by Greeks */}
            <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-white">Profit/Loss by Greeks</h3>
                <button className="text-gray-400 hover:text-white transition">
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4" />
                  </svg>
                </button>
              </div>
              <div className="mb-3">
                <select
                  value={selectedGreek}
                  onChange={(e) => setSelectedGreek(e.target.value)}
                  className="w-full bg-slate-700/50 border border-slate-600 rounded px-3 py-2 text-white text-sm"
                >
                  <option value="Delta">Delta</option>
                  <option value="Theta">Theta</option>
                  <option value="Vega">Vega</option>
                </select>
              </div>
              <div className="h-72">
                <Line 
                  data={{
                    labels: Array.from({ length: 20 }, (_, i) => `T${i+1}`),
                    datasets: [{
                      label: `${selectedGreek} P/L`,
                      data: selectedGreek === 'Delta' 
                        ? [250, -150, 320, 180, -200, 290, 160, -140, 240, 310, -180, 220, 280, -160, 200, 270, -190, 230, 260, 300]
                        : selectedGreek === 'Theta'
                        ? [-120, 180, -90, 240, 160, -130, 210, -170, 190, 220, -150, 200, -110, 230, 180, -140, 210, 250, -160, 190]
                        : [190, -170, 260, 140, -200, 280, 150, -130, 230, 270, -180, 210, 240, -150, 190, 250, -170, 220, 260, 290],
                      borderColor: 'rgba(148, 163, 184, 0.5)',
                      backgroundColor: 'transparent',
                      borderWidth: 1,
                      pointRadius: 6,
                      pointHoverRadius: 8,
                      pointBackgroundColor: (context) => {
                        const value = context.parsed.y;
                        return value >= 0 ? 'rgb(34, 197, 94)' : 'rgb(239, 68, 68)';
                      },
                      pointBorderColor: (context) => {
                        const value = context.parsed.y;
                        return value >= 0 ? 'rgb(34, 197, 94)' : 'rgb(239, 68, 68)';
                      },
                      pointBorderWidth: 2,
                      tension: 0
                    }]
                  }}
                  options={{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                      legend: { display: false },
                      tooltip: {
                        backgroundColor: 'rgba(15, 23, 42, 0.9)',
                        borderColor: 'rgba(148, 163, 184, 0.2)',
                        borderWidth: 1,
                        padding: 12,
                        callbacks: {
                          title: (context) => `Trade ${context[0].label}`,
                          label: (context) => {
                            const value = context.parsed.y;
                            return [
                              `${selectedGreek}: ${value >= 0 ? '+' : ''}${value.toFixed(2)}`,
                              `P/L: ${value >= 0 ? '+' : ''}$${Math.abs(value * 10).toFixed(0)}`
                            ];
                          }
                        }
                      }
                    },
                    scales: {
                      x: {
                        grid: { color: 'rgba(148, 163, 184, 0.1)' },
                        ticks: { 
                          color: 'rgb(148, 163, 184)',
                          font: { size: 10 }
                        }
                      },
                      y: {
                        grid: { 
                          color: (context) => {
                            return context.tick.value === 0 
                              ? 'rgba(148, 163, 184, 0.5)' 
                              : 'rgba(148, 163, 184, 0.1)';
                          },
                          lineWidth: (context) => context.tick.value === 0 ? 2 : 1
                        },
                        ticks: { 
                          color: 'rgb(148, 163, 184)',
                          callback: (value) => value.toFixed(1)
                        },
                        title: { 
                          display: true, 
                          text: `${selectedGreek} Value`, 
                          color: 'rgb(148, 163, 184)' 
                        }
                      }
                    }
                  }}
                />
              </div>
            </div>
          </div>
        </div>
      )}

      {activeTab === "STOCKS" && (
        <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-6">
          <h3 className="text-xl font-semibold text-white mb-4">Stock Positions</h3>
          <div className="text-gray-400">Coming soon: Stock positions with cost basis, current value, P&L</div>
        </div>
      )}

      {activeTab === "OPTIONS" && (
        <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-6">
          <h3 className="text-xl font-semibold text-white mb-4">Options Positions</h3>
          <div className="text-gray-400">Coming soon: Options with Greeks, DTE, P&L breakdown</div>
        </div>
      )}

      {activeTab === "DIVIDEND" && (
        <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-6">
          <h3 className="text-xl font-semibold text-white mb-4">Dividend Income</h3>
          <div className="text-gray-400">Coming soon: Dividend tracking and projections</div>
        </div>
      )}
    </div>
  );
}
