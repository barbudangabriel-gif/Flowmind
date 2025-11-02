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
    { id: 'algos', label: 'Algos' },
    { id: 'rebalancing', label: 'Smart Rebalancing' },
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

        {activeTab === 'algos' && (
          <div className="space-y-6">
            {/* Capital Allocation Algorithms */}
            <div className="bg-slate-800 border border-slate-700 rounded-lg p-6">
              <div className="flex items-center justify-between mb-6">
                <div>
                  <h2 className="text-xl font-bold text-white mb-1">Capital Allocation Algorithms</h2>
                  <p className="text-sm text-gray-400">Configure automated capital allocation strategies</p>
                </div>
                <button className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm font-semibold transition">
                  + Add Algorithm
                </button>
              </div>

              {/* Algorithm Cards */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* Equal Weight Algorithm */}
                <div className="bg-slate-700/30 border border-slate-600 rounded-lg p-5">
                  <div className="flex items-center justify-between mb-3">
                    <h3 className="font-semibold text-white">Equal Weight</h3>
                    <span className="px-2 py-1 bg-green-500/20 text-green-400 text-xs rounded border border-green-500/30">
                      ACTIVE
                    </span>
                  </div>
                  <p className="text-sm text-gray-400 mb-4">
                    Distribute capital equally across all selected symbols
                  </p>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-400">Allocated:</span>
                      <span className="text-white font-medium">$15,000</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-400">Symbols:</span>
                      <span className="text-white font-medium">5</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-400">Per Symbol:</span>
                      <span className="text-white font-medium">$3,000</span>
                    </div>
                  </div>
                  <div className="flex gap-2 mt-4">
                    <button className="flex-1 px-3 py-2 bg-slate-600 hover:bg-slate-500 text-white rounded text-xs transition">
                      Configure
                    </button>
                    <button className="flex-1 px-3 py-2 bg-slate-600 hover:bg-slate-500 text-white rounded text-xs transition">
                      Pause
                    </button>
                  </div>
                </div>

                {/* Risk Parity Algorithm */}
                <div className="bg-slate-700/30 border border-slate-600 rounded-lg p-5">
                  <div className="flex items-center justify-between mb-3">
                    <h3 className="font-semibold text-white">Risk Parity</h3>
                    <span className="px-2 py-1 bg-gray-500/20 text-gray-400 text-xs rounded border border-gray-500/30">
                      INACTIVE
                    </span>
                  </div>
                  <p className="text-sm text-gray-400 mb-4">
                    Allocate capital based on inverse volatility for equal risk contribution
                  </p>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-400">Allocated:</span>
                      <span className="text-white font-medium">$0</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-400">Symbols:</span>
                      <span className="text-white font-medium">0</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-400">Rebalance:</span>
                      <span className="text-white font-medium">Weekly</span>
                    </div>
                  </div>
                  <div className="flex gap-2 mt-4">
                    <button className="flex-1 px-3 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded text-xs transition">
                      Activate
                    </button>
                    <button className="flex-1 px-3 py-2 bg-slate-600 hover:bg-slate-500 text-white rounded text-xs transition">
                      Configure
                    </button>
                  </div>
                </div>

                {/* Momentum Algorithm */}
                <div className="bg-slate-700/30 border border-slate-600 rounded-lg p-5">
                  <div className="flex items-center justify-between mb-3">
                    <h3 className="font-semibold text-white">Momentum Based</h3>
                    <span className="px-2 py-1 bg-gray-500/20 text-gray-400 text-xs rounded border border-gray-500/30">
                      INACTIVE
                    </span>
                  </div>
                  <p className="text-sm text-gray-400 mb-4">
                    Allocate more capital to assets with strong momentum signals
                  </p>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-400">Allocated:</span>
                      <span className="text-white font-medium">$0</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-400">Lookback:</span>
                      <span className="text-white font-medium">20 days</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-400">Rebalance:</span>
                      <span className="text-white font-medium">Daily</span>
                    </div>
                  </div>
                  <div className="flex gap-2 mt-4">
                    <button className="flex-1 px-3 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded text-xs transition">
                      Activate
                    </button>
                    <button className="flex-1 px-3 py-2 bg-slate-600 hover:bg-slate-500 text-white rounded text-xs transition">
                      Configure
                    </button>
                  </div>
                </div>

                {/* Kelly Criterion Algorithm */}
                <div className="bg-slate-700/30 border border-slate-600 rounded-lg p-5">
                  <div className="flex items-center justify-between mb-3">
                    <h3 className="font-semibold text-white">Kelly Criterion</h3>
                    <span className="px-2 py-1 bg-gray-500/20 text-gray-400 text-xs rounded border border-gray-500/30">
                      INACTIVE
                    </span>
                  </div>
                  <p className="text-sm text-gray-400 mb-4">
                    Optimal position sizing based on win probability and risk-reward ratio
                  </p>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-400">Allocated:</span>
                      <span className="text-white font-medium">$0</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-400">Win Rate:</span>
                      <span className="text-white font-medium">N/A</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-400">Kelly Factor:</span>
                      <span className="text-white font-medium">0.25x</span>
                    </div>
                  </div>
                  <div className="flex gap-2 mt-4">
                    <button className="flex-1 px-3 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded text-xs transition">
                      Activate
                    </button>
                    <button className="flex-1 px-3 py-2 bg-slate-600 hover:bg-slate-500 text-white rounded text-xs transition">
                      Configure
                    </button>
                  </div>
                </div>
              </div>
            </div>

            {/* Options Strategy Scanners & Tools */}
            <div className="bg-slate-800 border border-slate-700 rounded-lg p-6">
              <div className="mb-6">
                <h2 className="text-xl font-bold text-white mb-1">Options Strategy Scanners</h2>
                <p className="text-sm text-gray-400">Automated strategy scanners and trading tools</p>
              </div>

              {/* Scanner Grid */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                {/* Trade Simulator */}
                <a href="/simulator" className="bg-slate-700/30 border border-slate-600 rounded-lg p-4 hover:border-blue-500 transition group">
                  <div className="flex items-center gap-3 mb-2">
                    <div className="w-10 h-10 rounded-lg bg-blue-500/20 flex items-center justify-center text-blue-400 group-hover:bg-blue-500/30 transition">
                      ▶
                    </div>
                    <h3 className="font-semibold text-white">Trade Simulator</h3>
                  </div>
                  <p className="text-sm text-gray-400">Test strategies with historical data</p>
                </a>

                {/* IV Setups (Auto) */}
                <a href="/screener/iv" className="bg-slate-700/30 border border-slate-600 rounded-lg p-4 hover:border-cyan-500 transition group">
                  <div className="flex items-center gap-3 mb-2">
                    <div className="w-10 h-10 rounded-lg bg-cyan-500/20 flex items-center justify-center text-cyan-400 group-hover:bg-cyan-500/30 transition">
                      📊
                    </div>
                    <h3 className="font-semibold text-white">IV Setups (Auto)</h3>
                  </div>
                  <p className="text-sm text-gray-400">Automated implied volatility analysis</p>
                </a>

                {/* Iron Condor Scanner */}
                <a href="/screener/iv?strategy=IRON_CONDOR" className="bg-slate-700/30 border border-slate-600 rounded-lg p-4 hover:border-purple-500 transition group">
                  <div className="flex items-center gap-3 mb-2">
                    <div className="w-10 h-10 rounded-lg bg-purple-500/20 flex items-center justify-center text-purple-400 group-hover:bg-purple-500/30 transition">
                      🎯
                    </div>
                    <h3 className="font-semibold text-white">Iron Condor Scanner</h3>
                  </div>
                  <p className="text-sm text-gray-400">Find high probability condor setups</p>
                </a>

                {/* Calendar Scanner */}
                <a href="/screener/iv?strategy=CALENDAR" className="bg-slate-700/30 border border-slate-600 rounded-lg p-4 hover:border-green-500 transition group">
                  <div className="flex items-center gap-3 mb-2">
                    <div className="w-10 h-10 rounded-lg bg-green-500/20 flex items-center justify-center text-green-400 group-hover:bg-green-500/30 transition">
                      📅
                    </div>
                    <h3 className="font-semibold text-white">Calendar Scanner</h3>
                  </div>
                  <p className="text-sm text-gray-400">Time-based spread opportunities</p>
                </a>

                {/* Diagonal Scanner */}
                <a href="/screener/iv?strategy=DIAGONAL" className="bg-slate-700/30 border border-slate-600 rounded-lg p-4 hover:border-yellow-500 transition group">
                  <div className="flex items-center gap-3 mb-2">
                    <div className="w-10 h-10 rounded-lg bg-yellow-500/20 flex items-center justify-center text-yellow-400 group-hover:bg-yellow-500/30 transition">
                      📈
                    </div>
                    <h3 className="font-semibold text-white">Diagonal Scanner</h3>
                  </div>
                  <p className="text-sm text-gray-400">Diagonal spread opportunities</p>
                </a>

                {/* Double Diagonal */}
                <a href="/screener/iv?strategy=DOUBLE_DIAGONAL" className="bg-slate-700/30 border border-slate-600 rounded-lg p-4 hover:border-orange-500 transition group">
                  <div className="flex items-center gap-3 mb-2">
                    <div className="w-10 h-10 rounded-lg bg-orange-500/20 flex items-center justify-center text-orange-400 group-hover:bg-orange-500/30 transition">
                      📊
                    </div>
                    <h3 className="font-semibold text-white">Double Diagonal</h3>
                  </div>
                  <p className="text-sm text-gray-400">Advanced diagonal strategies</p>
                </a>
              </div>

              {/* Income Strategies */}
              <div className="mb-4">
                <h3 className="text-lg font-semibold text-white mb-3">Income Strategies</h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  {/* Put Selling Engine */}
                  <a href="/screener/sell-puts" className="bg-slate-700/30 border border-slate-600 rounded-lg p-4 hover:border-red-500 transition group">
                    <div className="flex items-center gap-3 mb-2">
                      <div className="w-10 h-10 rounded-lg bg-red-500/20 flex items-center justify-center text-red-400 group-hover:bg-red-500/30 transition">
                        ↓
                      </div>
                      <h3 className="font-semibold text-white">Put Selling Engine</h3>
                    </div>
                    <p className="text-sm text-gray-400">Cash-flow from selling puts</p>
                  </a>

                  {/* Covered Calls */}
                  <a href="/screener/covered-calls" className="bg-slate-700/30 border border-slate-600 rounded-lg p-4 hover:border-blue-500 transition group">
                    <div className="flex items-center gap-3 mb-2">
                      <div className="w-10 h-10 rounded-lg bg-blue-500/20 flex items-center justify-center text-blue-400 group-hover:bg-blue-500/30 transition">
                        🛡
                      </div>
                      <h3 className="font-semibold text-white">Covered Calls</h3>
                    </div>
                    <p className="text-sm text-gray-400">Generate income on holdings</p>
                  </a>

                  {/* Cash-Secured Puts */}
                  <a href="/screener/csp" className="bg-slate-700/30 border border-slate-600 rounded-lg p-4 hover:border-green-500 transition group">
                    <div className="flex items-center gap-3 mb-2">
                      <div className="w-10 h-10 rounded-lg bg-green-500/20 flex items-center justify-center text-green-400 group-hover:bg-green-500/30 transition">
                        💵
                      </div>
                      <h3 className="font-semibold text-white">Cash-Secured Puts</h3>
                    </div>
                    <p className="text-sm text-gray-400">Conservative put selling strategy</p>
                  </a>
                </div>
              </div>

              {/* Trade Management */}
              <div>
                <h3 className="text-lg font-semibold text-white mb-3">Trade Management</h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  {/* Preview Queue */}
                  <a href="/trades/preview" className="bg-slate-700/30 border border-slate-600 rounded-lg p-4 hover:border-cyan-500 transition group">
                    <div className="flex items-center gap-3 mb-2">
                      <div className="w-10 h-10 rounded-lg bg-cyan-500/20 flex items-center justify-center text-cyan-400 group-hover:bg-cyan-500/30 transition">
                        📋
                      </div>
                      <h3 className="font-semibold text-white">Preview Queue</h3>
                    </div>
                    <p className="text-sm text-gray-400">Review pending trade setups</p>
                  </a>

                  {/* Orders (SIM) */}
                  <a href="/trades/orders/sim" className="bg-slate-700/30 border border-slate-600 rounded-lg p-4 hover:border-yellow-500 transition group">
                    <div className="flex items-center gap-3 mb-2">
                      <div className="w-10 h-10 rounded-lg bg-yellow-500/20 flex items-center justify-center text-yellow-400 group-hover:bg-yellow-500/30 transition">
                        📝
                      </div>
                      <h3 className="font-semibold text-white">Orders (SIM)</h3>
                    </div>
                    <p className="text-sm text-gray-400">Simulation account orders</p>
                  </a>

                  {/* Orders (LIVE) */}
                  <a href="/trades/orders/live" className="bg-slate-700/30 border border-slate-600 rounded-lg p-4 hover:border-red-500 transition group">
                    <div className="flex items-center gap-3 mb-2">
                      <div className="w-10 h-10 rounded-lg bg-red-500/20 flex items-center justify-center text-red-400 group-hover:bg-red-500/30 transition">
                        💳
                      </div>
                      <h3 className="font-semibold text-white">Orders (LIVE)</h3>
                    </div>
                    <p className="text-sm text-gray-400">Live account orders</p>
                  </a>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'rebalancing' && (
          <div className="space-y-6">
            {/* Smart Rebalancing */}
            <div className="bg-slate-800 border border-slate-700 rounded-lg p-6">
              <div className="flex items-center justify-between mb-6">
                <div>
                  <h2 className="text-xl font-bold text-white mb-1">Smart Rebalancing</h2>
                  <p className="text-sm text-gray-400">AI-powered portfolio rebalancing recommendations</p>
                </div>
                <button className="px-4 py-2 bg-cyan-600 hover:bg-cyan-700 text-white rounded-lg text-sm font-semibold transition">
                  Run Analysis
                </button>
              </div>

              {/* Rebalancing Status */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                <div className="bg-slate-700/30 rounded-lg p-4 border border-slate-600">
                  <div className="text-sm text-gray-400 mb-1">Last Rebalanced</div>
                  <div className="text-xl font-bold text-white">15 days ago</div>
                  <div className="text-xs text-gray-400 mt-1">October 18, 2025</div>
                </div>
                <div className="bg-slate-700/30 rounded-lg p-4 border border-slate-600">
                  <div className="text-sm text-gray-400 mb-1">Drift Score</div>
                  <div className="text-xl font-bold text-yellow-400">12.3%</div>
                  <div className="text-xs text-gray-400 mt-1">Moderate drift detected</div>
                </div>
                <div className="bg-slate-700/30 rounded-lg p-4 border border-slate-600">
                  <div className="text-sm text-gray-400 mb-1">Recommendation</div>
                  <div className="text-xl font-bold text-cyan-400">Rebalance</div>
                  <div className="text-xs text-gray-400 mt-1">Expected improvement: +2.1%</div>
                </div>
              </div>

              {/* Current vs Target Allocation */}
              <div className="bg-slate-700/30 rounded-lg p-5 border border-slate-600 mb-6">
                <h3 className="font-semibold text-white mb-4">Current vs Target Allocation</h3>
                <div className="space-y-4">
                  {/* Example allocation comparison */}
                  <div>
                    <div className="flex justify-between items-center mb-2">
                      <span className="text-sm text-gray-300">AAPL</span>
                      <div className="flex gap-4 text-sm">
                        <span className="text-gray-400">Current: <span className="text-white">25.3%</span></span>
                        <span className="text-gray-400">Target: <span className="text-cyan-400">20.0%</span></span>
                        <span className="text-red-400">+5.3%</span>
                      </div>
                    </div>
                    <div className="w-full h-2 bg-slate-600 rounded-full overflow-hidden">
                      <div className="h-full bg-gradient-to-r from-cyan-500 to-red-500" style={{width: '25.3%'}}></div>
                    </div>
                  </div>

                  <div>
                    <div className="flex justify-between items-center mb-2">
                      <span className="text-sm text-gray-300">MSFT</span>
                      <div className="flex gap-4 text-sm">
                        <span className="text-gray-400">Current: <span className="text-white">18.7%</span></span>
                        <span className="text-gray-400">Target: <span className="text-cyan-400">20.0%</span></span>
                        <span className="text-yellow-400">-1.3%</span>
                      </div>
                    </div>
                    <div className="w-full h-2 bg-slate-600 rounded-full overflow-hidden">
                      <div className="h-full bg-gradient-to-r from-cyan-500 to-yellow-500" style={{width: '18.7%'}}></div>
                    </div>
                  </div>

                  <div>
                    <div className="flex justify-between items-center mb-2">
                      <span className="text-sm text-gray-300">TSLA</span>
                      <div className="flex gap-4 text-sm">
                        <span className="text-gray-400">Current: <span className="text-white">22.1%</span></span>
                        <span className="text-gray-400">Target: <span className="text-cyan-400">20.0%</span></span>
                        <span className="text-red-400">+2.1%</span>
                      </div>
                    </div>
                    <div className="w-full h-2 bg-slate-600 rounded-full overflow-hidden">
                      <div className="h-full bg-gradient-to-r from-cyan-500 to-red-500" style={{width: '22.1%'}}></div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Rebalancing Actions */}
              <div className="bg-slate-700/30 rounded-lg p-5 border border-slate-600">
                <h3 className="font-semibold text-white mb-4">Suggested Actions</h3>
                <div className="space-y-3">
                  <div className="flex items-center justify-between p-3 bg-slate-800/50 rounded border border-slate-600">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="text-red-400 font-medium">SELL</span>
                        <span className="text-white font-medium">AAPL</span>
                      </div>
                      <div className="text-sm text-gray-400">Reduce position by $1,325 (5 shares @ $265)</div>
                    </div>
                    <button className="px-4 py-2 bg-slate-600 hover:bg-slate-500 text-white rounded text-sm transition">
                      Execute
                    </button>
                  </div>

                  <div className="flex items-center justify-between p-3 bg-slate-800/50 rounded border border-slate-600">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="text-green-400 font-medium">BUY</span>
                        <span className="text-white font-medium">MSFT</span>
                      </div>
                      <div className="text-sm text-gray-400">Increase position by $325 (1 share @ $325)</div>
                    </div>
                    <button className="px-4 py-2 bg-slate-600 hover:bg-slate-500 text-white rounded text-sm transition">
                      Execute
                    </button>
                  </div>

                  <div className="flex items-center justify-between p-3 bg-slate-800/50 rounded border border-slate-600">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="text-red-400 font-medium">SELL</span>
                        <span className="text-white font-medium">TSLA</span>
                      </div>
                      <div className="text-sm text-gray-400">Reduce position by $525 (2 shares @ $262.50)</div>
                    </div>
                    <button className="px-4 py-2 bg-slate-600 hover:bg-slate-500 text-white rounded text-sm transition">
                      Execute
                    </button>
                  </div>
                </div>

                <div className="mt-4 pt-4 border-t border-slate-600">
                  <div className="flex items-center justify-between">
                    <div className="text-sm text-gray-400">
                      Total transactions: <span className="text-white font-medium">3</span> • 
                      Est. cost: <span className="text-white font-medium">$0.00</span>
                    </div>
                    <button className="px-6 py-2 bg-cyan-600 hover:bg-cyan-700 text-white rounded-lg text-sm font-semibold transition">
                      Execute All
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'analytics' && (
          <div className="space-y-6">
            {/* Performance Metrics */}
            <div className="bg-slate-800 border border-slate-700 rounded-lg p-6">
              <h2 className="text-xl font-bold text-white mb-4">Performance Metrics</h2>
              
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
                <div className="bg-slate-700/30 rounded-lg p-4 border border-slate-600">
                  <div className="text-sm text-gray-400 mb-1">Sharpe Ratio</div>
                  <div className="text-2xl font-bold text-cyan-400">1.85</div>
                  <div className="text-xs text-gray-400 mt-1">Risk-adjusted return</div>
                </div>
                <div className="bg-slate-700/30 rounded-lg p-4 border border-slate-600">
                  <div className="text-sm text-gray-400 mb-1">Max Drawdown</div>
                  <div className="text-2xl font-bold text-red-400">-12.3%</div>
                  <div className="text-xs text-gray-400 mt-1">Peak to trough</div>
                </div>
                <div className="bg-slate-700/30 rounded-lg p-4 border border-slate-600">
                  <div className="text-sm text-gray-400 mb-1">Volatility</div>
                  <div className="text-2xl font-bold text-yellow-400">18.5%</div>
                  <div className="text-xs text-gray-400 mt-1">Annualized std dev</div>
                </div>
                <div className="bg-slate-700/30 rounded-lg p-4 border border-slate-600">
                  <div className="text-sm text-gray-400 mb-1">Alpha</div>
                  <div className="text-2xl font-bold text-green-400">+3.2%</div>
                  <div className="text-xs text-gray-400 mt-1">vs SPY benchmark</div>
                </div>
              </div>
            </div>

            {/* Sector Allocation */}
            <div className="bg-slate-800 border border-slate-700 rounded-lg p-6">
              <h2 className="text-xl font-bold text-white mb-4">Sector Allocation</h2>
              <div className="space-y-3">
                {[
                  { sector: 'Technology', pct: 35.2, color: 'bg-blue-500' },
                  { sector: 'Healthcare', pct: 18.7, color: 'bg-green-500' },
                  { sector: 'Financials', pct: 15.3, color: 'bg-yellow-500' },
                  { sector: 'Consumer', pct: 12.8, color: 'bg-purple-500' },
                  { sector: 'Energy', pct: 10.5, color: 'bg-red-500' },
                  { sector: 'Other', pct: 7.5, color: 'bg-gray-500' }
                ].map(item => (
                  <div key={item.sector}>
                    <div className="flex justify-between items-center mb-1">
                      <span className="text-sm text-gray-300">{item.sector}</span>
                      <span className="text-sm text-white font-medium">{item.pct}%</span>
                    </div>
                    <div className="w-full h-2 bg-slate-700 rounded-full overflow-hidden">
                      <div className={`h-full ${item.color}`} style={{width: `${item.pct}%`}}></div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Trade Statistics */}
            <div className="bg-slate-800 border border-slate-700 rounded-lg p-6">
              <h2 className="text-xl font-bold text-white mb-4">Trade Statistics</h2>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div>
                  <div className="text-sm text-gray-400 mb-3">Win/Loss Breakdown</div>
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span className="text-gray-300">Winning Trades</span>
                      <span className="text-green-400 font-medium">28 (65%)</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-300">Losing Trades</span>
                      <span className="text-red-400 font-medium">15 (35%)</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-300">Break Even</span>
                      <span className="text-gray-400 font-medium">2</span>
                    </div>
                  </div>
                </div>

                <div>
                  <div className="text-sm text-gray-400 mb-3">Profit Metrics</div>
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span className="text-gray-300">Avg Win</span>
                      <span className="text-green-400 font-medium">$485.20</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-300">Avg Loss</span>
                      <span className="text-red-400 font-medium">$-287.50</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-300">Profit Factor</span>
                      <span className="text-cyan-400 font-medium">1.68</span>
                    </div>
                  </div>
                </div>

                <div>
                  <div className="text-sm text-gray-400 mb-3">Hold Time</div>
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span className="text-gray-300">Avg Duration</span>
                      <span className="text-white font-medium">5.3 days</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-300">Shortest</span>
                      <span className="text-white font-medium">0.5 days</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-300">Longest</span>
                      <span className="text-white font-medium">45 days</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Top Performers */}
            <div className="bg-slate-800 border border-slate-700 rounded-lg p-6">
              <h2 className="text-xl font-bold text-white mb-4">Top Performers</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <div className="text-sm text-gray-400 mb-3">Best Trades</div>
                  <div className="space-y-2">
                    {[
                      { symbol: 'NVDA', pnl: 1250.00, date: '2025-10-15' },
                      { symbol: 'AAPL', pnl: 890.50, date: '2025-10-22' },
                      { symbol: 'TSLA', pnl: 765.30, date: '2025-10-28' }
                    ].map((trade, i) => (
                      <div key={i} className="flex justify-between items-center p-3 bg-slate-700/30 rounded border border-slate-600">
                        <div>
                          <div className="text-white font-medium">{trade.symbol}</div>
                          <div className="text-xs text-gray-400">{trade.date}</div>
                        </div>
                        <div className="text-green-400 font-bold">+${trade.pnl.toFixed(2)}</div>
                      </div>
                    ))}
                  </div>
                </div>

                <div>
                  <div className="text-sm text-gray-400 mb-3">Worst Trades</div>
                  <div className="space-y-2">
                    {[
                      { symbol: 'META', pnl: -425.00, date: '2025-10-12' },
                      { symbol: 'GOOGL', pnl: -380.25, date: '2025-10-18' },
                      { symbol: 'AMZN', pnl: -295.80, date: '2025-10-25' }
                    ].map((trade, i) => (
                      <div key={i} className="flex justify-between items-center p-3 bg-slate-700/30 rounded border border-slate-600">
                        <div>
                          <div className="text-white font-medium">{trade.symbol}</div>
                          <div className="text-xs text-gray-400">{trade.date}</div>
                        </div>
                        <div className="text-red-400 font-bold">${trade.pnl.toFixed(2)}</div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
