import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { mfClient } from "../services/mindfolioClient";

const API = process.env.REACT_APP_BACKEND_URL || "";

export default function ImportFromTradeStation() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [accounts, setAccounts] = useState([]);
  const [selectedAccount, setSelectedAccount] = useState(null);
  const [positions, setPositions] = useState([]);
  const [balance, setBalance] = useState(null);
  const [importing, setImporting] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    loadTradeStationAccounts();
  }, []);

  const loadTradeStationAccounts = async () => {
    try {
      const response = await fetch(`${API}/api/tradestation/accounts`, {
        headers: { "X-User-ID": "default" }
      });
      
      if (!response.ok) {
        throw new Error("Not authenticated with TradeStation");
      }
      
      const data = await response.json();
      const accountsList = data.data?.Accounts || [];
      
      setAccounts(accountsList);
      
      // Auto-select first account
      if (accountsList.length > 0) {
        selectAccount(accountsList[0].AccountID);
      }
    } catch (err) {
      console.error("Failed to load accounts:", err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const selectAccount = async (accountId) => {
    setSelectedAccount(accountId);
    setLoading(true);
    
    try {
      // Load positions
      const posResp = await fetch(`${API}/api/tradestation/accounts/${accountId}/positions`, {
        headers: { "X-User-ID": "default" }
      });
      const posData = await posResp.json();
      setPositions(posData.data?.Positions || []);
      
      // Load balance
      const balResp = await fetch(`${API}/api/tradestation/accounts/${accountId}/balances`, {
        headers: { "X-User-ID": "default" }
      });
      const balData = await balResp.json();
      setBalance(balData.data?.Balances?.[0] || null);
    } catch (err) {
      console.error("Failed to load account data:", err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleImport = async () => {
    if (!selectedAccount) return;
    
    if (!window.confirm(`Import ${positions.length} positions and $${balance?.CashBalance || 0} cash from TradeStation?`)) {
      return;
    }
    
    setImporting(true);
    try {
      const result = await mfClient.importFromTradeStation(
        selectedAccount,
        `TradeStation - ${selectedAccount}`
      );
      
      alert(`Success! Imported ${result.positions_imported} positions.\nCash: $${result.cash_balance.toFixed(2)}`);
      navigate(`/mindfolio/${result.mindfolio.id}`);
    } catch (err) {
      console.error("Import failed:", err);
      alert("Import failed: " + err.message);
    } finally {
      setImporting(false);
    }
  };

  if (error && !loading) {
    return (
      <div className="p-8">
        <div className="max-w-2xl mx-auto">
          <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-6">
            <h2 className="text-xl font-bold text-red-400 mb-4">Authentication Required</h2>
            <p className="text-gray-300 mb-4">{error}</p>
            <a 
              href={`${API}/api/ts/login`}
              className="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-semibold inline-block"
            >
              Connect TradeStation
            </a>
          </div>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="p-8">
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
            <div className="text-gray-400">Loading TradeStation data...</div>
          </div>
        </div>
      </div>
    );
  }

  const totalMarketValue = positions.reduce((sum, p) => sum + parseFloat(p.MarketValue || 0), 0);
  const totalUnrealizedPnL = positions.reduce((sum, p) => sum + parseFloat(p.UnrealizedProfitLoss || 0), 0);

  return (
    <div className="p-8 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white mb-2">Import from TradeStation</h1>
          <p className="text-gray-400">Select account and review positions before importing</p>
        </div>
        <button
          onClick={() => navigate('/mindfolio')}
          className="px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-lg transition"
        >
          Cancel
        </button>
      </div>

      {/* Account Selection */}
      {accounts.length > 1 && (
        <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-6">
          <h2 className="text-lg font-semibold text-white mb-4">Select Account</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {accounts.map(acc => (
              <button
                key={acc.AccountID}
                onClick={() => selectAccount(acc.AccountID)}
                className={`p-4 rounded-lg border-2 transition text-left ${
                  selectedAccount === acc.AccountID
                    ? 'border-blue-500 bg-blue-500/10'
                    : 'border-slate-700 bg-slate-800/30 hover:border-slate-600'
                }`}
              >
                <div className="font-semibold text-white">{acc.Name || acc.AccountID}</div>
                <div className="text-sm text-gray-400">Account: {acc.AccountID}</div>
                <div className="text-sm text-gray-400">Type: {acc.AccountType}</div>
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-6">
          <div className="text-sm text-gray-400 mb-1">Cash Balance</div>
          <div className="text-2xl font-bold text-green-400">
            ${parseFloat(balance?.CashBalance || 0).toLocaleString('en-US', { minimumFractionDigits: 2 })}
          </div>
        </div>
        <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-6">
          <div className="text-sm text-gray-400 mb-1">Positions</div>
          <div className="text-2xl font-bold text-white">{positions.length}</div>
        </div>
        <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-6">
          <div className="text-sm text-gray-400 mb-1">Market Value</div>
          <div className="text-2xl font-bold text-white">
            ${totalMarketValue.toLocaleString('en-US', { minimumFractionDigits: 2 })}
          </div>
        </div>
        <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-6">
          <div className="text-sm text-gray-400 mb-1">Unrealized P&L</div>
          <div className={`text-2xl font-bold ${totalUnrealizedPnL >= 0 ? 'text-green-400' : 'text-red-400'}`}>
            ${totalUnrealizedPnL.toLocaleString('en-US', { minimumFractionDigits: 2 })}
          </div>
        </div>
      </div>

      {/* Positions Table */}
      <div className="bg-slate-800/50 border border-slate-700 rounded-lg overflow-hidden">
        <div className="p-6 border-b border-slate-700">
          <h2 className="text-lg font-semibold text-white">Positions to Import</h2>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-slate-900/50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">Symbol</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">Type</th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-400 uppercase tracking-wider">Quantity</th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-400 uppercase tracking-wider">Avg Price</th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-400 uppercase tracking-wider">Current</th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-400 uppercase tracking-wider">Market Value</th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-400 uppercase tracking-wider">P&L</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-700">
              {positions.length === 0 ? (
                <tr>
                  <td colSpan="7" className="px-6 py-8 text-center text-gray-400">
                    No positions found in this account
                  </td>
                </tr>
              ) : (
                positions.map((pos, idx) => (
                  <tr key={idx} className="hover:bg-slate-800/30">
                    <td className="px-6 py-4 whitespace-nowrap text-white font-semibold">{pos.Symbol}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-gray-400">{pos.AssetType}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-white">{pos.Quantity}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-gray-400">
                      ${parseFloat(pos.AveragePrice || 0).toFixed(2)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-white">
                      ${parseFloat(pos.Last || 0).toFixed(2)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-white">
                      ${parseFloat(pos.MarketValue || 0).toLocaleString('en-US', { minimumFractionDigits: 2 })}
                    </td>
                    <td className={`px-6 py-4 whitespace-nowrap text-right font-semibold ${
                      parseFloat(pos.UnrealizedProfitLoss || 0) >= 0 ? 'text-green-400' : 'text-red-400'
                    }`}>
                      ${parseFloat(pos.UnrealizedProfitLoss || 0).toFixed(2)}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Import Button */}
      <div className="flex justify-end">
        <button
          onClick={handleImport}
          disabled={importing || !selectedAccount || positions.length === 0}
          className="px-8 py-4 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 disabled:opacity-50 disabled:cursor-not-allowed text-white rounded-lg font-bold text-lg transition-all hover:scale-105 shadow-lg flex items-center gap-3"
        >
          {importing ? (
            <>
              <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-white"></div>
              Importing...
            </>
          ) : (
            <>
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
              </svg>
              Import {positions.length} Position{positions.length !== 1 ? 's' : ''} & ${parseFloat(balance?.CashBalance || 0).toFixed(0)} Cash
            </>
          )}
        </button>
      </div>
    </div>
  );
}
