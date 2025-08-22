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
  const [cashBalance, setCashBalance] = useState(0);

  const backendUrl = process.env.REACT_APP_BACKEND_URL;

  const monthNames = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"];

  const formatOptionDescription = (p) => {
    const base = (p.symbol || "").toUpperCase();
    const strike = p.metadata?.strike_price ? String(p.metadata.strike_price) : "";
    // YYYY-MM-DD -> Mon DD
    let descDate = "";
    const ed = p.metadata?.expiration_date;
    if (ed && /^\d{4}-\d{2}-\d{2}$/.test(ed)) {
      const [Y, M, D] = ed.split('-');
      const mon = monthNames[parseInt(M, 10) - 1] || M;
      descDate = `${mon} ${parseInt(D, 10)}`;
    } else if (p.metadata?.contract_symbol) {
      // Try to parse YYMMDD from contract symbol tail
      const parts = p.metadata.contract_symbol.split(' ');
      if (parts.length > 1) {
        const tail = parts[1];
        const yymmdd = tail.slice(0, 6);
        const yy = parseInt(yymmdd.slice(0, 2), 10);
        const mm = yymmdd.slice(2, 4);
        const dd = yymmdd.slice(4, 6);
        const mon = monthNames[parseInt(mm, 10) - 1] || mm;
        descDate = `${mon} ${parseInt(dd, 10)}`;
      }
    }
    const cp = (p.metadata?.option_type || "").toUpperCase() === 'PUT' ? 'Put' : 'Call';
    return `${base} ${descDate} ${strike} ${p.position_type === 'option' ? cp : 'Stock'}`.trim();
  };

  const normalizePositions = (rawPositions) => {
    return (rawPositions || []).map((pos) => {
      const rawSymbol = (pos.symbol || '').trim();
      const asset = (pos.asset_type || '').toUpperCase();
      let isStock = asset.includes('EQ') || asset.includes('STOCK');
      let isOption = asset.includes('OP') || asset.includes('OPTION');
      if (isOption) isStock = false; // STOCKOPTION treated as option

      // Detect option from symbol if needed: e.g., AAPL 271217C195 or AAPL_271217C195
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
      // TS variants
      if (isOption) {
        option_type = option_type || pos.right || pos.optionRight || pos.put_call || pos.CallPut; // CALL/PUT variants
        strike_price = strike_price || pos.strike || pos.strikePrice;
        expiration_date = expiration_date || pos.expiration || pos.expirationDate || pos.Expiry;
      }

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
            option_type = (cp || '').toUpperCase() === 'P' ? 'PUT' : 'CALL';
            strike_price = parseFloat(strikeStr);
          }
        } catch {}
      }

      const position_type = isStock ? 'stock' : (isOption ? 'option' : 'stock');
      const symbolField = position_type === 'option' ? baseSymbol : rawSymbol;
      const price = pos.mark_price || pos.current_price || pos.last_price || pos.market_price || pos.price || 0;
      const mv = pos.market_value || Math.abs((pos.quantity || 0) * price);

      // Potential numeric identifiers from TS (for future trade list)
      const symbol_number = pos.SymbolId || pos.SymbolID || pos.PositionID || pos.position_id || pos.id;

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
          symbol_number: symbol_number || null,
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

      // Balances (Cash)
      try {
        const balancesResponse = await fetch(`${backendUrl}/api/tradestation/accounts/${mainAccount.AccountID}/balances`);
        if (balancesResponse.ok) {
          const balancesData = await balancesResponse.json();
          const cashAvailable = balancesData?.balances?.Balances?.[0]?.CashBalance || balancesData?.balances?.CashBalance || 0;
          setCashBalance(parseFloat(cashAvailable) || 0);
        } else {
          setCashBalance(0);
        }
      } catch { setCashBalance(0); }

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

  const formatCurrency = (value, digits = 2) => new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', minimumFractionDigits: digits, maximumFractionDigits: digits }).format(value);
  const getChangeColor = (value) => (value >= 0 ? 'text-green-400' : 'text-red-400');
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
      const acctValue = (portfolioData?.totalMarketValue || 0) + (cashBalance || 0);
      const accountPercent = acctValue > 0 ? (totalValue / acctValue) * 100 : 0;
      const stock = arr.find((p) => p.position_type === 'stock');
      const currentPrice = stock ? stock.current_price : arr.reduce((s, p) => s + (p.current_price || 0), 0) / arr.length;
      groups[symbol]._summary = { symbol, totalValue, totalPnL: totalPnl, totalQuantity: totalQty, accountPercent, currentPrice, positionCount: arr.length, hasStock: arr.some((p) => p.position_type === 'stock'), hasOptions: arr.some((p) => p.position_type === 'option') };
    });

    return groups;
  }, [positionsNormalized, portfolioData?.totalMarketValue, cashBalance]);

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
  const accountValue = (portfolioData?.totalMarketValue || 0) + (cashBalance || 0);
  const stocksValue = (positionsNormalized || []).filter(p => p.position_type === 'stock').reduce((s,p)=> s + (p.market_value || 0), 0);
  const optionsValue = (positionsNormalized || []).filter(p => p.position_type === 'option').reduce((s,p)=> s + (p.market_value || 0), 0);

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

          {/* Account Value with breakdown */}
          <div className="mt-6">
            <div className="flex items-center space-x-2">
              <Eye className="text-white" size={20} />
              <span className="text-4xl font-bold text-white">{formatCurrency(accountValue, 0)}</span>
              <span className="text-blue-100">(Account Value)</span>
            </div>
            <div className="mt-2 flex items-center gap-4 text-sm text-blue-100">
              <span>Market Value: <strong>{formatCurrency(portfolioData?.totalMarketValue || 0, 0)}</strong></span>
              <span>Cash: <strong>{formatCurrency(cashBalance || 0, 0)}</strong></span>
            </div>
            <div className={`flex items-center mt-2 space-x-2 ${getChangeColor(portfolioData?.totalUnrealizedPnL)}`}>
              <ChangeIcon size={24} />
              <span className="text-2xl font-semibold">{portfolioData?.totalUnrealizedPnL >= 0 ? '+' : ''}{formatCurrency(Math.abs(portfolioData?.totalUnrealizedPnL || 0), 0)}</span>
              <span className="text-lg">({portfolioData?.percentChange >= 0 ? '+' : ''}{(portfolioData?.percentChange || 0).toFixed(2)}%)</span>
            </div>
            <p className="text-blue-100 text-sm mt-1">Last updated: {lastUpdated.toLocaleString()}</p>
          </div>
        </div>
      </div>

      {/* Summary Cards moved under header */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-6">
        <div className="grid grid-cols-1 md:grid-cols-5 gap-6">
          <div className="bg-gray-800 p-6 rounded-xl shadow-lg border border-gray-700">
            <p className="text-gray-400 text-sm">Account Value</p>
            <p className="text-3xl font-bold text-white">{formatCurrency(accountValue, 0)}</p>
          </div>
          <div className="bg-gray-800 p-6 rounded-xl shadow-lg border border-gray-700">
            <p className="text-gray-400 text-sm">Unrealized P&amp;L</p>
            <p className={`text-3xl font-bold ${portfolioData?.totalUnrealizedPnL >= 0 ? 'text-green-400' : 'text-red-400'}`}>{portfolioData?.totalUnrealizedPnL >= 0 ? '+' : ''}{formatCurrency(Math.abs(portfolioData?.totalUnrealizedPnL || 0), 0)}</p>
          </div>
          <div className="bg-gray-800 p-6 rounded-xl shadow-lg border border-gray-700">
            <p className="text-gray-400 text-sm">Stocks</p>
            <p className="text-3xl font-bold text-white">{formatCurrency(stocksValue, 0)}</p>
          </div>
          <div className="bg-gray-800 p-6 rounded-xl shadow-lg border border-gray-700">
            <p className="text-gray-400 text-sm">Options</p>
            <p className="text-3xl font-bold text-white">{formatCurrency(optionsValue, 0)}</p>
          </div>
          <div className="bg-gray-800 p-6 rounded-xl shadow-lg border border-gray-700">
            <p className="text-gray-400 text-sm">Cash</p>
            <p className="text-3xl font-bold text-white">{formatCurrency(cashBalance || 0, 0)}</p>
          </div>
        </div>
      </div>

      {/* Detailed Holdings - inline, LIVE only */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="flex items-center justify-between mb-3">
          <div className="text-sm text-gray-300">Positions: <span className="font-semibold text-white">{portfolioData?.totalPositions || 0}</span></div>
          {positionsNormalized.length > 0 && (
            <div className="flex gap-2">
              <button onClick={expandAll} className="px-3 py-1 bg-gray-700 text-gray-200 rounded hover:bg-gray-600">Expand All</button>
              <button onClick={collapseAll} className="px-3 py-1 bg-gray-700 text-gray-200 rounded hover:bg-gray-600">Collapse All</button>
            </div>
          )}
        </div>

        {error && (
          <div className="bg-red-900 border border-red-700 rounded-lg p-4 mb-4 text-red-300">Error: {error}</div>
        )}

        {positionsNormalized.length === 0 && !error && (
          <div className="text-center py-8 text-gray-400">No positions found.</div>
        )}

        {positionsNormalized.length > 0 && (
          <table className="w-full text-sm bg-gray-800 rounded-lg">
            <thead>
              <tr className="border-b border-gray-700">
                <th className="text-left py-3 px-2 font-medium text-gray-300">Symbol</th>
                <th className="text-left py-3 px-2 font-medium text-gray-300">Description</th>
                <th className="text-left py-3 px-2 font-medium text-gray-300">Position</th>
                <th className="text-right py-3 px-2 font-medium text-gray-300">Open P/L</th>
                <th className="text-right py-3 px-2 font-medium text-gray-300">Avg Price</th>
                <th className="text-right py-3 px-2 font-medium text-gray-300">Today's Open P/L</th>
                <th className="text-right py-3 px-2 font-medium text-gray-300">Open P/L / Qty</th>
                <th className="text-right py-3 px-2 font-medium text-gray-300">Open P/L %</th>
                <th className="text-right py-3 px-2 font-medium text-gray-300">Total Cost</th>
                <th className="text-right py-3 px-2 font-medium text-gray-300">Market Value</th>
                <th className="text-right py-3 px-2 font-medium text-gray-300">Qty</th>
                <th className="text-right py-3 px-2 font-medium text-gray-300">Last</th>
                <th className="text-right py-3 px-2 font-medium text-gray-300">Contract Exp Date</th>
              </tr>
            </thead>
            <tbody>
              {Object.keys(groupedPositions).sort().map((symbol) => {
                const arr = groupedPositions[symbol];
                const summary = arr._summary;
                const isExpanded = !!expandedTickers[symbol];

                // Case 1: Single stock only -> render leaf row with full details (no expand)
                if (summary.hasStock && !summary.hasOptions && summary.positionCount === 1) {
                  const p = arr[0];
                  const qty = Math.abs(p.quantity || 0);
                  const isLong = (p.quantity || 0) >= 0;
                  const openPL = p.unrealized_pnl || 0;
                  const openPLPerQty = qty > 0 ? openPL / qty : 0;
                  const openPLPct = p.unrealized_pnl_percent || (qty > 0 && p.avg_cost > 0 ? (openPL / (qty * p.avg_cost)) * 100 : 0);
                  const totalCost = qty * (p.avg_cost || 0);
                  const symbolNumber = p.metadata?.symbol_number ? `#${p.metadata.symbol_number}` : '';

                  return (
                    <tr key={p.id} className="border-b border-gray-700 hover:bg-gray-700">
                      <td className="py-3 px-2 text-gray-200">{symbolNumber && (<span className="text-gray-400 mr-2">{symbolNumber}</span>)}{p.symbol}</td>
                      <td className="py-3 px-2 text-gray-200">{`${p.symbol} Stock`}</td>
                      <td className="py-3 px-2 text-gray-200">{`${qty} ${isLong ? 'Long' : 'Short'}`}</td>
                      <td className={`text-right py-3 px-2 ${openPL >= 0 ? 'text-green-400' : 'text-red-400'}`}>{openPL >= 0 ? '+' : ''}{formatCurrency(Math.abs(openPL), 0)}</td>
                      <td className="text-right py-3 px-2 text-gray-200">{formatCurrency(p.avg_cost, 2)}</td>
                      <td className="text-right py-3 px-2 text-gray-400">-</td>
                      <td className="text-right py-3 px-2 text-gray-200">{formatCurrency(openPLPerQty, 2)}</td>
                      <td className={`text-right py-3 px-2 ${openPLPct >= 0 ? 'text-green-400' : 'text-red-400'}`}>{openPLPct >= 0 ? '+' : ''}{openPLPct.toFixed(2)}%</td>
                      <td className="text-right py-3 px-2 text-gray-200">{formatCurrency(totalCost, 0)}</td>
                      <td className="text-right py-3 px-2 text-gray-200">{formatCurrency(p.market_value, 0)}</td>
                      <td className="text-right py-3 px-2 text-gray-200">{qty}</td>
                      <td className="text-right py-3 px-2 text-gray-200">{formatCurrency(p.current_price, 2)}</td>
                      <td className="text-right py-3 px-2 text-gray-200">-</td>
                    </tr>
                  );
                }

                // Case 2: Grouped (stock + options or options only) -> header + expandable children
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
                      <td className="text-left py-4 px-2 text-gray-200">-</td>
                      <td className="text-left py-4 px-2 text-gray-200">-</td>
                      <td className={`text-right py-4 px-2 font-bold ${summary.totalPnL >= 0 ? 'text-green-400' : 'text-red-400'}`}>{summary.totalPnL >= 0 ? '+' : ''}{formatCurrency(Math.abs(summary.totalPnL), 0)}</td>
                      <td className="text-right py-4 px-2 text-gray-400">-</td>
                      <td className="text-right py-4 px-2 text-gray-400">-</td>
                      <td className="text-right py-4 px-2 text-gray-400">-</td>
                      <td className="text-right py-4 px-2 text-gray-400">-</td>
                      <td className="text-right py-4 px-2 text-gray-400">-</td>
                      <td className="text-right py-4 px-2 font-bold text-white">{formatCurrency(summary.totalValue, 0)}</td>
                      <td className="text-right py-4 px-2 font-bold text-gray-200">{summary.totalQuantity.toLocaleString()}</td>
                      <td className="text-right py-4 px-2 font-medium text-gray-200">{formatCurrency(summary.currentPrice, 2)}</td>
                      <td className="text-right py-4 px-2 text-gray-400">-</td>
                    </tr>

                    {/* Expanded children */}
                    {isExpanded && (
                      <tr>
                        <td colSpan="13" className="p-0">
                          <div className="bg-gray-900 border-l-4 border-blue-400">
                            <table className="w-full">
                              <tbody>
                                {arr.map((p) => {
                                  const qty = Math.abs(p.quantity || 0);
                                  const isLong = (p.quantity || 0) >= 0;
                                  const openPL = p.unrealized_pnl || 0;
                                  const openPLPerQty = qty > 0 ? openPL / qty : 0;
                                  const openPLPct = p.unrealized_pnl_percent || (qty > 0 && p.avg_cost > 0 ? (openPL / (qty * p.avg_cost)) * 100 : 0);
                                  const totalCost = qty * (p.avg_cost || 0);
                                  const expDate = p.position_type === 'option' ? (p.metadata?.expiration_date || '-') : '-';
                                  const positionLabel = `${qty} ${isLong ? 'Long' : 'Short'}`;
                                  const symbolNumber = p.metadata?.symbol_number ? `#${p.metadata.symbol_number}` : '';
                                  const description = p.position_type === 'option' ? formatOptionDescription(p) : `${p.symbol} Stock`;
                                  return (
                                    <tr key={p.id} className="border-b border-gray-700 hover:bg-gray-700">
                                      <td className="py-3 px-2 text-gray-200">{symbolNumber && (<span className="text-gray-400 mr-2">{symbolNumber}</span>)}{p.symbol}</td>
                                      <td className="text-left py-3 px-2 text-gray-200">{description}</td>
                                      <td className="text-left py-3 px-2 text-gray-200">{positionLabel}</td>
                                      <td className={`text-right py-3 px-2 ${openPL >= 0 ? 'text-green-400' : 'text-red-400'}`}>{openPL >= 0 ? '+' : ''}{formatCurrency(Math.abs(openPL), 0)}</td>
                                      <td className="text-right py-3 px-2 text-gray-200">{formatCurrency(p.avg_cost, 2)}</td>
                                      <td className="text-right py-3 px-2 text-gray-400">-</td>
                                      <td className="text-right py-3 px-2 text-gray-200">{formatCurrency(openPLPerQty, 2)}</td>
                                      <td className={`text-right py-3 px-2 ${openPLPct >= 0 ? 'text-green-400' : 'text-red-400'}`}>{openPLPct >= 0 ? '+' : ''}{openPLPct.toFixed(2)}%</td>
                                      <td className="text-right py-3 px-2 text-gray-200">{formatCurrency(totalCost, 0)}</td>
                                      <td className="text-right py-3 px-2 text-gray-200">{formatCurrency(p.market_value, 0)}</td>
                                      <td className="text-right py-3 px-2 text-gray-200">{qty}</td>
                                      <td className="text-right py-3 px-2 text-gray-200">{formatCurrency(p.current_price, 2)}</td>
                                      <td className="text-right py-3 px-2 text-gray-200">{expDate}</td>
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
            </tbody>
          </table>
        )}

        {/* Bottom Cards (moved here) */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-8">
          <div className="bg-gray-800 p-6 rounded-xl shadow-lg border border-gray-700">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-sm">Account Value</p>
                <p className="text-3xl font-bold text-white">{formatCurrency(accountValue, 0)}</p>
              </div>
              <DollarSign className="text-yellow-400" size={32} />
            </div>
          </div>
          <div className="bg-gray-800 p-6 rounded-xl shadow-lg border border-gray-700">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-sm">Unrealized P&amp;L</p>
                <p className={`text-3xl font-bold ${portfolioData?.totalUnrealizedPnL >= 0 ? 'text-green-400' : 'text-red-400'}`}>{portfolioData?.totalUnrealizedPnL >= 0 ? '+' : ''}{formatCurrency(Math.abs(portfolioData?.totalUnrealizedPnL || 0), 0)}</p>
              </div>
              <BarChart3 className="text-green-400" size={32} />
            </div>
          </div>
          <div className="bg-gray-800 p-6 rounded-xl shadow-lg border border-gray-700">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-sm">Cash Balance</p>
                <p className="text-3xl font-bold text-white">{formatCurrency(cashBalance || 0, 0)}</p>
              </div>
              <Target className="text-blue-400" size={32} />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TradeStationMainPortfolio;