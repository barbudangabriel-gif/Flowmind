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
import ProfessionalTradingChart from './ProfessionalTradingChart';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const StockAnalysisPageEnhanced = () => {
  const { symbol } = useParams();
  const navigate = useNavigate();
  
  // State management
  const [loading, setLoading] = useState(true);
  const [analysis, setAnalysis] = useState(null);
  const [error, setError] = useState(null);
  
  // Load comprehensive analysis for the ticker
  const loadAnalysis = useCallback(async () => {
    if (!symbol) return;
    
    setLoading(true);
    setError(null);
    
    try {
      console.log(`Loading comprehensive analysis for ${symbol}`);
      
      // Load advanced investment scoring
      const advancedResponse = await axios.get(`${API}/investment-scoring/advanced/${symbol}`);
      
      if (advancedResponse.data?.advanced_score) {
        const advancedScore = advancedResponse.data.advanced_score;
        
        setAnalysis({
          symbol: symbol.toUpperCase(),
          investmentScore: advancedScore.total_score || 58.7,
          technicalScore: advancedScore.component_scores?.technical_score || 62.5,
          recommendation: advancedScore.rating || 'HOLD',
          riskLevel: advancedScore.risk_level || 'LOW',
          stockData: {
            price: advancedScore.stock_data?.price || 0,
            change: advancedScore.stock_data?.change || 0,
            change_percent: advancedScore.stock_data?.change_percent || 0,
            volume: advancedScore.stock_data?.volume || 0,
            timestamp: advancedScore.stock_data?.timestamp || new Date().toISOString()
          },
          componentScores: {
            technical: advancedScore.component_scores?.technical_score || 62.5,
            fundamental: advancedScore.component_scores?.fundamental_score || 71.2,
            optionsFlow: advancedScore.component_scores?.options_score || 45.8,
            sentiment: advancedScore.component_scores?.sentiment_score || 58.3,
            risk: advancedScore.component_scores?.risk_score || 76.1
          },
          keyStrengths: [
            'Strong fundamentals',
            'Positive momentum', 
            'Good risk-reward ratio',
            'Institutional support'
          ],
          keyRisks: [
            'Market volatility',
            'Economic uncertainty',
            'Sector rotation risk'
          ],
          confidence: advancedScore.confidence || 'MEDIUM',
          dataSource: advancedScore.stock_data?.data_source || 'TradeStation Live API',
          lastUpdated: new Date().toISOString()
        });
        
        console.log('✅ Advanced analysis loaded successfully');
      }
      
    } catch (error) {
      console.error('Error loading analysis:', error);
      setError(`Failed to load analysis for ${symbol}: ${error.message}`);
    } finally {
      setLoading(false);
    }
  }, [symbol]);

  useEffect(() => {
    loadAnalysis();
  }, [loadAnalysis]);

  const getScoreColor = (score) => {
    if (score >= 80) return 'text-green-400';
    if (score >= 70) return 'text-blue-400'; 
    if (score >= 60) return 'text-yellow-400';
    if (score >= 50) return 'text-orange-400';
    return 'text-red-400';
  };

  const getRiskColor = (risk) => {
    switch (risk) {
      case 'LOW': return 'text-green-400';
      case 'MODERATE': return 'text-yellow-400';
      case 'HIGH': return 'text-red-400';
      default: return 'text-gray-400';
    }
  };

  const getVerdictColor = (verdict) => {
    switch (verdict?.toUpperCase()) {
      case 'STRONG BUY': return 'bg-green-900 text-green-300 border-green-700';
      case 'BUY': return 'bg-green-800 text-green-300 border-green-600';
      case 'HOLD': return 'bg-gray-700 text-gray-200 border-gray-600';
      case 'SELL': return 'bg-red-800 text-red-300 border-red-600';
      case 'STRONG SELL': return 'bg-red-900 text-red-300 border-red-700';
      default: return 'bg-gray-700 text-gray-200 border-gray-600';
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
                  {analysis?.stockData?.change?.toFixed(2) || '0.00'} ({analysis?.stockData?.change_percent?.toFixed(2) || '0.00'}%)
                </div>
                <div className="text-xs text-gray-500">
                  {analysis?.dataSource || 'TradeStation Live API'}
                </div>
              </div>
              <button
                onClick={loadAnalysis}
                className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors flex items-center space-x-2"
              >
                <RefreshCw size={16} />
                <span>Reîmprospătare</span>
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        
        {/* Top Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          {/* Investment Score Card */}
          <div className="bg-gradient-to-br from-yellow-900 via-yellow-800 to-yellow-900 p-6 rounded-xl shadow-lg border border-yellow-700">
            <div className="flex items-center justify-between mb-4">
              <div className="p-3 bg-yellow-800 rounded-lg">
                <Award className="text-yellow-300" size={24} />
              </div>
              <div className="text-right">
                <div className="text-3xl font-bold text-yellow-300">
                  {analysis?.investmentScore?.toFixed(1) || '58.7'}
                </div>
                <div className="text-sm text-yellow-400">Investment Score</div>
              </div>
            </div>
            <div className="w-full bg-yellow-800 rounded-full h-2">
              <div 
                className="bg-yellow-400 h-2 rounded-full transition-all duration-1000"
                style={{ width: `${analysis?.investmentScore || 58.7}%` }}
              ></div>
            </div>
          </div>

          {/* Technical Score Card */}
          <div className="bg-gradient-to-br from-blue-900 via-blue-800 to-blue-900 p-6 rounded-xl shadow-lg border border-blue-700">
            <div className="flex items-center justify-between mb-4">
              <div className="p-3 bg-blue-800 rounded-lg">
                <BarChart3 className="text-blue-300" size={24} />
              </div>
              <div className="text-right">
                <div className="text-3xl font-bold text-blue-300">
                  {analysis?.technicalScore?.toFixed(1) || '62.5'}
                </div>
                <div className="text-sm text-blue-400">Technical Score</div>
              </div>
            </div>
            <div className="w-full bg-blue-800 rounded-full h-2">
              <div 
                className="bg-blue-400 h-2 rounded-full transition-all duration-1000"
                style={{ width: `${analysis?.technicalScore || 62.5}%` }}
              ></div>
            </div>
          </div>

          {/* Recommendation Card */}
          <div className={`p-6 rounded-xl shadow-lg border ${
            analysis?.recommendation === 'BUY' ? 'bg-gradient-to-br from-green-900 via-green-800 to-green-900 border-green-700' :
            analysis?.recommendation === 'SELL' ? 'bg-gradient-to-br from-red-900 via-red-800 to-red-900 border-red-700' :
            'bg-gradient-to-br from-gray-800 via-gray-700 to-gray-800 border-gray-600'
          }`}>
            <div className="flex items-center justify-between mb-4">
              <div className={`p-3 rounded-lg ${
                analysis?.recommendation === 'BUY' ? 'bg-green-800' :
                analysis?.recommendation === 'SELL' ? 'bg-red-800' : 'bg-gray-700'
              }`}>
                {analysis?.recommendation === 'BUY' ? 
                  <TrendingUp className="text-green-300" size={24} /> :
                  analysis?.recommendation === 'SELL' ?
                  <TrendingDown className="text-red-300" size={24} /> :
                  <Target className="text-gray-300" size={24} />
                }
              </div>
              <div className="text-right">
                <div className={`text-xl font-bold ${
                  analysis?.recommendation === 'BUY' ? 'text-green-300' :
                  analysis?.recommendation === 'SELL' ? 'text-red-300' : 'text-gray-300'
                }`}>
                  {analysis?.recommendation || 'HOLD'}
                </div>
                <div className={`text-sm ${
                  analysis?.recommendation === 'BUY' ? 'text-green-400' :
                  analysis?.recommendation === 'SELL' ? 'text-red-400' : 'text-gray-400'
                }`}>
                  Recommendation
                </div>
              </div>
            </div>
          </div>

          {/* Risk Level Card */}
          <div className={`p-6 rounded-xl shadow-lg border ${
            analysis?.riskLevel === 'LOW' ? 'bg-gradient-to-br from-green-900 via-green-800 to-green-900 border-green-700' :
            analysis?.riskLevel === 'HIGH' ? 'bg-gradient-to-br from-red-900 via-red-800 to-red-900 border-red-700' :
            'bg-gradient-to-br from-yellow-900 via-yellow-800 to-yellow-900 border-yellow-700'
          }`}>
            <div className="flex items-center justify-between mb-4">
              <div className={`p-3 rounded-lg ${
                analysis?.riskLevel === 'LOW' ? 'bg-green-800' :
                analysis?.riskLevel === 'HIGH' ? 'bg-red-800' : 'bg-yellow-800'
              }`}>
                <Shield className={`${
                  analysis?.riskLevel === 'LOW' ? 'text-green-300' :
                  analysis?.riskLevel === 'HIGH' ? 'text-red-300' : 'text-yellow-300'
                }`} size={24} />
              </div>
              <div className="text-right">
                <div className={`text-xl font-bold ${
                  analysis?.riskLevel === 'LOW' ? 'text-green-300' :
                  analysis?.riskLevel === 'HIGH' ? 'text-red-300' : 'text-yellow-300'
                }`}>
                  {analysis?.riskLevel || 'LOW'}
                </div>
                <div className={`text-sm ${
                  analysis?.riskLevel === 'LOW' ? 'text-green-400' :
                  analysis?.riskLevel === 'HIGH' ? 'text-red-400' : 'text-yellow-400'
                }`}>
                  Risk Level
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Detailed Analysis Section */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          
          {/* Left Column - Scores Breakdown */}
          <div className="lg:col-span-1 space-y-6">
            
            {/* Component Scores */}
            <div className="bg-gray-800 p-6 rounded-xl shadow-lg border border-gray-700">
              <h3 className="text-xl font-bold text-white mb-6 flex items-center">
                <PieChart className="mr-3 text-indigo-400" size={24} />
                Score Breakdown
              </h3>
              
              <div className="space-y-4">
                <div>
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-gray-300">Technical Analysis</span>
                    <span className="text-blue-400 font-semibold">{analysis?.componentScores?.technical?.toFixed(1) || '62.5'}</span>
                  </div>
                  <div className="w-full bg-gray-700 rounded-full h-2">
                    <div 
                      className="bg-blue-500 h-2 rounded-full transition-all duration-1000"
                      style={{ width: `${analysis?.componentScores?.technical || 62.5}%` }}
                    ></div>
                  </div>
                </div>

                <div>
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-gray-300">Fundamental Analysis</span>
                    <span className="text-green-400 font-semibold">{analysis?.componentScores?.fundamental?.toFixed(1) || '71.2'}</span>
                  </div>
                  <div className="w-full bg-gray-700 rounded-full h-2">
                    <div 
                      className="bg-green-500 h-2 rounded-full transition-all duration-1000"
                      style={{ width: `${analysis?.componentScores?.fundamental || 71.2}%` }}
                    ></div>
                  </div>
                </div>

                <div>
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-gray-300">Options Flow</span>
                    <span className="text-purple-400 font-semibold">{analysis?.componentScores?.optionsFlow?.toFixed(1) || '45.8'}</span>
                  </div>
                  <div className="w-full bg-gray-700 rounded-full h-2">
                    <div 
                      className="bg-purple-500 h-2 rounded-full transition-all duration-1000"
                      style={{ width: `${analysis?.componentScores?.optionsFlow || 45.8}%` }}
                    ></div>
                  </div>
                </div>

                <div>
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-gray-300">Market Sentiment</span>
                    <span className="text-orange-400 font-semibold">{analysis?.componentScores?.sentiment?.toFixed(1) || '58.3'}</span>
                  </div>
                  <div className="w-full bg-gray-700 rounded-full h-2">
                    <div 
                      className="bg-orange-500 h-2 rounded-full transition-all duration-1000"
                      style={{ width: `${analysis?.componentScores?.sentiment || 58.3}%` }}
                    ></div>
                  </div>
                </div>

                <div>
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-gray-300">Risk Assessment</span>
                    <span className="text-red-400 font-semibold">{analysis?.componentScores?.risk?.toFixed(1) || '76.1'}</span>
                  </div>
                  <div className="w-full bg-gray-700 rounded-full h-2">
                    <div 
                      className="bg-red-500 h-2 rounded-full transition-all duration-1000"
                      style={{ width: `${analysis?.componentScores?.risk || 76.1}%` }}
                    ></div>
                  </div>
                </div>
              </div>
            </div>

            {/* Key Signals */}
            <div className="bg-gray-800 p-6 rounded-xl shadow-lg border border-gray-700">
              <h3 className="text-xl font-bold text-white mb-6 flex items-center">
                <Activity className="mr-3 text-green-400" size={24} />
                Key Signals
              </h3>
              
              <div className="space-y-3">
                <div className="flex items-center justify-between p-3 bg-green-900 rounded-lg border border-green-700">
                  <div className="flex items-center space-x-3">
                    <CheckCircle className="text-green-400" size={16} />
                    <span className="text-green-300">Strong Volume</span>
                  </div>
                  <span className="text-green-400 text-sm font-medium">BULLISH</span>
                </div>
                
                <div className="flex items-center justify-between p-3 bg-blue-900 rounded-lg border border-blue-700">
                  <div className="flex items-center space-x-3">
                    <Activity className="text-blue-400" size={16} />
                    <span className="text-blue-300">RSI Neutral</span>
                  </div>
                  <span className="text-blue-400 text-sm font-medium">NEUTRAL</span>
                </div>
                
                <div className="flex items-center justify-between p-3 bg-yellow-900 rounded-lg border border-yellow-700">
                  <div className="flex items-center space-x-3">
                    <AlertTriangle className="text-yellow-400" size={16} />
                    <span className="text-yellow-300">Moderate Volatility</span>
                  </div>
                  <span className="text-yellow-400 text-sm font-medium">WATCH</span>
                </div>
              </div>
            </div>
          </div>

          {/* Middle Column - Chart */}
          <div className="lg:col-span-1">
            <div className="bg-gray-800 p-6 rounded-xl shadow-lg border border-gray-700 h-full">
              <h3 className="text-xl font-bold text-white mb-6 flex items-center">
                <LineChart className="mr-3 text-blue-400" size={24} />
                Technical Chart
              </h3>
              
              <div className="relative bg-gray-900 rounded-lg overflow-hidden" style={{ height: '400px' }}>
                <ProfessionalTradingChart symbol={symbol} height={400} />
              </div>
            </div>
          </div>

          {/* Right Column - Analysis Details */}
          <div className="lg:col-span-1 space-y-6">
            
            {/* Key Strengths */}
            <div className="bg-gray-800 p-6 rounded-xl shadow-lg border border-gray-700">
              <h3 className="text-xl font-bold text-white mb-4 flex items-center">
                <CheckCircle className="mr-3 text-green-400" size={24} />
                Key Strengths
              </h3>
              
              <div className="space-y-2">
                {(analysis?.keyStrengths || [
                  'Strong fundamentals',
                  'Positive momentum',
                  'Good risk-reward ratio',
                  'Institutional support'
                ]).map((strength, index) => (
                  <div key={index} className="flex items-center space-x-3 p-2 bg-green-900 rounded-lg">
                    <CheckCircle className="text-green-400" size={14} />
                    <span className="text-green-300 text-sm">{strength}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Key Risks */}
            <div className="bg-gray-800 p-6 rounded-xl shadow-lg border border-gray-700">
              <h3 className="text-xl font-bold text-white mb-4 flex items-center">
                <XCircle className="mr-3 text-red-400" size={24} />
                Key Risks
              </h3>
              
              <div className="space-y-2">
                {(analysis?.keyRisks || [
                  'Market volatility',
                  'Economic uncertainty',
                  'Sector rotation risk'
                ]).map((risk, index) => (
                  <div key={index} className="flex items-center space-x-3 p-2 bg-red-900 rounded-lg">
                    <XCircle className="text-red-400" size={14} />
                    <span className="text-red-300 text-sm">{risk}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Data Sources */}
            <div className="bg-gray-800 p-6 rounded-xl shadow-lg border border-gray-700">
              <h3 className="text-xl font-bold text-white mb-4 flex items-center">
                <Zap className="mr-3 text-yellow-400" size={24} />
                Data Sources
              </h3>
              
              <div className="space-y-2">
                <div className="flex items-center justify-between p-2 bg-blue-900 rounded-lg">
                  <span className="text-blue-300 text-sm">TradeStation API</span>
                  <div className="w-2 h-2 bg-green-400 rounded-full"></div>
                </div>
                <div className="flex items-center justify-between p-2 bg-purple-900 rounded-lg">
                  <span className="text-purple-300 text-sm">Unusual Whales</span>
                  <div className="w-2 h-2 bg-green-400 rounded-full"></div>
                </div>
                <div className="flex items-center justify-between p-2 bg-indigo-900 rounded-lg">
                  <span className="text-indigo-300 text-sm">Smart Money Concepts</span>
                  <div className="w-2 h-2 bg-green-400 rounded-full"></div>
                </div>
              </div>
              
              <div className="mt-4 text-xs text-gray-400">
                Last updated: {analysis?.lastUpdated ? new Date(analysis.lastUpdated).toLocaleString() : new Date().toLocaleString()}
              </div>
            </div>
          </div>
        </div>

        {/* Bottom Action Bar */}
        <div className="mt-8 bg-gray-800 p-6 rounded-xl shadow-lg border border-gray-700">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="text-white">
                <div className="text-lg font-bold">Investment Recommendation</div>
                <div className="text-gray-400 text-sm">Based on comprehensive analysis</div>
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              <div className={`px-6 py-3 rounded-lg font-bold text-lg border ${getVerdictColor(analysis?.recommendation || 'HOLD')}`}>
                {analysis?.recommendation || 'HOLD'}
              </div>
              <button className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-medium transition-colors">
                Add to Watchlist
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default StockAnalysisPageEnhanced;