import React, { useState, useEffect, Suspense, useMemo, useCallback } from "react";
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
  Award,
  RefreshCw
} from "lucide-react";

// Lazy loading for heavy components
const AdvancedScreener = React.lazy(() => import("./components/AdvancedScreener"));
const InvestmentScoring = React.lazy(() => import("./components/InvestmentScoring"));

import "./App.css";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Loading fallback component with enhanced design
const LoadingFallback = ({ componentName }) => (
  <div className="flex flex-col justify-center items-center h-64 space-y-4">
    <div className="relative">
      <div className="w-16 h-16 border-4 border-blue-200 rounded-full animate-spin"></div>
      <div className="absolute top-0 left-0 w-16 h-16 border-4 border-blue-500 rounded-full border-t-transparent animate-spin"></div>
      <div className="absolute top-2 left-2 w-12 h-12 border-4 border-blue-300 rounded-full border-t-transparent animate-spin animation-delay-150"></div>
    </div>
    <div className="text-center">
      <span className="text-gray-700 font-medium text-lg">Loading {componentName}...</span>
      <p className="text-gray-500 text-sm mt-1">Preparing advanced features</p>
    </div>
    <div className="flex space-x-1">
      <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce"></div>
      <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce animation-delay-150"></div>
      <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce animation-delay-300"></div>
    </div>
  </div>
);

// Navigation Component
const Sidebar = ({ activeTab, setActiveTab }) => {
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [isMobile, setIsMobile] = useState(false);

  // Check if mobile on mount and resize
  useEffect(() => {
    const checkMobile = () => {
      const mobile = window.innerWidth < 768;
      setIsMobile(mobile);
      if (mobile) {
        setIsCollapsed(true);
      }
    };
    
    checkMobile();
    window.addEventListener('resize', checkMobile);
    return () => window.removeEventListener('resize', checkMobile);
  }, []);

  const menuGroups = [
    {
      title: "Overview",
      items: [
        { id: 'dashboard', label: 'Dashboard', icon: Home, color: 'from-blue-500 to-cyan-500', shortLabel: 'Dash' },
        { id: 'portfolio', label: 'Portfolio', icon: Briefcase, color: 'from-emerald-500 to-teal-500', shortLabel: 'Port' }
      ]
    },
    {
      title: "Analysis & Trading",
      items: [
        { id: 'investments', label: 'Investment Scoring', icon: Award, color: 'from-amber-500 to-orange-500', badge: '🎯', shortLabel: 'Score' },
        { id: 'screener', label: 'Advanced Screener', icon: Database, color: 'from-violet-500 to-purple-500', shortLabel: 'Screen' },
        { id: 'simple-screener', label: 'Stock Search', icon: Search, color: 'from-pink-500 to-rose-500', shortLabel: 'Search' },
        { id: 'technical', label: 'Technical Analysis', icon: BarChart3, color: 'from-indigo-500 to-purple-500', shortLabel: 'Tech' }
      ]
    },
    {
      title: "Tools & Alerts",
      items: [
        { id: 'watchlist', label: 'Watchlist', icon: Star, color: 'from-yellow-500 to-amber-500', shortLabel: 'Watch' },
        { id: 'news', label: 'Market News', icon: Newspaper, color: 'from-slate-500 to-gray-500', shortLabel: 'News' }
      ]
    }
  ];

  return (
    <>
      {/* Mobile Overlay */}
      {isMobile && !isCollapsed && (
        <div 
          className="fixed inset-0 bg-black bg-opacity-50 z-40 lg:hidden"
          onClick={() => setIsCollapsed(true)}
        />
      )}

      {/* Sidebar */}
      <div className={`${isCollapsed ? 'w-16' : 'w-64'} bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 text-white h-screen fixed left-0 top-0 overflow-y-auto shadow-xl border-r border-slate-700 z-50 transition-all duration-300 custom-scrollbar`}>
        <div className="p-4">
          {/* Toggle Button */}
          <button
            onClick={() => setIsCollapsed(!isCollapsed)}
            className="absolute top-4 -right-3 bg-slate-700 hover:bg-slate-600 rounded-full p-2 shadow-lg transition-colors duration-200 z-60"
          >
            <svg className={`w-4 h-4 transform transition-transform duration-200 ${isCollapsed ? 'rotate-180' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
          </button>

          {/* Logo/Header */}
          <div className="mb-8">
            <div className={`flex items-center ${isCollapsed ? 'justify-center' : 'justify-center'} mb-2`}>
              {isCollapsed ? (
                // Collapsed state - custom CSS icon
                <div className="flex items-center justify-center flex-shrink-0">
                  <div className="w-10 h-10 rounded-lg bg-gradient-to-r from-blue-500 to-cyan-500 flex items-center justify-center relative">
                    <div className="text-white font-bold text-lg">F</div>
                    <div className="absolute inset-0 flex items-center justify-center">
                      <div className="w-8 h-1 bg-green-400 rounded-full transform rotate-12 opacity-60"></div>
                      <div className="w-6 h-1 bg-green-300 rounded-full transform -rotate-12 opacity-50 ml-1"></div>
                    </div>
                  </div>
                </div>
              ) : (
                // Expanded state - CSS text logo (larger and clean)
                <div className="flex items-center justify-center w-full px-2">
                  <div className="text-center">
                    <div className="flex items-center justify-center space-x-1">
                      <div className="relative">
                        <span className="text-2xl font-bold bg-gradient-to-r from-blue-400 to-cyan-400 bg-clip-text text-transparent">
                          Flow
                        </span>
                        <div className="absolute top-1/2 left-0 right-0 h-0.5 bg-gradient-to-r from-green-400 to-emerald-400 opacity-70 rounded-full transform -translate-y-1/2"></div>
                      </div>
                      <span className="text-2xl font-bold bg-gradient-to-r from-slate-200 to-white bg-clip-text text-transparent">
                        Mind
                      </span>
                    </div>
                    <div className="text-xs text-blue-300 font-medium tracking-wider">ANALYTICS</div>
                  </div>
                </div>
              )}
            </div>
            {!isCollapsed && (
              <p className="text-xs text-slate-400 text-center mt-2">Where Data Flows, Intelligence Grows</p>
            )}
          </div>

          {/* Navigation Groups */}
          <nav className="space-y-6">
            {menuGroups.map((group, groupIndex) => (
              <div key={groupIndex}>
                {!isCollapsed && (
                  <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-3 px-3">
                    {group.title}
                  </h3>
                )}
                <div className="space-y-1">
                  {group.items.map((item) => {
                    const Icon = item.icon;
                    const isActive = activeTab === item.id;
                    return (
                      <div key={item.id} className="relative group">
                        <button
                          onClick={() => {
                            setActiveTab(item.id);
                            if (isMobile) setIsCollapsed(true);
                          }}
                          className={`w-full group flex items-center ${isCollapsed ? 'justify-center px-2' : 'space-x-3 px-3'} py-3 rounded-xl transition-all duration-200 relative ${
                            isActive
                              ? 'bg-gradient-to-r ' + item.color + ' text-white shadow-lg transform scale-105'
                              : 'text-slate-300 hover:text-white hover:bg-slate-700/50 hover:transform hover:scale-102'
                          }`}
                        >
                          {/* Active indicator */}
                          {isActive && !isCollapsed && (
                            <div className="absolute left-0 top-0 bottom-0 w-1 bg-white rounded-r-full opacity-80"></div>
                          )}
                          
                          {/* Icon with background */}
                          <div className={`flex items-center justify-center w-8 h-8 rounded-lg transition-all duration-200 ${
                            isActive 
                              ? 'bg-white/20' 
                              : 'bg-slate-600/30 group-hover:bg-slate-600/50'
                          }`}>
                            <Icon size={18} className={isActive ? 'text-white' : 'text-slate-300 group-hover:text-white'} />
                          </div>
                          
                          {/* Label */}
                          {!isCollapsed && (
                            <div className="flex-1 text-left">
                              <div className="flex items-center justify-between">
                                <span className="font-medium text-sm">{item.label}</span>
                                {item.badge && (
                                  <span className="text-xs opacity-70">{item.badge}</span>
                                )}
                              </div>
                            </div>
                          )}
                          
                          {/* Hover effect */}
                          {!isActive && !isCollapsed && (
                            <div className="w-0 h-0 opacity-0 group-hover:w-1 group-hover:h-8 group-hover:opacity-50 bg-gradient-to-r from-blue-400 to-cyan-400 rounded-full transition-all duration-300"></div>
                          )}
                        </button>

                        {/* Tooltip for collapsed state */}
                        {isCollapsed && (
                          <div className="absolute left-16 top-1/2 transform -translate-y-1/2 bg-slate-800 text-white px-2 py-1 rounded text-xs whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none z-50 shadow-lg">
                            {item.label}
                            <div className="absolute left-0 top-1/2 transform -translate-y-1/2 -translate-x-1 w-2 h-2 bg-slate-800 rotate-45"></div>
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              </div>
            ))}
          </nav>

          {/* Bottom section with version/status */}
          {!isCollapsed && (
            <div className="absolute bottom-4 left-4 right-4">
              <div className="bg-slate-800/50 rounded-xl p-3 border border-slate-600/30">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                    <span className="text-xs text-slate-400">Live Data</span>
                  </div>
                  <span className="text-xs text-slate-500">v2.1.0</span>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </>
  );
};

// Memoized Dashboard Component
const Dashboard = React.memo(() => {
  const [marketData, setMarketData] = useState(null);
  const [topMovers, setTopMovers] = useState(null);
  const [loading, setLoading] = useState(true);

  // Memoized fetch function
  const fetchMarketData = useCallback(async () => {
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
  }, []);

  useEffect(() => {
    fetchMarketData();
  }, [fetchMarketData]);

  // Memoized formatted number function
  const formatNumber = useCallback((num) => {
    if (num >= 1e9) return (num / 1e9).toFixed(2) + 'B';
    if (num >= 1e6) return (num / 1e6).toFixed(2) + 'M';
    if (num >= 1e3) return (num / 1e3).toFixed(2) + 'K';
    return num?.toFixed(2) || '0.00';
  }, []);

  // Memoized market indices data
  const memoizedIndices = useMemo(() => {
    return marketData?.indices?.map((index, idx) => ({
      ...index,
      id: `index-${idx}`,
      formattedPrice: formatNumber(index.price)
    })) || [];
  }, [marketData?.indices, formatNumber]);

  // Memoized top movers data
  const memoizedTopMovers = useMemo(() => ({
    gainers: topMovers?.gainers?.slice(0, 5).map((stock, idx) => ({
      ...stock,
      id: `gainer-${idx}`,
      rank: idx + 1
    })) || [],
    losers: topMovers?.losers?.slice(0, 5).map((stock, idx) => ({
      ...stock,
      id: `loser-${idx}`,
      rank: idx + 1
    })) || []
  }), [topMovers]);

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="flex flex-col items-center space-y-4">
          <div className="relative">
            {/* Animated loading spinner with multiple rings */}
            <div className="w-16 h-16 border-4 border-blue-200 rounded-full animate-spin"></div>
            <div className="absolute top-0 left-0 w-16 h-16 border-4 border-blue-500 rounded-full border-t-transparent animate-spin"></div>
            <div className="absolute top-2 left-2 w-12 h-12 border-4 border-blue-300 rounded-full border-t-transparent animate-spin animation-delay-150"></div>
          </div>
          <div className="text-center">
            <span className="text-gray-700 font-medium text-lg">Loading market data...</span>
            <p className="text-gray-500 text-sm mt-1">Getting real-time stock prices and market indices</p>
          </div>
          {/* Progress dots */}
          <div className="flex space-x-1">
            <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce"></div>
            <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce animation-delay-150"></div>
            <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce animation-delay-300"></div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Page Header */}
      <div className="bg-gradient-to-r from-blue-600 via-blue-700 to-indigo-700 rounded-2xl p-4 md:p-6 text-white shadow-xl">
        <div className="flex flex-col md:flex-row md:items-center justify-between">
          <div className="mb-4 md:mb-0">
            <h2 className="text-2xl md:text-3xl font-bold mb-2">Market Dashboard</h2>
            <p className="text-blue-100 text-sm md:text-lg">Real-time market overview and top movers</p>
          </div>
          <div className="text-left md:text-right">
            <div className="text-sm text-blue-200 mb-1">Last Updated</div>
            <div className="text-blue-100 font-medium mb-2">{new Date().toLocaleTimeString()}</div>
            <button
              onClick={fetchMarketData}
              className="bg-white/20 hover:bg-white/30 px-3 md:px-4 py-2 rounded-lg transition-colors duration-200 flex items-center space-x-2"
            >
              <RefreshCw size={16} />
              <span>Refresh</span>
            </button>
          </div>
        </div>
      </div>
      
      {/* Market Indices */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 md:gap-6">
        {memoizedIndices.map((index) => (
          <MemoizedIndexCard key={index.id} index={index} />
        ))}
      </div>

      {/* Top Movers */}
      <div className="grid grid-cols-1 xl:grid-cols-2 gap-6 md:gap-8">
        <MemoizedTopMoversCard
          title="Top Gainers"
          stocks={memoizedTopMovers.gainers}
          type="gainers"
        />
        <MemoizedTopMoversCard
          title="Top Losers"
          stocks={memoizedTopMovers.losers}
          type="losers"
        />
      </div>
    </div>
  );
});

// Memoized Index Card Component
const MemoizedIndexCard = React.memo(({ index }) => (
  <div className="group relative">
    {/* Background gradient based on performance */}
    <div className={`absolute inset-0 rounded-xl opacity-10 ${
      index.change >= 0 
        ? 'bg-gradient-to-br from-emerald-400 to-green-500' 
        : 'bg-gradient-to-br from-red-400 to-red-500'
    }`}></div>
    
    <div className="relative bg-white/80 backdrop-blur-sm p-4 md:p-6 rounded-xl shadow-lg card-hover border border-gray-100">
      <div className="flex justify-between items-start mb-4">
        <div>
          <div className="flex items-center space-x-2 mb-2">
            <span className="text-xs md:text-sm font-bold text-gray-500 bg-gray-100 px-2 py-1 rounded-full">
              {index.symbol}
            </span>
          </div>
          <p className="text-xl md:text-2xl font-bold text-gray-800">${index.price?.toFixed(2)}</p>
        </div>
        <div className={`p-2 md:p-3 rounded-xl ${
          index.change >= 0 
            ? 'bg-gradient-to-r from-emerald-500 to-green-500' 
            : 'bg-gradient-to-r from-red-500 to-red-600'
        } text-white`}>
          {index.change >= 0 ? <TrendingUp size={20} /> : <TrendingDown size={20} />}
        </div>
      </div>
      
      <div className={`flex items-center space-x-2 text-base md:text-lg font-semibold ${
        index.change >= 0 ? 'text-emerald-600' : 'text-red-600'
      }`}>
        <span>{index.change >= 0 ? '+' : ''}{index.change?.toFixed(2)}</span>
        <span>({index.change_percent?.toFixed(2)}%)</span>
      </div>
      
      {/* Progress bar for visual change representation */}
      <div className="mt-3">
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div 
            className={`h-2 rounded-full transition-all duration-500 ${
              index.change >= 0 
                ? 'bg-gradient-to-r from-emerald-400 to-green-500' 
                : 'bg-gradient-to-r from-red-400 to-red-500'
            }`}
            style={{ width: `${Math.min(100, Math.abs(index.change_percent) * 10)}%` }}
          ></div>
        </div>
      </div>
    </div>
  </div>
));

// Memoized Top Movers Card Component
const MemoizedTopMoversCard = React.memo(({ title, stocks, type }) => (
  <div className="bg-white/80 backdrop-blur-sm p-4 md:p-6 rounded-2xl shadow-lg border border-gray-100 card-hover">
    <div className="flex items-center space-x-3 mb-4 md:mb-6">
      <div className={`p-2 md:p-3 rounded-xl text-white animate-pulse-soft ${
        type === 'gainers' 
          ? 'bg-gradient-to-r from-emerald-500 to-green-500'
          : 'bg-gradient-to-r from-red-500 to-red-600'
      }`}>
        {type === 'gainers' ? <TrendingUp size={20} /> : <TrendingDown size={20} />}
      </div>
      <div>
        <h3 className="text-lg md:text-xl font-bold text-gray-800">{title}</h3>
        <p className="text-gray-600 text-sm">
          {type === 'gainers' ? 'Best performing stocks today' : 'Worst performing stocks today'}
        </p>
      </div>
    </div>
    
    <div className="space-y-3">
      {stocks.map((stock) => (
        <MemoizedStockRow key={stock.id} stock={stock} type={type} />
      ))}
    </div>
  </div>
));

// Memoized Stock Row Component
const MemoizedStockRow = React.memo(({ stock, type }) => (
  <div className={`group p-3 md:p-4 rounded-xl transition-all duration-200 border border-transparent hover:border-${type === 'gainers' ? 'emerald' : 'red'}-200 hover:bg-gradient-to-r ${
    type === 'gainers' 
      ? 'hover:from-emerald-50 hover:to-green-50'
      : 'hover:from-red-50 hover:to-red-50'
  }`}>
    <div className="flex justify-between items-center">
      <div className="flex items-center space-x-3">
        <div className={`w-8 h-8 md:w-10 md:h-10 rounded-full flex items-center justify-center ${
          type === 'gainers'
            ? 'bg-gradient-to-r from-emerald-100 to-green-100'
            : 'bg-gradient-to-r from-red-100 to-red-100'
        }`}>
          <span className={`font-bold text-sm md:text-base ${
            type === 'gainers' ? 'text-emerald-600' : 'text-red-600'
          }`}>
            {stock.rank}
          </span>
        </div>
        <div>
          <span className="font-bold text-gray-800 text-sm md:text-base">{stock.symbol}</span>
          <p className="text-xs md:text-sm text-gray-600">${stock.price?.toFixed(2)}</p>
        </div>
      </div>
      <div className="text-right">
        <div className={`flex items-center space-x-1 font-bold text-sm md:text-base ${
          type === 'gainers' ? 'text-emerald-600' : 'text-red-600'
        }`}>
          {type === 'gainers' ? <TrendingUp size={14} /> : <TrendingDown size={14} />}
          <span>{type === 'gainers' ? '+' : ''}{stock.change_percent?.toFixed(2)}%</span>
        </div>
        <p className="text-xs md:text-sm text-gray-600">
          {type === 'gainers' ? '+' : ''}${stock.change?.toFixed(2)}
        </p>
      </div>
    </div>
  </div>
));

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
    <div className="space-y-6 md:space-y-8">
      {/* Page Header */}
      <div className="bg-gradient-to-r from-emerald-600 via-green-700 to-teal-700 rounded-2xl p-4 md:p-6 text-white shadow-xl">
        <div className="flex flex-col md:flex-row md:items-center justify-between">
          <div className="mb-4 md:mb-0">
            <h2 className="text-2xl md:text-3xl font-bold mb-2">Portfolio Management</h2>
            <p className="text-emerald-100 text-sm md:text-lg">Track your investments and performance</p>
          </div>
          <button
            onClick={() => setShowAddForm(true)}
            className="bg-white/20 hover:bg-white/30 px-4 py-2 rounded-lg transition-colors duration-200 flex items-center space-x-2"
          >
            <Plus size={20} />
            <span>Add Stock</span>
          </button>
        </div>
      </div>

      {/* Portfolio Summary */}
      {portfolio && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 md:gap-6">
          <div className="bg-white/80 backdrop-blur-sm p-4 md:p-6 rounded-xl shadow-lg border border-gray-100 card-hover">
            <div className="flex items-center space-x-3 mb-2">
              <div className="p-2 bg-gradient-to-r from-blue-500 to-cyan-500 rounded-lg text-white">
                <DollarSign size={20} />
              </div>
              <h3 className="text-sm font-medium text-gray-600">Total Value</h3>
            </div>
            <p className="text-2xl md:text-3xl font-bold text-gray-800">${portfolio.total_value?.toFixed(2)}</p>
          </div>
          
          <div className="bg-white/80 backdrop-blur-sm p-4 md:p-6 rounded-xl shadow-lg border border-gray-100 card-hover">
            <div className="flex items-center space-x-3 mb-2">
              <div className="p-2 bg-gradient-to-r from-purple-500 to-indigo-500 rounded-lg text-white">
                <Briefcase size={20} />
              </div>
              <h3 className="text-sm font-medium text-gray-600">Total Cost</h3>
            </div>
            <p className="text-2xl md:text-3xl font-bold text-gray-800">${portfolio.total_cost?.toFixed(2)}</p>
          </div>
          
          <div className="bg-white/80 backdrop-blur-sm p-4 md:p-6 rounded-xl shadow-lg border border-gray-100 card-hover">
            <div className="flex items-center space-x-3 mb-2">
              <div className={`p-2 rounded-lg text-white ${
                portfolio.total_profit_loss >= 0 
                  ? 'bg-gradient-to-r from-emerald-500 to-green-500' 
                  : 'bg-gradient-to-r from-red-500 to-red-600'
              }`}>
                {portfolio.total_profit_loss >= 0 ? <TrendingUp size={20} /> : <TrendingDown size={20} />}
              </div>
              <h3 className="text-sm font-medium text-gray-600">P&L</h3>
            </div>
            <p className={`text-2xl md:text-3xl font-bold ${portfolio.total_profit_loss >= 0 ? 'text-emerald-600' : 'text-red-600'}`}>
              ${portfolio.total_profit_loss?.toFixed(2)}
            </p>
          </div>
          
          <div className="bg-white/80 backdrop-blur-sm p-4 md:p-6 rounded-xl shadow-lg border border-gray-100 card-hover">
            <div className="flex items-center space-x-3 mb-2">
              <div className={`p-2 rounded-lg text-white ${
                portfolio.total_profit_loss_percent >= 0 
                  ? 'bg-gradient-to-r from-emerald-500 to-green-500' 
                  : 'bg-gradient-to-r from-red-500 to-red-600'
              }`}>
                <Activity size={20} />
              </div>
              <h3 className="text-sm font-medium text-gray-600">P&L %</h3>
            </div>
            <p className={`text-2xl md:text-3xl font-bold ${portfolio.total_profit_loss_percent >= 0 ? 'text-emerald-600' : 'text-red-600'}`}>
              {portfolio.total_profit_loss_percent?.toFixed(2)}%
            </p>
          </div>
        </div>
      )}

      {/* Portfolio Chart */}
      {portfolioChartData.length > 0 && (
        <div className="bg-white/80 backdrop-blur-sm p-4 md:p-6 rounded-2xl shadow-lg border border-gray-100 card-hover">
          <h3 className="text-lg md:text-xl font-bold text-gray-800 mb-4 flex items-center">
            <PieChartIcon className="mr-3 text-blue-600" size={24} />
            Portfolio Allocation
          </h3>
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
      <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-lg border border-gray-100 overflow-hidden card-hover">
        <div className="px-4 md:px-6 py-4 bg-gradient-to-r from-blue-50 to-cyan-50 border-b border-gray-200">
          <h3 className="text-lg md:text-xl font-bold text-gray-800 flex items-center">
            <Briefcase className="mr-3 text-blue-600" size={24} />
            Holdings
          </h3>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 md:px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Symbol</th>
                <th className="px-4 md:px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Shares</th>
                <th className="px-4 md:px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Avg Cost</th>
                <th className="px-4 md:px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Current Price</th>
                <th className="px-4 md:px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Market Value</th>
                <th className="px-4 md:px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">P&L</th>
                <th className="px-4 md:px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {portfolio?.items?.map((item) => (
                <tr key={item.id} className="hover:bg-blue-50 transition-colors duration-200">
                  <td className="px-4 md:px-6 py-4 font-bold text-blue-600 font-mono">{item.symbol}</td>
                  <td className="px-4 md:px-6 py-4 text-gray-600">{item.shares}</td>
                  <td className="px-4 md:px-6 py-4 text-gray-600">${item.purchase_price?.toFixed(2)}</td>
                  <td className="px-4 md:px-6 py-4 text-gray-900 font-medium">${item.current_price?.toFixed(2)}</td>
                  <td className="px-4 md:px-6 py-4 text-gray-900 font-medium">${item.current_value?.toFixed(2)}</td>
                  <td className={`px-4 md:px-6 py-4 font-bold ${item.profit_loss >= 0 ? 'text-emerald-600' : 'text-red-600'}`}>
                    <div className="flex items-center space-x-1">
                      {item.profit_loss >= 0 ? <TrendingUp size={16} /> : <TrendingDown size={16} />}
                      <span>${item.profit_loss?.toFixed(2)} ({item.profit_loss_percent?.toFixed(2)}%)</span>
                    </div>
                  </td>
                  <td className="px-4 md:px-6 py-4">
                    <button
                      onClick={() => deleteItem(item.id)}
                      className="text-red-600 hover:text-red-800 hover:bg-red-50 p-2 rounded-lg transition-colors duration-200"
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
        <div className="fixed inset-0 bg-black bg-opacity-50 backdrop-blur-sm flex items-center justify-center p-4 z-50 transition-all duration-300">
          <div className="bg-white rounded-2xl p-6 w-full max-w-md transform transition-all duration-300 scale-100 shadow-2xl border border-gray-200">
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center space-x-3">
                <div className="p-2 bg-gradient-to-r from-blue-500 to-cyan-500 rounded-lg text-white">
                  <Plus size={20} />
                </div>
                <h3 className="text-xl font-bold text-gray-800">Add Stock to Portfolio</h3>
              </div>
              <button
                onClick={() => setShowAddForm(false)}
                className="text-gray-400 hover:text-gray-600 hover:bg-gray-100 p-2 rounded-lg transition-colors duration-200"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            
            <form onSubmit={handleSubmit} className="space-y-5">
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">Stock Symbol</label>
                <input
                  type="text"
                  value={formData.symbol}
                  onChange={(e) => setFormData({...formData, symbol: e.target.value.toUpperCase()})}
                  className="w-full px-4 py-3 rounded-xl border border-gray-300 focus:border-blue-500 focus:ring-2 focus:ring-blue-200 transition-all duration-200"
                  placeholder="e.g., AAPL, MSFT, GOOGL"
                  required
                />
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">Shares</label>
                  <input
                    type="number"
                    step="0.01"
                    value={formData.shares}
                    onChange={(e) => setFormData({...formData, shares: e.target.value})}
                    className="w-full px-4 py-3 rounded-xl border border-gray-300 focus:border-blue-500 focus:ring-2 focus:ring-blue-200 transition-all duration-200"
                    placeholder="100"
                    required
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">Purchase Price</label>
                  <input
                    type="number"
                    step="0.01"
                    value={formData.purchase_price}
                    onChange={(e) => setFormData({...formData, purchase_price: e.target.value})}
                    className="w-full px-4 py-3 rounded-xl border border-gray-300 focus:border-blue-500 focus:ring-2 focus:ring-blue-200 transition-all duration-200"
                    placeholder="150.00"
                    required
                  />
                </div>
              </div>
              
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">Purchase Date</label>
                <input
                  type="date"
                  value={formData.purchase_date}
                  onChange={(e) => setFormData({...formData, purchase_date: e.target.value})}
                  className="w-full px-4 py-3 rounded-xl border border-gray-300 focus:border-blue-500 focus:ring-2 focus:ring-blue-200 transition-all duration-200"
                  required
                />
              </div>
              
              <div className="flex space-x-3 pt-4">
                <button
                  type="submit"
                  className="flex-1 bg-gradient-to-r from-blue-600 to-cyan-600 text-white py-3 px-6 rounded-xl hover:from-blue-700 hover:to-cyan-700 transition-all duration-200 font-semibold flex items-center justify-center space-x-2"
                >
                  <Plus size={18} />
                  <span>Add Stock</span>
                </button>
                <button
                  type="button"
                  onClick={() => setShowAddForm(false)}
                  className="flex-1 bg-gray-200 text-gray-700 py-3 px-6 rounded-xl hover:bg-gray-300 transition-all duration-200 font-semibold"
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
      // Use enhanced endpoint for better data
      const [stockRes, historyRes] = await Promise.all([
        axios.get(`${API}/stocks/${symbol}/enhanced`),
        axios.get(`${API}/stocks/${symbol}/history?period=1mo`)
      ]);
      
      console.log('Stock search response:', stockRes.data);
      setStockData(stockRes.data);
      setHistoricalData(historyRes.data);
    } catch (error) {
      console.error('Error fetching stock data:', error);
      // Fallback to basic endpoint if enhanced fails
      try {
        const stockRes = await axios.get(`${API}/stocks/${symbol}`);
        console.log('Fallback stock response:', stockRes.data);
        setStockData(stockRes.data);
      } catch (fallbackError) {
        console.error('Fallback also failed:', fallbackError);
        setStockData(null);
      }
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

// Enhanced Technical Analysis Component with Smart Money Concepts
const TechnicalAnalysis = () => {
  const [symbol, setSymbol] = useState('AAPL');
  const [smartMoneyData, setSmartMoneyData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('overview');

  const fetchSmartMoneyAnalysis = async () => {
    if (!symbol) return;
    
    setLoading(true);
    try {
      const response = await axios.get(`${API}/investments/smart-money/${symbol}?timeframe=3mo`);
      console.log('Smart Money Analysis Response:', response.data);
      setSmartMoneyData(response.data);
    } catch (error) {
      console.error('Error fetching smart money analysis:', error);
      setSmartMoneyData(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSmartMoneyAnalysis();
  }, []);

  const handleSubmit = (e) => {
    e.preventDefault();
    fetchSmartMoneyAnalysis();
  };

  const getVerdictColor = (verdict) => {
    switch (verdict) {
      case 'BULLISH': return 'text-green-700 bg-green-100';
      case 'BEARISH': return 'text-red-700 bg-red-100';
      case 'NEUTRAL': return 'text-gray-700 bg-gray-100';
      default: return 'text-gray-700 bg-gray-100';
    }
  };

  const getSignalColor = (signal) => {
    switch (signal) {
      case 'bullish': return 'text-green-600 bg-green-50';
      case 'bearish': return 'text-red-600 bg-red-50';
      case 'buy': return 'text-green-700 bg-green-100';
      case 'sell': return 'text-red-700 bg-red-100';
      default: return 'text-gray-600 bg-gray-50';
    }
  };

  const OrderBlockCard = ({ orderBlock }) => (
    <div className={`p-3 rounded-lg border-l-4 ${
      orderBlock.type === 'bullish' 
        ? 'border-green-500 bg-green-50' 
        : 'border-red-500 bg-red-50'
    }`}>
      <div className="flex justify-between items-center mb-2">
        <span className={`font-semibold ${
          orderBlock.type === 'bullish' ? 'text-green-700' : 'text-red-700'
        }`}>
          {orderBlock.type.toUpperCase()} Order Block
        </span>
        <span className={`text-xs px-2 py-1 rounded ${
          orderBlock.strength === 'strong' 
            ? 'bg-purple-100 text-purple-700'
            : orderBlock.strength === 'medium'
            ? 'bg-blue-100 text-blue-700'
            : 'bg-gray-100 text-gray-700'
        }`}>
          {orderBlock.strength}
        </span>
      </div>
      <div className="text-sm space-y-1">
        <div>High: <span className="font-medium">${orderBlock.high?.toFixed(2)}</span></div>
        <div>Low: <span className="font-medium">${orderBlock.low?.toFixed(2)}</span></div>
        <div>Status: <span className={`font-medium ${orderBlock.tested ? 'text-red-600' : 'text-green-600'}`}>
          {orderBlock.tested ? 'Tested' : 'Untested'}
        </span></div>
      </div>
    </div>
  );

  const FairValueGapCard = ({ fvg }) => (
    <div className={`p-3 rounded-lg border-l-4 ${
      fvg.type === 'bullish' 
        ? 'border-blue-500 bg-blue-50' 
        : 'border-orange-500 bg-orange-50'
    }`}>
      <div className="flex justify-between items-center mb-2">
        <span className={`font-semibold ${
          fvg.type === 'bullish' ? 'text-blue-700' : 'text-orange-700'
        }`}>
          {fvg.type.toUpperCase()} FVG
        </span>
        <span className={`text-xs px-2 py-1 rounded ${
          fvg.filled ? 'bg-gray-100 text-gray-700' : 'bg-yellow-100 text-yellow-700'
        }`}>
          {fvg.filled ? 'Filled' : 'Open'}
        </span>
      </div>
      <div className="text-sm space-y-1">
        <div>Gap High: <span className="font-medium">${fvg.gap_high?.toFixed(2)}</span></div>
        <div>Gap Low: <span className="font-medium">${fvg.gap_low?.toFixed(2)}</span></div>
        <div>Size: <span className="font-medium">${fvg.gap_size?.toFixed(2)}</span></div>
        {!fvg.filled && fvg.fill_percentage > 0 && (
          <div>Filled: <span className="font-medium">{fvg.fill_percentage?.toFixed(1)}%</span></div>
        )}
      </div>
    </div>
  );

  const LiquiditySweepCard = ({ sweep }) => (
    <div className={`p-3 rounded-lg border-l-4 ${
      sweep.type === 'high_sweep' 
        ? 'border-purple-500 bg-purple-50' 
        : 'border-indigo-500 bg-indigo-50'
    }`}>
      <div className="flex justify-between items-center mb-2">
        <span className={`font-semibold ${
          sweep.type === 'high_sweep' ? 'text-purple-700' : 'text-indigo-700'
        }`}>
          {sweep.type === 'high_sweep' ? 'High Sweep' : 'Low Sweep'}
        </span>
        <span className={`text-xs px-2 py-1 rounded ${
          sweep.significance === 'major' 
            ? 'bg-red-100 text-red-700'
            : 'bg-yellow-100 text-yellow-700'
        }`}>
          {sweep.significance}
        </span>
      </div>
      <div className="text-sm space-y-1">
        <div>Price: <span className="font-medium">${sweep.price?.toFixed(2)}</span></div>
        <div>Volume: <span className="font-medium">{sweep.volume?.toLocaleString()}</span></div>
        <div>Time: <span className="font-medium">{new Date(sweep.time).toLocaleDateString()}</span></div>
      </div>
    </div>
  );

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-gray-800">🎯 Smart Money & Price Action Analysis</h2>
          <p className="text-gray-600">Advanced institutional trading concepts and price action patterns</p>
        </div>
      </div>
      
      <form onSubmit={handleSubmit} className="flex space-x-4">
        <input
          type="text"
          value={symbol}
          onChange={(e) => setSymbol(e.target.value.toUpperCase())}
          placeholder="Enter stock symbol (e.g., AAPL)"
          className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        <button
          type="submit"
          className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 flex items-center space-x-2"
        >
          <Activity size={20} />
          <span>Analyze Smart Money</span>
        </button>
      </form>

      {loading && (
        <div className="flex justify-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
        </div>
      )}

      {smartMoneyData && (
        <div className="space-y-6">
          {/* Smart Money Verdict */}
          <div className="bg-gradient-to-r from-blue-50 to-indigo-50 p-6 rounded-lg border border-blue-200">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-xl font-bold text-gray-800">{smartMoneyData.symbol} Smart Money Analysis</h3>
                <p className="text-gray-600 mt-1">{smartMoneyData.smart_money_verdict?.key_insight}</p>
              </div>
              <div className="text-right">
                <div className={`text-2xl font-bold px-4 py-2 rounded-lg ${getVerdictColor(smartMoneyData.smart_money_verdict?.verdict)}`}>
                  {smartMoneyData.smart_money_verdict?.verdict}
                </div>
                <div className="text-sm text-gray-500 mt-1">
                  {smartMoneyData.smart_money_verdict?.confidence}% Confidence
                </div>
              </div>
            </div>
          </div>

          {/* Tab Navigation */}
          <div className="bg-white p-1 rounded-lg shadow-sm">
            <div className="flex space-x-1">
              {[
                { id: 'overview', label: 'Overview', icon: Target },
                { id: 'order-blocks', label: 'Order Blocks', icon: Award },
                { id: 'fvg', label: 'Fair Value Gaps', icon: BarChart3 },
                { id: 'liquidity', label: 'Liquidity Sweeps', icon: TrendingUp },
                { id: 'structure', label: 'Market Structure', icon: Activity },
                { id: 'price-action', label: 'Price Action', icon: PieChartIcon }
              ].map((tab) => {
                const Icon = tab.icon;
                return (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`flex items-center space-x-2 px-3 py-2 rounded-md transition-colors text-sm ${
                      activeTab === tab.id
                        ? 'bg-blue-600 text-white'
                        : 'text-gray-600 hover:bg-gray-100'
                    }`}
                  >
                    <Icon size={16} />
                    <span>{tab.label}</span>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Overview Tab */}
          {activeTab === 'overview' && (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {/* Premium/Discount Zone */}
              <div className="bg-white p-6 rounded-lg shadow-md">
                <h3 className="text-lg font-semibold mb-4 flex items-center">
                  <Target className="mr-2" size={20} />
                  Premium/Discount
                </h3>
                <div className="text-center">
                  <div className={`text-2xl font-bold mb-2 ${
                    smartMoneyData.premium_discount?.current_zone === 'premium' 
                      ? 'text-red-600' 
                      : smartMoneyData.premium_discount?.current_zone === 'discount'
                      ? 'text-green-600'
                      : 'text-blue-600'
                  }`}>
                    {smartMoneyData.premium_discount?.current_zone?.toUpperCase()}
                  </div>
                  <div className="text-sm text-gray-600">
                    {smartMoneyData.premium_discount?.premium_percentage?.toFixed(1)}% of Range
                  </div>
                  <div className="mt-3 space-y-1 text-xs">
                    <div>High: ${smartMoneyData.premium_discount?.range_high?.toFixed(2)}</div>
                    <div>Low: ${smartMoneyData.premium_discount?.range_low?.toFixed(2)}</div>
                    <div>Equilibrium: ${smartMoneyData.premium_discount?.equilibrium?.toFixed(2)}</div>
                  </div>
                </div>
              </div>

              {/* Market Structure */}
              <div className="bg-white p-6 rounded-lg shadow-md">
                <h3 className="text-lg font-semibold mb-4 flex items-center">
                  <Activity className="mr-2" size={20} />
                  Market Structure
                </h3>
                <div className="text-center">
                  <div className={`text-2xl font-bold mb-2 ${
                    smartMoneyData.market_structure?.current_trend === 'bullish' 
                      ? 'text-green-600' 
                      : smartMoneyData.market_structure?.current_trend === 'bearish'
                      ? 'text-red-600'
                      : 'text-gray-600'
                  }`}>
                    {smartMoneyData.market_structure?.current_trend?.toUpperCase()}
                  </div>
                  <div className="text-sm text-gray-600">
                    {smartMoneyData.market_structure?.structure_points?.length || 0} Structure Points
                  </div>
                  <div className="mt-3 text-xs">
                    BOS Events: {smartMoneyData.market_structure?.break_of_structure?.length || 0}
                  </div>
                </div>
              </div>

              {/* Trading Signals */}
              <div className="bg-white p-6 rounded-lg shadow-md">
                <h3 className="text-lg font-semibold mb-4 flex items-center">
                  <TrendingUp className="mr-2" size={20} />
                  Active Signals
                </h3>
                <div className="space-y-2">
                  {smartMoneyData.trading_signals?.slice(0, 3).map((signal, index) => (
                    <div key={index} className={`px-3 py-2 rounded text-sm ${getSignalColor(signal.type)}`}>
                      <div className="font-medium">{signal.type.toUpperCase()}</div>
                      <div className="text-xs mt-1">{signal.reason}</div>
                      <div className="text-xs mt-1">
                        Entry: ${signal.entry?.toFixed(2)} | Target: ${signal.target?.toFixed(2)}
                      </div>
                    </div>
                  )) || <div className="text-gray-500 text-sm">No active signals</div>}
                </div>
              </div>
            </div>
          )}

          {/* Order Blocks Tab */}
          {activeTab === 'order-blocks' && (
            <div className="space-y-4">
              <div className="bg-blue-50 p-4 rounded-lg">
                <h3 className="text-lg font-semibold text-blue-800 mb-2">Order Blocks Analysis</h3>
                <p className="text-blue-600 text-sm">
                  Order blocks represent areas where institutions placed significant orders. Untested blocks often act as strong support/resistance.
                </p>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {smartMoneyData.order_blocks?.length > 0 ? (
                  smartMoneyData.order_blocks.map((ob, index) => (
                    <OrderBlockCard key={index} orderBlock={ob} />
                  ))
                ) : (
                  <div className="col-span-full text-center text-gray-500">
                    No order blocks detected in current timeframe
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Fair Value Gaps Tab */}
          {activeTab === 'fvg' && (
            <div className="space-y-4">
              <div className="bg-blue-50 p-4 rounded-lg">
                <h3 className="text-lg font-semibold text-blue-800 mb-2">Fair Value Gaps (FVG)</h3>
                <p className="text-blue-600 text-sm">
                  Fair Value Gaps are price imbalances that often get filled. They represent areas where price moved too quickly.
                </p>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {smartMoneyData.fair_value_gaps?.length > 0 ? (
                  smartMoneyData.fair_value_gaps.map((fvg, index) => (
                    <FairValueGapCard key={index} fvg={fvg} />
                  ))
                ) : (
                  <div className="col-span-full text-center text-gray-500">
                    No unfilled fair value gaps detected
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Liquidity Sweeps Tab */}
          {activeTab === 'liquidity' && (
            <div className="space-y-4">
              <div className="bg-purple-50 p-4 rounded-lg">
                <h3 className="text-lg font-semibold text-purple-800 mb-2">Liquidity Sweeps</h3>
                <p className="text-purple-600 text-sm">
                  Liquidity sweeps occur when price briefly moves beyond key levels to grab retail liquidity before reversing.
                </p>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {smartMoneyData.liquidity_sweeps?.length > 0 ? (
                  smartMoneyData.liquidity_sweeps.map((sweep, index) => (
                    <LiquiditySweepCard key={index} sweep={sweep} />
                  ))
                ) : (
                  <div className="col-span-full text-center text-gray-500">
                    No recent liquidity sweeps detected
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Market Structure Tab */}
          {activeTab === 'structure' && (
            <div className="space-y-4">
              <div className="bg-green-50 p-4 rounded-lg">
                <h3 className="text-lg font-semibold text-green-800 mb-2">Market Structure Analysis</h3>
                <p className="text-green-600 text-sm">
                  Market structure shows the pattern of higher highs/lows (bullish) or lower highs/lows (bearish).
                </p>
              </div>
              
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Structure Summary */}
                <div className="bg-white p-6 rounded-lg shadow-md">
                  <h4 className="font-semibold mb-4">Current Structure</h4>
                  <div className="space-y-3">
                    <div className={`p-3 rounded text-center ${
                      smartMoneyData.market_structure?.current_trend === 'bullish' 
                        ? 'bg-green-100 text-green-700'
                        : smartMoneyData.market_structure?.current_trend === 'bearish'
                        ? 'bg-red-100 text-red-700'
                        : 'bg-gray-100 text-gray-700'
                    }`}>
                      <div className="font-bold text-lg">
                        {smartMoneyData.market_structure?.current_trend?.toUpperCase()}
                      </div>
                      <div className="text-sm">Market Trend</div>
                    </div>
                    
                    <div className="grid grid-cols-2 gap-3 text-sm">
                      <div className="bg-gray-50 p-2 rounded text-center">
                        <div className="font-medium">{smartMoneyData.market_structure?.structure_points?.length || 0}</div>
                        <div className="text-gray-600">Structure Points</div>
                      </div>
                      <div className="bg-gray-50 p-2 rounded text-center">
                        <div className="font-medium">{smartMoneyData.market_structure?.break_of_structure?.length || 0}</div>
                        <div className="text-gray-600">BOS Events</div>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Recent BOS Events */}
                <div className="bg-white p-6 rounded-lg shadow-md">
                  <h4 className="font-semibold mb-4">Recent Break of Structure</h4>
                  <div className="space-y-2 max-h-60 overflow-y-auto">
                    {smartMoneyData.market_structure?.break_of_structure?.length > 0 ? (
                      smartMoneyData.market_structure.break_of_structure.map((bos, index) => (
                        <div key={index} className={`p-2 rounded text-sm ${
                          bos.type === 'bullish_bos' ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700'
                        }`}>
                          <div className="font-medium">{bos.type.replace('_', ' ').toUpperCase()}</div>
                          <div className="text-xs">Price: ${bos.price?.toFixed(2)} | Level: ${bos.level_broken?.toFixed(2)}</div>
                          <div className="text-xs">{new Date(bos.time).toLocaleDateString()}</div>
                        </div>
                      ))
                    ) : (
                      <div className="text-gray-500 text-center">No recent BOS events</div>
                    )}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Price Action Tab */}
          {activeTab === 'price-action' && (
            <div className="space-y-6">
              <div className="bg-indigo-50 p-4 rounded-lg">
                <h3 className="text-lg font-semibold text-indigo-800 mb-2">Price Action Analysis</h3>
                <p className="text-indigo-600 text-sm">
                  Comprehensive price action including support/resistance, candlestick patterns, and volume analysis.
                </p>
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Support/Resistance */}
                <div className="bg-white p-6 rounded-lg shadow-md">
                  <h4 className="font-semibold mb-4 flex items-center">
                    <Target className="mr-2" size={16} />
                    Key Levels
                  </h4>
                  <div className="space-y-3">
                    {smartMoneyData.key_levels?.support_resistance?.nearest_resistance && (
                      <div className="flex justify-between items-center p-2 bg-red-50 rounded">
                        <span className="text-sm text-red-700">Nearest Resistance</span>
                        <span className="font-medium text-red-800">
                          ${smartMoneyData.key_levels.support_resistance.nearest_resistance.toFixed(2)}
                        </span>
                      </div>
                    )}
                    {smartMoneyData.key_levels?.support_resistance?.nearest_support && (
                      <div className="flex justify-between items-center p-2 bg-green-50 rounded">
                        <span className="text-sm text-green-700">Nearest Support</span>
                        <span className="font-medium text-green-800">
                          ${smartMoneyData.key_levels.support_resistance.nearest_support.toFixed(2)}
                        </span>
                      </div>
                    )}
                  </div>
                </div>

                {/* Candlestick Patterns */}
                <div className="bg-white p-6 rounded-lg shadow-md">
                  <h4 className="font-semibold mb-4 flex items-center">
                    <BarChart3 className="mr-2" size={16} />
                    Recent Patterns
                  </h4>
                  <div className="space-y-2 max-h-48 overflow-y-auto">
                    {smartMoneyData.patterns?.candlestick_patterns?.slice(0, 5).map((pattern, index) => (
                      <div key={index} className={`p-2 rounded text-sm ${getSignalColor(pattern.signal)}`}>
                        <div className="font-medium">{pattern.name}</div>
                        <div className="text-xs">{pattern.signal.toUpperCase()} | {pattern.reliability} reliability</div>
                        <div className="text-xs">{new Date(pattern.time).toLocaleDateString()}</div>
                      </div>
                    )) || <div className="text-gray-500 text-center">No recent patterns</div>}
                  </div>
                </div>

                {/* Volume Analysis */}
                <div className="bg-white p-6 rounded-lg shadow-md lg:col-span-2">
                  <h4 className="font-semibold mb-4 flex items-center">
                    <Activity className="mr-2" size={16} />
                    Volume Analysis
                  </h4>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="bg-gray-50 p-3 rounded text-center">
                      <div className="font-bold text-lg">
                        {smartMoneyData.volume_analysis?.current_volume_ratio?.toFixed(2)}x
                      </div>
                      <div className="text-sm text-gray-600">Current Volume Ratio</div>
                    </div>
                    <div className="bg-gray-50 p-3 rounded text-center">
                      <div className="font-bold text-lg">
                        ${smartMoneyData.volume_analysis?.point_of_control?.price?.toFixed(2)}
                      </div>
                      <div className="text-sm text-gray-600">Point of Control</div>
                    </div>
                    <div className="bg-gray-50 p-3 rounded text-center">
                      <div className="font-bold text-lg">
                        {smartMoneyData.volume_analysis?.high_volume_bars?.length || 0}
                      </div>
                      <div className="text-sm text-gray-600">High Volume Bars</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {!smartMoneyData && !loading && (
        <div className="bg-white p-8 rounded-lg shadow-md text-center">
          <Activity className="mx-auto mb-4 text-gray-400" size={48} />
          <p className="text-gray-600">Enter a stock symbol and click "Analyze Smart Money" to view comprehensive Smart Money Concepts and Price Action analysis.</p>
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
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

  // Function to handle sidebar state from Sidebar component
  const handleSidebarToggle = (collapsed) => {
    setSidebarCollapsed(collapsed);
  };

  const renderContent = () => {
    switch (activeTab) {
      case 'dashboard':
        return <Dashboard />;
      case 'portfolio':
        return <Portfolio />;
      case 'investments':
        return (
          <Suspense fallback={<LoadingFallback componentName="Investment Scoring" />}>
            <InvestmentScoring />
          </Suspense>
        );
      case 'screener':
        return (
          <Suspense fallback={<LoadingFallback componentName="Advanced Screener" />}>
            <AdvancedScreener />
          </Suspense>
        );
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
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50 flex">
        <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} />
        <main className={`flex-1 transition-all duration-300 ${
          // Dynamic margin based on screen size and sidebar state
          'ml-16 md:ml-64'
        } p-4 md:p-8`}>
          <div className="max-w-7xl mx-auto">
            {renderContent()}
          </div>
        </main>
      </div>
    </BrowserRouter>
  );
}

export default App;