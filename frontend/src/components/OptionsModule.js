import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import InteractiveOptionsChart from './InteractiveOptionsChart';
import OptionStrategyCard from './OptionStrategyCard';
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
  Maximize2,
  AlertCircle
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

  // Sentiment options pentru Optimizer - OptionStrat style
  const sentimentOptions = [
    { value: 'Very Bearish', color: 'bg-red-600', textColor: 'text-red-100' },
    { value: 'Bearish', color: 'bg-red-500', textColor: 'text-red-100' },
    { value: 'Neutral', color: 'bg-gray-600', textColor: 'text-gray-100' },
    { value: 'Directional', color: 'bg-purple-600', textColor: 'text-purple-100' },
    { value: 'Bullish', color: 'bg-green-500', textColor: 'text-green-100' },
    { value: 'Very Bullish', color: 'bg-green-600', textColor: 'text-green-100' }
  ];

  // Mock optimized strategies data - OptionStrat style results (6 strategies)
  const mockOptimizedStrategies = [
    {
      name: 'Long Call',
      strike: '635C',
      returnOnRisk: '87%',
      chance: '--',
      profit: '$1,362.94',
      risk: '$1,570',
      category: 'Novice',
      breakeven: '$653.48',
      probProfit: '45%'
    },
    {
      name: 'Bull Call Spread', 
      strikes: '646C/665C',
      returnOnRisk: '173%',
      chance: '--',
      profit: '$1,161.94',
      risk: '$671',
      category: 'Intermediate',
      breakeven: '$651.20',
      probProfit: '62%'
    },
    {
      name: 'Bull Put Spread',
      strikes: '643P/646P', 
      returnOnRisk: '63%',
      chance: '--',
      profit: '$116',
      risk: '$184',
      category: 'Intermediate',
      breakeven: '$644.84',
      probProfit: '73%'
    },
    {
      name: 'Short Put',
      strike: '625P',
      returnOnRisk: '3%',
      chance: '--',
      profit: '$332',
      risk: '$11,021.60',
      category: 'Advanced',
      breakeven: '$621.68',
      probProfit: '78%'
    },
    {
      name: 'Covered Call',
      strikes: 'Own + Sell 656C',
      returnOnRisk: '2.5%',
      chance: '--',
      profit: '$1,579',
      risk: '$64,021',
      category: 'Novice',
      breakeven: '$640.21',
      probProfit: '85%'
    },
    {
      name: 'Cash-Secured Put',
      strike: 'Sell 628P',
      returnOnRisk: '0.6%',  
      chance: '--',
      profit: '$378',
      risk: '$62,800',
      category: 'Novice',
      breakeven: '$624.22',
      probProfit: '82%'
    }
  ];

  const expirationDates = ['Dec 20', 'Dec 27', 'Jan 3', 'Jan 10', 'Jan 17', 'Jan 24'];

  // Optimizer function - Real API integration
  const runOptimizer = async () => {
    setOptimizing(true);
    setError(null);
    
    try {
      const response = await fetch(`${API}/options/optimize`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          symbol: symbol,
          stock_price: stockPrice,
          target_price: targetPrice,
          sentiment: optimizerSentiment,
          budget: budget,
          days_to_expiry: daysToExpiry,
          volatility: volatility,
          risk_free_rate: riskFreeRate
        })
      });

      if (!response.ok) {
        throw new Error(`Optimization failed: ${response.statusText}`);
      }

      const data = await response.json();
      
      // Convert API response to frontend format
      const convertedStrategies = data.strategies.map(strategy => ({
        name: strategy.name,
        strikes: strategy.strikes,
        returnOnRisk: `${strategy.return_on_risk.toFixed(1)}%`,
        chance: '--',
        profit: `$${strategy.max_profit.toFixed(2)}`,
        risk: `$${Math.abs(strategy.max_loss).toFixed(2)}`,
        category: strategy.category,
        breakeven: `$${strategy.breakeven.toFixed(2)}`,
        probProfit: `${strategy.prob_profit.toFixed(0)}%`,
        chartData: strategy.chart_data
      }));
      
      setOptimizedStrategies(convertedStrategies);
    } catch (error) {
      setError('Optimization failed: ' + error.message);
    } finally {
      setOptimizing(false);
    }
  };

  // Auto-calculate when parameters change
  useEffect(() => {
    if (selectedStrategy && symbol && stockPrice && strike) {
      calculateStrategy();
    }
  }, [selectedStrategy, symbol, stockPrice, strike, daysToExpiry, volatility, riskFreeRate]);

  const calculateStrategy = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`${API}/options/calculate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          strategy_name: selectedStrategy,
          symbol: symbol,
          stock_price: stockPrice,
          strike: strike,
          days_to_expiry: daysToExpiry,
          volatility: volatility,
          risk_free_rate: riskFreeRate
        })
      });

      if (!response.ok) {
        throw new Error(`Failed to calculate strategy: ${response.statusText}`);
      }

      const data = await response.json();
      setCalculationData(data);
    } catch (error) {
      setError(error.message);
      console.error('Strategy calculation error:', error);
    } finally {
      setLoading(false);
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

      {/* Main Content */}
      <div className="max-w-7xl mx-auto p-6">
        
        {/* BUILDER Tab - Real Strategy Builder */}
        {activeTab === 'builder' && (
          <div className="grid grid-cols-12 gap-6">
            
            {/* Left Panel - Strategy Controls */}
            <div className="col-span-12 lg:col-span-4 space-y-4">
              
              {/* Strategy Selection */}
              <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
                <label className="block text-sm font-medium text-gray-300 mb-3">Strategy</label>
                <select
                  value={selectedStrategy}
                  onChange={(e) => setSelectedStrategy(e.target.value)}
                  className="w-full bg-gray-700 border border-gray-600 rounded text-white px-3 py-2 focus:border-blue-500"
                >
                  <option value="Long Call">Long Call</option>
                  <option value="Long Put">Long Put</option>
                  <option value="Bull Call Spread">Bull Call Spread</option>
                  <option value="Bear Put Spread">Bear Put Spread</option>
                  <option value="Iron Condor">Iron Condor</option>
                  <option value="Long Straddle">Long Straddle</option>
                  <option value="Covered Call">Covered Call</option>
                </select>
              </div>

              {/* Symbol and Price */}
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
                  <div className="text-xs text-gray-400">Live</div>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">Stock Price</label>
                  <input
                    type="number"
                    value={stockPrice}
                    onChange={(e) => setStockPrice(parseFloat(e.target.value) || 0)}
                    className="w-full bg-gray-700 border border-gray-600 rounded text-white px-3 py-2 focus:border-blue-500"
                    step="0.01"
                  />
                </div>
              </div>

              {/* Strike Price */}
              <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
                <label className="block text-sm font-medium text-gray-300 mb-3">
                  Strike Price: <span className="text-white">${strike}</span>
                </label>
                <input
                  type="range"
                  min={stockPrice * 0.8}
                  max={stockPrice * 1.2}
                  step="1"
                  value={strike}
                  onChange={(e) => setStrike(parseFloat(e.target.value))}
                  className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer"
                />
                <div className="flex justify-between text-xs text-gray-400 mt-2">
                  <span>${(stockPrice * 0.8).toFixed(0)}</span>
                  <span>${(stockPrice * 1.2).toFixed(0)}</span>
                </div>
              </div>

              {/* Days to Expiry */}
              <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
                <label className="block text-sm font-medium text-gray-300 mb-3">Days to Expiry</label>
                <input
                  type="number"
                  value={daysToExpiry}
                  onChange={(e) => setDaysToExpiry(parseInt(e.target.value) || 30)}
                  className="w-full bg-gray-700 border border-gray-600 rounded text-white px-3 py-2 focus:border-blue-500"
                  min="1"
                  max="365"
                />
              </div>

              {/* Advanced Parameters */}
              <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
                <h4 className="text-sm font-medium text-gray-300 mb-3">Advanced Parameters</h4>
                
                <div className="space-y-3">
                  <div>
                    <label className="block text-xs text-gray-400 mb-1">
                      Implied Volatility: {(volatility * 100).toFixed(0)}%
                    </label>
                    <input
                      type="range"
                      min="0.1"
                      max="1.0"
                      step="0.01"
                      value={volatility}
                      onChange={(e) => setVolatility(parseFloat(e.target.value))}
                      className="w-full h-1 bg-gray-700 rounded-lg appearance-none cursor-pointer"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-xs text-gray-400 mb-1">
                      Risk-Free Rate: {(riskFreeRate * 100).toFixed(1)}%
                    </label>
                    <input
                      type="range"
                      min="0.01"
                      max="0.10"
                      step="0.001"
                      value={riskFreeRate}
                      onChange={(e) => setRiskFreeRate(parseFloat(e.target.value))}
                      className="w-full h-1 bg-gray-700 rounded-lg appearance-none cursor-pointer"
                    />
                  </div>
                </div>
              </div>

              {/* Calculate Button */}
              <button
                onClick={calculateStrategy}
                disabled={loading}
                className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 text-white py-3 px-4 rounded-lg font-semibold transition-colors flex items-center justify-center space-x-2"
              >
                {loading ? (
                  <>
                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                    <span>Calculating...</span>
                  </>
                ) : (
                  <>
                    <Calculator size={20} />
                    <span>Calculate Strategy</span>
                  </>
                )}
              </button>
            </div>

            {/* Right Panel - Chart and Analysis */}
            <div className="col-span-12 lg:col-span-8 space-y-4">
              
              {/* Error Message */}
              {error && (
                <div className="bg-red-900/50 border border-red-700 rounded-lg p-4 flex items-center space-x-3">
                  <AlertCircle className="text-red-400" size={20} />
                  <div className="text-red-300">{error}</div>
                </div>
              )}

              {/* Interactive P&L Chart */}
              {calculationData ? (
                <div className="space-y-4">
                  <InteractiveOptionsChart
                    chartData={calculationData.chart_data}
                    strategyName={calculationData.strategy_config.name}
                    stockPrice={stockPrice}
                    height={400}
                  />
                  
                  {/* Strategy Analysis */}
                  <div className="grid grid-cols-2 gap-4">
                    
                    {/* Key Metrics */}
                    <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
                      <h4 className="text-white font-semibold mb-4">Key Metrics</h4>
                      <div className="space-y-3">
                        <div className="flex justify-between">
                          <span className="text-gray-400">Max Profit</span>
                          <span className="text-green-400 font-semibold">
                            ${calculationData.analysis.max_profit.toFixed(2)}
                          </span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-400">Max Loss</span>
                          <span className="text-red-400 font-semibold">
                            ${Math.abs(calculationData.analysis.max_loss).toFixed(2)}
                          </span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-400">Breakeven</span>
                          <span className="text-yellow-400 font-semibold">
                            ${calculationData.analysis.breakeven_points[0]?.toFixed(2) || 'N/A'}
                          </span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-400">Prob. of Profit</span>
                          <span className="text-blue-400 font-semibold">
                            {calculationData.analysis.probability_of_profit.toFixed(1)}%
                          </span>
                        </div>
                      </div>
                    </div>

                    {/* Greeks */}
                    <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
                      <h4 className="text-white font-semibold mb-4">Greeks</h4>
                      <div className="space-y-3">
                        <div className="flex justify-between">
                          <span className="text-gray-400">Delta</span>
                          <span className="text-white font-mono">
                            {calculationData.analysis.greeks.delta.toFixed(3)}
                          </span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-400">Gamma</span>
                          <span className="text-white font-mono">
                            {calculationData.analysis.greeks.gamma.toFixed(3)}
                          </span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-400">Theta</span>
                          <span className="text-white font-mono">
                            {calculationData.analysis.greeks.theta.toFixed(2)}
                          </span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-400">Vega</span>
                          <span className="text-white font-mono">
                            {calculationData.analysis.greeks.vega.toFixed(2)}
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="bg-gray-800 rounded-lg p-8 text-center border border-gray-700">
                  <Calculator className="mx-auto mb-4 text-blue-400" size={64} />
                  <h4 className="text-2xl font-bold text-white mb-2">Strategy Builder</h4>
                  <p className="text-gray-400 mb-6">
                    Select your strategy parameters and click "Calculate Strategy" to see interactive P&L analysis
                  </p>
                  <div className="text-sm text-gray-500">
                    Current: {selectedStrategy} for {symbol} at ${stockPrice}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* OPTIMIZER Tab - OptionStrat Style */}
        {activeTab === 'optimizer' && (
          <div className="grid grid-cols-12 gap-6">
            
            {/* Left Panel - Optimizer Controls */}
            <div className="col-span-12 lg:col-span-4 space-y-4">
              
              {/* Symbol și Price */}
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

              {/* Sentiment Selector */}
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

              {/* Target Price */}
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

              {/* Budget */}
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

              {/* Ranking Mode */}
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

              {/* Optimize Button */}
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

            {/* Right Panel - Results */}
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
                    Select your market sentiment and target parameters, then click "Find Best Strategies" to discover optimal trades.
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
                    Analyzing thousands of potential trades for your parameters
                  </p>
                </div>
              )}

              {/* Results List - Using New OptionStrategyCard */}
              {optimizedStrategies.length > 0 && !optimizing && (
                <div className="space-y-4">
                  
                  {/* Strategies per page counter */}
                  <div className="flex items-center justify-between mb-6">
                    <div className="text-sm text-gray-400">
                      Showing {optimizedStrategies.length} strategies sorted by {rankingMode.toLowerCase()}
                    </div>
                    <div className="flex items-center space-x-2">
                      <button className="bg-gray-700 hover:bg-gray-600 text-gray-300 px-3 py-1 rounded text-sm transition-colors">
                        ← Previous
                      </button>
                      <span className="text-sm text-gray-400">Page 1 of 3</span>
                      <button className="bg-gray-700 hover:bg-gray-600 text-gray-300 px-3 py-1 rounded text-sm transition-colors">
                        Next →
                      </button>
                    </div>
                  </div>

                  {/* Strategy Cards using the new component */}
                  {optimizedStrategies.map((strategy, index) => {
                    // Convert strategy data to new card format
                    const cardStrategy = {
                      name: strategy.name,
                      strikes: strategy.strikes,
                      returnOnRisk: strategy.returnOnRisk,
                      chance: strategy.chance || '--',
                      profit: strategy.profit,
                      risk: strategy.risk,
                      category: strategy.category,
                      breakeven: strategy.breakeven,
                      probProfit: strategy.probProfit,
                      expiration: selectedExpiry,
                      chartData: strategy.chartData
                    };

                    return (
                      <OptionStrategyCard
                        key={index}
                        strategy={cardStrategy}
                        onOpenInBuilder={() => {
                          setSelectedStrategy(strategy.name);
                          setActiveTab('builder');
                        }}
                      />
                    );
                  })}


                  {/* Pagination Footer - OptionStrat style */}
                  <div className="flex items-center justify-center pt-6">
                    <div className="flex items-center space-x-4">
                      <button className="bg-gray-700 hover:bg-gray-600 text-gray-300 px-4 py-2 rounded text-sm transition-colors disabled:opacity-50" disabled>
                        ← Previous
                      </button>
                      <div className="flex items-center space-x-2">
                        <button className="bg-blue-600 text-white px-3 py-2 rounded text-sm">1</button>
                        <button className="bg-gray-700 hover:bg-gray-600 text-gray-300 px-3 py-2 rounded text-sm transition-colors">2</button>
                        <button className="bg-gray-700 hover:bg-gray-600 text-gray-300 px-3 py-2 rounded text-sm transition-colors">3</button>
                      </div>
                      <button className="bg-gray-700 hover:bg-gray-600 text-gray-300 px-4 py-2 rounded text-sm transition-colors">
                        Next →
                      </button>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Other tabs */}
        {(activeTab === 'flow' || activeTab === 'portfolio') && (
          <div className="bg-gray-800 rounded-lg p-8 text-center border border-gray-700">
            {activeTab === 'flow' && <Activity className="mx-auto mb-4 text-blue-400" size={64} />}
            {activeTab === 'portfolio' && <PieChart className="mx-auto mb-4 text-blue-400" size={64} />}
            
            <h4 className="text-2xl font-bold text-white mb-2 capitalize">
              {activeTab} Module
            </h4>
            <p className="text-gray-400 mb-6">
              This section will be implemented in next development phases
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default OptionsModule;