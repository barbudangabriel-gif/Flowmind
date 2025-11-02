import React, { useState, useEffect } from 'react';

const API = process.env.REACT_APP_BACKEND_URL || '';

export default function MindfolioTemplateModal({ isOpen, onClose, onCreateFromTemplate }) {
  const [accounts, setAccounts] = useState([]);
  const [accountBalances, setAccountBalances] = useState(null);
  const [selectedBroker, setSelectedBroker] = useState('');
  const [selectedAccountType, setSelectedAccountType] = useState('Equity');
  const [selectedAccount, setSelectedAccount] = useState(null);
  const [mindfolioType, setMindfolioType] = useState('day_trading');
  const [mindfolioName, setMindfolioName] = useState('Day Trading');
  const [manualBalance, setManualBalance] = useState(10000);
  const [creating, setCreating] = useState(false);

  const mindfolioTypes = {
    'day_trading': { name: 'Day Trading', risk: 'HIGH' },
    'options_selling': { name: 'Options Selling', risk: 'MEDIUM' },
    'swing_trading': { name: 'Swing Trading', risk: 'MEDIUM' },
    'longterm': { name: 'Long-term Investing', risk: 'LOW' }
  };

  const brokerConfigs = {
    'TradeStation': {
      accountTypes: ['Equity', 'Futures'],
      endpoint: '/api/tradestation/mock/accounts'
    },
    'Tastytrade': {
      accountTypes: ['Equity', 'Futures', 'Crypto'],
      endpoint: '/api/tastytrade/mock/accounts'
    }
  };

  // Auto-populate name when type changes
  useEffect(() => {
    setMindfolioName(mindfolioTypes[mindfolioType].name);
  }, [mindfolioType]);

  useEffect(() => {
    if (selectedBroker) {
      fetchAccounts(selectedBroker);
    } else {
      setAccounts([]);
      setSelectedAccount(null);
    }
  }, [selectedBroker]);

  useEffect(() => {
    if (selectedAccount && selectedBroker) {
      fetchAccountBalances(selectedBroker, selectedAccount.AccountID);
    } else {
      setAccountBalances(null);
    }
  }, [selectedAccount, selectedBroker]);

  const fetchAccounts = async (broker) => {
    const config = brokerConfigs[broker];
    try {
      const response = await fetch(`${API}${config.endpoint}`, {
        headers: { 'X-User-ID': 'default' }
      });
      if (response.ok) {
        const data = await response.json();
        setAccounts(data.Accounts || []);
      }
    } catch (error) {
      console.error(`Failed to fetch ${broker} accounts:`, error);
      setAccounts([]);
    }
  };

  const fetchAccountBalances = async (broker, accountId) => {
    try {
      const endpoint = `/api/${broker.toLowerCase()}/mock/accounts/${accountId}/balances`;
      const response = await fetch(`${API}${endpoint}`, {
        headers: { 'X-User-ID': 'default' }
      });
      if (response.ok) {
        const data = await response.json();
        setAccountBalances(data.Balances?.[0] || null);
      }
    } catch (error) {
      console.error('Failed to fetch balances:', error);
      setAccountBalances(null);
    }
  };

  const handleCreate = async () => {
    if (!mindfolioName.trim()) {
      alert('Please enter a mindfolio name');
      return;
    }

    const finalBalance = selectedAccount 
      ? parseFloat(selectedAccount.CashBalance || 0)
      : manualBalance;

    setCreating(true);
    try {
      await onCreateFromTemplate({
        name: mindfolioName,
        type: mindfolioType,
        starting_balance: finalBalance,
        modules: [],
        account_id: selectedAccount?.AccountID || null,
        account_type: selectedAccountType,
        broker: selectedBroker || null,
      });
      onClose();
      setSelectedBroker('');
      setSelectedAccountType('Equity');
      setSelectedAccount(null);
      setMindfolioType('day_trading');
      setMindfolioName('');
      setManualBalance(10000);
    } catch (error) {
      console.error('Failed to create mindfolio:', error);
      alert('Failed to create mindfolio: ' + error.message);
    } finally {
      setCreating(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-4">
      <div className="bg-slate-900 border border-slate-700 rounded-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div className="bg-slate-900 border-b border-slate-700 p-6 flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold text-white mb-1">Create Mindfolio</h2>
            <p className="text-sm text-gray-400">Configure your trading account</p>
          </div>
          <button onClick={onClose} className="text-gray-400 hover:text-white transition-colors text-2xl">
            ✕
          </button>
        </div>

        <div className="p-6 space-y-6">
          <div>
            <label className="block text-sm font-semibold text-gray-300 mb-2">Mindfolio Type</label>
            <select value={mindfolioType} onChange={(e) => setMindfolioType(e.target.value)} className="w-full bg-slate-900 border border-slate-700 text-white rounded-lg px-4 py-3">
              {Object.keys(mindfolioTypes).map(key => (
                <option key={key} value={key}>{mindfolioTypes[key].name} ({mindfolioTypes[key].risk} RISK)</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-semibold text-gray-300 mb-2">Mindfolio Name</label>
            <input 
              type="text" 
              value={mindfolioName} 
              onChange={(e) => setMindfolioName(e.target.value)} 
              className="w-full bg-slate-900 border border-slate-700 text-white rounded-lg px-4 py-3" 
            />
          </div>

          <div>
            <label className="block text-sm font-semibold text-gray-300 mb-2">Broker (Optional)</label>
            <select value={selectedBroker} onChange={(e) => { setSelectedBroker(e.target.value); setSelectedAccount(null); setSelectedAccountType('Equity'); }} className="w-full bg-slate-900 border border-slate-700 text-white rounded-lg px-4 py-3">
              <option value="">Manual (no broker)</option>
              {Object.keys(brokerConfigs).map(broker => (
                <option key={broker} value={broker}>{broker}</option>
              ))}
            </select>
          </div>

          {selectedBroker && (
            <div>
              <label className="block text-sm font-semibold text-gray-300 mb-2">Account Type</label>
              <select value={selectedAccountType} onChange={(e) => { setSelectedAccountType(e.target.value); setSelectedAccount(null); }} className="w-full bg-slate-900 border border-slate-700 text-white rounded-lg px-4 py-3">
                {brokerConfigs[selectedBroker].accountTypes.map(type => (
                  <option key={type} value={type}>{type}</option>
                ))}
              </select>
              <p className="text-xs text-yellow-400 mt-1">⚠️ You can only allocate modules compatible with {selectedAccountType} accounts</p>
            </div>
          )}

          {selectedBroker && accounts.length > 0 && (
            <div>
              <label className="block text-sm font-semibold text-gray-300 mb-2">Select Account</label>
              <select value={selectedAccount?.AccountID || ''} onChange={(e) => { const account = accounts.find(a => a.AccountID === e.target.value); setSelectedAccount(account || null); }} className="w-full bg-slate-900 border border-slate-700 text-white rounded-lg px-4 py-3">
                <option value="">Select account</option>
                {accounts.map(account => (
                  <option key={account.AccountID} value={account.AccountID}>{account.Name || account.AccountID}</option>
                ))}
              </select>
            </div>
          )}

          {selectedAccount && accountBalances && (
            <div className="bg-slate-900/50 border border-slate-700 rounded-lg p-4">
              <div className="text-sm font-semibold text-gray-400 mb-3">Account Snapshot</div>
              <div className="grid grid-cols-2 gap-3">
                <div className="bg-slate-800/50 rounded p-2">
                  <div className="text-xs text-gray-500">Cash Balance</div>
                  <div className="text-base font-semibold text-green-400">\${parseFloat(accountBalances.CashBalance || 0).toLocaleString()}</div>
                </div>
                <div className="bg-slate-800/50 rounded p-2">
                  <div className="text-xs text-gray-500">Buying Power</div>
                  <div className="text-base font-semibold text-blue-400">\${parseFloat(accountBalances.BuyingPower || 0).toLocaleString()}</div>
                </div>
                <div className="bg-slate-800/50 rounded p-2">
                  <div className="text-xs text-gray-500">Equity</div>
                  <div className="text-base font-semibold text-white">\${parseFloat(accountBalances.Equity || 0).toLocaleString()}</div>
                </div>
                <div className="bg-slate-800/50 rounded p-2">
                  <div className="text-xs text-gray-500">Market Value</div>
                  <div className="text-base font-semibold text-yellow-400">\${parseFloat(accountBalances.MarketValue || 0).toLocaleString()}</div>
                </div>
              </div>
            </div>
          )}

          {!selectedBroker && (
            <div>
              <label className="block text-sm font-semibold text-gray-300 mb-2">Starting Balance (USD)</label>
              <input type="number" step="0.01" min="0" value={manualBalance} onChange={(e) => setManualBalance(Number(e.target.value))} className="w-full bg-slate-900 border border-slate-700 text-white rounded-lg px-4 py-3" />
            </div>
          )}

          <div className="bg-blue-500/10 border border-blue-500/30 rounded-lg p-4">
            <div className="text-sm text-blue-400">ℹ️ Modules can be allocated after creating the mindfolio</div>
          </div>

          <div className="flex items-center justify-end gap-3">
            <button onClick={onClose} className="px-6 py-3 bg-slate-800 hover:bg-slate-700 text-white rounded-lg font-semibold">Cancel</button>
            <button onClick={handleCreate} disabled={!mindfolioName.trim() || creating} className="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-semibold disabled:opacity-50">
              {creating ? 'Creating...' : 'Create Mindfolio'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
