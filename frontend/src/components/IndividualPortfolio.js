import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import {
  ChevronDown,
  TrendingUp,
  TrendingDown,
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
    fetchPortfolioPositions,
    fetchAvailablePortfolios,
    movePosition,
    clearError
  } = usePortfolioManagement();

  // Current portfolio data
  const [currentPortfolio, setCurrentPortfolio] = useState(null);
  const [positions, setPositions] = useState([]);
  const [cashBalance, setCashBalance] = useState(0);
  const [expandedTickers, setExpandedTickers] = useState(new Set()); // EXACT sidebar pattern
  const [error, setError] = useState(null);

  // Format helpers
  const getChangeColor = (change) => (change >= 0 ? 'text-green-400' : 'text-red-400');

  // Load portfolio and positions data
  useEffect(() => {
    const isTradeStation = portfolioId === 'tradestation-main';

    const setDemoData = () => {
      const testPositions = [
        {
          id: 'aapl-stock',
          symbol: 'AAPL',
          quantity: 100,
          avg_cost: 185.5,
          current_price: 189.25,
          market_value: 18925,
          unrealized_pnl: 375,
          unrealized_pnl_percent: 2.02,
          position_type: 'stock'
        },
        {
          id: 'aapl-call',
          symbol: 'AAPL',
          quantity: 5,
          avg_cost: 8.5,
          current_price: 12.75,
          market_value: 6375,
          unrealized_pnl: 2125,
          unrealized_pnl_percent: 50.0,
          position_type: 'option',
          metadata: { option_type: 'CALL', strike_price: 190, expiration_date: '2024-12-20' }
        },
        {
          id: 'tsla-stock',
          symbol: 'TSLA',
          quantity: 50,
          avg_cost: 235.6,
          current_price: 248.45,
          market_value: 12422.5,
          unrealized_pnl: 642.5,
          unrealized_pnl_percent: 5.45,
          position_type: 'stock'
        }
      ];
      setPositions(testPositions);
      setCashBalance(5000);
      setCurrentPortfolio({
        id: 'tradestation-main',
        name: 'TradeStation Main',
        total_value: testPositions.reduce((s, p) => s + (p.market_value || 0), 0),
        total_pnl: testPositions.reduce((s, p) => s + (p.unrealized_pnl || 0), 0),
        positions_count: testPositions.length
      });
    };

    const loadRealTradeStationData = async () => {
      try {
        setLoading(true);
        // Accounts
        const accountsResp = await Promise.race([
          fetch(`${process.env.REACT_APP_BACKEND_URL}/api/tradestation/accounts`),
          new Promise((_, rej) => setTimeout(() => rej(new Error('Accounts timeout')), 12000))
        ]);
        const accountsData = await accountsResp.json();
        if (accountsData.status !== 'success' || !accountsData.accounts?.length) {
          throw new Error('No TradeStation accounts found');
        }
        const mainAccount =
          accountsData.accounts.find((acc) => acc.Type === 'Margin') || accountsData.accounts[0];

        // Positions
        const positionsResp = await Promise.race([
          fetch(
            `${process.env.REACT_APP_BACKEND_URL}/api/tradestation/accounts/${mainAccount.AccountID}/positions`
          ),
          new Promise((_, rej) => setTimeout(() => rej(new Error('Positions timeout')), 15000))
        ]);
        const positionsData = await positionsResp.json();

        // Balances
        try {
          const balancesResp = await Promise.race([
            fetch(
              `${process.env.REACT_APP_BACKEND_URL}/api/tradestation/accounts/${mainAccount.AccountID}/balances`
            ),
            new Promise((_, rej) => setTimeout(() => rej(new Error('Balances timeout')), 10000))
          ]);
          const balancesData = await balancesResp.json();
          const cashAvailable =
            balancesData?.balances?.Balances?.[0]?.CashBalance ||
            balancesData?.balances?.CashBalance ||
            0;
          setCashBalance(parseFloat(cashAvailable) || 0);
        } catch (e) {
          setCashBalance(0);
        }

        if (positionsData?.positions?.length) {
          const transformed = positionsData.positions.map((pos) => ({
            id: `ts-${pos.symbol}-${Math.random()}`,
            symbol: pos.symbol,
            quantity: pos.quantity,
            avg_cost: pos.average_price || 0,
            current_price: pos.mark_price || pos.current_price || 0,
            market_value:
              pos.market_value || Math.abs((pos.quantity || 0) * (pos.mark_price || pos.current_price || 0)),
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

          const totalValue = transformed.reduce((s, p) => s + (p.market_value || 0), 0);
          const totalPnl = transformed.reduce((s, p) => s + (p.unrealized_pnl || 0), 0);

          setPositions(transformed);
          setCurrentPortfolio({
            id: 'tradestation-main',
            name: 'TradeStation Main',
            total_value: totalValue,
            total_pnl: totalPnl,
            positions_count: transformed.length,
            description: `Live TradeStation Account ${mainAccount.AccountID}`
          });
        } else {
          // Fallback to demo if no positions returned
          setDemoData();
        }

        // Ensure context menu has targets
        await fetchAvailablePortfolios('tradestation-main');
      } catch (e) {
        // Use demo data on any failure to keep UI testable
        setError(e.message);
        setDemoData();
        await fetchAvailablePortfolios('tradestation-main');
      } finally {
        setLoading(false);
      }
    };

    const loadOtherPortfolioData = async () => {
      try {
        setLoading(true);
        const portfolio = portfolios.find((p) => p.id === portfolioId);
        setCurrentPortfolio(portfolio || null);
        await fetchPortfolioPositions(portfolioId);
        await fetchAvailablePortfolios(portfolioId);
      } catch (e) {
        setError(e.message);
      } finally {
        setLoading(false);
      }
    };

    if (isTradeStation) {
      loadRealTradeStationData();
    } else if (portfolioId && portfolios.length > 0) {
      loadOtherPortfolioData();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [portfolioId]);

  // Handle right-click context menu
  const handleContextMenu = (event, position) => {
    event.preventDefault();
    setContextMenu({
      isVisible: true,
      position: { x: event.clientX, y: event.clientY },
      selectedPosition: position
    });
  };

  const closeContextMenu = () => {
    setContextMenu({ isVisible: false, position: { x: 0, y: 0 }, selectedPosition: null });
  };

  const handleMovePosition = async (positionId, toPortfolioId, portfolioName) => {
    try {
      const result = await movePosition(positionId, toPortfolioId);
      if (result.success) {
        alert(`Position moved successfully to ${portfolioName}`);
        await fetchPortfolioPositions(portfolioId);
      } else {
        throw new Error(result.error || 'Failed to move position');
      }
    } catch (err) {
      alert(`Error moving position: ${err.message}`);
    }
  };

  const displayPortfolio = currentPortfolio || {
    id: 'tradestation-main',
    name: 'TradeStation Main',
    total_value: 0,
    total_pnl: 0,
    positions_count: 0
  };

  const changePercent =
    displayPortfolio.total_value > 0
      ? (displayPortfolio.total_pnl / (displayPortfolio.total_value - displayPortfolio.total_pnl)) * 100
      : 0;

  // Group positions by ticker symbol with summaries
  const groupedPositions = React.useMemo(() => {
    if (!positions || positions.length === 0) return {};
    const groups = {};
    positions.forEach((pos) => {
      const s = pos.symbol;
      if (!groups[s]) groups[s] = [];
      groups[s].push(pos);
    });

    Object.keys(groups).forEach((symbol) => {
      const arr = groups[symbol];
      // stock first
      arr.sort((a, b) => {
        if (a.position_type === 'stock' && b.position_type !== 'stock') return -1;
        if (a.position_type !== 'stock' && b.position_type === 'stock') return 1;
        return 0;
      });

      const totalValue = arr.reduce((s, p) => s + (p.market_value || 0), 0);
      const totalPnl = arr.reduce((s, p) => s + (p.unrealized_pnl || 0), 0);
      const totalQty = arr.reduce((s, p) => s + Math.abs(p.quantity || 0), 0);
      const accountPercent = displayPortfolio?.total_value > 0 ? (totalValue / displayPortfolio.total_value) * 100 : 0;
      const stock = arr.find((p) => p.position_type === 'stock');
      const currentPrice = stock ? stock.current_price : arr.reduce((s, p) => s + (p.current_price || 0), 0) / arr.length;

      groups[symbol]._summary = {
        symbol,
        totalValue,
        totalPnL: totalPnl,
        totalQuantity: totalQty,
        accountPercent,
        currentPrice,
        positionCount: arr.length,
        hasStock: arr.some((p) => p.position_type === 'stock'),
        hasOptions: arr.some((p) => p.position_type === 'option')
      };
    });

    return groups;
  }, [positions, displayPortfolio?.total_value]);

  // EXACTLY the sidebar-style toggle (Set state and chevron rotation)
  const toggleTicker = (symbol) => {
    const next = new Set(expandedTickers);
    if (next.has(symbol)) next.delete(symbol);
    else next.add(symbol);
    setExpandedTickers(next);
  };

  // Cards stats
  const portfolioStats = React.useMemo(() => {
    const stocks = positions.filter((p) => p.position_type === 'stock');
    const options = positions.filter((p) => p.position_type === 'option');
    const stocksValue = stocks.reduce((s, p) => s + (p.market_value || 0), 0);
    const optionsValue = options.reduce((s, p) => s + (p.market_value || 0), 0);
    const totalAccountValue = (displayPortfolio?.total_value || 0) + cashBalance;
    return {
      stocksCount: stocks.length,
      stocksValue,
      optionsCount: options.length,
      optionsValue,
      totalAccountValue,
      cashBalance
    };
  }, [positions, displayPortfolio?.total_value, cashBalance]);

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

      {/* Tabs (placeholder) */}
      <div className="border-b border-slate-700 bg-slate-800">
        <div className="flex space-x-8 px-6">
          {[
            { id: 'summary', label: 'Summary' },
            { id: 'health-score', label: 'Health Score' },
            { id: 'ratings', label: 'Ratings' },
            { id: 'holdings', label: 'Holdings' },
            { id: 'dividends', label: 'Dividends' },
            { id: 'add-edit-views', label: '+ Add / Edit Views', hasArrow: true }
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => (tab.id === 'add-edit-views' ? navigate(`/portfolios/${portfolioId}/add-edit-views`) : setActiveTab(tab.id))}
              className={`py-4 px-2 border-b-2 font-medium text-sm flex items-center ${
                activeTab === tab.id ? 'border-blue-400 text-blue-400' : 'border-transparent text-slate-400 hover:text-slate-200 hover:border-slate-600'
              }`}
            >
              {tab.label}
              {tab.hasArrow && <span className="ml-1 text-red-400">→</span>}
            </button>
          ))}
        </div>
      </div>

      {/* Stats Cards */}
      <div className="p-6 bg-slate-900">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
          <div className="bg-slate-800 rounded-lg p-6 border border-slate-600">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-slate-300">Stock Positions</p>
                <p className="text-2xl font-bold text-white">{portfolioStats.stocksCount}</p>
                <p className="text-sm text-slate-400">${portfolioStats.stocksValue.toLocaleString(undefined, { minimumFractionDigits: 0, maximumFractionDigits: 0 })}</p>
              </div>
              <div className="p-3 bg-blue-600 rounded-full">
                <BarChart3 className="h-6 w-6 text-white" />
              </div>
            </div>
          </div>
          <div className="bg-slate-800 rounded-lg p-6 border border-slate-600">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-slate-300">Options Positions</p>
                <p className="text-2xl font-bold text-white">{portfolioStats.optionsCount}</p>
                <p className="text-sm text-slate-400">${portfolioStats.optionsValue.toLocaleString(undefined, { minimumFractionDigits: 0, maximumFractionDigits: 0 })}</p>
              </div>
              <div className="p-3 bg-purple-600 rounded-full">
                <Target className="h-6 w-6 text-white" />
              </div>
            </div>
          </div>
          <div className="bg-slate-800 rounded-lg p-6 border border-slate-600">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-slate-300">Cash Balance</p>
                <p className="text-2xl font-bold text-white">${portfolioStats.cashBalance.toLocaleString(undefined, { minimumFractionDigits: 0, maximumFractionDigits: 0 })}</p>
                <p className="text-sm text-slate-400">Available Cash</p>
              </div>
              <div className="p-3 bg-green-600 rounded-full">
                <DollarSign className="h-6 w-6 text-white" />
              </div>
            </div>
          </div>
        </div>

        {/* Holdings Table - Sidebar-style expandable groups */}
        <div className="overflow-x-auto">
          {loading && (
            <div className="flex items-center justify-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
              <span className="ml-2 text-slate-300">Loading positions...</span>
            </div>
          )}

          {error && (
            <div className="bg-red-900 border border-red-700 rounded-lg p-4 mb-4 text-red-300">
              Error: {error}
              <button onClick={clearError} className="ml-2 text-red-400 hover:text-red-200">Dismiss</button>
            </div>
          )}

          {!loading && positions.length === 0 && !error && (
            <div className="text-center py-8 text-slate-400">No positions found in this portfolio.</div>
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
                  <th className="text-right py-3 px-2 font-medium text-slate-300">% din Cont</th>
                  <th className="text-right py-3 px-2 font-medium text-slate-300">Unrealized P&amp;L</th>
                  <th className="text-right py-3 px-2 font-medium text-slate-300">P&amp;L %</th>
                  <th className="text-center py-3 px-2 font-medium text-slate-300">Type</th>
                </tr>
              </thead>
              <tbody>
                {Object.keys(groupedPositions)
                  .sort()
                  .map((symbol) => {
                    const symbolPositions = groupedPositions[symbol];
                    const summary = symbolPositions._summary;
                    const isExpanded = expandedTickers.has(symbol);

                    return (
                      <React.Fragment key={symbol}>
                        {/* Group header row - EXACT sidebar behavior */}
                        <tr
                          className="border-b border-slate-600 bg-slate-800 hover:bg-slate-700 cursor-pointer"
                          onClick={() => toggleTicker(symbol)}
                          title={`Click to ${isExpanded ? 'collapse' : 'expand'} ${symbol} positions`}
                        >
                          <td className="py-4 px-2">
                            <div className="flex items-center">
                              <ChevronDown className={`w-4 h-4 text-slate-400 mr-2 transition-transform duration-200 ${isExpanded ? 'rotate-180' : 'rotate-0'}`} />
                              <span className="text-blue-300 font-bold text-lg">{symbol}</span>
                              <div className="ml-3 flex gap-1">
                                {summary.hasStock && (
                                  <span className="px-1 py-0.5 rounded text-xs bg-blue-600 text-white">S</span>
                                )}
                                {summary.hasOptions && (
                                  <span className="px-1 py-0.5 rounded text-xs bg-purple-600 text-white">O</span>
                                )}
                              </div>
                            </div>
                          </td>
                          <td className="text-right py-4 px-2 font-bold text-slate-200">{summary.totalQuantity.toLocaleString()}</td>
                          <td className="text-right py-4 px-2 text-slate-400">-</td>
                          <td className="text-right py-4 px-2 font-medium text-slate-200">${summary.currentPrice.toFixed(2)}</td>
                          <td className="text-right py-4 px-2 font-bold text-white">${summary.totalValue.toFixed(2)}</td>
                          <td className="text-right py-4 px-2 font-bold text-blue-300">{summary.accountPercent.toFixed(2)}%</td>
                          <td className={`text-right py-4 px-2 font-bold ${getChangeColor(summary.totalPnL)}`}>
                            {summary.totalPnL >= 0 ? '+' : ''}${summary.totalPnL.toFixed(2)}
                          </td>
                          <td className="text-right py-4 px-2 text-slate-400">-</td>
                          <td className="text-center py-4 px-2">
                            <span className="px-2 py-1 rounded text-xs font-medium bg-slate-600 text-white">
                              {summary.positionCount} POS
                            </span>
                          </td>
                        </tr>

                        {/* Expanded rows */}
                        {isExpanded && (
                          <tr>
                            <td colSpan="9" className="p-0">
                              <div className="bg-slate-900 border-l-4 border-blue-400">
                                <table className="w-full">
                                  <tbody>
                                    {symbolPositions.map((position) => {
                                      const pnlPercent = position.unrealized_pnl_percent || 0;
                                      const accountPercent =
                                        displayPortfolio?.total_value > 0
                                          ? (position.market_value / displayPortfolio.total_value) * 100
                                          : 0;
                                      return (
                                        <tr
                                          key={position.id}
                                          className="border-b border-slate-700 hover:bg-slate-700 cursor-context-menu"
                                          onContextMenu={(e) => handleContextMenu(e, position)}
                                          title="Right-click to move position to another portfolio"
                                        >
                                          <td className="py-3 px-6">
                                            <div className="flex items-center">
                                              <span className="text-slate-400 text-sm mr-2">├──</span>
                                              <span className="text-slate-300 font-medium">
                                                {position.position_type === 'stock' ? '📈 Stock' : '⚡ Option'}
                                              </span>
                                              {position.position_type === 'option' && (
                                                <div className="text-xs text-slate-400 ml-2">
                                                  {position.metadata?.option_type} ${position.metadata?.strike_price} {position.metadata?.expiration_date}
                                                </div>
                                              )}
                                            </div>
                                          </td>
                                          <td className="text-right py-3 px-2 text-slate-200">{position.quantity}</td>
                                          <td className="text-right py-3 px-2 text-slate-200">${position.avg_cost.toFixed(2)}</td>
                                          <td className="text-right py-3 px-2 text-slate-200">${position.current_price.toFixed(2)}</td>
                                          <td className="text-right py-3 px-2 text-slate-200">${position.market_value.toFixed(2)}</td>
                                          <td className="text-right py-3 px-2 text-blue-400">{accountPercent.toFixed(2)}%</td>
                                          <td className={`text-right py-3 px-2 ${getChangeColor(position.unrealized_pnl)}`}>
                                            {position.unrealized_pnl >= 0 ? '+' : ''}${position.unrealized_pnl.toFixed(2)}
                                          </td>
                                          <td className={`text-right py-3 px-2 ${getChangeColor(pnlPercent)}`}>
                                            {pnlPercent >= 0 ? '+' : ''}{pnlPercent.toFixed(2)}%
                                          </td>
                                          <td className="text-center py-3 px-2">
                                            <span className={`px-2 py-1 rounded text-xs font-medium ${
                                              position.position_type === 'stock' ? 'bg-blue-600 text-white' : 'bg-purple-600 text-white'
                                            }`}>
                                              {position.position_type.toUpperCase()}
                                            </span>
                                          </td>
                                        </tr>
                                      );
                                    })}
                                  </tbody>
                                </table>
                              </div>
                            </td>
                          </tr>
                        )}
                      </React.Fragment>
                    );
                  })}

                {/* Total Row */}
                {positions.length > 0 && (
                  <tr className="border-t-2 border-slate-600 bg-slate-700">
                    <td className="py-3 px-2 font-bold text-slate-200">TOTAL PORTFOLIO</td>
                    <td className="text-right py-3 px-2 font-bold text-slate-200">
                      {positions.reduce((sum, pos) => sum + Math.abs(pos.quantity || 0), 0).toLocaleString()}
                    </td>
                    <td className="text-right py-3 px-2 text-slate-400">-</td>
                    <td className="text-right py-3 px-2 text-slate-400">-</td>
                    <td className="text-right py-3 px-2 font-bold text-white">
                      ${positions
                        .reduce((sum, pos) => sum + (pos.market_value || 0), 0)
                        .toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                    </td>
                    <td className="text-right py-3 px-2 font-bold text-blue-300">100.00%</td>
                    <td className={`text-right py-3 px-2 font-bold ${getChangeColor(positions.reduce((s, p) => s + (p.unrealized_pnl || 0), 0))}`}>
                      {positions.reduce((s, p) => s + (p.unrealized_pnl || 0), 0) >= 0 ? '+' : ''}
                      {positions.reduce((s, p) => s + (p.unrealized_pnl || 0), 0).toFixed(2)}
                    </td>
                    <td className={`text-right py-3 px-2 font-bold ${getChangeColor(displayPortfolio.total_pnl || 0)}`}>
                      {displayPortfolio?.total_value > 0
                        ? `${(
                            ((displayPortfolio.total_pnl || 0) /
                              (displayPortfolio.total_value - (displayPortfolio.total_pnl || 0))) *
                            100
                          ).toFixed(2)}%`
                        : '0.00%'}
                    </td>
                    <td className="text-center py-3 px-2">
                      <span className="px-2 py-1 rounded text-xs font-medium bg-slate-600 text-white">
                        {Object.keys(groupedPositions).length} SYMBOLS
                      </span>
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          )}
        </div>

        {/* Warnings (kept) */}
        <div className="mt-6 space-y-3">
          <div className="bg-red-900 border border-red-700 rounded-lg p-4 flex items-center justify-between">
            <div className="flex items-center">
              <AlertTriangle className="text-red-400 mr-3" size={20} />
              <span className="text-red-300">
                <strong>Warning:</strong> ASGN is at high risk of performing badly.{' '}
                <span className="text-blue-400 underline cursor-pointer">Learn why »</span>
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
                <strong>Warning:</strong> IT is at high risk of performing badly.{' '}
                <span className="text-blue-400 underline cursor-pointer">Learn why »</span>
              </span>
            </div>
            <button className="text-red-400 hover:text-red-300">
              <X size={20} />
            </button>
          </div>
        </div>

        {/* News/Transcripts Section */}
        <div className="mt-6 space-y-4">
          {[
            {
              symbol: 'MCHP',
              title:
                'Microchip Technology Incorporated (MCHP) Presents at KeyBanc Technology Leadership Forum Conference Transcript',
              source: 'SA Transcripts',
              date: 'Thu, Aug 14'
            },
            {
              symbol: 'SWKS',
              title:
                'Skyworks Solutions, Inc. (SWKS) KeyBanc Technology Leadership Forum Conference (Transcript)',
              source: 'SA Transcripts',
              date: 'Tue, Aug 12'
            }
          ].map((item, index) => (
            <div key={index} className="flex items-start space-x-4 p-4 hover:bg-gray-50 rounded-lg cursor-pointer">
              <div className="w-10 h-10 bg-gray-100 rounded-lg flex items-center justify-center">
                <FileText className="text-gray-500" size={16} />
              </div>
              <div className="flex-1">
                <h3 className="font-medium text-gray-900 hover:text-blue-600">{item.title}</h3>
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