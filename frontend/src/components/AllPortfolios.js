import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  TrendingUp, 
  TrendingDown, 
  Plus, 
  Briefcase, 
  PieChart, 
  BarChart3,
  Target,
  DollarSign,
  Clock,
  Shield,
  RefreshCw,
  Activity
} from 'lucide-react';
import usePortfolioManagement from '../hooks/usePortfolioManagement';

const AllPortfolios = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  
  // Use real portfolio management hook
  const {
    portfolios,
    loading: apiLoading,
    error,
    fetchPortfolios,
    clearError
  } = usePortfolioManagement();

  // Load portfolios on component mount
  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      try {
        await fetchPortfolios();
      } catch (err) {
        console.error('Error loading portfolios:', err);
      } finally {
        setLoading(false);
      }
    };
    
    loadData();
  }, []);

  // Calculate aggregate stats from real data
  const aggregateStats = React.useMemo(() => {
    if (!portfolios || portfolios.length === 0) {
      return {
        totalValue: 0,
        totalPnl: 0,
        totalPortfolios: 0,
        activePortfolio: 'No Portfolios'
      };
    }
    
    const totalValue = portfolios.reduce((sum, p) => sum + (p.total_value || 0), 0);
    const totalPnl = portfolios.reduce((sum, p) => sum + (p.total_pnl || 0), 0);
    const mainPortfolio = portfolios.find(p => p.id === 'tradestation-main');
    
    return {
      totalValue,
      totalPnl,
      totalPortfolios: portfolios.length,
      activePortfolio: mainPortfolio ? mainPortfolio.name : portfolios[0]?.name || 'No Portfolio'
    };
  }, [portfolios]);

  const getTrendIcon = (change) => {
    return change >= 0 ? TrendingUp : TrendingDown;
  };

  const getChangeColor = (change) => {
    return change >= 0 ? 'text-green-500' : 'text-red-500';
  };

  const getBgChangeColor = (change) => {
    return change >= 0 ? 'bg-green-50 border-green-200' : 'bg-red-50 border-red-200';
  };

  const getRiskColor = (category) => {
    switch (category) {
      case 'main': return 'bg-blue-100 text-blue-800';
      case 'long-term': return 'bg-green-100 text-green-800';  
      case 'medium-term': return 'bg-yellow-100 text-yellow-800';
      case 'short-term': return 'bg-red-100 text-red-800';
      case 'custom': return 'bg-purple-100 text-purple-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getCategoryLabel = (category) => {
    switch (category) {
      case 'main': return 'MAIN ACCOUNT';
      case 'long-term': return 'LONG TERM';
      case 'medium-term': return 'MEDIUM TERM';
      case 'short-term': return 'SHORT TERM';
      case 'custom': return 'CUSTOM';
      default: return 'PORTFOLIO';
    }
  };

  const handleRefresh = async () => {
    setLoading(true);
    try {
      await fetchPortfolios();
    } finally {
      setLoading(false);
    }
  };

  const formatValue = (value) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value);
  };

  if (loading || apiLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <span className="text-xl text-gray-300">Loading portfolios...</span>
          <p className="text-gray-500 mt-2">Fetching real TradeStation data</p>
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
            <div>
              <h1 className="text-2xl font-bold text-white flex items-center">
                <Briefcase className="mr-3 text-blue-400" size={28} />
                All Portfolios
              </h1>
              <p className="text-sm text-gray-400">
                Manage and monitor your TradeStation portfolios
              </p>
            </div>
            
            <div className="flex space-x-3">
              <button 
                onClick={handleRefresh}
                className="bg-gray-700 text-white px-4 py-2 rounded-lg hover:bg-gray-600 transition-colors flex items-center space-x-2"
                disabled={loading}
              >
                <RefreshCw size={16} className={loading ? 'animate-spin' : ''} />
                <span>Refresh</span>
              </button>
              
              <button 
                onClick={() => navigate('/portfolios/create')}
                className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors flex items-center space-x-2"
              >
                <Plus size={20} />
                <span>Create Portfolio</span>
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="bg-red-50 border border-red-200 rounded-lg p-4">
            <span className="text-red-700">Error: {error}</span>
            <button
              onClick={clearError}
              className="ml-2 text-red-600 hover:text-red-800"
            >
              Dismiss
            </button>
          </div>
        </div>
      )}

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        
        {/* Portfolio Summary Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-gray-800 p-6 rounded-xl shadow-lg border border-gray-700">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-sm">Total Value</p>
                <p className="text-2xl font-bold text-white">
                  {formatValue(aggregateStats.totalValue)}
                </p>
              </div>
              <DollarSign className="text-green-400" size={32} />
            </div>
          </div>
          
          <div className="bg-gray-800 p-6 rounded-xl shadow-lg border border-gray-700">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-sm">Total Portfolios</p>
                <p className="text-2xl font-bold text-white">{aggregateStats.totalPortfolios}</p>
              </div>
              <Briefcase className="text-blue-400" size={32} />
            </div>
          </div>
          
          <div className="bg-gray-800 p-6 rounded-xl shadow-lg border border-gray-700">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-sm">Unrealized P&L</p>
                <p className={`text-2xl font-bold ${getChangeColor(aggregateStats.totalPnl)}`}>
                  {aggregateStats.totalPnl >= 0 ? '+' : ''}{formatValue(aggregateStats.totalPnl)}
                </p>
              </div>
              {aggregateStats.totalPnl >= 0 ? 
                <TrendingUp className="text-green-400" size={32} /> : 
                <TrendingDown className="text-red-400" size={32} />
              }
            </div>
          </div>
          
          <div className="bg-gray-800 p-6 rounded-xl shadow-lg border border-gray-700">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-sm">Main Portfolio</p>
                <p className="text-lg font-bold text-white">{aggregateStats.activePortfolio}</p>
                <p className="text-xs text-blue-400">Live TradeStation</p>
              </div>
              <Activity className="text-blue-400" size={32} />
            </div>
          </div>
        </div>

        {/* Portfolio Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-2 gap-6">
          {portfolios && portfolios.length > 0 ? (
            portfolios.map((portfolio) => {
              const changePercent = portfolio.total_value > 0 
                ? (portfolio.total_pnl / (portfolio.total_value - portfolio.total_pnl)) * 100 
                : 0;
              
              const TrendIcon = getTrendIcon(portfolio.total_pnl);
              
              return (
                <div 
                  key={portfolio.id}
                  className="bg-gray-800 rounded-xl shadow-lg border border-gray-700 hover:border-blue-500 transition-colors cursor-pointer"
                  onClick={() => navigate(`/portfolios/${portfolio.id}`)}
                >
                  <div className="p-6">
                    {/* Portfolio Header */}
                    <div className="flex items-center justify-between mb-4">
                      <div>
                        <h3 className="text-xl font-bold text-white">{portfolio.name}</h3>
                        <p className="text-gray-400 text-sm">{portfolio.positions_count} positions</p>
                      </div>
                      <div className={`px-3 py-1 rounded-full text-xs font-medium ${getRiskColor(portfolio.category)}`}>
                        {getCategoryLabel(portfolio.category)}
                      </div>
                    </div>

                    {/* Portfolio Value */}
                    <div className="mb-4">
                      <div className="text-3xl font-bold text-white mb-1">
                        {formatValue(portfolio.total_value)}
                      </div>
                      <div className={`flex items-center space-x-2 ${getChangeColor(portfolio.total_pnl)}`}>
                        <TrendIcon size={20} />
                        <span className="text-lg font-semibold">
                          {changePercent >= 0 ? '+' : ''}{changePercent.toFixed(2)}%
                        </span>
                        <span className="text-sm">
                          ({portfolio.total_pnl >= 0 ? '+' : ''}{formatValue(portfolio.total_pnl)})
                        </span>
                      </div>
                    </div>

                    {/* Quick Stats */}
                    <div className="grid grid-cols-2 gap-4 mb-4">
                      <div className="text-center p-3 bg-gray-700 rounded-lg">
                        <div className="text-sm text-gray-400">Positions</div>
                        <div className="text-lg font-bold text-white">{portfolio.positions_count}</div>
                      </div>
                      <div className="text-center p-3 bg-gray-700 rounded-lg">
                        <div className="text-sm text-gray-400">Updated</div>
                        <div className="text-sm font-medium text-blue-400">
                          {new Date(portfolio.last_updated).toLocaleString()}
                        </div>
                      </div>
                    </div>

                    {/* Action Buttons */}
                    <div className="flex space-x-2 pt-4 border-t border-gray-700">
                      <button 
                        className="flex-1 flex items-center justify-center space-x-2 px-3 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                        onClick={(e) => {
                          e.stopPropagation();
                          navigate(`/portfolios/${portfolio.id}`);
                        }}
                      >
                        <PieChart size={16} />
                        <span>View</span>
                      </button>
                      <button 
                        className="flex-1 flex items-center justify-center space-x-2 px-3 py-2 bg-gray-700 text-white rounded-lg hover:bg-gray-600 transition-colors"
                        onClick={(e) => {
                          e.stopPropagation();
                          navigate(`/portfolios/${portfolio.id}/charts`);
                        }}
                      >
                        <BarChart3 size={16} />
                        <span>Charts</span>
                      </button>
                    </div>
                  </div>
                </div>
              );
            })
          ) : (
            <div className="col-span-full text-center py-12">
              <Briefcase className="mx-auto h-16 w-16 text-gray-400 mb-4" />
              <h3 className="text-lg font-medium text-gray-300 mb-2">No portfolios found</h3>
              <p className="text-gray-500 mb-6">
                Get started by creating your first portfolio or check your TradeStation connection.
              </p>
              <button 
                onClick={() => navigate('/portfolios/create')}
                className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors flex items-center space-x-2 mx-auto"
              >
                <Plus size={20} />
                <span>Create Your First Portfolio</span>
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default AllPortfolios;