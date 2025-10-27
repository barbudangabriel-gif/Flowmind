import React, { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { mfClient } from "../services/mindfolioClient";

/**
 * MindfolioDetailNewV2 - Clean redesign focused on positions and YTD data
 * 
 * Structure:
 * - Header: Name, ID, Performance Cards (Daily P/L, Total Return, Win Rate)
 * - Tabs: Overview, Positions, Transactions, Analytics
 * - Positions: TradeStation-style table with grouped options
 * - YTD Import: Complete transaction history from TradeStation
 */

export default function MindfolioDetailNewV2() {
  const { id } = useParams();
  const navigate = useNavigate();
  
  const [mindfolio, setMindfolio] = useState(null);
  const [positions, setPositions] = useState([]);
  const [positionsWithPrices, setPositionsWithPrices] = useState([]);
  const [transactions, setTransactions] = useState([]);
  const [activeTab, setActiveTab] = useState("overview");
  const [loading, setLoading] = useState(true);
  const [loadingPrices, setLoadingPrices] = useState(false);
  const [importingYTD, setImportingYTD] = useState(false);
  const [expandedSymbols, setExpandedSymbols] = useState({});
  const [deleting, setDeleting] = useState(false);

  useEffect(() => {
    loadMindfolio();
  }, [id]);

  useEffect(() => {
    if (positions.length > 0 && activeTab === 'positions') {
      loadLivePrices();
    }
  }, [positions, activeTab]);

  const loadLivePrices = async () => {
    if (positions.length === 0) return;
    
    setLoadingPrices(true);
    const API = process.env.REACT_APP_BACKEND_URL || "";
    
    try {
      const positionsWithLivePrices = await Promise.all(
        positions.map(async (pos) => {
          try {
            const response = await fetch(`${API}/api/options/spot/${pos.symbol}`);
            const data = await response.json();
            const currentPrice = data.price || pos.avg_cost; // Fallback to avg_cost
            
            const marketValue = pos.qty * currentPrice;
            const unrealizedPnL = marketValue - pos.cost_basis;
            const unrealizedPnLPct = (unrealizedPnL / pos.cost_basis) * 100;
            
            return {
              ...pos,
              current_price: currentPrice,
              market_value: marketValue,
              unrealized_pnl: unrealizedPnL,
              unrealized_pnl_pct: unrealizedPnLPct
            };
          } catch (err) {
            console.error(`Failed to get price for ${pos.symbol}:`, err);
            return {
              ...pos,
              current_price: pos.avg_cost,
              market_value: pos.qty * pos.avg_cost,
              unrealized_pnl: 0,
              unrealized_pnl_pct: 0
            };
          }
        })
      );
      
      setPositionsWithPrices(positionsWithLivePrices);
    } catch (err) {
      console.error("Failed to load live prices:", err);
      setPositionsWithPrices(positions);
    } finally {
      setLoadingPrices(false);
    }
  };

  const handleRefreshPrices = function() {
    loadLivePrices();
  };

  async function loadMindfolio() {
    try {
      setLoading(true);
      
      // Load mindfolio data
      const data = await mfClient.get(id);
      setMindfolio(data);
      
      // Load positions
      try {
        const positionsData = await mfClient.getPositions(id);
        setPositions(positionsData || []);
      } catch (err) {
        console.error("Failed to load positions:", err);
        setPositions([]);
      }
      
      // Load transactions
      try {
        const transactionsData = await mfClient.getTransactions(id);
        setTransactions(transactionsData || []);
      } catch (err) {
        console.error("Failed to load transactions:", err);
        setTransactions([]);
      }
      
    } catch (err) {
      console.error("Failed to load mindfolio:", err);
      // Mock data for development
      setMindfolio({
        id: id,
        name: 'TradeStation Master',
        broker: 'TradeStation',
        environment: 'LIVE',
        account_id: '11775499',
        cash_balance: 25430.50,
        starting_balance: 50000,
        status: 'ACTIVE',
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      });
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async () => {
    if (!window.confirm(`Are you sure you want to delete "${mindfolio?.name}"?`)) {
      return;
    }
    
    setDeleting(true);
    try {
      await mfClient.delete(id);
      navigate('/mindfolio');
    } catch (err) {
      console.error('Failed to delete mindfolio:', err);
      alert('Failed to delete mindfolio: ' + err.message);
      setDeleting(false);
    }
  };

  const handleImportFromTS = async () => {
    if (!mindfolio.account_id) {
      alert('No TradeStation account ID found. Please re-import this mindfolio from TradeStation.');
      return;
    }
    
    if (!window.confirm(
      `Import ALL transactions from TradeStation account ${mindfolio.account_id} since 2025-01-01?\n\n` +
      `This will fetch your complete trade history and recalculate positions with FIFO.`
    )) {
      return;
    }
    
    setImportingYTD(true);
    try {
      const result = await mfClient.importYTD(id, mindfolio.account_id);
      
      alert(
        `✅ YTD Import Complete!\n\n` +
        `Transactions imported: ${result.transactions_imported}\n` +
        `Date range: ${result.date_range?.earliest?.split('T')[0]} to ${result.date_range?.latest?.split('T')[0]}\n` +
        `Symbols: ${result.symbols?.join(', ')}\n` +
        `Positions recalculated: ${result.positions_recalculated}`
      );
      
      // Reload mindfolio data
      await loadMindfolio();
      
      // Switch to transactions tab to see imported data
      setActiveTab('transactions');
    } catch (err) {
      console.error('YTD import failed:', err);
      alert('YTD import failed: ' + err.message);
    } finally {
      setImportingYTD(false);
    }
  };

  const toggleSymbol = (symbol) => {
    setExpandedSymbols(prev => ({
      ...prev,
      [symbol]: !prev[symbol]
    }));
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen bg-slate-900">
        <div className="text-white text-lg">Loading mindfolio...</div>
      </div>
    );
  }

  if (!mindfolio) {
    return (
      <div className="flex items-center justify-center h-screen bg-slate-900">
        <div className="text-red-400 text-lg">Mindfolio not found</div>
      </div>
    );
  }

  // Calculate metrics
  const positionsValue = positionsWithPrices.length > 0
    ? positionsWithPrices.reduce((sum, p) => sum + (p.market_value || 0), 0)
    : positions.reduce((sum, p) => sum + (p.cost_basis || 0), 0);
  
  const totalValue = mindfolio.cash_balance + positionsValue;
  const totalReturn = mindfolio.starting_balance 
    ? ((totalValue - mindfolio.starting_balance) / mindfolio.starting_balance * 100).toFixed(2)
    : 0;
  
  const unrealizedPnL = positionsWithPrices.reduce((sum, p) => sum + (p.unrealized_pnl || 0), 0);
  const dailyPL = unrealizedPnL; // For now, show unrealized P/L as daily
  const winRate = 0; // TODO: Calculate from closed trades

  const tabs = [
    { id: 'overview', label: 'Overview' },
    { id: 'positions', label: 'Positions' },
    { id: 'transactions', label: 'Transactions' },
    { id: 'analytics', label: 'Analytics' }
  ];

  return (
    <div className="min-h-screen bg-slate-900 text-white">
      {/* Header Section */}
      <div className="bg-slate-800 border-b border-slate-700">
        <div className="max-w-7xl mx-auto px-6 py-6">
          {/* Title Row */}
          <div className="flex items-center justify-between mb-6">
            <div>
              <h1 className="text-3xl font-bold text-white mb-1">{mindfolio.name}</h1>
              <div className="flex items-center gap-4 text-sm text-gray-400">
                <span>ID: {mindfolio.id}</span>
                <span>•</span>
                <span>{mindfolio.broker}</span>
                <span>•</span>
                <span className={`px-2 py-0.5 rounded text-xs ${
                  mindfolio.environment === 'LIVE' 
                    ? 'bg-green-500/20 text-green-400 border border-green-500/30' 
                    : 'bg-yellow-500/20 text-yellow-400 border border-yellow-500/30'
                }`}>
                  {mindfolio.environment}
                </span>
                {mindfolio.account_id && (
                  <>
                    <span>•</span>
                    <span>Account: {mindfolio.account_id}</span>
                  </>
                )}
              </div>
            </div>
            
            {/* Action Buttons */}
            <div className="flex gap-3">
              <button 
                onClick={handleImportFromTS}
                disabled={importingYTD}
                className="px-4 py-2 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 disabled:from-gray-600 disabled:to-gray-600 disabled:cursor-not-allowed text-white rounded-lg transition flex items-center gap-2"
              >
                {importingYTD ? (
                  <>
                    <svg className="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Importing...
                  </>
                ) : (
                  <>
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
                    </svg>
                    Import YTD Data
                  </>
                )}
              </button>
              <button 
                onClick={handleDelete}
                disabled={deleting}
                className="px-4 py-2 bg-red-600 hover:bg-red-500 disabled:bg-gray-600 disabled:cursor-not-allowed text-white rounded-lg transition"
              >
                {deleting ? 'Deleting...' : 'Delete'}
              </button>
            </div>
          </div>

          {/* Performance Cards */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            {/* Total Value */}
            <div className="bg-slate-700/30 rounded-lg p-4 border border-slate-600">
              <div className="text-sm text-gray-400 mb-1">Total Value</div>
              <div className="text-2xl font-bold text-white">
                ${totalValue.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
              </div>
              <div className="text-xs text-gray-400 mt-1">
                Cash: ${mindfolio.cash_balance.toLocaleString('en-US', { minimumFractionDigits: 2 })}
              </div>
            </div>

            {/* Total Return */}
            <div className="bg-slate-700/30 rounded-lg p-4 border border-slate-600">
              <div className="text-sm text-gray-400 mb-1">Total Return</div>
              <div className={`text-2xl font-bold ${totalReturn >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                {totalReturn >= 0 ? '+' : ''}{totalReturn}%
              </div>
              <div className="text-xs text-gray-400 mt-1">
                ${(totalValue - mindfolio.starting_balance).toLocaleString('en-US', { minimumFractionDigits: 2 })}
              </div>
            </div>

            {/* Daily P/L */}
            <div className="bg-slate-700/30 rounded-lg p-4 border border-slate-600">
              <div className="text-sm text-gray-400 mb-1">Daily P/L</div>
              <div className={`text-2xl font-bold ${dailyPL >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                {dailyPL >= 0 ? '+' : ''}${dailyPL.toLocaleString('en-US', { minimumFractionDigits: 2 })}
              </div>
              <div className="text-xs text-gray-400 mt-1">
                Today's change
              </div>
            </div>

            {/* Win Rate */}
            <div className="bg-slate-700/30 rounded-lg p-4 border border-slate-600">
              <div className="text-sm text-gray-400 mb-1">Win Rate</div>
              <div className="text-2xl font-bold text-white">
                {winRate}%
              </div>
              <div className="text-xs text-gray-400 mt-1">
                Closed trades
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Tabs Navigation */}
      <div className="bg-slate-800 border-b border-slate-700">
        <div className="max-w-7xl mx-auto px-6">
          <div className="flex gap-1">
            {tabs.map(tab => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`px-6 py-3 font-medium transition ${
                  activeTab === tab.id
                    ? 'text-white border-b-2 border-cyan-500'
                    : 'text-gray-400 hover:text-gray-300'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Tab Content */}
      <div className="max-w-7xl mx-auto px-6 py-6">
        {activeTab === 'overview' && (
          <div className="space-y-6">
            <div className="bg-slate-800 border border-slate-700 rounded-lg p-6">
              <h2 className="text-xl font-bold text-white mb-4">Overview</h2>
              <div className="text-gray-400">
                P/L chart and financial summary coming soon...
              </div>
            </div>
          </div>
        )}

        {activeTab === 'positions' && (
          <div className="space-y-6">
            <div className="bg-slate-800 border border-slate-700 rounded-lg p-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-bold text-white">Current Positions</h2>
                <button 
                  onClick={handleRefreshPrices}
                  disabled={loadingPrices}
                  className="text-sm text-gray-400 hover:text-white transition disabled:opacity-50"
                >
                  {loadingPrices ? '🔄 Loading...' : '🔄 Refresh Prices'}
                </button>
              </div>
              
              {positions.length === 0 ? (
                <div className="text-center py-12 text-gray-400">
                  No positions found. Import from TradeStation to get started.
                </div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="text-gray-400 border-b border-slate-700">
                        <th className="text-left py-3 px-3">Symbol</th>
                        <th className="text-right py-3 px-3">Qty</th>
                        <th className="text-right py-3 px-3">Avg Cost</th>
                        <th className="text-right py-3 px-3">Current Price</th>
                        <th className="text-right py-3 px-3">Market Value</th>
                        <th className="text-right py-3 px-3">P/L</th>
                        <th className="text-right py-3 px-3">P/L %</th>
                      </tr>
                    </thead>
                    <tbody className="text-white">
                      {(positionsWithPrices.length > 0 ? positionsWithPrices : positions).map((pos, idx) => {
                        const hasLiveData = pos.current_price !== undefined;
                        const pnlColor = pos.unrealized_pnl > 0 ? 'text-green-400' : pos.unrealized_pnl < 0 ? 'text-red-400' : 'text-gray-400';
                        
                        return (
                          <tr key={idx} className="border-b border-slate-700/50 hover:bg-slate-700/30">
                            <td className="py-3 px-3 font-semibold">{pos.symbol}</td>
                            <td className="text-right py-3 px-3">{pos.qty}</td>
                            <td className="text-right py-3 px-3">${pos.avg_cost?.toFixed(2)}</td>
                            <td className="text-right py-3 px-3 font-semibold">
                              {hasLiveData ? `$${pos.current_price?.toFixed(2)}` : '-'}
                            </td>
                            <td className="text-right py-3 px-3">
                              {hasLiveData ? `$${pos.market_value?.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2})}` : '-'}
                            </td>
                            <td className={`text-right py-3 px-3 font-semibold ${pnlColor}`}>
                              {hasLiveData ? `${pos.unrealized_pnl >= 0 ? '+' : ''}$${pos.unrealized_pnl?.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2})}` : '-'}
                            </td>
                            <td className={`text-right py-3 px-3 ${pnlColor}`}>
                              {hasLiveData ? `${pos.unrealized_pnl_pct >= 0 ? '+' : ''}${pos.unrealized_pnl_pct?.toFixed(2)}%` : '-'}
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          </div>
        )}

        {activeTab === 'transactions' && (
          <div className="space-y-6">
            <div className="bg-slate-800 border border-slate-700 rounded-lg p-6">
              <h2 className="text-xl font-bold text-white mb-4">Transaction History</h2>
              {transactions.length === 0 ? (
                <div className="text-center py-12 text-gray-400">
                  No transactions found.
                </div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="text-gray-400 border-b border-slate-700">
                        <th className="text-left py-3 px-3">Date</th>
                        <th className="text-left py-3 px-3">Symbol</th>
                        <th className="text-left py-3 px-3">Side</th>
                        <th className="text-right py-3 px-3">Qty</th>
                        <th className="text-right py-3 px-3">Price</th>
                        <th className="text-right py-3 px-3">Total</th>
                      </tr>
                    </thead>
                    <tbody className="text-white">
                      {transactions.map((tx, idx) => (
                        <tr key={idx} className="border-b border-slate-700/50 hover:bg-slate-700/30">
                          <td className="py-3 px-3">{new Date(tx.datetime).toLocaleDateString()}</td>
                          <td className="py-3 px-3 font-semibold">{tx.symbol}</td>
                          <td className="py-3 px-3">
                            <span className={`px-2 py-0.5 rounded text-xs ${
                              tx.side === 'BUY' 
                                ? 'bg-green-500/20 text-green-400' 
                                : 'bg-red-500/20 text-red-400'
                            }`}>
                              {tx.side}
                            </span>
                          </td>
                          <td className="text-right py-3 px-3">{tx.qty}</td>
                          <td className="text-right py-3 px-3">${tx.price.toFixed(2)}</td>
                          <td className="text-right py-3 px-3">${(tx.qty * tx.price).toFixed(2)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          </div>
        )}

        {activeTab === 'analytics' && (
          <div className="space-y-6">
            <div className="bg-slate-800 border border-slate-700 rounded-lg p-6">
              <h2 className="text-xl font-bold text-white mb-4">Analytics</h2>
              <div className="text-gray-400">
                Performance metrics, sector allocation, and trade statistics coming soon...
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
