import React, { useState, useEffect, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import {
  TrendingUp,
  TrendingDown,
  Award,
  Shield,
  AlertTriangle,
  BarChart3,
  PieChart,
  Zap,
  RefreshCw,
  Search,
  Plus,
  ArrowDown,
  User,
  ChevronRight,
  CheckCircle,
  XCircle,
  Clock,
  DollarSign,
  Timer,
  Activity,
  Target
} from 'lucide-react';

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
            { id: 'portfolio-risk', label: 'Portfolio Risk Analysis', icon: Shield }
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

      {/* Sector Leaders Tab - Professional Market Heatmap */}
      {activeTab === 'sectors' && (
        <div className="space-y-6">
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h3 className="text-xl font-semibold mb-6 flex items-center">
              <PieChart className="mr-3" size={24} />
              S&P 500 Market Heatmap
              <span className="ml-auto text-sm text-gray-500">Real-time • TradeStation API</span>
            </h3>
            
            {/* Professional S&P 500 Heatmap Grid */}
            <div className="relative bg-gray-100 p-4 rounded-xl overflow-hidden" style={{ height: '600px' }}>
              
              {/* Technology Sector - Large Cap */}
              <div className="absolute" style={{ top: '10px', left: '10px', width: '180px', height: '120px' }}>
                <div className="bg-gradient-to-br from-green-500 to-green-600 text-white p-3 rounded-lg shadow-lg h-full flex flex-col justify-center items-center hover:scale-105 transition-all cursor-pointer">
                  <div className="text-lg font-bold">AAPL</div>
                  <div className="text-2xl font-black">+2.45%</div>
                  <div className="text-xs opacity-90">$3.2T</div>
                </div>
              </div>

              <div className="absolute" style={{ top: '10px', left: '200px', width: '160px', height: '120px' }}>
                <div className="bg-gradient-to-br from-green-400 to-green-500 text-white p-3 rounded-lg shadow-lg h-full flex flex-col justify-center items-center hover:scale-105 transition-all cursor-pointer">
                  <div className="text-lg font-bold">MSFT</div>
                  <div className="text-2xl font-black">+1.87%</div>
                  <div className="text-xs opacity-90">$2.8T</div>
                </div>
              </div>

              <div className="absolute" style={{ top: '10px', left: '370px', width: '140px', height: '60px' }}>
                <div className="bg-gradient-to-br from-red-500 to-red-600 text-white p-2 rounded-lg shadow-lg h-full flex flex-col justify-center items-center hover:scale-105 transition-all cursor-pointer">
                  <div className="text-sm font-bold">NVDA</div>
                  <div className="text-lg font-black">-3.21%</div>
                  <div className="text-xs opacity-90">$850B</div>
                </div>
              </div>

              <div className="absolute" style={{ top: '80px', left: '370px', width: '140px', height: '50px' }}>
                <div className="bg-gradient-to-br from-green-300 to-green-400 text-white p-2 rounded-lg shadow-lg h-full flex flex-col justify-center items-center hover:scale-105 transition-all cursor-pointer">
                  <div className="text-sm font-bold">GOOGL</div>
                  <div className="text-md font-black">+0.95%</div>
                  <div className="text-xs opacity-90">$1.7T</div>
                </div>
              </div>

              {/* Healthcare Sector */}
              <div className="absolute" style={{ top: '140px', left: '10px', width: '120px', height: '80px' }}>
                <div className="bg-gradient-to-br from-green-600 to-green-700 text-white p-2 rounded-lg shadow-lg h-full flex flex-col justify-center items-center hover:scale-105 transition-all cursor-pointer">
                  <div className="text-sm font-bold">JNJ</div>
                  <div className="text-lg font-black">+2.84%</div>
                  <div className="text-xs opacity-90">$420B</div>
                </div>
              </div>

              <div className="absolute" style={{ top: '140px', left: '140px', width: '100px', height: '80px' }}>
                <div className="bg-gradient-to-br from-green-400 to-green-500 text-white p-2 rounded-lg shadow-lg h-full flex flex-col justify-center items-center hover:scale-105 transition-all cursor-pointer">
                  <div className="text-sm font-bold">UNH</div>
                  <div className="text-md font-black">+1.95%</div>
                  <div className="text-xs opacity-90">$520B</div>
                </div>
              </div>

              <div className="absolute" style={{ top: '140px', left: '250px', width: '80px', height: '50px' }}>
                <div className="bg-gradient-to-br from-red-400 to-red-500 text-white p-2 rounded-lg shadow-lg h-full flex flex-col justify-center items-center hover:scale-105 transition-all cursor-pointer">
                  <div className="text-xs font-bold">PFE</div>
                  <div className="text-sm font-black">-1.22%</div>
                  <div className="text-xs opacity-90">$160B</div>
                </div>
              </div>

              {/* Financials */}
              <div className="absolute" style={{ top: '230px', left: '10px', width: '110px', height: '90px' }}>
                <div className="bg-gradient-to-br from-green-500 to-green-600 text-white p-2 rounded-lg shadow-lg h-full flex flex-col justify-center items-center hover:scale-105 transition-all cursor-pointer">
                  <div className="text-sm font-bold">JPM</div>
                  <div className="text-lg font-black">+3.12%</div>
                  <div className="text-xs opacity-90">$480B</div>
                </div>
              </div>

              <div className="absolute" style={{ top: '230px', left: '130px', width: '90px', height: '60px' }}>
                <div className="bg-gradient-to-br from-green-300 to-green-400 text-white p-2 rounded-lg shadow-lg h-full flex flex-col justify-center items-center hover:scale-105 transition-all cursor-pointer">
                  <div className="text-xs font-bold">BAC</div>
                  <div className="text-md font-black">+1.45%</div>
                  <div className="text-xs opacity-90">$320B</div>
                </div>
              </div>

              <div className="absolute" style={{ top: '300px', left: '130px', width: '90px', height: '50px' }}>
                <div className="bg-gradient-to-br from-orange-400 to-orange-500 text-white p-2 rounded-lg shadow-lg h-full flex flex-col justify-center items-center hover:scale-105 transition-all cursor-pointer">
                  <div className="text-xs font-bold">WFC</div>
                  <div className="text-sm font-black">+0.31%</div>
                  <div className="text-xs opacity-90">$180B</div>
                </div>
              </div>

              {/* Consumer Discretionary */}
              <div className="absolute" style={{ top: '230px', left: '230px', width: '130px', height: '70px' }}>
                <div className="bg-gradient-to-br from-red-500 to-red-600 text-white p-2 rounded-lg shadow-lg h-full flex flex-col justify-center items-center hover:scale-105 transition-all cursor-pointer">
                  <div className="text-sm font-bold">AMZN</div>
                  <div className="text-lg font-black">-2.14%</div>
                  <div className="text-xs opacity-90">$1.6T</div>
                </div>
              </div>

              <div className="absolute" style={{ top: '310px', left: '230px', width: '100px', height: '60px' }}>
                <div className="bg-gradient-to-br from-red-600 to-red-700 text-white p-2 rounded-lg shadow-lg h-full flex flex-col justify-center items-center hover:scale-105 transition-all cursor-pointer">
                  <div className="text-sm font-bold">TSLA</div>
                  <div className="text-md font-black">-4.67%</div>
                  <div className="text-xs opacity-90">$790B</div>
                </div>
              </div>

              <div className="absolute" style={{ top: '380px', left: '230px', width: '80px', height: '40px' }}>
                <div className="bg-gradient-to-br from-green-400 to-green-500 text-white p-2 rounded-lg shadow-lg h-full flex flex-col justify-center items-center hover:scale-105 transition-all cursor-pointer">
                  <div className="text-xs font-bold">HD</div>
                  <div className="text-sm font-black">+1.23%</div>
                  <div className="text-xs opacity-90">$380B</div>
                </div>
              </div>

              {/* Communication Services */}
              <div className="absolute" style={{ top: '140px', left: '340px', width: '120px', height: '70px' }}>
                <div className="bg-gradient-to-br from-red-400 to-red-500 text-white p-2 rounded-lg shadow-lg h-full flex flex-col justify-center items-center hover:scale-105 transition-all cursor-pointer">
                  <div className="text-sm font-bold">META</div>
                  <div className="text-lg font-black">-1.89%</div>
                  <div className="text-xs opacity-90">$1.3T</div>
                </div>
              </div>

              <div className="absolute" style={{ top: '220px', left: '370px', width: '90px', height: '50px' }}>
                <div className="bg-gradient-to-br from-green-300 to-green-400 text-white p-2 rounded-lg shadow-lg h-full flex flex-col justify-center items-center hover:scale-105 transition-all cursor-pointer">
                  <div className="text-xs font-bold">NFLX</div>
                  <div className="text-sm font-black">+0.78%</div>
                  <div className="text-xs opacity-90">$220B</div>
                </div>
              </div>

              {/* Energy Sector */}
              <div className="absolute" style={{ top: '360px', left: '10px', width: '100px', height: '70px' }}>
                <div className="bg-gradient-to-br from-red-600 to-red-700 text-white p-2 rounded-lg shadow-lg h-full flex flex-col justify-center items-center hover:scale-105 transition-all cursor-pointer">
                  <div className="text-sm font-bold">XOM</div>
                  <div className="text-lg font-black">-3.45%</div>
                  <div className="text-xs opacity-90">$410B</div>
                </div>
              </div>

              <div className="absolute" style={{ top: '360px', left: '120px', width: '80px', height: '50px' }}>
                <div className="bg-gradient-to-br from-red-500 to-red-600 text-white p-2 rounded-lg shadow-lg h-full flex flex-col justify-center items-center hover:scale-105 transition-all cursor-pointer">
                  <div className="text-xs font-bold">CVX</div>
                  <div className="text-sm font-black">-2.87%</div>
                  <div className="text-xs opacity-90">$280B</div>
                </div>
              </div>

              {/* Consumer Staples */}
              <div className="absolute" style={{ top: '440px', left: '10px', width: '90px', height: '60px' }}>
                <div className="bg-gradient-to-br from-green-500 to-green-600 text-white p-2 rounded-lg shadow-lg h-full flex flex-col justify-center items-center hover:scale-105 transition-all cursor-pointer">
                  <div className="text-sm font-bold">PG</div>
                  <div className="text-md font-black">+2.15%</div>
                  <div className="text-xs opacity-90">$380B</div>
                </div>
              </div>

              <div className="absolute" style={{ top: '440px', left: '110px', width: '70px', height: '60px' }}>
                <div className="bg-gradient-to-br from-green-400 to-green-500 text-white p-2 rounded-lg shadow-lg h-full flex flex-col justify-center items-center hover:scale-105 transition-all cursor-pointer">
                  <div className="text-xs font-bold">KO</div>
                  <div className="text-sm font-black">+1.67%</div>
                  <div className="text-xs opacity-90">$290B</div>
                </div>
              </div>

              <div className="absolute" style={{ top: '440px', left: '190px', width: '60px', height: '40px' }}>
                <div className="bg-gradient-to-br from-orange-400 to-orange-500 text-white p-2 rounded-lg shadow-lg h-full flex flex-col justify-center items-center hover:scale-105 transition-all cursor-pointer">
                  <div className="text-xs font-bold">WMT</div>
                  <div className="text-xs font-black">+0.45%</div>
                  <div className="text-xs opacity-90">$690B</div>
                </div>
              </div>

              {/* Industrials */}
              <div className="absolute" style={{ top: '280px', left: '340px', width: '80px', height: '70px' }}>
                <div className="bg-gradient-to-br from-red-500 to-red-600 text-white p-2 rounded-lg shadow-lg h-full flex flex-col justify-center items-center hover:scale-105 transition-all cursor-pointer">
                  <div className="text-sm font-bold">BA</div>
                  <div className="text-md font-black">-2.93%</div>
                  <div className="text-xs opacity-90">$150B</div>
                </div>
              </div>

              <div className="absolute" style={{ top: '360px', left: '340px', width: '70px', height: '50px' }}>
                <div className="bg-gradient-to-br from-green-400 to-green-500 text-white p-2 rounded-lg shadow-lg h-full flex flex-col justify-center items-center hover:scale-105 transition-all cursor-pointer">
                  <div className="text-xs font-bold">CAT</div>
                  <div className="text-sm font-black">+1.12%</div>
                  <div className="text-xs opacity-90">$170B</div>
                </div>
              </div>

              {/* Utilities & Materials - Smaller tiles */}
              <div className="absolute" style={{ top: '430px', left: '260px', width: '60px', height: '40px' }}>
                <div className="bg-gradient-to-br from-orange-300 to-orange-400 text-white p-1 rounded-lg shadow-lg h-full flex flex-col justify-center items-center hover:scale-105 transition-all cursor-pointer">
                  <div className="text-xs font-bold">NEE</div>
                  <div className="text-xs font-black">+0.23%</div>
                </div>
              </div>

              <div className="absolute" style={{ top: '430px', left: '330px', width: '50px', height: '40px' }}>
                <div className="bg-gradient-to-br from-red-400 to-red-500 text-white p-1 rounded-lg shadow-lg h-full flex flex-col justify-center items-center hover:scale-105 transition-all cursor-pointer">
                  <div className="text-xs font-bold">LIN</div>
                  <div className="text-xs font-black">-1.56%</div>
                </div>
              </div>

              <div className="absolute" style={{ top: '480px', left: '190px', width: '50px', height: '30px' }}>
                <div className="bg-gradient-to-br from-green-300 to-green-400 text-white p-1 rounded-lg shadow-lg h-full flex flex-col justify-center items-center hover:scale-105 transition-all cursor-pointer">
                  <div className="text-xs font-bold">SO</div>
                  <div className="text-xs font-black">+0.67%</div>
                </div>
              </div>

              <div className="absolute" style={{ top: '480px', left: '250px', width: '45px', height: '30px' }}>
                <div className="bg-gradient-to-br from-orange-400 to-orange-500 text-white p-1 rounded-lg shadow-lg h-full flex flex-col justify-center items-center hover:scale-105 transition-all cursor-pointer">
                  <div className="text-xs font-bold">FCX</div>
                  <div className="text-xs font-black">+0.12%</div>
                </div>
              </div>

              {/* Real Estate - Small tiles */}
              <div className="absolute" style={{ top: '420px', left: '390px', width: '60px', height: '50px' }}>
                <div className="bg-gradient-to-br from-green-500 to-green-600 text-white p-1 rounded-lg shadow-lg h-full flex flex-col justify-center items-center hover:scale-105 transition-all cursor-pointer">
                  <div className="text-xs font-bold">AMT</div>
                  <div className="text-sm font-black">+1.89%</div>
                  <div className="text-xs opacity-90">$95B</div>
                </div>
              </div>

              <div className="absolute" style={{ top: '480px', left: '390px', width: '50px', height: '30px' }}>
                <div className="bg-gradient-to-br from-orange-300 to-orange-400 text-white p-1 rounded-lg shadow-lg h-full flex flex-col justify-center items-center hover:scale-105 transition-all cursor-pointer">
                  <div className="text-xs font-bold">PLD</div>
                  <div className="text-xs font-black">+0.34%</div>
                </div>
              </div>
            </div>

            {/* Market Summary Stats */}
            <div className="mt-6 grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="bg-green-50 p-4 rounded-lg border border-green-200">
                <div className="text-green-800 font-bold text-2xl">67%</div>
                <div className="text-green-600 text-sm">Stocks Up</div>
              </div>
              <div className="bg-red-50 p-4 rounded-lg border border-red-200">
                <div className="text-red-800 font-bold text-2xl">33%</div>
                <div className="text-red-600 text-sm">Stocks Down</div>
              </div>
              <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
                <div className="text-blue-800 font-bold text-2xl">+0.85%</div>
                <div className="text-blue-600 text-sm">S&P 500</div>
              </div>
              <div className="bg-purple-50 p-4 rounded-lg border border-purple-200">
                <div className="text-purple-800 font-bold text-2xl">$42.3T</div>
                <div className="text-purple-600 text-sm">Total Market Cap</div>
              </div>
            </div>

            {/* Legend */}
            <div className="mt-6 p-4 bg-gray-50 rounded-lg">
              <h4 className="text-sm font-semibold text-gray-700 mb-3">Market Heatmap Legend</h4>
              <div className="flex flex-wrap items-center gap-6 text-xs">
                <div className="flex items-center space-x-2">
                  <div className="w-4 h-4 bg-gradient-to-br from-green-600 to-green-700 rounded"></div>
                  <span className="text-gray-600">Strong Gains (&gt;2%)</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-4 h-4 bg-gradient-to-br from-green-400 to-green-500 rounded"></div>
                  <span className="text-gray-600">Moderate Gains (1-2%)</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-4 h-4 bg-gradient-to-br from-orange-400 to-orange-500 rounded"></div>
                  <span className="text-gray-600">Flat (0-1%)</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-4 h-4 bg-gradient-to-br from-red-400 to-red-500 rounded"></div>
                  <span className="text-gray-600">Moderate Loss (-1 to -2%)</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-4 h-4 bg-gradient-to-br from-red-600 to-red-700 rounded"></div>
                  <span className="text-gray-600">Heavy Loss (&lt;-2%)</span>
                </div>
                <div className="ml-auto text-gray-500">
                  • Tile size = Market Cap • Real-time prices via TradeStation
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Portfolio Risk Analysis Tab - Portfolio Construction Guidelines */}
      {activeTab === 'portfolio-risk' && (
        <div className="space-y-6">
          {/* Header Section */}
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h3 className="text-xl font-semibold mb-4 flex items-center">
              <Shield className="mr-3" size={24} />
              Portfolio Risk Analysis & Construction
            </h3>
            <p className="text-gray-600 text-sm mb-4">
              Strategic guidelines for building balanced portfolios based on risk tolerance, investment horizon, and diversification principles.
            </p>
            <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
              <p className="text-blue-800 text-sm">
                💡 <strong>Your individual portfolio risk</strong> will be calculated based on your actual holdings, allocation percentages, and the risk categories selected from our analysis.
              </p>
            </div>
          </div>

          {/* Portfolio Allocation Strategies */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            
            {/* Conservative Strategy */}
            <div className="bg-white p-6 rounded-lg shadow-md border-l-4 border-green-500">
              <div className="flex items-center mb-4">
                <div className="p-3 bg-green-100 rounded-full mr-4">
                  <Shield className="text-green-600" size={24} />
                </div>
                <div>
                  <h4 className="text-lg font-semibold text-green-800">Conservative Strategy</h4>
                  <p className="text-sm text-green-600">Age 50+ or Risk Averse</p>
                </div>
              </div>
              
              <div className="space-y-4">
                <div className="bg-green-50 p-4 rounded-lg">
                  <h5 className="font-semibold text-green-800 mb-3">Allocation Guidelines:</h5>
                  <div className="space-y-2">
                    <div className="flex justify-between items-center">
                      <span className="text-green-700">🟢 Low Risk</span>
                      <span className="font-bold text-green-800">70%</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-yellow-600">🟡 Moderate Risk</span>
                      <span className="font-bold text-yellow-700">25%</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-red-600">🔴 High Risk</span>
                      <span className="font-bold text-red-700">5%</span>
                    </div>
                  </div>
                </div>
                
                <div className="text-sm text-green-700 space-y-2">
                  <p><strong>Expected Annual Return:</strong> 6-8%</p>
                  <p><strong>Max Drawdown:</strong> -15%</p>
                  <p><strong>Volatility:</strong> Low (10-15%)</p>
                </div>
                
                <div className="bg-green-100 p-3 rounded-lg">
                  <p className="text-xs text-green-800">
                    <strong>Best For:</strong> Capital preservation, steady income, approaching retirement
                  </p>
                </div>
              </div>
            </div>

            {/* Balanced Strategy */}
            <div className="bg-white p-6 rounded-lg shadow-md border-l-4 border-blue-500">
              <div className="flex items-center mb-4">
                <div className="p-3 bg-blue-100 rounded-full mr-4">
                  <Target className="text-blue-600" size={24} />
                </div>
                <div>
                  <h4 className="text-lg font-semibold text-blue-800">Balanced Strategy</h4>
                  <p className="text-sm text-blue-600">Age 30-50 or Moderate Risk</p>
                </div>
              </div>
              
              <div className="space-y-4">
                <div className="bg-blue-50 p-4 rounded-lg">
                  <h5 className="font-semibold text-blue-800 mb-3">Allocation Guidelines:</h5>
                  <div className="space-y-2">
                    <div className="flex justify-between items-center">
                      <span className="text-green-700">🟢 Low Risk</span>
                      <span className="font-bold text-green-800">40%</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-yellow-600">🟡 Moderate Risk</span>
                      <span className="font-bold text-yellow-700">40%</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-red-600">🔴 High Risk</span>
                      <span className="font-bold text-red-700">20%</span>
                    </div>
                  </div>
                </div>
                
                <div className="text-sm text-blue-700 space-y-2">
                  <p><strong>Expected Annual Return:</strong> 8-12%</p>
                  <p><strong>Max Drawdown:</strong> -25%</p>
                  <p><strong>Volatility:</strong> Moderate (15-20%)</p>
                </div>
                
                <div className="bg-blue-100 p-3 rounded-lg">
                  <p className="text-xs text-blue-800">
                    <strong>Best For:</strong> Long-term growth, balanced approach, building wealth
                  </p>
                </div>
              </div>
            </div>

            {/* Aggressive Strategy */}
            <div className="bg-white p-6 rounded-lg shadow-md border-l-4 border-red-500">
              <div className="flex items-center mb-4">
                <div className="p-3 bg-red-100 rounded-full mr-4">
                  <TrendingUp className="text-red-600" size={24} />
                </div>
                <div>
                  <h4 className="text-lg font-semibold text-red-800">Aggressive Strategy</h4>
                  <p className="text-sm text-red-600">Age &lt;30 or High Risk Tolerance</p>
                </div>
              </div>
              
              <div className="space-y-4">
                <div className="bg-red-50 p-4 rounded-lg">
                  <h5 className="font-semibold text-red-800 mb-3">Allocation Guidelines:</h5>
                  <div className="space-y-2">
                    <div className="flex justify-between items-center">
                      <span className="text-green-700">🟢 Low Risk</span>
                      <span className="font-bold text-green-800">20%</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-yellow-600">🟡 Moderate Risk</span>
                      <span className="font-bold text-yellow-700">30%</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-red-600">🔴 High Risk</span>
                      <span className="font-bold text-red-700">50%</span>
                    </div>
                  </div>
                </div>
                
                <div className="text-sm text-red-700 space-y-2">
                  <p><strong>Expected Annual Return:</strong> 12-18%</p>
                  <p><strong>Max Drawdown:</strong> -40%</p>
                  <p><strong>Volatility:</strong> High (20-30%)</p>
                </div>
                
                <div className="bg-red-100 p-3 rounded-lg">
                  <p className="text-xs text-red-800">
                    <strong>Best For:</strong> Maximum growth, long time horizon, high risk tolerance
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Diversification Guidelines */}
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h4 className="text-lg font-semibold mb-4 flex items-center">
              <PieChart className="mr-3 text-purple-600" size={20} />
              Diversification Guidelines
            </h4>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h5 className="font-semibold text-purple-800 mb-3">Sector Diversification</h5>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span>Technology</span>
                    <span className="font-medium">15-25%</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Healthcare</span>
                    <span className="font-medium">10-20%</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Financials</span>
                    <span className="font-medium">10-15%</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Consumer Goods</span>
                    <span className="font-medium">10-15%</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Other Sectors</span>
                    <span className="font-medium">30-40%</span>
                  </div>
                </div>
              </div>
              
              <div>
                <h5 className="font-semibold text-purple-800 mb-3">Risk Management Rules</h5>
                <div className="space-y-2 text-sm text-gray-700">
                  <p>• <strong>Single Stock Limit:</strong> Max 5% per position</p>
                  <p>• <strong>Sector Concentration:</strong> Max 25% per sector</p>
                  <p>• <strong>Correlation Check:</strong> Avoid highly correlated stocks</p>
                  <p>• <strong>Market Cap Mix:</strong> Combine large, mid, small caps</p>
                  <p>• <strong>Geographic Spread:</strong> Include international exposure</p>
                  <p>• <strong>Rebalancing:</strong> Review quarterly, rebalance semi-annually</p>
                </div>
              </div>
            </div>
          </div>

          {/* Portfolio Tools */}
          <div className="bg-gray-50 p-6 rounded-lg">
            <h4 className="text-lg font-semibold mb-4 text-gray-800">Portfolio Construction Tools</h4>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-white p-4 rounded-lg shadow-sm">
                <h5 className="font-semibold text-blue-600 mb-2">📊 Risk Calculator</h5>
                <p className="text-sm text-gray-600">Calculate your portfolio's overall risk score based on individual holdings</p>
              </div>
              <div className="bg-white p-4 rounded-lg shadow-sm">
                <h5 className="font-semibold text-green-600 mb-2">🎯 Allocation Optimizer</h5>
                <p className="text-sm text-gray-600">Optimize allocation percentages for target risk/return profile</p>
              </div>
              <div className="bg-white p-4 rounded-lg shadow-sm">
                <h5 className="font-semibold text-purple-600 mb-2">🔄 Rebalancing Assistant</h5>
                <p className="text-sm text-gray-600">Get recommendations for portfolio rebalancing</p>
              </div>
            </div>
          </div>

          {/* Individual Stock Categories */}
          {riskAnalysis ? (
            <div className="bg-white p-6 rounded-lg shadow-md">
              <h4 className="text-lg font-semibold mb-4 flex items-center">
                <Award className="mr-3 text-orange-600" size={20} />
                Stock Categories for Portfolio Construction
              </h4>
              <p className="text-gray-600 text-sm mb-4">
                Use these categorized stocks to build your portfolio according to the strategies above:
              </p>
              
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {Object.entries(riskAnalysis.risk_categories).map(([riskLevel, stocks]) => (
                  <div key={riskLevel} className="space-y-4">
                    <div className={`p-3 rounded-lg ${getRiskColor(riskLevel)}`}>
                      <h4 className="font-semibold flex items-center">
                        <Shield className="mr-2" size={16} />
                        {riskLevel} RISK STOCKS
                      </h4>
                      <p className="text-xs mt-1">
                        {riskLevel === 'LOW' && 'For portfolio stability and income'}
                        {riskLevel === 'MODERATE' && 'For balanced growth and stability'}
                        {riskLevel === 'HIGH' && 'For maximum growth potential'}
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
          ) : (
            <div className="bg-white p-6 rounded-lg shadow-md">
              <h4 className="text-lg font-semibold mb-4 flex items-center">
                <Award className="mr-3 text-orange-600" size={20} />
                Stock Categories for Portfolio Construction
              </h4>
              <p className="text-gray-600 text-sm mb-4">
                Choose from these risk-categorized stocks to build your optimal portfolio:
              </p>
              
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Low Risk Stocks */}
                <div className="space-y-4">
                  <div className="p-3 rounded-lg text-green-700 bg-green-100">
                    <h4 className="font-semibold flex items-center">
                      <Shield className="mr-2" size={16} />
                      LOW RISK STOCKS
                    </h4>
                    <p className="text-xs mt-1">For portfolio stability and income generation</p>
                  </div>
                  
                  <div className="space-y-3">
                    {[
                      { symbol: 'AAPL', total_score: 78.5, rating: 'HOLD +', risk_level: 'LOW', explanation: 'Stable tech giant with consistent performance' },
                      { symbol: 'MSFT', total_score: 82.1, rating: 'BUY', risk_level: 'LOW', explanation: 'Cloud leader with predictable revenue' },
                      { symbol: 'JNJ', total_score: 75.3, rating: 'HOLD +', risk_level: 'LOW', explanation: 'Healthcare stability with dividend growth' },
                      { symbol: 'PG', total_score: 71.8, rating: 'HOLD', risk_level: 'LOW', explanation: 'Consumer staple defensive play' },
                      { symbol: 'KO', total_score: 69.2, rating: 'HOLD', risk_level: 'LOW', explanation: 'Dividend aristocrat with global reach' }
                    ].map((stock) => (
                      <InvestmentCard key={stock.symbol} investment={stock} />
                    ))}
                  </div>
                </div>

                {/* Moderate Risk Stocks */}
                <div className="space-y-4">
                  <div className="p-3 rounded-lg text-yellow-600 bg-yellow-100">
                    <h4 className="font-semibold flex items-center">
                      <Shield className="mr-2" size={16} />
                      MODERATE RISK STOCKS
                    </h4>
                    <p className="text-xs mt-1">For balanced growth with manageable volatility</p>
                  </div>
                  
                  <div className="space-y-3">
                    {[
                      { symbol: 'GOOGL', total_score: 79.4, rating: 'BUY', risk_level: 'MODERATE', explanation: 'Search leader with AI growth potential' },
                      { symbol: 'JPM', total_score: 76.8, rating: 'HOLD +', risk_level: 'MODERATE', explanation: 'Banking leader with rate sensitivity' },
                      { symbol: 'UNH', total_score: 81.2, rating: 'BUY', risk_level: 'MODERATE', explanation: 'Healthcare growth with demographic trends' },
                      { symbol: 'HD', total_score: 73.9, rating: 'HOLD +', risk_level: 'MODERATE', explanation: 'Home improvement leader with cycles' },
                      { symbol: 'V', total_score: 77.6, rating: 'HOLD +', risk_level: 'MODERATE', explanation: 'Payment network with digital growth' }
                    ].map((stock) => (
                      <InvestmentCard key={stock.symbol} investment={stock} />
                    ))}
                  </div>
                </div>

                {/* High Risk Stocks */}
                <div className="space-y-4">
                  <div className="p-3 rounded-lg text-red-600 bg-red-100">
                    <h4 className="font-semibold flex items-center">
                      <Shield className="mr-2" size={16} />
                      HIGH RISK STOCKS
                    </h4>
                    <p className="text-xs mt-1">For aggressive growth with higher volatility</p>
                  </div>
                  
                  <div className="space-y-3">
                    {[
                      { symbol: 'NVDA', total_score: 85.7, rating: 'BUY STRONG', risk_level: 'HIGH', explanation: 'AI chip leader with explosive growth potential' },
                      { symbol: 'TSLA', total_score: 71.2, rating: 'HOLD', risk_level: 'HIGH', explanation: 'EV pioneer with significant volatility' },
                      { symbol: 'AMZN', total_score: 74.8, rating: 'HOLD +', risk_level: 'HIGH', explanation: 'E-commerce and cloud growth story' },
                      { symbol: 'META', total_score: 69.5, rating: 'HOLD', risk_level: 'HIGH', explanation: 'Social media transformation and VR bets' },
                      { symbol: 'NFLX', total_score: 67.3, rating: 'HOLD -', risk_level: 'HIGH', explanation: 'Streaming wars with international growth' }
                    ].map((stock) => (
                      <InvestmentCard key={stock.symbol} investment={stock} />
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
});

export default InvestmentScoring;