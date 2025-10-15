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
                         module.module === "SMART_REBALANCER" ? "⚖️" : "🎯"}
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
