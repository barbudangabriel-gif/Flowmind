import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
import TradeListTable from './TradeListTable';

const PortfolioTradeList = () => {
  const { portfolioId } = useParams();
  const navigate = useNavigate();
  const [activeFilter, setActiveFilter] = useState('closed');

  // Portfolio information
  const portfolioInfo = {
    'htech-15t': { name: 'HTech 15T', value: 139902.60 }
  };

  const currentPortfolio = portfolioInfo[portfolioId] || portfolioInfo['htech-15t'];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between py-4">
            <div className="flex items-center space-x-4">
              <button
                onClick={() => navigate(`/portfolios/${portfolioId}/charts`)}
                className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <ArrowLeft size={20} className="text-gray-600" />
              </button>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">
                  {currentPortfolio.name} Trade List
                </h1>
                <p className="text-gray-600">Detailed view of all trades and positions</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {/* Filter Controls */}
        <div className="bg-white rounded-xl p-6 shadow-sm mb-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-gray-900">Trade Filters</h2>
          </div>
          
          {/* Trade Status Filter */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Trade Status</label>
            <div className="flex rounded-lg border border-gray-300 overflow-hidden w-fit">
              <button
                onClick={() => setActiveFilter('open')}
                className={`px-4 py-2 text-sm font-medium transition-colors ${
                  activeFilter === 'open'
                    ? 'bg-green-600 text-white'
                    : 'bg-white text-gray-700 hover:bg-gray-50'
                }`}
              >
                Open Trades
              </button>
              <button
                onClick={() => setActiveFilter('closed')}
                className={`px-4 py-2 text-sm font-medium transition-colors ${
                  activeFilter === 'closed'
                    ? 'bg-blue-600 text-white'
                    : 'bg-white text-gray-700 hover:bg-gray-50'
                }`}
              >
                Closed Trades
              </button>
              <button
                onClick={() => setActiveFilter('all')}
                className={`px-4 py-2 text-sm font-medium transition-colors ${
                  activeFilter === 'all'
                    ? 'bg-purple-600 text-white'
                    : 'bg-white text-gray-700 hover:bg-gray-50'
                }`}
              >
                All Trades
              </button>
            </div>
          </div>
        </div>

        {/* Trade List Table */}
        <TradeListTable activeFilter={activeFilter} />
      </div>
    </div>
  );
};

export default PortfolioTradeList;