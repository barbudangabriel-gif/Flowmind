import React, { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import {
  ArrowLeft,
  TrendingUp,
  TrendingDown,
  Award,
  Shield,
  AlertTriangle,
  Target,
  BarChart3,
  Activity,
  DollarSign,
  RefreshCw,
  XCircle,
  CheckCircle,
  LineChart,
  PieChart,
  Zap,
  Calendar,
  Clock,
  TrendingUp as BullishIcon,
  TrendingDown as BearishIcon
} from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const StockAnalysisPage = () => {
  const { symbol } = useParams();
  const navigate = useNavigate();
  
  // State management
  const [loading, setLoading] = useState(true);
  const [analysis, setAnalysis] = useState(null);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('overview');
  const [optionsStrategies, setOptionsStrategies] = useState(null);
  const [optionsLoading, setOptionsLoading] = useState(false);
  
  // Load options strategies for the ticker
  const loadOptionsStrategies = useCallback(async () => {
    if (!symbol) return;
    
    setOptionsLoading(true);
    
    try {
      console.log(`Loading options strategies for ${symbol}`);
      
      // Fetch options strategies specific to this stock
      const response = await axios.get(`${API}/unusual-whales/trading-strategies`, {
        params: { symbol: symbol.toUpperCase() }
      });
      
      if (response.data?.strategies) {
        // Filter strategies specific to this symbol
        const symbolStrategies = response.data.strategies.filter(
          strategy => strategy.ticker?.toUpperCase() === symbol.toUpperCase()
        );
        setOptionsStrategies({
          strategies: symbolStrategies,
          total: symbolStrategies.length,
          symbol: symbol.toUpperCase()
        });
      } else {
        setOptionsStrategies({
          strategies: [],
          total: 0,
          symbol: symbol.toUpperCase()
        });
      }
      
    } catch (error) {
      console.error('Error loading options strategies:', error);
      setOptionsStrategies({
        strategies: [],
        total: 0,
        error: `Failed to load options strategies: ${error.message}`,
        symbol: symbol.toUpperCase()
      });
    } finally {
      setOptionsLoading(false);
    }
  }, [symbol]);

  // Load comprehensive analysis for the ticker
  const loadAnalysis = useCallback(async () => {
    if (!symbol) return;
    
    setLoading(true);
    setError(null);
    
    try {
      console.log(`Loading comprehensive analysis for ${symbol}`);
      
      // Fetch multiple types of analysis in parallel
      const [investmentRes, technicalRes, stockDataRes] = await Promise.allSettled([
        axios.post(`${API}/agents/investment-scoring`, {}, {
          params: { symbol: symbol.toUpperCase() }
        }),
        axios.post(`${API}/agents/technical-analysis`, {}, {
          params: { symbol: symbol.toUpperCase(), include_smc: true }
        }),
        axios.get(`${API}/stocks/${symbol.toUpperCase()}/enhanced`)
      ]);
      
      // Process results
      const analysisData = {
        symbol: symbol.toUpperCase(),
        investment: investmentRes.status === 'fulfilled' ? investmentRes.value.data : null,
        technical: technicalRes.status === 'fulfilled' ? technicalRes.value.data : null,
        stockData: stockDataRes.status === 'fulfilled' ? stockDataRes.value.data : null,
        timestamp: new Date().toISOString()
      };
      
      // Handle any errors
      if (investmentRes.status === 'rejected') {
        console.error('Investment analysis error:', investmentRes.reason);
      }
      if (technicalRes.status === 'rejected') {
        console.error('Technical analysis error:', technicalRes.reason);
      }
      if (stockDataRes.status === 'rejected') {
        console.error('Stock data error:', stockDataRes.reason);
      }
      
      setAnalysis(analysisData);
      
    } catch (error) {
      console.error('Error loading comprehensive analysis:', error);
      setError(`Failed to load analysis for ${symbol}: ${error.message}`);
    } finally {
      setLoading(false);
    }
  }, [symbol]);
  
  // Load data on component mount
  useEffect(() => {
    loadAnalysis();
  }, [loadAnalysis]);
  
  // Utility functions
  const getScoreColor = (score) => {
    if (score >= 85) return 'text-green-700';
    if (score >= 75) return 'text-green-600';
    if (score >= 65) return 'text-blue-600';
    if (score >= 55) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getRatingColor = (rating) => {
    switch (rating) {
      case 'BUY STRONG': return 'text-green-700 bg-green-100';
      case 'BUY': return 'text-green-600 bg-green-50';
      case 'HOLD +': return 'text-blue-600 bg-blue-50';
      case 'HOLD': return 'text-gray-600 bg-gray-50';
      case 'HOLD -': return 'text-yellow-600 bg-yellow-50';
      case 'AVOID': return 'text-red-600 bg-red-50';
      default: return 'text-gray-600 bg-gray-50';
    }
  };

  const getRiskColor = (risk) => {
    switch (risk) {
      case 'LOW': return 'text-green-700 bg-green-100';
      case 'MODERATE': return 'text-yellow-600 bg-yellow-100';
      case 'HIGH': return 'text-red-600 bg-red-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getVerdictColor = (verdict) => {
    switch (verdict?.toUpperCase()) {
      case 'STRONG BUY': return 'bg-green-900 text-green-300';
      case 'BUY': return 'bg-green-800 text-green-300';
      case 'HOLD': return 'bg-gray-600 text-gray-200';
      case 'SELL': return 'bg-red-800 text-red-300';
      case 'STRONG SELL': return 'bg-red-900 text-red-300';
      default: return 'bg-gray-600 text-gray-200';
    }
  };

  const getSignalColor = (signal) => {
    switch (signal?.toLowerCase()) {
      case 'bullish': return 'text-green-400';
      case 'bearish': return 'text-red-400';
      case 'neutral': return 'text-gray-400';
      default: return 'text-gray-400';
    }
  };

  // Loading state
  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <RefreshCw className="animate-spin mx-auto mb-4 text-blue-500" size={48} />
          <h2 className="text-2xl font-bold text-gray-800 mb-2">Loading Analysis</h2>
          <p className="text-gray-600">Fetching comprehensive data for {symbol?.toUpperCase()}...</p>
        </div>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center max-w-md">
          <XCircle className="mx-auto mb-4 text-red-500" size={48} />
          <h2 className="text-2xl font-bold text-gray-800 mb-2">Analysis Error</h2>
          <p className="text-gray-600 mb-4">{error}</p>
          <div className="space-x-4">
            <button
              onClick={() => navigate(-1)}
              className="bg-gray-600 text-white px-4 py-2 rounded-lg hover:bg-gray-700"
            >
              Go Back
            </button>
            <button
              onClick={loadAnalysis}
              className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
            >
              Retry
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-4">
              <button
                onClick={() => navigate(-1)}
                className="flex items-center space-x-2 text-gray-600 hover:text-gray-800 transition-colors"
              >
                <ArrowLeft size={20} />
                <span>Back</span>
              </button>
              <div className="h-6 w-px bg-gray-300"></div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900 flex items-center">
                  <Target className="mr-3 text-blue-600" size={28} />
                  {symbol?.toUpperCase()} Analysis
                </h1>
                <p className="text-sm text-gray-500">
                  Comprehensive investment and technical analysis
                </p>
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              <button
                onClick={loadAnalysis}
                className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 flex items-center space-x-2"
              >
                <RefreshCw size={16} />
                <span>Refresh</span>
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex space-x-8">
            {[
              { id: 'overview', label: '📊 Overview', icon: PieChart },
              { id: 'investment', label: '🎯 Investment Analysis', icon: Award },
              { id: 'technical', label: '📈 Technical Analysis', icon: BarChart3 },
              { id: 'options', label: '⚡ Options Strategies', icon: Zap },
              { id: 'charts', label: '📉 Charts', icon: LineChart },
              { id: 'fundamentals', label: '💼 Fundamentals', icon: DollarSign }
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
        {/* Overview Tab */}
        {activeTab === 'overview' && (
          <div className="space-y-8">
            {/* Key Metrics Cards */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
              {/* Stock Price */}
              <div className="bg-white rounded-lg shadow-md p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-500">Current Price</p>
                    <p className="text-3xl font-bold text-gray-900">
                      ${analysis?.stockData?.price?.toFixed(2) || 'N/A'}
                    </p>
                    <p className={`text-sm ${
                      (analysis?.stockData?.change || 0) >= 0 ? 'text-green-600' : 'text-red-600'
                    }`}>
                      {(analysis?.stockData?.change || 0) >= 0 ? '+' : ''}
                      {analysis?.stockData?.change?.toFixed(2) || '0.00'} (
                      {(analysis?.stockData?.change_percent || 0) >= 0 ? '+' : ''}
                      {analysis?.stockData?.change_percent?.toFixed(2) || '0.00'}%)
                    </p>
                  </div>
                  <DollarSign className="text-blue-500" size={24} />
                </div>
              </div>

              {/* Investment Score */}
              <div className="bg-white rounded-lg shadow-md p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-500">Investment Score</p>
                    <p className={`text-3xl font-bold ${getScoreColor(analysis?.investment?.investment_score || 0)}`}>
                      {analysis?.investment?.investment_score || 'N/A'}
                    </p>
                    <p className="text-sm text-gray-600">
                      {analysis?.investment?.recommendation || 'No Rating'}
                    </p>
                  </div>
                  <Award className="text-yellow-500" size={24} />
                </div>
              </div>

              {/* Technical Score */}
              <div className="bg-white rounded-lg shadow-md p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-500">Technical Score</p>
                    <p className={`text-3xl font-bold ${getScoreColor(analysis?.technical?.technical_score || 0)}`}>
                      {analysis?.technical?.technical_score || 'N/A'}
                    </p>
                    <p className="text-sm text-gray-600">
                      {analysis?.technical?.overall_verdict || 'No Verdict'}
                    </p>
                  </div>
                  <BarChart3 className="text-green-500" size={24} />
                </div>
              </div>

              {/* Risk Level */}
              <div className="bg-white rounded-lg shadow-md p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-500">Risk Level</p>
                    <p className={`text-2xl font-bold px-3 py-1 rounded-full ${getRiskColor(analysis?.investment?.risk_analysis?.overall_risk || 'MODERATE')}`}>
                      {(analysis?.investment?.risk_analysis?.overall_risk || 'MODERATE').toUpperCase()}
                    </p>
                    <p className="text-sm text-gray-600 mt-1">
                      Confidence: {(analysis?.investment?.confidence_level || 'medium').toUpperCase()}
                    </p>
                  </div>
                  <Shield className="text-purple-500" size={24} />
                </div>
              </div>
            </div>

            {/* Quick Summary */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="text-lg font-bold text-gray-900 mb-4">Quick Summary</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h4 className="font-semibold text-green-700 mb-2 flex items-center">
                    <CheckCircle size={16} className="mr-2" />
                    Key Strengths
                  </h4>
                  <div className="space-y-1">
                    {(analysis?.investment?.key_signals || [])
                      .filter(signal => signal.direction === 'bullish')
                      .slice(0, 3)
                      .map((signal, idx) => (
                        <div key={idx} className="text-sm text-gray-600 flex items-center">
                          <BullishIcon size={12} className="mr-2 text-green-500" />
                          {signal.type?.replace('_', ' ') || 'Positive Signal'}
                        </div>
                      ))}
                  </div>
                </div>
                
                <div>
                  <h4 className="font-semibold text-red-700 mb-2 flex items-center">
                    <AlertTriangle size={16} className="mr-2" />
                    Key Risks
                  </h4>
                  <div className="space-y-1">
                    {(analysis?.investment?.risk_analysis?.risk_factors || [])
                      .slice(0, 3)
                      .map((risk, idx) => (
                        <div key={idx} className="text-sm text-gray-600 flex items-center">
                          <BearishIcon size={12} className="mr-2 text-red-500" />
                          {risk}
                        </div>
                      ))}
                  </div>
                </div>
              </div>
            </div>

            {/* Chart Placeholder */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center">
                <LineChart className="mr-2" size={20} />
                Price Chart
              </h3>
              <div className="h-64 bg-gray-100 rounded-lg flex items-center justify-center">
                <div className="text-center text-gray-500">
                  <LineChart size={48} className="mx-auto mb-2" />
                  <p>Interactive chart will be implemented here</p>
                  <p className="text-sm">TradingView, Chart.js, or custom chart component</p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Investment Analysis Tab */}
        {activeTab === 'investment' && analysis?.investment && (
          <div className="space-y-8">
            {/* Investment Score Section */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="text-xl font-bold text-blue-600 mb-6 flex items-center">
                <Award className="mr-2" size={24} />
                🎯 Investment Scoring Analysis
              </h3>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
                <div className="text-center bg-gray-50 rounded-lg p-6">
                  <div className={`text-5xl font-bold ${getScoreColor(analysis.investment.investment_score || 0)}`}>
                    {analysis.investment.investment_score || 0}
                  </div>
                  <div className="text-gray-600 text-sm mt-2">Investment Score</div>
                </div>
                <div className="text-center bg-gray-50 rounded-lg p-6">
                  <div className={`text-xl font-bold px-4 py-2 rounded-full ${getRatingColor(analysis.investment.recommendation || 'HOLD')}`}>
                    {analysis.investment.recommendation || 'HOLD'}
                  </div>
                  <div className="text-gray-600 text-sm mt-2">Recommendation</div>
                </div>
                <div className="text-center bg-gray-50 rounded-lg p-6">
                  <div className={`text-xl font-bold px-4 py-2 rounded-full ${
                    analysis.investment.confidence_level === 'high' ? 'bg-green-100 text-green-700' :
                    analysis.investment.confidence_level === 'medium' ? 'bg-yellow-100 text-yellow-700' :
                    'bg-red-100 text-red-700'
                  }`}>
                    {(analysis.investment.confidence_level || 'low').toUpperCase()}
                  </div>
                  <div className="text-gray-600 text-sm mt-2">Confidence</div>
                </div>
              </div>

              {/* Key Signals */}
              {analysis.investment.key_signals && analysis.investment.key_signals.length > 0 && (
                <div className="mb-6">
                  <h4 className="text-lg font-semibold text-purple-700 mb-3">Key Signals</h4>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    {analysis.investment.key_signals.map((signal, index) => (
                      <div key={index} className="bg-gray-50 p-4 rounded-lg border">
                        <div className="flex justify-between items-center mb-2">
                          <span className="text-sm font-medium text-gray-700 capitalize">
                            {signal.type?.replace('_', ' ') || 'Unknown Signal'}
                          </span>
                          <span className={`text-xs px-2 py-1 rounded-full ${
                            signal.strength === 'strong' ? 'bg-red-100 text-red-700' :
                            signal.strength === 'moderate' ? 'bg-yellow-100 text-yellow-700' :
                            'bg-gray-100 text-gray-700'
                          }`}>
                            {signal.strength || 'weak'}
                          </span>
                        </div>
                        <div className={`text-sm font-bold ${getSignalColor(signal.direction)}`}>
                          {signal.score} - {signal.direction || 'neutral'}
                        </div>
                        {signal.details && (
                          <div className="text-xs text-gray-500 mt-1">
                            {signal.details}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Technical Analysis Tab */}
        {activeTab === 'technical' && analysis?.technical && (
          <div className="space-y-8">
            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="text-xl font-bold text-indigo-600 mb-6 flex items-center">
                <BarChart3 className="mr-2" size={24} />
                📊 Technical Analysis Expert
              </h3>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
                <div className="text-center bg-gray-50 rounded-lg p-6">
                  <div className={`text-5xl font-bold ${getScoreColor(analysis.technical.technical_score || 0)}`}>
                    {analysis.technical.technical_score || 0}
                  </div>
                  <div className="text-gray-600 text-sm mt-2">Technical Score</div>
                </div>
                <div className="text-center bg-gray-50 rounded-lg p-6">
                  <div className={`text-xl font-bold px-4 py-2 rounded-full ${getVerdictColor(analysis.technical.overall_verdict || 'NEUTRAL')}`}>
                    {analysis.technical.overall_verdict || 'NEUTRAL'}
                  </div>
                  <div className="text-gray-600 text-sm mt-2">Overall Verdict</div>
                </div>
                <div className="text-center bg-gray-50 rounded-lg p-6">
                  <div className="text-xl font-bold text-blue-600">
                    {analysis.technical.risk_reward_ratio || 'N/A'}
                  </div>
                  <div className="text-gray-600 text-sm mt-2">Risk/Reward</div>
                </div>
              </div>

              {/* Multi-timeframe Analysis */}
              {analysis.technical.multi_timeframe_analysis && (
                <div className="mb-6">
                  <h4 className="text-lg font-semibold text-indigo-700 mb-3">Multi-Timeframe Analysis</h4>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    {Object.entries(analysis.technical.multi_timeframe_analysis).map(([timeframe, data]) => (
                      <div key={timeframe} className="bg-gray-50 p-4 rounded-lg border">
                        <div className="text-sm font-medium text-gray-700 capitalize mb-2">
                          {timeframe}
                        </div>
                        <div className={`text-2xl font-bold ${getScoreColor(data.score)}`}>
                          {data.score}
                        </div>
                        <div className={`text-xs ${getSignalColor(data.signal)} font-medium`}>
                          {data.signal}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Charts Tab */}
        {activeTab === 'charts' && (
          <div className="space-y-8">
            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="text-xl font-bold text-gray-900 mb-6 flex items-center">
                <LineChart className="mr-2" size={24} />
                📉 Interactive Charts
              </h3>
              
              {/* Chart Controls */}
              <div className="flex flex-wrap gap-4 mb-6">
                <select className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500">
                  <option>1D</option>
                  <option>1W</option>
                  <option>1M</option>
                  <option>3M</option>
                  <option>1Y</option>
                </select>
                <select className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500">
                  <option>Candlestick</option>
                  <option>Line</option>
                  <option>Area</option>
                </select>
                <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
                  Add Indicators
                </button>
              </div>

              {/* Main Chart Placeholder */}
              <div className="h-96 bg-gray-100 rounded-lg flex items-center justify-center mb-6">
                <div className="text-center text-gray-500">
                  <LineChart size={64} className="mx-auto mb-4" />
                  <h4 className="text-lg font-semibold mb-2">Advanced Chart Component</h4>
                  <p>TradingView Chart, Chart.js, or Recharts integration</p>
                  <p className="text-sm mt-2">Features: Candlesticks, Volume, Technical Indicators, Drawing Tools</p>
                </div>
              </div>

              {/* Secondary Charts */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="h-48 bg-gray-100 rounded-lg flex items-center justify-center">
                  <div className="text-center text-gray-500">
                    <BarChart3 size={32} className="mx-auto mb-2" />
                    <p>Volume Chart</p>
                  </div>
                </div>
                <div className="h-48 bg-gray-100 rounded-lg flex items-center justify-center">
                  <div className="text-center text-gray-500">
                    <Activity size={32} className="mx-auto mb-2" />
                    <p>RSI Indicator</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Fundamentals Tab */}
        {activeTab === 'fundamentals' && (
          <div className="space-y-8">
            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="text-xl font-bold text-gray-900 mb-6 flex items-center">
                <DollarSign className="mr-2" size={24} />
                💼 Fundamental Analysis
              </h3>
              
              {/* Key Metrics */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mb-8">
                <div className="text-center">
                  <p className="text-sm text-gray-500">Market Cap</p>
                  <p className="text-xl font-bold text-gray-900">
                    {analysis?.stockData?.market_cap || 'N/A'}
                  </p>
                </div>
                <div className="text-center">
                  <p className="text-sm text-gray-500">P/E Ratio</p>
                  <p className="text-xl font-bold text-gray-900">
                    {analysis?.stockData?.pe_ratio || 'N/A'}
                  </p>
                </div>
                <div className="text-center">
                  <p className="text-sm text-gray-500">Volume</p>
                  <p className="text-xl font-bold text-gray-900">
                    {analysis?.stockData?.volume ? 
                      (analysis.stockData.volume / 1000000).toFixed(1) + 'M' : 'N/A'}
                  </p>
                </div>
                <div className="text-center">
                  <p className="text-sm text-gray-500">Sector</p>
                  <p className="text-xl font-bold text-gray-900">
                    {analysis?.stockData?.sector || 'N/A'}
                  </p>
                </div>
              </div>

              {/* Placeholder for more fundamental data */}
              <div className="bg-gray-100 rounded-lg p-6 text-center">
                <DollarSign size={48} className="mx-auto mb-4 text-gray-400" />
                <h4 className="text-lg font-semibold text-gray-700 mb-2">Extended Fundamentals</h4>
                <p className="text-gray-600">
                  Revenue, Earnings, Ratios, Financial Statements, Analyst Estimates
                </p>
                <p className="text-sm text-gray-500 mt-2">
                  Integration with financial data providers (Alpha Vantage, Financial Modeling Prep, etc.)
                </p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default StockAnalysisPage;