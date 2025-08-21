import React, { useState, useEffect, useMemo } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
  ScatterChart,
  Scatter,
  Legend
} from 'recharts';
import {
  TrendingUp,
  TrendingDown,
  PieChart as PieChartIcon,
  BarChart3,
  ArrowLeft,
  Calendar,
  Filter,
  Download,
  RefreshCw
} from 'lucide-react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const PortfolioCharts = () => {
  const { portfolioId } = useParams();
  const navigate = useNavigate();
  
  // State management
  const [activeFilter, setActiveFilter] = useState('closed'); // 'closed' | 'all'
  const [assetFilter, setAssetFilter] = useState('combined'); // 'stocks' | 'options' | 'combined'
  const [allocationView, setAllocationView] = useState('stocks'); // 'stocks' | 'options' for pie chart
  const [timeFilter, setTimeFilter] = useState('all'); // 'daily' | 'weekly' | 'monthly' | 'all' | 'custom'
  const [showCalendar, setShowCalendar] = useState(false);
  const [customDateRange, setCustomDateRange] = useState({ start: '', end: '' });
  const [loading, setLoading] = useState(true);
  const [portfolioData, setPortfolioData] = useState(null);
  const [performanceData, setPerformanceData] = useState([]);
  const [allocationData, setAllocationData] = useState([]);
  const [error, setError] = useState(null);

  // Colors for charts
  const COLORS = {
    stocks: '#10B981', // Green
    options: '#3B82F6', // Blue  
    combined: '#F59E0B', // Orange
    cash: '#8B5CF6', // Purple
    margin: '#F59E0B', // Orange
    profit: '#10B981',
    loss: '#EF4444'
  };

  // Get color for allocation pie chart
  const getAllocationColor = (item, index) => {
    if (item.type === 'cash') return COLORS.cash;
    if (item.type === 'margin') return COLORS.margin;
    if (item.type === 'stocks') return COLORS.stocks;
    if (item.type === 'options') return COLORS.options;
    // Fallback colors for mixed items
    const fallbackColors = ['#EF4444', '#F59E0B', '#10B981', '#3B82F6', '#8B5CF6', '#EC4899'];
    return fallbackColors[index % fallbackColors.length];
  };

  // Portfolio information
  const portfolioInfo = {
    'htech-15t': { name: 'HTech 15T', value: 139902.60, cash: 100000.00 }
  };

  const currentPortfolio = portfolioInfo[portfolioId] || portfolioInfo['htech-15t'];

  // Fetch portfolio charts data
  const fetchPortfolioChartsData = async () => {
    setLoading(true);
    setError(null);
    try {
      const params = {
        filter: activeFilter,
        asset_type: assetFilter,
        timeframe: timeFilter,
        ...(timeFilter === 'custom' && customDateRange.start && customDateRange.end ? {
          start_date: customDateRange.start,
          end_date: customDateRange.end
        } : {})
      };

      // Fetch performance data
      const performanceResponse = await axios.get(`${API}/portfolio/${portfolioId}/performance`, { params });
      setPerformanceData(performanceResponse.data?.performance_data || []);

      // Fetch allocation data  
      const allocationResponse = await axios.get(`${API}/portfolio/${portfolioId}/allocation`, { params });
      setAllocationData(allocationResponse.data?.allocation_data || []);

      // Set portfolio summary
      setPortfolioData({
        total_value: performanceResponse.data?.portfolio_summary?.total_value || currentPortfolio.value,
        total_pnl: performanceResponse.data?.portfolio_summary?.total_pnl || 0,
        cash_balance: performanceResponse.data?.portfolio_summary?.cash_balance || currentPortfolio.cash
      });

    } catch (err) {
      console.error('Error fetching portfolio charts data:', err);
      setError('Failed to load portfolio charts data');
      // Use mock data for development
      generateMockData();
    } finally {
      setLoading(false);
    }
  };

  // Generate mock data for development
  const generateMockData = () => {
    const dates = [];
    const performanceData = [];
    
    // Generate 30 days of mock data
    for (let i = 29; i >= 0; i--) {
      const date = new Date();
      date.setDate(date.getDate() - i);
      const dateStr = date.toISOString().split('T')[0];
      
      const baseValue = 1000;
      const noise = Math.sin(i * 0.2) * 100 + Math.random() * 50 - 25;
      
      performanceData.push({
        date: dateStr,
        stocks_pnl: baseValue + noise,
        options_pnl: (baseValue * 0.3) + (noise * 0.5),
        combined_pnl: (baseValue * 1.3) + (noise * 1.2),
        cumulative_stocks: baseValue + noise + (i * 10),
        cumulative_options: (baseValue * 0.3) + (noise * 0.5) + (i * 3),
        cumulative_combined: (baseValue * 1.3) + (noise * 1.2) + (i * 13)
      });
    }

    const allocationData = [
      { name: 'AAPL', value: 25000, type: 'stocks', count: 5 },
      { name: 'MSFT', value: 20000, type: 'stocks', count: 3 },
      { name: 'GOOGL', value: 15000, type: 'stocks', count: 2 },
      { name: 'NVDA', value: 12000, type: 'stocks', count: 4 },
      { name: 'TSLA Calls', value: 8000, type: 'options', count: 10 },
      { name: 'SPY Puts', value: 5000, type: 'options', count: 5 },
      { name: 'Cash', value: 100000, type: 'cash', count: 1 },
      { name: 'Margin Available', value: 25000, type: 'margin', count: 1 }
    ];

    setPerformanceData(performanceData);
    setAllocationData(allocationData);
    setPortfolioData({
      total_value: currentPortfolio.value,
      total_pnl: 2500.75,
      cash_balance: currentPortfolio.cash
    });
  };

  useEffect(() => {
    fetchPortfolioChartsData();
  }, [portfolioId, activeFilter, assetFilter, timeFilter, customDateRange]);

  // Filter performance data for display
  const filteredPerformanceData = useMemo(() => {
    return performanceData.map(item => {
      if (assetFilter === 'stocks') {
        return { ...item, pnl: item.stocks_pnl, cumulative: item.cumulative_stocks };
      } else if (assetFilter === 'options') {
        return { ...item, pnl: item.options_pnl, cumulative: item.cumulative_options };
      } else {
        return { ...item, pnl: item.combined_pnl, cumulative: item.cumulative_combined };
      }
    });
  }, [performanceData, assetFilter]);

  // Filter allocation data based on allocation view (stocks/options toggle)
  const filteredAllocationData = useMemo(() => {
    let data = allocationData;
    
    // Always include cash and margin
    const cashAndMargin = data.filter(item => item.type === 'cash' || item.type === 'margin');
    
    // Filter based on allocation view toggle
    let filteredPositions;
    if (allocationView === 'stocks') {
      filteredPositions = data.filter(item => item.type === 'stocks');
    } else if (allocationView === 'options') {
      filteredPositions = data.filter(item => item.type === 'options');
    } else {
      // Combined view - show both stocks and options
      filteredPositions = data.filter(item => item.type === 'stocks' || item.type === 'options');
    }
    
    // Combine positions with cash and margin
    return [...filteredPositions, ...cashAndMargin];
  }, [allocationData, allocationView]);

  // Custom tooltip for performance chart
  const PerformanceTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white p-3 border border-gray-200 rounded-lg shadow-lg">
          <p className="font-medium">{label}</p>
          {payload.map((entry, index) => (
            <p key={index} style={{ color: entry.color }}>
              {entry.name}: ${entry.value?.toFixed(2)}
            </p>
          ))}
        </div>
      );
    }
    return null;
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading portfolio charts...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between py-4">
            <div className="flex items-center space-x-4">
              <button
                onClick={() => navigate(`/portfolios/${portfolioId}`)}
                className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <ArrowLeft size={20} className="text-gray-600" />
              </button>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">
                  {currentPortfolio.name} Charts
                </h1>
                <p className="text-gray-600">Portfolio performance and allocation analysis</p>
              </div>
            </div>
            
            <div className="flex items-center space-x-3">
              <button
                onClick={fetchPortfolioChartsData}
                className="flex items-center space-x-2 px-3 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                <RefreshCw size={16} />
                <span>Refresh</span>
              </button>
              <button className="flex items-center space-x-2 px-3 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors">
                <Download size={16} />
                <span>Export</span>
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {/* Filter Controls */}
        <div className="bg-white rounded-xl p-6 shadow-sm mb-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            
            {/* Trade Status Filter */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Trade Status</label>
              <div className="flex rounded-lg border border-gray-300 overflow-hidden">
                <button
                  onClick={() => setActiveFilter('closed')}
                  className={`flex-1 px-4 py-2 text-sm font-medium transition-colors ${
                    activeFilter === 'closed'
                      ? 'bg-blue-600 text-white'
                      : 'bg-white text-gray-700 hover:bg-gray-50'
                  }`}
                >
                  Closed Trades
                </button>
                <button
                  onClick={() => setActiveFilter('all')}
                  className={`flex-1 px-4 py-2 text-sm font-medium transition-colors ${
                    activeFilter === 'all'
                      ? 'bg-blue-600 text-white'
                      : 'bg-white text-gray-700 hover:bg-gray-50'
                  }`}
                >
                  All
                </button>
              </div>
            </div>

            {/* Asset Type Filter */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Asset Type</label>
              <div className="flex rounded-lg border border-gray-300 overflow-hidden">
                {['stocks', 'options', 'combined'].map((type) => (
                  <button
                    key={type}
                    onClick={() => setAssetFilter(type)}
                    className={`flex-1 px-3 py-2 text-sm font-medium transition-colors ${
                      assetFilter === type
                        ? 'bg-blue-600 text-white'
                        : 'bg-white text-gray-700 hover:bg-gray-50'
                    }`}
                  >
                    {type.charAt(0).toUpperCase() + type.slice(1)}
                  </button>
                ))}
              </div>
            </div>

            {/* Time Period Filter */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Time Period</label>
              <div className="flex rounded-lg border border-gray-300 overflow-hidden">
                {['daily', 'weekly', 'monthly', 'all'].map((period) => (
                  <button
                    key={period}
                    onClick={() => setTimeFilter(period)}
                    className={`flex-1 px-2 py-2 text-xs font-medium transition-colors ${
                      timeFilter === period
                        ? 'bg-blue-600 text-white'
                        : 'bg-white text-gray-700 hover:bg-gray-50'
                    }`}
                  >
                    {period.charAt(0).toUpperCase() + period.slice(1)}
                  </button>
                ))}
                <button
                  onClick={() => setShowCalendar(!showCalendar)}
                  className={`flex items-center justify-center px-3 py-2 text-xs font-medium transition-colors ${
                    timeFilter === 'custom'
                      ? 'bg-blue-600 text-white'
                      : 'bg-white text-gray-700 hover:bg-gray-50'
                  }`}
                >
                  <Calendar size={14} />
                </button>
              </div>
            </div>
          </div>

          {/* Custom Date Range */}
          {showCalendar && (
            <div className="mt-4 p-4 border border-gray-200 rounded-lg bg-gray-50">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Start Date</label>
                  <input
                    type="date"
                    value={customDateRange.start}
                    onChange={(e) => setCustomDateRange(prev => ({ ...prev, start: e.target.value }))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">End Date</label>
                  <input
                    type="date"
                    value={customDateRange.end}
                    onChange={(e) => setCustomDateRange(prev => ({ ...prev, end: e.target.value }))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
              </div>
              <button
                onClick={() => {
                  setTimeFilter('custom');
                  setShowCalendar(false);
                }}
                className="mt-3 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                Apply Custom Range
              </button>
            </div>
          )}
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
            <p className="text-red-700">{error}</p>
          </div>
        )}

        {/* Main Chart Area */}
        <div className="bg-white rounded-xl p-6 shadow-sm mb-6">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h2 className="text-xl font-bold text-gray-900">P&L Performance</h2>
              <p className="text-gray-600">
                {activeFilter === 'closed' ? 'Closed trades only' : 'All positions'} • 
                {assetFilter === 'combined' ? ' Stocks + Options' : ` ${assetFilter.charAt(0).toUpperCase() + assetFilter.slice(1)} only`}
              </p>
            </div>
            
            {/* Legend */}
            <div className="flex items-center space-x-4">
              {assetFilter === 'combined' ? (
                <>
                  <div className="flex items-center space-x-2">
                    <div className="w-4 h-4 bg-green-500 rounded"></div>
                    <span className="text-sm text-gray-600">Stocks</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <div className="w-4 h-4 bg-blue-500 rounded"></div>
                    <span className="text-sm text-gray-600">Options</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <div className="w-4 h-4 bg-orange-500 rounded"></div>
                    <span className="text-sm text-gray-600">Combined</span>
                  </div>
                </>
              ) : (
                <div className="flex items-center space-x-2">
                  <div className={`w-4 h-4 rounded`} style={{ backgroundColor: COLORS[assetFilter] }}></div>
                  <span className="text-sm text-gray-600">{assetFilter.charAt(0).toUpperCase() + assetFilter.slice(1)} P&L</span>
                </div>
              )}
            </div>
          </div>

          <div className="h-96">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={filteredPerformanceData}>
                <CartesianGrid 
                  strokeDasharray="3 3" 
                  stroke="#e2e8f0" 
                  strokeWidth={1}
                  horizontal={true}
                  vertical={false}
                />
                <XAxis 
                  dataKey="date" 
                  axisLine={false}
                  tickLine={false}
                  tick={{ fontSize: 12, fill: '#6B7280' }}
                />
                <YAxis 
                  orientation="right"
                  axisLine={false}
                  tickLine={false}
                  tick={{ fontSize: 12, fill: '#6B7280' }}
                  tickFormatter={(value) => `$${value.toFixed(0)}`}
                />
                <Tooltip content={<PerformanceTooltip />} />
                
                {assetFilter === 'combined' ? (
                  <>
                    <Line 
                      type="monotone" 
                      dataKey="stocks_pnl" 
                      stroke={COLORS.stocks} 
                      strokeWidth={2} 
                      dot={false}
                      name="Stocks P&L"
                    />
                    <Line 
                      type="monotone" 
                      dataKey="options_pnl" 
                      stroke={COLORS.options} 
                      strokeWidth={2} 
                      dot={false}
                      name="Options P&L"
                    />
                    <Line 
                      type="monotone" 
                      dataKey="combined_pnl" 
                      stroke={COLORS.combined} 
                      strokeWidth={3} 
                      dot={false}
                      name="Combined P&L"
                    />
                  </>
                ) : (
                  <Line 
                    type="monotone" 
                    dataKey="pnl" 
                    stroke={COLORS[assetFilter]} 
                    strokeWidth={3} 
                    dot={false}
                    name={`${assetFilter.charAt(0).toUpperCase() + assetFilter.slice(1)} P&L`}
                  />
                )}
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Side Charts */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
          
          {/* Allocation Pie Chart */}
          <div className="bg-white rounded-xl p-6 shadow-sm">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="text-lg font-bold text-gray-900">Portfolio Allocation</h3>
                <p className="text-gray-600">Active positions distribution</p>
              </div>
              <PieChartIcon size={20} className="text-gray-400" />
            </div>

            {/* Stocks/Options Toggle Switch */}
            <div className="flex justify-center mb-4">
              <div className="flex rounded-lg border border-gray-300 overflow-hidden bg-gray-50">
                <button
                  onClick={() => setAllocationView('stocks')}
                  className={`px-4 py-2 text-sm font-medium transition-colors ${
                    allocationView === 'stocks'
                      ? 'bg-green-600 text-white'
                      : 'bg-transparent text-gray-700 hover:bg-gray-100'
                  }`}
                >
                  📊 Stocks
                </button>
                <button
                  onClick={() => setAllocationView('options')}
                  className={`px-4 py-2 text-sm font-medium transition-colors ${
                    allocationView === 'options'
                      ? 'bg-blue-600 text-white'
                      : 'bg-transparent text-gray-700 hover:bg-gray-100'
                  }`}
                >
                  ⚡ Options
                </button>
              </div>
            </div>

            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={filteredAllocationData}
                    cx="50%"
                    cy="50%"
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                    label={({name, value}) => `${name}: $${(value/1000).toFixed(1)}k`}
                  >
                    {filteredAllocationData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={getAllocationColor(entry, index)} />
                    ))}
                  </Pie>
                  <Tooltip formatter={(value) => [`$${value.toLocaleString()}`, 'Value']} />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            </div>

            {/* Cash and Margin Information */}
            <div className="mt-4 grid grid-cols-2 gap-4">
              <div className="bg-purple-50 p-3 rounded-lg">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium text-purple-700">💰 Cash Available</span>
                  <span className="text-lg font-bold text-purple-900">$100k</span>
                </div>
                <p className="text-xs text-purple-600 mt-1">Available for withdrawal</p>
              </div>
              
              <div className="bg-orange-50 p-3 rounded-lg">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium text-orange-700">📈 Margin Use</span>
                  <span className="text-lg font-bold text-orange-900">$25k</span>
                </div>
                <p className="text-xs text-orange-600 mt-1">Available margin capacity</p>
              </div>
            </div>
          </div>

          {/* Risk/Return Scatter */}
          <div className="bg-white rounded-xl p-6 shadow-sm">
            <div className="flex items-center justify-between mb-6">
              <div>
                <h3 className="text-lg font-bold text-gray-900">Risk vs Return</h3>
                <p className="text-gray-600">Position analysis</p>
              </div>
              <BarChart3 size={20} className="text-gray-400" />
            </div>

            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <ScatterChart data={filteredAllocationData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis 
                    dataKey="count" 
                    name="Position Size" 
                    tick={{ fontSize: 12, fill: '#6B7280' }}
                  />
                  <YAxis 
                    orientation="right"
                    dataKey="value" 
                    name="Value" 
                    tick={{ fontSize: 12, fill: '#6B7280' }}
                    tickFormatter={(value) => `$${(value/1000).toFixed(0)}k`}
                  />
                  <Tooltip 
                    formatter={(value, name) => [
                      name === 'Value' ? `$${value.toLocaleString()}` : value,
                      name
                    ]}
                    labelFormatter={(label) => `Position: ${label}`}
                  />
                  <Scatter 
                    dataKey="value" 
                    fill={COLORS.combined}
                  />
                </ScatterChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>

        {/* Portfolio Summary Panel */}
        <div className="bg-white rounded-xl shadow-sm">
          <div className="px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-bold text-gray-900">Portfolio Summary</h3>
          </div>
          
          <div className="p-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="text-center">
                <div className="text-2xl font-bold text-gray-900">
                  ${portfolioData?.total_value?.toLocaleString() || '0.00'}
                </div>
                <div className="text-sm text-gray-600">Total Portfolio Value</div>
                <div className="text-xs text-gray-500 mt-1">
                  Cash excluded from charts: ${portfolioData?.cash_balance?.toLocaleString() || '0.00'}
                </div>
              </div>
              
              <div className="text-center">
                <div className={`text-2xl font-bold ${
                  (portfolioData?.total_pnl || 0) >= 0 ? 'text-green-600' : 'text-red-600'
                }`}>
                  {(portfolioData?.total_pnl || 0) >= 0 ? '+' : ''}${portfolioData?.total_pnl?.toFixed(2) || '0.00'}
                </div>
                <div className="text-sm text-gray-600">Total P&L</div>
                <div className="text-xs text-gray-500 mt-1">
                  {activeFilter === 'closed' ? 'Closed positions only' : 'All positions'}
                </div>
              </div>
              
              <div className="text-center">
                <div className="text-2xl font-bold text-gray-900">
                  {filteredAllocationData.length}
                </div>
                <div className="text-sm text-gray-600">Active Positions</div>
                <div className="text-xs text-gray-500 mt-1">
                  {assetFilter === 'combined' ? 'Stocks + Options' : assetFilter}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PortfolioCharts;