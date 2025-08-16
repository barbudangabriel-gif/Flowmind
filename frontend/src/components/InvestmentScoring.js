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
      const response = await axios.get(`${API}/investments/top-picks?limit=10`);
      console.log('Top picks response:', response.data);
      const recommendations = response.data.recommendations || [];
      console.log('Setting topPicks to:', recommendations.length, 'items');
      setTopPicks(recommendations);
    } catch (error) {
      console.error('Error loading top picks:', error);
      setTopPicks([]); // Ensure it's always an array
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
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {topPicks.slice(0, 9).map((pick, index) => (
                <div key={pick?.symbol || index} className="relative">
                  {index < 3 && (
                    <div className="absolute -top-2 -right-2 bg-yellow-400 text-yellow-900 text-xs font-bold px-2 py-1 rounded-full z-10">
                      #{index + 1}
                    </div>
                  )}
                  <InvestmentCard investment={pick} />
                </div>
              ))}
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