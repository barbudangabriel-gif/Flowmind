import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Brain,
  TrendingUp,
  TrendingDown,
  ArrowLeft,
  RefreshCw,
  AlertTriangle,
  CheckCircle,
  Target,
  BarChart3,
  DollarSign,
  Zap,
  Activity,
  Shield,
  Clock,
  Bot,
  Eye,
  Calculator,
  Lightbulb
} from 'lucide-react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const SmartRebalancingAgent = () => {
  const { portfolioId } = useParams();
  const navigate = useNavigate();
  
  // State management
  const [loading, setLoading] = useState(true);
  const [analysisData, setAnalysisData] = useState(null);
  const [recommendations, setRecommendations] = useState([]);
  const [smartDCAData, setSmartDCAData] = useState(null);
  const [riskAnalysis, setRiskAnalysis] = useState(null);
  const [marketConditions, setMarketConditions] = useState(null);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('analysis');
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  // Portfolio information
  const portfolioInfo = {
    'htech-15t': { name: 'HTech 15T', value: 139902.60 }
  };

  const currentPortfolio = portfolioInfo[portfolioId] || portfolioInfo['htech-15t'];

  // Fetch AI rebalancing analysis
  const fetchRebalancingAnalysis = async () => {
    setLoading(true);
    setError(null);
    try {
      // Get current portfolio analysis
      const analysisResponse = await axios.post(`${API}/agents/rebalancing-analysis`, {
        portfolio_id: portfolioId
      });
      setAnalysisData(analysisResponse.data?.analysis || {});

      // Get AI recommendations
      const recommendationsResponse = await axios.post(`${API}/agents/rebalancing-recommendations`, {
        portfolio_id: portfolioId
      });
      setRecommendations(recommendationsResponse.data?.recommendations || []);

      // Get Smart DCA analysis
      const dcaResponse = await axios.post(`${API}/agents/smart-dca-analysis`, {
        portfolio_id: portfolioId
      });
      setSmartDCAData(dcaResponse.data?.dca_analysis || {});

      // Get risk analysis
      const riskResponse = await axios.post(`${API}/agents/risk-analysis`, {
        portfolio_id: portfolioId
      });
      setRiskAnalysis(riskResponse.data?.risk_analysis || {});

      // Get market conditions
      const marketResponse = await axios.get(`${API}/agents/market-conditions`);
      setMarketConditions(marketResponse.data?.market_conditions || {});

    } catch (err) {
      console.error('Error fetching rebalancing analysis:', err);
      setError('Failed to load AI analysis');
      // Use mock data for development
      generateMockData();
    } finally {
      setLoading(false);
    }
  };

  // Generate mock data for development
  const generateMockData = () => {
    setAnalysisData({
      portfolio_health: 7.8,
      diversification_score: 6.5,
      risk_score: 8.2,
      leverage_ratio: 1.35,
      concentration_risk: 'MEDIUM',
      sector_allocation: {
        'Technology': 45,
        'Healthcare': 20,
        'Finance': 15,
        'Consumer': 10,
        'Energy': 10
      }
    });

    setRecommendations([
      {
        type: 'REBALANCE',
        priority: 'HIGH',
        action: 'Reduce Technology Exposure',
        current_allocation: 45,
        target_allocation: 35,
        reason: 'Over-concentrated in tech sector. Reduce by $15,000',
        impact: 'Reduces sector risk by 25%',
        confidence: 0.89
      },
      {
        type: 'OPTIONS_ROLL',
        priority: 'MEDIUM',
        action: 'Roll TSLA Call Options',
        symbol: 'TSLA',
        current_expiry: '2024-12-20',
        target_expiry: '2025-01-17',
        reason: 'High theta decay approaching, roll for better time value',
        impact: 'Extends time for position profitability',
        confidence: 0.76
      },
      {
        type: 'SMART_DCA',
        priority: 'HIGH',
        action: 'Initiate DCA on NVDA',
        symbol: 'NVDA',
        bottom_probability: 0.73,
        entry_points: [450, 425, 400],
        allocation_amounts: ['$3,000', '$4,000', '$5,000'],
        reason: 'Technical indicators suggest bottom formation',
        confidence: 0.82
      },
      {
        type: 'POSITION_SIZE',
        priority: 'MEDIUM',
        action: 'Reduce AAPL Position Size',
        symbol: 'AAPL',
        current_weight: 18,
        target_weight: 12,
        reason: 'Position size exceeds optimal portfolio weight',
        impact: 'Improves risk-adjusted returns',
        confidence: 0.71
      }
    ]);

    setSmartDCAData({
      active_opportunities: 3,
      total_capital_required: 25000,
      expected_return: 0.15,
      risk_level: 'MODERATE',
      opportunities: [
        {
          symbol: 'NVDA',
          bottom_confidence: 0.73,
          support_levels: [450, 425, 400],
          allocation_strategy: 'Progressive (30-40-30)',
          technical_signals: ['RSI Oversold', 'Support Test', 'Volume Divergence'],
          timeline: '2-4 weeks'
        },
        {
          symbol: 'META',
          bottom_confidence: 0.68,
          support_levels: [320, 300, 280],
          allocation_strategy: 'Equal Weight (33-33-34)',
          technical_signals: ['Bollinger Bands', 'MACD Divergence', 'institutional buying'],
          timeline: '3-6 weeks'
        },
        {
          symbol: 'AMZN',
          bottom_confidence: 0.61,
          support_levels: [145, 135, 125],
          allocation_strategy: 'Conservative (50-30-20)',
          technical_signals: ['Support Hold', 'Earnings Support'],
          timeline: '4-8 weeks'
        }
      ]
    });

    setRiskAnalysis({
      overall_risk: 'MODERATE-HIGH',
      beta: 1.45,
      var_95: -0.08,
      max_drawdown: -0.15,
      correlation_sp500: 0.82,
      volatility: 0.24,
      sharpe_ratio: 1.23,
      risk_factors: [
        { factor: 'Sector Concentration', level: 'HIGH', impact: 'Tech sector dominance increases volatility' },
        { factor: 'Options Leverage', level: 'MODERATE', impact: 'Options positions add 35% leverage exposure' },
        { factor: 'Market Beta', level: 'HIGH', impact: 'Portfolio moves 45% more than market' }
      ]
    });

    setMarketConditions({
      overall_sentiment: 'NEUTRAL',
      vix: 18.5,
      market_trend: 'SIDEWAYS',
      sector_rotation: 'TECH_TO_VALUE',
      fed_policy: 'HAWKISH',
      earnings_season: 'MODERATE_BEATS',
      technical_outlook: 'CONSOLIDATION',
      recommended_strategy: 'DEFENSIVE_REBALANCE'
    });
  };

  // Run AI analysis
  const runAIAnalysis = async () => {
    setIsAnalyzing(true);
    try {
      // Trigger comprehensive AI analysis
      const aiAnalysisResponse = await axios.post(`${API}/agents/comprehensive-rebalancing`, {
        portfolio_id: portfolioId,
        include_ml_predictions: true,
        include_smart_dca: true,
        risk_tolerance: 'moderate'
      });
      
      // Refresh all data after analysis
      await fetchRebalancingAnalysis();
    } catch (err) {
      console.error('Error running AI analysis:', err);
    } finally {
      setIsAnalyzing(false);
    }
  };

  useEffect(() => {
    fetchRebalancingAnalysis();
  }, [portfolioId]);

  const tabs = [
    { id: 'analysis', label: 'Current Analysis', icon: Brain },
    { id: 'recommendations', label: 'AI Recommendations', icon: Lightbulb },
    { id: 'smart-dca', label: 'Smart DCA', icon: Calculator },
    { id: 'risk', label: 'Risk Management', icon: Shield }
  ];

  const getPriorityColor = (priority) => {
    switch (priority?.toUpperCase()) {
      case 'HIGH': return 'text-red-600 bg-red-100';
      case 'MEDIUM': return 'text-yellow-600 bg-yellow-100';
      case 'LOW': return 'text-green-600 bg-green-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getConfidenceColor = (confidence) => {
    if (confidence >= 0.8) return 'text-green-600';
    if (confidence >= 0.6) return 'text-yellow-600';
    return 'text-red-600';
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <Brain className="h-12 w-12 text-blue-500 mx-auto mb-4 animate-pulse" />
          <p className="text-gray-600">AI is analyzing your portfolio...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-gradient-to-r from-purple-600 to-blue-600 text-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between py-6">
            <div className="flex items-center space-x-4">
              <button
                onClick={() => navigate(`/portfolios/view/${portfolioId}`)}
                className="p-2 hover:bg-white/20 rounded-lg transition-colors"
              >
                <ArrowLeft size={20} />
              </button>
              <div>
                <h1 className="text-2xl font-bold flex items-center">
                  <Bot className="mr-3" size={28} />
                  Smart Rebalancing Agent
                </h1>
                <p className="text-purple-100">
                  AI-powered portfolio optimization for {currentPortfolio.name}
                </p>
              </div>
            </div>
            
            <div className="flex items-center space-x-3">
              <div className="text-right">
                <div className="text-sm text-purple-200">Portfolio Value</div>
                <div className="text-xl font-bold">${currentPortfolio.value.toLocaleString()}</div>
              </div>
              <button
                onClick={runAIAnalysis}
                disabled={isAnalyzing}
                className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-colors ${
                  isAnalyzing
                    ? 'bg-white/20 cursor-not-allowed'
                    : 'bg-white/20 hover:bg-white/30'
                }`}
              >
                {isAnalyzing ? (
                  <RefreshCw size={16} className="animate-spin" />
                ) : (
                  <Zap size={16} />
                )}
                <span>{isAnalyzing ? 'Analyzing...' : 'Run Analysis'}</span>
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
            <div className="flex items-center">
              <AlertTriangle size={16} className="text-red-500 mr-2" />
              <p className="text-red-700">{error}</p>
            </div>
          </div>
        )}

        {/* Tab Navigation */}
        <div className="bg-white rounded-xl shadow-sm mb-6">
          <div className="border-b border-gray-200">
            <div className="flex space-x-8 px-6">
              {tabs.map((tab) => {
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

          {/* Tab Content */}
          <div className="p-6">
            
            {/* Current Analysis Tab */}
            {activeTab === 'analysis' && (
              <div className="space-y-6">
                <div>
                  <h2 className="text-xl font-bold text-gray-900 mb-4">Portfolio Health Overview</h2>
                  <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                    <div className="bg-gradient-to-br from-blue-50 to-blue-100 p-4 rounded-lg">
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="text-blue-600 text-sm font-medium">Health Score</p>
                          <p className="text-2xl font-bold text-blue-900">{analysisData?.portfolio_health}/10</p>
                        </div>
                        <Activity size={24} className="text-blue-500" />
                      </div>
                    </div>
                    
                    <div className="bg-gradient-to-br from-green-50 to-green-100 p-4 rounded-lg">
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="text-green-600 text-sm font-medium">Diversification</p>
                          <p className="text-2xl font-bold text-green-900">{analysisData?.diversification_score}/10</p>
                        </div>
                        <BarChart3 size={24} className="text-green-500" />
                      </div>
                    </div>
                    
                    <div className="bg-gradient-to-br from-yellow-50 to-yellow-100 p-4 rounded-lg">
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="text-yellow-600 text-sm font-medium">Risk Score</p>
                          <p className="text-2xl font-bold text-yellow-900">{analysisData?.risk_score}/10</p>
                        </div>
                        <Shield size={24} className="text-yellow-500" />
                      </div>
                    </div>
                    
                    <div className="bg-gradient-to-br from-purple-50 to-purple-100 p-4 rounded-lg">
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="text-purple-600 text-sm font-medium">Leverage</p>
                          <p className="text-2xl font-bold text-purple-900">{analysisData?.leverage_ratio}x</p>
                        </div>
                        <Target size={24} className="text-purple-500" />
                      </div>
                    </div>
                  </div>
                </div>

                {/* Sector Allocation */}
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Sector Allocation</h3>
                  <div className="bg-gray-50 rounded-lg p-4">
                    {analysisData?.sector_allocation && Object.entries(analysisData.sector_allocation).map(([sector, percentage]) => (
                      <div key={sector} className="flex items-center justify-between py-2">
                        <span className="text-gray-700">{sector}</span>
                        <div className="flex items-center space-x-3">
                          <div className="w-32 bg-gray-200 rounded-full h-2">
                            <div 
                              className="bg-blue-600 h-2 rounded-full" 
                              style={{ width: `${percentage}%` }}
                            ></div>
                          </div>
                          <span className="text-sm font-medium text-gray-900 w-12">{percentage}%</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Market Conditions */}
                {marketConditions && (
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-4">Current Market Conditions</h3>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                      <div className="bg-white p-3 rounded-lg border">
                        <p className="text-xs text-gray-600">Sentiment</p>
                        <p className="font-medium">{marketConditions.overall_sentiment}</p>
                      </div>
                      <div className="bg-white p-3 rounded-lg border">
                        <p className="text-xs text-gray-600">VIX</p>
                        <p className="font-medium">{marketConditions.vix}</p>
                      </div>
                      <div className="bg-white p-3 rounded-lg border">
                        <p className="text-xs text-gray-600">Trend</p>
                        <p className="font-medium">{marketConditions.market_trend}</p>
                      </div>
                      <div className="bg-white p-3 rounded-lg border">
                        <p className="text-xs text-gray-600">Strategy</p>
                        <p className="font-medium text-xs">{marketConditions.recommended_strategy}</p>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* AI Recommendations Tab */}
            {activeTab === 'recommendations' && (
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <h2 className="text-xl font-bold text-gray-900">AI Recommendations</h2>
                  <span className="text-sm text-gray-600">{recommendations.length} recommendations</span>
                </div>
                
                {recommendations.map((rec, index) => (
                  <div key={index} className="bg-white border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow">
                    <div className="flex items-start justify-between mb-4">
                      <div className="flex items-center space-x-3">
                        <span className={`px-2 py-1 rounded text-xs font-medium ${getPriorityColor(rec.priority)}`}>
                          {rec.priority}
                        </span>
                        <span className="text-sm text-gray-600">{rec.type}</span>
                      </div>
                      <div className={`text-sm font-medium ${getConfidenceColor(rec.confidence)}`}>
                        {(rec.confidence * 100).toFixed(0)}% confidence
                      </div>
                    </div>
                    
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">{rec.action}</h3>
                    
                    {rec.symbol && (
                      <div className="text-sm text-gray-600 mb-2">
                        <strong>Symbol:</strong> {rec.symbol}
                      </div>
                    )}
                    
                    <p className="text-gray-700 mb-3">{rec.reason}</p>
                    
                    <div className="bg-blue-50 p-3 rounded-lg">
                      <p className="text-blue-800 text-sm">
                        <strong>Expected Impact:</strong> {rec.impact}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {/* Smart DCA Tab */}
            {activeTab === 'smart-dca' && (
              <div className="space-y-6">
                <div>
                  <h2 className="text-xl font-bold text-gray-900 mb-4">Smart Dollar-Cost Averaging</h2>
                  <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
                    <div className="bg-gradient-to-br from-green-50 to-green-100 p-4 rounded-lg">
                      <p className="text-green-600 text-sm font-medium">Active Opportunities</p>
                      <p className="text-2xl font-bold text-green-900">{smartDCAData?.active_opportunities}</p>
                    </div>
                    <div className="bg-gradient-to-br from-blue-50 to-blue-100 p-4 rounded-lg">
                      <p className="text-blue-600 text-sm font-medium">Required Capital</p>
                      <p className="text-2xl font-bold text-blue-900">${smartDCAData?.total_capital_required?.toLocaleString()}</p>
                    </div>
                    <div className="bg-gradient-to-br from-purple-50 to-purple-100 p-4 rounded-lg">
                      <p className="text-purple-600 text-sm font-medium">Expected Return</p>
                      <p className="text-2xl font-bold text-purple-900">{((smartDCAData?.expected_return || 0) * 100).toFixed(1)}%</p>
                    </div>
                    <div className="bg-gradient-to-br from-yellow-50 to-yellow-100 p-4 rounded-lg">
                      <p className="text-yellow-600 text-sm font-medium">Risk Level</p>
                      <p className="text-2xl font-bold text-yellow-900">{smartDCAData?.risk_level}</p>
                    </div>
                  </div>
                </div>

                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">DCA Opportunities</h3>
                  <div className="space-y-4">
                    {smartDCAData?.opportunities?.map((opp, index) => (
                      <div key={index} className="bg-white border border-gray-200 rounded-lg p-6">
                        <div className="flex items-center justify-between mb-4">
                          <h4 className="text-lg font-semibold text-gray-900">{opp.symbol}</h4>
                          <div className={`text-sm font-medium ${getConfidenceColor(opp.bottom_confidence)}`}>
                            {(opp.bottom_confidence * 100).toFixed(0)}% bottom confidence
                          </div>
                        </div>
                        
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                          <div>
                            <p className="text-sm font-medium text-gray-600 mb-2">Support Levels</p>
                            <div className="space-y-1">
                              {opp.support_levels?.map((level, idx) => (
                                <div key={idx} className="text-sm bg-gray-50 px-2 py-1 rounded">
                                  ${level}
                                </div>
                              ))}
                            </div>
                          </div>
                          
                          <div>
                            <p className="text-sm font-medium text-gray-600 mb-2">Strategy</p>
                            <p className="text-sm">{opp.allocation_strategy}</p>
                          </div>
                          
                          <div>
                            <p className="text-sm font-medium text-gray-600 mb-2">Timeline</p>
                            <p className="text-sm">{opp.timeline}</p>
                          </div>
                        </div>
                        
                        <div>
                          <p className="text-sm font-medium text-gray-600 mb-2">Technical Signals</p>
                          <div className="flex flex-wrap gap-2">
                            {opp.technical_signals?.map((signal, idx) => (
                              <span key={idx} className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded-full">
                                {signal}
                              </span>
                            ))}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* Risk Management Tab */}
            {activeTab === 'risk' && (
              <div className="space-y-6">
                <div>
                  <h2 className="text-xl font-bold text-gray-900 mb-4">Risk Analysis</h2>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                    <div className="bg-white p-4 rounded-lg border">
                      <p className="text-sm text-gray-600">Portfolio Beta</p>
                      <p className="text-2xl font-bold text-gray-900">{riskAnalysis?.beta}</p>
                    </div>
                    <div className="bg-white p-4 rounded-lg border">
                      <p className="text-sm text-gray-600">Sharpe Ratio</p>
                      <p className="text-2xl font-bold text-gray-900">{riskAnalysis?.sharpe_ratio}</p>
                    </div>
                    <div className="bg-white p-4 rounded-lg border">
                      <p className="text-sm text-gray-600">Max Drawdown</p>
                      <p className="text-2xl font-bold text-red-600">{((riskAnalysis?.max_drawdown || 0) * 100).toFixed(1)}%</p>
                    </div>
                  </div>
                </div>

                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Risk Factors</h3>
                  <div className="space-y-3">
                    {riskAnalysis?.risk_factors?.map((factor, index) => (
                      <div key={index} className="bg-white border border-gray-200 rounded-lg p-4">
                        <div className="flex items-center justify-between mb-2">
                          <h4 className="font-semibold text-gray-900">{factor.factor}</h4>
                          <span className={`px-2 py-1 rounded text-xs font-medium ${getPriorityColor(factor.level)}`}>
                            {factor.level}
                          </span>
                        </div>
                        <p className="text-gray-700 text-sm">{factor.impact}</p>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default SmartRebalancingAgent;