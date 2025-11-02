import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';

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
 * Generic Account Detail Page
 * Displays account information and balances
 * Works for all brokers (TradeStation, Tastytrade, IBKR) and account types (Equity, Futures, Crypto)
 */
export default function AccountDetailPage() {
  const { broker, accountType } = useParams();
  const [accounts, setAccounts] = useState([]);
  const [selectedAccount, setSelectedAccount] = useState(null);
  const [balances, setBalances] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [equityTab, setEquityTab] = useState('stocks'); // 'stocks' or 'options'

  // Broker display names
  const brokerNames = {
    'tradestation': 'TradeStation',
    'tastytrade': 'Tastytrade',
    'ibkr': 'IBKR'
  };

  // Account type display info
  const accountTypeInfo = {
    'equity': { 
      name: 'Equity (Margin)', 
      icon: '📈',
      color: 'blue',
      description: 'Stock and options trading'
    },
    'futures': { 
      name: 'Futures', 
      icon: '⚡',
      color: 'yellow',
      description: 'Futures and futures options'
    },
    'crypto': { 
      name: 'Crypto', 
      icon: '₿',
      color: 'orange',
      description: 'Cryptocurrency trading'
    }
  };

  // Futures account field definitions with descriptions
  const futuresFields = {
    mainCards: [
      {
        key: 'FuturesBuyingPower',
        label: 'Futures Buying Power',
        color: 'blue',
        tooltip: 'Account equity available to trade futures contracts.'
      },
      {
        key: 'CashBalance',
        label: 'Cash Balance',
        color: 'green',
        tooltip: 'The amount of cash available to invest.'
      },
      {
        key: 'AccountValue',
        label: 'Account Value',
        color: 'white',
        tooltip: 'Total value of the futures account.'
      }
    ],
    metrics: [
      {
        key: 'FuturesPositions',
        label: 'Futures Positions',
        tooltip: 'Number of open futures positions.'
      },
      {
        key: 'RealizedPnL',
        label: 'Realized P/L',
        tooltip: 'Profit or loss from closed positions.'
      },
      {
        key: 'UnrealizedPnL',
        label: 'Unrealized P/L',
        tooltip: 'Profit or loss from open positions.'
      },
      {
        key: 'InitialMargin',
        label: 'Initial Margin',
        tooltip: 'The sum of Initial Margin of all your positions. The initial margin is the amount of funds that must be available to open a position.'
      },
      {
        key: 'MaintenanceMargin',
        label: 'Maintenance Margin',
        tooltip: 'The sum of Maintenance Margins of all your positions. If the account drops below the maintenance margin, the account will receive a margin call.'
      },
      {
        key: 'OpenOrderInitialMargin',
        label: 'Open Order Initial Margin',
        tooltip: 'The sum of Open Order Initial Margins for all your positions. This value is the amount of funds that must be available for all opening orders.'
      },
      {
        key: 'CashAvailableToWithdraw',
        label: 'Cash Available to Withdraw',
        tooltip: 'The total amount of cash available to invest or withdraw in your futures account. This value updates at the end of the day.'
      },
      {
        key: 'PendingUSDDeposits',
        label: 'Pending USD Deposits',
        tooltip: 'Pending USD Deposits are required to clear prior to use. This may take a few business days.'
      },
      {
        key: 'SecuritiesOnDeposit',
        label: 'Securities on Deposit',
        tooltip: 'The value of special securities deposited such as Treasury Bills and other government interest bearing coupons you may have in your account.'
      }
    ]
  };

  // Equity account field definitions with descriptions
  const equityFields = {
    portfolioOverview: [
      {
        key: 'TotalPortfolioValue',
        label: 'Total Portfolio Value',
        tooltip: 'Combined value of all stocks, options, futures, and cash across all accounts.'
      },
      {
        key: 'TotalTodayChange',
        label: 'Today Change',
        tooltip: 'Total change in portfolio value today.'
      }
    ],
    marketValueBreakdown: [
      { key: 'StocksMarketValue', label: 'Stocks', color: 'blue' },
      { key: 'CashValue', label: 'Cash', color: 'green' },
      { key: 'OptionsMarketValue', label: 'Options', color: 'purple' },
      { key: 'FuturesMarketValue', label: 'Futures', color: 'yellow' },
      { key: 'ShortOptionsValue', label: 'Short Options', color: 'red' }
    ],
    mainCards: [
      {
        key: 'AccountValue',
        label: 'Account Value',
        color: 'white',
        tooltip: 'The total value of stocks and options holdings, and cash in your account.'
      },
      {
        key: 'StocksBuyingPower',
        keyAlt: 'OptionsBuyingPower',
        label: 'Buying Power',
        color: 'blue',
        tooltip: {
          stocks: 'The money available to purchase or short sell stocks. Buying power is equal to the total cash held in your account plus funds available to borrow, also referred to as margin.',
          options: 'Options Buying Power is the money available to purchase options. Options are not marginable.'
        }
      },
      {
        key: 'CashBalance',
        label: 'Cash Balance',
        color: 'green',
        tooltip: 'The total cash funds in the account. This may be a negative number if you are borrowing funds, also referred to as margin. A positive Cash Balance may not always be funds that are available to trade, depending on the margin requirements of current positions.'
      },
      {
        key: 'CashAvailableToWithdraw',
        label: 'Cash Available to Withdraw',
        color: 'cyan',
        tooltip: 'The total amount of cash available to invest or withdraw in your stocks and options account. This data updates at the end of the day. Pending USD Deposits and Uncleared Funds are required to clear prior to use. This may take a few business days.'
      }
    ],
    stocksMetrics: [
      {
        key: 'StocksValue',
        label: 'Stocks Value',
        tooltip: 'Total market value of stock positions.'
      },
      {
        key: 'StocksTodayChange',
        label: 'Today Change',
        tooltip: 'Today\'s change in stocks value.'
      },
      {
        key: 'StocksUnrealizedPnL',
        label: 'Unrealized P/L',
        tooltip: 'Profit or loss from open stock positions.'
      },
      {
        key: 'OvernightBuyingPower',
        label: 'Overnight Buying Power',
        tooltip: 'The maximum funds available for holding positions through the pre- and post- market sessions. This may mean that you are borrowing funds, also referred to as margin.'
      },
      {
        key: 'DayTradingBuyingPower',
        label: 'Day Trading Buying Power',
        tooltip: 'The maximum funds available for holding positions during the regular market session. This may mean that you are borrowing funds, also referred to as margin.'
      },
      {
        key: 'DayTradingQualified',
        label: 'Day Trading Qualified',
        tooltip: 'A Day Trade is defined as the opening and closing of a transaction in the same security in a margin account in the same trading day. Pattern Day Traders (PDT) with less than $25,000 will face restrictions on further trading.'
      },
      {
        key: 'PatternDayTrader',
        label: 'Pattern Day Trader',
        tooltip: 'Pattern Day Traders are defined as investors who execute 4 or more day trades over the span of 5 business days in a margin account. The cash amount in the account must be at least $25,000.'
      }
    ],
    optionsMetrics: [
      {
        key: 'OptionsValue',
        label: 'Options Value',
        tooltip: 'Total market value of options positions.'
      },
      {
        key: 'OptionsTodayChange',
        label: 'Today Change',
        tooltip: 'Today\'s change in options value.'
      },
      {
        key: 'OptionsUnrealizedPnL',
        label: 'Unrealized P/L',
        tooltip: 'Profit or loss from open options positions.'
      },
      {
        key: 'OptionsApprovalLevel',
        label: 'Options Approval Level',
        tooltip: 'Your Option Approval Level enables what option strategies you may trade in your account. Level 1: Covered Calls/Puts. Level 2: Buy Calls/Puts. Level 3: Spreads. Level 4: Sell Uncovered Puts. Level 5: Sell Uncovered Calls, Straddles.'
      }
    ]
  };

  const brokerName = brokerNames[broker] || broker;
  const typeInfo = accountTypeInfo[accountType] || { name: accountType, icon: '💼', color: 'gray' };

  useEffect(() => {
    loadAccounts();
  }, [broker, accountType]);

  useEffect(() => {
    if (selectedAccount) {
      loadBalances(selectedAccount.AccountID);
    }
  }, [selectedAccount]);

  const loadAccounts = async () => {
    setLoading(true);
    setError(null);
    try {
      const endpoint = `/api/${broker}/mock/accounts`;
      const response = await fetch(`${API}${endpoint}`, {
        headers: { 'X-User-ID': 'default' }
      });

      if (!response.ok) {
        throw new Error(`Failed to load accounts: ${response.status}`);
      }

      const data = await response.json();
      const filteredAccounts = (data.Accounts || []).filter(
        acc => acc.AccountType.toLowerCase() === accountType
      );

      setAccounts(filteredAccounts);

      // Auto-select first account
      if (filteredAccounts.length > 0) {
        setSelectedAccount(filteredAccounts[0]);
      }
    } catch (err) {
      console.error('Error loading accounts:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const loadBalances = async (accountId) => {
    try {
      const endpoint = `/api/${broker}/mock/accounts/${accountId}/balances`;
      const response = await fetch(`${API}${endpoint}`, {
        headers: { 'X-User-ID': 'default' }
      });

      if (!response.ok) {
        throw new Error(`Failed to load balances: ${response.status}`);
      }

      const data = await response.json();
      setBalances(data.Balances?.[0] || null);
    } catch (err) {
      console.error('Error loading balances:', err);
    }
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
              <h3 className="text-lg font-semibold text-red-400">Error Loading Account</h3>
              <p className="text-red-300 mt-1">{error}</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (accounts.length === 0) {
    return (
      <div className="min-h-screen bg-slate-900 p-6">
        <div className="bg-slate-800 border border-slate-700 rounded-lg p-8 text-center">
          <div className="text-4xl mb-4">{typeInfo.icon}</div>
          <h2 className="text-xl font-bold text-white mb-2">No {typeInfo.name} Accounts Found</h2>
          <p className="text-gray-400">
            No {typeInfo.name} accounts available for {brokerName}
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-900 p-6">
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center gap-3 mb-2">
          <span className="text-3xl">{typeInfo.icon}</span>
          <div>
            <h1 className="text-2xl font-bold text-white">
              {brokerName} - {typeInfo.name}
            </h1>
            <p className="text-sm text-gray-400">{typeInfo.description}</p>
          </div>
        </div>
      </div>

      {/* Account Selector */}
      {accounts.length > 1 && (
        <div className="bg-slate-800 border border-slate-700 rounded-lg p-4 mb-6">
          <label className="block text-sm font-semibold text-gray-300 mb-2">Select Account</label>
          <select
            value={selectedAccount?.AccountID || ''}
            onChange={(e) => {
              const account = accounts.find(a => a.AccountID === e.target.value);
              setSelectedAccount(account);
            }}
            className="w-full bg-slate-900 border border-slate-700 text-white rounded-lg px-4 py-2"
          >
            {accounts.map(account => (
              <option key={account.AccountID} value={account.AccountID}>
                {account.Name || account.AccountID}
              </option>
            ))}
          </select>
        </div>
      )}

      {/* Account Info Card */}
      {selectedAccount && (
        <div className="bg-slate-800 border border-slate-700 rounded-lg p-6 mb-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-bold text-white">Account Information</h2>
            <span className={`px-3 py-1 rounded-lg text-sm font-semibold bg-${typeInfo.color}-500/20 text-${typeInfo.color}-400 border border-${typeInfo.color}-500/30`}>
              {typeInfo.name}
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <div className="text-sm text-gray-400">Account ID</div>
              <div className="text-lg font-semibold text-white">{selectedAccount.AccountID}</div>
            </div>
            <div>
              <div className="text-sm text-gray-400">Account Name</div>
              <div className="text-lg font-semibold text-white">{selectedAccount.Name}</div>
            </div>
            <div>
              <div className="text-sm text-gray-400">Broker</div>
              <div className="text-lg font-semibold text-white">{brokerName}</div>
            </div>
            <div>
              <div className="text-sm text-gray-400">Currency</div>
              <div className="text-lg font-semibold text-white">{selectedAccount.Currency || 'USD'}</div>
            </div>
          </div>
        </div>
      )}

      {/* Balance Cards - Conditional based on account type */}
      {balances && accountType === 'futures' && (
        <>
          {/* Main Cards for Futures */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            {futuresFields.mainCards.map(field => (
              <div key={field.key} className="bg-slate-800 border border-slate-700 rounded-lg p-6">
                <div className="flex items-center mb-3">
                  <div className="text-sm text-gray-400 uppercase tracking-wide">{field.label}</div>
                  <InfoTooltip text={field.tooltip} />
                </div>
                <div className={`text-4xl font-bold text-${field.color}-400`}>
                  {typeof balances[field.key] === 'number' 
                    ? `$${balances[field.key].toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
                    : balances[field.key] || '$0.00'
                  }
                </div>
              </div>
            ))}
          </div>

          {/* Additional Metrics for Futures */}
          <div className="bg-slate-800 border border-slate-700 rounded-lg p-6 mb-6">
            <h2 className="text-lg font-bold text-white mb-4">Account Metrics</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {futuresFields.metrics.map(field => (
                <div key={field.key} className="bg-slate-900 rounded-lg p-4">
                  <div className="flex items-center mb-2">
                    <span className="text-sm text-gray-400">{field.label}</span>
                    <InfoTooltip text={field.tooltip} />
                  </div>
                  <div className="text-xl font-bold text-white">
                    {field.key === 'FuturesPositions'
                      ? (balances[field.key] || 0)
                      : typeof balances[field.key] === 'number'
                      ? `$${balances[field.key].toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
                      : balances[field.key] || '$0.00'
                    }
                  </div>
                </div>
              ))}
            </div>
          </div>
        </>
      )}

      {/* Equity Account Type - Placeholder for now */}
      {balances && accountType === 'equity' && (
        <>
          {/* Portfolio Overview Section */}
          <div className="bg-slate-800 border border-slate-700 rounded-lg p-6 mb-6">
            <div className="flex items-center justify-between mb-6">
              <div>
                <div className="flex items-center gap-2 mb-1">
                  <h2 className="text-2xl font-bold text-white">Total Portfolio Value</h2>
                  <InfoTooltip text="Combined value of all stocks, options, futures, and cash across all accounts." />
                </div>
                <div className="text-4xl font-bold text-white">
                  ${balances.TotalPortfolioValue?.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) || '0.00'}
                </div>
                <div className={`text-lg mt-1 ${balances.TotalTodayChangePercent >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                  Today: {balances.TotalTodayChangePercent >= 0 ? '+' : ''}{balances.TotalTodayChangePercent}% 
                  ({balances.TotalTodayChangePercent >= 0 ? '+' : ''}${Math.abs(balances.TotalTodayChangeAmount || 0).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })})
                </div>
              </div>
            </div>

            {/* Market Value Breakdown */}
            <div className="border-t border-slate-700 pt-4">
              <h3 className="text-sm font-semibold text-gray-400 mb-3 uppercase tracking-wide">Market Value Breakdown</h3>
              <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
                {equityFields.marketValueBreakdown.map(item => (
                  <div key={item.key} className="bg-slate-900 rounded-lg p-3">
                    <div className={`text-xs text-${item.color}-400 mb-1`}>{item.label}</div>
                    <div className="text-lg font-bold text-white">
                      {balances[item.key] < 0 ? '−' : ''}${Math.abs(balances[item.key] || 0).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Account Summaries */}
            <div className="border-t border-slate-700 pt-4 mt-4">
              <h3 className="text-sm font-semibold text-gray-400 mb-3 uppercase tracking-wide">Account Summaries</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                <div className="bg-slate-900 rounded-lg p-4 flex items-center justify-between">
                  <div>
                    <div className="text-sm text-gray-400">Stocks • Options</div>
                    <div className="text-xl font-bold text-white">
                      ${balances.StocksOptionsAccountValue?.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) || '0.00'}
                    </div>
                  </div>
                  <div className={`text-sm ${balances.StocksOptionsTodayPercent >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                    Today: {balances.StocksOptionsTodayPercent >= 0 ? '+' : ''}{balances.StocksOptionsTodayPercent}%
                  </div>
                </div>
                <div className="bg-slate-900 rounded-lg p-4 flex items-center justify-between">
                  <div>
                    <div className="text-sm text-gray-400">Futures</div>
                    <div className="text-xl font-bold text-white">
                      ${balances.FuturesAccountValue?.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) || '0.00'}
                    </div>
                  </div>
                  <div className={`text-sm ${balances.FuturesTodayPercent >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                    Today: {balances.FuturesTodayPercent >= 0 ? '+' : ''}{balances.FuturesTodayPercent}%
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Main Cards for Equity */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
            {equityFields.mainCards.map(field => {
              const displayKey = equityTab === 'options' && field.keyAlt ? field.keyAlt : field.key;
              const tooltip = typeof field.tooltip === 'object' 
                ? field.tooltip[equityTab] 
                : field.tooltip;
              
              return (
                <div key={field.key} className="bg-slate-800 border border-slate-700 rounded-lg p-6">
                  <div className="flex items-center mb-3">
                    <div className="text-sm text-gray-400 uppercase tracking-wide">
                      {equityTab === 'stocks' && field.label === 'Buying Power' ? 'Stocks Buying Power' : 
                       equityTab === 'options' && field.label === 'Buying Power' ? 'Options Buying Power' : 
                       field.label}
                    </div>
                    <InfoTooltip text={tooltip} />
                  </div>
                  <div className={`text-4xl font-bold text-${field.color}-400`}>
                    {typeof balances[displayKey] === 'number' 
                      ? `$${balances[displayKey].toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
                      : balances[displayKey] || '$0.00'
                    }
                  </div>
                </div>
              );
            })}
          </div>

          {/* Tab Switcher for Equity */}
          <div className="bg-slate-800 border border-slate-700 rounded-lg p-6 mb-6">
            <div className="flex items-center gap-4 mb-6">
              <button
                onClick={() => setEquityTab('stocks')}
                className={`px-6 py-2 rounded-lg font-semibold transition ${
                  equityTab === 'stocks'
                    ? 'bg-blue-600 text-white'
                    : 'bg-slate-700 text-gray-400 hover:bg-slate-600'
                }`}
              >
                Stocks
              </button>
              <button
                onClick={() => setEquityTab('options')}
                className={`px-6 py-2 rounded-lg font-semibold transition ${
                  equityTab === 'options'
                    ? 'bg-blue-600 text-white'
                    : 'bg-slate-700 text-gray-400 hover:bg-slate-600'
                }`}
              >
                Options
              </button>
            </div>

            {/* Stocks Tab Content */}
            {equityTab === 'stocks' && (
              <div>
                <h2 className="text-lg font-bold text-white mb-4">Stocks Metrics</h2>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {equityFields.stocksMetrics.map(field => (
                    <div key={field.key} className="bg-slate-900 rounded-lg p-4">
                      <div className="flex items-center mb-2">
                        <span className="text-sm text-gray-400">{field.label}</span>
                        <InfoTooltip text={field.tooltip} />
                      </div>
                      <div className="text-xl font-bold text-white">
                        {field.key === 'DayTradingQualified' || field.key === 'PatternDayTrader'
                          ? balances[field.key] ? 'Yes' : 'No'
                          : typeof balances[field.key] === 'number'
                          ? `$${balances[field.key].toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
                          : balances[field.key] || 'N/A'
                        }
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Options Tab Content */}
            {equityTab === 'options' && (
              <div>
                <h2 className="text-lg font-bold text-white mb-4">Options Metrics</h2>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {equityFields.optionsMetrics.map(field => (
                    <div key={field.key} className="bg-slate-900 rounded-lg p-4">
                      <div className="flex items-center mb-2">
                        <span className="text-sm text-gray-400">{field.label}</span>
                        <InfoTooltip text={field.tooltip} />
                      </div>
                      <div className="text-xl font-bold text-white">
                        {field.key === 'OptionsApprovalLevel'
                          ? `Level ${balances[field.key] || 0}`
                          : typeof balances[field.key] === 'number'
                          ? `$${balances[field.key].toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
                          : balances[field.key] || 'N/A'
                        }
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </>
      )}

      {/* Crypto Account Type - Placeholder for now */}
      {balances && accountType === 'crypto' && (
        <div className="bg-slate-800 border border-slate-700 rounded-lg p-8 mb-6 text-center">
          <div className="text-4xl mb-4">₿</div>
          <h2 className="text-xl font-bold text-white mb-2">Crypto Account Structure Coming Soon</h2>
          <p className="text-gray-400">Waiting for field definitions...</p>
        </div>
      )}

      {/* Info Card */}
      <div className="bg-blue-500/10 border border-blue-500/30 rounded-lg p-6">
        <div className="flex items-start gap-3">
          <div className="text-2xl">ℹ️</div>
          <div>
            <h3 className="text-lg font-semibold text-blue-400 mb-2">Positions & Transactions</h3>
            <p className="text-gray-300 mb-3">
              To view and manage your positions and transaction history, create or open a Mindfolio linked to this account.
            </p>
            <a 
              href="/mindfolio" 
              className="inline-block px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm font-semibold transition"
            >
              Go to Mindfolios →
            </a>
          </div>
        </div>
      </div>
    </div>
  );
}
