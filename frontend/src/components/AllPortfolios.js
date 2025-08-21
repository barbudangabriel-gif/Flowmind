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
  RefreshCw
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

  const getRiskColor = (risk) => {
    switch (risk) {
      case 'LOW': return 'bg-green-100 text-green-800';
      case 'MODERATE': return 'bg-yellow-100 text-yellow-800';  
      case 'HIGH': return 'bg-red-100 text-red-800';
      case 'MODERATE-HIGH': return 'bg-orange-100 text-orange-800';
      default: return 'bg-gray-100 text-gray-800';
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

  if (loading || apiLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        <span className="ml-3 text-gray-600">Loading portfolios...</span>
      </div>
    );
  }
  };

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
                Manage and monitor your investment portfolios
              </p>
            </div>
            
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

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        
        {/* Portfolio Summary Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-gray-800 p-6 rounded-xl shadow-lg border border-gray-700">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-sm">Total Value</p>
                <p className="text-2xl font-bold text-white">$139,903</p>
              </div>
              <DollarSign className="text-green-400" size={32} />
            </div>
          </div>
          
          <div className="bg-gray-800 p-6 rounded-xl shadow-lg border border-gray-700">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-sm">Total Portfolios</p>
                <p className="text-2xl font-bold text-white">1</p>
              </div>
              <Briefcase className="text-blue-400" size={32} />
            </div>
          </div>
          
          <div className="bg-gray-800 p-6 rounded-xl shadow-lg border border-gray-700">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-sm">Daily P&L</p>
                <p className="text-2xl font-bold text-green-400">+$112</p>
              </div>
              <TrendingUp className="text-green-400" size={32} />
            </div>
          </div>
          
          <div className="bg-gray-800 p-6 rounded-xl shadow-lg border border-gray-700">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-sm">Active Portfolio</p>
                <p className="text-xl font-bold text-white">HTech 15T</p>
                <p className="text-sm text-green-400">+0.28%</p>
              </div>
              <Target className="text-blue-400" size={32} />
            </div>
          </div>
        </div>

        {/* Portfolios Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-2 gap-6">
          {portfolios.map((portfolio) => {
            const TrendIcon = getTrendIcon(portfolio.change);
            
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
                      <p className="text-gray-400 text-sm">{portfolio.holdings} holdings</p>
                    </div>
                    <div className={`px-3 py-1 rounded-full text-xs font-medium ${getRiskColor(portfolio.riskLevel)}`}>
                      {portfolio.riskLevel} RISK
                    </div>
                  </div>

                  {/* Portfolio Value */}
                  <div className="mb-4">
                    <div className="text-3xl font-bold text-white mb-1">{portfolio.value}</div>
                    <div className={`flex items-center space-x-2 ${getChangeColor(portfolio.change)}`}>
                      <TrendIcon size={20} />
                      <span className="text-lg font-semibold">
                        {portfolio.change >= 0 ? '+' : ''}{portfolio.change.toFixed(2)}%
                      </span>
                      <span className="text-sm">
                        ({portfolio.change >= 0 ? '+' : ''}${portfolio.changeAmount.toFixed(2)})
                      </span>
                    </div>
                  </div>

                  {/* Allocation Bar */}
                  <div className="mb-4">
                    <div className="flex items-center justify-between text-xs text-gray-400 mb-2">
                      <span>Asset Allocation</span>
                      <span>Stocks/Bonds/Cash</span>
                    </div>
                    <div className="w-full bg-gray-700 rounded-full h-2 flex">
                      <div 
                        className="bg-blue-500 h-2 rounded-l-full"
                        style={{ width: `${portfolio.allocation.stocks}%` }}
                      ></div>
                      <div 
                        className="bg-yellow-500 h-2"
                        style={{ width: `${portfolio.allocation.bonds}%` }}
                      ></div>
                      <div 
                        className="bg-gray-500 h-2 rounded-r-full"
                        style={{ width: `${portfolio.allocation.cash}%` }}
                      ></div>
                    </div>
                    <div className="flex justify-between text-xs text-gray-400 mt-1">
                      <span>{portfolio.allocation.stocks}%</span>
                      <span>{portfolio.allocation.bonds}%</span>
                      <span>{portfolio.allocation.cash}%</span>
                    </div>
                  </div>

                  {/* Last Updated */}
                  <div className="flex items-center text-xs text-gray-500">
                    <Clock size={12} className="mr-1" />
                    <span>Updated {portfolio.lastUpdated}</span>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
        
        {/* Empty state for Create Portfolio */}
        <div className="mt-8">
          <div 
            onClick={() => navigate('/portfolios/create')}
            className="bg-gray-800 border-2 border-dashed border-gray-600 rounded-xl p-8 hover:border-blue-500 transition-colors cursor-pointer"
          >
            <div className="text-center">
              <Plus className="mx-auto text-gray-500 mb-4" size={48} />
              <h3 className="text-lg font-medium text-gray-300 mb-2">Create New Portfolio</h3>
              <p className="text-gray-500">Start building your next investment portfolio</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AllPortfolios;