import React, { useState, useEffect, Suspense, useMemo, useCallback, createContext, useContext } from "react";
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
  RefreshCw,
  Moon,
  Sun,
  Bot,
  History,
  Users,
  ChevronDown,
  Info,
  Zap,
  MoreVertical,
  CheckCircle,
  XCircle
} from "lucide-react";

// Lazy loading for heavy components
const AdvancedScreener = React.lazy(() => import("./components/AdvancedScreener"));
const InvestmentScoring = React.lazy(() => import("./components/InvestmentScoring"));

import "./App.css";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

// Configure axios with timeout and better error handling
axios.defaults.timeout = 30000; // 30 seconds timeout
axios.defaults.headers.common['Content-Type'] = 'application/json';

// Error Boundary Component to prevent browser extension crashes
class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('Browser extension or runtime error caught:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen bg-gradient-to-br from-blue-900 to-purple-900 flex items-center justify-center">
          <div className="bg-white p-8 rounded-lg shadow-xl max-w-md text-center">
            <h2 className="text-xl font-bold text-red-600 mb-4">Application Error</h2>
            <p className="text-gray-600 mb-4">
              An error occurred, possibly due to a browser extension. Please try:
            </p>
            <ul className="text-left text-sm text-gray-600 mb-4">
              <li>• Disabling crypto/trading browser extensions</li>
              <li>• Refreshing the page</li>
              <li>• Using incognito mode</li>
            </ul>
            <button 
              onClick={() => window.location.reload()} 
              className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
            >
              Reload Application
            </button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

// Colors for portfolio charts
const COLORS = [
  '#2563eb', '#7c3aed', '#dc2626', '#ea580c', '#ca8a04', 
  '#16a34a', '#0891b2', '#c2410c', '#9333ea', '#0d9488'
];

// Theme Context
const ThemeContext = createContext();
export const useTheme = () => useContext(ThemeContext);

const ThemeProvider = ({ children }) => {
  const [isDarkMode, setIsDarkMode] = useState(false);

  const toggleDarkMode = useCallback(() => {
    setIsDarkMode(prev => {
      const newMode = !prev;
      localStorage.setItem('darkMode', JSON.stringify(newMode));
      return newMode;
    });
  }, []);

  useEffect(() => {
    const savedMode = localStorage.getItem('darkMode');
    if (savedMode) {
      setIsDarkMode(JSON.parse(savedMode));
    }
  }, []);

  return (
    <ThemeContext.Provider value={{ isDarkMode, toggleDarkMode }}>
      <div className={isDarkMode ? 'dark' : ''}>
        {children}
      </div>
    </ThemeContext.Provider>
  );
};
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
  const { isDarkMode, toggleDarkMode } = useTheme();

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
      title: "Unusual Whales 🐋",
      items: [
        { id: 'options-flow', label: 'Options Flow', icon: Activity, color: 'from-cyan-500 to-blue-600', badge: '📈', shortLabel: 'Flow' },
        { id: 'dark-pool', label: 'Dark Pool', icon: Eye, color: 'from-gray-600 to-slate-700', badge: '🌊', shortLabel: 'Dark' },
        { id: 'congressional', label: 'Congressional Trades', icon: Users, color: 'from-red-500 to-pink-600', badge: '🏛️', shortLabel: 'Congress' },
        { id: 'trading-strategies', label: 'Trading Strategies', icon: Target, color: 'from-green-500 to-emerald-600', badge: '🎯', shortLabel: 'Strategies' }
      ]
    },
    {
      title: "TradeStation 🏛️",
      items: [
        { id: 'ts-auth', label: 'Authentication', icon: Settings, color: 'from-blue-500 to-indigo-600', badge: '🔐', shortLabel: 'Auth' },
        { id: 'ts-portfolio', label: 'Live Portfolio', icon: Briefcase, color: 'from-emerald-500 to-green-600', badge: '📊', shortLabel: 'Live' },
        { id: 'ts-trading', label: 'Live Trading', icon: Zap, color: 'from-red-500 to-pink-600', badge: '⚡', shortLabel: 'Trade' },
        { id: 'ts-orders', label: 'Order Management', icon: History, color: 'from-purple-500 to-violet-600', badge: '📋', shortLabel: 'Orders' }
      ]
    },
    {
      title: "Automated Trading 🤖",
      items: [
        { id: 'auto-trading', label: 'Auto Options Trading', icon: Bot, color: 'from-purple-500 to-indigo-600', badge: '🤖', shortLabel: 'Auto' },
        { id: 'trading-history', label: 'Trading History', icon: History, color: 'from-blue-500 to-cyan-600', badge: '📊', shortLabel: 'History' },
        { id: 'performance', label: 'Performance Analytics', icon: BarChart3, color: 'from-green-500 to-teal-600', badge: '📈', shortLabel: 'Analytics' }
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
          <div className="mb-6">
            <div className={`flex items-center ${isCollapsed ? 'justify-center' : 'justify-center'} mb-3`}>
              {isCollapsed ? (
                // Collapsed state - FlowMind transparent glyph (larger for better visibility)
                <div className="flex items-center justify-center flex-shrink-0">
                  <img 
                    src="/assets/logos/flowmind_transparent_glyph.svg" 
                    alt="FlowMind" 
                    className="w-16 h-16"
                  />
                </div>
              ) : (
                // Expanded state - FlowMind horizontal transparent logo (larger for better visibility)
                <div className="flex items-center justify-center w-full px-2">
                  <img 
                    src="/assets/logos/flowmind_horizontal_transparent.svg" 
                    alt="FlowMind Analytics" 
                    className="h-16 w-full max-w-[280px] object-contain"
                  />
                </div>
              )}
            </div>
            {!isCollapsed && (
              <p className="text-xs text-slate-400 text-center mt-3">Where Data Flows, Intelligence Grows</p>
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
                  {group.items.map((item, itemIndex) => {
                    const Icon = item.icon;
                    const isActive = activeTab === item.id;
                    const isLastGroup = groupIndex === menuGroups.length - 1;
                    const isLastItem = itemIndex === group.items.length - 1;
                    const isNewsItem = item.id === 'news';
                    
                    return (
                      <React.Fragment key={item.id}>
                        <div className="relative group">
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
                        
                        {/* Dark Mode Toggle - Show after Market News */}
                        {isNewsItem && !isCollapsed && (
                          <div className="mt-3">
                            <button
                              onClick={toggleDarkMode}
                              className="w-full flex items-center justify-between bg-slate-800/50 hover:bg-slate-700/50 rounded-xl p-3 border border-slate-600/30 transition-all duration-200 group"
                            >
                              <div className="flex items-center space-x-3">
                                <div className={`w-8 h-8 rounded-lg flex items-center justify-center transition-all duration-200 ${
                                  isDarkMode ? 'bg-indigo-500/20 text-indigo-400' : 'bg-amber-500/20 text-amber-400'
                                }`}>
                                  {isDarkMode ? <Moon size={16} /> : <Sun size={16} />}
                                </div>
                                <span className="text-sm text-slate-300 group-hover:text-white">
                                  {isDarkMode ? 'Dark Mode' : 'Light Mode'}
                                </span>
                              </div>
                              <div className={`w-12 h-6 rounded-full p-1 transition-all duration-200 ${
                                isDarkMode ? 'bg-indigo-600' : 'bg-slate-600'
                              }`}>
                                <div className={`w-4 h-4 rounded-full bg-white transition-all duration-200 transform ${
                                  isDarkMode ? 'translate-x-6' : 'translate-x-0'
                                }`}></div>
                              </div>
                            </button>
                          </div>
                        )}
                        
                        {/* Dark Mode Toggle for collapsed state - Show after Market News */}
                        {isNewsItem && isCollapsed && (
                          <div className="mt-2 flex justify-center">
                            <button
                              onClick={toggleDarkMode}
                              className={`w-10 h-10 rounded-xl flex items-center justify-center border transition-all duration-200 ${
                                isDarkMode 
                                  ? 'bg-indigo-500/20 border-indigo-500/30 text-indigo-400 hover:bg-indigo-500/30' 
                                  : 'bg-amber-500/20 border-amber-500/30 text-amber-400 hover:bg-amber-500/30'
                              }`}
                              title={isDarkMode ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
                            >
                              {isDarkMode ? <Moon size={16} /> : <Sun size={16} />}
                            </button>
                          </div>
                        )}
                      </React.Fragment>
                    );
                  })}
                </div>
              </div>
            ))}
          </nav>

          {/* Bottom section with version/status */}
          {!isCollapsed && (
            <div className="absolute bottom-4 left-4 right-4 space-y-3">
              {/* Status Info */}
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
  const [isRefreshing, setIsRefreshing] = useState(false);

  // Memoized fetch function with duplicate request prevention
  const fetchMarketData = useCallback(async () => {
    // Prevent duplicate requests
    if (isRefreshing) return;
    
    setIsRefreshing(true);
    try {
      // Fetch market overview first
      const overviewRes = await axios.get(`${API}/market/overview`);
      setMarketData(overviewRes.data);
      
      // Then fetch top movers
      const moversRes = await axios.get(`${API}/market/top-movers`);
      setTopMovers(moversRes.data);
      
    } catch (error) {
      console.error('Error fetching market data:', error);
    } finally {
      setLoading(false);
      setIsRefreshing(false);
    }
  }, [isRefreshing]);

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
              disabled={isRefreshing}
              className={`px-3 md:px-4 py-2 rounded-lg transition-colors duration-200 flex items-center space-x-2 ${
                isRefreshing 
                  ? 'bg-white/10 cursor-not-allowed' 
                  : 'bg-white/20 hover:bg-white/30'
              }`}
            >
              <RefreshCw size={16} className={isRefreshing ? 'animate-spin' : ''} />
              <span>{isRefreshing ? 'Refreshing...' : 'Refresh'}</span>
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

// Enhanced Portfolio Component - TradeStation Inspired
const Portfolio = React.memo(() => {
  const [portfolio, setPortfolio] = useState(null);
  const [portfolioChartData, setPortfolioChartData] = useState([]);
  const [showAddForm, setShowAddForm] = useState(false);
  const [activeTab, setActiveTab] = useState('positions');
  const [whaleDataEnabled, setWhaleDataEnabled] = useState(false); // Will be true when API key is added
  const [formData, setFormData] = useState({
    symbol: '',
    shares: '',
    purchase_price: '',
    purchase_date: new Date().toISOString().split('T')[0],
    position_type: 'stock' // stock, option_call, option_put
  });

  // Memoized API functions
  const fetchPortfolio = useCallback(async () => {
    try {
      const response = await axios.get(`${API}/portfolio`);
      setPortfolio(response.data);
      
      // Generate chart data
      if (response.data.items) {
        const chartData = response.data.items.map(item => ({
          symbol: item.symbol,
          value: item.current_value,
          shares: item.shares,
          sector: item.sector || 'Unknown'
        }));
        setPortfolioChartData(chartData);
      }
    } catch (error) {
      console.error('Error loading portfolio:', error);
    }
  }, []);

  const deleteItem = useCallback(async (itemId) => {
    try {
      await axios.delete(`${API}/portfolio/${itemId}`);
      await fetchPortfolio();
    } catch (error) {
      console.error('Error deleting portfolio item:', error);
    }
  }, [fetchPortfolio]);

  const handleSubmit = useCallback(async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${API}/portfolio`, {
        ...formData,
        shares: parseFloat(formData.shares),
        purchase_price: parseFloat(formData.purchase_price)
      });
      setShowAddForm(false);
      setFormData({
        symbol: '',
        shares: '',
        purchase_price: '',
        purchase_date: new Date().toISOString().split('T')[0],
        position_type: 'stock'
      });
      await fetchPortfolio();
    } catch (error) {
      console.error('Error adding portfolio item:', error);
    }
  }, [formData, fetchPortfolio]);

  useEffect(() => {
    fetchPortfolio();
  }, [fetchPortfolio]);

  // Tab navigation
  const tabs = [
    { id: 'positions', label: 'Positions', icon: '📊' },
    { id: 'options', label: 'Options', icon: '🎯', disabled: !whaleDataEnabled },
    { id: 'performance', label: 'Performance', icon: '📈' },
    { id: 'risk', label: 'Risk Analysis', icon: '⚡', disabled: !whaleDataEnabled }
  ];

  const renderTabContent = () => {
    switch (activeTab) {
      case 'positions':
        return renderPositionsTab();
      case 'options':
        return renderOptionsTab();
      case 'performance':
        return renderPerformanceTab();
      case 'risk':
        return renderRiskTab();
      default:
        return renderPositionsTab();
    }
  };

  const renderPositionsTab = () => (
    <div className="space-y-6">
      {/* Portfolio Summary Cards */}
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
            <div className="mt-2 flex items-center space-x-1 text-xs text-gray-500">
              <span>Market Value</span>
              {whaleDataEnabled && <span className="text-green-500">• Live Whale Data</span>}
            </div>
          </div>
          
          <div className="bg-white/80 backdrop-blur-sm p-4 md:p-6 rounded-xl shadow-lg border border-gray-100 card-hover">
            <div className="flex items-center space-x-3 mb-2">
              <div className="p-2 bg-gradient-to-r from-purple-500 to-indigo-500 rounded-lg text-white">
                <Briefcase size={20} />
              </div>
              <h3 className="text-sm font-medium text-gray-600">Total Cost</h3>
            </div>
            <p className="text-2xl md:text-3xl font-bold text-gray-800">${portfolio.total_cost?.toFixed(2)}</p>
            <div className="mt-2 text-xs text-gray-500">Cost Basis</div>
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
            <div className="mt-2 text-xs text-gray-500">Unrealized</div>
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
              <h3 className="text-sm font-medium text-gray-600">Return %</h3>
            </div>
            <p className={`text-2xl md:text-3xl font-bold ${portfolio.total_profit_loss_percent >= 0 ? 'text-emerald-600' : 'text-red-600'}`}>
              {portfolio.total_profit_loss_percent?.toFixed(2)}%
            </p>
            <div className="mt-2 text-xs text-gray-500">Total Return</div>
          </div>
        </div>
      )}

      {/* Portfolio Allocation Chart */}
      {portfolioChartData.length > 0 && (
        <div className="bg-white/80 backdrop-blur-sm p-4 md:p-6 rounded-2xl shadow-lg border border-gray-100 card-hover">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg md:text-xl font-bold text-gray-800 flex items-center">
              <PieChartIcon className="mr-3 text-blue-600" size={24} />
              Portfolio Allocation
            </h3>
            {whaleDataEnabled && (
              <span className="px-3 py-1 bg-green-100 text-green-700 text-xs rounded-full">
                🐋 Whale Data Active
              </span>
            )}
          </div>
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

      {/* Holdings Table */}
      <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-lg border border-gray-100 overflow-hidden card-hover">
        <div className="px-4 md:px-6 py-4 bg-gradient-to-r from-blue-50 to-cyan-50 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <h3 className="text-lg md:text-xl font-bold text-gray-800 flex items-center">
              <Briefcase className="mr-3 text-blue-600" size={24} />
              Holdings
            </h3>
            <div className="flex items-center space-x-2">
              {!whaleDataEnabled && (
                <span className="px-3 py-1 bg-amber-100 text-amber-700 text-xs rounded-full">
                  ⏳ Whale Features Coming Soon
                </span>
              )}
            </div>
          </div>
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
                <th className="px-4 md:px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  {whaleDataEnabled ? 'Whale Activity' : 'Actions'}
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {portfolio?.items?.map((item) => (
                <tr key={item.id} className="hover:bg-blue-50 transition-colors duration-200">
                  <td className="px-4 md:px-6 py-4">
                    <div className="flex items-center space-x-2">
                      <span className="font-bold text-blue-600 font-mono">{item.symbol}</span>
                      {whaleDataEnabled && (
                        <span className="px-2 py-1 bg-green-100 text-green-700 text-xs rounded">
                          🐋 Active
                        </span>
                      )}
                    </div>
                  </td>
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
                    {whaleDataEnabled ? (
                      <div className="flex items-center space-x-2">
                        <button className="text-blue-600 hover:text-blue-800 hover:bg-blue-50 p-2 rounded-lg transition-colors duration-200">
                          🐋 Flow
                        </button>
                        <button className="text-purple-600 hover:text-purple-800 hover:bg-purple-50 p-2 rounded-lg transition-colors duration-200">
                          📊 Dark Pool
                        </button>
                      </div>
                    ) : (
                      <button
                        onClick={() => deleteItem(item.id)}
                        className="text-red-600 hover:text-red-800 hover:bg-red-50 p-2 rounded-lg transition-colors duration-200"
                      >
                        <Trash2 size={16} />
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );

  const renderOptionsTab = () => (
    <div className="space-y-6">
      <div className="bg-white/80 backdrop-blur-sm p-8 rounded-2xl shadow-lg border border-gray-100 text-center">
        <div className="max-w-md mx-auto">
          <div className="w-16 h-16 bg-gradient-to-r from-amber-400 to-orange-500 rounded-full flex items-center justify-center mx-auto mb-4">
            <span className="text-2xl">🐋</span>
          </div>
          <h3 className="text-xl font-bold text-gray-800 mb-2">Options Tracking Coming Soon</h3>
          <p className="text-gray-600 mb-4">
            Options positions, unusual flow, and smart money analysis will be available when you connect your Unusual Whales API.
          </p>
          <div className="bg-amber-50 border border-amber-200 rounded-lg p-4 mb-4">
            <p className="text-sm text-amber-800">
              <strong>Planned Features:</strong><br />
              • Options positions tracking<br />
              • Unusual options flow alerts<br />
              • Dark pool activity for holdings<br />
              • Congressional trades monitoring
            </p>
          </div>
          <button 
            onClick={() => setWhaleDataEnabled(true)}
            className="px-6 py-2 bg-gradient-to-r from-blue-600 to-cyan-600 text-white rounded-lg hover:shadow-lg transition-all duration-200"
          >
            🔜 Preview Mode
          </button>
        </div>
      </div>
    </div>
  );

  const renderPerformanceTab = () => (
    <div className="space-y-6">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white/80 backdrop-blur-sm p-6 rounded-2xl shadow-lg border border-gray-100 card-hover">
          <h3 className="text-lg font-bold text-gray-800 mb-4 flex items-center">
            📈 Performance Metrics
          </h3>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-gray-600">Total Return</span>
              <span className="font-bold text-emerald-600">
                {portfolio?.total_profit_loss_percent ? `${portfolio.total_profit_loss_percent.toFixed(2)}%` : '0.00%'}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Best Performer</span>
              <span className="font-bold text-green-600">
                {portfolio?.items?.length > 0 ? 
                  portfolio.items.reduce((best, item) => 
                    (item.profit_loss_percent || 0) > (best.profit_loss_percent || 0) ? item : best
                  ).symbol : 'N/A'}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Worst Performer</span>
              <span className="font-bold text-red-600">
                {portfolio?.items?.length > 0 ? 
                  portfolio.items.reduce((worst, item) => 
                    (item.profit_loss_percent || 0) < (worst.profit_loss_percent || 0) ? item : worst
                  ).symbol : 'N/A'}
              </span>
            </div>
          </div>
        </div>

        <div className="bg-white/80 backdrop-blur-sm p-6 rounded-2xl shadow-lg border border-gray-100 card-hover">
          <h3 className="text-lg font-bold text-gray-800 mb-4 flex items-center">
            📊 Allocation Analysis
          </h3>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-gray-600">Total Positions</span>
              <span className="font-bold text-blue-600">{portfolio?.items?.length || 0}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Largest Position</span>
              <span className="font-bold text-purple-600">
                {portfolio?.items?.length > 0 ? 
                  portfolio.items.reduce((largest, item) => 
                    (item.current_value || 0) > (largest.current_value || 0) ? item : largest
                  ).symbol : 'N/A'}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Concentration Risk</span>
              <span className="font-bold text-amber-600">
                {portfolio?.items?.length > 0 ? 
                  `${((portfolio.items.reduce((largest, item) => 
                    (item.current_value || 0) > (largest.current_value || 0) ? item : largest
                  ).current_value / portfolio.total_value) * 100).toFixed(1)}%` : '0%'}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  const renderRiskTab = () => (
    <div className="space-y-6">
      <div className="bg-white/80 backdrop-blur-sm p-8 rounded-2xl shadow-lg border border-gray-100 text-center">
        <div className="max-w-md mx-auto">
          <div className="w-16 h-16 bg-gradient-to-r from-red-400 to-pink-500 rounded-full flex items-center justify-center mx-auto mb-4">
            <span className="text-2xl">⚡</span>
          </div>
          <h3 className="text-xl font-bold text-gray-800 mb-2">Advanced Risk Analysis</h3>
          <p className="text-gray-600 mb-4">
            VaR calculations, correlation analysis, and smart money risk alerts coming with Unusual Whales integration.
          </p>
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-4">
            <p className="text-sm text-red-800">
              <strong>Planned Risk Features:</strong><br />
              • Value at Risk (VaR) calculations<br />
              • Portfolio correlation matrix<br />
              • Smart money divergence alerts<br />
              • Sector concentration warnings
            </p>
          </div>
        </div>
      </div>
    </div>
  );

  return (
    <div className="space-y-6">
      {/* Portfolio Header with Add Button */}
      <div className="bg-gradient-to-r from-blue-600 via-purple-600 to-cyan-600 rounded-2xl p-6 text-white shadow-xl">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-3xl font-bold mb-2">Portfolio Manager</h2>
            <p className="text-blue-100">TradeStation-inspired portfolio tracking {whaleDataEnabled && '🐋'}</p>
          </div>
          <button
            onClick={() => setShowAddForm(true)}
            className="bg-white/20 hover:bg-white/30 px-4 py-3 rounded-xl transition-all duration-200 flex items-center space-x-2"
          >
            <Plus size={20} />
            <span className="font-medium">Add Position</span>
          </button>
        </div>
      </div>

      {/* Portfolio Tab Navigation */}
      <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-lg border border-gray-100 overflow-hidden">
        <div className="flex border-b border-gray-200">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => !tab.disabled && setActiveTab(tab.id)}
              disabled={tab.disabled}
              className={`flex-1 flex items-center justify-center space-x-2 px-4 py-4 text-sm font-medium transition-all duration-200 ${
                activeTab === tab.id
                  ? 'bg-gradient-to-r from-blue-600 to-cyan-600 text-white'
                  : tab.disabled
                  ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                  : 'bg-white text-gray-600 hover:bg-blue-50 hover:text-blue-700'
              }`}
            >
              <span className="text-lg">{tab.icon}</span>
              <span>{tab.label}</span>
              {tab.disabled && (
                <span className="text-xs bg-gray-300 text-gray-600 px-2 py-1 rounded-full">Soon</span>
              )}
            </button>
          ))}
        </div>
        
        {/* Tab Content */}
        <div className="p-6">
          {renderTabContent()}
        </div>
      </div>

      {/* Add Stock Modal */}
      {showAddForm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-2xl p-6 w-full max-w-md shadow-2xl">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-xl font-bold text-gray-800">Add New Position</h3>
              <button
                onClick={() => setShowAddForm(false)}
                className="text-gray-400 hover:text-gray-600 p-2 hover:bg-gray-100 rounded-lg transition-colors duration-200"
              >
                ×
              </button>
            </div>
            
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Stock Symbol</label>
                <input
                  type="text"
                  value={formData.symbol}
                  onChange={(e) => setFormData({...formData, symbol: e.target.value.toUpperCase()})}
                  className="w-full px-4 py-3 rounded-lg border border-gray-300 focus:border-blue-500 focus:ring-2 focus:ring-blue-200 transition-all"
                  placeholder="e.g., AAPL, MSFT"
                  required
                />
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Shares</label>
                  <input
                    type="number"
                    step="0.01"
                    value={formData.shares}
                    onChange={(e) => setFormData({...formData, shares: e.target.value})}
                    className="w-full px-4 py-3 rounded-lg border border-gray-300 focus:border-blue-500 focus:ring-2 focus:ring-blue-200 transition-all"
                    placeholder="100"
                    required
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Purchase Price</label>
                  <input
                    type="number"
                    step="0.01"
                    value={formData.purchase_price}
                    onChange={(e) => setFormData({...formData, purchase_price: e.target.value})}
                    className="w-full px-4 py-3 rounded-lg border border-gray-300 focus:border-blue-500 focus:ring-2 focus:ring-blue-200 transition-all"
                    placeholder="150.00"
                    required
                  />
                </div>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Purchase Date</label>
                <input
                  type="date"
                  value={formData.purchase_date}
                  onChange={(e) => setFormData({...formData, purchase_date: e.target.value})}
                  className="w-full px-4 py-3 rounded-lg border border-gray-300 focus:border-blue-500 focus:ring-2 focus:ring-blue-200 transition-all"
                  required
                />
              </div>
              
              <div className="flex space-x-3 pt-4">
                <button
                  type="submit"
                  className="flex-1 bg-gradient-to-r from-blue-600 to-cyan-600 text-white py-3 px-6 rounded-lg font-medium hover:from-blue-700 hover:to-cyan-700 transition-all duration-200"
                >
                  Add Position
                </button>
                <button
                  type="button"
                  onClick={() => setShowAddForm(false)}
                  className="flex-1 bg-gray-200 text-gray-700 py-3 px-6 rounded-lg font-medium hover:bg-gray-300 transition-all duration-200"
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
});

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
    // Defensive programming - ensure signal is valid
    if (!signal || typeof signal !== 'string') {
      return 'text-gray-600 bg-gray-50';
    }
    
    switch (signal.toLowerCase()) {
      case 'bullish': return 'text-green-600 bg-green-50';
      case 'bearish': return 'text-red-600 bg-red-50';
      case 'buy': return 'text-green-700 bg-green-100';
      case 'sell': return 'text-red-700 bg-red-100';
      default: return 'text-gray-600 bg-gray-50';
    }
  };

  const OrderBlockCard = ({ orderBlock }) => {
    // Defensive programming against browser extension interference
    if (!orderBlock || typeof orderBlock !== 'object') {
      return <div className="p-3 text-gray-500">Invalid order block data</div>;
    }
    
    const blockType = orderBlock.type || 'unknown';
    const strength = orderBlock.strength || 'weak';
    
    return (
      <div className={`p-3 rounded-lg border-l-4 ${
        blockType === 'bullish' 
          ? 'border-green-500 bg-green-50' 
          : 'border-red-500 bg-red-50'
      }`}>
        <div className="flex justify-between items-center mb-2">
          <span className={`font-semibold ${
            blockType === 'bullish' ? 'text-green-700' : 'text-red-700'
          }`}>
            {blockType.toUpperCase()} Order Block
          </span>
          <span className={`text-xs px-2 py-1 rounded ${
            strength === 'strong' 
              ? 'bg-purple-100 text-purple-700'
              : strength === 'medium'
              ? 'bg-blue-100 text-blue-700'
              : 'bg-gray-100 text-gray-700'
          }`}>
            {strength}
          </span>
        </div>
        <div className="text-sm space-y-1">
          <div>High: <span className="font-medium">${orderBlock.high?.toFixed(2) || 'N/A'}</span></div>
          <div>Low: <span className="font-medium">${orderBlock.low?.toFixed(2) || 'N/A'}</span></div>
          <div>Status: <span className={`font-medium ${orderBlock.tested ? 'text-red-600' : 'text-green-600'}`}>
            {orderBlock.tested ? 'Tested' : 'Untested'}
          </span></div>
        </div>
      </div>
    );
  };

  const FairValueGapCard = ({ fvg }) => {
    // Defensive programming against browser extension interference
    if (!fvg || typeof fvg !== 'object') {
      return <div className="p-3 text-gray-500">Invalid FVG data</div>;
    }
    
    const fvgType = fvg.type || 'unknown';
    
    return (
      <div className={`p-3 rounded-lg border-l-4 ${
        fvgType === 'bullish' 
          ? 'border-blue-500 bg-blue-50' 
          : 'border-orange-500 bg-orange-50'
      }`}>
        <div className="flex justify-between items-center mb-2">
          <span className={`font-semibold ${
            fvgType === 'bullish' ? 'text-blue-700' : 'text-orange-700'
          }`}>
            {fvgType.toUpperCase()} FVG
          </span>
          <span className={`text-xs px-2 py-1 rounded ${
            fvg.filled ? 'bg-gray-100 text-gray-700' : 'bg-yellow-100 text-yellow-700'
          }`}>
            {fvg.filled ? 'Filled' : 'Open'}
          </span>
        </div>
        <div className="text-sm space-y-1">
          <div>Gap High: <span className="font-medium">${fvg.gap_high?.toFixed(2) || 'N/A'}</span></div>
          <div>Gap Low: <span className="font-medium">${fvg.gap_low?.toFixed(2) || 'N/A'}</span></div>
          <div>Size: <span className="font-medium">${fvg.gap_size?.toFixed(2) || 'N/A'}</span></div>
          {!fvg.filled && fvg.fill_percentage > 0 && (
            <div>Filled: <span className="font-medium">{fvg.fill_percentage?.toFixed(1) || '0'}%</span></div>
          )}
        </div>
      </div>
    );
  };

  const LiquiditySweepCard = ({ sweep }) => {
    // Defensive programming against browser extension interference
    if (!sweep || typeof sweep !== 'object') {
      return <div className="p-3 text-gray-500">Invalid sweep data</div>;
    }
    
    const sweepType = sweep.type || 'unknown';
    const significance = sweep.significance || 'minor';
    
    return (
      <div className={`p-3 rounded-lg border-l-4 ${
        sweepType === 'high_sweep' 
          ? 'border-purple-500 bg-purple-50' 
          : 'border-indigo-500 bg-indigo-50'
      }`}>
        <div className="flex justify-between items-center mb-2">
          <span className={`font-semibold ${
            sweepType === 'high_sweep' ? 'text-purple-700' : 'text-indigo-700'
          }`}>
            {sweepType === 'high_sweep' ? 'High Sweep' : 'Low Sweep'}
          </span>
          <span className={`text-xs px-2 py-1 rounded ${
            significance === 'major' 
              ? 'bg-red-100 text-red-700'
              : 'bg-yellow-100 text-yellow-700'
          }`}>
            {significance}
          </span>
        </div>
        <div className="text-sm space-y-1">
          <div>Price: <span className="font-medium">${sweep.price?.toFixed(2) || 'N/A'}</span></div>
          <div>Volume: <span className="font-medium">{sweep.volume?.toLocaleString() || 'N/A'}</span></div>
          <div>Time: <span className="font-medium">{sweep.time ? new Date(sweep.time).toLocaleDateString() : 'N/A'}</span></div>
        </div>
      </div>
    );
  };

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
                  {smartMoneyData.trading_signals?.slice(0, 3).map((signal, index) => {
                    // Defensive programming against browser extension interference
                    if (!signal || typeof signal !== 'object') return null;
                    const signalType = signal.type || 'UNKNOWN';
                    
                    return (
                      <div key={index} className={`px-3 py-2 rounded text-sm ${getSignalColor(signalType)}`}>
                        <div className="font-medium">{signalType.toUpperCase()}</div>
                        <div className="text-xs mt-1">{signal.reason || 'No reason provided'}</div>
                        <div className="text-xs mt-1">
                          Entry: ${signal.entry?.toFixed(2) || 'N/A'} | Target: ${signal.target?.toFixed(2) || 'N/A'}
                        </div>
                      </div>
                    );
                  }).filter(Boolean) || <div className="text-gray-500 text-sm">No active signals</div>}
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

// ==================== UNUSUAL WHALES COMPONENTS ====================

// Options Flow Component
const OptionsFlow = () => {
  const [optionsData, setOptionsData] = useState([]);
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filters, setFilters] = useState({
    minimum_premium: 200000,
    minimum_volume_oi_ratio: 1.0,
    limit: 50
  });
  const { isDarkMode } = useTheme();
  
  // Auto-refresh state - every 1 second for real-time flow
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [lastUpdate, setLastUpdate] = useState(null);
  const [refreshCountdown, setRefreshCountdown] = useState(1); // 1 second for real-time
  const [isRefreshing, setIsRefreshing] = useState(false);

  const fetchOptionsFlow = async (showLoading = true) => {
    if (showLoading) {
      setLoading(true);
    } else {
      setIsRefreshing(true);
    }
    setError(null);
    
    try {
      const response = await axios.get(`${API}/unusual-whales/options/flow-alerts`, {
        params: { ...filters, include_analysis: true }
      });
      
      if (response.data.status === 'success') {
        setOptionsData(response.data.data.alerts || []);
        setAnalysis(response.data.analysis || null);
        setLastUpdate(new Date());
        setRefreshCountdown(1); // Reset to 1 second
      }
    } catch (err) {
      console.error('Error fetching options flow:', err);
      setError(err.message);
    } finally {
      setLoading(false);
      setIsRefreshing(false);
    }
  };

  // Auto-refresh effect - runs every second for real-time flow like OptionStrat
  useEffect(() => {
    if (autoRefresh && !loading) {
      const interval = setInterval(() => {
        setRefreshCountdown(prev => {
          if (prev <= 1) {
            fetchOptionsFlow(false); // Silent refresh every second
            return 1; // Reset to 1 second
          }
          return prev - 1;
        });
      }, 1000);

      return () => clearInterval(interval);
    }
  }, [autoRefresh, loading, filters]);

  // Initial load
  useEffect(() => {
    fetchOptionsFlow();
  }, []);

  const handleFiltersChange = (newFilters) => {
    setFilters(newFilters);
    fetchOptionsFlow();
  };

  const toggleAutoRefresh = () => {
    setAutoRefresh(!autoRefresh);
    if (!autoRefresh) {
      setRefreshCountdown(1); // 1 second intervals
    }
  };

  const manualRefresh = () => {
    fetchOptionsFlow();
  };

  const formatLastUpdate = (date) => {
    if (!date) return 'Niciodată';
    return date.toLocaleTimeString('ro-RO', { 
      hour: '2-digit', 
      minute: '2-digit', 
      second: '2-digit' 
    });
  };

  const applyFilters = () => {
    fetchOptionsFlow();
  };

  const getSentimentColor = (sentiment) => {
    switch (sentiment) {
      case 'bullish': return 'text-green-600 bg-green-50';
      case 'bearish': return 'text-red-600 bg-red-50';
      default: return 'text-gray-600 bg-gray-50';
    }
  };

  const getTradeSize = (size) => {
    switch (size) {
      case 'whale': return 'bg-purple-100 text-purple-800';
      case 'large': return 'bg-blue-100 text-blue-800';
      case 'medium': return 'bg-yellow-100 text-yellow-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className={`space-y-6 ${isDarkMode ? 'text-white' : 'text-gray-800'}`}>
      <div className="flex justify-between items-center">
        <div className="flex flex-col">
          <h2 className="text-2xl md:text-3xl font-bold">
            ⚡ Real-Time Options Flow
          </h2>
          <div className="flex items-center space-x-4 mt-1">
            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
              🔴 LIVE • 1s updates
            </span>
            <span className="text-sm text-gray-500">
              Unusual Whales API în timp real
            </span>
            {lastUpdate && (
              <span className="text-xs text-gray-400 flex items-center space-x-1">
                <span>•</span>
                <span>Ultima actualizare: {formatLastUpdate(lastUpdate)}</span>
              </span>
            )}
            {autoRefresh && (
              <span className="text-xs text-green-600 flex items-center space-x-1">
                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                <span>Flow live activ</span>
              </span>
            )}
          </div>
        </div>
        <div className="flex items-center space-x-3">
          {/* Auto-refresh toggle */}
          <div className="flex items-center space-x-2">
            <button
              onClick={toggleAutoRefresh}
              className={`flex items-center space-x-2 px-3 py-2 rounded-lg transition-colors ${
                autoRefresh 
                  ? 'bg-green-100 text-green-700 hover:bg-green-200' 
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              <div className={`w-2 h-2 rounded-full ${autoRefresh ? 'bg-green-500 animate-pulse' : 'bg-gray-400'}`}></div>
              <span className="text-sm font-medium">
                {autoRefresh ? 'Auto ON' : 'Auto OFF'}
              </span>
            </button>
            {autoRefresh && (
              <span className="text-sm text-green-600 font-medium">
                Actualizare în {refreshCountdown}s
              </span>
            )}
          </div>
          
          {/* Manual refresh button */}
          <button
            onClick={manualRefresh}
            disabled={loading || isRefreshing}
            className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-colors ${
              loading || isRefreshing
                ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                : 'bg-blue-500 hover:bg-blue-600 text-white'
            }`}
          >
            <RefreshCw className={`w-4 h-4 ${(loading || isRefreshing) ? 'animate-spin' : ''}`} />
            <span>{loading ? 'Loading...' : isRefreshing ? 'Refreshing...' : 'Refresh'}</span>
          </button>
        </div>
      </div>

      {/* Filters */}
      <div className={`${isDarkMode ? 'bg-slate-800' : 'bg-white'} p-4 rounded-lg shadow-md`}>
        <h3 className="text-lg font-semibold mb-4">Filters</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium mb-2">Min Premium ($)</label>
            <input
              type="number"
              value={filters.minimum_premium}
              onChange={(e) => setFilters({...filters, minimum_premium: parseInt(e.target.value)})}
              className={`w-full px-3 py-2 border rounded-md ${isDarkMode ? 'bg-slate-700 border-slate-600' : 'bg-white border-gray-300'}`}
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-2">Min Volume/OI Ratio</label>
            <input
              type="number"
              step="0.1"
              value={filters.minimum_volume_oi_ratio}
              onChange={(e) => setFilters({...filters, minimum_volume_oi_ratio: parseFloat(e.target.value)})}
              className={`w-full px-3 py-2 border rounded-md ${isDarkMode ? 'bg-slate-700 border-slate-600' : 'bg-white border-gray-300'}`}
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-2">Limit</label>
            <select
              value={filters.limit}
              onChange={(e) => setFilters({...filters, limit: parseInt(e.target.value)})}
              className={`w-full px-3 py-2 border rounded-md ${isDarkMode ? 'bg-slate-700 border-slate-600' : 'bg-white border-gray-300'}`}
            >
              <option value={25}>25</option>
              <option value={50}>50</option>
              <option value={100}>100</option>
            </select>
          </div>
        </div>
        <button
          onClick={applyFilters}
          className="mt-4 bg-green-500 hover:bg-green-600 text-white px-4 py-2 rounded-lg transition-colors"
        >
          Apply Filters
        </button>
      </div>

      {/* Error Display */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-center space-x-2">
            <div className="w-4 h-4 bg-red-500 rounded-full"></div>
            <span className="text-red-700 font-medium">Error loading options flow data</span>
          </div>
          <p className="text-red-600 text-sm mt-1">{error}</p>
          <button
            onClick={manualRefresh}
            className="mt-2 text-red-600 hover:text-red-800 text-sm underline"
          >
            Try again
          </button>
        </div>
      )}

      {/* Summary Stats */}
      {analysis && analysis.summary && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className={`${isDarkMode ? 'bg-slate-800' : 'bg-white'} p-4 rounded-lg shadow-md`}>
            <h3 className="text-lg font-semibold">Total Alerts</h3>
            <p className="text-2xl font-bold text-blue-600">{analysis.summary.total_alerts}</p>
          </div>
          <div className={`${isDarkMode ? 'bg-slate-800' : 'bg-white'} p-4 rounded-lg shadow-md`}>
            <h3 className="text-lg font-semibold">Total Premium</h3>
            <p className="text-2xl font-bold text-green-600">
              {analysis.summary.total_premium > 0 ? 
                `$${(analysis.summary.total_premium / 1000000).toFixed(1)}M` : 
                'N/A'
              }
            </p>
          </div>
          <div className={`${isDarkMode ? 'bg-slate-800' : 'bg-white'} p-4 rounded-lg shadow-md`}>
            <h3 className="text-lg font-semibold">Bullish/Bearish</h3>
            <p className="text-xl font-bold">
              <span className="text-green-600">{analysis.summary.bullish_count}</span>/
              <span className="text-red-600">{analysis.summary.bearish_count}</span>
            </p>
          </div>
          <div className={`${isDarkMode ? 'bg-slate-800' : 'bg-white'} p-4 rounded-lg shadow-md`}>
            <h3 className="text-lg font-semibold">Opening Trades</h3>
            <p className="text-2xl font-bold text-purple-600">{analysis.summary.opening_trades}</p>
          </div>
        </div>
      )}

      {/* Options Flow Table */}
      <div className={`${isDarkMode ? 'bg-slate-800' : 'bg-white'} rounded-lg shadow-md overflow-hidden`}>
        <h3 className="text-lg font-semibold p-4 border-b border-gray-200">Recent Flow Alerts</h3>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className={`${isDarkMode ? 'bg-slate-700' : 'bg-gray-50'}`}>
              <tr>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Time</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Symbol</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Strategy</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Expiration</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Premium</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Type</th>
              </tr>
            </thead>
            <tbody>
              {optionsData.slice(0, 20).map((alert, index) => {
                const timeStamp = new Date(alert.timestamp || Date.now());
                const timeStr = timeStamp.toLocaleTimeString('en-US', { 
                  hour: 'numeric', 
                  minute: '2-digit',
                  second: '2-digit',
                  hour12: true 
                });
                
                const strategyText = `${alert.action} ${alert.volume} ${alert.option_type === 'call' ? 'Call' : 'Put'}${alert.is_opener ? ' To Open' : ' To Close'}`;
                const expirationText = new Date(alert.expiration).toLocaleDateString('en-US', { 
                  month: 'short', 
                  day: 'numeric' 
                });
                
                return (
                  <tr key={index} className={`border-b ${isDarkMode ? 'border-slate-600' : 'border-gray-100'} hover:${isDarkMode ? 'bg-slate-700' : 'bg-gray-50'}`}>
                    <td className="px-4 py-3 text-sm text-gray-500">{timeStr}</td>
                    <td className="px-4 py-3 font-semibold text-blue-600">{alert.symbol}</td>
                    <td className="px-4 py-3">
                      <span className={`${alert.action === 'BUY' ? 'text-green-600' : 'text-red-600'} font-medium`}>
                        {strategyText}
                      </span>
                    </td>
                    <td className="px-4 py-3">{expirationText}</td>
                    <td className="px-4 py-3 font-bold">
                      {alert.premium && alert.premium > 0 ? 
                        `$${(alert.premium / 1000).toFixed(0)}k` : 
                        <span className="text-gray-400">N/A</span>
                      }
                    </td>
                    <td className="px-4 py-3">
                      <span className={`px-2 py-1 rounded text-xs font-medium ${
                        alert.has_sweep ? 'bg-red-100 text-red-800' : 
                        alert.trade_size === 'whale' ? 'bg-purple-100 text-purple-800' :
                        'bg-gray-100 text-gray-800'
                      }`}>
                        {alert.has_sweep ? 'SWEEP' : 
                         alert.trade_size === 'whale' ? 'BLOCK' : 'SPLIT'}
                      </span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Analysis Signals */}
      {analysis && analysis.signals && analysis.signals.length > 0 && (
        <div className={`${isDarkMode ? 'bg-slate-800' : 'bg-white'} p-6 rounded-lg shadow-md`}>
          <h3 className="text-lg font-semibold mb-4">Trading Signals</h3>
          <div className="space-y-3">
            {analysis.signals.map((signal, index) => (
              <div key={index} className={`p-3 rounded-lg ${isDarkMode ? 'bg-slate-700' : 'bg-blue-50'} border-l-4 border-blue-500`}>
                <h4 className="font-semibold">{signal.type}</h4>
                <p className="text-sm">{signal.description}</p>
                <p className="text-xs text-gray-500 mt-1">Confidence: {(signal.confidence * 100).toFixed(0)}%</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Data Source Information */}
      <div className={`${isDarkMode ? 'bg-slate-800 border-slate-600' : 'bg-blue-50 border-blue-200'} border rounded-lg p-4`}>
        <div className="flex items-start space-x-3">
          <div className={`${isDarkMode ? 'text-blue-400' : 'text-blue-500'}`}>
            ℹ️
          </div>
          <div>
            <h4 className={`font-semibold ${isDarkMode ? 'text-blue-300' : 'text-blue-800'}`}>
              Despre datele Options Flow
            </h4>
            <p className={`text-sm mt-1 ${isDarkMode ? 'text-slate-300' : 'text-blue-700'}`}>
              <strong>✅ REZOLVAT:</strong> Endpoint-ul corect pentru Options Flow este `/api/option-trades/flow-alerts`. 
              Datele afișate sunt 100% reale de la Unusual Whales API cu planul dvs. Basic ($150/lună). 
              Includ premii reale, DTE, tipuri de tranzacții (BUY/SELL), și detalii complete despre alert rules și sectors.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

// Dark Pool Component
const DarkPool = () => {
  const [darkPoolData, setDarkPoolData] = useState([]);
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    minimum_volume: 100000,
    minimum_dark_percentage: 0.01,
    limit: 50
  });
  const { isDarkMode } = useTheme();

  useEffect(() => {
    fetchDarkPoolData();
  }, []);

  const fetchDarkPoolData = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API}/unusual-whales/dark-pool/recent`, {
        params: { ...filters, include_analysis: true }
      });
      
      if (response.data.status === 'success') {
        setDarkPoolData(response.data.data.trades || []);
        setAnalysis(response.data.analysis || null);
      }
    } catch (error) {
      console.error('Error fetching dark pool data:', error);
    } finally {
      setLoading(false);
    }
  };

  const getSignificanceColor = (significance) => {
    switch (significance) {
      case 'very_high': return 'bg-red-100 text-red-800';
      case 'high': return 'bg-orange-100 text-orange-800';
      case 'medium': return 'bg-yellow-100 text-yellow-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className={`space-y-6 ${isDarkMode ? 'text-white' : 'text-gray-800'}`}>
      <div className="flex justify-between items-center">
        <h2 className="text-2xl md:text-3xl font-bold">
          🌊 Dark Pool Analysis
        </h2>
        <button
          onClick={fetchDarkPoolData}
          className="flex items-center space-x-2 bg-gray-600 hover:bg-gray-700 text-white px-4 py-2 rounded-lg transition-colors"
        >
          <RefreshCw className="w-4 h-4" />
          <span>Refresh</span>
        </button>
      </div>

      {/* Summary Stats */}
      {analysis && analysis.summary && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className={`${isDarkMode ? 'bg-slate-800' : 'bg-white'} p-4 rounded-lg shadow-md`}>
            <h3 className="text-lg font-semibold">Total Trades</h3>
            <p className="text-2xl font-bold text-blue-600">{analysis.summary.total_trades}</p>
          </div>
          <div className={`${isDarkMode ? 'bg-slate-800' : 'bg-white'} p-4 rounded-lg shadow-md`}>
            <h3 className="text-lg font-semibold">Dark Volume</h3>
            <p className="text-2xl font-bold text-gray-600">
              {(analysis.summary.total_dark_volume / 1000000).toFixed(1)}M
            </p>
          </div>
          <div className={`${isDarkMode ? 'bg-slate-800' : 'bg-white'} p-4 rounded-lg shadow-md`}>
            <h3 className="text-lg font-semibold">Avg Dark %</h3>
            <p className="text-2xl font-bold text-purple-600">{analysis.summary.avg_dark_percentage}%</p>
          </div>
          <div className={`${isDarkMode ? 'bg-slate-800' : 'bg-white'} p-4 rounded-lg shadow-md`}>
            <h3 className="text-lg font-semibold">Institutional</h3>
            <p className="text-2xl font-bold text-green-600">{analysis.summary.institutional_signals}</p>
          </div>
        </div>
      )}

      {/* Dark Pool Table */}
      <div className={`${isDarkMode ? 'bg-slate-800' : 'bg-white'} rounded-lg shadow-md overflow-hidden`}>
        <h3 className="text-lg font-semibold p-4 border-b border-gray-200">Recent Dark Pool Activity</h3>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className={`${isDarkMode ? 'bg-slate-700' : 'bg-gray-50'}`}>
              <tr>
                <th className="px-4 py-3 text-left">Ticker</th>
                <th className="px-4 py-3 text-left">Price</th>
                <th className="px-4 py-3 text-left">Dark Volume</th>
                <th className="px-4 py-3 text-left">Dark %</th>
                <th className="px-4 py-3 text-left">Dollar Volume</th>
                <th className="px-4 py-3 text-left">Significance</th>
                <th className="px-4 py-3 text-left">Institutional</th>
              </tr>
            </thead>
            <tbody>
              {darkPoolData.slice(0, 20).map((trade, index) => (
                <tr key={index} className={`border-b ${isDarkMode ? 'border-slate-600' : 'border-gray-100'} hover:${isDarkMode ? 'bg-slate-700' : 'bg-gray-50'}`}>
                  <td className="px-4 py-3 font-semibold">{trade.ticker}</td>
                  <td className="px-4 py-3">${trade.price?.toFixed(2)}</td>
                  <td className="px-4 py-3">{trade.dark_volume?.toLocaleString()}</td>
                  <td className="px-4 py-3 font-medium">{trade.dark_percentage}%</td>
                  <td className="px-4 py-3">${(trade.dollar_volume / 1000000).toFixed(1)}M</td>
                  <td className="px-4 py-3">
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getSignificanceColor(trade.significance)}`}>
                      {trade.significance}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    {trade.institutional_signal ? 
                      <span className="text-green-600">✓</span> : 
                      <span className="text-gray-400">-</span>
                    }
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

// Congressional Trades Component  
const CongressionalTrades = () => {
  const [congressionalData, setCongressionalData] = useState([]);
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    days_back: 30,
    minimum_amount: 15000,
    party_filter: '',
    transaction_type: ''
  });
  const { isDarkMode } = useTheme();

  useEffect(() => {
    fetchCongressionalData();
  }, []);

  const fetchCongressionalData = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API}/unusual-whales/congressional/trades`, {
        params: { ...filters, include_analysis: true }
      });
      
      if (response.data.status === 'success') {
        setCongressionalData(response.data.data.trades || []);
        setAnalysis(response.data.analysis || null);
      }
    } catch (error) {
      console.error('Error fetching congressional data:', error);
    } finally {
      setLoading(false);
    }
  };

  const getPartyColor = (party) => {
    switch (party?.toLowerCase()) {
      case 'democrat': return 'bg-blue-100 text-blue-800';
      case 'republican': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getTransactionColor = (type) => {
    return type === 'Purchase' ? 'text-green-600' : 'text-red-600';
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className={`space-y-6 ${isDarkMode ? 'text-white' : 'text-gray-800'}`}>
      <div className="flex justify-between items-center">
        <h2 className="text-2xl md:text-3xl font-bold">
          🏛️ Congressional Trades
        </h2>
        <button
          onClick={fetchCongressionalData}
          className="flex items-center space-x-2 bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded-lg transition-colors"
        >
          <RefreshCw className="w-4 h-4" />
          <span>Refresh</span>
        </button>
      </div>

      {/* Summary Stats */}
      {analysis && analysis.summary && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className={`${isDarkMode ? 'bg-slate-800' : 'bg-white'} p-4 rounded-lg shadow-md`}>
            <h3 className="text-lg font-semibold">Total Trades</h3>
            <p className="text-2xl font-bold text-blue-600">{analysis.summary.total_trades}</p>
          </div>
          <div className={`${isDarkMode ? 'bg-slate-800' : 'bg-white'} p-4 rounded-lg shadow-md`}>
            <h3 className="text-lg font-semibold">Total Amount</h3>
            <p className="text-2xl font-bold text-green-600">
              ${(analysis.summary.total_amount / 1000000).toFixed(1)}M
            </p>
          </div>
          <div className={`${isDarkMode ? 'bg-slate-800' : 'bg-white'} p-4 rounded-lg shadow-md`}>
            <h3 className="text-lg font-semibold">Representatives</h3>
            <p className="text-2xl font-bold text-purple-600">{analysis.summary.unique_representatives}</p>
          </div>
          <div className={`${isDarkMode ? 'bg-slate-800' : 'bg-white'} p-4 rounded-lg shadow-md`}>
            <h3 className="text-lg font-semibold">Recent (7d)</h3>
            <p className="text-2xl font-bold text-orange-600">{analysis.summary.recent_trades}</p>
          </div>
        </div>
      )}

      {/* Congressional Trades Table */}
      <div className={`${isDarkMode ? 'bg-slate-800' : 'bg-white'} rounded-lg shadow-md overflow-hidden`}>
        <h3 className="text-lg font-semibold p-4 border-b border-gray-200">Recent Congressional Activity</h3>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className={`${isDarkMode ? 'bg-slate-700' : 'bg-gray-50'}`}>
              <tr>
                <th className="px-4 py-3 text-left">Representative</th>
                <th className="px-4 py-3 text-left">Party</th>
                <th className="px-4 py-3 text-left">Ticker</th>
                <th className="px-4 py-3 text-left">Type</th>
                <th className="px-4 py-3 text-left">Amount</th>
                <th className="px-4 py-3 text-left">Date</th>
                <th className="px-4 py-3 text-left">Sector</th>
              </tr>
            </thead>
            <tbody>
              {congressionalData.slice(0, 20).map((trade, index) => (
                <tr key={index} className={`border-b ${isDarkMode ? 'border-slate-600' : 'border-gray-100'} hover:${isDarkMode ? 'bg-slate-700' : 'bg-gray-50'}`}>
                  <td className="px-4 py-3 font-medium">{trade.representative}</td>
                  <td className="px-4 py-3">
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getPartyColor(trade.party)}`}>
                      {trade.party}
                    </span>
                  </td>
                  <td className="px-4 py-3 font-semibold">{trade.ticker}</td>
                  <td className={`px-4 py-3 font-medium ${getTransactionColor(trade.transaction_type)}`}>
                    {trade.transaction_type}
                  </td>
                  <td className="px-4 py-3">${trade.transaction_amount?.toLocaleString()}</td>
                  <td className="px-4 py-3 text-sm">{trade.transaction_date}</td>
                  <td className="px-4 py-3 text-sm">{trade.sector}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

// Trading Strategies Component
const TradingStrategies = () => {
  const [strategies, setStrategies] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showAdvancedModal, setShowAdvancedModal] = useState(false);
  const [selectedStrategy, setSelectedStrategy] = useState(null);

  // Auto Trading States
  const [autoTradingConfig, setAutoTradingConfig] = useState({
    enabled: false,
    budget: 10000,
    maxDailyLoss: 500,
    maxPositionSize: 1000,
    riskPerTrade: 2, // percentage
    strategies: ['long_call', 'long_put', 'bull_call_spread']
  });
  
  const [tradingHistory, setTradingHistory] = useState([]);
  const [activeTrades, setActiveTrades] = useState([]);
  const [portfolioStats, setPortfolioStats] = useState({
    totalValue: 10000,
    totalPnL: 0,
    todayPnL: 0,
    winRate: 0,
    totalTrades: 0,
    activePositions: 0
  });
  const { isDarkMode } = useTheme();

  // Load Plotly dynamically
  useEffect(() => {
    if (!window.Plotly) {
      const script = document.createElement('script');
      script.src = 'https://cdn.plot.ly/plotly-latest.min.js';
      script.async = true;
      document.head.appendChild(script);
      
      script.onload = () => {
        console.log('Plotly loaded successfully');
      };
    }
  }, []);

  useEffect(() => {
    fetchTradingStrategies();
  }, []);

  const fetchTradingStrategies = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API}/unusual-whales/trading-strategies`);
      
      if (response.data.status === 'success') {
        setStrategies(response.data.trading_strategies || []);
        
        // Render charts after strategies are loaded
        setTimeout(() => {
          renderCharts(response.data.trading_strategies || []);
        }, 500);
      }
    } catch (error) {
      console.error('Error fetching trading strategies:', error);
    } finally {
      setLoading(false);
    }
  };

  const renderCharts = (strategiesData) => {
    strategiesData.forEach((strategy, index) => {
      if (strategy.chart && strategy.chart.plotly_chart && window.Plotly) {
        try {
          const chartData = JSON.parse(strategy.chart.plotly_chart);
          const chartDiv = document.getElementById(`strategy-chart-${index}`);
          
          if (chartDiv && chartData) {
            // Configure chart for dark/light mode
            const config = {
              displayModeBar: false,
              responsive: true,
              displaylogo: false
            };
            
            // Update layout for theme
            if (chartData.layout) {
              chartData.layout.paper_bgcolor = isDarkMode ? '#1e293b' : '#ffffff';
              chartData.layout.plot_bgcolor = isDarkMode ? '#1e293b' : '#ffffff';
              chartData.layout.font = {
                color: isDarkMode ? '#ffffff' : '#000000'
              };
            }
            
            window.Plotly.newPlot(chartDiv, chartData.data, chartData.layout, config);
          }
        } catch (error) {
          console.error('Error rendering chart:', error);
        }
      }
    });
  };

  const openAdvancedOptionsModal = (strategy) => {
    setSelectedStrategy(strategy);
    setShowAdvancedModal(true);
  };

  const getConfidenceColor = (confidence) => {
    if (confidence >= 0.7) return 'bg-green-100 text-green-800';
    if (confidence >= 0.5) return 'bg-yellow-100 text-yellow-800';
    return 'bg-red-100 text-red-800';
  };

  const getStrategyTypeColor = (type) => {
    switch (type) {
      case 'vertical_spread': return 'bg-purple-100 text-purple-800';
      case 'directional': return 'bg-blue-100 text-blue-800';
      case 'volatility': return 'bg-pink-100 text-pink-800';
      case 'income': return 'bg-green-100 text-green-800';
      case 'policy_play': return 'bg-red-100 text-red-800';
      case 'income_generation': return 'bg-teal-100 text-teal-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getChartTypeIcon = (chartType) => {
    switch (chartType) {
      case 'vertical_spread': return '📊';
      case 'directional': return '📈';
      case 'volatility': return '⚡';
      case 'iron_condor': return '🦅';
      case 'income': return '💰';
      default: return '📉';
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className={`space-y-6 ${isDarkMode ? 'text-white' : 'text-gray-800'}`}>
      <div className="flex justify-between items-center">
        <h2 className="text-2xl md:text-3xl font-bold">
          🎯 AI Trading Strategies
        </h2>
        <button
          onClick={fetchTradingStrategies}
          className="flex items-center space-x-2 bg-green-500 hover:bg-green-600 text-white px-4 py-2 rounded-lg transition-colors"
        >
          <RefreshCw className="w-4 h-4" />
          <span>Refresh</span>
        </button>
      </div>

      <div className={`${isDarkMode ? 'bg-slate-800' : 'bg-white'} p-4 rounded-lg shadow-md`}>
        <div className="flex items-center space-x-2 mb-4">
          <Target className="w-5 h-5 text-green-500" />
          <h3 className="text-lg font-semibold">TradeStation Ready Strategies with Interactive Charts</h3>
        </div>
        <p className={`text-sm ${isDarkMode ? 'text-gray-300' : 'text-gray-600'}`}>
          These strategies include visual P&L diagrams and are designed for direct execution on TradeStation.
        </p>
      </div>

      {/* Strategies */}
      <div className="space-y-6">
        {strategies.map((strategy, index) => (
          <div key={index} className={`${isDarkMode ? 'bg-slate-800' : 'bg-white'} p-6 rounded-lg shadow-md border-l-4 ${
            strategy.confidence >= 0.7 ? 'border-green-500' : 
            strategy.confidence >= 0.5 ? 'border-yellow-500' : 'border-red-500'
          }`}>
            <div className="flex justify-between items-start mb-4">
              <div>
                <h3 className="text-xl font-bold flex items-center space-x-2">
                  <span>{getChartTypeIcon(strategy.chart?.chart_type)}</span>
                  <span>{strategy.strategy_name}</span>
                </h3>
                <p className="text-lg font-semibold text-blue-600">{strategy.ticker}</p>
              </div>
              <div className="text-right">
                <span className={`px-3 py-1 rounded-full text-sm font-medium ${getConfidenceColor(strategy.confidence)}`}>
                  {(strategy.confidence * 100).toFixed(0)}% Confidence
                </span>
                <br />
                <span className={`mt-2 inline-block px-3 py-1 rounded-full text-sm font-medium ${getStrategyTypeColor(strategy.strategy_type)}`}>
                  {strategy.strategy_type}
                </span>
              </div>
            </div>

            {/* Interactive P&L Chart */}
            {strategy.chart && strategy.chart.plotly_chart && (
              <div className={`mb-6 ${isDarkMode ? 'bg-slate-700' : 'bg-gray-50'} p-4 rounded-lg`}>
                <h4 className="font-semibold mb-3 flex items-center space-x-2">
                  <BarChart3 className="w-4 h-4" />
                  <span>Profit/Loss Diagram</span>
                </h4>
                <div 
                  id={`strategy-chart-${index}`} 
                  className="w-full"
                  style={{ height: '400px' }}
                ></div>
                
                {/* Chart Key Metrics */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mt-4">
                  {strategy.chart.max_profit && (
                    <div className={`${isDarkMode ? 'bg-slate-600' : 'bg-green-50'} p-2 rounded text-center`}>
                      <p className="text-xs text-green-600 font-medium">Max Profit</p>
                      <p className="text-sm font-bold">${strategy.chart.max_profit.toFixed(0)}</p>
                    </div>
                  )}
                  {strategy.chart.max_loss && (
                    <div className={`${isDarkMode ? 'bg-slate-600' : 'bg-red-50'} p-2 rounded text-center`}>
                      <p className="text-xs text-red-600 font-medium">Max Loss</p>
                      <p className="text-sm font-bold">${strategy.chart.max_loss.toFixed(0)}</p>
                    </div>
                  )}
                  {strategy.chart.breakeven && (
                    <div className={`${isDarkMode ? 'bg-slate-600' : 'bg-yellow-50'} p-2 rounded text-center`}>
                      <p className="text-xs text-yellow-600 font-medium">Breakeven</p>
                      <p className="text-sm font-bold">${strategy.chart.breakeven.toFixed(2)}</p>
                    </div>
                  )}
                  {strategy.chart.breakeven_points && strategy.chart.breakeven_points.length > 1 && (
                    <div className={`${isDarkMode ? 'bg-slate-600' : 'bg-yellow-50'} p-2 rounded text-center`}>
                      <p className="text-xs text-yellow-600 font-medium">Breakevens</p>
                      <p className="text-sm font-bold">{strategy.chart.breakeven_points.length}</p>
                    </div>
                  )}
                </div>
              </div>
            )}

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h4 className="font-semibold mb-2">Entry Logic</h4>
                <div className={`${isDarkMode ? 'bg-slate-700' : 'bg-gray-50'} p-3 rounded text-sm`}>
                  <p>{strategy.entry_logic.condition}</p>
                  {strategy.entry_logic.premium_threshold && (
                    <p className="mt-1">Premium: ${(strategy.entry_logic.premium_threshold / 1000).toFixed(0)}K</p>
                  )}
                  {strategy.entry_logic.sentiment && (
                    <p className="mt-1">Sentiment: <span className="capitalize">{strategy.entry_logic.sentiment}</span></p>
                  )}
                  {strategy.entry_logic.underlying_price && (
                    <p className="mt-1">Underlying: ${strategy.entry_logic.underlying_price.toFixed(2)}</p>
                  )}
                </div>
              </div>

              <div>
                <h4 className="font-semibold mb-2">TradeStation Execution</h4>
                <div className={`${isDarkMode ? 'bg-slate-700' : 'bg-gray-50'} p-3 rounded text-sm`}>
                  <p><strong>Strategy:</strong> {strategy.tradestation_execution.strategy_type || strategy.tradestation_execution.instrument_type}</p>
                  {strategy.tradestation_execution.legs && strategy.tradestation_execution.legs.length > 0 && (
                    <div className="mt-2">
                      <strong>Legs:</strong>
                      {strategy.tradestation_execution.legs.map((leg, idx) => (
                        <div key={idx} className="ml-2 text-xs">
                          {leg.action} {leg.option_type} @ ${leg.strike} ({leg.quantity}x)
                        </div>
                      ))}
                    </div>
                  )}
                  <p><strong>Max Risk:</strong> {strategy.tradestation_execution.max_risk}</p>
                  <p><strong>Max Profit:</strong> {strategy.tradestation_execution.max_profit}</p>
                </div>
              </div>

              <div>
                <h4 className="font-semibold mb-2">Risk Management</h4>
                <div className={`${isDarkMode ? 'bg-slate-700' : 'bg-gray-50'} p-3 rounded text-sm`}>
                  <p><strong>Max Position:</strong> {strategy.risk_management.max_position_size}</p>
                  <p><strong>Stop Loss:</strong> {strategy.risk_management.stop_loss_percentage}%</p>
                  {strategy.risk_management.trailing_stop && <p><strong>Trailing Stop:</strong> Enabled</p>}
                  {strategy.risk_management.time_stop && <p><strong>Time Stop:</strong> {strategy.risk_management.time_stop}</p>}
                </div>
              </div>

              <div>
                <h4 className="font-semibold mb-2">Timeframe & Details</h4>
                <div className={`${isDarkMode ? 'bg-slate-700' : 'bg-gray-50'} p-3 rounded text-sm`}>
                  <p><strong>Timeframe:</strong> {strategy.timeframe}</p>
                  {strategy.entry_logic.dte && <p><strong>DTE:</strong> {strategy.entry_logic.dte}</p>}
                  {strategy.entry_logic.sector && <p><strong>Sector:</strong> {strategy.entry_logic.sector}</p>}
                  {strategy.entry_logic.volume && <p><strong>Volume:</strong> {strategy.entry_logic.volume.toLocaleString()}</p>}
                </div>
              </div>
            </div>

            <div className="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded">
              <p className="text-sm text-yellow-800">
                <strong>Disclaimer:</strong> Strategy generated from unusual market activity patterns. 
                Charts show theoretical P&L at expiration. Always perform your own due diligence and risk assessment before executing trades.
              </p>
            </div>
            
            {/* Trade Execution Button */}
            <div className="mt-4 flex justify-center">
              <button
                onClick={() => openAdvancedOptionsModal(strategy)}
                className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-semibold flex items-center space-x-2 transition-colors"
              >
                <TrendingUp className="w-5 h-5" />
                <span>Execute Strategy</span>
              </button>
            </div>
          </div>
        ))}
      </div>

      {strategies.length === 0 && (
        <div className={`${isDarkMode ? 'bg-slate-800' : 'bg-white'} p-6 rounded-lg shadow-md text-center`}>
          <Target className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-600">No trading strategies available at the moment.</p>
          <p className="text-sm text-gray-500 mt-2">Strategies are generated based on unusual market activity.</p>
        </div>
      )}

      {/* Advanced Options Trading Modal */}
      {showAdvancedModal && selectedStrategy && (
        <AdvancedOptionsModal
          strategy={selectedStrategy}
          isOpen={showAdvancedModal}
          onClose={() => {
            setShowAdvancedModal(false);
            setSelectedStrategy(null);
          }}
          isDarkMode={isDarkMode}
        />
      )}
    </div>
  );
};

// Advanced Options Trading Modal Component  
const AdvancedOptionsModal = ({ strategy, isOpen, onClose, isDarkMode }) => {
  const [activeTab, setActiveTab] = useState('expirations');
  const [selectedExpiration, setSelectedExpiration] = useState('');
  const [selectedStrike, setSelectedStrike] = useState('');
  const [quantity, setQuantity] = useState(1);
  const [optionsChain, setOptionsChain] = useState([]);
  const [underlyingData, setUnderlyingData] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (isOpen && strategy) {
      fetchUnderlyingData();
      generateMockOptionsChain();
    }
  }, [isOpen, strategy]);

  const fetchUnderlyingData = async () => {
    setLoading(true);
    try {
      const mockData = {
        symbol: strategy.ticker,
        price: strategy.entry_logic?.underlying_price || 100,
        change: 0.35,
        changePercent: 1.12,
        company: getCompanyName(strategy.ticker),
        earnings: '63d'
      };
      setUnderlyingData(mockData);
    } catch (error) {
      console.error('Error fetching underlying data:', error);
    } finally {
      setLoading(false);
    }
  };

  const generateMockOptionsChain = () => {
    const currentPrice = strategy.entry_logic?.underlying_price || 100;
    
    const expirations = [
      { date: 'Aug 15', dte: 2, type: 'Standard' },
      { date: 'Aug 22', dte: 9, type: 'Weeklys' },
      { date: 'Aug 29', dte: 16, type: 'EoM' },
      { date: 'Sep 5', dte: 23, type: 'Weeklys' },
      { date: 'Sep 12', dte: 30, type: 'Weeklys' }
    ];

    const mockChain = expirations.map(exp => ({
      expiration: exp.date,
      dte: exp.dte,
      type: exp.type,
      strikes: generateStrikesForExpiration(currentPrice, exp.dte)
    }));

    setOptionsChain(mockChain);
  };

  const generateStrikesForExpiration = (currentPrice, dte) => {
    const strikes = [];
    const priceStep = currentPrice > 100 ? 5 : 2.5;
    
    for (let i = -10; i <= 10; i++) {
      const strikePrice = currentPrice + (i * priceStep);
      
      const call = {
        strike: strikePrice.toFixed(2),
        type: 'call',
        bid: (Math.max(0, currentPrice - strikePrice) + Math.random() * 2).toFixed(2),
        ask: (Math.max(0, currentPrice - strikePrice) + 0.5 + Math.random() * 2).toFixed(2),
        last: (Math.max(0, currentPrice - strikePrice) + 0.25 + Math.random() * 2).toFixed(2),
        volume: Math.floor(Math.random() * 500),
        oi: Math.floor(Math.random() * 2000),
        iv: (50 + Math.random() * 20).toFixed(1)
      };

      const put = {
        strike: strikePrice.toFixed(2),
        type: 'put',
        bid: (Math.max(0, strikePrice - currentPrice) + Math.random() * 2).toFixed(2),
        ask: (Math.max(0, strikePrice - currentPrice) + 0.5 + Math.random() * 2).toFixed(2),
        last: (Math.max(0, strikePrice - currentPrice) + 0.25 + Math.random() * 2).toFixed(2),
        volume: Math.floor(Math.random() * 300),
        oi: Math.floor(Math.random() * 1500),
        iv: (50 + Math.random() * 15).toFixed(1)
      };

      strikes.push({ strike: strikePrice, call, put });
    }
    
    return strikes;
  };

  const getCompanyName = (ticker) => {
    const companies = {
      'AAPL': 'Apple Inc',
      'MSFT': 'Microsoft Corp', 
      'GOOGL': 'Alphabet Inc',
      'TSLA': 'Tesla Inc',
      'NVDA': 'NVIDIA Corp',
      'META': 'Meta Platforms',
      'AMZN': 'Amazon.com Inc'
    };
    return companies[ticker] || `${ticker} Corp`;
  };

  const handleTradeClick = (expiration, strike, optionType) => {
    setSelectedExpiration(expiration.expiration);
    setSelectedStrike(strike.strike);
    // You could open another modal or navigate to order entry here
    alert(`Selected: ${strategy.ticker} ${strike.strike}${optionType.toUpperCase()} ${expiration.expiration}`);
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className={`${isDarkMode ? 'bg-slate-800 text-white' : 'bg-white text-gray-900'} rounded-lg shadow-xl max-w-6xl w-full max-h-[90vh] overflow-hidden flex flex-col`}>
        {/* Modal Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center text-white font-bold">
                {underlyingData?.symbol?.charAt(0) || strategy.ticker.charAt(0)}
              </div>
              <div>
                <h2 className="text-xl font-bold">{underlyingData?.symbol || strategy.ticker}</h2>
                <p className="text-sm text-gray-500">{underlyingData?.company}</p>
              </div>
            </div>
            <div className="flex items-center space-x-4 ml-6">
              <div className={`text-lg font-bold ${underlyingData?.change >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                ${underlyingData?.price?.toFixed(2) || '0.00'}
              </div>
              <div className={`text-sm ${underlyingData?.change >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                {underlyingData?.change >= 0 ? '+' : ''}{underlyingData?.change?.toFixed(2) || '0.00'} ({underlyingData?.changePercent?.toFixed(2) || '0.00'}%)
              </div>
            </div>
          </div>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Modal Body */}
        <div className="flex-1 flex overflow-hidden">
          {/* Left Panel - Options Chain */}
          <div className="flex-1 p-6 overflow-y-auto">
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold">Options Chain</h3>
                <div className="flex items-center space-x-2">
                  <select className="px-3 py-1 border border-gray-300 rounded text-sm">
                    <option>All Strikes</option>
                    <option>ITM Only</option>
                    <option>OTM Only</option>
                  </select>
                  <button className="px-3 py-1 bg-blue-600 text-white rounded text-sm">
                    Refresh
                  </button>
                </div>
              </div>

              {/* Options Chain Table */}
              {optionsChain.length > 0 && (
                <div className="space-y-4">
                  {optionsChain.map((exp, index) => (
                    <div key={index} className="border rounded-lg overflow-hidden">
                      <div className={`${isDarkMode ? 'bg-slate-700' : 'bg-gray-50'} px-4 py-2 border-b`}>
                        <div className="flex items-center justify-between">
                          <h4 className="font-semibold">{exp.expiration}</h4>
                          <div className="flex items-center space-x-4 text-sm text-gray-500">
                            <span>{exp.dte} DTE</span>
                            <span>{exp.type}</span>
                          </div>
                        </div>
                      </div>
                      
                      <div className="overflow-x-auto">
                        <table className="w-full text-sm">
                          <thead className={`${isDarkMode ? 'bg-slate-600' : 'bg-gray-100'}`}>
                            <tr>
                              <th className="px-3 py-2 text-left">Calls</th>
                              <th className="px-3 py-2 text-center">Strike</th>
                              <th className="px-3 py-2 text-right">Puts</th>
                              <th className="px-3 py-2 text-center">Action</th>
                            </tr>
                          </thead>
                          <tbody className="divide-y divide-gray-200">
                            {exp.strikes && exp.strikes.slice(0, 5).map((strike, strikeIndex) => (
                              <tr key={strikeIndex} className="hover:bg-blue-50">
                                <td className="px-3 py-2">
                                  <div className="text-xs space-y-1">
                                    <div>Bid/Ask: {strike.call.bid}/{strike.call.ask}</div>
                                    <div>Vol: {strike.call.volume} | OI: {strike.call.oi}</div>
                                    <div>IV: {strike.call.iv}%</div>
                                  </div>
                                </td>
                                <td className="px-3 py-2 text-center font-bold">
                                  ${strike.strike.toFixed(2)}
                                </td>
                                <td className="px-3 py-2 text-right">
                                  <div className="text-xs space-y-1">
                                    <div>Bid/Ask: {strike.put.bid}/{strike.put.ask}</div>
                                    <div>Vol: {strike.put.volume} | OI: {strike.put.oi}</div>
                                    <div>IV: {strike.put.iv}%</div>
                                  </div>
                                </td>
                                <td className="px-3 py-2 text-center">
                                  <button 
                                    onClick={() => handleTradeClick(exp, strike, 'call')}
                                    className="px-2 py-1 bg-green-600 text-white rounded text-xs hover:bg-green-700"
                                  >
                                    Trade →
                                  </button>
                                </td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Right Panel - Strategy Details */}
          <div className="w-1/3 p-6">
            <div className="space-y-4">
              <div>
                <h3 className="font-semibold mb-2">Strategy Overview</h3>
                <div className={`${isDarkMode ? 'bg-slate-700' : 'bg-gray-50'} p-3 rounded text-sm space-y-2`}>
                  <p><strong>Type:</strong> {strategy.strategy_type}</p>
                  <p><strong>Timeframe:</strong> {strategy.timeframe}</p>
                  <p><strong>Confidence:</strong> {(strategy.confidence * 100).toFixed(0)}%</p>
                </div>
              </div>

              <div>
                <h3 className="font-semibold mb-2">Entry Conditions</h3>
                <div className={`${isDarkMode ? 'bg-slate-700' : 'bg-gray-50'} p-3 rounded text-sm`}>
                  <p>{strategy.entry_logic?.condition || 'Strategy-based entry'}</p>
                  {strategy.entry_logic?.sentiment && (
                    <p className="mt-1">Market Bias: <span className="capitalize font-medium">{strategy.entry_logic.sentiment}</span></p>
                  )}
                </div>
              </div>

              <div>
                <h3 className="font-semibold mb-2">Risk Management</h3>
                <div className={`${isDarkMode ? 'bg-slate-700' : 'bg-gray-50'} p-3 rounded text-sm space-y-1`}>
                  <p><strong>Max Position:</strong> {strategy.risk_management?.max_position_size || '2% of portfolio'}</p>
                  <p><strong>Stop Loss:</strong> {strategy.risk_management?.stop_loss_percentage || '10'}%</p>
                  {strategy.chart && (
                    <>
                      {strategy.chart.max_profit && <p><strong>Max Profit:</strong> ${strategy.chart.max_profit.toFixed(0)}</p>}
                      {strategy.chart.max_loss && <p><strong>Max Loss:</strong> ${strategy.chart.max_loss.toFixed(0)}</p>}
                    </>
                  )}
                </div>
              </div>

              <div className="pt-4 border-t">
                <button className="w-full bg-blue-600 hover:bg-blue-700 text-white py-3 px-4 rounded-lg font-semibold">
                  Execute Full Strategy
                </button>
                <p className="text-xs text-gray-500 mt-2 text-center">
                  Based on Unusual Whales data analysis
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

// ==================== AUTO TRADING COMPONENTS ====================

const AutoOptionsTrading = () => {
  const { isDarkMode } = useTheme();
  const [config, setConfig] = useState({
    enabled: false,
    budget: 10000,
    maxDailyLoss: 500,
    maxPositionSize: 1000,
    riskPerTrade: 2,
    strategies: ['wheel', 'iron_condor', 'volatility_play'],
    symbols: ['SPY', 'QQQ', 'AAPL', 'MSFT']
  });

  const [stats, setStats] = useState({
    totalValue: 10000,
    availableCash: 10000,
    totalPnL: 0,
    todayPnL: 0,
    activePositions: 0,
    todayTrades: 0
  });

  const [expertRecommendations, setExpertRecommendations] = useState([]);
  const [learningInsights, setLearningInsights] = useState(null);
  const [loading, setLoading] = useState(false);
  const [selectedSymbol, setSelectedSymbol] = useState('SPY');
  const [showOptionsDropdown, setShowOptionsDropdown] = useState(false);

  const [activeTrades, setActiveTrades] = useState([
    {
      id: 1,
      symbol: 'SPY',
      strategy: 'Wheel Strategy',
      entry_price: 2.50,
      current_price: 3.20,
      quantity: 5,
      pnl: 350,
      pnl_percent: 28.0,
      entry_time: '2024-08-14 09:30:00',
      expiration: '2024-08-21',
      strike: 645,
      confidence_score: 0.85
    },
    {
      id: 2,
      symbol: 'QQQ',
      strategy: 'Iron Condor',
      entry_price: 1.80,
      current_price: 1.65,
      quantity: 3,
      pnl: -45,
      pnl_percent: -8.3,
      entry_time: '2024-08-14 10:15:00',
      expiration: '2024-08-16',
      strike: '580/585',
      confidence_score: 0.72
    }
  ]);

  // Fetch expert recommendations
  const fetchExpertRecommendations = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API}/expert-options/strategies/${selectedSymbol}`);
      setExpertRecommendations(response.data.recommendations || []);
    } catch (error) {
      console.error('Error fetching expert recommendations:', error);
    } finally {
      setLoading(false);
    }
  };

  // Fetch learning insights
  const fetchLearningInsights = async () => {
    try {
      const response = await axios.get(`${API}/expert-options/learning/insights`);
      setLearningInsights(response.data.learning_insights || {});
    } catch (error) {
      console.error('Error fetching learning insights:', error);
    }
  };

  // Optimize strategy parameters
  const optimizeStrategy = async (strategyType) => {
    try {
      const response = await axios.post(`${API}/expert-options/optimize/${strategyType}`);
      console.log('Optimization completed:', response.data);
      // Refresh insights after optimization
      await fetchLearningInsights();
    } catch (error) {
      console.error('Error optimizing strategy:', error);
    }
  };

  useEffect(() => {
    fetchExpertRecommendations();
    fetchLearningInsights();
  }, [selectedSymbol]);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (showOptionsDropdown && !event.target.closest('.relative')) {
        setShowOptionsDropdown(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [showOptionsDropdown]);

  const handleConfigChange = (field, value) => {
    setConfig(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const toggleAutoTrading = () => {
    setConfig(prev => ({
      ...prev,
      enabled: !prev.enabled
    }));
  };

  const getStrategyColor = (strategyType) => {
    switch (strategyType?.toLowerCase()) {
      case 'wheel': return 'bg-blue-100 text-blue-700 border-blue-300';
      case 'iron_condor': return 'bg-purple-100 text-purple-700 border-purple-300';
      case 'volatility_play': return 'bg-green-100 text-green-700 border-green-300';
      default: return 'bg-gray-100 text-gray-700 border-gray-300';
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold text-gray-800">🤖 Expert Auto Options Trading</h2>
          <p className="text-gray-600">AI-powered options trading with machine learning optimization</p>
        </div>
        <div className="flex items-center space-x-3">
          <div className="text-sm text-gray-500">AI Trading Status</div>
          <div className={`text-lg font-semibold ${config.enabled ? 'text-green-600' : 'text-gray-500'}`}>
            {config.enabled ? '🟢 LEARNING & ACTIVE' : '🔴 INACTIVE'}
          </div>
          
          {/* Options Dropdown */}
          <div className="relative">
            <button
              onClick={() => setShowOptionsDropdown(!showOptionsDropdown)}
              className="flex items-center space-x-2 bg-gradient-to-r from-purple-600 to-blue-600 text-white px-4 py-2 rounded-lg hover:from-purple-700 hover:to-blue-700 transition-all duration-200 shadow-lg"
            >
              <Settings size={16} />
              <span className="font-medium">Options</span>
              <ChevronDown className={`w-4 h-4 transition-transform duration-200 ${showOptionsDropdown ? 'rotate-180' : ''}`} />
            </button>

            {/* Dropdown Menu */}
            {showOptionsDropdown && (
              <div className="absolute right-0 mt-2 w-64 bg-white rounded-lg shadow-xl border border-gray-200 z-50 overflow-hidden">
                {/* Header */}
                <div className="bg-gradient-to-r from-purple-600 to-blue-600 px-4 py-3">
                  <h3 className="text-white font-semibold">Trading Options</h3>
                  <p className="text-purple-100 text-sm">Configure your automated trading</p>
                </div>
                
                {/* Menu Items */}
                <div className="py-2">
                  <button className="w-full px-4 py-2 text-left hover:bg-gray-50 flex items-center space-x-3 text-gray-700">
                    <Zap className="w-4 h-4 text-yellow-500" />
                    <span>Strategy Settings</span>
                  </button>
                  
                  <button className="w-full px-4 py-2 text-left hover:bg-gray-50 flex items-center space-x-3 text-gray-700">
                    <Target className="w-4 h-4 text-blue-500" />
                    <span>Risk Management</span>
                  </button>
                  
                  <button className="w-full px-4 py-2 text-left hover:bg-gray-50 flex items-center space-x-3 text-gray-700">
                    <BarChart3 className="w-4 h-4 text-green-500" />
                    <span>Performance Analytics</span>
                  </button>
                  
                  <button className="w-full px-4 py-2 text-left hover:bg-gray-50 flex items-center space-x-3 text-gray-700">
                    <Bot className="w-4 h-4 text-purple-500" />
                    <span>AI Learning Config</span>
                  </button>
                  
                  <hr className="my-2" />
                  
                  <button className="w-full px-4 py-2 text-left hover:bg-gray-50 flex items-center space-x-3 text-gray-700">
                    <Info className="w-4 h-4 text-gray-500" />
                    <span>Help & Documentation</span>
                  </button>
                  
                  <button className="w-full px-4 py-2 text-left hover:bg-red-50 flex items-center space-x-3 text-red-600">
                    <MoreVertical className="w-4 h-4" />
                    <span>Advanced Settings</span>
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Expert Strategy Recommendations */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-xl font-semibold flex items-center">
            <Target className="mr-2" size={20} />
            AI Expert Recommendations
          </h3>
          <div className="flex items-center space-x-4">
            <select
              value={selectedSymbol}
              onChange={(e) => setSelectedSymbol(e.target.value)}
              className="border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="SPY">SPY</option>
              <option value="QQQ">QQQ</option>
              <option value="AAPL">AAPL</option>
              <option value="MSFT">MSFT</option>
            </select>
            <button
              onClick={fetchExpertRecommendations}
              disabled={loading}
              className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 flex items-center disabled:opacity-50"
            >
              <RefreshCw className={`mr-2 ${loading ? 'animate-spin' : ''}`} size={16} />
              {loading ? 'Analyzing...' : 'Get AI Recommendations'}
            </button>
          </div>
        </div>

        {loading ? (
          <div className="text-center py-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
            <p className="mt-2 text-gray-600">AI analyzing market conditions...</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {expertRecommendations.map((recommendation, index) => (
              <div key={index} className={`border-2 rounded-lg p-4 ${getStrategyColor(recommendation.strategy_type)}`}>
                <div className="flex items-center justify-between mb-3">
                  <h4 className="font-semibold">{recommendation.strategy_name || recommendation.strategy_type}</h4>
                  <div className="flex items-center">
                    <div className="text-xs bg-white px-2 py-1 rounded-full">
                      Confidence: {(recommendation.confidence_score * 100).toFixed(0)}%
                    </div>
                  </div>
                </div>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span>Max Profit:</span>
                    <span className="font-medium text-green-600">
                      {recommendation.max_profit === "Unlimited" ? "Unlimited" : `$${recommendation.max_profit}`}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span>Max Risk:</span>
                    <span className="font-medium text-red-600">
                      ${recommendation.max_loss || recommendation.total_cost || 'N/A'}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span>Strategy Type:</span>
                    <span className="font-medium capitalize">{recommendation.strategy_type?.replace('_', ' ')}</span>
                  </div>
                  {recommendation.roi_potential && (
                    <div className="flex justify-between">
                      <span>ROI Potential:</span>
                      <span className="font-medium text-blue-600">{recommendation.roi_potential}%</span>
                    </div>
                  )}
                </div>
                <button className="w-full mt-3 bg-white/50 hover:bg-white/70 text-gray-800 py-2 px-3 rounded text-sm font-medium transition-colors">
                  Execute Strategy
                </button>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Learning Insights */}
      {learningInsights && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-xl font-semibold mb-4 flex items-center">
            <BarChart3 className="mr-2" size={20} />
            AI Learning Insights
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div>
              <h4 className="font-medium mb-2">System Performance</h4>
              <div className="space-y-1 text-sm">
                <div>Total Trades: <span className="font-semibold">{learningInsights.total_trades || 0}</span></div>
                <div>Active Trades: <span className="font-semibold">{learningInsights.active_trades || 0}</span></div>
                <div>Learning Status: <span className="font-semibold text-green-600">Active</span></div>
              </div>
            </div>
            <div>
              <h4 className="font-medium mb-2">Strategy Optimization</h4>
              <div className="space-y-2">
                {['wheel', 'iron_condor', 'volatility_play'].map(strategy => (
                  <button
                    key={strategy}
                    onClick={() => optimizeStrategy(strategy)}
                    className="w-full text-left bg-gray-50 hover:bg-gray-100 p-2 rounded text-sm"
                  >
                    Optimize {strategy.replace('_', ' ')} ⚡
                  </button>
                ))}
              </div>
            </div>
            <div>
              <h4 className="font-medium mb-2">Market Insights</h4>
              <div className="space-y-1 text-sm">
                <div>Preferred Strategy: <span className="font-semibold capitalize">{learningInsights.market_insights?.preferred_strategy || 'Learning'}</span></div>
                <div>Market Condition: <span className="font-semibold">{learningInsights.market_insights?.current_conditions || 'Neutral'}</span></div>
                <div>IV Environment: <span className="font-semibold">{learningInsights.market_insights?.iv_environment || 'Moderate'}</span></div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Control Panel */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-xl font-semibold">AI Trading Control</h3>
          <button
            onClick={toggleAutoTrading}
            className={`px-6 py-3 rounded-lg font-semibold text-white transition-colors ${
              config.enabled 
                ? 'bg-red-500 hover:bg-red-600' 
                : 'bg-green-500 hover:bg-green-600'
            }`}
          >
            {config.enabled ? 'Stop AI Trading' : 'Start AI Trading'}
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {/* Budget */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Total Budget
            </label>
            <div className="relative">
              <span className="absolute left-3 top-3 text-gray-500">$</span>
              <input
                type="number"
                value={config.budget}
                onChange={(e) => handleConfigChange('budget', Number(e.target.value))}
                className="w-full pl-8 pr-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                disabled={config.enabled}
              />
            </div>
          </div>

          {/* Max Daily Loss */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              AI Max Daily Loss
            </label>
            <div className="relative">
              <span className="absolute left-3 top-3 text-gray-500">$</span>
              <input
                type="number"
                value={config.maxDailyLoss}
                onChange={(e) => handleConfigChange('maxDailyLoss', Number(e.target.value))}
                className="w-full pl-8 pr-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                disabled={config.enabled}
              />
            </div>
          </div>

          {/* Risk Per Trade */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              AI Risk Per Trade (%)
            </label>
            <div className="relative">
              <input
                type="number"
                value={config.riskPerTrade}
                onChange={(e) => handleConfigChange('riskPerTrade', Number(e.target.value))}
                className="w-full pr-8 pl-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                disabled={config.enabled}
                step="0.1"
                min="0.1"
                max="10"
              />
              <span className="absolute right-3 top-3 text-gray-500">%</span>
            </div>
          </div>

          {/* Max Position Size */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Max Position Size
            </label>
            <div className="relative">
              <span className="absolute left-3 top-3 text-gray-500">$</span>
              <input
                type="number"
                value={config.maxPositionSize}
                onChange={(e) => handleConfigChange('maxPositionSize', Number(e.target.value))}
                className="w-full pl-8 pr-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                disabled={config.enabled}
              />
            </div>
          </div>
        </div>
      </div>

      {/* Portfolio Stats - Same as before */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-6 gap-4">
        <div className="bg-white rounded-lg shadow-md p-4">
          <div className="text-sm text-gray-500">Total Value</div>
          <div className="text-2xl font-bold text-gray-800">${stats.totalValue.toLocaleString()}</div>
        </div>
        <div className="bg-white rounded-lg shadow-md p-4">
          <div className="text-sm text-gray-500">Available Cash</div>
          <div className="text-2xl font-bold text-blue-600">${stats.availableCash.toLocaleString()}</div>
        </div>
        <div className="bg-white rounded-lg shadow-md p-4">
          <div className="text-sm text-gray-500">Total P&L</div>
          <div className={`text-2xl font-bold ${stats.totalPnL >= 0 ? 'text-green-600' : 'text-red-600'}`}>
            ${stats.totalPnL >= 0 ? '+' : ''}{stats.totalPnL.toLocaleString()}
          </div>
        </div>
        <div className="bg-white rounded-lg shadow-md p-4">
          <div className="text-sm text-gray-500">Today's P&L</div>
          <div className={`text-2xl font-bold ${stats.todayPnL >= 0 ? 'text-green-600' : 'text-red-600'}`}>
            ${stats.todayPnL >= 0 ? '+' : ''}{stats.todayPnL.toLocaleString()}
          </div>
        </div>
        <div className="bg-white rounded-lg shadow-md p-4">
          <div className="text-sm text-gray-500">Active Positions</div>
          <div className="text-2xl font-bold text-purple-600">{stats.activePositions}</div>
        </div>
        <div className="bg-white rounded-lg shadow-md p-4">
          <div className="text-sm text-gray-500">Today's Trades</div>
          <div className="text-2xl font-bold text-orange-600">{stats.todayTrades}</div>
        </div>
      </div>

      {/* Active Trades with AI Confidence Scores */}
      <div className="bg-white rounded-lg shadow-md">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-semibold flex items-center">
            <Activity className="mr-2" size={20} />
            AI-Managed Active Trades ({activeTrades.length})
          </h3>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Symbol</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">AI Strategy</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Strike/Exp</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Entry</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Current</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">P&L</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">AI Confidence</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {activeTrades.map((trade) => (
                <tr key={trade.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 font-semibold text-blue-600">{trade.symbol}</td>
                  <td className="px-6 py-4 text-sm">
                    <div className="font-medium">{trade.strategy}</div>
                    <div className="text-xs text-gray-500">AI Selected</div>
                  </td>
                  <td className="px-6 py-4 text-sm">
                    <div>${trade.strike}</div>
                    <div className="text-gray-500">{trade.expiration}</div>
                  </td>
                  <td className="px-6 py-4 text-sm">
                    <div>${trade.entry_price}</div>
                    <div className="text-gray-500">x{trade.quantity}</div>
                  </td>
                  <td className="px-6 py-4 text-sm font-medium">${trade.current_price}</td>
                  <td className="px-6 py-4">
                    <div className={`font-semibold ${trade.pnl >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                      ${trade.pnl >= 0 ? '+' : ''}{trade.pnl}
                    </div>
                    <div className={`text-sm ${trade.pnl_percent >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                      ({trade.pnl_percent >= 0 ? '+' : ''}{trade.pnl_percent}%)
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex items-center">
                      <div className={`text-sm font-medium ${
                        trade.confidence_score >= 0.8 ? 'text-green-600' :
                        trade.confidence_score >= 0.6 ? 'text-yellow-600' : 'text-red-600'
                      }`}>
                        {(trade.confidence_score * 100).toFixed(0)}%
                      </div>
                      <div className={`ml-1 w-2 h-2 rounded-full ${
                        trade.confidence_score >= 0.8 ? 'bg-green-500' :
                        trade.confidence_score >= 0.6 ? 'bg-yellow-500' : 'bg-red-500'
                      }`}></div>
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <button className="text-red-600 hover:text-red-800 font-medium text-sm">
                      Close Position
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Expert Strategy Configuration */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-lg font-semibold mb-4">AI Expert Strategies</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {[
            { id: 'wheel', name: 'Wheel Strategy', description: 'AI-optimized cash-secured puts → covered calls', icon: '♻️' },
            { id: 'iron_condor', name: 'Iron Condor', description: 'AI delta-neutral income strategy', icon: '🦅' },
            { id: 'volatility_play', name: 'Volatility Play', description: 'AI volatility expansion/contraction plays', icon: '⚡' }
          ].map((strategy) => (
            <div key={strategy.id} className="border rounded-lg p-4">
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center space-x-2">
                  <span className="text-lg">{strategy.icon}</span>
                  <div className="font-medium">{strategy.name}</div>
                </div>
                <input
                  type="checkbox"
                  checked={config.strategies.includes(strategy.id)}
                  onChange={(e) => {
                    if (e.target.checked) {
                      handleConfigChange('strategies', [...config.strategies, strategy.id]);
                    } else {
                      handleConfigChange('strategies', config.strategies.filter(s => s !== strategy.id));
                    }
                  }}
                  disabled={config.enabled}
                  className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                />
              </div>
              <div className="text-sm text-gray-600">{strategy.description}</div>
              <div className="mt-2 text-xs text-blue-600">AI-Powered with Machine Learning</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

const TradingHistory = () => {
  const { isDarkMode } = useTheme();
  const [trades, setTrades] = useState([
    {
      id: 1,
      date: '2024-08-14',
      symbol: 'SPY',
      strategy: 'Long Call',
      entry_price: 2.50,
      exit_price: 3.20,
      quantity: 5,
      pnl: 350,
      pnl_percent: 28.0,
      status: 'Closed',
      entry_time: '09:30:00',
      exit_time: '15:45:00',
      expiration: '2024-08-21',
      strike: 645
    },
    {
      id: 2,
      date: '2024-08-13',
      symbol: 'QQQ',
      strategy: 'Bull Call Spread',
      entry_price: 1.80,
      exit_price: 1.65,
      quantity: 3,
      pnl: -45,
      pnl_percent: -8.3,
      status: 'Closed',
      entry_time: '10:15:00',
      exit_time: '14:30:00',
      expiration: '2024-08-16',
      strike: '580/585'
    },
    {
      id: 3,
      date: '2024-08-12',
      symbol: 'AAPL',
      strategy: 'Long Put',
      entry_price: 3.10,
      exit_price: 4.25,
      quantity: 2,
      pnl: 230,
      pnl_percent: 37.1,
      status: 'Closed',
      entry_time: '11:00:00',
      exit_time: '13:20:00',
      expiration: '2024-08-19',
      strike: 220
    }
  ]);

  const [filter, setFilter] = useState('all');
  const [dateRange, setDateRange] = useState('7d');

  const filteredTrades = trades.filter(trade => {
    if (filter === 'all') return true;
    if (filter === 'profitable') return trade.pnl > 0;
    if (filter === 'losses') return trade.pnl < 0;
    return true;
  });

  const totalPnL = trades.reduce((sum, trade) => sum + trade.pnl, 0);
  const winRate = (trades.filter(trade => trade.pnl > 0).length / trades.length) * 100;
  const avgWin = trades.filter(trade => trade.pnl > 0).reduce((sum, trade) => sum + trade.pnl, 0) / trades.filter(trade => trade.pnl > 0).length;
  const avgLoss = Math.abs(trades.filter(trade => trade.pnl < 0).reduce((sum, trade) => sum + trade.pnl, 0) / trades.filter(trade => trade.pnl < 0).length);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold text-gray-800">📊 Trading History</h2>
          <p className="text-gray-600">Complete record of automated trading activity</p>
        </div>
        <div className="flex items-center space-x-4">
          <select 
            value={dateRange} 
            onChange={(e) => setDateRange(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          >
            <option value="7d">Last 7 Days</option>
            <option value="30d">Last 30 Days</option>
            <option value="90d">Last 90 Days</option>
            <option value="1y">Last Year</option>
          </select>
        </div>
      </div>

      {/* Summary Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg shadow-md p-4">
          <div className="text-sm text-gray-500">Total P&L</div>
          <div className={`text-2xl font-bold ${totalPnL >= 0 ? 'text-green-600' : 'text-red-600'}`}>
            ${totalPnL >= 0 ? '+' : ''}{totalPnL.toFixed(0)}
          </div>
        </div>
        <div className="bg-white rounded-lg shadow-md p-4">
          <div className="text-sm text-gray-500">Win Rate</div>
          <div className="text-2xl font-bold text-blue-600">{winRate.toFixed(1)}%</div>
        </div>
        <div className="bg-white rounded-lg shadow-md p-4">
          <div className="text-sm text-gray-500">Avg Win</div>
          <div className="text-2xl font-bold text-green-600">${avgWin.toFixed(0)}</div>
        </div>
        <div className="bg-white rounded-lg shadow-md p-4">
          <div className="text-sm text-gray-500">Avg Loss</div>
          <div className="text-2xl font-bold text-red-600">${avgLoss.toFixed(0)}</div>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg shadow-md p-4">
        <div className="flex items-center space-x-4">
          <span className="text-sm font-medium text-gray-700">Filter:</span>
          <div className="flex space-x-2">
            {[
              { id: 'all', label: 'All Trades' },
              { id: 'profitable', label: 'Profitable' },
              { id: 'losses', label: 'Losses' }
            ].map((filterOption) => (
              <button
                key={filterOption.id}
                onClick={() => setFilter(filterOption.id)}
                className={`px-3 py-1 rounded-lg text-sm font-medium transition-colors ${
                  filter === filterOption.id
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                {filterOption.label}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Trading History Table */}
      <div className="bg-white rounded-lg shadow-md overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-semibold">Trade History ({filteredTrades.length} trades)</h3>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Symbol</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Strategy</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Entry/Exit</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Quantity</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">P&L</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Time</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {filteredTrades.map((trade) => (
                <tr key={trade.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 text-sm text-gray-900">{trade.date}</td>
                  <td className="px-6 py-4 font-semibold text-blue-600">{trade.symbol}</td>
                  <td className="px-6 py-4 text-sm">{trade.strategy}</td>
                  <td className="px-6 py-4 text-sm">
                    <div>${trade.entry_price} → ${trade.exit_price}</div>
                    <div className="text-gray-500">${trade.strike} {trade.expiration}</div>
                  </td>
                  <td className="px-6 py-4 text-sm">{trade.quantity}</td>
                  <td className="px-6 py-4">
                    <div className={`font-semibold ${trade.pnl >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                      ${trade.pnl >= 0 ? '+' : ''}{trade.pnl}
                    </div>
                    <div className={`text-sm ${trade.pnl_percent >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                      ({trade.pnl_percent >= 0 ? '+' : ''}{trade.pnl_percent}%)
                    </div>
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-500">
                    <div>{trade.entry_time} - {trade.exit_time}</div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

const PerformanceAnalytics = () => {
  const { isDarkMode } = useTheme();
  const [timeframe, setTimeframe] = useState('30d');
  
  // Mock performance data
  const performanceData = [
    { date: '2024-08-01', portfolio_value: 10000, pnl: 0 },
    { date: '2024-08-02', portfolio_value: 10150, pnl: 150 },
    { date: '2024-08-03', portfolio_value: 10080, pnl: -70 },
    { date: '2024-08-04', portfolio_value: 10320, pnl: 240 },
    { date: '2024-08-05', portfolio_value: 10280, pnl: -40 },
    { date: '2024-08-06', portfolio_value: 10450, pnl: 170 },
    { date: '2024-08-07', portfolio_value: 10380, pnl: -70 },
    { date: '2024-08-08', portfolio_value: 10520, pnl: 140 },
    { date: '2024-08-09', portfolio_value: 10480, pnl: -40 },
    { date: '2024-08-10', portfolio_value: 10650, pnl: 170 },
    { date: '2024-08-11', portfolio_value: 10590, pnl: -60 },
    { date: '2024-08-12', portfolio_value: 10720, pnl: 130 },
    { date: '2024-08-13', portfolio_value: 10680, pnl: -40 },
    { date: '2024-08-14', portfolio_value: 10850, pnl: 170 }
  ];

  const metrics = {
    totalReturn: 8.5,
    sharpeRatio: 1.42,
    maxDrawdown: -2.1,
    winRate: 64.3,
    profitFactor: 1.85,
    avgWin: 156,
    avgLoss: -58,
    totalTrades: 28,
    bestTrade: 350,
    worstTrade: -120
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold text-gray-800">📈 Performance Analytics</h2>
          <p className="text-gray-600">Detailed analysis of trading performance and risk metrics</p>
        </div>
        <div className="flex items-center space-x-4">
          <select 
            value={timeframe} 
            onChange={(e) => setTimeframe(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          >
            <option value="7d">Last 7 Days</option>
            <option value="30d">Last 30 Days</option>
            <option value="90d">Last 90 Days</option>
            <option value="1y">Last Year</option>
          </select>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
        <div className="bg-white rounded-lg shadow-md p-4">
          <div className="text-sm text-gray-500">Total Return</div>
          <div className="text-2xl font-bold text-green-600">+{metrics.totalReturn}%</div>
        </div>
        <div className="bg-white rounded-lg shadow-md p-4">
          <div className="text-sm text-gray-500">Sharpe Ratio</div>
          <div className="text-2xl font-bold text-blue-600">{metrics.sharpeRatio}</div>
        </div>
        <div className="bg-white rounded-lg shadow-md p-4">
          <div className="text-sm text-gray-500">Max Drawdown</div>
          <div className="text-2xl font-bold text-red-600">{metrics.maxDrawdown}%</div>
        </div>
        <div className="bg-white rounded-lg shadow-md p-4">
          <div className="text-sm text-gray-500">Win Rate</div>
          <div className="text-2xl font-bold text-purple-600">{metrics.winRate}%</div>
        </div>
        <div className="bg-white rounded-lg shadow-md p-4">
          <div className="text-sm text-gray-500">Profit Factor</div>
          <div className="text-2xl font-bold text-orange-600">{metrics.profitFactor}</div>
        </div>
      </div>

      {/* Performance Chart */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-lg font-semibold mb-4">Portfolio Value Over Time</h3>
        <ResponsiveContainer width="100%" height={400}>
          <LineChart data={performanceData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" />
            <YAxis />
            <Tooltip 
              formatter={(value, name) => [`$${value.toLocaleString()}`, 'Portfolio Value']}
              labelFormatter={(date) => `Date: ${date}`}
            />
            <Legend />
            <Line 
              type="monotone" 
              dataKey="portfolio_value" 
              stroke="#2563eb" 
              strokeWidth={2} 
              dot={false}
              name="Portfolio Value"
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Detailed Analytics */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Trade Statistics */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-semibold mb-4">Trade Statistics</h3>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-gray-600">Total Trades</span>
              <span className="font-bold">{metrics.totalTrades}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Average Win</span>
              <span className="font-bold text-green-600">${metrics.avgWin}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Average Loss</span>
              <span className="font-bold text-red-600">${metrics.avgLoss}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Best Trade</span>
              <span className="font-bold text-green-600">${metrics.bestTrade}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Worst Trade</span>
              <span className="font-bold text-red-600">${metrics.worstTrade}</span>
            </div>
          </div>
        </div>

        {/* Risk Metrics */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-semibold mb-4">Risk Analysis</h3>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-gray-600">Volatility (30d)</span>
              <span className="font-bold">12.4%</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Beta</span>
              <span className="font-bold">0.85</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">VaR (95%)</span>
              <span className="font-bold text-red-600">-$245</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Calmar Ratio</span>
              <span className="font-bold">4.05</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Sortino Ratio</span>
              <span className="font-bold">2.18</span>
            </div>
          </div>
        </div>
      </div>

      {/* Monthly Performance */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-lg font-semibold mb-4">Monthly Performance</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-6 gap-4">
          {[
            { month: 'Jan', return: 2.1 },
            { month: 'Feb', return: -0.8 },
            { month: 'Mar', return: 3.4 },
            { month: 'Apr', return: 1.9 },
            { month: 'May', return: -1.2 },
            { month: 'Jun', return: 2.8 },
            { month: 'Jul', return: 1.5 },
            { month: 'Aug', return: 0.8 }
          ].map((month) => (
            <div key={month.month} className="text-center p-3 border rounded-lg">
              <div className="text-sm text-gray-600">{month.month}</div>
              <div className={`font-bold ${month.return >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                {month.return >= 0 ? '+' : ''}{month.return}%
              </div>
            </div>
          ))}
        </div>
      </div>
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

// ==================== TRADESTATION COMPONENTS ====================

// TradeStation Authentication Component
const TradeStationAuth = () => {
  const [authStatus, setAuthStatus] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const { isDarkMode } = useTheme();

  // Check authentication status on component mount
  useEffect(() => {
    checkAuthStatus();
  }, []);

  const checkAuthStatus = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API}/auth/tradestation/status`);
      setAuthStatus(response.data);
      setError(null);
    } catch (err) {
      setError('Failed to check authentication status');
      console.error('Auth status error:', err);
    } finally {
      setLoading(false);
    }
  };

  const initiateLogin = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await axios.get(`${API}/auth/tradestation/login`);
      
      if (response.data.auth_url) {
        // Open OAuth URL in new window
        const authWindow = window.open(response.data.auth_url, 'tradestation-auth', 
          'width=800,height=600,scrollbars=yes,resizable=yes');
        
        if (!authWindow) {
          throw new Error('Popup window blocked. Please allow popups for this site.');
        }
        
        // Listen for messages from the callback window
        const messageListener = (event) => {
          // Verify origin for security (allow localhost for TradeStation callback)
          if (!event.origin.includes('localhost') && event.origin !== window.location.origin) return;
          
          if (event.data.type === 'TRADESTATION_AUTH_SUCCESS') {
            setLoading(false);
            setError(null);
            // Refresh auth status
            checkAuthStatus();
            window.removeEventListener('message', messageListener);
          } else if (event.data.type === 'TRADESTATION_AUTH_ERROR') {
            setLoading(false);
            setError(event.data.error || 'Authentication failed');
            window.removeEventListener('message', messageListener);
          }
        };
        
        window.addEventListener('message', messageListener);
        
        // Set up polling as backup and to detect window closure
        let checkCount = 0;
        const maxChecks = 60; // 3 minutes maximum
        
        const authCheckInterval = setInterval(async () => {
          try {
            checkCount++;
            
            // Check if window was closed by user
            if (authWindow.closed) {
              clearInterval(authCheckInterval);
              window.removeEventListener('message', messageListener);
              setLoading(false);
              
              // Only show error if closed very quickly (before authentication could complete)
              if (checkCount < 3) {
                setError('Authentication window was closed. Please try again.');
              }
              return;
            }
            
            // Stop after maximum checks
            if (checkCount >= maxChecks) {
              clearInterval(authCheckInterval);
              window.removeEventListener('message', messageListener);
              setLoading(false);
              setError('Authentication timeout. Please try again.');
              if (!authWindow.closed) {
                authWindow.close();
              }
            }
          } catch (err) {
            console.error('Auth check error:', err);
          }
        }, 3000);
        
      } else {
        throw new Error('Failed to generate authentication URL');
      }
    } catch (err) {
      setError(err.message || 'Failed to initiate login');
      console.error('Login error:', err);
      setLoading(false);
    }
  };

  const getStatusColor = (status) => {
    if (status?.authentication?.authenticated) return 'text-green-600';
    return 'text-red-600';
  };

  const getStatusText = (status) => {
    if (status?.authentication?.authenticated) return 'Connected';
    return 'Not Connected';
  };

  return (
    <div className={`space-y-6 ${isDarkMode ? 'text-white' : 'text-gray-800'}`}>
      <div className="flex items-center justify-between">
        <h2 className="text-3xl font-bold flex items-center gap-3">
          <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-indigo-600 rounded-lg flex items-center justify-center">
            🏛️
          </div>
          TradeStation Authentication
        </h2>
        <button
          onClick={checkAuthStatus}
          disabled={loading}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 flex items-center gap-2"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          Refresh Status
        </button>
      </div>

      {error && (
        <div className="bg-red-100 border border-red-300 text-red-700 px-4 py-3 rounded-lg">
          <div className="flex items-center gap-2">
            <Info className="w-5 h-5" />
            {error}
          </div>
        </div>
      )}

      {/* Authentication Status Card */}
      <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-xl p-6`}>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Status Overview */}
          <div className="space-y-4">
            <h3 className="text-xl font-semibold mb-4">Connection Status</h3>
            
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-sm font-medium">Status:</span>
                <span className={`font-semibold ${getStatusColor(authStatus)}`}>
                  {loading ? 'Checking...' : getStatusText(authStatus)}
                </span>
              </div>
              
              <div className="flex justify-between items-center">
                <span className="text-sm font-medium">Environment:</span>
                <span className="font-medium text-blue-600">
                  {authStatus?.api_configuration?.environment || 'LIVE'}
                </span>
              </div>
              
              <div className="flex justify-between items-center">
                <span className="text-sm font-medium">Credentials:</span>
                <span className={`font-medium ${authStatus?.api_configuration?.credentials_configured ? 'text-green-600' : 'text-red-600'}`}>
                  {authStatus?.api_configuration?.credentials_configured ? 'Configured' : 'Missing'}
                </span>
              </div>

              {authStatus?.authentication?.authenticated && (
                <div className="flex justify-between items-center">
                  <span className="text-sm font-medium">Expires In:</span>
                  <span className="font-medium text-amber-600">
                    {authStatus.authentication.expires_in_minutes} minutes
                  </span>
                </div>
              )}
            </div>
          </div>

          {/* Connection Details */}
          <div className="space-y-4">
            <h3 className="text-xl font-semibold mb-4">Connection Details</h3>
            
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-sm font-medium">API URL:</span>
                <span className="text-xs font-mono bg-gray-100 px-2 py-1 rounded">
                  {authStatus?.api_configuration?.base_url || 'Not configured'}
                </span>
              </div>
              
              {authStatus?.connection_test && (
                <div className="flex justify-between items-center">
                  <span className="text-sm font-medium">API Test:</span>
                  <span className={`font-medium ${authStatus.connection_test.status === 'success' ? 'text-green-600' : 'text-red-600'}`}>
                    {authStatus.connection_test.status === 'success' ? 'Passed' : 'Failed'}
                  </span>
                </div>
              )}

              {authStatus?.connection_test?.accounts_found !== undefined && (
                <div className="flex justify-between items-center">
                  <span className="text-sm font-medium">Accounts Found:</span>
                  <span className="font-medium text-blue-600">
                    {authStatus.connection_test.accounts_found}
                  </span>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Authentication Action */}
        <div className="mt-6 pt-6 border-t border-gray-200 dark:border-gray-600">
          {!authStatus?.authentication?.authenticated ? (
            <div className="text-center">
              <button
                onClick={initiateLogin}
                disabled={loading || !authStatus?.api_configuration?.credentials_configured}
                className="px-6 py-3 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-lg hover:from-blue-700 hover:to-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 mx-auto"
              >
                <Settings className="w-5 h-5" />
                {loading ? 'Authenticating...' : 'Connect to TradeStation'}
              </button>
              <p className="text-sm text-gray-500 mt-2">
                This will open TradeStation's OAuth login in a new window
              </p>
            </div>
          ) : (
            <div className="text-center">
              <div className="inline-flex items-center gap-2 px-4 py-2 bg-green-100 text-green-800 rounded-lg">
                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                Successfully connected to TradeStation
              </div>
              <p className="text-sm text-gray-500 mt-2">
                You can now access portfolio data and place trades
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Instructions Card */}
      <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-blue-50 border-blue-200'} border rounded-xl p-6`}>
        <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <Info className="w-5 h-5 text-blue-600" />
          Authentication Instructions
        </h3>
        <div className="space-y-3 text-sm">
          <div className="flex items-start gap-3">
            <div className="w-6 h-6 bg-blue-600 text-white rounded-full flex items-center justify-center text-xs font-bold">1</div>
            <p>Click "Connect to TradeStation" to initiate OAuth authentication</p>
          </div>
          <div className="flex items-start gap-3">
            <div className="w-6 h-6 bg-blue-600 text-white rounded-full flex items-center justify-center text-xs font-bold">2</div>
            <p>Log in with your TradeStation credentials in the popup window</p>
          </div>
          <div className="flex items-start gap-3">
            <div className="w-6 h-6 bg-blue-600 text-white rounded-full flex items-center justify-center text-xs font-bold">3</div>
            <p>Authorize FlowMind Analytics to access your account</p>
          </div>
          <div className="flex items-start gap-3">
            <div className="w-6 h-6 bg-blue-600 text-white rounded-full flex items-center justify-center text-xs font-bold">4</div>
            <p>Connection status will update automatically once authenticated</p>
          </div>
        </div>
      </div>
    </div>
  );
};

// TradeStation Live Portfolio Component
const TradeStationPortfolio = () => {
  const [accounts, setAccounts] = useState([]);
  const [selectedAccount, setSelectedAccount] = useState(null);
  const [portfolioData, setPortfolioData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const { isDarkMode } = useTheme();

  useEffect(() => {
    loadAccounts();
  }, []);

  const loadAccounts = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API}/tradestation/accounts`);
      setAccounts(response.data.accounts || []);
      if (response.data.accounts?.length > 0) {
        setSelectedAccount(response.data.accounts[0].Key);
      }
      setError(null);
    } catch (err) {
      setError('Failed to load accounts. Please ensure you are authenticated.');
      console.error('Accounts error:', err);
    } finally {
      setLoading(false);
    }
  };

  const loadPortfolioData = async (accountId) => {
    if (!accountId) return;
    
    try {
      setLoading(true);
      const response = await axios.get(`${API}/tradestation/accounts/${accountId}/summary`);
      setPortfolioData(response.data.data);
      setError(null);
    } catch (err) {
      setError('Failed to load portfolio data');
      console.error('Portfolio error:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (selectedAccount) {
      loadPortfolioData(selectedAccount);
    }
  }, [selectedAccount]);

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(value || 0);
  };

  const formatPercent = (value) => {
    return `${value >= 0 ? '+' : ''}${(value || 0).toFixed(2)}%`;
  };

  return (
    <div className={`space-y-6 ${isDarkMode ? 'text-white' : 'text-gray-800'}`}>
      <div className="flex items-center justify-between">
        <h2 className="text-3xl font-bold flex items-center gap-3">
          <div className="w-10 h-10 bg-gradient-to-r from-emerald-500 to-green-600 rounded-lg flex items-center justify-center">
            📊
          </div>
          Live Portfolio
        </h2>
        <div className="flex items-center gap-3">
          {accounts.length > 0 && (
            <select
              value={selectedAccount || ''}
              onChange={(e) => setSelectedAccount(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
            >
              {accounts.map((account) => (
                <option key={account.Key} value={account.Key}>
                  {account.Name} ({account.Key})
                </option>
              ))}
            </select>
          )}
          <button
            onClick={() => loadPortfolioData(selectedAccount)}
            disabled={loading || !selectedAccount}
            className="px-4 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 disabled:opacity-50 flex items-center gap-2"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </button>
        </div>
      </div>

      {error && (
        <div className="bg-red-100 border border-red-300 text-red-700 px-4 py-3 rounded-lg">
          <div className="flex items-center gap-2">
            <Info className="w-5 h-5" />
            {error}
          </div>
        </div>
      )}

      {loading && !portfolioData && (
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <RefreshCw className="w-8 h-8 animate-spin text-emerald-600 mx-auto mb-4" />
            <p>Loading portfolio data...</p>
          </div>
        </div>
      )}

      {portfolioData && (
        <>
          {/* Portfolio Summary Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-xl p-6`}>
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-500">Total Value</p>
                  <p className="text-2xl font-bold text-emerald-600">
                    {formatCurrency(portfolioData.portfolio_metrics?.total_market_value)}
                  </p>
                </div>
                <DollarSign className="w-8 h-8 text-emerald-600" />
              </div>
            </div>

            <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-xl p-6`}>
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-500">Total P&L</p>
                  <p className={`text-2xl font-bold ${(portfolioData.portfolio_metrics?.total_unrealized_pnl || 0) >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                    {formatCurrency(portfolioData.portfolio_metrics?.total_unrealized_pnl)}
                  </p>
                </div>
                <TrendingUp className={`w-8 h-8 ${(portfolioData.portfolio_metrics?.total_unrealized_pnl || 0) >= 0 ? 'text-green-600' : 'text-red-600'}`} />
              </div>
            </div>

            <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-xl p-6`}>
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-500">Total Return</p>
                  <p className={`text-2xl font-bold ${(portfolioData.portfolio_metrics?.total_return_percent || 0) >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                    {formatPercent(portfolioData.portfolio_metrics?.total_return_percent)}
                  </p>
                </div>
                <BarChart3 className={`w-8 h-8 ${(portfolioData.portfolio_metrics?.total_return_percent || 0) >= 0 ? 'text-green-600' : 'text-red-600'}`} />
              </div>
            </div>

            <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-xl p-6`}>
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-500">Positions</p>
                  <p className="text-2xl font-bold text-blue-600">
                    {portfolioData.portfolio_metrics?.position_count || 0}
                  </p>
                </div>
                <Briefcase className="w-8 h-8 text-blue-600" />
              </div>
            </div>
          </div>

          {/* Positions Table */}
          {portfolioData.positions && portfolioData.positions.length > 0 && (
            <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-xl overflow-hidden`}>
              <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-600">
                <h3 className="text-lg font-semibold">Current Positions</h3>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className={`${isDarkMode ? 'bg-gray-700' : 'bg-gray-50'}`}>
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Symbol</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Quantity</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Avg Price</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Current Price</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Market Value</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">P&L</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">P&L %</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200 dark:divide-gray-600">
                    {portfolioData.positions.map((position, index) => (
                      <tr key={index} className={`${isDarkMode ? 'hover:bg-gray-700' : 'hover:bg-gray-50'}`}>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="flex items-center">
                            <div className="font-medium text-blue-600">{position.symbol}</div>
                            <div className="text-xs text-gray-500 ml-2">{position.asset_type}</div>
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`${position.quantity >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                            {position.quantity >= 0 ? '+' : ''}{position.quantity}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">{formatCurrency(position.average_price)}</td>
                        <td className="px-6 py-4 whitespace-nowrap">{formatCurrency(position.current_price)}</td>
                        <td className="px-6 py-4 whitespace-nowrap font-medium">{formatCurrency(position.market_value)}</td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`font-medium ${position.unrealized_pnl >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                            {formatCurrency(position.unrealized_pnl)}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`font-medium ${position.unrealized_pnl_percent >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                            {formatPercent(position.unrealized_pnl_percent)}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Risk Analysis */}
          {portfolioData.risk_analysis && (
            <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-xl p-6`}>
              <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                <Target className="w-5 h-5 text-orange-500" />
                Risk Analysis
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="text-center">
                  <div className={`text-2xl font-bold ${
                    portfolioData.risk_analysis.risk_level === 'LOW' ? 'text-green-600' :
                    portfolioData.risk_analysis.risk_level === 'MEDIUM' ? 'text-yellow-600' : 'text-red-600'
                  }`}>
                    {portfolioData.risk_analysis.risk_level}
                  </div>
                  <div className="text-sm text-gray-500">Risk Level</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-orange-600">
                    {portfolioData.risk_analysis.risk_score || 0}/100
                  </div>
                  <div className="text-sm text-gray-500">Risk Score</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-blue-600">
                    {portfolioData.risk_analysis.concentration_analysis?.max_position_weight?.toFixed(1) || 0}%
                  </div>
                  <div className="text-sm text-gray-500">Max Position</div>
                </div>
              </div>
            </div>
          )}
        </>
      )}

      {!loading && !error && accounts.length === 0 && (
        <div className="text-center py-12">
          <Settings className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-500 mb-2">No Accounts Found</h3>
          <p className="text-gray-400">Please authenticate with TradeStation first</p>
        </div>
      )}
    </div>
  );
};

// TradeStation Live Trading Component
const TradeStationTrading = () => {
  const [accounts, setAccounts] = useState([]);
  const [selectedAccount, setSelectedAccount] = useState(null);
  const [orderForm, setOrderForm] = useState({
    symbol: '',
    quantity: '',
    side: 'Buy',
    order_type: 'Market',
    price: '',
    time_in_force: 'DAY'
  });
  const [orderValidation, setOrderValidation] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const { isDarkMode } = useTheme();

  useEffect(() => {
    loadAccounts();
  }, []);

  const loadAccounts = async () => {
    try {
      const response = await axios.get(`${API}/tradestation/accounts`);
      setAccounts(response.data.accounts || []);
      if (response.data.accounts?.length > 0) {
        setSelectedAccount(response.data.accounts[0].Key);
      }
    } catch (err) {
      setError('Failed to load accounts. Please ensure you are authenticated.');
      console.error('Accounts error:', err);
    }
  };

  const validateOrder = async () => {
    if (!selectedAccount || !orderForm.symbol || !orderForm.quantity) {
      setError('Please fill in all required fields');
      return;
    }

    try {
      setLoading(true);
      const response = await axios.post(`${API}/tradestation/accounts/${selectedAccount}/orders/validate`, orderForm);
      setOrderValidation(response.data.validation);
      setError(null);
    } catch (err) {
      setError('Order validation failed');
      console.error('Validation error:', err);
    } finally {
      setLoading(false);
    }
  };

  const placeOrder = async (force = false) => {
    if (!orderValidation?.valid && !force) {
      await validateOrder();
      return;
    }

    try {
      setLoading(true);
      const response = await axios.post(
        `${API}/tradestation/accounts/${selectedAccount}/orders?force=${force}`,
        orderForm
      );
      
      if (response.data.status === 'success') {
        setSuccess('Order placed successfully!');
        setOrderForm({
          symbol: '',
          quantity: '',
          side: 'Buy',
          order_type: 'Market',
          price: '',
          time_in_force: 'DAY'
        });
        setOrderValidation(null);
      } else {
        setError(response.data.message || 'Failed to place order');
      }
    } catch (err) {
      setError('Failed to place order');
      console.error('Order error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (field, value) => {
    setOrderForm(prev => ({ ...prev, [field]: value }));
    setOrderValidation(null);
    setError(null);
    setSuccess(null);
  };

  return (
    <div className={`space-y-6 ${isDarkMode ? 'text-white' : 'text-gray-800'}`}>
      <div className="flex items-center justify-between">
        <h2 className="text-3xl font-bold flex items-center gap-3">
          <div className="w-10 h-10 bg-gradient-to-r from-red-500 to-pink-600 rounded-lg flex items-center justify-center">
            ⚡
          </div>
          Live Trading
        </h2>
        {accounts.length > 0 && (
          <select
            value={selectedAccount || ''}
            onChange={(e) => setSelectedAccount(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-red-500"
          >
            {accounts.map((account) => (
              <option key={account.Key} value={account.Key}>
                {account.Name} ({account.Key})
              </option>
            ))}
          </select>
        )}
      </div>

      {error && (
        <div className="bg-red-100 border border-red-300 text-red-700 px-4 py-3 rounded-lg">
          <div className="flex items-center gap-2">
            <Info className="w-5 h-5" />
            {error}
          </div>
        </div>
      )}

      {success && (
        <div className="bg-green-100 border border-green-300 text-green-700 px-4 py-3 rounded-lg">
          <div className="flex items-center gap-2">
            <Info className="w-5 h-5" />
            {success}
          </div>
        </div>
      )}

      {/* Order Form */}
      <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-xl p-6`}>
        <h3 className="text-xl font-semibold mb-6">Place Order</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium mb-2">Symbol</label>
            <input
              type="text"
              value={orderForm.symbol}
              onChange={(e) => handleInputChange('symbol', e.target.value.toUpperCase())}
              placeholder="e.g., AAPL"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-red-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">Quantity</label>
            <input
              type="number"
              value={orderForm.quantity}
              onChange={(e) => handleInputChange('quantity', e.target.value)}
              placeholder="Number of shares"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-red-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">Side</label>
            <select
              value={orderForm.side}
              onChange={(e) => handleInputChange('side', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-red-500"
            >
              <option value="Buy">Buy</option>
              <option value="Sell">Sell</option>
              <option value="SellShort">Sell Short</option>
              <option value="BuyToCover">Buy to Cover</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">Order Type</label>
            <select
              value={orderForm.order_type}
              onChange={(e) => handleInputChange('order_type', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-red-500"
            >
              <option value="Market">Market</option>
              <option value="Limit">Limit</option>
              <option value="StopMarket">Stop Market</option>
              <option value="StopLimit">Stop Limit</option>
            </select>
          </div>

          {(orderForm.order_type === 'Limit' || orderForm.order_type === 'StopLimit') && (
            <div>
              <label className="block text-sm font-medium mb-2">Price</label>
              <input
                type="number"
                step="0.01"
                value={orderForm.price}
                onChange={(e) => handleInputChange('price', e.target.value)}
                placeholder="0.00"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-red-500"
              />
            </div>
          )}

          <div>
            <label className="block text-sm font-medium mb-2">Time in Force</label>
            <select
              value={orderForm.time_in_force}
              onChange={(e) => handleInputChange('time_in_force', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-red-500"
            >
              <option value="DAY">Day</option>
              <option value="GTC">Good Till Canceled</option>
              <option value="IOC">Immediate or Cancel</option>
              <option value="FOK">Fill or Kill</option>
            </select>
          </div>
        </div>

        <div className="mt-6 flex gap-3">
          <button
            onClick={validateOrder}
            disabled={loading || !selectedAccount || !orderForm.symbol || !orderForm.quantity}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 flex items-center gap-2"
          >
            <Target className="w-4 h-4" />
            Validate Order
          </button>
          
          <button
            onClick={() => placeOrder(false)}
            disabled={loading || !orderValidation?.valid}
            className="px-6 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50 flex items-center gap-2"
          >
            <Zap className="w-4 h-4" />
            {loading ? 'Placing...' : 'Place Order'}
          </button>
        </div>
      </div>

      {/* Order Validation Results */}
      {orderValidation && (
        <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-xl p-6`}>
          <h3 className="text-lg font-semibold mb-4">Order Validation</h3>
          
          <div className="space-y-4">
            <div className="flex items-center gap-2">
              <span className="text-sm font-medium">Status:</span>
              <span className={`px-2 py-1 rounded text-xs font-medium ${
                orderValidation.valid ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
              }`}>
                {orderValidation.valid ? 'VALID' : 'INVALID'}
              </span>
            </div>

            <div className="flex items-center gap-2">
              <span className="text-sm font-medium">Risk Assessment:</span>
              <span className={`px-2 py-1 rounded text-xs font-medium ${
                orderValidation.risk_assessment === 'LOW' ? 'bg-green-100 text-green-800' :
                orderValidation.risk_assessment === 'MEDIUM' ? 'bg-yellow-100 text-yellow-800' :
                'bg-red-100 text-red-800'
              }`}>
                {orderValidation.risk_assessment}
              </span>
            </div>

            <div className="flex items-center gap-2">
              <span className="text-sm font-medium">Estimated Cost:</span>
              <span className="font-medium">
                ${orderValidation.estimated_cost?.toFixed(2) || '0.00'}
              </span>
            </div>

            {orderValidation.warnings?.length > 0 && (
              <div>
                <span className="text-sm font-medium text-amber-600">Warnings:</span>
                <ul className="mt-2 space-y-1">
                  {orderValidation.warnings.map((warning, index) => (
                    <li key={index} className="text-sm text-amber-600 flex items-start gap-2">
                      <Info className="w-4 h-4 mt-0.5 flex-shrink-0" />
                      {warning}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {orderValidation.errors?.length > 0 && (
              <div>
                <span className="text-sm font-medium text-red-600">Errors:</span>
                <ul className="mt-2 space-y-1">
                  {orderValidation.errors.map((error, index) => (
                    <li key={index} className="text-sm text-red-600 flex items-start gap-2">
                      <Info className="w-4 h-4 mt-0.5 flex-shrink-0" />
                      {error}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {orderValidation.warnings?.length > 0 && orderValidation.valid && (
              <button
                onClick={() => placeOrder(true)}
                disabled={loading}
                className="mt-4 px-4 py-2 bg-amber-600 text-white rounded-lg hover:bg-amber-700 disabled:opacity-50 flex items-center gap-2"
              >
                <Zap className="w-4 h-4" />
                Force Place Order
              </button>
            )}
          </div>
        </div>
      )}

      {!selectedAccount && accounts.length === 0 && (
        <div className="text-center py-12">
          <Settings className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-500 mb-2">No Trading Accounts</h3>
          <p className="text-gray-400">Please authenticate with TradeStation first</p>
        </div>
      )}
    </div>
  );
};

// TradeStation Order Management Component
const TradeStationOrders = () => {
  const [accounts, setAccounts] = useState([]);
  const [selectedAccount, setSelectedAccount] = useState(null);
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [filters, setFilters] = useState({
    status: '',
    symbol: '',
    days_back: 7
  });
  const { isDarkMode } = useTheme();

  useEffect(() => {
    loadAccounts();
  }, []);

  useEffect(() => {
    if (selectedAccount) {
      loadOrders();
    }
  }, [selectedAccount, filters]);

  const loadAccounts = async () => {
    try {
      const response = await axios.get(`${API}/tradestation/accounts`);
      setAccounts(response.data.accounts || []);
      if (response.data.accounts?.length > 0) {
        setSelectedAccount(response.data.accounts[0].Key);
      }
    } catch (err) {
      setError('Failed to load accounts. Please ensure you are authenticated.');
      console.error('Accounts error:', err);
    }
  };

  const loadOrders = async () => {
    if (!selectedAccount) return;
    
    try {
      setLoading(true);
      const params = new URLSearchParams();
      if (filters.status) params.append('status', filters.status);
      if (filters.symbol) params.append('symbol', filters.symbol);
      params.append('days_back', filters.days_back);

      const response = await axios.get(`${API}/tradestation/accounts/${selectedAccount}/orders?${params}`);
      setOrders(response.data.orders || []);
      setError(null);
    } catch (err) {
      setError('Failed to load orders');
      console.error('Orders error:', err);
    } finally {
      setLoading(false);
    }
  };

  const cancelOrder = async (orderId) => {
    try {
      setLoading(true);
      await axios.delete(`${API}/tradestation/accounts/${selectedAccount}/orders/${orderId}`);
      await loadOrders(); // Refresh orders list
      setError(null);
    } catch (err) {
      setError('Failed to cancel order');
      console.error('Cancel error:', err);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'FLL': return 'bg-green-100 text-green-800';
      case 'PND': return 'bg-yellow-100 text-yellow-800';
      case 'PFL': return 'bg-blue-100 text-blue-800';
      case 'CAN': return 'bg-gray-100 text-gray-800';
      case 'REJ': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusLabel = (status) => {
    switch (status) {
      case 'FLL': return 'Filled';
      case 'PND': return 'Pending';
      case 'PFL': return 'Partially Filled';
      case 'CAN': return 'Cancelled';
      case 'REJ': return 'Rejected';
      default: return status;
    }
  };

  return (
    <div className={`space-y-6 ${isDarkMode ? 'text-white' : 'text-gray-800'}`}>
      <div className="flex items-center justify-between">
        <h2 className="text-3xl font-bold flex items-center gap-3">
          <div className="w-10 h-10 bg-gradient-to-r from-purple-500 to-violet-600 rounded-lg flex items-center justify-center">
            📋
          </div>
          Order Management
        </h2>
        <div className="flex items-center gap-3">
          {accounts.length > 0 && (
            <select
              value={selectedAccount || ''}
              onChange={(e) => setSelectedAccount(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
            >
              {accounts.map((account) => (
                <option key={account.Key} value={account.Key}>
                  {account.Name} ({account.Key})
                </option>
              ))}
            </select>
          )}
          <button
            onClick={loadOrders}
            disabled={loading || !selectedAccount}
            className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50 flex items-center gap-2"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </button>
        </div>
      </div>

      {error && (
        <div className="bg-red-100 border border-red-300 text-red-700 px-4 py-3 rounded-lg">
          <div className="flex items-center gap-2">
            <Info className="w-5 h-5" />
            {error}
          </div>
        </div>
      )}

      {/* Filters */}
      <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-xl p-6`}>
        <h3 className="text-lg font-semibold mb-4">Filters</h3>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <label className="block text-sm font-medium mb-2">Status</label>
            <select
              value={filters.status}
              onChange={(e) => setFilters(prev => ({ ...prev, status: e.target.value }))}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
            >
              <option value="">All Statuses</option>
              <option value="PND">Pending</option>
              <option value="FLL">Filled</option>
              <option value="PFL">Partially Filled</option>
              <option value="CAN">Cancelled</option>
              <option value="REJ">Rejected</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">Symbol</label>
            <input
              type="text"
              value={filters.symbol}
              onChange={(e) => setFilters(prev => ({ ...prev, symbol: e.target.value.toUpperCase() }))}
              placeholder="e.g., AAPL"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">Days Back</label>
            <select
              value={filters.days_back}
              onChange={(e) => setFilters(prev => ({ ...prev, days_back: parseInt(e.target.value) }))}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
            >
              <option value={1}>1 Day</option>
              <option value={7}>7 Days</option>
              <option value={14}>14 Days</option>
              <option value={30}>30 Days</option>
            </select>
          </div>
        </div>
      </div>

      {/* Orders Table */}
      {orders.length > 0 ? (
        <div className={`${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'} border rounded-xl overflow-hidden`}>
          <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-600">
            <h3 className="text-lg font-semibold">Orders ({orders.length})</h3>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className={`${isDarkMode ? 'bg-gray-700' : 'bg-gray-50'}`}>
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Order ID</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Symbol</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Quantity</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Type</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Price</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Filled</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Time</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200 dark:divide-gray-600">
                {orders.map((order) => (
                  <tr key={order.order_id} className={`${isDarkMode ? 'hover:bg-gray-700' : 'hover:bg-gray-50'}`}>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-mono text-gray-500">
                        {order.order_id.substring(0, 8)}...
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="font-medium text-blue-600">{order.symbol}</div>
                      <div className="text-xs text-gray-500">{order.asset_type}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`${order.quantity >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                        {order.quantity >= 0 ? '+' : ''}{order.quantity}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">{order.order_type}</td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {order.price ? `$${order.price.toFixed(2)}` : 'Market'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 py-1 rounded text-xs font-medium ${getStatusColor(order.status)}`}>
                        {getStatusLabel(order.status)}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {order.filled_quantity}/{Math.abs(order.quantity)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {new Date(order.timestamp).toLocaleDateString()} {new Date(order.timestamp).toLocaleTimeString()}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {(order.status === 'PND' || order.status === 'PFL') && (
                        <button
                          onClick={() => cancelOrder(order.order_id)}
                          disabled={loading}
                          className="text-red-600 hover:text-red-800 disabled:opacity-50"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      ) : (
        <div className="text-center py-12">
          {loading ? (
            <>
              <RefreshCw className="w-16 h-16 text-gray-400 mx-auto mb-4 animate-spin" />
              <h3 className="text-lg font-medium text-gray-500 mb-2">Loading Orders...</h3>
            </>
          ) : (
            <>
              <History className="w-16 h-16 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-500 mb-2">No Orders Found</h3>
              <p className="text-gray-400">No orders match the current filters</p>
            </>
          )}
        </div>
      )}
    </div>
  );
};

// TradeStation Callback Handler Component
const TradeStationCallback = () => {
  const [status, setStatus] = useState('processing');
  const [message, setMessage] = useState('Processing authentication...');

  useEffect(() => {
    const handleCallback = async () => {
      try {
        // Get the authorization code from URL
        const urlParams = new URLSearchParams(window.location.search);
        const code = urlParams.get('code');
        const state = urlParams.get('state');
        const error = urlParams.get('error');

        if (error) {
          setStatus('error');
          setMessage(`Authentication failed: ${error}`);
          return;
        }

        if (!code) {
          setStatus('error');
          setMessage('No authorization code received');
          return;
        }

        // Exchange code for tokens
        const response = await axios.get(`${API}/auth/tradestation/callback?code=${code}&state=${state}`);
        
        if (response.data.status === 'success') {
          setStatus('success');
          setMessage('Authentication successful! You can close this window.');
          
          // Try to communicate back to parent window
          if (window.opener) {
            window.opener.postMessage({ 
              type: 'TRADESTATION_AUTH_SUCCESS', 
              data: response.data 
            }, '*');
            setTimeout(() => window.close(), 2000);
          }
        } else {
          setStatus('error');
          setMessage('Authentication failed');
        }
      } catch (err) {
        setStatus('error');
        setMessage(`Authentication error: ${err.message}`);
      }
    };

    handleCallback();
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <div className="bg-white rounded-xl shadow-lg p-8 max-w-md w-full text-center">
        <div className="mb-6">
          <div className="w-16 h-16 mx-auto mb-4 bg-gradient-to-r from-blue-500 to-indigo-600 rounded-full flex items-center justify-center">
            🏛️
          </div>
          <h2 className="text-2xl font-bold text-gray-800">TradeStation Authentication</h2>
        </div>
        
        <div className="mb-6">
          {status === 'processing' && (
            <div className="flex items-center justify-center gap-3">
              <RefreshCw className="w-6 h-6 animate-spin text-blue-600" />
              <span className="text-gray-600">Processing...</span>
            </div>
          )}
          
          {status === 'success' && (
            <div className="text-center">
              <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-3">
                <CheckCircle className="w-8 h-8 text-green-600" />
              </div>
              <p className="text-green-700 font-medium">Success!</p>
            </div>
          )}
          
          {status === 'error' && (
            <div className="text-center">
              <div className="w-12 h-12 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-3">
                <XCircle className="w-8 h-8 text-red-600" />
              </div>
              <p className="text-red-700 font-medium">Error</p>
            </div>
          )}
        </div>
        
        <p className="text-sm text-gray-600 mb-4">{message}</p>
        
        {status !== 'processing' && (
          <button
            onClick={() => window.close()}
            className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700"
          >
            Close Window
          </button>
        )}
      </div>
    </div>
  );
};

// Main App Component
function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const { isDarkMode } = useTheme();

  // Function to handle sidebar state from Sidebar component
  const handleSidebarToggle = (collapsed) => {
    setSidebarCollapsed(collapsed);
  };

  // Get the current URL path to handle callback
  const currentPath = window.location.pathname;
  
  // Handle TradeStation callback
  if (currentPath === '/tradestation-callback') {
    return <TradeStationCallback />;
  }

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
      case 'options-flow':
        return <OptionsFlow />;
      case 'dark-pool':
        return <DarkPool />;
      case 'congressional':
        return <CongressionalTrades />;
      case 'trading-strategies':
        return <TradingStrategies />;
      case 'ts-auth':
        return <TradeStationAuth />;
      case 'ts-portfolio':
        return <TradeStationPortfolio />;
      case 'ts-trading':
        return <TradeStationTrading />;
      case 'ts-orders':
        return <TradeStationOrders />;
      case 'auto-trading':
        return <AutoOptionsTrading />;
      case 'trading-history':
        return <TradingHistory />;
      case 'performance':
        return <PerformanceAnalytics />;
      case 'news':
        return <MarketNews />;
      default:
        return <Dashboard />;
    }
  };

  return (
    <BrowserRouter>
      <div className={`min-h-screen flex transition-all duration-300 ${
        isDarkMode 
          ? 'bg-gradient-to-br from-slate-900 via-gray-900 to-slate-800' 
          : 'bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50'
      }`}>
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

export default function AppWithTheme() {
  return (
    <ErrorBoundary>
      <ThemeProvider>
        <App />
      </ThemeProvider>
    </ErrorBoundary>
  );
}