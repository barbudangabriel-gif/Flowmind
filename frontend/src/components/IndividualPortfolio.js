import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import {
  ChevronDown,
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
  const [contextMenu, setContextMenu] = useState({ isVisible: false, position: { x: 0, y: 0 }, selectedPosition: null });

  // Portfolio management hook
  const { portfolios, availablePortfolios, fetchPortfolioPositions, fetchAvailablePortfolios, movePosition, clearError } = usePortfolioManagement();

  // Current portfolio data
  const [currentPortfolio, setCurrentPortfolio] = useState(null);
  const [positions, setPositions] = useState([]);
  const [cashBalance, setCashBalance] = useState(0);
  const [expandedTickers, setExpandedTickers] = useState(new Set());
  const [error, setError] = useState(null);

  const getChangeColor = (change) => (change >= 0 ? 'text-green-400' : 'text-red-400');

  // Persistence for expanded tickers per-portfolio
  useEffect(() => {
    const key = `expandedTickers:${portfolioId}`;
    const saved = localStorage.getItem(key);
    if (saved) {
      try { setExpandedTickers(new Set(JSON.parse(saved))); } catch {}
    } else { setExpandedTickers(new Set()); }
  }, [portfolioId]);
  useEffect(() => {
    const key = `expandedTickers:${portfolioId}`;
    try { localStorage.setItem(key, JSON.stringify(Array.from(expandedTickers))); } catch {}
  }, [expandedTickers, portfolioId]);

  // Load data (force LIVE for TradeStation Main)
  useEffect(() => {
    const isTradeStation = portfolioId === 'tradestation-main';

    const loadRealTradeStationData = async () => {
      try {
        setLoading(true);
        // Accounts
        const accountsResp = await Promise.race([
          fetch(`${process.env.REACT_APP_BACKEND_URL}/api/tradestation/accounts`),
          new Promise((_, rej) => setTimeout(() => rej(new Error('Accounts timeout')), 12000))
        ]);
        const accountsData = await accountsResp.json();
        const accounts = accountsData.accounts || accountsData;
        let mainAccount = null;
        if (Array.isArray(accounts)) mainAccount = accounts.find((acc) => acc.Type === 'Margin') || accounts[0];
        else if (accounts && typeof accounts === 'object') mainAccount = accounts;
        if (!mainAccount || !mainAccount.AccountID) throw new Error('No TradeStation accounts found');

        // Positions
        const positionsResp = await Promise.race([
          fetch(`${process.env.REACT_APP_BACKEND_URL}/api/tradestation/accounts/${mainAccount.AccountID}/positions`),
          new Promise((_, rej) => setTimeout(() => rej(new Error('Positions timeout')), 15000))
        ]);
        if (!positionsResp.ok) throw new Error(`Positions request failed: ${positionsResp.status}`);
        const positionsData = await positionsResp.json();

        // Balances
        try {
          const balancesResp = await Promise.race([
            fetch(`${process.env.REACT_APP_BACKEND_URL}/api/tradestation/accounts/${mainAccount.AccountID}/balances`),
            new Promise((_, rej) => setTimeout(() => rej(new Error('Balances timeout')), 10000))
          ]);
          const balancesData = await balancesResp.json();
          const cashAvailable = balancesData?.balances?.Balances?.[0]?.CashBalance || balancesData?.balances?.CashBalance || 0;
          setCashBalance(parseFloat(cashAvailable) || 0);
        } catch { setCashBalance(0); }

        // Transform positions
        const transformed = (positionsData.positions || positionsData.data || positionsData || []).map((pos) => {
          const rawSymbol = (pos.symbol || '').trim();
          const asset = (pos.asset_type || '').toUpperCase();
          let isStock = asset.includes('EQ') || asset.includes('STOCK');
          let isOption = asset.includes('OP') || asset.includes('OPTION');
          let baseSymbol = (rawSymbol.split(' ')[0] || rawSymbol).split('_')[0];
          const symbolTail = rawSymbol.replace(baseSymbol, '').replace(/^[ _]/, '');
          const pattern = /^(\d{6})([CP])([0-9]+(?:\.[0-9]+)?)$/i;
          let optionMatch = null;
          if (!isOption && symbolTail) {
            optionMatch = symbolTail.match(pattern); if (optionMatch) { isOption = true; isStock = false; }
          }
          let option_type = pos.option_type, strike_price = pos.strike_price, expiration_date = pos.expiration_date;
          if (isOption && (!option_type || !strike_price || !expiration_date)) {
            try {
              if (!optionMatch) { const parts = rawSymbol.split(' '); if (parts.length > 1) optionMatch = parts[1].match(pattern); }
              if (optionMatch) {
                const [, yymmdd, cp, strikeStr] = optionMatch; const yy = parseInt(yymmdd.slice(0,2),10); const mm = yymmdd.slice(2,4); const dd = yymmdd.slice(4,6);
                const fullYear = yy >= 70 ? 1900 + yy : 2000 + yy; expiration_date = `${fullYear}-${mm}-${dd}`; option_type = cp.toUpperCase()==='P' ? 'PUT' : 'CALL'; strike_price = parseFloat(strikeStr);
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
            metadata: { asset_type: pos.asset_type, option_type, strike_price, expiration_date, contract_symbol: rawSymbol, source: 'tradestation_direct_api' }
          };
        });

        const totalValue = transformed.reduce((s, p) => s + (p.market_value || 0), 0);
        const totalPnl = transformed.reduce((s, p) => s + (p.unrealized_pnl || 0), 0);
        setPositions(transformed);
        setCurrentPortfolio({ id: 'tradestation-main', name: 'TradeStation Main', total_value: totalValue, total_pnl: totalPnl, positions_count: transformed.length, description: `Live TradeStation Account ${mainAccount.AccountID}` });
        await fetchAvailablePortfolios('tradestation-main');
      } catch (e) {
        setError(e.message);
        setPositions([]);
        await fetchAvailablePortfolios('tradestation-main');
      } finally { setLoading(false); }
    };

    const loadOtherPortfolioData = async () => {
      try {
        setLoading(true);
        const portfolio = portfolios.find((p) => p.id === portfolioId) || null;
        setCurrentPortfolio(portfolio);
        const fetched = await fetchPortfolioPositions(portfolioId);
        await fetchAvailablePortfolios(portfolioId);
        const transformed = (fetched || []).map((pos) => ({
          id: pos.id || `${pos.symbol}-${Math.random()}`,
          symbol: pos.symbol,
          quantity: pos.quantity || 0,
          avg_cost: pos.avg_cost ?? pos.average_price ?? 0,
          current_price: pos.current_price ?? pos.mark_price ?? 0,
          market_value: pos.market_value ?? Math.abs((pos.quantity || 0) * (pos.current_price ?? pos.mark_price ?? 0)),
          unrealized_pnl: pos.unrealized_pnl ?? 0,
          unrealized_pnl_percent: pos.unrealized_pnl_percent ?? 0,
          portfolio_id: portfolioId,
          position_type: pos.position_type || pos.type || 'stock',
          metadata: { ...(pos.metadata || {}), source: pos.metadata?.source || 'portfolio_management_service' }
        }));
        const totalValue = transformed.reduce((s, p) => s + (p.market_value || 0), 0);
        const totalPnl = transformed.reduce((s, p) => s + (p.unrealized_pnl || 0), 0);
        setPositions(transformed);
        setCurrentPortfolio((prev) => ({ id: portfolioId, name: portfolio?.name || portfolioId, total_value: totalValue, total_pnl: totalPnl, positions_count: transformed.length, description: portfolio?.description || '' }));
      } catch (e) { setError(e.message); setPositions([]); } finally { setLoading(false); }
    };

    if (isTradeStation) loadRealTradeStationData();
    else if (portfolioId && portfolios.length > 0) loadOtherPortfolioData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [portfolioId]);

  // Context menu handlers
  const handleContextMenu = (event, position) => { event.preventDefault(); setContextMenu({ isVisible: true, position: { x: event.clientX, y: event.clientY }, selectedPosition: position }); };
  const closeContextMenu = () => { setContextMenu({ isVisible: false, position: { x: 0, y: 0 }, selectedPosition: null }); };
  const handleMovePosition = async (positionId, toPortfolioId, portfolioName) => {
    try { const result = await movePosition(positionId, toPortfolioId); if (result.success) { alert(`Position moved successfully to ${portfolioName}`); await fetchPortfolioPositions(portfolioId); } else { throw new Error(result.error || 'Failed to move position'); } } catch (err) { alert(`Error moving position: ${err.message}`); }
  };

  const displayPortfolio = currentPortfolio || { id: portfolioId, name: portfolioId === 'tradestation-main' ? 'TradeStation Main' : (portfolios.find((p) => p.id === portfolioId)?.name || 'Portfolio'), total_value: 0, total_pnl: 0, positions_count: 0 };
  const changePercent = displayPortfolio.total_value > 0 ? (displayPortfolio.total_pnl / (displayPortfolio.total_value - displayPortfolio.total_pnl)) * 100 : 0;

  // Group positions
  const groupedPositions = React.useMemo(() => {
    if (!positions || positions.length === 0) return {};
    const getBaseSymbol = (p) => {
      if (p.metadata?.underlying_symbol) return (p.metadata.underlying_symbol || '').toUpperCase();
      const raw = (p.symbol || '').trim();
      const first = (raw.split(' ')[0] || raw).split('_')[0];
      return (first || raw).toUpperCase();
    };
    const groups = {};
    positions.forEach((pos) => {
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
      const accountPercent = displayPortfolio?.total_value > 0 ? (totalValue / displayPortfolio.total_value) * 100 : 0;
      const stock = arr.find((p) => p.position_type === 'stock');
      const currentPrice = stock ? stock.current_price : arr.reduce((s, p) => s + (p.current_price || 0), 0) / arr.length;
      groups[symbol]._summary = { symbol, totalValue, totalPnL: totalPnl, totalQuantity: totalQty, accountPercent, currentPrice, positionCount: arr.length, hasStock: arr.some((p) => p.position_type === 'stock'), hasOptions: arr.some((p) => p.position_type === 'option') };
    });
    return groups;
  }, [positions, displayPortfolio?.total_value]);

  const toggleTicker = (symbol) => { const next = new Set(expandedTickers); if (next.has(symbol)) next.delete(symbol); else next.add(symbol); setExpandedTickers(next); };
  const expandAll = () => setExpandedTickers(new Set(Object.keys(groupedPositions)));
  const collapseAll = () => setExpandedTickers(new Set());

  return (
    <div className="min-h-screen bg-slate-900">
      <div className="bg-gradient-to-r from-blue-600 to-blue-700 px-6 py-4">
        <div className="flex items-center justify-between">
          <h1 className="text-2xl font-bold text-white flex items-center">Portfolio {displayPortfolio.name}</h1>
        </div>
        <div className="flex items-center mt-2">
          <Eye className="text-white mr-2" size={16} />
          <span className="text-3xl font-bold text-white">${((displayPortfolio?.total_value || 0) + cashBalance).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</span>
          <span className="text-sm text-blue-200 ml-2">(Total Account Value)</span>
          <span className={`ml-4 text-lg font-medium ${displayPortfolio.total_pnl >= 0 ? 'text-green-300' : 'text-red-300'}`}>{displayPortfolio.total_pnl >= 0 ? '+' : ''}${Math.abs(displayPortfolio.total_pnl).toFixed(2)} ({changePercent >= 0 ? '+' : ''}{changePercent.toFixed(2)}%)</span>
        </div>
        <div className="flex items-center mt-4 space-x-3">
          <button onClick={() => navigate(`/portfolios/${portfolioId}/charts`)} className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
            <PieChartIcon size={16} />
            <span>Charts</span>
          </button>
          <button onClick={() => navigate(`/portfolios/${portfolioId}/rebalancing`)} className="flex items-center space-x-2 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors">
            <Brain size={16} />
            <span>AI Rebalancing</span>
          </button>
        </div>
      </div>

      <div className="border-b border-slate-700 bg-slate-800">
        <div className="flex space-x-8 px-6">
          {[{ id: 'summary', label: 'Summary' }, { id: 'health-score', label: 'Health Score' }, { id: 'ratings', label: 'Ratings' }, { id: 'holdings', label: 'Holdings' }, { id: 'dividends', label: 'Dividends' }, { id: 'add-edit-views', label: '+ Add / Edit Views', hasArrow: true }].map((tab) => (
            <button key={tab.id} onClick={() => (tab.id === 'add-edit-views' ? navigate(`/portfolios/${portfolioId}/add-edit-views`) : setActiveTab(tab.id))} className={`py-4 px-2 border-b-2 font-medium text-sm flex items-center ${activeTab === tab.id ? 'border-blue-400 text-blue-400' : 'border-transparent text-slate-400 hover:text-slate-200 hover:border-slate-600'}`}>{tab.label}{tab.hasArrow && <span className="ml-1 text-red-400">→</span>}</button>
          ))}
        </div>
      </div>

      <div className="p-6 bg-slate-900">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
          <div className="bg-slate-800 rounded-lg p-6 border border-slate-600">
            <div className="flex items-center justify-between"><div><p className="text-sm font-medium text-slate-300">Stock Positions</p><p className="text-2xl font-bold text-white">{positions.filter((p) => p.position_type === 'stock').length}</p><p className="text-sm text-slate-400">${positions.filter((p)=>p.position_type==='stock').reduce((s,p)=>s+(p.market_value||0),0).toLocaleString()}</p></div><div className="p-3 bg-blue-600 rounded-full"><BarChart3 className="h-6 w-6 text-white" /></div></div>
          </div>
          <div className="bg-slate-800 rounded-lg p-6 border border-slate-600">
            <div className="flex items-center justify-between"><div><p className="text-sm font-medium text-slate-300">Options Positions</p><p className="text-2xl font-bold text-white">{positions.filter((p) => p.position_type === 'option').length}</p><p className="text-sm text-slate-400">${positions.filter((p)=>p.position_type==='option').reduce((s,p)=>s+(p.market_value||0),0).toLocaleString()}</p></div><div className="p-3 bg-purple-600 rounded-full"><Target className="h-6 w-6 text-white" /></div></div>
          </div>
          <div className="bg-slate-800 rounded-lg p-6 border border-slate-600">
            <div className="flex items-center justify-between"><div><p className="text-sm font-medium text-slate-300">Cash Balance</p><p className="text-2xl font-bold text-white">${cashBalance.toLocaleString(undefined, { minimumFractionDigits: 0, maximumFractionDigits: 0 })}</p><p className="text-sm text-slate-400">Available Cash</p></div><div className="p-3 bg-green-600 rounded-full"><DollarSign className="h-6 w-6 text-white" /></div></div>
          </div>
        </div>

        <div className="overflow-x-auto">
          <div className="flex items-center justify-between mb-3">
            {loading ? (<div className="flex items-center py-2"><div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div><span className="ml-2 text-slate-300">Loading positions...</span></div>) : (<div />)}
            {positions.length > 0 && (<div className="flex gap-2"><button onClick={() => setExpandedTickers(new Set(Object.keys(groupedPositions)))} className="px-3 py-1 bg-slate-700 text-slate-200 rounded hover:bg-slate-600">Expand All</button><button onClick={() => setExpandedTickers(new Set())} className="px-3 py-1 bg-slate-700 text-slate-200 rounded hover:bg-slate-600">Collapse All</button></div>)}
          </div>

          {error && (<div className="bg-red-900 border border-red-700 rounded-lg p-4 mb-4 text-red-300">Error: {error}<button onClick={clearError} className="ml-2 text-red-400 hover:text-red-200">Dismiss</button></div>)}
          {!loading && positions.length === 0 && !error && (<div className="text-center py-8 text-slate-400">No positions found in this portfolio.</div>)}

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
                {Object.keys(groupedPositions).sort().map((symbol) => {
                  const arr = groupedPositions[symbol]; const summary = arr._summary; const isExpanded = expandedTickers.has(symbol);
                  return (
                    <React.Fragment key={symbol}>
                      <tr className="border-b border-slate-600 bg-slate-800 hover:bg-slate-700" title={`Click to ${isExpanded ? 'collapse' : 'expand'} ${symbol} positions`}>
                        <td className="py-4 px-2">
                          <button
                            type="button"
                            aria-expanded={isExpanded}
                            onClick={() => toggleTicker(symbol)}
                            onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); toggleTicker(symbol); } }}
                            className="w-full text-left flex items-center focus:outline-none cursor-pointer"
                          >
                            <ChevronDown className={`w-4 h-4 text-slate-400 mr-2 transform transition-transform duration-200 ${isExpanded ? 'rotate-180' : 'rotate-0'}`} />
                            <span className="text-blue-300 font-bold text-lg">{symbol}</span>
                            <div className="ml-3 flex gap-1">
                              {summary.hasStock && (
                                <span className="px-1 py-0.5 rounded text-xs bg-blue-600 text-white">S</span>
                              )}
                              {summary.hasOptions && (
                                <span className="px-1 py-0.5 rounded text-xs bg-purple-600 text-white">O</span>
                              )}
                            </div>
                          </button>
                        </td>
                        <td className="text-right py-4 px-2 font-bold text-slate-200">{summary.totalQuantity.toLocaleString()}</td>
                        <td className="text-right py-4 px-2 text-slate-400">-</td>
                        <td className="text-right py-4 px-2 font-medium text-slate-200">${summary.currentPrice.toFixed(2)}</td>
                        <td className="text-right py-4 px-2 font-bold text-white">${summary.totalValue.toFixed(2)}</td>
                        <td className="text-right py-4 px-2 font-bold text-blue-300">{summary.accountPercent.toFixed(2)}%</td>
                        <td className={`text-right py-4 px-2 font-bold ${getChangeColor(summary.totalPnL)}`}>{summary.totalPnL >= 0 ? '+' : ''}${summary.totalPnL.toFixed(2)}</td>
                        <td className="text-right py-4 px-2 text-slate-400">-</td>
                        <td className="text-center py-4 px-2"><span className="px-2 py-1 rounded text-xs font-medium bg-slate-600 text-white">{summary.positionCount} POS</span></td>
                      </tr>
                      {isExpanded && (
                        <tr>
                          <td colSpan="9" className="p-0">
                            <div className="bg-slate-900 border-l-4 border-blue-400"><table className="w-full"><tbody>
                              {arr.map((p) => {
                                const pnlPercent = p.unrealized_pnl_percent || 0;
                                const accountPercent = displayPortfolio?.total_value > 0 ? (p.market_value / displayPortfolio.total_value) * 100 : 0;
                                return (
                                  <tr key={p.id} className="border-b border-slate-700 hover:bg-slate-700 cursor-context-menu" onContextMenu={(e) => handleContextMenu(e, p)}>
                                    <td className="py-3 px-6"><div className="flex items-center"><span className="text-slate-400 text-sm mr-2">├──</span><span className="text-slate-300 font-medium">{p.position_type === 'stock' ? '📈 Stock' : '⚡ Option'}</span>{p.position_type === 'option' && (<div className="text-xs text-slate-400 ml-2">{p.metadata?.option_type} ${p.metadata?.strike_price} {p.metadata?.expiration_date}</div>)}</div></td>
                                    <td className="text-right py-3 px-2 text-slate-200">{p.quantity}</td>
                                    <td className="text-right py-3 px-2 text-slate-200">${p.avg_cost.toFixed(2)}</td>
                                    <td className="text-right py-3 px-2 text-slate-200">${p.current_price.toFixed(2)}</td>
                                    <td className="text-right py-3 px-2 text-slate-200">${p.market_value.toFixed(2)}</td>
                                    <td className="text-right py-3 px-2 text-blue-400">{accountPercent.toFixed(2)}%</td>
                                    <td className={`text-right py-3 px-2 ${getChangeColor(p.unrealized_pnl)}`}>{p.unrealized_pnl >= 0 ? '+' : ''}${p.unrealized_pnl.toFixed(2)}</td>
                                    <td className={`text-right py-3 px-2 ${getChangeColor(pnlPercent)}`}>{pnlPercent >= 0 ? '+' : ''}{pnlPercent.toFixed(2)}%</td>
                                    <td className="text-center py-3 px-2"><span className={`px-2 py-1 rounded text-xs font-medium ${p.position_type === 'stock' ? 'bg-blue-600 text-white' : 'bg-purple-600 text-white'}`}>{p.position_type.toUpperCase()}</span></td>
                                  </tr>
                                );
                              })}
                            </tbody></table></div>
                          </td>
                        </tr>
                      )}
                    </React.Fragment>
                  );
                })}
                <tr className="border-t-2 border-slate-600 bg-slate-700">
                  <td className="py-3 px-2 font-bold text-slate-200">TOTAL PORTFOLIO</td>
                  <td className="text-right py-3 px-2 font-bold text-slate-200">{positions.reduce((sum, pos) => sum + Math.abs(pos.quantity || 0), 0).toLocaleString()}</td>
                  <td className="text-right py-3 px-2 text-slate-400">-</td>
                  <td className="text-right py-3 px-2 text-slate-400">-</td>
                  <td className="text-right py-3 px-2 font-bold text-white">${positions.reduce((sum, pos) => sum + (pos.market_value || 0), 0).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</td>
                  <td className="text-right py-3 px-2 font-bold text-blue-300">100.00%</td>
                  <td className={`text-right py-3 px-2 font-bold ${getChangeColor(positions.reduce((s, p) => s + (p.unrealized_pnl || 0), 0))}`}>{positions.reduce((s, p) => s + (p.unrealized_pnl || 0), 0) >= 0 ? '+' : ''}{positions.reduce((s, p) => s + (p.unrealized_pnl || 0), 0).toFixed(2)}</td>
                  <td className={`text-right py-3 px-2 font-bold ${getChangeColor(displayPortfolio.total_pnl || 0)}`}>{displayPortfolio?.total_value > 0 ? `${(((displayPortfolio.total_pnl || 0) / (displayPortfolio.total_value - (displayPortfolio.total_pnl || 0))) * 100).toFixed(2)}%` : '0.00%'}</td>
                  <td className="text-center py-3 px-2"><span className="px-2 py-1 rounded text-xs font-medium bg-slate-600 text-white">{Object.keys(groupedPositions).length} SYMBOLS</span></td>
                </tr>
              </tbody>
            </table>
          )}
        </div>

        {/* News/Transcripts Section (placeholder) */}
        <div className="mt-6 space-y-4">
          {[{ symbol: 'MCHP', title: 'Microchip Technology Incorporated (MCHP) Presents at KeyBanc Technology Leadership Forum Conference Transcript', source: 'SA Transcripts', date: 'Thu, Aug 14' }, { symbol: 'SWKS', title: 'Skyworks Solutions, Inc. (SWKS) KeyBanc Technology Leadership Forum Conference (Transcript)', source: 'SA Transcripts', date: 'Tue, Aug 12' }].map((item, index) => (
            <div key={index} className="flex items-start space-x-4 p-4 hover:bg-gray-50 rounded-lg cursor-pointer"><div className="w-10 h-10 bg-gray-100 rounded-lg flex items-center justify-center"><FileText className="text-gray-500" size={16} /></div><div className="flex-1"><h3 className="font-medium text-gray-900 hover:text-blue-600">{item.title}</h3><div className="flex items-center mt-1 space-x-2 text-sm text-gray-500"><span className="text-blue-600 font-medium">{item.symbol}</span><span>•</span><span>{item.source}</span><span>•</span><span>{item.date}</span><span>•</span><span>📄</span></div></div></div>
          ))}
        </div>
      </div>

      {/* Context Menu */}
      <ContextMenu isVisible={contextMenu.isVisible} position={contextMenu.position} selectedPosition={contextMenu.selectedPosition} availablePortfolios={availablePortfolios} onClose={closeContextMenu} onMovePosition={handleMovePosition} />
    </div>
  );
};

export default IndividualPortfolio;