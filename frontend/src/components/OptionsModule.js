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
    }
  ];

  const expirationDates = ['Dec 20', 'Dec 27', 'Jan 3', 'Jan 10', 'Jan 17', 'Jan 24'];

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

  // Auto-calculate when parameters change
  useEffect(() => {
    if (selectedStrategy && symbol && stockPrice && strike) {
      // calculateStrategy(); // Commented out for now
    }
  }, [selectedStrategy, symbol, stockPrice, strike, daysToExpiry, volatility, riskFreeRate]);

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
        
        {/* BUILDER Tab (Simplified) */}
        {activeTab === 'builder' && (
          <div className="bg-gray-800 rounded-lg p-8 text-center border border-gray-700">
            <Calculator className="mx-auto mb-4 text-blue-400" size={64} />
            <h4 className="text-2xl font-bold text-white mb-2">Strategy Builder</h4>
            <p className="text-gray-400 mb-6">
              Complete strategy builder with real-time calculations coming soon
            </p>
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

              {/* Results List */}
              {optimizedStrategies.length > 0 && !optimizing && (
                <div className="space-y-3">
                  {optimizedStrategies.map((strategy, index) => (
                    <div key={index} className="bg-gray-800 rounded-lg p-4 border border-gray-700 hover:border-gray-600 transition-colors">
                      <div className="grid grid-cols-12 gap-4 items-center">
                        
                        {/* Strategy Info */}
                        <div className="col-span-4">
                          <div className="font-semibold text-white">{strategy.name}</div>
                          <div className="text-sm text-gray-400">
                            {strategy.strikes || strategy.strike}
                          </div>
                          <div className={`text-xs px-2 py-1 rounded mt-1 inline-block ${
                            strategy.category === 'Novice' ? 'bg-green-900/30 text-green-300' :
                            strategy.category === 'Intermediate' ? 'bg-blue-900/30 text-blue-300' :
                            'bg-purple-900/30 text-purple-300'
                          }`}>
                            {strategy.category}
                          </div>
                        </div>

                        {/* Return on Risk */}
                        <div className="col-span-2 text-center">
                          <div className="text-lg font-bold text-green-400">
                            {strategy.returnOnRisk}
                          </div>
                          <div className="text-xs text-gray-400">Return</div>
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
                        <div className="col-span-2">
                          <button 
                            onClick={() => {
                              setSelectedStrategy(strategy.name);
                              setActiveTab('builder');
                            }}
                            className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded text-sm transition-colors w-full"
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