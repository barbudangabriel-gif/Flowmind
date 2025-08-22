import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { 
  ChevronDown, 
  ChevronRight,
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
  const [expandedTickers, setExpandedTickers] = useState(new Set()); // Track expanded tickers
  const [error, setError] = useState(null);

  // Load portfolio and positions data directly from TradeStation API
  useEffect(() => {
    if (portfolioId === 'tradestation-main') {
      // For TradeStation Main, load REAL data directly from TradeStation API
      const loadRealTradeStationData = async () => {
        try {
          setLoading(true);
          console.log('🔄 Starting TradeStation data load...');
          
          // Get accounts first
          const accountsResponse = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/tradestation/accounts`);
          const accountsData = await accountsResponse.json();
          console.log('📊 Accounts response:', accountsData.status, accountsData.accounts?.length);
          
          if (accountsData.status === 'success' && accountsData.accounts.length > 0) {
            const mainAccount = accountsData.accounts.find(acc => acc.Type === 'Margin') || accountsData.accounts[0];
            console.log('💼 Using account:', mainAccount.AccountID);
            
            // Get positions - add timeout
            const positionsResponse = await Promise.race([
              fetch(`${process.env.REACT_APP_BACKEND_URL}/api/tradestation/accounts/${mainAccount.AccountID}/positions`),
              new Promise((_, reject) => setTimeout(() => reject(new Error('Positions timeout')), 15000))
            ]);
            const positionsData = await positionsResponse.json();
            console.log('📈 Positions response:', positionsData.status, positionsData.positions?.length);
            
            // Get cash balance - add timeout
            try {
              const balancesResponse = await Promise.race([
                fetch(`${process.env.REACT_APP_BACKEND_URL}/api/tradestation/accounts/${mainAccount.AccountID}/balances`),
                new Promise((_, reject) => setTimeout(() => reject(new Error('Balances timeout')), 10000))
              ]);
              const balancesData = await balancesResponse.json();
              
              if (balancesData.status === 'success' && balancesData.balances) {
                const cashAvailable = balancesData.balances.Balances?.[0]?.CashBalance || 
                                    balancesData.balances.CashBalance || 
                                    0;
                setCashBalance(parseFloat(cashAvailable));
                console.log('💰 Cash balance loaded:', cashAvailable);
              }
            } catch (balanceError) {
              console.warn('⚠️ Balance error:', balanceError.message);
              setCashBalance(0);
            }
            
            if (positionsData.positions && positionsData.positions.length > 0) {
              // Transform positions
              const transformedPositions = positionsData.positions.map(pos => ({
                id: `ts-${pos.symbol}-${Math.random()}`,
                symbol: pos.symbol,
                quantity: pos.quantity,
                avg_cost: pos.average_price || 0,
                current_price: pos.current_price || 0,
                market_value: pos.market_value || 0,
                unrealized_pnl: pos.unrealized_pnl || 0,
                unrealized_pnl_percent: pos.unrealized_pnl_percent || 0,
                portfolio_id: 'tradestation-main',
                position_type: pos.asset_type === 'STOCK' ? 'stock' : 'option',
                metadata: {
                  asset_type: pos.asset_type,
                  option_type: pos.option_type,
                  strike_price: pos.strike_price,
                  expiration_date: pos.expiration_date,
                  source: 'tradestation_direct_api'
                }
              }));
              
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
              
              console.log('✅ Loaded positions:', transformedPositions.length, 'Total value:', totalValue);
            } else {
              console.log('⚠️ No positions found');
              setPositions([]);
              setCurrentPortfolio({
                id: 'tradestation-main',
                name: 'TradeStation Main',
                total_value: 0,
                total_pnl: 0,
                positions_count: 0,
                description: 'No positions in TradeStation account'
              });
            }
          } else {
            throw new Error('No TradeStation accounts found');
          }
        } catch (error) {
          console.error('❌ TradeStation error:', error);
          setError(error.message);
          setPositions([]);
        } finally {
          console.log('🏁 Loading complete, setting loading to false');
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
  }, [portfolioId]); // Only re-run when portfolioId changes

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

  // Group positions by ticker symbol
  const groupedPositions = React.useMemo(() => {
    if (!positions || positions.length === 0) return {};
    
    const groups = {};
    positions.forEach(position => {
      const symbol = position.symbol;
      if (!groups[symbol]) {
        groups[symbol] = [];
      }
      groups[symbol].push(position);
    });
    
    // Sort positions within each group: stock first, then options
    Object.keys(groups).forEach(symbol => {
      groups[symbol].sort((a, b) => {
        // Stock always comes first
        if (a.position_type === 'stock' && b.position_type !== 'stock') return -1;
        if (a.position_type !== 'stock' && b.position_type === 'stock') return 1;
        return 0;
      });
      
      // Calculate aggregate data for the ticker
      const symbolPositions = groups[symbol];
      const totalValue = symbolPositions.reduce((sum, pos) => sum + pos.market_value, 0);
      const totalPnL = symbolPositions.reduce((sum, pos) => sum + pos.unrealized_pnl, 0);
      const totalQuantity = symbolPositions.reduce((sum, pos) => sum + Math.abs(pos.quantity), 0);
      const accountPercent = displayPortfolio?.total_value > 0 ? (totalValue / displayPortfolio.total_value) * 100 : 0;
      const pnlPercent = totalValue > 0 ? (totalPnL / (totalValue - totalPnL)) * 100 : 0;
      
      // Get current price from the first stock position, or average if no stock
      const stockPosition = symbolPositions.find(p => p.position_type === 'stock');
      const currentPrice = stockPosition ? stockPosition.current_price : 
        symbolPositions.reduce((sum, pos) => sum + pos.current_price, 0) / symbolPositions.length;
      
      groups[symbol]._summary = {
        symbol,
        totalValue,
        totalPnL,
        totalQuantity,
        accountPercent,
        pnlPercent,
        currentPrice,
        positionCount: symbolPositions.length,
        hasStock: symbolPositions.some(p => p.position_type === 'stock'),
        hasOptions: symbolPositions.some(p => p.position_type === 'option')
      };
    });
    
    return groups;
  }, [positions, displayPortfolio?.total_value]);

  // Toggle ticker expansion
  const toggleTicker = (symbol) => {
    console.log('🔄 Toggling ticker:', symbol, 'Currently expanded:', expandedTickers.has(symbol));
    const newExpanded = new Set(expandedTickers);
    if (newExpanded.has(symbol)) {
      newExpanded.delete(symbol);
      console.log('➖ Collapsed:', symbol);
    } else {
      newExpanded.add(symbol);
      console.log('➕ Expanded:', symbol);
    }
    setExpandedTickers(newExpanded);
    console.log('📊 New expanded tickers:', Array.from(newExpanded));
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
            <>
              {Object.keys(groupedPositions).sort().map((symbol) => {
                const symbolPositions = groupedPositions[symbol];
                const summary = symbolPositions._summary;
                const isExpanded = expandedTickers.has(symbol);

                return (
                  <div key={symbol} className="mb-4">
                    {/* Ticker Header - EXACT ca în sidebar */}
                    <div className="flex items-center justify-between mb-3 px-3">
                      <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                        <button
                          onClick={() => toggleTicker(symbol)}
                          className="flex items-center gap-2 hover:text-slate-200 transition-colors"
                        >
                          <span className="text-blue-300 font-bold text-lg">{symbol}</span>
                          <div className="ml-3 flex gap-1">
                            {summary.hasStock && (
                              <span className="px-1 py-0.5 rounded text-xs bg-blue-600 text-white">S</span>
                            )}
                            {summary.hasOptions && (
                              <span className="px-1 py-0.5 rounded text-xs bg-purple-600 text-white">O</span>
                            )}
                          </div>
                          <ChevronDown className={`w-3 h-3 transition-transform duration-200 ${isExpanded ? 'rotate-180' : ''}`} />
                        </button>
                      </h3>
                    </div>

                    {/* Show positions only if expanded - EXACT ca în sidebar */}
                    {isExpanded && (
                      <div className="space-y-1">
                        {symbolPositions.map((position, index) => {
                          const pnlPercent = position.unrealized_pnl_percent || 0;
                          const accountPercent = displayPortfolio?.total_value > 0 
                            ? (position.market_value / displayPortfolio.total_value) * 100 
                            : 0;
                          
                          return (
                            <div key={position.id} className="relative group">
                              <button
                                onContextMenu={(e) => handleContextMenu(e, position)}
                                className="w-full group flex items-center space-x-3 px-3 py-3 rounded-xl transition-all duration-200 relative text-slate-300 hover:text-white hover:bg-slate-700/50 hover:transform hover:scale-102"
                              >
                                {/* Icon with background */}
                                <div className="flex items-center justify-center w-8 h-8 rounded-lg transition-all duration-200 bg-slate-600/30 group-hover:bg-slate-600/50">
                                  <span className="text-xs text-white">
                                    {position.position_type === 'stock' ? 'S' : 'O'}
                                  </span>
                                </div>
                                
                                {/* Position details */}
                                <div className="flex-1 text-left">
                                  <div className="text-slate-300 font-medium">
                                    {position.position_type === 'stock' ? 'Stock' : 'Option'}
                                  </div>
                                  {position.position_type === 'option' && (
                                    <div className="text-xs text-slate-400">
                                      {position.metadata?.option_type} ${position.metadata?.strike_price} {position.metadata?.expiration_date}
                                    </div>
                                  )}
                                </div>

                                {/* Position values */}
                                <div className="flex gap-4 text-sm text-slate-200">
                                  <span>{position.quantity}</span>
                                  <span>${position.avg_cost.toFixed(2)}</span>
                                  <span>${position.current_price.toFixed(2)}</span>
                                  <span>${position.market_value.toFixed(2)}</span>
                                  <span className="text-blue-400">{accountPercent.toFixed(2)}%</span>
                                  <span className={getChangeColor(position.unrealized_pnl)}>
                                    {position.unrealized_pnl >= 0 ? '+' : ''}${position.unrealized_pnl.toFixed(2)}
                                  </span>
                                  <span className={getChangeColor(pnlPercent)}>
                                    {pnlPercent >= 0 ? '+' : ''}{pnlPercent.toFixed(2)}%
                                  </span>
                                </div>
                              </button>
                            </div>
                          );
                        })}
                      </div>
                    )}
                  </div>
                );
              })}
            </>
          )}
        </div>

        {/* Warnings */}
        <div className="mt-6 space-y-3">
          <div className="bg-red-900 border border-red-700 rounded-lg p-4 flex items-center justify-between">
            <div className="flex items-center">
              <AlertTriangle className="text-red-400 mr-3" size={20} />
              <span className="text-red-300">
                <strong>Warning:</strong> ASGN is at high risk of performing badly. <span className="text-blue-400 underline cursor-pointer">Learn why »</span>
              </span>
            </div>
            <button className="text-red-400 hover:text-red-300">
              <X size={20} />
            </button>
          </div>
          
          <div className="bg-red-900 border border-red-700 rounded-lg p-4 flex items-center justify-between">
            <div className="flex items-center">
              <AlertTriangle className="text-red-400 mr-3" size={20} />
              <span className="text-red-300">
                <strong>Warning:</strong> IT is at high risk of performing badly. <span className="text-blue-400 underline cursor-pointer">Learn why »</span>
              </span>
            </div>
            <button className="text-red-400 hover:text-red-300">
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