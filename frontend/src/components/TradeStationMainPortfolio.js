import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  TrendingUp, 
  TrendingDown, 
  RefreshCw, 
  Activity,
  DollarSign,
  Target,
  BarChart3,
  PieChart as PieChartIcon,
  Eye,
  AlertCircle
} from 'lucide-react';

const TradeStationMainPortfolio = () => {
  const navigate = useNavigate();
  const [portfolioData, setPortfolioData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(new Date());

  const backendUrl = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

  // Fetch real TradeStation data directly from TradeStation API (not Portfolio Management Service)
  const fetchTradeStationData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Get accounts first
      const accountsResponse = await fetch(`${backendUrl}/api/tradestation/accounts`);
      if (!accountsResponse.ok) throw new Error(`Failed to fetch accounts: ${accountsResponse.status}`);
      const accountsData = await accountsResponse.json();
      
      console.log('🔍 Raw accounts response:', accountsData);
      
      // Find the margin account (usually the main trading account)
      // The accounts are directly in the response, not under .accounts
      const accounts = accountsData.accounts || accountsData;
      console.log('🔍 Parsed accounts:', accounts);
      
      let mainAccount;
      if (Array.isArray(accounts)) {
        mainAccount = accounts.find(acc => acc.Type === 'Margin') || accounts[0];
      } else if (accounts && typeof accounts === 'object') {
        // If accounts is an object, check if it has account properties
        mainAccount = accounts;
      }
      
      console.log('🎯 Selected account:', mainAccount);
      
      if (!mainAccount || !mainAccount.AccountID) {
        throw new Error(`No valid TradeStation account found. Accounts structure: ${JSON.stringify(accounts)}`);
      }
      
      console.log('🎯 Using account:', mainAccount.AccountID);
      
      // Get positions for the main account
      const positionsResponse = await fetch(`${backendUrl}/api/tradestation/accounts/${mainAccount.AccountID}/positions`);
      if (!positionsResponse.ok) throw new Error(`Failed to fetch positions: ${positionsResponse.status}`);
      const positionsData = await positionsResponse.json();
      
      console.log('🔍 Raw positions response:', positionsData);
      console.log('🔍 Positions response keys:', Object.keys(positionsData || {}));
      console.log('🔍 Positions data field:', positionsData.data);
      
      // Calculate portfolio totals from real TradeStation data
      let positions;
      if (positionsData.data && Array.isArray(positionsData.data)) {
        positions = positionsData.data;
      } else if (Array.isArray(positionsData)) {
        positions = positionsData;
      } else {
        positions = [];
      }
      
      console.log('🔍 Final positions array:', {
        isArray: Array.isArray(positions),
        count: positions.length,
        firstPosition: positions[0]
      });
      
      let totalMarketValue = 0;
      let totalUnrealizedPnL = 0;
      
      positions.forEach(position => {
        const marketValue = Math.abs(position.quantity * position.mark_price);
        const unrealizedPnL = position.unrealized_pnl || 0;
        
        console.log('📊 Processing position:', {
          symbol: position.symbol,
          quantity: position.quantity,
          markPrice: position.mark_price,
          marketValue,
          unrealizedPnL
        });
        
        totalMarketValue += marketValue;
        totalUnrealizedPnL += unrealizedPnL;
      });
      
      // Calculate percentage change
      const costBasis = totalMarketValue - totalUnrealizedPnL;
      const percentChange = costBasis !== 0 ? (totalUnrealizedPnL / costBasis) * 100 : 0;
      
      // Group positions by asset type
      const stocks = positions.filter(p => p.asset_type === 'STOCK');
      const options = positions.filter(p => p.asset_type === 'STOCKOPTION');
      
      console.log('🎯 Final portfolio calculated:', {
        totalMarketValue,
        totalUnrealizedPnL,
        percentChange,
        totalPositions: positions.length,
        stocks: stocks.length,
        options: options.length
      });
      
      setPortfolioData({
        account: mainAccount,
        totalMarketValue,
        totalUnrealizedPnL,
        percentChange,
        totalPositions: positionsArray.length,
        stocks: stocks.length,
        options: options.length,
        positions: positionsArray
      });
      
      setLastUpdated(new Date());
      
    } catch (err) {
      setError(err.message);
      console.error('Error fetching TradeStation data:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTradeStationData();
  }, []);

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value);
  };

  const getChangeColor = (value) => {
    return value >= 0 ? 'text-green-500' : 'text-red-500';
  };

  const getChangeIcon = (value) => {
    return value >= 0 ? TrendingUp : TrendingDown;
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <span className="text-xl text-gray-300">Loading TradeStation Portfolio...</span>
          <p className="text-gray-500 mt-2">Fetching real-time data from TradeStation API</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 flex items-center justify-center">
        <div className="text-center max-w-md">
          <AlertCircle className="mx-auto h-16 w-16 text-red-500 mb-4" />
          <h2 className="text-xl font-bold text-white mb-2">Error Loading Portfolio</h2>
          <p className="text-gray-400 mb-6">{error}</p>
          <button
            onClick={fetchTradeStationData}
            className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  const ChangeIcon = getChangeIcon(portfolioData?.totalUnrealizedPnL);

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900">
      {/* Header */}
      <div className="bg-gradient-to-r from-green-600 to-blue-600 shadow-lg">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-white flex items-center">
                <Activity className="mr-3" size={32} />
                TradeStation Main Portfolio
              </h1>
              <p className="text-blue-100 mt-2">
                Account: {portfolioData?.account?.AccountID} • Live Trading Account
              </p>
            </div>
            
            <button 
              onClick={fetchTradeStationData}
              className="bg-white/20 text-white px-4 py-2 rounded-lg hover:bg-white/30 transition-colors flex items-center space-x-2"
              disabled={loading}
            >
              <RefreshCw size={16} className={loading ? 'animate-spin' : ''} />
              <span>Refresh</span>
            </button>
          </div>
          
          {/* Portfolio Value Display */}
          <div className="mt-6">
            <div className="flex items-center space-x-2">
              <Eye className="text-white" size={20} />
              <span className="text-4xl font-bold text-white">
                {formatCurrency(portfolioData?.totalMarketValue || 0)}
              </span>
            </div>
            <div className={`flex items-center mt-2 space-x-2 ${getChangeColor(portfolioData?.totalUnrealizedPnL)}`}>
              <ChangeIcon size={24} />
              <span className="text-2xl font-semibold">
                {portfolioData?.totalUnrealizedPnL >= 0 ? '+' : ''}{formatCurrency(portfolioData?.totalUnrealizedPnL || 0)}
              </span>
              <span className="text-lg">
                ({portfolioData?.percentChange >= 0 ? '+' : ''}{(portfolioData?.percentChange || 0).toFixed(2)}%)
              </span>
            </div>
            <p className="text-blue-100 text-sm mt-1">
              Last updated: {lastUpdated.toLocaleString()}
            </p>
          </div>
        </div>
      </div>

      {/* Portfolio Stats */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-gray-800 p-6 rounded-xl shadow-lg border border-gray-700">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-sm">Total Positions</p>
                <p className="text-3xl font-bold text-white">{portfolioData?.totalPositions || 0}</p>
              </div>
              <Target className="text-blue-400" size={32} />
            </div>
          </div>
          
          <div className="bg-gray-800 p-6 rounded-xl shadow-lg border border-gray-700">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-sm">Stock Positions</p>
                <p className="text-3xl font-bold text-white">{portfolioData?.stocks || 0}</p>
              </div>
              <BarChart3 className="text-green-400" size={32} />
            </div>
          </div>
          
          <div className="bg-gray-800 p-6 rounded-xl shadow-lg border border-gray-700">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-sm">Options Positions</p>
                <p className="text-3xl font-bold text-white">{portfolioData?.options || 0}</p>
              </div>
              <PieChartIcon className="text-purple-400" size={32} />
            </div>
          </div>
          
          <div className="bg-gray-800 p-6 rounded-xl shadow-lg border border-gray-700">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-sm">Portfolio Value</p>
                <p className="text-2xl font-bold text-white">
                  {formatCurrency(portfolioData?.totalMarketValue || 0)}
                </p>
              </div>
              <DollarSign className="text-yellow-400" size={32} />
            </div>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
          <button 
            onClick={() => navigate('/portfolios/tradestation-main')}
            className="bg-blue-600 text-white p-4 rounded-xl hover:bg-blue-700 transition-colors flex items-center justify-center space-x-3"
          >
            <Eye size={24} />
            <span className="text-lg font-medium">View Detailed Positions</span>
          </button>
          
          <button 
            onClick={() => navigate('/portfolios/tradestation-main/charts')}
            className="bg-green-600 text-white p-4 rounded-xl hover:bg-green-700 transition-colors flex items-center justify-center space-x-3"
          >
            <BarChart3 size={24} />
            <span className="text-lg font-medium">Portfolio Charts</span>
          </button>
          
          <button 
            onClick={() => navigate('/portfolios/tradestation-main/rebalancing')}
            className="bg-purple-600 text-white p-4 rounded-xl hover:bg-purple-700 transition-colors flex items-center justify-center space-x-3"
          >
            <Target size={24} />
            <span className="text-lg font-medium">AI Rebalancing</span>
          </button>
        </div>

        {/* Recent Activity */}
        <div className="bg-gray-800 rounded-xl shadow-lg border border-gray-700 p-6">
          <h3 className="text-xl font-bold text-white mb-4">Portfolio Summary</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h4 className="text-lg font-semibold text-gray-300 mb-2">Performance</h4>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-gray-400">Market Value:</span>
                  <span className="text-white font-medium">{formatCurrency(portfolioData?.totalMarketValue || 0)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Unrealized P&L:</span>
                  <span className={`font-medium ${getChangeColor(portfolioData?.totalUnrealizedPnL)}`}>
                    {portfolioData?.totalUnrealizedPnL >= 0 ? '+' : ''}{formatCurrency(portfolioData?.totalUnrealizedPnL || 0)}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Percentage Change:</span>
                  <span className={`font-medium ${getChangeColor(portfolioData?.totalUnrealizedPnL)}`}>
                    {portfolioData?.percentChange >= 0 ? '+' : ''}{(portfolioData?.percentChange || 0).toFixed(2)}%
                  </span>
                </div>
              </div>
            </div>
            
            <div>
              <h4 className="text-lg font-semibold text-gray-300 mb-2">Asset Allocation</h4>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-gray-400">Stock Positions:</span>
                  <span className="text-white font-medium">{portfolioData?.stocks || 0}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Options Positions:</span>
                  <span className="text-white font-medium">{portfolioData?.options || 0}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Total Positions:</span>
                  <span className="text-white font-medium">{portfolioData?.totalPositions || 0}</span>
                </div>
              </div>
            </div>
          </div>
          
          <div className="mt-6 pt-4 border-t border-gray-700">
            <p className="text-sm text-gray-400">
              Data source: TradeStation Direct API • Account: {portfolioData?.account?.AccountID} • 
              Last refresh: {lastUpdated.toLocaleString()}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TradeStationMainPortfolio;