import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { 
  ChevronDown, 
  TrendingUp, 
  TrendingDown, 
  Plus, 
  AlertTriangle,
  X,
  Eye,
  BarChart3,
  FileText,
  Brain,
  PieChart as PieChartIcon,
  Target,
  DollarSign
} from 'lucide-react';
import ContextMenu from './ContextMenu';
import usePortfolioManagement from '../hooks/usePortfolioManagement';

const IndividualPortfolio = () => {
  const navigate = useNavigate();
  const { portfolioId } = useParams();
  const [activeTab, setActiveTab] = useState('holdings');
  const [loading, setLoading] = useState(false);
  
  // Context menu state
  const [contextMenu, setContextMenu] = useState({
    isVisible: false,
    position: { x: 0, y: 0 },
    selectedPosition: null
  });

  // Portfolio management hook
  const {
    portfolios,
    availablePortfolios,
    loading: apiLoading,
    error: hookError,
    fetchPortfolioPositions,
    fetchAvailablePortfolios,
    movePosition,
    clearError
  } = usePortfolioManagement();

  // Current portfolio data
  const [currentPortfolio, setCurrentPortfolio] = useState(null);
  const [positions, setPositions] = useState([]);
  const [cashBalance, setCashBalance] = useState(0); // Add cash balance state
  const [error, setError] = useState(null);

  // Load portfolio and positions data directly from TradeStation API
  useEffect(() => {
    if (portfolioId === 'tradestation-main') {
      // For TradeStation Main, load REAL data directly from TradeStation API
      const loadRealTradeStationData = async () => {
        try {
          setLoading(true);
          
          // Get accounts first
          const accountsResponse = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/tradestation/accounts`);
          const accountsData = await accountsResponse.json();
          
          if (accountsData.status === 'success' && accountsData.accounts.length > 0) {
            const mainAccount = accountsData.accounts.find(acc => acc.Type === 'Margin') || accountsData.accounts[0];
            
            // Get real positions from TradeStation
            const positionsResponse = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/tradestation/accounts/${mainAccount.AccountID}/positions`);
            const positionsData = await positionsResponse.json();
            
            // Get cash balance from account balances API
            try {
              const balancesResponse = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/tradestation/accounts/${mainAccount.AccountID}/balances`);
              const balancesData = await balancesResponse.json();
              
              if (balancesData.status === 'success' && balancesData.balances) {
                // Extract cash balance from TradeStation balances
                const cashAvailable = balancesData.balances.CashBalance || 
                                    balancesData.balances.TotalCash || 
                                    balancesData.balances.AvailableCash || 
                                    0;
                setCashBalance(parseFloat(cashAvailable));
                console.log('✅ Loaded cash balance from TradeStation:', cashAvailable);
              }
            } catch (balanceError) {
              console.warn('⚠️ Could not fetch cash balance:', balanceError.message);
              setCashBalance(0);
            }
            
            if (positionsData.positions) {
              // Transform TradeStation positions to match frontend format
              const transformedPositions = positionsData.positions.map(pos => ({
                id: `ts-${pos.symbol}-${Math.random()}`,
                symbol: pos.symbol,
                quantity: pos.quantity,
                avg_cost: pos.average_price || 0,
                current_price: pos.mark_price || pos.current_price || 0,
                market_value: pos.market_value || Math.abs(pos.quantity * (pos.mark_price || pos.current_price || 0)),
                unrealized_pnl: pos.unrealized_pnl || 0,
                unrealized_pnl_percent: pos.unrealized_pnl_percent || 0,
                portfolio_id: 'tradestation-main',
                position_type: pos.asset_type === 'STOCK' ? 'stock' : 'option',
                metadata: {
                  asset_type: pos.asset_type,
                  source: 'tradestation_direct_api',
                  ...pos
                }
              }));
              
              // Calculate portfolio totals
              const totalValue = transformedPositions.reduce((sum, pos) => sum + pos.market_value, 0);
              const totalPnl = transformedPositions.reduce((sum, pos) => sum + pos.unrealized_pnl, 0);
              
              setPositions(transformedPositions);
              setCurrentPortfolio({
                id: 'tradestation-main',
                name: 'TradeStation Main',
                total_value: totalValue,
                total_pnl: totalPnl,
                positions_count: transformedPositions.length,
                description: `Live TradeStation Account ${mainAccount.AccountID}`
              });
              
              console.log('✅ Loaded REAL TradeStation positions:', {
                count: transformedPositions.length,
                symbols: transformedPositions.map(p => p.symbol),
                totalValue,
                totalPnl
              });
            }
          }
        } catch (error) {
          console.error('Error loading real TradeStation data:', error);
          setError(error.message);
        } finally {
          setLoading(false);
        }
      };
      
      loadRealTradeStationData();
      
    } else if (portfolioId && portfolios.length > 0) {
      // For other portfolios, use Portfolio Management Service
      const portfolio = portfolios.find(p => p.id === portfolioId);
      setCurrentPortfolio(portfolio);
      
      // Use hook positions for non-TradeStation portfolios
      const loadOtherPortfolioData = async () => {
        try {
          await fetchPortfolioPositions(portfolioId);
          await fetchAvailablePortfolios(portfolioId);
          // Positions will be set via hook's internal state
        } catch (error) {
          setError(error.message);
        }
      };
      
      loadOtherPortfolioData();
    }
  }, [portfolioId, portfolios]);

  // Handle right-click context menu
  const handleContextMenu = (event, position) => {
    event.preventDefault();
    
    setContextMenu({
      isVisible: true,
      position: { x: event.clientX, y: event.clientY },
      selectedPosition: position
    });
  };

  // Close context menu
  const closeContextMenu = () => {
    setContextMenu({
      isVisible: false,
      position: { x: 0, y: 0 },
      selectedPosition: null
    });
  };

  // Handle position move
  const handleMovePosition = async (positionId, toPortfolioId, portfolioName) => {
    try {
      const result = await movePosition(positionId, toPortfolioId);
      
      if (result.success) {
        // Show success message
        alert(`Position moved successfully to ${portfolioName}`);
        
        // Refresh positions
        fetchPortfolioPositions(portfolioId);
      } else {
        throw new Error(result.error || 'Failed to move position');
      }
    } catch (error) {
      alert(`Error moving position: ${error.message}`);
    }
  };

  // Default to TradeStation Main if no portfolio found
  const displayPortfolio = currentPortfolio || {
    name: 'TradeStation Main',
    total_value: 0,
    total_pnl: 0,
    positions_count: 0
  };

  const changePercent = displayPortfolio.total_value > 0 
    ? (displayPortfolio.total_pnl / (displayPortfolio.total_value - displayPortfolio.total_pnl)) * 100 
    : 0;

  // Calculate portfolio statistics for cards
  const portfolioStats = React.useMemo(() => {
    if (!positions || positions.length === 0) {
      return {
        stocksCount: 0,
        stocksValue: 0,
        optionsCount: 0,
        optionsValue: 0,
        totalAccountValue: (displayPortfolio?.total_value || 0) + cashBalance,
        cashBalance: cashBalance
      };
    }

    const stocks = positions.filter(p => p.position_type === 'stock');
    const options = positions.filter(p => p.position_type === 'option');
    
    const stocksValue = stocks.reduce((sum, pos) => sum + (pos.market_value || 0), 0);
    const optionsValue = options.reduce((sum, pos) => sum + (pos.market_value || 0), 0);
    
    // Total account value includes positions + cash balance
    const totalAccountValue = (displayPortfolio?.total_value || 0) + cashBalance;

    return {
      stocksCount: stocks.length,
      stocksValue,
      optionsCount: options.length,
      optionsValue,
      totalAccountValue,
      cashBalance: cashBalance
    };
  }, [positions, displayPortfolio?.total_value, cashBalance]);

  const getRatingColor = (rating) => {
    if (rating >= 4) return 'bg-green-500 text-white';
    if (rating >= 3.5) return 'bg-green-400 text-white';
    if (rating >= 3) return 'bg-yellow-500 text-white';
    if (rating >= 2.5) return 'bg-yellow-400 text-white';
    if (rating >= 2) return 'bg-orange-500 text-white';
    return 'bg-red-500 text-white';
  };

  const getChangeColor = (change) => {
    return change >= 0 ? 'text-green-600' : 'text-red-600';
  };

  const formatNumber = (num) => {
    if (num >= 1000000) return (num / 1000000).toFixed(2) + 'M';
    if (num >= 1000) return (num / 1000).toFixed(0) + 'K';
    return num.toString();
  };

  const tabs = [
    { id: 'summary', label: 'Summary' },
    { id: 'health-score', label: 'Health Score' },
    { id: 'ratings', label: 'Ratings' },
    { id: 'holdings', label: 'Holdings' },
    { id: 'dividends', label: 'Dividends' },
    { id: 'add-edit-views', label: '+ Add / Edit Views', hasArrow: true }
  ];

  const newsItems = [
    {
      symbol: 'MCHP',
      title: 'Microchip Technology Incorporated (MCHP) Presents at KeyBanc Technology Leadership Forum Conference Transcript',
      source: 'SA Transcripts',
      date: 'Thu, Aug 14'
    },
    {
      symbol: 'SWKS',
      title: 'Skyworks Solutions, Inc. (SWKS) KeyBanc Technology Leadership Forum Conference (Transcript)',
      source: 'SA Transcripts',
      date: 'Tue, Aug 12'
    }
  ];

  return (
    <div className="min-h-screen bg-slate-900">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-blue-700 px-6 py-4">
        <div className="flex items-center space-x-2">
          <h1 className="text-2xl font-bold text-white flex items-center">
            Portfolio {displayPortfolio.name}
            <ChevronDown className="ml-2" size={20} />
          </h1>
        </div>
        
        <div className="flex items-center mt-2">
          <Eye className="text-white mr-2" size={16} />
          <span className="text-3xl font-bold text-white">
            ${portfolioStats.totalAccountValue.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
          </span>
          <span className="text-sm text-blue-200 ml-2">(Total Account Value)</span>
          <span className={`ml-4 text-lg font-medium ${displayPortfolio.total_pnl >= 0 ? 'text-green-300' : 'text-red-300'}`}>
            {displayPortfolio.total_pnl >= 0 ? '+' : ''}${Math.abs(displayPortfolio.total_pnl).toFixed(2)} ({changePercent >= 0 ? '+' : ''}{changePercent.toFixed(2)}%)
          </span>
        </div>
        
        {/* Action Buttons */}
        <div className="flex items-center mt-4 space-x-3">
          <button
            onClick={() => navigate(`/portfolios/${portfolioId}/charts`)}
            className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            <PieChartIcon size={16} />
            <span>Charts</span>
          </button>
          
          <button
            onClick={() => navigate(`/portfolios/${portfolioId}/rebalancing`)}
            className="flex items-center space-x-2 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
          >
            <Brain size={16} />
            <span>AI Rebalancing</span>
          </button>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="border-b border-slate-700 bg-slate-800">
        <div className="flex space-x-8 px-6">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => {
                if (tab.id === 'add-edit-views') {
                  // Handle Add/Edit Views click - you mentioned you'll show the method
                  navigate(`/portfolios/${portfolioId}/add-edit-views`);
                } else {
                  setActiveTab(tab.id);
                }
              }}
              className={`py-4 px-2 border-b-2 font-medium text-sm flex items-center ${
                activeTab === tab.id
                  ? 'border-blue-400 text-blue-400'
                  : 'border-transparent text-slate-400 hover:text-slate-200 hover:border-slate-600'
              }`}
            >
              {tab.label}
              {tab.hasArrow && <span className="ml-1 text-red-400">→</span>}
            </button>
          ))}
        </div>
      </div>

      {/* Main Content */}
      <div className="p-6 bg-slate-900">
        
        {/* Portfolio Statistics Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
          
          {/* Stocks Positions Card */}
          <div className="bg-slate-800 rounded-lg p-6 border border-slate-600">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-slate-300">Stock Positions</p>
                <p className="text-2xl font-bold text-white">{portfolioStats.stocksCount}</p>
                <p className="text-sm text-slate-400">
                  ${portfolioStats.stocksValue.toLocaleString(undefined, { minimumFractionDigits: 0, maximumFractionDigits: 0 })}
                </p>
              </div>
              <div className="p-3 bg-blue-600 rounded-full">
                <BarChart3 className="h-6 w-6 text-white" />
              </div>
            </div>
          </div>

          {/* Options Positions Card */}
          <div className="bg-slate-800 rounded-lg p-6 border border-slate-600">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-slate-300">Options Positions</p>
                <p className="text-2xl font-bold text-white">{portfolioStats.optionsCount}</p>
                <p className="text-sm text-slate-400">
                  ${portfolioStats.optionsValue.toLocaleString(undefined, { minimumFractionDigits: 0, maximumFractionDigits: 0 })}
                </p>
              </div>
              <div className="p-3 bg-purple-600 rounded-full">
                <Target className="h-6 w-6 text-white" />
              </div>
            </div>
          </div>

          {/* Cash Balance Card - Ultimul din dreapta */}
          <div className="bg-slate-800 rounded-lg p-6 border border-slate-600">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-slate-300">Cash Balance</p>
                <p className="text-2xl font-bold text-white">
                  ${portfolioStats.cashBalance.toLocaleString(undefined, { minimumFractionDigits: 0, maximumFractionDigits: 0 })}
                </p>
                <p className="text-sm text-slate-400">Available Cash</p>
              </div>
              <div className="p-3 bg-green-600 rounded-full">
                <DollarSign className="h-6 w-6 text-white" />
              </div>
            </div>
          </div>

        </div>
        
        {/* Holdings Table */}
        <div className="overflow-x-auto">
          {loading && (
            <div className="flex items-center justify-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
              <span className="ml-2 text-gray-600">Loading positions...</span>
            </div>
          )}
          
          {error && (
            <div className="bg-red-900 border border-red-700 rounded-lg p-4 mb-4">
              <span className="text-red-300">Error: {error}</span>
              <button
                onClick={clearError}
                className="ml-2 text-red-400 hover:text-red-200"
              >
                Dismiss
              </button>
            </div>
          )}
          
          {!loading && positions.length === 0 && !error && (
            <div className="text-center py-8 text-slate-400">
              No positions found in this portfolio.
            </div>
          )}

          {!loading && positions.length > 0 && (
            <table className="w-full text-sm bg-slate-800 rounded-lg">
              <thead>
                <tr className="border-b border-slate-700">
                  <th className="text-left py-3 px-2 font-medium text-slate-300">Symbol</th>
                  <th className="text-right py-3 px-2 font-medium text-slate-300">Quantity</th>
                  <th className="text-right py-3 px-2 font-medium text-slate-300">Avg Cost</th>
                  <th className="text-right py-3 px-2 font-medium text-slate-300">Current Price</th>
                  <th className="text-right py-3 px-2 font-medium text-slate-300">Market Value</th>
                  <th className="text-right py-3 px-2 font-medium text-slate-300">Unrealized P&L</th>
                  <th className="text-right py-3 px-2 font-medium text-slate-300">P&L %</th>
                  <th className="text-center py-3 px-2 font-medium text-slate-300">Type</th>
                </tr>
              </thead>
              <tbody>
                {positions.map((position, index) => {
                  const pnlPercent = position.unrealized_pnl_percent || 0;
                  
                  return (
                    <tr 
                      key={position.id} 
                      className="border-b border-gray-100 hover:bg-gray-50 cursor-context-menu"
                      onContextMenu={(e) => handleContextMenu(e, position)}
                      title="Right-click to move position to another portfolio"
                    >
                      <td className="py-3 px-2">
                        <div>
                          <span className="text-blue-600 font-medium cursor-pointer hover:underline">
                            {position.symbol}
                          </span>
                          {position.position_type === 'option' && (
                            <div className="text-xs text-gray-500">
                              {position.metadata?.option_type} {position.metadata?.strike} {position.metadata?.expiry}
                            </div>
                          )}
                        </div>
                      </td>
                      <td className="text-right py-3 px-2 font-medium">{position.quantity}</td>
                      <td className="text-right py-3 px-2">${position.avg_cost.toFixed(2)}</td>
                      <td className="text-right py-3 px-2 font-medium">${position.current_price.toFixed(2)}</td>
                      <td className="text-right py-3 px-2 font-medium">${position.market_value.toFixed(2)}</td>
                      <td className={`text-right py-3 px-2 font-medium ${getChangeColor(position.unrealized_pnl)}`}>
                        {position.unrealized_pnl >= 0 ? '+' : ''}${position.unrealized_pnl.toFixed(2)}
                      </td>
                      <td className={`text-right py-3 px-2 font-medium ${getChangeColor(pnlPercent)}`}>
                        {pnlPercent >= 0 ? '+' : ''}{pnlPercent.toFixed(2)}%
                      </td>
                      <td className="text-center py-3 px-2">
                        <span className={`px-2 py-1 rounded text-xs font-medium ${
                          position.position_type === 'stock' 
                            ? 'bg-blue-100 text-blue-800' 
                            : 'bg-purple-100 text-purple-800'
                        }`}>
                          {position.position_type.toUpperCase()}
                        </span>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          )}
        </div>

        {/* Warnings */}
        <div className="mt-6 space-y-3">
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-center justify-between">
            <div className="flex items-center">
              <AlertTriangle className="text-red-500 mr-3" size={20} />
              <span className="text-red-700">
                <strong>Warning:</strong> ASGN is at high risk of performing badly. <span className="text-blue-600 underline cursor-pointer">Learn why »</span>
              </span>
            </div>
            <button className="text-red-500 hover:text-red-700">
              <X size={20} />
            </button>
          </div>
          
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-center justify-between">
            <div className="flex items-center">
              <AlertTriangle className="text-red-500 mr-3" size={20} />
              <span className="text-red-700">
                <strong>Warning:</strong> IT is at high risk of performing badly. <span className="text-blue-600 underline cursor-pointer">Learn why »</span>
              </span>
            </div>
            <button className="text-red-500 hover:text-red-700">
              <X size={20} />
            </button>
          </div>
        </div>

        {/* Bottom Tabs */}
        <div className="mt-8 border-b border-gray-200">
          <div className="flex space-x-8">
            {['Latest', 'Analysis', 'News', 'Warnings', 'Transcripts', 'Press Releases'].map((tabName, index) => (
              <button
                key={tabName}
                className={`py-3 px-2 border-b-2 font-medium text-sm ${
                  index === 4 // Transcripts active
                    ? 'border-black text-black'
                    : 'border-transparent text-gray-500 hover:text-gray-700'
                }`}
              >
                {tabName}
              </button>
            ))}
          </div>
        </div>

        {/* News/Transcripts Section */}
        <div className="mt-6 space-y-4">
          {newsItems.map((item, index) => (
            <div key={index} className="flex items-start space-x-4 p-4 hover:bg-gray-50 rounded-lg cursor-pointer">
              <div className="w-10 h-10 bg-gray-100 rounded-lg flex items-center justify-center">
                <FileText className="text-gray-500" size={16} />
              </div>
              <div className="flex-1">
                <h3 className="font-medium text-gray-900 hover:text-blue-600">
                  {item.title}
                </h3>
                <div className="flex items-center mt-1 space-x-2 text-sm text-gray-500">
                  <span className="text-blue-600 font-medium">{item.symbol}</span>
                  <span>•</span>
                  <span>{item.source}</span>
                  <span>•</span>
                  <span>{item.date}</span>
                  <span>•</span>
                  <span>📄</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Context Menu */}
      <ContextMenu
        isVisible={contextMenu.isVisible}
        position={contextMenu.position}
        selectedPosition={contextMenu.selectedPosition}
        availablePortfolios={availablePortfolios}
        onClose={closeContextMenu}
        onMovePosition={handleMovePosition}
      />
    </div>
  );
};

export default IndividualPortfolio;