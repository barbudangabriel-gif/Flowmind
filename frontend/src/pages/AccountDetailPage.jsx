import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';

const API = process.env.REACT_APP_BACKEND_URL || '';

/**
 * Generic Account Detail Page
 * Displays account information, balances, positions, and transactions
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

      {/* Balance Cards */}
      {balances && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
          <div className="bg-slate-800 border border-slate-700 rounded-lg p-5">
            <div className="text-xs text-gray-400 uppercase tracking-wide mb-2">Cash Balance</div>
            <div className="text-3xl font-bold text-green-400">
              ${balances.CashBalance?.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
            </div>
            <div className="text-xs text-gray-500 mt-1">Available for trading</div>
          </div>

          <div className="bg-slate-800 border border-slate-700 rounded-lg p-5">
            <div className="text-xs text-gray-400 uppercase tracking-wide mb-2">Buying Power</div>
            <div className="text-3xl font-bold text-blue-400">
              ${balances.BuyingPower?.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
            </div>
            <div className="text-xs text-gray-500 mt-1">Including margin</div>
          </div>

          <div className="bg-slate-800 border border-slate-700 rounded-lg p-5">
            <div className="text-xs text-gray-400 uppercase tracking-wide mb-2">Account Value</div>
            <div className="text-3xl font-bold text-white">
              ${balances.AccountValue?.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
            </div>
            <div className="text-xs text-gray-500 mt-1">Total equity</div>
          </div>

          <div className="bg-slate-800 border border-slate-700 rounded-lg p-5">
            <div className="text-xs text-gray-400 uppercase tracking-wide mb-2">Margin Used</div>
            <div className="text-3xl font-bold text-yellow-400">
              ${balances.MarginUsed?.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
            </div>
            <div className="text-xs text-gray-500 mt-1">
              {((balances.MarginUsed / balances.Equity) * 100).toFixed(1)}% of equity
            </div>
          </div>
        </div>
      )}

      {/* Additional Balance Details */}
      {balances && (
        <div className="bg-slate-800 border border-slate-700 rounded-lg p-6 mb-6">
          <h2 className="text-lg font-bold text-white mb-4">Balance Details</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="flex justify-between items-center py-3 border-b border-slate-700">
              <span className="text-gray-400">Market Value</span>
              <span className="text-white font-semibold">
                ${balances.MarketValue?.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
              </span>
            </div>
            <div className="flex justify-between items-center py-3 border-b border-slate-700">
              <span className="text-gray-400">Equity</span>
              <span className="text-white font-semibold">
                ${balances.Equity?.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
              </span>
            </div>
            <div className="flex justify-between items-center py-3 border-b border-slate-700">
              <span className="text-gray-400">Maintenance Margin</span>
              <span className="text-white font-semibold">
                ${balances.MaintenanceMargin?.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
              </span>
            </div>
            {balances.OptionBuyingPower && (
              <div className="flex justify-between items-center py-3 border-b border-slate-700">
                <span className="text-gray-400">Option Buying Power</span>
                <span className="text-white font-semibold">
                  ${balances.OptionBuyingPower?.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                </span>
              </div>
            )}
            {balances.DayTradingBuyingPower && (
              <div className="flex justify-between items-center py-3 border-b border-slate-700">
                <span className="text-gray-400">Day Trading Buying Power</span>
                <span className="text-white font-semibold">
                  ${balances.DayTradingBuyingPower?.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                </span>
              </div>
            )}
          </div>
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
