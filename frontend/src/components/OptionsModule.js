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
  Info,
  ChevronDown,
  Maximize2
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
  
  // Strategy parameters - OptionStrat style
  const [symbol, setSymbol] = useState('SPY');
  const [stockPrice, setStockPrice] = useState(643.48);
  const [strike, setStrike] = useState(645.0);
  const [daysToExpiry, setDaysToExpiry] = useState(30);
  const [volatility, setVolatility] = useState(0.25);
  const [riskFreeRate, setRiskFreeRate] = useState(0.05);
  const [selectedExpiry, setSelectedExpiry] = useState('Dec 20');

  // OPTIMIZER specific states - OptionStrat style
  const [optimizerSentiment, setOptimizerSentiment] = useState('Neutral');
  const [targetPrice, setTargetPrice] = useState(660.0);
  const [budget, setBudget] = useState(1000);
  const [targetDate, setTargetDate] = useState('Dec 20');
  const [rankingMode, setRankingMode] = useState('Max Return');
  const [optimizedStrategies, setOptimizedStrategies] = useState([]);
  const [optimizing, setOptimizing] = useState(false);

  // OptionStrat style strategy categories
  const strategyCategories = {
    'Novice': {
      color: 'bg-green-900/20 border-green-700',
      textColor: 'text-green-300',
      strategies: ['Long Call', 'Long Put', 'Covered Call', 'Cash-Secured Put', 'Protective Put']
    },
    'Intermediate': {
      color: 'bg-blue-900/20 border-blue-700', 
      textColor: 'text-blue-300',
      strategies: ['Bull Call Spread', 'Bear Put Spread', 'Iron Condor', 'Iron Butterfly', 'Straddle', 'Strangle']
    },
    'Advanced': {
      color: 'bg-purple-900/20 border-purple-700',
      textColor: 'text-purple-300', 
      strategies: ['Short Straddle', 'Jade Lizard', 'Call Ratio Spread', 'Put Broken Wing']
    },
    'Expert': {
      color: 'bg-red-900/20 border-red-700',
      textColor: 'text-red-300',
      strategies: ['Synthetic Future', 'Double Diagonal', 'Strip', 'Strap']
    }
  };

  // Sentiment options pentru Optimizer - OptionStrat style
  const sentimentOptions = [
    { value: 'Very Bearish', color: 'bg-red-600', textColor: 'text-red-100' },
    { value: 'Bearish', color: 'bg-red-500', textColor: 'text-red-100' },
    { value: 'Neutral', color: 'bg-gray-600', textColor: 'text-gray-100' },
    { value: 'Directional', color: 'bg-purple-600', textColor: 'text-purple-100' },
    { value: 'Bullish', color: 'bg-green-500', textColor: 'text-green-100' },
    { value: 'Very Bullish', color: 'bg-green-600', textColor: 'text-green-100' }
  ];

  // Mock optimized strategies data - OptionStrat style results
  const mockOptimizedStrategies = [
    {
      name: 'Long Call',
      strike: '635C',
      returnOnRisk: '87%',
      chance: '--',
      profit: '$1,362.94',
      risk: '$1,570',
      category: 'Novice'
    },
    {
      name: 'Bull Call Spread', 
      strikes: '646C/665C',
      returnOnRisk: '173%',
      chance: '--',
      profit: '$1,161.94',
      risk: '$671',
      category: 'Intermediate'
    },
    {
      name: 'Bull Put Spread',
      strikes: '643P/646P', 
      returnOnRisk: '63%',
      chance: '--',
      profit: '$116',
      risk: '$184',
      category: 'Intermediate'
    },
    {
      name: 'Short Put',
      strike: '625P',
      returnOnRisk: '3%',
      chance: '--',
      profit: '$332',
      risk: '$11,021.60',
      category: 'Advanced'
    }
  ];

  // Strike prices pentru selection - OptionStrat style
  const generateStrikes = (currentPrice) => {
    const strikes = [];
    const baseStrike = Math.round(currentPrice / 5) * 5; // Round to nearest 5
    for (let i = -10; i <= 10; i++) {
      strikes.push(baseStrike + (i * 5));
    }
    return strikes;
  };

  const availableStrikes = generateStrikes(stockPrice);
  const expirationDates = ['Dec 20', 'Dec 27', 'Jan 3', 'Jan 10', 'Jan 17', 'Jan 24', 'Jan 31'];

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

  const getStrategyCategory = (strategy) => {
    for (const [category, data] of Object.entries(strategyCategories)) {
      if (data.strategies.includes(strategy)) {
        return { category, ...data };
      }
    }
    return { category: 'Novice', ...strategyCategories.Novice };
  };

  const currentStrategyInfo = getStrategyCategory(selectedStrategy);

  // Optimizer function - OptionStrat style
  const runOptimizer = async () => {
    setOptimizing(true);
    setError(null);
    
    try {
      // Simulate API call pentru optimization
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      // Filter și rank strategies based on sentiment și parameters
      let filteredStrategies = [...mockOptimizedStrategies];
      
      // Apply sentiment filter
      if (optimizerSentiment === 'Very Bullish' || optimizerSentiment === 'Bullish') {
        filteredStrategies = filteredStrategies.filter(s => 
          s.name.includes('Call') || s.name.includes('Bull')
        );
      } else if (optimizerSentiment === 'Very Bearish' || optimizerSentiment === 'Bearish') {
        filteredStrategies = filteredStrategies.filter(s => 
          s.name.includes('Put') || s.name.includes('Bear')
        );
      }
      
      // Sort by ranking mode
      if (rankingMode === 'Max Return') {
        filteredStrategies.sort((a, b) => 
          parseFloat(b.returnOnRisk) - parseFloat(a.returnOnRisk)
        );
      }
      
      setOptimizedStrategies(filteredStrategies);
    } catch (error) {
      setError('Optimization failed: ' + error.message);
    } finally {
      setOptimizing(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-900">
      {/* OptionStrat style header */}
      <div className="bg-gray-800 border-b border-gray-700">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <button
                onClick={() => navigate('/')}
                className="text-gray-400 hover:text-white transition-colors"
              >
                <ArrowLeft size={20} />
              </button>
              <div>
                <h1 className="text-xl font-bold text-white flex items-center">
                  <Zap className="mr-2 text-blue-500" size={24} />
                  FlowMind Options
                </h1>
                <p className="text-sm text-gray-400">The Option Trader's Toolkit</p>
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              <div className="bg-green-900 text-green-300 px-3 py-1 rounded text-sm border border-green-700">
                ✅ Live Data
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Navigation Tabs - OptionStrat style */}
      <div className="bg-gray-800 border-b border-gray-700">
        <div className="max-w-7xl mx-auto px-6">
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

      {/* Main OptionStrat-style layout */}
      <div className="max-w-7xl mx-auto p-6">
        
        {/* BUILDER Tab */}
        {activeTab === 'builder' && (
          <div className="grid grid-cols-12 gap-6">
          
            {/* Left Panel - OptionStrat style controls */}
            <div className="col-span-12 lg:col-span-4 space-y-4">
            
            {/* Symbol și Price - OptionStrat style */}
            <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center space-x-3">
                  <div className="relative">
                    <input
                      type="text"
                      value={symbol}
                      onChange={(e) => setSymbol(e.target.value.toUpperCase())}
                      className="bg-gray-700 text-white px-3 py-2 rounded border border-gray-600 focus:border-blue-500 w-20 text-center font-bold"
                      placeholder="SPY"
                    />
                  </div>
                  <div className="text-right">
                    <div className="text-2xl font-bold text-white">${stockPrice}</div>
                    <div className="text-sm text-green-400">+0.23% +$1.47</div>
                  </div>
                </div>
                <div className="text-xs text-gray-400">Delayed</div>
              </div>
            </div>

            {/* Strategy Selection - OptionStrat style */}
            <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
              <label className="block text-sm font-medium text-gray-300 mb-3">Strategy</label>
              
              {/* Strategy categories */}
              <div className="space-y-2 mb-4">
                {Object.entries(strategyCategories).map(([category, data]) => (
                  <div key={category} className={`rounded p-2 border ${data.color}`}>
                    <div className={`text-xs font-semibold ${data.textColor} mb-1`}>
                      {category}
                    </div>
                    <div className="grid grid-cols-1 gap-1">
                      {data.strategies.slice(0, 2).map((strategy) => (
                        <button
                          key={strategy}
                          onClick={() => setSelectedStrategy(strategy)}
                          className={`text-left text-xs p-1 rounded transition-colors ${
                            selectedStrategy === strategy 
                              ? 'bg-blue-600 text-white' 
                              : 'text-gray-300 hover:bg-gray-700'
                          } ${!['Long Call', 'Long Put'].includes(strategy) ? 'opacity-50 cursor-not-allowed' : ''}`}
                          disabled={!['Long Call', 'Long Put'].includes(strategy)}
                        >
                          {strategy}
                        </button>
                      ))}
                    </div>
                  </div>
                ))}
              </div>

              {/* Current strategy display */}
              <div className={`rounded p-3 border ${currentStrategyInfo.color}`}>
                <div className={`font-semibold ${currentStrategyInfo.textColor}`}>
                  {selectedStrategy}
                </div>
                <div className="text-xs text-gray-400 mt-1">
                  {currentStrategyInfo.category} Strategy
                </div>
              </div>
            </div>

            {/* Strike Selection - OptionStrat style */}
            <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
              <label className="block text-sm font-medium text-gray-300 mb-3">Strike Price</label>
              <div className="grid grid-cols-3 gap-2 max-h-40 overflow-y-auto">
                {availableStrikes.map((strikePrice) => (
                  <button
                    key={strikePrice}
                    onClick={() => setStrike(strikePrice)}
                    className={`text-sm p-2 rounded border transition-colors ${
                      strike === strikePrice
                        ? 'bg-blue-600 text-white border-blue-500'
                        : 'bg-gray-700 text-gray-300 border-gray-600 hover:bg-gray-600'
                    }`}
                  >
                    ${strikePrice}
                  </button>
                ))}
              </div>
            </div>

            {/* Expiration Selection - OptionStrat style */}
            <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
              <label className="block text-sm font-medium text-gray-300 mb-3">Expiration</label>
              <div className="grid grid-cols-2 gap-2">
                {expirationDates.map((date) => (
                  <button
                    key={date}
                    onClick={() => setSelectedExpiry(date)}
                    className={`text-sm p-2 rounded border transition-colors ${
                      selectedExpiry === date
                        ? 'bg-blue-600 text-white border-blue-500'
                        : 'bg-gray-700 text-gray-300 border-gray-600 hover:bg-gray-600'
                    }`}
                  >
                    {date}
                  </button>
                ))}
              </div>
            </div>

            {/* Advanced Parameters - Collapsible */}
            <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
              <details className="group">
                <summary className="flex items-center justify-between cursor-pointer text-sm font-medium text-gray-300 mb-3">
                  <span>Advanced Parameters</span>
                  <ChevronDown className="w-4 h-4 group-open:rotate-180 transition-transform" />
                </summary>
                <div className="space-y-3 mt-3">
                  <div>
                    <label className="block text-xs text-gray-400 mb-1">Volatility (%)</label>
                    <input
                      type="number"
                      value={volatility * 100}
                      onChange={(e) => setVolatility(e.target.value / 100)}
                      className="w-full bg-gray-700 text-white px-2 py-1 rounded border border-gray-600 text-sm"
                      step="1"
                    />
                  </div>
                  <div>
                    <label className="block text-xs text-gray-400 mb-1">Risk-Free Rate (%)</label>
                    <input
                      type="number"
                      value={riskFreeRate * 100}
                      onChange={(e) => setRiskFreeRate(e.target.value / 100)}
                      className="w-full bg-gray-700 text-white px-2 py-1 rounded border border-gray-600 text-sm"
                      step="0.1"
                    />
                  </div>
                  <div>
                    <label className="block text-xs text-gray-400 mb-1">Days to Expiry</label>
                    <input
                      type="number"
                      value={daysToExpiry}
                      onChange={(e) => setDaysToExpiry(e.target.value)}
                      className="w-full bg-gray-700 text-white px-2 py-1 rounded border border-gray-600 text-sm"
                    />
                  </div>
                </div>
              </details>
            </div>
          </div>

          {/* Right Panel - Chart și Analysis (OptionStrat style) */}
          <div className="col-span-12 lg:col-span-8">
            
            {/* Main P&L Chart - OptionStrat style */}
            <div className="bg-gray-800 rounded-lg border border-gray-700 mb-4">
              <div className="flex items-center justify-between p-4 border-b border-gray-700">
                <h3 className="text-white font-semibold">Profit & Loss</h3>
                <div className="flex items-center space-x-2">
                  <button className="text-gray-400 hover:text-white">
                    <Maximize2 size={16} />
                  </button>
                </div>
              </div>
              
              <div className="p-4">
                {loading && (
                  <div className="h-80 flex items-center justify-center">
                    <div className="text-center">
                      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto mb-2"></div>
                      <div className="text-gray-400">Calculating...</div>
                    </div>
                  </div>
                )}

                {error && (
                  <div className="h-80 flex items-center justify-center">
                    <div className="text-center text-red-400">
                      <div className="mb-2">⚠️</div>
                      <div>{error}</div>
                    </div>
                  </div>
                )}

                {calculationData && !loading && !error && (
                  <div className="h-80 bg-gray-900 rounded border border-gray-600 flex items-center justify-center">
                    <div className="text-center">
                      <BarChart3 className="mx-auto mb-3 text-blue-400" size={48} />
                      <div className="text-white font-semibold mb-2">Interactive P&L Chart</div>
                      <div className="text-gray-400 text-sm">
                        Ready pentru Plotly.js integration
                      </div>
                      <div className="text-xs text-gray-500 mt-2">
                        {calculationData.chart_data.x.length} price points calculated
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* Analysis Results - OptionStrat style */}
            {calculationData && (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-4">
                
                {/* Max Profit */}
                <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
                  <div className="text-xs text-gray-400 mb-1">MAX PROFIT</div>
                  <div className="text-lg font-bold text-green-400">
                    ${calculationData.analysis.max_profit.toFixed(0)}
                  </div>
                  <div className="text-xs text-gray-500">
                    {calculationData.analysis.max_profit > 10000 ? 'Unlimited' : 'Limited'}
                  </div>
                </div>

                {/* Max Loss */}
                <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
                  <div className="text-xs text-gray-400 mb-1">MAX LOSS</div>
                  <div className="text-lg font-bold text-red-400">
                    ${Math.abs(calculationData.analysis.max_loss).toFixed(0)}
                  </div>
                  <div className="text-xs text-gray-500">Limited</div>
                </div>

                {/* Breakeven */}
                <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
                  <div className="text-xs text-gray-400 mb-1">BREAKEVEN</div>
                  <div className="text-lg font-bold text-yellow-400">
                    {calculationData.analysis.breakeven_points.length > 0 
                      ? `$${calculationData.analysis.breakeven_points[0].toFixed(2)}`
                      : 'N/A'
                    }
                  </div>
                  <div className="text-xs text-gray-500">At Expiration</div>
                </div>

                {/* Probability of Profit */}
                <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
                  <div className="text-xs text-gray-400 mb-1">PROB OF PROFIT</div>
                  <div className="text-lg font-bold text-blue-400">
                    {calculationData.analysis.probability_of_profit.toFixed(1)}%
                  </div>
                  <div className="text-xs text-gray-500">Estimated</div>
                </div>
              </div>
            )}

            {/* Greeks - OptionStrat style */}
            {calculationData && (
              <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
                <h4 className="text-white font-semibold mb-3">Greeks</h4>
                <div className="grid grid-cols-5 gap-4">
                  {Object.entries(calculationData.analysis.greeks).map(([greek, value]) => (
                    <div key={greek} className="text-center">
                      <div className="text-xs text-gray-400 mb-1">{greek.toUpperCase()}</div>
                      <div className="text-sm font-mono text-white">
                        {typeof value === 'number' ? value.toFixed(3) : value}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Strategy Details - OptionStrat style */}
            {calculationData && (
              <div className="bg-gray-800 rounded-lg p-4 border border-gray-700 mt-4">
                <h4 className="text-white font-semibold mb-3">Strategy Details</h4>
                <div className="space-y-2">
                  {calculationData.strategy_config.legs.map((leg, index) => (
                    <div key={index} className="flex items-center justify-between p-2 bg-gray-700 rounded">
                      <div className="flex items-center space-x-3">
                        <div className={`w-3 h-3 rounded-full ${
                          leg.action === 'buy' ? 'bg-green-400' : 'bg-red-400'
                        }`}></div>
                        <span className="text-white text-sm">
                          {leg.action.toUpperCase()} {leg.option_type.toUpperCase()}
                        </span>
                        <span className="text-gray-300 text-sm">
                          ${leg.strike}
                        </span>
                      </div>
                      <div className="text-right">
                        <div className="text-white font-mono text-sm">
                          ${leg.premium.toFixed(2)}
                        </div>
                        <div className="text-xs text-gray-400">Premium</div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* OPTIMIZER Tab - OptionStrat Style */}
        {activeTab === 'optimizer' && (
          <div className="grid grid-cols-12 gap-6">
            
            {/* Left Panel - Optimizer Controls */}
            <div className="col-span-12 lg:col-span-4 space-y-4">
              
              {/* Symbol și Price - Same as builder */}
              <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center space-x-3">
                    <div className="relative">
                      <input
                        type="text"
                        value={symbol}
                        onChange={(e) => setSymbol(e.target.value.toUpperCase())}
                        className="bg-gray-700 text-white px-3 py-2 rounded border border-gray-600 focus:border-blue-500 w-20 text-center font-bold"
                        placeholder="SPY"
                      />
                    </div>
                    <div className="text-right">
                      <div className="text-2xl font-bold text-white">${stockPrice}</div>
                      <div className="text-sm text-green-400">+0.23% +$1.47</div>
                    </div>
                  </div>
                  <div className="text-xs text-gray-400">Delayed</div>
                </div>
              </div>

              {/* Sentiment Selector - OptionStrat style */}
              <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
                <label className="block text-sm font-medium text-gray-300 mb-3">Market Sentiment</label>
                <div className="grid grid-cols-2 gap-2">
                  {sentimentOptions.map((sentiment) => (
                    <button
                      key={sentiment.value}
                      onClick={() => setOptimizerSentiment(sentiment.value)}
                      className={`p-2 rounded text-sm font-medium transition-colors ${
                        optimizerSentiment === sentiment.value
                          ? `${sentiment.color} ${sentiment.textColor}`
                          : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                      }`}
                    >
                      {sentiment.value}
                    </button>
                  ))}
                </div>
              </div>

              {/* Target Price - OptionStrat style */}
              <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
                <label className="block text-sm font-medium text-gray-300 mb-3">
                  Target Price: <span className="text-white">${targetPrice}</span>
                  <span className="text-green-400 text-xs ml-2">
                    (+{(((targetPrice - stockPrice) / stockPrice) * 100).toFixed(1)}%)
                  </span>
                </label>
                <input
                  type="range"
                  min={stockPrice * 0.8}
                  max={stockPrice * 1.2}
                  step="0.5"
                  value={targetPrice}
                  onChange={(e) => setTargetPrice(parseFloat(e.target.value))}
                  className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer"
                />
                <div className="flex justify-between text-xs text-gray-400 mt-2">
                  <span>${(stockPrice * 0.8).toFixed(0)}</span>
                  <span>${(stockPrice * 1.2).toFixed(0)}</span>
                </div>
              </div>

              {/* Budget Constraint - OptionStrat style */}
              <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
                <label className="block text-sm font-medium text-gray-300 mb-3">Budget</label>
                <div className="relative">
                  <DollarSign className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={16} />
                  <input
                    type="number"
                    value={budget}
                    onChange={(e) => setBudget(parseInt(e.target.value) || 0)}
                    className="w-full pl-10 pr-3 py-2 bg-gray-700 border border-gray-600 rounded text-white"
                    placeholder="1000"
                  />
                </div>
              </div>

              {/* Ranking Mode - OptionStrat style */}
              <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
                <label className="block text-sm font-medium text-gray-300 mb-3">Ranking</label>
                <div className="grid grid-cols-2 gap-2">
                  {['Max Return', 'Max Chance'].map((mode) => (
                    <button
                      key={mode}
                      onClick={() => setRankingMode(mode)}
                      className={`text-sm p-2 rounded border transition-colors ${
                        rankingMode === mode
                          ? 'bg-yellow-600 text-white border-yellow-500'
                          : 'bg-gray-700 text-gray-300 border-gray-600 hover:bg-gray-600'
                      }`}
                    >
                      {mode}
                    </button>
                  ))}
                </div>
              </div>

              {/* Optimize Button - OptionStrat style */}
              <button
                onClick={runOptimizer}
                disabled={optimizing}
                className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 text-white py-3 px-4 rounded-lg font-semibold transition-colors flex items-center justify-center space-x-2"
              >
                {optimizing ? (
                  <>
                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                    <span>Optimizing...</span>
                  </>
                ) : (
                  <>
                    <Target size={20} />
                    <span>Find Best Strategies</span>
                  </>
                )}
              </button>
            </div>

            {/* Right Panel - Optimized Results */}
            <div className="col-span-12 lg:col-span-8">
              
              {/* Results Header */}
              <div className="bg-gray-800 rounded-lg p-4 border border-gray-700 mb-4">
                <div className="flex items-center justify-between">
                  <h3 className="text-white font-semibold">Optimized Strategies</h3>
                  <div className="flex items-center space-x-2 text-sm text-gray-400">
                    <span>Ranked by: {rankingMode}</span>
                    {optimizedStrategies.length > 0 && (
                      <span className="bg-blue-600 text-white px-2 py-1 rounded text-xs">
                        {optimizedStrategies.length} results
                      </span>
                    )}
                  </div>
                </div>
              </div>

              {/* No results state */}
              {optimizedStrategies.length === 0 && !optimizing && (
                <div className="bg-gray-800 rounded-lg border border-gray-700 p-8 text-center">
                  <Target className="mx-auto mb-4 text-gray-500" size={48} />
                  <h4 className="text-lg font-semibold text-white mb-2">Ready to Optimize</h4>
                  <p className="text-gray-400 mb-4">
                    Select your market sentiment și target parameters, then click "Find Best Strategies" to discover optimal trades.
                  </p>
                  <div className="text-sm text-gray-500">
                    Current setup: {optimizerSentiment} outlook targeting ${targetPrice}
                  </div>
                </div>
              )}

              {/* Loading state */}
              {optimizing && (
                <div className="bg-gray-800 rounded-lg border border-gray-700 p-8 text-center">
                  <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
                  <h4 className="text-lg font-semibold text-white mb-2">Scanning Strategies...</h4>
                  <p className="text-gray-400">
                    Analyzing thousands of potential trades pentru your parameters
                  </p>
                </div>
              )}

              {/* Results List - OptionStrat style */}
              {optimizedStrategies.length > 0 && !optimizing && (
                <div className="space-y-3">
                  {optimizedStrategies.map((strategy, index) => (
                    <div key={index} className="bg-gray-800 rounded-lg p-4 border border-gray-700 hover:border-gray-600 transition-colors">
                      <div className="grid grid-cols-12 gap-4 items-center">
                        
                        {/* Strategy Info */}
                        <div className="col-span-3">
                          <div className="font-semibold text-white">{strategy.name}</div>
                          <div className="text-sm text-gray-400">
                            {strategy.strikes || strategy.strike}
                          </div>
                          <div className={`text-xs px-2 py-1 rounded mt-1 inline-block ${
                            strategy.category === 'Novice' ? 'bg-green-900/30 text-green-300' :
                            strategy.category === 'Intermediate' ? 'bg-blue-900/30 text-blue-300' :
                            strategy.category === 'Advanced' ? 'bg-purple-900/30 text-purple-300' :
                            'bg-red-900/30 text-red-300'
                          }`}>
                            {strategy.category}
                          </div>
                        </div>

                        {/* Return on Risk */}
                        <div className="col-span-2 text-center">
                          <div className="text-lg font-bold text-green-400">
                            {strategy.returnOnRisk}
                          </div>
                          <div className="text-xs text-gray-400">Return on Risk</div>
                        </div>

                        {/* Chance */}
                        <div className="col-span-2 text-center">
                          <div className="text-lg font-bold text-blue-400">
                            {strategy.chance}
                          </div>
                          <div className="text-xs text-gray-400">Chance</div>
                        </div>

                        {/* Profit */}
                        <div className="col-span-2 text-center">
                          <div className="text-lg font-bold text-green-400">
                            {strategy.profit}
                          </div>
                          <div className="text-xs text-gray-400">Profit</div>
                        </div>

                        {/* Risk */}
                        <div className="col-span-2 text-center">
                          <div className="text-lg font-bold text-red-400">
                            {strategy.risk}
                          </div>
                          <div className="text-xs text-gray-400">Risk</div>
                        </div>

                        {/* Action */}
                        <div className="col-span-1">
                          <button 
                            onClick={() => {
                              setSelectedStrategy(strategy.name);
                              setActiveTab('builder');
                            }}
                            className="bg-blue-600 hover:bg-blue-700 text-white px-3 py-1 rounded text-sm transition-colors"
                          >
                            Build
                          </button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}

        {/* Other tabs placeholder */}
        {(activeTab === 'flow' || activeTab === 'portfolio') && (
          <div className="bg-gray-800 rounded-lg p-8 text-center border border-gray-700">
            <div className="mb-6">
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