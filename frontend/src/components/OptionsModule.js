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
  Download
} from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const OptionsModule = () => {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('builder');
  const [selectedStrategy, setSelectedStrategy] = useState(null);
  const [loading, setLoading] = useState(false);

  // Mock data for development
  const strategyCategories = {
    novice: {
      label: 'Novice',
      count: 8,
      strategies: [
        'Long Call', 'Long Put', 'Covered Call', 'Cash-Secured Put', 'Protective Put'
      ]
    },
    intermediate: {
      label: 'Intermediate', 
      count: 16,
      strategies: [
        'Bull Call Spread', 'Bear Put Spread', 'Iron Condor', 'Iron Butterfly',
        'Straddle', 'Strangle', 'Calendar Spread'
      ]
    },
    advanced: {
      label: 'Advanced',
      count: 16, 
      strategies: [
        'Short Straddle', 'Jade Lizard', 'Call Ratio Spread', 'Put Broken Wing'
      ]
    },
    expert: {
      label: 'Expert',
      count: 14,
      strategies: [
        'Synthetic Future', 'Double Diagonal', 'Strip', 'Strap'
      ]
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-4">
              <button
                onClick={() => navigate('/')}
                className="flex items-center space-x-2 text-gray-600 hover:text-gray-800 transition-colors"
              >
                <ArrowLeft size={20} />
                <span>Back to Dashboard</span>
              </button>
              <div className="h-6 w-px bg-gray-300"></div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900 flex items-center">
                  <Zap className="mr-3 text-blue-600" size={28} />
                  Options Module
                </h1>
                <p className="text-sm text-gray-500">
                  Complete options trading toolkit - 54 strategies like OptionStrat
                </p>
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              <div className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm font-medium">
                🚧 In Development
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex space-x-8">
            {[
              { id: 'builder', label: '🏗️ Strategy Builder', icon: Calculator },
              { id: 'optimizer', label: '🎯 Optimizer', icon: Target },
              { id: 'flow', label: '🌊 Options Flow', icon: Activity },
              { id: 'portfolio', label: '📊 Portfolio', icon: PieChart },
              { id: 'education', label: '📚 Education', icon: BookOpen }
            ].map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center space-x-2 py-4 px-2 border-b-2 font-medium text-sm transition-colors ${
                    activeTab === tab.id
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
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
          <div className="space-y-8">
            {/* Strategy Categories */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
              {Object.entries(strategyCategories).map(([key, category]) => (
                <div key={key} className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-lg font-bold text-gray-900">{category.label}</h3>
                    <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded-full text-sm font-medium">
                      {category.count}
                    </span>
                  </div>
                  <div className="space-y-2 mb-4">
                    {category.strategies.slice(0, 3).map((strategy) => (
                      <div key={strategy} className="text-sm text-gray-600">
                        • {strategy}
                      </div>
                    ))}
                    {category.strategies.length > 3 && (
                      <div className="text-sm text-gray-500">
                        +{category.strategies.length - 3} more...
                      </div>
                    )}
                  </div>
                  <button className="w-full bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700 transition-colors">
                    Browse {category.label}
                  </button>
                </div>
              ))}
            </div>

            {/* Quick Strategy Builder */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="text-xl font-bold text-gray-900 mb-6 flex items-center">
                <Calculator className="mr-2" size={24} />
                Quick Strategy Builder
              </h3>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Select Symbol
                    </label>
                    <div className="relative">
                      <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={16} />
                      <input
                        type="text"
                        placeholder="e.g. AAPL, MSFT, SPY"
                        className="pl-10 w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      />
                    </div>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Market Outlook
                    </label>
                    <select className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500">
                      <option>Very Bullish</option>
                      <option>Bullish</option>
                      <option>Neutral</option>
                      <option>Bearish</option>
                      <option>Very Bearish</option>
                    </select>
                  </div>
                </div>

                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Strategy Type
                    </label>
                    <select className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500">
                      <option>Income</option>
                      <option>Directional</option>
                      <option>Volatility</option>
                      <option>Neutral</option>
                    </select>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Risk Level
                    </label>
                    <select className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500">
                      <option>Low</option>
                      <option>Medium</option>
                      <option>High</option>
                    </select>
                  </div>
                </div>

                <div className="flex flex-col justify-center space-y-4">
                  <button className="bg-green-600 text-white py-3 rounded-lg hover:bg-green-700 transition-colors flex items-center justify-center space-x-2">
                    <Target size={20} />
                    <span>Find Strategies</span>
                  </button>
                  
                  <button className="bg-blue-600 text-white py-3 rounded-lg hover:bg-blue-700 transition-colors flex items-center justify-center space-x-2">
                    <Calculator size={20} />
                    <span>Build Custom</span>
                  </button>
                </div>
              </div>
            </div>

            {/* Coming Soon Notice */}
            <div className="bg-gradient-to-br from-blue-50 to-indigo-100 rounded-xl p-8 text-center">
              <Zap className="mx-auto mb-4 text-blue-500" size={64} />
              <h4 className="text-2xl font-bold text-gray-800 mb-2">Full Strategy Builder Coming Soon</h4>
              <p className="text-gray-600 mb-6 max-w-2xl mx-auto">
                Implementation following the complete blueprint with all 54 strategies, interactive P&L charts, 
                and TradeStation + Unusual Whales integration.
              </p>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                <div className="bg-white rounded-lg p-4 shadow-sm">
                  <BarChart3 className="mx-auto mb-2 text-green-500" size={32} />
                  <h5 className="font-semibold text-gray-800">Interactive Charts</h5>
                  <p className="text-sm text-gray-600">Plotly.js profit/loss visualizations</p>
                </div>
                <div className="bg-white rounded-lg p-4 shadow-sm">
                  <Activity className="mx-auto mb-2 text-blue-500" size={32} />
                  <h5 className="font-semibold text-gray-800">Real-time Data</h5>
                  <p className="text-sm text-gray-600">TradeStation options chains & pricing</p>
                </div>
                <div className="bg-white rounded-lg p-4 shadow-sm">
                  <Target className="mx-auto mb-2 text-purple-500" size={32} />
                  <h5 className="font-semibold text-gray-800">AI Optimization</h5>
                  <p className="text-sm text-gray-600">Unusual Whales flow integration</p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Other tabs placeholder */}
        {activeTab !== 'builder' && (
          <div className="bg-white rounded-lg shadow-md p-8 text-center">
            <div className="mb-6">
              {activeTab === 'optimizer' && <Target className="mx-auto mb-4 text-blue-500" size={64} />}
              {activeTab === 'flow' && <Activity className="mx-auto mb-4 text-blue-500" size={64} />}
              {activeTab === 'portfolio' && <PieChart className="mx-auto mb-4 text-blue-500" size={64} />}
              {activeTab === 'education' && <BookOpen className="mx-auto mb-4 text-blue-500" size={64} />}
              
              <h4 className="text-2xl font-bold text-gray-800 mb-2 capitalize">
                {activeTab} Module
              </h4>
              <p className="text-gray-600 mb-6">
                This section will be implemented following the complete blueprint
              </p>
              
              <div className="bg-blue-50 rounded-lg p-4 text-left max-w-md mx-auto">
                <h5 className="font-semibold text-blue-800 mb-2">Planned Features:</h5>
                <ul className="text-sm text-blue-700 space-y-1">
                  {activeTab === 'optimizer' && (
                    <>
                      <li>• AI-powered strategy recommendations</li>
                      <li>• Market condition analysis</li>
                      <li>• Risk-adjusted optimization</li>
                    </>
                  )}
                  {activeTab === 'flow' && (
                    <>
                      <li>• Real-time unusual options activity</li>
                      <li>• Large trade monitoring</li>
                      <li>• Flow-based signals</li>
                    </>
                  )}
                  {activeTab === 'portfolio' && (
                    <>
                      <li>• Paper trading system</li>
                      <li>• Performance tracking</li>
                      <li>• Risk analysis</li>
                    </>
                  )}
                  {activeTab === 'education' && (
                    <>
                      <li>• Strategy explanations</li>
                      <li>• Interactive tutorials</li>
                      <li>• Risk/reward guides</li>
                    </>
                  )}
                </ul>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default OptionsModule;