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
  Shield
} from 'lucide-react';

const AllPortfolios = () => {
  const navigate = useNavigate();
  const [portfolios] = useState([
    {
      id: 'portfolio-1',
      name: 'Portfolio 1',
      value: '$125,450.00',
      change: -1.15,
      changeAmount: -1450.23,
      holdings: 12,
      lastUpdated: '2 minutes ago',
      riskLevel: 'MODERATE',
      allocation: { stocks: 70, bonds: 20, cash: 10 }
    },
    {
      id: 'portfolio-2', 
      name: 'Portfolio 2',
      value: '$89,230.00',
      change: 0.54,
      changeAmount: 481.64,
      holdings: 8,
      lastUpdated: '1 minute ago',
      riskLevel: 'LOW',
      allocation: { stocks: 60, bonds: 30, cash: 10 }
    },
    {
      id: 'portfolio-3',
      name: 'Portfolio 3', 
      value: '$205,890.00',
      change: 1.39,
      changeAmount: 2828.36,
      holdings: 18,
      lastUpdated: '5 minutes ago',
      riskLevel: 'HIGH',
      allocation: { stocks: 85, bonds: 10, cash: 5 }
    },
    {
      id: 'portfolio-htech',
      name: 'HTech 15T',
      value: '$310,675.00',
      change: -0.07,
      changeAmount: -217.49,
      holdings: 15,
      lastUpdated: '3 minutes ago',
      riskLevel: 'HIGH',
      allocation: { stocks: 90, bonds: 5, cash: 5 }
    }
  ]);

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
      default: return 'bg-gray-100 text-gray-800';
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
                <p className="text-2xl font-bold text-white">$731,245</p>
              </div>
              <DollarSign className="text-green-400" size={32} />
            </div>
          </div>
          
          <div className="bg-gray-800 p-6 rounded-xl shadow-lg border border-gray-700">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-sm">Total Portfolios</p>
                <p className="text-2xl font-bold text-white">4</p>
              </div>
              <Briefcase className="text-blue-400" size={32} />
            </div>
          </div>
          
          <div className="bg-gray-800 p-6 rounded-xl shadow-lg border border-gray-700">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-sm">Daily P&L</p>
                <p className="text-2xl font-bold text-green-400">+$1,642</p>
              </div>
              <TrendingUp className="text-green-400" size={32} />
            </div>
          </div>
          
          <div className="bg-gray-800 p-6 rounded-xl shadow-lg border border-gray-700">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-sm">Best Performer</p>
                <p className="text-xl font-bold text-white">Portfolio 3</p>
                <p className="text-sm text-green-400">+1.39%</p>
              </div>
              <Target className="text-orange-400" size={32} />
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