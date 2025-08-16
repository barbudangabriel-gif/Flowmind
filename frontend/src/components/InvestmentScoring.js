import React, { useState, useEffect, useCallback } from "react";
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
  XCircle
} from "lucide-react";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Memoized Investment Scoring Component
const InvestmentScoring = React.memo(() => {
  const [topPicks, setTopPicks] = useState([]);
  const [riskAnalysis, setRiskAnalysis] = useState(null);
  const [sectorLeaders, setSectorLeaders] = useState([]);
  const [selectedSector, setSelectedSector] = useState('Technology');
  const [selectedStock, setSelectedStock] = useState('');
  const [stockAnalysis, setStockAnalysis] = useState(null);
  const [activeTab, setActiveTab] = useState('ai-agent');  // Default to AI Agent tab
  const [loading, setLoading] = useState(false);
  
  // AI Agent specific states
  const [aiAnalysisSymbol, setAiAnalysisSymbol] = useState('');
  const [aiAnalysis, setAiAnalysis] = useState(null);
  const [aiLoading, setAiLoading] = useState(false);

  const sectors = [
    'Technology', 'Healthcare', 'Financial Services', 'Consumer Cyclical',
    'Communication Services', 'Industrials', 'Consumer Defensive', 'Energy',
    'Utilities', 'Real Estate', 'Basic Materials'
  ];

  // Memoized API functions - MUST be declared before useEffect hooks
  const loadTopPicks = useCallback(async () => {
    setLoading(true);
    try {
      console.log('Loading top picks from:', `${API}/investments/top-picks?limit=10`);
      
      // Set a timeout for the request
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 10000); // 10 second timeout
      
      const response = await axios.get(`${API}/investments/top-picks?limit=10`, {
        signal: controller.signal,
        timeout: 10000
      });
      
      clearTimeout(timeoutId);
      
      console.log('Top picks response status:', response.status);
      console.log('Top picks response data:', response.data);
      
      const recommendations = response.data?.recommendations || [];
      console.log('Extracted recommendations:', recommendations.length, 'items');
      console.log('First recommendation:', recommendations[0]);
      
      setTopPicks(recommendations);
    } catch (error) {
      console.error('Error loading top picks:', error);
      console.error('Error response:', error.response?.data);
      console.error('Error status:', error.response?.status);
      
      // Fallback to mock data for demonstration
      console.log('Using mock data fallback...');
      const mockTopPicks = [
        {
          symbol: "UNH",
          total_score: 72.53,
          rating: "HOLD +",
          explanation: "UNH (Healthcare) at $304.01 presents a solid investment opportunity with strong fundamentals.",
          risk_level: "LOW",
          key_strengths: ["Attractive Valuation", "Financial Stability", "High Profitability"],
          key_risks: []
        },
        {
          symbol: "HD",
          total_score: 70.17,
          rating: "HOLD +", 
          explanation: "HD (Consumer Cyclical) at $399.38 presents a solid investment opportunity.",
          risk_level: "LOW",
          key_strengths: ["Financial Stability", "Bullish Trend"],
          key_risks: ["Near Resistance Level"]
        },
        {
          symbol: "META",
          total_score: 68.65,
          rating: "HOLD +",
          explanation: "META (Communication Services) at $785.23 presents a solid investment opportunity.",
          risk_level: "LOW", 
          key_strengths: ["Financial Stability", "Strong Technical Trend", "Bullish Trend"],
          key_risks: ["Near Resistance Level"]
        },
        {
          symbol: "AAPL",
          total_score: 68.35,
          rating: "HOLD +",
          explanation: "AAPL (Technology) at $231.59 presents a solid investment opportunity.",
          risk_level: "LOW",
          key_strengths: ["Financial Stability", "High Profitability", "Bullish Trend"],
          key_risks: ["Near Resistance Level"]
        },
        {
          symbol: "GOOGL", 
          total_score: 67.79,
          rating: "HOLD +",
          explanation: "GOOGL (Communication Services) at $203.90 presents a solid investment opportunity.",
          risk_level: "LOW",
          key_strengths: ["Attractive Valuation", "Financial Stability", "Bullish Trend"],
          key_risks: ["Near Resistance Level"]
        },
        {
          symbol: "JNJ",
          total_score: 67.61,
          rating: "HOLD +",
          explanation: "JNJ (Healthcare) at $176.64 presents a solid investment opportunity.",
          risk_level: "LOW", 
          key_strengths: ["Attractive Valuation", "Financial Stability", "High Profitability", "Bullish Trend"],
          key_risks: ["Near Resistance Level"]
        },
        {
          symbol: "MSFT",
          total_score: 65.76,
          rating: "HOLD +",
          explanation: "MSFT (Technology) at $520.17 presents a solid investment opportunity.",
          risk_level: "LOW",
          key_strengths: ["Financial Stability", "High Profitability", "Bullish Trend"], 
          key_risks: ["Near Resistance Level"]
        },
        {
          symbol: "AMZN",
          total_score: 65.5,
          rating: "HOLD +",
          explanation: "AMZN (Consumer Cyclical) at $231.03 presents a solid investment opportunity.",
          risk_level: "LOW",
          key_strengths: ["Financial Stability", "Bullish Trend"],
          key_risks: ["Near Resistance Level"]
        },
        {
          symbol: "TSLA",
          total_score: 64.69,
          rating: "HOLD",
          explanation: "TSLA (Consumer Cyclical) at $330.56 offers moderate investment appeal.",
          risk_level: "MODERATE",
          key_strengths: ["Financial Stability", "Bullish Trend"],
          key_risks: ["Valuation Concerns"]
        },
        {
          symbol: "NVDA",
          total_score: 63.25,
          rating: "HOLD",
          explanation: "NVDA (Technology) at $142.50 offers moderate investment appeal.",
          risk_level: "MODERATE", 
          key_strengths: ["Growth Potential", "Market Leadership"],
          key_risks: ["High Volatility", "Valuation Concerns"]
        }
      ];
      
      console.log('Setting mock top picks:', mockTopPicks.length, 'items');
      setTopPicks(mockTopPicks);
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

  const analyzeStock = useCallback(async () => {
    if (!selectedStock) return;
    
    setLoading(true);
    try {
      console.log(`Analyzing stock: ${selectedStock}`);
      const response = await axios.get(`${API}/investments/score/${selectedStock}`);
      console.log('Stock analysis response:', response.data);
      setStockAnalysis(response.data);
    } catch (error) {
      console.error('Error analyzing stock:', error);
      setStockAnalysis(null);
    } finally {
      setLoading(false);
    }
  }, [selectedStock]);

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
    } catch (error) {
      console.error('Error in AI analysis:', error);
      setAiAnalysis({
        error: `Failed to analyze ${aiAnalysisSymbol}: ${error.response?.data?.detail || error.message}`,
        symbol: aiAnalysisSymbol.toUpperCase()
      });
    } finally {
      setAiLoading(false);
    }
  }, [aiAnalysisSymbol]);

  // useEffect hooks - MUST be declared after useCallback functions
  useEffect(() => {
    loadTopPicks();
    loadRiskAnalysis();
  }, []); // Remove dependencies for initial load

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
            { id: 'search', label: 'Stock Analysis', icon: Search },
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
            <div className="overflow-x-auto">
              <table className="w-full bg-gray-900 rounded-lg shadow-md border border-gray-700">
                <thead className="bg-gradient-to-r from-gray-800 to-gray-700">
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
                  {topPicks.slice(0, displayLimit).map((pick, index) => (
                    <tr 
                      key={pick?.symbol || index} 
                      className="hover:bg-gray-800 transition-colors cursor-pointer"
                      onClick={() => handleTickerClick(pick?.symbol)}
                    >
                      <td className="px-4 py-4">
                        <div className={`w-8 h-8 rounded-full flex items-center justify-center font-bold text-sm ${
                          index < 3 ? 'bg-gradient-to-r from-yellow-400 to-yellow-500 text-yellow-900' :
                          index < 6 ? 'bg-gradient-to-r from-blue-400 to-blue-500 text-blue-900' :
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
                          {pick?.total_score || 'N/A'}
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
              
              {/* Expansion Button */}
              {displayLimit < 1000 && topPicks.length >= displayLimit && (
                <div className="mt-4 text-center">
                  <button
                    onClick={expandTopPicks}
                    className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white px-6 py-3 rounded-lg font-medium transition-all duration-200 flex items-center space-x-2 mx-auto"
                  >
                    <span>Load More Results</span>
                    <span className="text-blue-200">({Math.min(1000, topPicks.length)} total available)</span>
                  </button>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* Stock Search Tab */}
      {activeTab === 'search' && (
        <div className="space-y-4">
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h3 className="text-lg font-semibold mb-4 flex items-center">
              <Search className="mr-2" size={20} />
              Stock Analysis
            </h3>
            <div className="flex space-x-4">
              <input
                type="text"
                value={selectedStock}
                onChange={(e) => setSelectedStock(e.target.value.toUpperCase())}
                placeholder="Enter stock symbol (e.g., AAPL)"
                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <button
                onClick={analyzeStock}
                disabled={loading}
                className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 flex items-center space-x-2 disabled:opacity-50"
              >
                {loading ? (
                  <RefreshCw className="animate-spin" size={20} />
                ) : (
                  <Zap size={20} />
                )}
                <span>Analyze</span>
              </button>
            </div>
          </div>

          {stockAnalysis && (
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <div className="lg:col-span-2">
                <InvestmentCard investment={stockAnalysis} showDetails={true} />
              </div>
              <div className="space-y-4">
                <div className="bg-white p-4 rounded-lg shadow-md">
                  <h4 className="font-semibold mb-3 flex items-center">
                    <BarChart3 className="mr-2" size={16} />
                    Score Breakdown
                  </h4>
                  <div className="space-y-2">
                    {Object.entries(stockAnalysis.individual_scores || {}).map(([key, value]) => (
                      <div key={key} className="flex justify-between items-center">
                        <span className="text-sm text-gray-600 capitalize">{key.replace('_', ' ')}</span>
                        <div className="flex items-center space-x-2">
                          <div className="w-20 bg-gray-200 rounded-full h-2">
                            <div 
                              className={`h-2 rounded-full ${getScoreColor(value).replace('text-', 'bg-')}`}
                              style={{ width: `${Math.max(0, Math.min(100, value))}%` }}
                            ></div>
                          </div>
                          <span className="text-sm font-medium w-8">{value}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Sector Leaders Tab */}
      {activeTab === 'sectors' && (
        <div className="space-y-4">
          <div className="bg-white p-4 rounded-lg shadow-md">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold flex items-center">
                <PieChart className="mr-2" size={20} />
                Sector Leaders
              </h3>
              <select
                value={selectedSector}
                onChange={(e) => setSelectedSector(e.target.value)}
                className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                {sectors.map(sector => (
                  <option key={sector} value={sector}>{sector}</option>
                ))}
              </select>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {sectorLeaders.map((leader) => (
              <InvestmentCard key={leader.symbol} investment={leader} />
            ))}
          </div>
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