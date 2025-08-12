import React, { useState, useEffect } from "react";
import { BrowserRouter, Routes, Route, Link, useLocation } from "react-router-dom";
import axios from "axios";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  ComposedChart,
  Area,
  AreaChart
} from "recharts";
import {
  TrendingUp,
  TrendingDown,
  DollarSign,
  BarChart3,
  PieChart as PieChartIcon,
  Search,
  Plus,
  Trash2,
  Eye,
  Activity,
  Target,
  Briefcase,
  Home,
  Star,
  Newspaper,
  Settings,
  Database,
  Target
} from "lucide-react";
import AdvancedScreener from "./components/AdvancedScreener";
import InvestmentScoring from "./components/InvestmentScoring";
import "./App.css";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Navigation Component
const Sidebar = ({ activeTab, setActiveTab }) => {
  const menuItems = [
    { id: 'dashboard', label: 'Dashboard', icon: Home },
    { id: 'portfolio', label: 'Portfolio', icon: Briefcase },
    { id: 'screener', label: 'Advanced Screener', icon: Database },
    { id: 'simple-screener', label: 'Stock Search', icon: Search },
    { id: 'watchlist', label: 'Watchlist', icon: Star },
    { id: 'technical', label: 'Technical Analysis', icon: BarChart3 },
    { id: 'news', label: 'Market News', icon: Newspaper }
  ];

  return (
    <div className="w-64 bg-gray-900 text-white h-screen fixed left-0 top-0 overflow-y-auto">
      <div className="p-4">
        <h1 className="text-xl font-bold mb-8 text-blue-400">📈 Market Insight</h1>
        <nav className="space-y-2">
          {menuItems.map((item) => {
            const Icon = item.icon;
            return (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                className={`w-full flex items-center space-x-3 px-4 py-2 rounded-lg transition-colors ${
                  activeTab === item.id
                    ? 'bg-blue-600 text-white'
                    : 'text-gray-300 hover:bg-gray-700'
                }`}
              >
                <Icon size={20} />
                <span>{item.label}</span>
              </button>
            );
          })}
        </nav>
      </div>
    </div>
  );
};

// Dashboard Component
const Dashboard = () => {
  const [marketData, setMarketData] = useState(null);
  const [topMovers, setTopMovers] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchMarketData();
  }, []);

  const fetchMarketData = async () => {
    try {
      const [overviewRes, moversRes] = await Promise.all([
        axios.get(`${API}/market/overview`),
        axios.get(`${API}/market/top-movers`)
      ]);
      
      setMarketData(overviewRes.data);
      setTopMovers(moversRes.data);
    } catch (error) {
      console.error('Error fetching market data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="flex justify-center items-center h-64">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
    </div>;
  }

  const formatNumber = (num) => {
    if (num >= 1e9) return (num / 1e9).toFixed(2) + 'B';
    if (num >= 1e6) return (num / 1e6).toFixed(2) + 'M';
    if (num >= 1e3) return (num / 1e3).toFixed(2) + 'K';
    return num?.toFixed(2) || '0.00';
  };

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-gray-800">Market Dashboard</h2>
      
      {/* Market Indices */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {marketData?.indices?.map((index, idx) => (
          <div key={idx} className="bg-white p-4 rounded-lg shadow-md">
            <div className="flex justify-between items-center">
              <div>
                <h3 className="text-sm font-medium text-gray-600">{index.symbol}</h3>
                <p className="text-xl font-bold">${index.price?.toFixed(2)}</p>
                <div className={`flex items-center space-x-1 text-sm ${
                  index.change >= 0 ? 'text-green-600' : 'text-red-600'
                }`}>
                  {index.change >= 0 ? <TrendingUp size={16} /> : <TrendingDown size={16} />}
                  <span>{index.change?.toFixed(2)} ({index.change_percent?.toFixed(2)}%)</span>
                </div>
              </div>
              <Activity className="h-8 w-8 text-gray-400" />
            </div>
          </div>
        ))}
      </div>

      {/* Top Movers */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h3 className="text-lg font-semibold mb-4 text-green-600">Top Gainers</h3>
          <div className="space-y-3">
            {topMovers?.gainers?.slice(0, 5).map((stock, idx) => (
              <div key={idx} className="flex justify-between items-center p-2 hover:bg-gray-50 rounded">
                <div>
                  <span className="font-medium">{stock.symbol}</span>
                  <p className="text-sm text-gray-600">${stock.price?.toFixed(2)}</p>
                </div>
                <div className="text-right">
                  <span className="text-green-600 font-medium">+{stock.change_percent?.toFixed(2)}%</span>
                  <p className="text-sm text-gray-600">+${stock.change?.toFixed(2)}</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-md">
          <h3 className="text-lg font-semibold mb-4 text-red-600">Top Losers</h3>
          <div className="space-y-3">
            {topMovers?.losers?.slice(0, 5).map((stock, idx) => (
              <div key={idx} className="flex justify-between items-center p-2 hover:bg-gray-50 rounded">
                <div>
                  <span className="font-medium">{stock.symbol}</span>
                  <p className="text-sm text-gray-600">${stock.price?.toFixed(2)}</p>
                </div>
                <div className="text-right">
                  <span className="text-red-600 font-medium">{stock.change_percent?.toFixed(2)}%</span>
                  <p className="text-sm text-gray-600">${stock.change?.toFixed(2)}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

// Portfolio Component
const Portfolio = () => {
  const [portfolio, setPortfolio] = useState(null);
  const [showAddForm, setShowAddForm] = useState(false);
  const [formData, setFormData] = useState({
    symbol: '',
    shares: '',
    purchase_price: '',
    purchase_date: new Date().toISOString().split('T')[0]
  });

  useEffect(() => {
    fetchPortfolio();
  }, []);

  const fetchPortfolio = async () => {
    try {
      const response = await axios.get(`${API}/portfolio`);
      setPortfolio(response.data);
    } catch (error) {
      console.error('Error fetching portfolio:', error);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${API}/portfolio`, {
        ...formData,
        shares: parseFloat(formData.shares),
        purchase_price: parseFloat(formData.purchase_price),
        purchase_date: new Date(formData.purchase_date).toISOString()
      });
      
      setFormData({ symbol: '', shares: '', purchase_price: '', purchase_date: new Date().toISOString().split('T')[0] });
      setShowAddForm(false);
      fetchPortfolio();
    } catch (error) {
      console.error('Error adding portfolio item:', error);
    }
  };

  const deleteItem = async (itemId) => {
    try {
      await axios.delete(`${API}/portfolio/${itemId}`);
      fetchPortfolio();
    } catch (error) {
      console.error('Error deleting portfolio item:', error);
    }
  };

  const portfolioChartData = portfolio?.items?.map(item => ({
    symbol: item.symbol,
    value: item.current_value,
    profit_loss: item.profit_loss
  })) || [];

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-gray-800">Portfolio</h2>
        <button
          onClick={() => setShowAddForm(true)}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 flex items-center space-x-2"
        >
          <Plus size={20} />
          <span>Add Stock</span>
        </button>
      </div>

      {/* Portfolio Summary */}
      {portfolio && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-white p-4 rounded-lg shadow-md">
            <h3 className="text-sm font-medium text-gray-600">Total Value</h3>
            <p className="text-2xl font-bold text-gray-800">${portfolio.total_value?.toFixed(2)}</p>
          </div>
          <div className="bg-white p-4 rounded-lg shadow-md">
            <h3 className="text-sm font-medium text-gray-600">Total Cost</h3>
            <p className="text-2xl font-bold text-gray-800">${portfolio.total_cost?.toFixed(2)}</p>
          </div>
          <div className="bg-white p-4 rounded-lg shadow-md">
            <h3 className="text-sm font-medium text-gray-600">P&L</h3>
            <p className={`text-2xl font-bold ${portfolio.total_profit_loss >= 0 ? 'text-green-600' : 'text-red-600'}`}>
              ${portfolio.total_profit_loss?.toFixed(2)}
            </p>
          </div>
          <div className="bg-white p-4 rounded-lg shadow-md">
            <h3 className="text-sm font-medium text-gray-600">P&L %</h3>
            <p className={`text-2xl font-bold ${portfolio.total_profit_loss_percent >= 0 ? 'text-green-600' : 'text-red-600'}`}>
              {portfolio.total_profit_loss_percent?.toFixed(2)}%
            </p>
          </div>
        </div>
      )}

      {/* Portfolio Chart */}
      {portfolioChartData.length > 0 && (
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h3 className="text-lg font-semibold mb-4">Portfolio Allocation</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={portfolioChartData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ symbol, percent }) => `${symbol} (${(percent * 100).toFixed(1)}%)`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {portfolioChartData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={`hsl(${index * 45}, 70%, 60%)`} />
                ))}
              </Pie>
              <Tooltip formatter={(value) => [`$${value.toFixed(2)}`, 'Value']} />
            </PieChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Portfolio Items */}
      <div className="bg-white rounded-lg shadow-md overflow-hidden">
        <div className="px-6 py-4 bg-gray-50 border-b">
          <h3 className="text-lg font-semibold">Holdings</h3>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Symbol</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Shares</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Avg Cost</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Current Price</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Market Value</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">P&L</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {portfolio?.items?.map((item) => (
                <tr key={item.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 font-medium text-gray-900">{item.symbol}</td>
                  <td className="px-6 py-4 text-gray-600">{item.shares}</td>
                  <td className="px-6 py-4 text-gray-600">${item.purchase_price?.toFixed(2)}</td>
                  <td className="px-6 py-4 text-gray-600">${item.current_price?.toFixed(2)}</td>
                  <td className="px-6 py-4 text-gray-600">${item.current_value?.toFixed(2)}</td>
                  <td className={`px-6 py-4 font-medium ${item.profit_loss >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                    ${item.profit_loss?.toFixed(2)} ({item.profit_loss_percent?.toFixed(2)}%)
                  </td>
                  <td className="px-6 py-4">
                    <button
                      onClick={() => deleteItem(item.id)}
                      className="text-red-600 hover:text-red-900"
                    >
                      <Trash2 size={16} />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Add Stock Modal */}
      {showAddForm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <h3 className="text-lg font-semibold mb-4">Add Stock to Portfolio</h3>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">Symbol</label>
                <input
                  type="text"
                  value={formData.symbol}
                  onChange={(e) => setFormData({...formData, symbol: e.target.value.toUpperCase()})}
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                  placeholder="AAPL"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Shares</label>
                <input
                  type="number"
                  step="0.01"
                  value={formData.shares}
                  onChange={(e) => setFormData({...formData, shares: e.target.value})}
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Purchase Price</label>
                <input
                  type="number"
                  step="0.01"
                  value={formData.purchase_price}
                  onChange={(e) => setFormData({...formData, purchase_price: e.target.value})}
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Purchase Date</label>
                <input
                  type="date"
                  value={formData.purchase_date}
                  onChange={(e) => setFormData({...formData, purchase_date: e.target.value})}
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                  required
                />
              </div>
              <div className="flex space-x-4">
                <button
                  type="submit"
                  className="flex-1 bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700"
                >
                  Add Stock
                </button>
                <button
                  type="button"
                  onClick={() => setShowAddForm(false)}
                  className="flex-1 bg-gray-300 text-gray-700 py-2 px-4 rounded-md hover:bg-gray-400"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

// Stock Screener Component (Simple version)
const SimpleStockScreener = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [stockData, setStockData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [historicalData, setHistoricalData] = useState(null);

  const searchStock = async (symbol) => {
    if (!symbol) return;
    
    setLoading(true);
    try {
      const [stockRes, historyRes] = await Promise.all([
        axios.get(`${API}/stocks/${symbol}`),
        axios.get(`${API}/stocks/${symbol}/history?period=1mo`)
      ]);
      
      setStockData(stockRes.data);
      setHistoricalData(historyRes.data);
    } catch (error) {
      console.error('Error fetching stock data:', error);
      setStockData(null);
      setHistoricalData(null);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (e) => {
    e.preventDefault();
    if (searchTerm.trim()) {
      searchStock(searchTerm.trim().toUpperCase());
    }
  };

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-gray-800">Stock Search</h2>
      
      <form onSubmit={handleSearch} className="flex space-x-4">
        <input
          type="text"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          placeholder="Enter stock symbol (e.g., AAPL)"
          className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        <button
          type="submit"
          className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 flex items-center space-x-2"
        >
          <Search size={20} />
          <span>Search</span>
        </button>
      </form>

      {loading && (
        <div className="flex justify-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
        </div>
      )}

      {stockData && (
        <div className="space-y-6">
          {/* Stock Info Card */}
          <div className="bg-white p-6 rounded-lg shadow-md">
            <div className="flex justify-between items-start">
              <div>
                <h3 className="text-2xl font-bold">{stockData.symbol}</h3>
                <p className="text-3xl font-bold text-gray-800">${stockData.price?.toFixed(2)}</p>
                <div className={`flex items-center space-x-2 ${stockData.change >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                  {stockData.change >= 0 ? <TrendingUp size={20} /> : <TrendingDown size={20} />}
                  <span className="text-lg">{stockData.change?.toFixed(2)} ({stockData.change_percent?.toFixed(2)}%)</span>
                </div>
              </div>
              <div className="text-right space-y-2">
                <div>
                  <span className="text-sm text-gray-600">Volume: </span>
                  <span className="font-medium">{stockData.volume?.toLocaleString()}</span>
                </div>
                {stockData.market_cap && (
                  <div>
                    <span className="text-sm text-gray-600">Market Cap: </span>
                    <span className="font-medium">${(stockData.market_cap / 1e9).toFixed(2)}B</span>
                  </div>
                )}
                {stockData.pe_ratio && (
                  <div>
                    <span className="text-sm text-gray-600">P/E Ratio: </span>
                    <span className="font-medium">{stockData.pe_ratio?.toFixed(2)}</span>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Price Chart */}
          {historicalData && (
            <div className="bg-white p-6 rounded-lg shadow-md">
              <h3 className="text-lg font-semibold mb-4">Price Chart (1 Month)</h3>
              <ResponsiveContainer width="100%" height={400}>
                <LineChart data={historicalData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis />
                  <Tooltip 
                    formatter={(value, name) => [`$${value.toFixed(2)}`, name]}
                    labelFormatter={(date) => `Date: ${date}`}
                  />
                  <Legend />
                  <Line type="monotone" dataKey="close" stroke="#2563eb" strokeWidth={2} dot={false} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

// Technical Analysis Component
const TechnicalAnalysis = () => {
  const [symbol, setSymbol] = useState('AAPL');
  const [indicators, setIndicators] = useState(null);
  const [loading, setLoading] = useState(false);

  const fetchIndicators = async () => {
    if (!symbol) return;
    
    setLoading(true);
    try {
      const response = await axios.get(`${API}/stocks/${symbol}/indicators`);
      setIndicators(response.data);
    } catch (error) {
      console.error('Error fetching indicators:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchIndicators();
  }, []);

  const handleSubmit = (e) => {
    e.preventDefault();
    fetchIndicators();
  };

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-gray-800">Technical Analysis</h2>
      
      <form onSubmit={handleSubmit} className="flex space-x-4">
        <input
          type="text"
          value={symbol}
          onChange={(e) => setSymbol(e.target.value.toUpperCase())}
          placeholder="Enter stock symbol"
          className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        <button
          type="submit"
          className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700"
        >
          Analyze
        </button>
      </form>

      {loading && (
        <div className="flex justify-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
        </div>
      )}

      {indicators && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {/* RSI */}
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h3 className="text-lg font-semibold mb-4 flex items-center">
              <Activity className="mr-2" size={20} />
              RSI (14)
            </h3>
            <div className="text-center">
              <div className="text-3xl font-bold text-blue-600">
                {indicators.rsi?.value ? indicators.rsi.value.toFixed(2) : 'N/A'}
              </div>
              <div className="mt-2 text-sm text-gray-600">
                {indicators.rsi?.value > 70 ? 'Overbought' : 
                 indicators.rsi?.value < 30 ? 'Oversold' : 'Neutral'}
              </div>
            </div>
          </div>

          {/* MACD */}
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h3 className="text-lg font-semibold mb-4 flex items-center">
              <TrendingUp className="mr-2" size={20} />
              MACD
            </h3>
            <div className="space-y-2">
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">MACD:</span>
                <span className="font-medium">
                  {indicators.macd?.macd ? indicators.macd.macd.toFixed(4) : 'N/A'}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">Signal:</span>
                <span className="font-medium">
                  {indicators.macd?.signal ? indicators.macd.signal.toFixed(4) : 'N/A'}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">Histogram:</span>
                <span className="font-medium">
                  {indicators.macd?.histogram ? indicators.macd.histogram.toFixed(4) : 'N/A'}
                </span>
              </div>
            </div>
          </div>

          {/* Moving Averages */}
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h3 className="text-lg font-semibold mb-4 flex items-center">
              <BarChart3 className="mr-2" size={20} />
              Moving Averages
            </h3>
            <div className="space-y-2">
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">SMA 20:</span>
                <span className="font-medium">
                  {indicators.sma?.sma20 ? `$${indicators.sma.sma20.toFixed(2)}` : 'N/A'}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">SMA 50:</span>
                <span className="font-medium">
                  {indicators.sma?.sma50 ? `$${indicators.sma.sma50.toFixed(2)}` : 'N/A'}
                </span>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

// Watchlist Component
const Watchlist = () => {
  const [watchlist, setWatchlist] = useState([]);
  const [showAddForm, setShowAddForm] = useState(false);
  const [formData, setFormData] = useState({ symbol: '', target_price: '', notes: '' });

  useEffect(() => {
    fetchWatchlist();
  }, []);

  const fetchWatchlist = async () => {
    try {
      const response = await axios.get(`${API}/watchlist`);
      setWatchlist(response.data);
    } catch (error) {
      console.error('Error fetching watchlist:', error);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${API}/watchlist`, {
        ...formData,
        target_price: formData.target_price ? parseFloat(formData.target_price) : null
      });
      
      setFormData({ symbol: '', target_price: '', notes: '' });
      setShowAddForm(false);
      fetchWatchlist();
    } catch (error) {
      console.error('Error adding watchlist item:', error);
    }
  };

  const deleteItem = async (itemId) => {
    try {
      await axios.delete(`${API}/watchlist/${itemId}`);
      fetchWatchlist();
    } catch (error) {
      console.error('Error deleting watchlist item:', error);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-gray-800">Watchlist</h2>
        <button
          onClick={() => setShowAddForm(true)}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 flex items-center space-x-2"
        >
          <Plus size={20} />
          <span>Add Stock</span>
        </button>
      </div>

      <div className="bg-white rounded-lg shadow-md overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Symbol</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Target Price</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Notes</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Added</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {watchlist.map((item) => (
                <tr key={item.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 font-medium text-gray-900">{item.symbol}</td>
                  <td className="px-6 py-4 text-gray-600">
                    {item.target_price ? `$${item.target_price.toFixed(2)}` : 'N/A'}
                  </td>
                  <td className="px-6 py-4 text-gray-600">{item.notes || 'N/A'}</td>
                  <td className="px-6 py-4 text-gray-600">
                    {new Date(item.added_date).toLocaleDateString()}
                  </td>
                  <td className="px-6 py-4">
                    <button
                      onClick={() => deleteItem(item.id)}
                      className="text-red-600 hover:text-red-900"
                    >
                      <Trash2 size={16} />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Add Stock Modal */}
      {showAddForm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <h3 className="text-lg font-semibold mb-4">Add to Watchlist</h3>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">Symbol</label>
                <input
                  type="text"
                  value={formData.symbol}
                  onChange={(e) => setFormData({...formData, symbol: e.target.value.toUpperCase()})}
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                  placeholder="AAPL"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Target Price (optional)</label>
                <input
                  type="number"
                  step="0.01"
                  value={formData.target_price}
                  onChange={(e) => setFormData({...formData, target_price: e.target.value})}
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Notes (optional)</label>
                <textarea
                  value={formData.notes}
                  onChange={(e) => setFormData({...formData, notes: e.target.value})}
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                  rows={3}
                />
              </div>
              <div className="flex space-x-4">
                <button
                  type="submit"
                  className="flex-1 bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700"
                >
                  Add to Watchlist
                </button>
                <button
                  type="button"
                  onClick={() => setShowAddForm(false)}
                  className="flex-1 bg-gray-300 text-gray-700 py-2 px-4 rounded-md hover:bg-gray-400"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

// Market News Component  
const MarketNews = () => {
  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-gray-800">Market News</h2>
      <div className="bg-white p-6 rounded-lg shadow-md">
        <p className="text-gray-600">Market news integration coming soon...</p>
        <p className="text-sm text-gray-500 mt-2">
          This section will show latest financial news, earnings reports, and market updates.
        </p>
      </div>
    </div>
  );
};

// Main App Component
function App() {
  const [activeTab, setActiveTab] = useState('dashboard');

  const renderContent = () => {
    switch (activeTab) {
      case 'dashboard':
        return <Dashboard />;
      case 'portfolio':
        return <Portfolio />;
      case 'screener':
        return <AdvancedScreener />;
      case 'simple-screener':
        return <SimpleStockScreener />;
      case 'watchlist':
        return <Watchlist />;
      case 'technical':
        return <TechnicalAnalysis />;
      case 'news':
        return <MarketNews />;
      default:
        return <Dashboard />;
    }
  };

  return (
    <BrowserRouter>
      <div className="min-h-screen bg-gray-100 flex">
        <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} />
        <main className="flex-1 ml-64 p-6">
          <div className="max-w-7xl mx-auto">
            {renderContent()}
          </div>
        </main>
      </div>
    </BrowserRouter>
  );
}

export default App;