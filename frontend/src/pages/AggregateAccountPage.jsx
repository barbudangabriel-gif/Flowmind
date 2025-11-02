import React, { useState, useEffect } from 'react';

const API = process.env.REACT_APP_BACKEND_URL || '';

/**
 * InfoTooltip Component - Shows info icon with hover tooltip
 */
function InfoTooltip({ text }) {
  const [show, setShow] = useState(false);

  return (
    <div className="relative inline-block ml-2">
      <button
        onMouseEnter={() => setShow(true)}
        onMouseLeave={() => setShow(false)}
        className="w-4 h-4 rounded-full border border-gray-500 text-gray-500 hover:border-gray-400 hover:text-gray-400 flex items-center justify-center text-xs font-semibold transition"
      >
        i
      </button>
      {show && (
        <div className="absolute z-50 left-1/2 transform -translate-x-1/2 bottom-full mb-2 w-64 bg-slate-800 border border-slate-600 rounded-lg p-3 shadow-xl">
          <div className="text-xs text-gray-300 leading-relaxed">{text}</div>
          <div className="absolute top-full left-1/2 transform -translate-x-1/2 -mt-1">
            <div className="border-4 border-transparent border-t-slate-800"></div>
          </div>
        </div>
      )}
    </div>
  );
}

/**
 * Aggregate Account Page
 * Unified view across all brokers (TradeStation, Tastytrade, IBKR)
 * Combines all account types (Equity, Futures, Crypto) into single dashboard
 */
export default function AggregateAccountPage() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [aggregateData, setAggregateData] = useState(null);

  useEffect(() => {
    loadAggregateData();
  }, []);

  const loadAggregateData = async () => {
    setLoading(true);
    setError(null);
    
    try {
      // TODO: Replace with real aggregate endpoint when backend ready
      // For now, fetch all broker accounts and combine
      const brokers = ['tradestation', 'tastytrade', 'ibkr'];
      const allAccounts = [];
      
      for (const broker of brokers) {
        try {
          const response = await fetch(`${API}/api/${broker}/mock/accounts`, {
            headers: { 'X-User-ID': 'default' }
          });
          
          if (response.ok) {
            const data = await response.json();
            const accounts = data.Accounts || [];
            
            // Fetch balances for each account
            for (const account of accounts) {
              const balancesResponse = await fetch(
                `${API}/api/${broker}/mock/accounts/${account.AccountID}/balances`,
                { headers: { 'X-User-ID': 'default' } }
              );
              
              if (balancesResponse.ok) {
                const balancesData = await balancesResponse.json();
                allAccounts.push({
                  broker,
                  account,
                  balances: balancesData.Balances?.[0] || {}
                });
              }
            }
          }
        } catch (err) {
          console.warn(`Failed to load ${broker} accounts:`, err);
        }
      }
      
      // Calculate aggregate totals
      const aggregate = calculateAggregates(allAccounts);
      setAggregateData(aggregate);
      
    } catch (err) {
      console.error('Error loading aggregate data:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const calculateAggregates = (accounts) => {
    let totalPortfolioValue = 0;
    let totalCash = 0;
    let totalStocks = 0;
    let totalOptions = 0;
    let totalFutures = 0;
    let totalShortOptions = 0;
    let totalTodayChangeAmount = 0;
    
    const brokerBreakdown = {
      tradestation: { equity: 0, futures: 0, crypto: 0 },
      tastytrade: { equity: 0, futures: 0, crypto: 0 },
      ibkr: { equity: 0, futures: 0, crypto: 0 }
    };
    
    accounts.forEach(({ broker, account, balances }) => {
      const accountType = account.AccountType?.toLowerCase() || 'equity';
      const accountValue = balances.AccountValue || balances.TotalPortfolioValue || 0;
      
      // Add to broker breakdown
      if (brokerBreakdown[broker] && accountType in brokerBreakdown[broker]) {
        brokerBreakdown[broker][accountType] += accountValue;
      }
      
      // Add to totals
      totalPortfolioValue += accountValue;
      totalCash += balances.CashBalance || 0;
      totalStocks += balances.StocksValue || balances.StocksMarketValue || 0;
      totalOptions += balances.OptionsValue || balances.OptionsMarketValue || 0;
      totalFutures += balances.FuturesBuyingPower || balances.FuturesMarketValue || 0;
      totalShortOptions += balances.ShortOptionsValue || 0;
      
      // Calculate today change (simplified - in production use real WebSocket data)
      if (balances.TotalTodayChangeAmount) {
        totalTodayChangeAmount += balances.TotalTodayChangeAmount;
      }
    });
    
    const totalTodayChangePercent = totalPortfolioValue > 0 
      ? (totalTodayChangeAmount / totalPortfolioValue) * 100 
      : 0;
    
    return {
      totalPortfolioValue,
      totalTodayChangeAmount,
      totalTodayChangePercent,
      totalCash,
      totalStocks,
      totalOptions,
      totalFutures,
      totalShortOptions,
      brokerBreakdown,
      accountCount: accounts.length
    };
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-900 p-6">
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-slate-900 p-6">
        <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-6">
          <div className="flex items-start gap-3">
            <span className="text-lg">❌</span>
            <div>
              <h3 className="text-lg font-semibold text-red-400">Error Loading Aggregate Data</h3>
              <p className="text-red-300 mt-1">{error}</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (!aggregateData) {
    return (
      <div className="min-h-screen bg-slate-900 p-6">
        <div className="bg-slate-800 border border-slate-700 rounded-lg p-8 text-center">
          <div className="text-4xl mb-4">🏦</div>
          <h2 className="text-xl font-bold text-white mb-2">No Accounts Found</h2>
          <p className="text-gray-400">Connect your broker accounts to see aggregate data</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-900 p-6">
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center gap-3 mb-2">
          <span className="text-3xl">🏦</span>
          <div>
            <h1 className="text-2xl font-bold text-white">Aggregate Account View</h1>
            <p className="text-sm text-gray-400">Unified view across all brokers and account types</p>
          </div>
        </div>
      </div>

      {/* Portfolio Overview */}
      <div className="bg-slate-800 border border-slate-700 rounded-lg p-6 mb-6">
        <div className="flex items-center justify-between mb-6">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <h2 className="text-2xl font-bold text-white">Total Portfolio Value</h2>
              <InfoTooltip text="Combined value across all brokers: TradeStation, Tastytrade, and IBKR" />
            </div>
            <div className="text-4xl font-bold text-white">
              ${aggregateData.totalPortfolioValue.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
            </div>
            <div className={`text-lg mt-1 ${aggregateData.totalTodayChangePercent >= 0 ? 'text-green-400' : 'text-red-400'}`}>
              Today: {aggregateData.totalTodayChangePercent >= 0 ? '+' : ''}{aggregateData.totalTodayChangePercent.toFixed(2)}% 
              ({aggregateData.totalTodayChangePercent >= 0 ? '+' : ''}${Math.abs(aggregateData.totalTodayChangeAmount).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })})
            </div>
          </div>
          <div className="text-right">
            <div className="text-sm text-gray-400">Connected Accounts</div>
            <div className="text-3xl font-bold text-blue-400">{aggregateData.accountCount}</div>
          </div>
        </div>

        {/* Market Value Breakdown */}
        <div className="border-t border-slate-700 pt-4">
          <h3 className="text-sm font-semibold text-gray-400 mb-3 uppercase tracking-wide">Asset Allocation</h3>
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
            <div className="bg-slate-900 rounded-lg p-3">
              <div className="text-xs text-blue-400 mb-1">Stocks</div>
              <div className="text-lg font-bold text-white">
                ${aggregateData.totalStocks.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
              </div>
            </div>
            <div className="bg-slate-900 rounded-lg p-3">
              <div className="text-xs text-green-400 mb-1">Cash</div>
              <div className="text-lg font-bold text-white">
                ${aggregateData.totalCash.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
              </div>
            </div>
            <div className="bg-slate-900 rounded-lg p-3">
              <div className="text-xs text-purple-400 mb-1">Options</div>
              <div className="text-lg font-bold text-white">
                ${aggregateData.totalOptions.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
              </div>
            </div>
            <div className="bg-slate-900 rounded-lg p-3">
              <div className="text-xs text-yellow-400 mb-1">Futures</div>
              <div className="text-lg font-bold text-white">
                ${aggregateData.totalFutures.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
              </div>
            </div>
            <div className="bg-slate-900 rounded-lg p-3">
              <div className="text-xs text-red-400 mb-1">Short Options</div>
              <div className="text-lg font-bold text-white">
                {aggregateData.totalShortOptions < 0 ? '−' : ''}${Math.abs(aggregateData.totalShortOptions).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Broker Breakdown */}
      <div className="bg-slate-800 border border-slate-700 rounded-lg p-6 mb-6">
        <h2 className="text-lg font-bold text-white mb-4">Broker Breakdown</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* TradeStation */}
          <div className="bg-slate-900 rounded-lg p-4">
            <div className="flex items-center gap-2 mb-3">
              <span className="text-xl">📊</span>
              <h3 className="text-lg font-semibold text-white">TradeStation</h3>
            </div>
            <div className="space-y-2">
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-400">Equity</span>
                <span className="text-sm font-semibold text-white">
                  ${aggregateData.brokerBreakdown.tradestation.equity.toLocaleString('en-US', { minimumFractionDigits: 2 })}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-400">Futures</span>
                <span className="text-sm font-semibold text-white">
                  ${aggregateData.brokerBreakdown.tradestation.futures.toLocaleString('en-US', { minimumFractionDigits: 2 })}
                </span>
              </div>
            </div>
          </div>

          {/* Tastytrade */}
          <div className="bg-slate-900 rounded-lg p-4">
            <div className="flex items-center gap-2 mb-3">
              <span className="text-xl">🥤</span>
              <h3 className="text-lg font-semibold text-white">Tastytrade</h3>
            </div>
            <div className="space-y-2">
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-400">Equity</span>
                <span className="text-sm font-semibold text-white">
                  ${aggregateData.brokerBreakdown.tastytrade.equity.toLocaleString('en-US', { minimumFractionDigits: 2 })}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-400">Futures</span>
                <span className="text-sm font-semibold text-white">
                  ${aggregateData.brokerBreakdown.tastytrade.futures.toLocaleString('en-US', { minimumFractionDigits: 2 })}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-400">Crypto</span>
                <span className="text-sm font-semibold text-white">
                  ${aggregateData.brokerBreakdown.tastytrade.crypto.toLocaleString('en-US', { minimumFractionDigits: 2 })}
                </span>
              </div>
            </div>
          </div>

          {/* IBKR */}
          <div className="bg-slate-900 rounded-lg p-4">
            <div className="flex items-center gap-2 mb-3">
              <span className="text-xl">🌐</span>
              <h3 className="text-lg font-semibold text-white">IBKR</h3>
            </div>
            <div className="space-y-2">
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-400">Equity</span>
                <span className="text-sm font-semibold text-white">
                  ${aggregateData.brokerBreakdown.ibkr.equity.toLocaleString('en-US', { minimumFractionDigits: 2 })}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-400">Futures</span>
                <span className="text-sm font-semibold text-white">
                  ${aggregateData.brokerBreakdown.ibkr.futures.toLocaleString('en-US', { minimumFractionDigits: 2 })}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Info Card */}
      <div className="bg-blue-500/10 border border-blue-500/30 rounded-lg p-6">
        <div className="flex items-start gap-3">
          <div className="text-2xl">ℹ️</div>
          <div>
            <h3 className="text-lg font-semibold text-blue-400 mb-2">Live Data Coming Soon</h3>
            <p className="text-gray-300 mb-3">
              This aggregate view currently combines mock data from all brokers. When connected to real broker APIs and WebSocket feeds, 
              you'll see live balance updates, real-time P/L, and position changes across all your accounts in one unified dashboard.
            </p>
            <div className="text-sm text-gray-400">
              Connected brokers: TradeStation • Tastytrade • IBKR
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
