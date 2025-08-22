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
  AlertCircle,
  ChevronDown
} from 'lucide-react';

const TradeStationMainPortfolio = () => {
  const navigate = useNavigate();
  const [portfolioData, setPortfolioData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(new Date());

  const [positionsNormalized, setPositionsNormalized] = useState([]);
  const [expandedTickers, setExpandedTickers] = useState({}); // expand/collapse per symbol

  const backendUrl = process.env.REACT_APP_BACKEND_URL;

  const normalizePositions = (rawPositions) => {
    return (rawPositions || []).map((pos) => {
      const rawSymbol = (pos.symbol || '').trim();
      const asset = (pos.asset_type || '').toUpperCase();
      let isStock = asset.includes('EQ') || asset.includes('STOCK');
      let isOption = asset.includes('OP') || asset.includes('OPTION');
      // If both flags true (e.g., STOCKOPTION), treat as option
      if (isOption) isStock = false;

      let baseSymbol = (rawSymbol.split(' ')[0] || rawSymbol).split('_')[0];
      const symbolTail = rawSymbol.replace(baseSymbol, '').replace(/^[ _]/, '');
      const pattern = /(\d{6})([CP])([0-9]+(?:\.[0-9]+)?)/i;
      let optionMatch = null;
      if (!isOption && symbolTail) {
        optionMatch = symbolTail.match(pattern);
        if (optionMatch) { isOption = true; isStock = false; }
      }

      let option_type = pos.option_type;
      let strike_price = pos.strike_price;
      let expiration_date = pos.expiration_date;
      if (isOption && (!option_type || !strike_price || !expiration_date)) {
        try {
          if (!optionMatch) {
            const parts = rawSymbol.split(' ');
            if (parts.length > 1) optionMatch = parts[1].match(pattern);
          }
          if (optionMatch) {
            const [, yymmdd, cp, strikeStr] = optionMatch;
            const yy = parseInt(yymmdd.slice(0, 2), 10);
            const mm = yymmdd.slice(2, 4);
            const dd = yymmdd.slice(4, 6);
            const fullYear = yy >= 70 ? 1900 + yy : 2000 + yy;
            expiration_date = `${fullYear}-${mm}-${dd}`;
            option_type = cp.toUpperCase() === 'P' ? 'PUT' : 'CALL';
            strike_price = parseFloat(strikeStr);
          }
        } catch {}
      }

      const position_type = isStock ? 'stock' : (isOption ? 'option' : 'stock');
      const symbolField = position_type === 'option' ? baseSymbol : rawSymbol;
      const price = pos.mark_price || pos.current_price || pos.last_price || pos.market_price || pos.price || 0;
      const mv = pos.market_value || Math.abs((pos.quantity || 0) * price);

      return {
        id: `ts-${rawSymbol}-${Math.random()}`,
        symbol: symbolField,
        quantity: pos.quantity || 0,
        avg_cost: pos.average_price || 0,
        current_price: price,
        market_value: mv,
        unrealized_pnl: pos.unrealized_pnl || 0,
        unrealized_pnl_percent: pos.unrealized_pnl_percent || 0,
        portfolio_id: 'tradestation-main',
        position_type,
        metadata: {
          asset_type: pos.asset_type,
          option_type,
          strike_price,
          expiration_date,
          contract_symbol: rawSymbol,
          source: 'tradestation_direct_api'
        }
      };
    });
  };

  // Fetch real TradeStation data directly from TradeStation API (not Portfolio Management Service)
  const fetchTradeStationData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Get accounts first
      const accountsResponse = await fetch(`${backendUrl}/api/tradestation/accounts`);
      if (!accountsResponse.ok) throw new Error(`Failed to fetch accounts: ${accountsResponse.status}`);
      const accountsData = await accountsResponse.json();
      
      // Find the margin account (usually the main trading account)
      const accounts = accountsData.accounts || accountsData;
      let mainAccount;
      if (Array.isArray(accounts)) {
        mainAccount = accounts.find(acc => acc.Type === 'Margin') || accounts[0];
      } else if (accounts && typeof accounts === 'object') {
        mainAccount = accounts;
      }
      if (!mainAccount || !mainAccount.AccountID) {
        throw new Error(`No valid TradeStation account found. Accounts structure: ${JSON.stringify(accounts)}`);
      }

      // Get positions for the main account
      const positionsResponse = await fetch(`${backendUrl}/api/tradestation/accounts/${mainAccount.AccountID}/positions`);
      if (!positionsResponse.ok) throw new Error(`Failed to fetch positions: ${positionsResponse.status}`);
      const positionsData = await positionsResponse.json();

      // Parse positions array from payload
      let positions;
      if (positionsData.positions && Array.isArray(positionsData.positions)) positions = positionsData.positions;
      else if (positionsData.data && Array.isArray(positionsData.data)) positions = positionsData.data;
      else if (Array.isArray(positionsData)) positions = positionsData;
      else positions = [];

      // Calculate portfolio totals
      let totalMarketValue = 0;
      let totalUnrealizedPnL = 0;
      positions.forEach(position => {
        const currentPrice = position.mark_price || position.current_price || position.last_price || position.market_price || position.price || 0;
        const marketValue = Math.abs((position.quantity || 0) * currentPrice);
        const unrealizedPnL = position.unrealized_pnl || 0;
        totalMarketValue += marketValue;
        totalUnrealizedPnL += unrealizedPnL;
      });
      const costBasis = totalMarketValue - totalUnrealizedPnL;
      const percentChange = costBasis !== 0 ? (totalUnrealizedPnL / costBasis) * 100 : 0;

      const stocks = positions.filter(p => (p.asset_type || '').toUpperCase().includes('STOCK') || (p.asset_type || '').toUpperCase().includes('EQ'));
      const options = positions.filter(p => (p.asset_type || '').toUpperCase().includes('OPTION') || (p.asset_type || '').toUpperCase().includes('OP'));

      // Set top-level portfolio summary
      setPortfolioData({
        account: mainAccount,
        totalMarketValue,
        totalUnrealizedPnL,
        percentChange,
        totalPositions: positions.length,
        stocks: stocks.length,
        options: options.length,
        positions
      });

      // Build normalized positions for detailed table
      const normalized = normalizePositions(positions);
      setPositionsNormalized(normalized);

      setLastUpdated(new Date());
      setError(null);
    } catch (err) {
      setError(err.message);
      console.error('Error fetching TradeStation data:', err);
      setPositionsNormalized([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTradeStationData();
  }, []);

  const formatCurrency = (value) => new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', minimumFractionDigits: 0, maximumFractionDigits: 0 }).format(value);
  const getChangeColor = (value) => (value >= 0 ? 'text-green-500' : 'text-red-500');
  const getChangeIcon = (value) => (value >= 0 ? TrendingUp : TrendingDown);

  // Group positions for detailed table
  const groupedPositions = React.useMemo(() => {
    if (!positionsNormalized || positionsNormalized.length === 0) return {};

    const getBaseSymbol = (p) => {
      if (p.metadata?.underlying_symbol) return (p.metadata.underlying_symbol || '').toUpperCase();
      const raw = (p.symbol || '').trim();
      const first = (raw.split(' ')[0] || raw).split('_')[0];
      return (first || raw).toUpperCase();
    };

    const groups = {};
    positionsNormalized.forEach((pos) => {
      const key = pos.position_type === 'option' ? getBaseSymbol(pos) : (pos.symbol || '').toUpperCase();
      if (!groups[key]) groups[key] = [];
      groups[key].push(pos);
    });

    Object.keys(groups).forEach((symbol) => {
      const arr = groups[symbol];
      arr.sort((a, b) => (a.position_type === 'stock' && b.position_type !== 'stock' ? -1 : a.position_type !== 'stock' && b.position_type === 'stock' ? 1 : 0));
      const totalValue = arr.reduce((s, p) => s + (p.market_value || 0), 0);
      const totalPnl = arr.reduce((s, p) => s + (p.unrealized_pnl || 0), 0);
      const totalQty = arr.reduce((s, p) => s + Math.abs(p.quantity || 0), 0);
      const accountPercent = (portfolioData?.totalMarketValue || 0) > 0 ? (totalValue / (portfolioData?.totalMarketValue || 0)) * 100 : 0;
      const stock = arr.find((p) => p.position_type === 'stock');
      const currentPrice = stock ? stock.current_price : arr.reduce((s, p) => s + (p.current_price || 0), 0) / arr.length;
      groups[symbol]._summary = { symbol, totalValue, totalPnL: totalPnl, totalQuantity: totalQty, accountPercent, currentPrice, positionCount: arr.length, hasStock: arr.some((p) => p.position_type === 'stock'), hasOptions: arr.some((p) => p.position_type === 'option') };
    });

    return groups;
  }, [positionsNormalized, portfolioData?.totalMarketValue]);

  const toggleTicker = (symbol) => {
    setExpandedTickers((prev) => ({ ...prev, [symbol]: !prev[symbol] }));
  };
  const expandAll = () => {
    const keys = Object.keys(groupedPositions);
    const next = keys.reduce((acc, s) => ({ ...acc, [s]: true }), {});
    setExpandedTickers(next);
  };
  const collapseAll = () => setExpandedTickers({});

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

  if (error && !portfolioData) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 flex items-center justify-center">
        <div className="text-center max-w-md">
          <AlertCircle className="mx-auto h-16 w-16 text-red-500 mb-4" />
          <h2 className="text-xl font-bold text-white mb-2">Error Loading Portfolio</h2>
          <p className="text-gray-400 mb-6">{error}</p>
          <button onClick={fetchTradeStationData} className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors">Retry</button>
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
              <p className="text-blue-100 mt-2">Account: {portfolioData?.account?.AccountID} • Live Trading Account</p>
            </div>
            <button onClick={fetchTradeStationData} className="bg-white/20 text-white px-4 py-2 rounded-lg hover:bg-white/30 transition-colors flex items-center space-x-2" disabled={loading}>
              <RefreshCw size={16} className={loading ? 'animate-spin' : ''} />
              <span>Refresh</span>
            </button>
          </div>

          {/* Portfolio Value Display */}
          <div className="mt-6">
            <div className="flex items-center space-x-2">
              <Eye className="text-white" size={20} />
              <span className="text-4xl font-bold text-white">{formatCurrency(portfolioData?.totalMarketValue || 0)}</span>
            </div>
            <div className={`flex items-center mt-2 space-x-2 ${getChangeColor(portfolioData?.totalUnrealizedPnL)}`}>
              <ChangeIcon size={24} />
              <span className="text-2xl font-semibold">{portfolioData?.totalUnrealizedPnL >= 0 ? '+' : ''}{formatCurrency(portfolioData?.totalUnrealizedPnL || 0)}</span>
              <span className="text-lg">({portfolioData?.percentChange >= 0 ? '+' : ''}{(portfolioData?.percentChange || 0).toFixed(2)}%)</span>
            </div>
            <p className="text-blue-100 text-sm mt-1">Last updated: {lastUpdated.toLocaleString()}</p>
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
                <p className="text-3xl font-bold text-white">{(positionsNormalized.filter((p) => p.position_type === 'stock')).length}</p>
              </div>
              <BarChart3 className="text-green-400" size={32} />
            </div>
          </div>
          <div className="bg-gray-800 p-6 rounded-xl shadow-lg border border-gray-700">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-sm">Options Positions</p>
                <p className="text-3xl font-bold text-white">{(positionsNormalized.filter((p) => p.position_type === 'option')).length}</p>
              </div>
              <PieChartIcon className="text-purple-400" size={32} />
            </div>
          </div>
          <div className="bg-gray-800 p-6 rounded-xl shadow-lg border border-gray-700">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-sm">Portfolio Value</p>
                <p className="text-2xl font-bold text-white">{formatCurrency(portfolioData?.totalMarketValue || 0)}</p>
              </div>
              <DollarSign className="text-yellow-400" size={32} />
            </div>
          </div>
        </div>

        {/* Detailed Holdings - inline, LIVE only */}
        <div className="overflow-x-auto">
          <div className="flex items-center justify-between mb-3">
            {loading ? (
              <div className="flex items-center py-2">
                <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
                <span className="ml-2 text-gray-300">Loading positions...</span>
              </div>
            ) : (<div />)}
            {positionsNormalized.length > 0 && (
              <div className="flex gap-2">
                <button onClick={expandAll} className="px-3 py-1 bg-gray-700 text-gray-200 rounded hover:bg-gray-600">Expand All</button>
                <button onClick={collapseAll} className="px-3 py-1 bg-gray-700 text-gray-200 rounded hover:bg-gray-600">Collapse All</button>
              </div>
            )}
          </div>

          {error && (
            <div className="bg-red-900 border border-red-700 rounded-lg p-4 mb-4 text-red-300">
              Error: {error}
            </div>
          )}

          {positionsNormalized.length === 0 && !error && (
            <div className="text-center py-8 text-gray-400">No positions found.</div>
          )}

          {positionsNormalized.length > 0 && (
            <table className="w-full text-sm bg-gray-800 rounded-lg">
              <thead>
                <tr className="border-b border-gray-700">
                  <th className="text-left py-3 px-2 font-medium text-gray-300">Symbol</th>
                  <th className="text-right py-3 px-2 font-medium text-gray-300">Quantity</th>
                  <th className="text-right py-3 px-2 font-medium text-gray-300">Avg Cost</th>
                  <th className="text-right py-3 px-2 font-medium text-gray-300">Current Price</th>
                  <th className="text-right py-3 px-2 font-medium text-gray-300">Market Value</th>
                  <th className="text-right py-3 px-2 font-medium text-gray-300">% din Cont</th>
                  <th className="text-right py-3 px-2 font-medium text-gray-300">Unrealized P&amp;L</th>
                  <th className="text-right py-3 px-2 font-medium text-gray-300">P&amp;L %</th>
                  <th className="text-center py-3 px-2 font-medium text-gray-300">Type</th>
                </tr>
              </thead>
              <tbody>
                {Object.keys(groupedPositions).sort().map((symbol) => {
                  const arr = groupedPositions[symbol];
                  const summary = arr._summary;
                  const isExpanded = !!expandedTickers[symbol];
                  return (
                    <React.Fragment key={symbol}>
                      {/* Group header - click entire row to toggle */}
                      <tr
                        className="border-b border-gray-600 bg-gray-800 hover:bg-gray-700 cursor-pointer"
                        onClick={() => toggleTicker(symbol)}
                        title={`Click to ${isExpanded ? 'collapse' : 'expand'} ${symbol} positions`}
                      >
                        <td className="py-4 px-2">
                          <div className="flex items-center">
                            <ChevronDown className={`w-4 h-4 text-gray-400 mr-2 transform transition-transform duration-200 ${isExpanded ? 'rotate-180' : 'rotate-0'}`} />
                            <span className="text-blue-300 font-bold text-lg">{symbol}</span>
                            <div className="ml-3 flex gap-1">
                              {summary.hasStock && (<span className="px-1 py-0.5 rounded text-xs bg-blue-600 text-white">S</span>)}
                              {summary.hasOptions && (<span className="px-1 py-0.5 rounded text-xs bg-purple-600 text-white">O</span>)}
                            </div>
                          </div>
                        </td>
                        <td className="text-right py-4 px-2 font-bold text-gray-200">{summary.totalQuantity.toLocaleString()}</td>
                        <td className="text-right py-4 px-2 text-gray-400">-</td>
                        <td className="text-right py-4 px-2 font-medium text-gray-200">${summary.currentPrice.toFixed(2)}</td>
                        <td className="text-right py-4 px-2 font-bold text-white">${summary.totalValue.toFixed(2)}</td>
                        <td className="text-right py-4 px-2 font-bold text-blue-300">{summary.accountPercent.toFixed(2)}%</td>
                        <td className={`text-right py-4 px-2 font-bold ${summary.totalPnL >= 0 ? 'text-green-400' : 'text-red-400'}`}>{summary.totalPnL >= 0 ? '+' : ''}${summary.totalPnL.toFixed(2)}</td>
                        <td className="text-right py-4 px-2 text-gray-400">-</td>
                        <td className="text-center py-4 px-2"><span className="px-2 py-1 rounded text-xs font-medium bg-gray-600 text-white">{summary.positionCount} POS</span></td>
                      </tr>

                      {/* Expanded children */}
                      {isExpanded && (
                        <tr>
                          <td colSpan="9" className="p-0">
                            <div className="bg-gray-900 border-l-4 border-blue-400">
                              <table className="w-full">
                                <tbody>
                                  {arr.map((p) => {
                                    const pnlPercent = p.unrealized_pnl_percent || 0;
                                    const accountPercent = (portfolioData?.totalMarketValue || 0) > 0 ? (p.market_value / (portfolioData?.totalMarketValue || 0)) * 100 : 0;
                                    return (
                                      <tr key={p.id} className="border-b border-gray-700 hover:bg-gray-700">
                                        <td className="py-3 px-6">
                                          <div className="flex items-center">
                                            <span className="text-gray-400 text-sm mr-2">├──</span>
                                            <span className="text-gray-300 font-medium">{p.position_type === 'stock' ? '📈 Stock' : '⚡ Option'}</span>
                                            {p.position_type === 'option' && (
                                              <div className="text-xs text-gray-400 ml-2">{p.metadata?.option_type} ${p.metadata?.strike_price} {p.metadata?.expiration_date}</div>
                                            )}
                                          </div>
                                        </td>
                                        <td className="text-right py-3 px-2 text-gray-200">{p.quantity}</td>
                                        <td className="text-right py-3 px-2 text-gray-200">${p.avg_cost.toFixed(2)}</td>
                                        <td className="text-right py-3 px-2 text-gray-200">${p.current_price.toFixed(2)}</td>
                                        <td className="text-right py-3 px-2 text-gray-200">${p.market_value.toFixed(2)}</td>
                                        <td className="text-right py-3 px-2 text-blue-400">{accountPercent.toFixed(2)}%</td>
                                        <td className={`text-right py-3 px-2 ${p.unrealized_pnl >= 0 ? 'text-green-400' : 'text-red-400'}`}>{p.unrealized_pnl >= 0 ? '+' : ''}${p.unrealized_pnl.toFixed(2)}</td>
                                        <td className={`text-right py-3 px-2 ${pnlPercent >= 0 ? 'text-green-400' : 'text-red-400'}`}>{pnlPercent >= 0 ? '+' : ''}{pnlPercent.toFixed(2)}%</td>
                                        <td className="text-center py-3 px-2"><span className={`px-2 py-1 rounded text-xs font-medium ${p.position_type === 'stock' ? 'bg-blue-600 text-white' : 'bg-purple-600 text-white'}`}>{p.position_type.toUpperCase()}</span></td>
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
                {/* Total row */}
                {positionsNormalized.length > 0 && (
                  <tr className="border-t-2 border-gray-600 bg-gray-700">
                    <td className="py-3 px-2 font-bold text-gray-200">TOTAL PORTFOLIO</td>
                    <td className="text-right py-3 px-2 font-bold text-gray-200">{positionsNormalized.reduce((sum, pos) => sum + Math.abs(pos.quantity || 0), 0).toLocaleString()}</td>
                    <td className="text-right py-3 px-2 text-gray-400">-</td>
                    <td className="text-right py-3 px-2 text-gray-400">-</td>
                    <td className="text-right py-3 px-2 font-bold text-white">${positionsNormalized.reduce((sum, pos) => sum + (pos.market_value || 0), 0).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</td>
                    <td className="text-right py-3 px-2 font-bold text-blue-300">100.00%</td>
                    <td className="text-right py-3 px-2 font-bold text-gray-200">{(positionsNormalized.reduce((s, p) => s + (p.unrealized_pnl || 0), 0) >= 0 ? '+' : '') + positionsNormalized.reduce((s, p) => s + (p.unrealized_pnl || 0), 0).toFixed(2)}</td>
                    <td className="text-right py-3 px-2 font-bold text-gray-200">{(portfolioData?.totalMarketValue || 0) > 0 ? `${(((positionsNormalized.reduce((s, p) => s + (p.unrealized_pnl || 0), 0)) / ((portfolioData?.totalMarketValue || 0) - (positionsNormalized.reduce((s, p) => s + (p.unrealized_pnl || 0), 0)))) * 100).toFixed(2)}%` : '0.00%'}</td>
                    <td className="text-center py-3 px-2"><span className="px-2 py-1 rounded text-xs font-medium bg-gray-600 text-white">{Object.keys(groupedPositions).length} SYMBOLS</span></td>
                  </tr>
                )}
              </tbody>
            </table>
          )}
        </div>
      </div>
    </div>
  );
};

export default TradeStationMainPortfolio;