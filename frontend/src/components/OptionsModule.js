import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Zap,
  Target,
  BarChart3,
  Activity,
  Calculator,
  TrendingUp,
  PieChart,
  Settings,
  BookOpen,
  ArrowLeft,
  Search,
  Filter,
  RefreshCw,
  Play,
  Pause,
  Download,
  DollarSign,
  Percent,
  Calendar,
  Info
} from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const OptionsModule = () => {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('builder');
  const [selectedStrategy, setSelectedStrategy] = useState('Long Call');
  const [loading, setLoading] = useState(false);
  const [calculationData, setCalculationData] = useState(null);
  const [error, setError] = useState(null);
  
  // Strategy parameters
  const [symbol, setSymbol] = useState('AAPL');
  const [stockPrice, setStockPrice] = useState(150.0);
  const [strike, setStrike] = useState(155.0);
  const [daysToExpiry, setDaysToExpiry] = useState(30);
  const [volatility, setVolatility] = useState(0.25);
  const [riskFreeRate, setRiskFreeRate] = useState(0.05);

  // Available strategies
  const [availableStrategies, setAvailableStrategies] = useState({});

  // Load available strategies
  useEffect(() => {
    const loadStrategies = async () => {
      try {
        const response = await fetch(`${API}/options/strategies`);
        const data = await response.json();
        if (data.status === 'success') {
          setAvailableStrategies(data.strategies);
        }
      } catch (error) {
        console.error('Failed to load strategies:', error);
      }
    };
    
    loadStrategies();
  }, []);

  // Auto-calculate when parameters change
  useEffect(() => {
    if (selectedStrategy && symbol && stockPrice && strike) {
      calculateStrategy();
    }
  }, [selectedStrategy, symbol, stockPrice, strike, daysToExpiry, volatility, riskFreeRate]);

  const calculateStrategy = async () => {
    if (!selectedStrategy || !symbol || !stockPrice || !strike) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const requestData = {
        symbol: symbol.toUpperCase(),
        strategy_name: selectedStrategy,
        stock_price: parseFloat(stockPrice),
        strike: parseFloat(strike),
        days_to_expiry: parseInt(daysToExpiry),
        volatility: parseFloat(volatility),
        risk_free_rate: parseFloat(riskFreeRate)
      };

      const response = await fetch(`${API}/options/calculate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestData)
      });

      const data = await response.json();
      
      if (response.ok) {
        setCalculationData(data);
      } else {
        setError(data.detail || 'Calculation failed');
      }
    } catch (error) {
      setError(`Network error: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  // Strategy categories for easy selection
  const strategyCategories = {
    novice: {
      label: 'Novice',
      strategies: ['Long Call', 'Long Put']
    },
    intermediate: {
      label: 'Intermediate', 
      strategies: ['Bull Call Spread', 'Bear Put Spread', 'Iron Condor', 'Straddle']
    },
    advanced: {
      label: 'Advanced',
      strategies: ['Short Straddle', 'Jade Lizard', 'Call Ratio Spread']
    }
  };

  return (
    <div className="min-h-screen bg-gray-900">
      {/* Header */}
      <div className="bg-gray-800 shadow-sm border-b border-gray-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-4">
              <button
                onClick={() => navigate('/')}
                className="flex items-center space-x-2 text-gray-300 hover:text-white transition-colors"
              >
                <ArrowLeft size={20} />
                <span>Back to Dashboard</span>
              </button>
              <div className="h-6 w-px bg-gray-600"></div>
              <div>
                <h1 className="text-2xl font-bold text-white flex items-center">
                  <Zap className="mr-3 text-blue-500" size={28} />
                  Options Module
                </h1>
                <p className="text-sm text-gray-400">
                  Complete options trading toolkit - Real-time Black-Scholes calculations
                </p>
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              <div className="bg-green-900 text-green-300 px-3 py-1 rounded-full text-sm font-medium border border-green-700">
                ✅ Live Calculations
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="bg-gray-800 border-b border-gray-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex space-x-8">
            {[
              { id: 'builder', label: '🏗️ Strategy Builder', icon: Calculator },
              { id: 'optimizer', label: '🎯 Optimizer', icon: Target },
              { id: 'flow', label: '🌊 Options Flow', icon: Activity },
              { id: 'portfolio', label: '📊 Portfolio', icon: PieChart }
            ].map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center space-x-2 py-4 px-2 border-b-2 font-medium text-sm transition-colors ${
                    activeTab === tab.id
                      ? 'border-blue-500 text-blue-400'
                      : 'border-transparent text-gray-400 hover:text-gray-300 hover:border-gray-600'
                  }`}
                >
                  <Icon size={16} />
                  <span>{tab.label}</span>
                </button>
              );
            })}
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        
        {/* Strategy Builder Tab */}
        {activeTab === 'builder' && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            
            {/* Left Panel - Strategy Configuration */}
            <div className="lg:col-span-1 space-y-6">
              
              {/* Strategy Selection */}
              <div className="bg-gray-800 rounded-lg shadow-lg p-6 border border-gray-700">
                <h3 className="text-lg font-bold text-white mb-4 flex items-center">
                  <Target className="mr-2 text-blue-400" size={20} />
                  Strategy Selection
                </h3>
                
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">
                      Strategy Type
                    </label>
                    <select 
                      value={selectedStrategy}
                      onChange={(e) => setSelectedStrategy(e.target.value)}
                      className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 text-white"
                    >
                      <optgroup label="✅ Implemented">
                        <option>Long Call</option>
                        <option>Long Put</option>
                      </optgroup>
                      <optgroup label="🚧 Coming Soon">
                        <option disabled>Bull Call Spread</option>
                        <option disabled>Bear Put Spread</option>
                        <option disabled>Iron Condor</option>
                        <option disabled>Straddle</option>
                      </optgroup>
                    </select>
                  </div>
                </div>
              </div>

              {/* Parameters */}
              <div className="bg-gray-800 rounded-lg shadow-lg p-6 border border-gray-700">
                <h3 className="text-lg font-bold text-white mb-4 flex items-center">
                  <Settings className="mr-2 text-blue-400" size={20} />
                  Parameters
                </h3>
                
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">
                      Symbol
                    </label>
                    <input
                      type="text"
                      value={symbol}
                      onChange={(e) => setSymbol(e.target.value.toUpperCase())}
                      className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 text-white"
                      placeholder="e.g. AAPL"
                    />
                  </div>
                  
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-300 mb-2">
                        Stock Price ($)
                      </label>
                      <input
                        type="number"
                        value={stockPrice}
                        onChange={(e) => setStockPrice(e.target.value)}
                        className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 text-white"
                        step="0.01"
                      />
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-300 mb-2">
                        Strike ($)
                      </label>
                      <input
                        type="number"
                        value={strike}
                        onChange={(e) => setStrike(e.target.value)}
                        className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 text-white"
                        step="0.01"
                      />
                    </div>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">
                      Days to Expiry
                    </label>
                    <input
                      type="number"
                      value={daysToExpiry}
                      onChange={(e) => setDaysToExpiry(e.target.value)}
                      className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 text-white"
                      min="1"
                      max="365"
                    />
                  </div>
                  
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-300 mb-2">
                        Volatility (%)
                      </label>
                      <input
                        type="number"
                        value={volatility * 100}
                        onChange={(e) => setVolatility(e.target.value / 100)}
                        className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 text-white"
                        step="1"
                        min="1"
                        max="100"
                      />
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-300 mb-2">
                        Risk Free Rate (%)
                      </label>
                      <input
                        type="number"
                        value={riskFreeRate * 100}
                        onChange={(e) => setRiskFreeRate(e.target.value / 100)}
                        className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 text-white"
                        step="0.1"
                        min="0"
                        max="10"
                      />
                    </div>
                  </div>
                </div>
              </div>

              {/* Strategy Analysis */}
              {calculationData && (
                <div className="bg-gray-800 rounded-lg shadow-lg p-6 border border-gray-700">
                  <h3 className="text-lg font-bold text-white mb-4 flex items-center">
                    <BarChart3 className="mr-2 text-blue-400" size={20} />
                    Analysis
                  </h3>
                  
                  <div className="space-y-4">
                    {/* Strategy Info */}
                    <div className="bg-blue-900/30 border border-blue-700 rounded-lg p-4">
                      <h4 className="font-semibold text-blue-300 mb-2">
                        {calculationData.strategy_config.name}
                      </h4>
                      <p className="text-sm text-blue-200">
                        {calculationData.strategy_config.description}
                      </p>
                    </div>
                    
                    {/* Legs */}
                    {calculationData.strategy_config.legs.map((leg, index) => (
                      <div key={index} className="bg-gray-700 rounded-lg p-4 border border-gray-600">
                        <div className="flex justify-between items-center">
                          <div>
                            <span className="font-medium text-white">
                              {leg.action.toUpperCase()} {leg.option_type.toUpperCase()}
                            </span>
                            <br />
                            <span className="text-sm text-gray-300">
                              Strike: ${leg.strike} × {leg.quantity}
                            </span>
                          </div>
                          <div className="text-right">
                            <div className="text-lg font-bold text-green-400">
                              ${leg.premium.toFixed(2)}
                            </div>
                            <div className="text-sm text-gray-400">Premium</div>
                          </div>
                        </div>
                      </div>
                    ))}
                    
                    {/* P&L Summary */}
                    <div className="grid grid-cols-2 gap-4">
                      <div className="bg-green-900/30 border border-green-700 rounded-lg p-4 text-center">
                        <div className="text-2xl font-bold text-green-400">
                          ${calculationData.analysis.max_profit.toFixed(0)}
                        </div>
                        <div className="text-sm text-green-300">Max Profit</div>
                      </div>
                      
                      <div className="bg-red-900/30 border border-red-700 rounded-lg p-4 text-center">
                        <div className="text-2xl font-bold text-red-400">
                          ${Math.abs(calculationData.analysis.max_loss).toFixed(0)}
                        </div>
                        <div className="text-sm text-red-300">Max Loss</div>
                      </div>
                    </div>
                    
                    {/* Breakeven */}
                    {calculationData.analysis.breakeven_points.length > 0 && (
                      <div className="bg-yellow-900/30 border border-yellow-700 rounded-lg p-4">
                        <div className="font-medium text-yellow-300 mb-2">Breakeven Points</div>
                        {calculationData.analysis.breakeven_points.map((point, index) => (
                          <div key={index} className="text-yellow-200">
                            ${point.toFixed(2)}
                          </div>
                        ))}
                      </div>
                    )}
                    
                    {/* Probability */}
                    <div className="bg-blue-900/30 border border-blue-700 rounded-lg p-4 text-center">
                      <div className="text-xl font-bold text-blue-400">
                        {calculationData.analysis.probability_of_profit.toFixed(1)}%
                      </div>
                      <div className="text-sm text-blue-300">Probability of Profit</div>
                    </div>
                  </div>
                </div>
              )}
            </div>
            
            {/* Right Panel - P&L Chart și Greeks */}
            <div className="lg:col-span-2 space-y-6">
              
              {/* P&L Chart */}
              <div className="bg-gray-800 rounded-lg shadow-lg p-6 border border-gray-700">
                <h3 className="text-lg font-bold text-white mb-4 flex items-center">
                  <TrendingUp className="mr-2 text-blue-400" size={20} />
                  Profit & Loss Chart
                </h3>
                
                {loading && (
                  <div className="flex items-center justify-center h-64">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
                    <span className="ml-2 text-gray-300">Calculating...</span>
                  </div>
                )}
                
                {error && (
                  <div className="bg-red-900/30 border border-red-700 rounded-lg p-4">
                    <div className="flex items-center">
                      <div className="text-red-400 mr-2">⚠️</div>
                      <div className="text-red-300">{error}</div>
                    </div>
                  </div>
                )}
                
                {calculationData && !loading && !error && (
                  <div className="h-64 bg-gray-900 rounded-lg flex items-center justify-center border border-gray-600">
                    <div className="text-center">
                      <BarChart3 className="mx-auto mb-2 text-blue-400" size={48} />
                      <p className="text-gray-300 mb-2">Interactive P&L Chart</p>
                      <p className="text-sm text-gray-400">
                        Plotly.js integration coming în next phase
                      </p>
                      <div className="mt-4 text-xs text-gray-500">
                        Data ready: {calculationData.chart_data.x.length} price points
                      </div>
                    </div>
                  </div>
                )}
              </div>
              
              {/* Greeks */}
              {calculationData && (
                <div className="bg-gray-800 rounded-lg shadow-lg p-6 border border-gray-700">
                  <h3 className="text-lg font-bold text-white mb-4 flex items-center">
                    <Calculator className="mr-2 text-blue-400" size={20} />
                    Greeks Analysis
                  </h3>
                  
                  <div className="grid grid-cols-5 gap-4">
                    {Object.entries(calculationData.analysis.greeks).map(([greek, value]) => (
                      <div key={greek} className="bg-gray-700 rounded-lg p-4 text-center border border-gray-600">
                        <div className="text-lg font-bold text-white">
                          {typeof value === 'number' ? value.toFixed(3) : value}
                        </div>
                        <div className="text-sm text-gray-300 capitalize">
                          {greek}
                        </div>
                      </div>
                    ))}
                  </div>
                  
                  <div className="mt-4 text-sm text-gray-400 flex items-center">
                    <Info className="inline mr-1" size={14} />
                    Greeks calculated using Black-Scholes model în real-time
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Other tabs placeholder */}
        {activeTab !== 'builder' && (
          <div className="bg-gray-800 rounded-lg shadow-lg p-8 text-center border border-gray-700">
            <div className="mb-6">
              {activeTab === 'optimizer' && <Target className="mx-auto mb-4 text-blue-400" size={64} />}
              {activeTab === 'flow' && <Activity className="mx-auto mb-4 text-blue-400" size={64} />}
              {activeTab === 'portfolio' && <PieChart className="mx-auto mb-4 text-blue-400" size={64} />}
              
              <h4 className="text-2xl font-bold text-white mb-2 capitalize">
                {activeTab} Module
              </h4>
              <p className="text-gray-400 mb-6">
                This section will be implemented în next development phases
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default OptionsModule;