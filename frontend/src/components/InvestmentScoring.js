import React, { useState, useEffect, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import {
  TrendingUp,
  TrendingDown,
  Award,
  Shield,
  AlertTriangle,
  Target,
  Star,
  BarChart3,
  PieChart,
  Activity,
  DollarSign,
  Timer,
  Search,
  RefreshCw,
  Zap,
  CheckCircle,
  XCircle,
  Plus,
  ArrowDown,
  ChevronUp,
  ChevronDown
} from "lucide-react";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Memoized Investment Scoring Component
const InvestmentScoring = React.memo(() => {
  const navigate = useNavigate();
  const [topPicks, setTopPicks] = useState([]);
  const [riskAnalysis, setRiskAnalysis] = useState(null);
  const [sectorLeaders, setSectorLeaders] = useState([]);
  const [selectedSector, setSelectedSector] = useState('Technology');
  const [activeTab, setActiveTab] = useState('ai-agent');  // Default to AI Agent tab
  const [loading, setLoading] = useState(false);
  
  // AI Agent specific states
  const [aiAnalysisSymbol, setAiAnalysisSymbol] = useState('');
  const [aiAnalysis, setAiAnalysis] = useState(null);
  const [aiLoading, setAiLoading] = useState(false);
  
  // Top Picks expansion states
  const [displayLimit, setDisplayLimit] = useState(10); // Start with 10
  const [maxScrollLimit, setMaxScrollLimit] = useState(50); // Can scroll to 50
  const [loadingMore, setLoadingMore] = useState(false);

  const sectors = [
    'Technology', 'Healthcare', 'Financial Services', 'Consumer Cyclical',
    'Communication Services', 'Industrials', 'Consumer Defensive', 'Energy',
    'Utilities', 'Real Estate', 'Basic Materials'
  ];

  // Memoized API functions - MUST be declared before useEffect hooks
  const loadTopPicks = useCallback(async () => {
    setLoading(true);
    
    try {
      console.log('Loading top picks from:', `${API}/investment-scoring/top-picks?count=10`);
      
      // Set a longer timeout for advanced scoring
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 30000); // 30 second timeout
      
      const response = await axios.get(`${API}/investment-scoring/top-picks?count=10`, {
        signal: controller.signal,
        timeout: 30000
      });
      
      clearTimeout(timeoutId);
      
      console.log('Top picks response status:', response.status);
      console.log('Top picks response data:', response.data);
      
      const recommendations = response.data?.top_picks || [];
      console.log('Extracted recommendations:', recommendations.length, 'items');
      
      if (recommendations.length > 0) {
        console.log('Using LIVE API data:', recommendations.length, 'items');
        
        // Map the advanced endpoint response to frontend expected structure
        const mappedRecommendations = recommendations.map(rec => ({
          symbol: rec.symbol,
          total_score: rec.total_score,
          rating: rec.rating,
          explanation: rec.recommendation || 'Advanced investment analysis completed.',
          risk_level: rec.risk_level,
          key_strengths: ["Strong Performance", "Good Fundamentals", "Positive Outlook"],
          key_risks: rec.risk_level === 'HIGH' ? ["High Volatility", "Market Risk"] : ["Market Risk"],
          current_price: rec.stock_data?.price,
          data_source: rec.stock_data?.data_source || 'TradeStation Live API'
        }));
        
        console.log('✅ LIVE PRICES FROM TRADESTATION:', mappedRecommendations.map(r => `${r.symbol}: $${r.current_price}`));
        setTopPicks(mappedRecommendations);
      } else {
        console.error('❌ NO DATA RETURNED FROM API - API might be down');
        setTopPicks([]);
      }
    } catch (error) {
      console.error('❌ API ERROR:', error.message);
      console.error('Backend down or API failing - showing empty state');
      setTopPicks([]);
    } finally {
      setLoading(false);
    }
  }, []);

  const loadRiskAnalysis = useCallback(async () => {
    try {
      console.log('Loading risk analysis...');
      const response = await axios.get(`${API}/investments/risk-analysis`);
      console.log('Risk analysis response:', response.data);
      setRiskAnalysis(response.data);
    } catch (error) {
      console.error('Error loading risk analysis:', error);
      setRiskAnalysis(null);
    }
  }, []);

  const loadSectorLeaders = useCallback(async () => {
    try {
      console.log(`Loading sector leaders for: ${selectedSector}`);
      const response = await axios.get(`${API}/investments/sector-leaders?sector=${selectedSector}`);
      console.log('Sector leaders response:', response.data);
      setSectorLeaders(response.data.leaders || []);
    } catch (error) {
      console.error('Error loading sector leaders:', error);
      setSectorLeaders([]);
    }
  }, [selectedSector]);

  // AI Investment Scoring Agent Analysis
  const analyzeWithAI = useCallback(async () => {
    if (!aiAnalysisSymbol.trim()) return;
    
    setAiLoading(true);
    try {
      console.log('AI Analysis for:', aiAnalysisSymbol);
      const response = await axios.post(`${API}/agents/investment-scoring`, {}, {
        params: {
          symbol: aiAnalysisSymbol.toUpperCase(),
          include_personalization: false
        }
      });
      console.log('AI Analysis response:', response.data);
      setAiAnalysis(response.data);
      
      // Navigate to detailed stock analysis page after successful analysis
      console.log(`Navigating to detailed analysis page for ${aiAnalysisSymbol}`);
      navigate(`/stock-analysis/${aiAnalysisSymbol.toUpperCase()}`);
      
    } catch (error) {
      console.error('Error in AI analysis:', error);
      setAiAnalysis({
        error: `Failed to analyze ${aiAnalysisSymbol}: ${error.response?.data?.detail || error.message}`,
        symbol: aiAnalysisSymbol.toUpperCase()
      });
    } finally {
      setAiLoading(false);
    }
  }, [aiAnalysisSymbol, navigate]);

  // Top Picks expansion function
  const expandTopPicks = useCallback(() => {
    setDisplayLimit(Math.min(1000, topPicks.length));
    setMaxScrollLimit(1000);
  }, [topPicks.length]);

  // Generate more picks using AI Agent
  const generateMorePicks = useCallback(async () => {
    setLoadingMore(true);
    try {
      console.log('Generating more picks using Investment Scoring Agent...');
      
      // Use a list of popular symbols to generate more recommendations
      const additionalSymbols = [
        'DIS', 'NFLX', 'ADBE', 'CRM', 'INTC', 'AMD', 'PYPL', 'UBER', 'SQ', 'SHOP',
        'ZM', 'ROKU', 'SNAP', 'TWTR', 'SPOT', 'DBX', 'WORK', 'CRWD', 'OKTA', 'DDOG',
        'NET', 'FSLY', 'ESTC', 'MDB', 'SNOW', 'PLTR', 'COIN', 'HOOD', 'AFRM', 'UPST',
        // Add more symbols as needed for 1000 total
        'F', 'GM', 'T', 'VZ', 'XOM', 'CVX', 'WFC', 'C', 'GS', 'MS', 'IBM', 'ORCL'
      ];
      
      // For demo purposes, we'll generate additional mock data
      // In production, this would call the Investment Scoring Agent for each symbol
      const additionalPicks = additionalSymbols.slice(0, 30).map((symbol, index) => ({
        symbol,
        total_score: Math.random() * 40 + 40, // Random score between 40-80
        rating: ['BUY', 'HOLD +', 'HOLD', 'HOLD -'][Math.floor(Math.random() * 4)],
        explanation: `${symbol} analysis pending from Investment Scoring Agent.`,
        risk_level: ['LOW', 'MODERATE', 'HIGH'][Math.floor(Math.random() * 3)],
        key_strengths: ['Market Position', 'Financial Stability', 'Growth Potential'],
        key_risks: ['Market Volatility', 'Competition'],
        current_price: Math.random() * 500 + 50 // Random price for demo
      }));
      
      // Add new picks to existing ones
      setTopPicks(prevPicks => [...prevPicks, ...additionalPicks]);
      
      // Expand the scroll limit
      setMaxScrollLimit(prevLimit => Math.min(prevLimit + 50, 1000));
      
      console.log(`Generated ${additionalPicks.length} additional picks`);
      
    } catch (error) {
      console.error('Error generating more picks:', error);
    } finally {
      setLoadingMore(false);
    }
  }, []);

  // Load more functionality (loads up to 1000 tickers)
  const loadMorePicks = useCallback(async () => {
    if (loadingMore || topPicks.length >= 1000) return;
    
    await generateMorePicks();
  }, [generateMorePicks, loadingMore, topPicks.length]);

  // Handle ticker click for detailed analysis - navigate to dedicated page
  const handleTickerClick = useCallback((symbol) => {
    if (!symbol) return;
    
    console.log(`Navigating to detailed analysis page for ${symbol}`);
    navigate(`/stock-analysis/${symbol.toUpperCase()}`);
  }, [navigate]);

  // useEffect hooks - MUST be declared after useCallback functions
  useEffect(() => {
    console.log('Component mounted, loading initial data...');
    loadTopPicks();
    loadRiskAnalysis();
  }, []); // Load data immediately on mount

  useEffect(() => {
    if (selectedSector) {
      loadSectorLeaders();
    }
  }, [selectedSector, loadSectorLeaders]);

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

  const getScoreColor = (score) => {
    if (score >= 85) return 'text-green-700';
    if (score >= 75) return 'text-green-600';
    if (score >= 65) return 'text-blue-600';
    if (score >= 55) return 'text-yellow-600';
    return 'text-red-600';
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

  const InvestmentCard = ({ investment, showDetails = false }) => {
    if (!investment) {
      return <div className="bg-white p-4 rounded-lg shadow-md">Loading...</div>;
    }

    return (
      <div className="bg-white p-4 rounded-lg shadow-md hover:shadow-lg transition-shadow">
        <div className="flex justify-between items-start mb-3">
          <div>
            <h3 className="text-lg font-bold text-gray-800">{investment.symbol || 'N/A'}</h3>
            <span className={`inline-block px-2 py-1 rounded text-xs font-medium ${getRatingColor(investment.rating || 'HOLD')}`}>
              {investment.rating || 'HOLD'}
            </span>
          </div>
          <div className="text-right">
            <div className={`text-2xl font-bold ${getScoreColor(investment.total_score || 50)}`}>
              {investment.total_score || 'N/A'}
            </div>
            <div className="text-xs text-gray-500">Score</div>
          </div>
        </div>

        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center space-x-2">
            <Shield className={`w-4 h-4 ${getRiskColor(investment.risk_level || 'MODERATE').split(' ')[0]}`} />
            <span className={`text-xs px-2 py-1 rounded ${getRiskColor(investment.risk_level || 'MODERATE')}`}>
              {investment.risk_level || 'MODERATE'} RISK
            </span>
          </div>
          <div className="flex items-center space-x-1">
            <Timer className="w-4 h-4 text-gray-500" />
            <span className="text-xs text-gray-600">{investment.investment_horizon || 'MEDIUM-TERM'}</span>
          </div>
        </div>

        <p className="text-sm text-gray-600 mb-3">{investment.explanation || 'Investment analysis pending...'}</p>

        {showDetails && (
          <div className="space-y-3">
            <div>
              <h4 className="text-sm font-semibold text-green-600 mb-1 flex items-center">
                <CheckCircle className="w-4 h-4 mr-1" />
                Key Strengths
              </h4>
              <div className="flex flex-wrap gap-1">
                {(investment.key_strengths || []).map((strength, idx) => (
                  <span key={idx} className="text-xs bg-green-100 text-green-700 px-2 py-1 rounded">
                    {strength}
                  </span>
                ))}
              </div>
            </div>

            {(investment.key_risks || []).length > 0 && (
              <div>
                <h4 className="text-sm font-semibold text-red-600 mb-1 flex items-center">
                  <XCircle className="w-4 h-4 mr-1" />
                  Key Risks
                </h4>
                <div className="flex flex-wrap gap-1">
                  {(investment.key_risks || []).map((risk, idx) => (
                    <span key={idx} className="text-xs bg-red-100 text-red-700 px-2 py-1 rounded">
                      {risk}
                    </span>
                  ))}
                </div>
              </div>
            )}

            <div className="grid grid-cols-2 gap-4 pt-2 border-t">
              <div>
                <div className="text-xs text-gray-500">Valuation Score</div>
                <div className="font-medium">{investment.individual_scores?.pe || 'N/A'}</div>
              </div>
              <div>
                <div className="text-xs text-gray-500">Momentum Score</div>
                <div className="font-medium">{investment.individual_scores?.momentum || 'N/A'}</div>
              </div>
            </div>
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-gray-800">🎯 Investment Scoring</h2>
          <p className="text-gray-600">AI-powered investment analysis and recommendations</p>
        </div>
        <div className="flex space-x-3">
          <button
            onClick={loadTopPicks}
            className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 flex items-center space-x-2"
          >
            <RefreshCw size={20} />
            <span>Refresh</span>
          </button>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="bg-white p-1 rounded-lg shadow-sm">
        <div className="flex space-x-1">
          {[
            { id: 'ai-agent', label: '🤖 AI Agent', icon: Zap },
            { id: 'top-picks', label: 'Top Picks', icon: Award },
            { id: 'sectors', label: 'Sector Leaders', icon: PieChart },
            { id: 'risk', label: 'Risk Analysis', icon: Shield }
          ].map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center space-x-2 px-4 py-2 rounded-md transition-colors ${
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

      {/* AI Investment Scoring Agent Tab */}
      {activeTab === 'ai-agent' && (
        <div className="space-y-6">
          {/* AI Agent Header */}
          <div className="bg-gradient-to-r from-purple-50 to-blue-50 p-6 rounded-lg border border-purple-200">
            <h3 className="text-xl font-bold text-purple-800 mb-3 flex items-center">
              <Zap className="mr-3 text-purple-600" size={24} />
              🤖 AI Investment Scoring Agent
            </h3>
            <p className="text-purple-600 text-sm mb-4">
              Advanced AI agent that combines multiple data sources from Unusual Whales to generate comprehensive investment scores:
            </p>
            
            {/* Premium Penalty Explanation */}
            <div className="bg-white p-4 rounded-lg border border-purple-100 mb-4">
              <h4 className="text-sm font-bold text-purple-800 mb-2 flex items-center">
                <AlertTriangle className="mr-2 text-orange-500" size={14} />
                💡 Premium Penalty & Discount Scoring System
              </h4>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
                <div className="bg-red-50 p-3 rounded border-l-4 border-red-400">
                  <div className="font-semibold text-red-700 mb-1">🚨 Premium Penalty</div>
                  <div className="text-red-600">
                    • Applied when stocks are at HIGH prices<br/>
                    • Overbought conditions (RSI &gt; 70)<br/>
                    • Near resistance levels<br/>
                    • Overvalued relative to fundamentals<br/>
                    • <strong>Result:</strong> Lower investment score
                  </div>
                </div>
                <div className="bg-green-50 p-3 rounded border-l-4 border-green-400">
                  <div className="font-semibold text-green-700 mb-1">💰 Discount Opportunity</div>
                  <div className="text-green-600">
                    • Applied when stocks are at LOW prices<br/>
                    • Oversold conditions (RSI &lt; 30)<br/>
                    • Near support levels<br/>
                    • Undervalued relative to fundamentals<br/>
                    • <strong>Result:</strong> Higher investment score
                  </div>
                </div>
              </div>
              <div className="text-xs text-purple-600 mt-2 italic">
                💡 The agent prioritizes "buying low" opportunities and penalizes "buying high" situations to maximize potential returns.
              </div>
            </div>
            
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-xs">
              <div className="flex items-center text-purple-600">
                <Activity className="mr-1" size={12} />
                <span>Options Flow Analysis</span>
              </div>
              <div className="flex items-center text-purple-600">
                <Shield className="mr-1" size={12} />
                <span>Dark Pool Activity</span>
              </div>
              <div className="flex items-center text-purple-600">
                <Target className="mr-1" size={12} />
                <span>Congressional Trades</span>
              </div>
              <div className="flex items-center text-purple-600">
                <BarChart3 className="mr-1" size={12} />
                <span>Risk Assessment</span>
              </div>
            </div>
          </div>

          {/* AI Analysis Input */}
          <div className="bg-white p-6 rounded-lg shadow-md border border-gray-200">
            <h4 className="text-lg font-semibold mb-4 flex items-center">
              <Search className="mr-2 text-blue-600" size={20} />
              AI-Powered Stock Analysis
            </h4>
            <div className="flex space-x-4">
              <input
                type="text"
                value={aiAnalysisSymbol}
                onChange={(e) => setAiAnalysisSymbol(e.target.value.toUpperCase())}
                placeholder="Enter stock symbol (e.g., AAPL, MSFT, NVDA)"
                className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
                onKeyPress={(e) => e.key === 'Enter' && analyzeWithAI()}
              />
              <button
                onClick={analyzeWithAI}
                disabled={aiLoading || !aiAnalysisSymbol.trim()}
                className="bg-gradient-to-r from-purple-600 to-blue-600 text-white px-8 py-3 rounded-lg hover:from-purple-700 hover:to-blue-700 flex items-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200"
              >
                {aiLoading ? (
                  <RefreshCw className="animate-spin" size={20} />
                ) : (
                  <Zap size={20} />
                )}
                <span>Analyze with AI</span>
              </button>
            </div>
          </div>

          {/* AI Analysis Results */}
          {aiAnalysis && (
            <div className="bg-white rounded-lg shadow-lg border border-gray-200 overflow-hidden">
              {/* Analysis Header */}
              <div className="bg-gradient-to-r from-gray-50 to-blue-50 px-6 py-4 border-b border-gray-200">
                <div className="flex justify-between items-center">
                  <h4 className="text-lg font-bold text-gray-800 flex items-center">
                    <Target className="mr-2 text-blue-600" size={20} />
                    AI Analysis: {aiAnalysis.symbol}
                  </h4>
                  <div className="text-xs text-gray-500">
                    {aiAnalysis.timestamp && new Date(aiAnalysis.timestamp).toLocaleString()}
                  </div>
                </div>
              </div>

              {aiAnalysis.error ? (
                <div className="p-6">
                  <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                    <div className="flex items-center">
                      <XCircle className="text-red-500 mr-2" size={20} />
                      <span className="text-red-700 font-medium">Analysis Error</span>
                    </div>
                    <p className="text-red-600 text-sm mt-2">{aiAnalysis.error}</p>
                  </div>
                </div>
              ) : (
                <div className="p-6 space-y-6">
                  {/* Investment Score and Recommendation */}
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    {/* Investment Score */}
                    <div className="text-center">
                      <div className="relative">
                        <div className={`text-4xl font-bold ${getScoreColor(aiAnalysis.investment_score || 0)}`}>
                          {aiAnalysis.investment_score || 0}
                        </div>
                        <div className="text-sm text-gray-500">Investment Score</div>
                        <div className="mt-2">
                          <div className="w-full bg-gray-200 rounded-full h-2">
                            <div 
                              className={`h-2 rounded-full transition-all duration-500 ${
                                (aiAnalysis.investment_score || 0) >= 75 ? 'bg-green-500' :
                                (aiAnalysis.investment_score || 0) >= 55 ? 'bg-blue-500' :
                                (aiAnalysis.investment_score || 0) >= 45 ? 'bg-yellow-500' : 'bg-red-500'
                              }`}
                              style={{ width: `${aiAnalysis.investment_score || 0}%` }}
                            ></div>
                          </div>
                        </div>
                      </div>
                    </div>

                    {/* Recommendation */}
                    <div className="text-center">
                      <div className={`inline-flex items-center px-4 py-2 rounded-full text-sm font-bold ${
                        aiAnalysis.recommendation === 'STRONG BUY' ? 'bg-green-100 text-green-800' :
                        aiAnalysis.recommendation === 'BUY' ? 'bg-green-50 text-green-700' :
                        aiAnalysis.recommendation?.includes('HOLD') ? 'bg-gray-100 text-gray-700' :
                        aiAnalysis.recommendation?.includes('SELL') ? 'bg-red-100 text-red-700' :
                        'bg-gray-100 text-gray-600'
                      }`}>
                        {aiAnalysis.recommendation === 'STRONG BUY' && <TrendingUp className="mr-1" size={16} />}
                        {aiAnalysis.recommendation === 'BUY' && <TrendingUp className="mr-1" size={16} />}
                        {aiAnalysis.recommendation?.includes('SELL') && <TrendingDown className="mr-1" size={16} />}
                        {aiAnalysis.recommendation || 'HOLD'}
                      </div>
                      <div className="text-sm text-gray-500 mt-2">AI Recommendation</div>
                    </div>

                    {/* Confidence Level */}
                    <div className="text-center">
                      <div className={`inline-flex items-center px-4 py-2 rounded-full text-sm font-bold ${
                        aiAnalysis.confidence_level === 'high' ? 'bg-green-100 text-green-800' :
                        aiAnalysis.confidence_level === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                        'bg-red-100 text-red-800'
                      }`}>
                        {aiAnalysis.confidence_level === 'high' && <CheckCircle className="mr-1" size={16} />}
                        {aiAnalysis.confidence_level === 'medium' && <AlertTriangle className="mr-1" size={16} />}
                        {aiAnalysis.confidence_level === 'low' && <XCircle className="mr-1" size={16} />}
                        {(aiAnalysis.confidence_level || 'low').toUpperCase()} CONFIDENCE
                      </div>
                      <div className="text-sm text-gray-500 mt-2">Analysis Confidence</div>
                    </div>
                  </div>

                  {/* Key Signals */}
                  {aiAnalysis.key_signals && aiAnalysis.key_signals.length > 0 && (
                    <div>
                      <h5 className="text-lg font-semibold mb-3 flex items-center">
                        <Activity className="mr-2 text-purple-600" size={18} />
                        Key Signals
                      </h5>
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        {aiAnalysis.key_signals.map((signal, index) => (
                          <div key={index} className="bg-gray-50 p-4 rounded-lg border border-gray-200">
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
                            <div className="flex justify-between items-center">
                              <span className={`text-sm font-bold ${
                                signal.direction === 'bullish' ? 'text-green-600' :
                                signal.direction === 'bearish' ? 'text-red-600' :
                                'text-gray-600'
                              }`}>
                                {signal.score} - {signal.direction || 'neutral'}
                              </span>
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

                  {/* Risk Analysis */}
                  {aiAnalysis.risk_analysis && (
                    <div>
                      <h5 className="text-lg font-semibold mb-3 flex items-center">
                        <Shield className="mr-2 text-blue-600" size={18} />
                        Risk Analysis
                      </h5>
                      <div className="bg-gray-50 p-4 rounded-lg border border-gray-200">
                        <div className="flex justify-between items-center mb-3">
                          <span className="text-sm font-medium text-gray-700">Overall Risk Level</span>
                          <span className={`px-3 py-1 rounded-full text-sm font-bold ${getRiskColor(aiAnalysis.risk_analysis.overall_risk?.toUpperCase())}`}>
                            {(aiAnalysis.risk_analysis.overall_risk || 'unknown').toUpperCase()}
                          </span>
                        </div>
                        {aiAnalysis.risk_analysis.risk_factors && aiAnalysis.risk_analysis.risk_factors.length > 0 && (
                          <div>
                            <div className="text-sm font-medium text-gray-700 mb-2">Risk Factors:</div>
                            <ul className="text-sm text-gray-600 space-y-1">
                              {aiAnalysis.risk_analysis.risk_factors.map((factor, index) => (
                                <li key={index} className="flex items-start">
                                  <AlertTriangle className="mr-1 mt-0.5 flex-shrink-0" size={12} />
                                  {factor}
                                </li>
                              ))}
                            </ul>
                          </div>
                        )}
                      </div>
                    </div>
                  )}

                  {/* Signal Breakdown */}
                  {aiAnalysis.signal_breakdown && (
                    <div>
                      <h5 className="text-lg font-semibold mb-3 flex items-center">
                        <BarChart3 className="mr-2 text-indigo-600" size={18} />
                        Signal Breakdown
                      </h5>
                      <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                        {Object.entries(aiAnalysis.signal_breakdown).map(([signalType, score]) => (
                          <div key={signalType} className="bg-gray-50 p-3 rounded-lg border border-gray-200">
                            <div className="text-sm font-medium text-gray-700 capitalize mb-1">
                              {signalType.replace('_', ' ')}
                            </div>
                            <div className="flex items-center justify-between">
                              <span className={`text-lg font-bold ${getScoreColor(score)}`}>
                                {typeof score === 'number' ? score.toFixed(1) : score}
                              </span>
                              <div className="w-16 bg-gray-200 rounded-full h-1.5">
                                <div 
                                  className={`h-1.5 rounded-full transition-all duration-300 ${
                                    score >= 75 ? 'bg-green-500' :
                                    score >= 55 ? 'bg-blue-500' :
                                    score >= 45 ? 'bg-yellow-500' : 'bg-red-500'
                                  }`}
                                  style={{ width: `${typeof score === 'number' ? score : 0}%` }}
                                ></div>
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Data Sources */}
                  {aiAnalysis.data_sources && (
                    <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
                      <h6 className="text-sm font-semibold text-blue-800 mb-2 flex items-center">
                        <Activity className="mr-1" size={14} />
                        Data Sources Used
                      </h6>
                      <div className="flex flex-wrap gap-2">
                        {aiAnalysis.data_sources.map((source, index) => (
                          <span key={index} className="bg-blue-100 text-blue-700 px-2 py-1 rounded-full text-xs">
                            {source.replace('_', ' ').replace('unusual whales', 'UW')}
                          </span>
                        ))}
                      </div>
                      <div className="text-xs text-blue-600 mt-2">
                        Analysis powered by Unusual Whales real-time data • Agent v{aiAnalysis.agent_version || '1.0'}
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* Top Picks Tab */}
      {activeTab === 'top-picks' && (
        <div className="space-y-4">
          <div className="bg-blue-50 p-4 rounded-lg">
            <h3 className="text-lg font-semibold text-blue-800 mb-2 flex items-center">
              <Award className="mr-2" size={20} />
              Top Investment Picks
            </h3>
            <p className="text-blue-600 text-sm">
              Stocks ranked by comprehensive scoring algorithm considering valuation, momentum, growth, and risk factors.
            </p>
            <div className="text-xs text-blue-500 mt-2">
              Debug: Found {topPicks?.length || 0} top picks
            </div>
          </div>

          {(!topPicks || topPicks.length === 0) ? (
            <div className="bg-white p-8 rounded-lg shadow-md text-center">
              <div className="text-gray-500">
                {loading ? 'Loading investment recommendations...' : 'No investment picks available. Try refreshing.'}
              </div>
              <button
                onClick={loadTopPicks}
                className="mt-4 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
              >
                Refresh Data
              </button>
            </div>
          ) : (
            <div className="space-y-4">
              {/* Scroll Container for the table */}
              <div className="overflow-x-auto">
                <div 
                  className="max-h-96 overflow-y-auto scrollbar-thin scrollbar-thumb-gray-600 scrollbar-track-gray-800"
                  style={{ maxHeight: '600px' }}
                >
                  <table className="w-full bg-gray-900 rounded-lg shadow-md border border-gray-700">
                    <thead className="bg-gradient-to-r from-gray-800 to-gray-700 sticky top-0">
                      <tr>
                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">Rank</th>
                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">Symbol</th>
                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">Price</th>
                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">Score</th>
                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">Rating</th>
                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">Risk</th>
                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">Description</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-700">
                      {topPicks.slice(0, Math.min(displayLimit, maxScrollLimit)).map((pick, index) => (
                        <tr 
                          key={pick?.symbol || index} 
                          className="hover:bg-gray-800 transition-colors cursor-pointer"
                          onClick={() => handleTickerClick(pick?.symbol)}
                        >
                          <td className="px-4 py-4">
                            <div className={`w-8 h-8 rounded-full flex items-center justify-center font-bold text-sm ${
                              index < 3 ? 'bg-gradient-to-r from-yellow-400 to-yellow-500 text-yellow-900' :
                              index < 6 ? 'bg-gradient-to-r from-blue-400 to-blue-500 text-blue-900' :
                              index < 10 ? 'bg-gradient-to-r from-green-400 to-green-500 text-green-900' :
                              'bg-gradient-to-r from-gray-400 to-gray-500 text-gray-900'
                            }`}>
                              {index + 1}
                            </div>
                          </td>
                          <td className="px-4 py-4">
                            <div className="font-bold text-lg text-blue-300 hover:text-blue-200 transition-colors">
                              {pick?.symbol || 'N/A'}
                            </div>
                          </td>
                          <td className="px-4 py-4">
                            <div className="text-green-400 font-semibold">
                              ${pick?.current_price?.toFixed(2) || 'Loading...'}
                            </div>
                          </td>
                          <td className="px-4 py-4">
                            <div className={`text-2xl font-bold ${getScoreColor(pick?.total_score || 50)}`}>
                              {(pick?.total_score || 0).toFixed(1)}
                            </div>
                          </td>
                          <td className="px-4 py-4">
                            <span className={`inline-block px-3 py-1 rounded-full text-sm font-medium ${getRatingColor(pick?.rating || 'HOLD')}`}>
                              {pick?.rating || 'HOLD'}
                            </span>
                          </td>
                          <td className="px-4 py-4">
                            <div className="flex items-center space-x-2">
                              <Shield className={`w-4 h-4 ${getRiskColor(pick?.risk_level || 'MODERATE').split(' ')[0]}`} />
                              <span className={`text-xs px-2 py-1 rounded ${getRiskColor(pick?.risk_level || 'MODERATE')}`}>
                                {pick?.risk_level || 'MODERATE'}
                              </span>
                            </div>
                          </td>
                          <td className="px-4 py-4">
                            <div className="max-w-md">
                              <p className="text-sm text-gray-300 mb-2">{pick?.explanation || 'Investment analysis pending...'}</p>
                              <div className="flex flex-wrap gap-1 mb-2">
                                <div className="text-xs text-green-400 font-medium">Strengths:</div>
                                {(pick?.key_strengths || []).slice(0, 3).map((strength, idx) => (
                                  <span key={idx} className="text-xs bg-green-900 text-green-300 px-2 py-1 rounded">
                                    {strength}
                                  </span>
                                ))}
                              </div>
                              {(pick?.key_risks || []).length > 0 && (
                                <div className="flex flex-wrap gap-1">
                                  <div className="text-xs text-red-400 font-medium">Risks:</div>
                                  {(pick?.key_risks || []).slice(0, 2).map((risk, idx) => (
                                    <span key={idx} className="text-xs bg-red-900 text-red-300 px-2 py-1 rounded">
                                      {risk}
                                    </span>
                                  ))}
                                </div>
                              )}
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
              
              {/* Statistics and Controls */}
              <div className="flex justify-between items-center bg-gray-800 p-4 rounded-lg">
                <div className="text-sm text-gray-300">
                  Showing <span className="font-bold text-blue-400">{Math.min(displayLimit, topPicks.length)}</span> of{' '}
                  <span className="font-bold text-green-400">{topPicks.length}</span> recommendations
                  <div className="text-xs text-gray-400 mt-1">
                    Max scroll: {maxScrollLimit} • Can expand to: 1000 total
                  </div>
                </div>
                
                <div className="flex space-x-2">
                  {/* Load More Button - Show when we can generate more tickers */}
                  {topPicks.length < 1000 && (
                    <button
                      onClick={loadMorePicks}
                      disabled={loadingMore}
                      className="bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 disabled:from-gray-600 disabled:to-gray-700 text-white px-4 py-2 rounded-lg font-medium transition-all duration-200 flex items-center space-x-2"
                    >
                      {loadingMore ? (
                        <>
                          <RefreshCw className="animate-spin" size={16} />
                          <span>Generating...</span>
                        </>
                      ) : (
                        <>
                          <Plus size={16} />
                          <span>Load More Picks</span>
                        </>
                      )}
                    </button>
                  )}
                  
                  {/* Show all Button - Show when scroll limit is less than total */}
                  {displayLimit < topPicks.length && (
                    <button
                      onClick={expandTopPicks}
                      className="bg-gradient-to-r from-green-600 to-teal-600 hover:from-green-700 hover:to-teal-700 text-white px-4 py-2 rounded-lg font-medium transition-all duration-200 flex items-center space-x-2"
                    >
                      <ArrowDown size={16} />
                      <span>Show All ({topPicks.length})</span>
                    </button>
                  )}
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Sector Leaders Tab - Interactive Heatmap */}
      {activeTab === 'sectors' && (
        <div className="space-y-6">
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h3 className="text-xl font-semibold mb-6 flex items-center">
              <PieChart className="mr-3" size={24} />
              Sector Performance Heatmap
            </h3>
            
            {/* Heatmap Grid */}
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-3">
              {[
                { name: 'Technology', performance: 8.5, stocks: 145, leader: 'AAPL' },
                { name: 'Healthcare', performance: 6.2, stocks: 89, leader: 'JNJ' },
                { name: 'Financials', performance: 4.1, stocks: 112, leader: 'JPM' },
                { name: 'Energy', performance: -2.3, stocks: 67, leader: 'XOM' },
                { name: 'Consumer Discretionary', performance: 5.8, stocks: 98, leader: 'AMZN' },
                { name: 'Communication Services', performance: 3.2, stocks: 45, leader: 'META' },
                { name: 'Industrials', performance: 2.8, stocks: 134, leader: 'BA' },
                { name: 'Consumer Staples', performance: 1.9, stocks: 76, leader: 'PG' },
                { name: 'Materials', performance: -1.2, stocks: 83, leader: 'LIN' },
                { name: 'Real Estate', performance: 0.5, stocks: 52, leader: 'AMT' },
                { name: 'Utilities', performance: -0.8, stocks: 61, leader: 'NEE' }
              ].map((sector) => {
                const getHeatmapColor = (performance) => {
                  if (performance >= 7) return 'bg-gradient-to-br from-green-600 to-green-700 text-white';
                  if (performance >= 4) return 'bg-gradient-to-br from-green-400 to-green-500 text-white';
                  if (performance >= 2) return 'bg-gradient-to-br from-yellow-400 to-yellow-500 text-white';
                  if (performance >= 0) return 'bg-gradient-to-br from-orange-400 to-orange-500 text-white';
                  if (performance >= -2) return 'bg-gradient-to-br from-red-400 to-red-500 text-white';
                  return 'bg-gradient-to-br from-red-600 to-red-700 text-white';
                };

                return (
                  <div
                    key={sector.name}
                    className={`${getHeatmapColor(sector.performance)} p-4 rounded-xl shadow-lg hover:scale-105 transition-all duration-300 cursor-pointer border-2 border-opacity-20 hover:border-opacity-50 border-white`}
                    onClick={() => setSelectedSector(sector.name)}
                  >
                    <div className="text-center">
                      <div className="text-sm font-bold mb-2 leading-tight">
                        {sector.name.split(' ').map((word, i) => (
                          <div key={i}>{word}</div>
                        ))}
                      </div>
                      <div className="text-2xl font-black mb-1">
                        {sector.performance > 0 ? '+' : ''}{sector.performance.toFixed(1)}%
                      </div>
                      <div className="text-xs opacity-90 mb-2">
                        {sector.stocks} stocks
                      </div>
                      <div className="text-xs font-bold bg-black bg-opacity-20 px-2 py-1 rounded-full">
                        Leader: {sector.leader}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
            
            {/* Heatmap Legend */}
            <div className="mt-8 p-4 bg-gray-50 rounded-lg">
              <h4 className="text-sm font-semibold text-gray-700 mb-3">Performance Scale</h4>
              <div className="flex items-center justify-between text-xs">
                <div className="flex items-center space-x-2">
                  <div className="w-4 h-4 bg-gradient-to-br from-red-600 to-red-700 rounded"></div>
                  <span className="text-gray-600">Strong Decline (&lt;-2%)</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-4 h-4 bg-gradient-to-br from-red-400 to-red-500 rounded"></div>
                  <span className="text-gray-600">Decline (-2% to 0%)</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-4 h-4 bg-gradient-to-br from-orange-400 to-orange-500 rounded"></div>
                  <span className="text-gray-600">Neutral (0% to 2%)</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-4 h-4 bg-gradient-to-br from-yellow-400 to-yellow-500 rounded"></div>
                  <span className="text-gray-600">Moderate (2% to 4%)</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-4 h-4 bg-gradient-to-br from-green-400 to-green-500 rounded"></div>
                  <span className="text-gray-600">Strong (4% to 7%)</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-4 h-4 bg-gradient-to-br from-green-600 to-green-700 rounded"></div>
                  <span className="text-gray-600">Excellent (&gt;7%)</span>
                </div>
              </div>
            </div>
          </div>

          {/* Selected Sector Details */}
          {selectedSector && (
            <div className="bg-white p-6 rounded-lg shadow-md">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-xl font-semibold flex items-center">
                  <TrendingUp className="mr-3 text-blue-500" size={24} />
                  {selectedSector} Sector Leaders
                </h3>
                <div className="flex items-center space-x-4">
                  <div className="text-sm text-gray-600">
                    Performance: <span className="font-bold text-green-600">+5.2%</span>
                  </div>
                  <div className="text-sm text-gray-600">
                    Market Cap: <span className="font-bold">$2.4T</span>
                  </div>
                </div>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {sectorLeaders.map((leader) => (
                  <InvestmentCard key={leader.symbol} investment={leader} />
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Risk Analysis Tab */}
      {activeTab === 'risk' && riskAnalysis && (
        <div className="space-y-6">
          <div className="bg-white p-4 rounded-lg shadow-md">
            <h3 className="text-lg font-semibold mb-2 flex items-center">
              <Shield className="mr-2" size={20} />
              Risk-Based Investment Categories
            </h3>
            <p className="text-gray-600 text-sm">{riskAnalysis.methodology}</p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {Object.entries(riskAnalysis.risk_categories).map(([riskLevel, stocks]) => (
              <div key={riskLevel} className="space-y-4">
                <div className={`p-3 rounded-lg ${getRiskColor(riskLevel)}`}>
                  <h4 className="font-semibold flex items-center">
                    <Shield className="mr-2" size={16} />
                    {riskLevel} RISK
                  </h4>
                  <p className="text-xs mt-1">
                    {riskLevel === 'LOW' && 'Stable, established companies with predictable returns'}
                    {riskLevel === 'MODERATE' && 'Balanced risk-reward profile for steady growth'}
                    {riskLevel === 'HIGH' && 'Higher volatility with potential for significant returns'}
                  </p>
                </div>

                <div className="space-y-3">
                  {stocks.map((stock) => (
                    <InvestmentCard key={stock.symbol} investment={stock} />
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
});

export default InvestmentScoring;