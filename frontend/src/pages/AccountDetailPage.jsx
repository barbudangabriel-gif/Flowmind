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
        <div className="bg-slate-800 border border-slate-700 rounded-lg p-8 mb-6 text-center">
          <div className="text-4xl mb-4">📈</div>
          <h2 className="text-xl font-bold text-white mb-2">Equity Account Structure Coming Soon</h2>
          <p className="text-gray-400">Waiting for field definitions...</p>
        </div>
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
