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
import TradingChart from './TradingChart';

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
  
  // Load comprehensive analysis for the ticker
  const loadAnalysis = useCallback(async () => {
    if (!symbol) return;
    
    setLoading(true);
    setError(null);
    
    try {
      console.log(`Loading comprehensive analysis for ${symbol}`);
      
      // First, get the stock price from the same source as Top Picks (mock data with real prices)
      let stockPrice = null;
      let stockChange = 0;
      let stockChangePercent = 0;
      
      // Use consistent pricing logic - same as Top Picks mock data
      const mockPrices = {
        'UNH': 304.01,
        'CRM': 242.44,
        'AAPL': 231.59,
        'MSFT': 520.17,
        'NVDA': 180.45,
        'GOOGL': 165.32,
        'TSLA': 187.91,
        'AMZN': 225.73,
        'META': 528.45,
        'JPM': 212.34
      };
      
      // Use mock price if available, otherwise try API
      if (mockPrices[symbol.toUpperCase()]) {
        stockPrice = mockPrices[symbol.toUpperCase()];
        stockChange = (Math.random() - 0.5) * 10; // Random change for demo
        stockChangePercent = (stockChange / stockPrice) * 100;
        console.log(`Using consistent mock price for ${symbol}: $${stockPrice}`);
      } else {
        // Fallback to API for symbols not in mock data
        try {
          const priceResponse = await axios.get(`${API}/stocks/${symbol.toUpperCase()}/enhanced`);
          if (priceResponse.data?.price) {
            stockPrice = priceResponse.data.price;
            stockChange = priceResponse.data.change || 0;
            stockChangePercent = priceResponse.data.change_percent || 0;
          }
        } catch (priceError) {
          console.warn(`Could not get API price for ${symbol}, using default`);
          stockPrice = 100.00; // Default price
        }
      }
      
      // Fetch AI analysis in parallel (keeping original logic)
      const timestamp = Date.now();
      const [investmentRes, technicalRes] = await Promise.allSettled([
        axios.post(`${API}/agents/investment-scoring`, {}, {
          params: { symbol: symbol.toUpperCase(), _t: timestamp }
        }),
        axios.post(`${API}/agents/technical-analysis`, {}, {
          params: { symbol: symbol.toUpperCase(), include_smc: true, _t: timestamp }
        })
      ]);
      
      // Create consistent analysis data with synchronized price
      const analysisData = {
        symbol: symbol.toUpperCase(),
        investment: investmentRes.status === 'fulfilled' ? investmentRes.value.data : null,
        technical: technicalRes.status === 'fulfilled' ? technicalRes.value.data : null,
        stockData: {
          symbol: symbol.toUpperCase(),
          price: stockPrice,
          change: stockChange,
          change_percent: stockChangePercent,
          data_source: mockPrices[symbol.toUpperCase()] ? 'Consistent Mock Data' : 'API Fallback'
        },
        timestamp: new Date().toISOString()
      };
      
      // Handle any errors
      if (investmentRes.status === 'rejected') {
        console.error('Investment analysis error:', investmentRes.reason);
      }
      if (technicalRes.status === 'rejected') {
        console.error('Technical analysis error:', technicalRes.reason);
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
  
  // Utility functions for dark mode
  const getScoreColor = (score) => {
    if (score >= 85) return 'text-green-400';
    if (score >= 75) return 'text-green-500';
    if (score >= 65) return 'text-blue-400';
    if (score >= 55) return 'text-yellow-400';
    return 'text-red-400';
  };

  const getRatingColor = (rating) => {
    switch (rating) {
      case 'BUY STRONG': return 'text-green-300 bg-green-900';
      case 'BUY': return 'text-green-400 bg-green-800';
      case 'HOLD +': return 'text-blue-400 bg-blue-800';
      case 'HOLD': return 'text-gray-300 bg-gray-700';
      case 'HOLD -': return 'text-yellow-400 bg-yellow-800';
      case 'AVOID': return 'text-red-400 bg-red-800';
      default: return 'text-gray-300 bg-gray-700';
    }
  };

  const getRiskColor = (risk) => {
    switch (risk) {
      case 'LOW': return 'text-green-300 bg-green-900';
      case 'MODERATE': return 'text-yellow-300 bg-yellow-900';
      case 'HIGH': return 'text-red-300 bg-red-900';
      default: return 'text-gray-300 bg-gray-700';
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
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 flex items-center justify-center">
        <div className="text-center">
          <RefreshCw className="animate-spin mx-auto mb-4 text-blue-400" size={48} />
          <h2 className="text-2xl font-bold text-white mb-2">Se încarcă analiza</h2>
          <p className="text-gray-400">Obținerea datelor comprehensive pentru {symbol?.toUpperCase()}...</p>
        </div>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 flex items-center justify-center">
        <div className="text-center max-w-md">
          <XCircle className="mx-auto mb-4 text-red-400" size={48} />
          <h2 className="text-2xl font-bold text-white mb-2">Eroare Analiză</h2>
          <p className="text-gray-400 mb-4">{error}</p>
          <div className="space-x-4">
            <button
              onClick={() => navigate(-1)}
              className="bg-gray-600 text-white px-4 py-2 rounded-lg hover:bg-gray-700 transition-colors"
            >
              Înapoi
            </button>
            <button
              onClick={loadAnalysis}
              className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
            >
              Reîncearcă
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900">
      {/* Header */}
      <div className="bg-gray-800 shadow-sm border-b border-gray-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-4">
              <button
                onClick={() => navigate(-1)}
                className="flex items-center space-x-2 text-gray-300 hover:text-white transition-colors"
              >
                <ArrowLeft size={20} />
                <span>Înapoi la Scanner</span>
              </button>
              <div className="h-6 w-px bg-gray-600"></div>
              <div>
                <h1 className="text-2xl font-bold text-white flex items-center">
                  <Target className="mr-3 text-blue-400" size={28} />
                  {symbol?.toUpperCase()} - Analiză Detaliată
                </h1>
                <p className="text-sm text-gray-400">
                  Analiză comprehensivă de investiții și tehnică
                </p>
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              <div className="text-right">
                <div className="text-2xl font-bold text-white">
                  ${analysis?.stockData?.price?.toFixed(2) || 'N/A'}
                </div>
                <div className={`text-sm ${
                  (analysis?.stockData?.change || 0) >= 0 ? 'text-green-400' : 'text-red-400'
                }`}>
                  {(analysis?.stockData?.change || 0) >= 0 ? '+' : ''}
                  {analysis?.stockData?.change?.toFixed(2) || '0.00'} (
                  {(analysis?.stockData?.change_percent || 0) >= 0 ? '+' : ''}
                  {analysis?.stockData?.change_percent?.toFixed(2) || '0.00'}%)
                </div>
              </div>
              <button
                onClick={loadAnalysis}
                className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 flex items-center space-x-2 transition-colors"
              >
                <RefreshCw size={16} />
                <span>Refresh</span>
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="bg-gray-800 border-b border-gray-700">
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
                      ? 'border-blue-400 text-blue-400'
                      : 'border-transparent text-gray-400 hover:text-gray-200 hover:border-gray-500'
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
              <div className="bg-gray-800 rounded-lg shadow-md p-6 border border-gray-700">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-400">Preț Curent</p>
                    <p className="text-3xl font-bold text-white">
                      ${analysis?.stockData?.price?.toFixed(2) || 'N/A'}
                    </p>
                    <p className={`text-sm ${
                      (analysis?.stockData?.change || 0) >= 0 ? 'text-green-400' : 'text-red-400'
                    }`}>
                      {(analysis?.stockData?.change || 0) >= 0 ? '+' : ''}
                      {analysis?.stockData?.change?.toFixed(2) || '0.00'} (
                      {(analysis?.stockData?.change_percent || 0) >= 0 ? '+' : ''}
                      {analysis?.stockData?.change_percent?.toFixed(2) || '0.00'}%)
                    </p>
                  </div>
                  <DollarSign className="text-blue-400" size={24} />
                </div>
              </div>

              {/* Investment Score */}
              <div className="bg-gray-800 rounded-lg shadow-md p-6 border border-gray-700">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-400">Scor Investiție</p>
                    <p className={`text-3xl font-bold ${getScoreColor(analysis?.investment?.total_score || 0)}`}>
                      {analysis?.investment?.total_score?.toFixed(1) || 'N/A'}
                    </p>
                    <p className="text-sm text-gray-300">
                      {analysis?.investment?.rating || 'No Rating'}
                    </p>
                  </div>
                  <Award className="text-yellow-400" size={24} />
                </div>
              </div>

              {/* Technical Score */}
              <div className="bg-gray-800 rounded-lg shadow-md p-6 border border-gray-700">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-400">Scor Tehnic</p>
                    <p className={`text-3xl font-bold ${getScoreColor(analysis?.investment?.technical_score || 0)}`}>
                      {analysis?.investment?.technical_score?.toFixed(1) || 'N/A'}
                    </p>
                    <p className="text-sm text-gray-300">
                      {analysis?.investment?.technical_analysis?.trend_direction || 'No Verdict'}
                    </p>
                  </div>
                  <BarChart3 className="text-green-400" size={24} />
                </div>
              </div>

              {/* Risk Level */}
              <div className="bg-gray-800 rounded-lg shadow-md p-6 border border-gray-700">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-400">Nivel Risc</p>
                    <p className={`text-2xl font-bold px-3 py-1 rounded-full ${getRiskColor(analysis?.investment?.risk_level || 'MODERATE')}`}>
                      {(analysis?.investment?.risk_level || 'MODERATE').toUpperCase()}
                    </p>
                    <p className="text-sm text-gray-400 mt-1">
                      Orizont: {(analysis?.investment?.investment_horizon || 'medium-term').toUpperCase()}
                    </p>
                  </div>
                  <Shield className="text-purple-400" size={24} />
                </div>
              </div>
            </div>

            {/* Quick Summary */}
            <div className="bg-gray-800 rounded-lg shadow-md p-6 border border-gray-700">
              <h3 className="text-lg font-bold text-white mb-4">Rezumat Rapid</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h4 className="font-semibold text-green-400 mb-2 flex items-center">
                    <CheckCircle size={16} className="mr-2" />
                    Puncte Forte
                  </h4>
                  <div className="space-y-1">
                    {(analysis?.investment?.key_signals || [])
                      .filter(signal => signal.direction === 'bullish')
                      .slice(0, 3)
                      .map((signal, idx) => (
                        <div key={idx} className="text-sm text-gray-300 flex items-center">
                          <BullishIcon size={12} className="mr-2 text-green-400" />
                          {signal.type?.replace('_', ' ') || 'Semnal Pozitiv'}
                        </div>
                      ))}
                    {(analysis?.investment?.key_signals || []).filter(signal => signal.direction === 'bullish').length === 0 && (
                      <div className="text-sm text-gray-500">Nu s-au identificat semnale pozitive</div>
                    )}
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
                  <div className={`text-5xl font-bold ${getScoreColor(analysis.investment.total_score || 0)}`}>
                    {analysis.investment.total_score?.toFixed(1) || 0}
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
                  <div className={`text-xl font-bold px-4 py-2 rounded-full ${getVerdictColor(analysis.technical.recommendation || 'NEUTRAL')}`}>
                    {analysis.technical.recommendation || 'NEUTRAL'}
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
              {analysis.technical.timeframe_analysis && (
                <div className="mb-6">
                  <h4 className="text-lg font-semibold text-indigo-700 mb-3">Multi-Timeframe Analysis</h4>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    {Object.entries(analysis.technical.timeframe_analysis).map(([timeframe, data]) => (
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

        {/* Options Strategies Tab */}
        {activeTab === 'options' && (
          <div className="space-y-8">
            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="text-xl font-bold text-gray-900 mb-6 flex items-center">
                <Zap className="mr-2" size={24} />
                ⚡ Options Strategies for {symbol?.toUpperCase()}
              </h3>
              
              <div className="bg-gradient-to-br from-blue-50 to-indigo-100 rounded-xl p-8 text-center">
                <div className="mb-6">
                  <Zap className="mx-auto mb-4 text-blue-500" size={64} />
                  <h4 className="text-2xl font-bold text-gray-800 mb-2">Options Module Coming Soon</h4>
                  <p className="text-gray-600 mb-4">
                    Comprehensive options strategies and analysis for {symbol?.toUpperCase()} will be available in the dedicated options module.
                  </p>
                </div>
                
                <div className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                    <div className="bg-white rounded-lg p-4 shadow-sm">
                      <Target className="mx-auto mb-2 text-green-500" size={32} />
                      <h5 className="font-semibold text-gray-800">Strategy Recommendations</h5>
                      <p className="text-sm text-gray-600">AI-powered options strategies based on current analysis</p>
                    </div>
                    <div className="bg-white rounded-lg p-4 shadow-sm">
                      <BarChart3 className="mx-auto mb-2 text-blue-500" size={32} />
                      <h5 className="font-semibold text-gray-800">Risk/Reward Analysis</h5>
                      <p className="text-sm text-gray-600">Detailed P&L charts and risk assessments</p>
                    </div>
                    <div className="bg-white rounded-lg p-4 shadow-sm">
                      <Activity className="mx-auto mb-2 text-purple-500" size={32} />
                      <h5 className="font-semibold text-gray-800">Live Options Flow</h5>
                      <p className="text-sm text-gray-600">Real-time options activity for this ticker</p>
                    </div>
                  </div>
                  
                  <button
                    onClick={() => navigate('/options')}
                    className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white px-8 py-3 rounded-lg hover:from-blue-700 hover:to-indigo-700 transition-all duration-200 flex items-center space-x-2 mx-auto"
                  >
                    <Zap size={20} />
                    <span>Go to Options Module</span>
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Charts Tab */}
        {activeTab === 'charts' && (
          <div className="space-y-8">
            <div className="bg-gray-800 rounded-lg shadow-md p-6 border border-gray-700">
              <h3 className="text-xl font-bold text-white mb-6 flex items-center">
                <LineChart className="mr-2 text-blue-400" size={24} />
                📉 Grafice Interactive
              </h3>
              
              {/* Simple Price Chart Placeholder */}
              <div className="bg-gray-700 rounded-lg p-8 text-center border border-gray-600">
                <h4 className="text-lg font-semibold text-white mb-4">Grafic Preț {symbol?.toUpperCase()}</h4>
                <div className="bg-gray-800 rounded-lg p-6 min-h-[400px] flex items-center justify-center">
                  <div className="text-center">
                    <LineChart className="w-16 h-16 text-blue-400 mx-auto mb-4" />
                    <p className="text-gray-400 text-lg">Interactive chart pentru {symbol?.toUpperCase()}</p>
                    <p className="text-gray-500 text-sm mt-2">Preț curent: ${analysis?.stockData?.price?.toFixed(2) || 'N/A'}</p>
                    <div className="mt-4 grid grid-cols-2 gap-4 text-sm">
                      <div className="bg-gray-900 rounded p-3">
                        <div className="text-gray-400">Change</div>
                        <div className={`font-semibold ${(analysis?.stockData?.change || 0) >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                          {(analysis?.stockData?.change || 0) >= 0 ? '+' : ''}
                          {analysis?.stockData?.change?.toFixed(2) || '0.00'}
                        </div>
                      </div>
                      <div className="bg-gray-900 rounded p-3">
                        <div className="text-gray-400">Change %</div>
                        <div className={`font-semibold ${(analysis?.stockData?.change_percent || 0) >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                          {(analysis?.stockData?.change_percent || 0) >= 0 ? '+' : ''}
                          {analysis?.stockData?.change_percent?.toFixed(2) || '0.00'}%
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            
            {/* Chart Controls & Info */}
            <div className="bg-gray-800 rounded-lg shadow-md p-6 border border-gray-700">
              <h4 className="text-lg font-semibold text-white mb-4">Funcții Grafic</h4>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="bg-blue-900 rounded-lg p-4 border border-blue-800">
                  <BarChart3 className="text-blue-400 mb-2" size={24} />
                  <h5 className="font-semibold text-white">Analiză Candlestick</h5>
                  <p className="text-sm text-gray-400">Date OHLC cu analiză volum</p>
                </div>
                <div className="bg-green-900 rounded-lg p-4 border border-green-800">
                  <Activity className="text-green-400 mb-2" size={24} />
                  <h5 className="font-semibold text-white">Multiple Timeframes</h5>
                  <p className="text-sm text-gray-400">Intervale 1m, 5m, 15m, 1H, 1D</p>
                </div>
                <div className="bg-purple-900 rounded-lg p-4 border border-purple-800">
                  <Target className="text-purple-400 mb-2" size={24} />
                  <h5 className="font-semibold text-white">Date TradeStation</h5>
                  <p className="text-sm text-gray-400">Integrare date în timp real</p>
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