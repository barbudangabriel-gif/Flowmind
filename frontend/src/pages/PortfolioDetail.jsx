import React, { useEffect, useState } from "react";
import { pfClient } from "../services/portfolioClient";
import { useParams, Link } from "react-router-dom";
import TransactionsTable from "../components/TransactionsTable";
import PositionsTable from "../components/PositionsTable";
import CSVImport from "../components/CSVImport";
import AnalyticsPanel from "../components/AnalyticsPanel";
import BucketForm from "../components/BucketForm";

export default function PortfolioDetail() {
  const { id } = useParams();
  const [p, setP] = useState(null);
  const [stats, setStats] = useState(null);
  const [err, setErr] = useState("");
  const [fundsDelta, setFundsDelta] = useState("");
  const [updating, setUpdating] = useState(false);
  const [activeTab, setActiveTab] = useState("overview");

  const loadData = async () => {
    if (!id) return;
    
    try {
      const [portfolio, statistics] = await Promise.all([
        pfClient.get(id),
        pfClient.stats(id)
      ]);
      
      setP(portfolio);
      setStats(statistics);
    } catch (e) {
      setErr(String(e));
    }
  };

  useEffect(() => {
    loadData();
  }, [id]);

  const handleFundsUpdate = async (e) => {
    e.preventDefault();
    if (!fundsDelta || updating) return;
    
    setUpdating(true);
    try {
      const delta = parseFloat(fundsDelta);
      await pfClient.funds(id, delta);
      setFundsDelta("");
      await loadData(); // Refresh data
    } catch (e) {
      setErr(`Funds update failed: ${e.message}`);
    } finally {
      setUpdating(false);
    }
  };

  const handleImportComplete = () => {
    // Refresh data after import
    loadData();
  };

  if (err) {
    return (
      <div className="p-4 text-sm text-red-400 bg-red-900/20 border border-red-700/40 rounded">
        <div className="font-semibold">Error loading portfolio</div>
        <div>{err}</div>
        <Link to="/portfolios" className="text-blue-400 hover:text-blue-300 mt-2 inline-block">
          ← Back to portfolios
        </Link>
      </div>
    );
  }

  if (!p) {
    return <div className="p-4 text-sm text-gray-400 bg-gray-950 min-h-screen">Loading portfolio…</div>;
  }

  const tabs = [
    { id: 'overview', label: 'Overview', icon: '📊' },
    { id: 'analytics', label: 'Analytics & Buckets', icon: '📈' },
    { id: 'positions', label: 'Positions & P&L', icon: '💼' },
    { id: 'transactions', label: 'Transactions', icon: '📋' },
    { id: 'import', label: 'Import CSV', icon: '📤' }
  ];

  return (
    <div className="p-4 space-y-6 bg-gray-950 min-h-screen">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <div className="flex items-center gap-3 mb-2">
            <Link to="/portfolios" className="text-blue-400 hover:text-blue-300">
              ← Back
            </Link>
            <h1 className="text-xl font-semibold text-white">{p.name}</h1>
          </div>
          <div className="flex items-center gap-4 text-sm text-gray-400">
            <span>NAV: <span className="font-mono text-lg">${p.cash_balance?.toFixed?.(2) ?? p.cash_balance}</span></span>
            <span>Status: <span className={`font-medium ${p.status === 'ACTIVE' ? 'text-green-400' : 'text-gray-400'}`}>
              {p.status}
            </span></span>
            <span>ID: <span className="font-mono text-xs">{p.id}</span></span>
          </div>
        </div>
      </div>

      {/* Stats Summary */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-4">
            <div className="text-sm text-gray-400">Realized P&L</div>
            <div className={`text-xl font-semibold ${(stats.pnl_realized || 0) >= 0 ? 'text-green-400' : 'text-red-400'}`}>
              {(stats.pnl_realized || 0).toFixed(2)}
            </div>
          </div>
          <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-4">
            <div className="text-sm text-gray-400">Total Trades</div>
            <div className="text-xl font-semibold text-white">
              {stats.total_trades || 0}
            </div>
          </div>
          <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-4">
            <div className="text-sm text-gray-400">Open Positions</div>
            <div className="text-xl font-semibold text-white">
              {stats.positions_count || 0}
            </div>
          </div>
          <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-4">
            <div className="text-sm text-gray-400">Cash Balance</div>
            <div className="text-xl font-semibold text-white">
              ${p.cash_balance?.toFixed?.(2) ?? 0}
            </div>
          </div>
        </div>
      )}

      {/* Tab Navigation */}
      <div className="border-b border-gray-800">
        <nav className="flex space-x-8">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === tab.id
                  ? 'border-blue-500 text-blue-400'
                  : 'border-transparent text-gray-400 hover:text-gray-300 hover:border-gray-700'
              }`}
            >
              <span className="mr-2">{tab.icon}</span>
              {tab.label}
            </button>
          ))}
        </nav>
      </div>

      {/* Tab Content */}
      <div className="mt-6">
        {activeTab === 'overview' && (
          <div className="grid md:grid-cols-2 gap-6">
            {/* Allocations */}
            <div className="border border-gray-800 rounded-xl p-4 bg-slate-900/60">
              <div className="text-lg font-semibold mb-4 text-white">Module Allocations</div>
              {(!p.modules || p.modules.length === 0) ? (
                <div className="text-sm text-gray-400 py-4">
                  No module allocations configured yet
                </div>
              ) : (
                <div className="space-y-3">
                  {p.modules.map((m, idx) => (
                    <div key={idx} className="border border-gray-700 rounded-lg p-3 bg-slate-800/50">
                      <div className="flex items-center justify-between mb-2">
                        <div className="text-sm font-medium text-white">{m.module}</div>
                        {m.autotrade && (
                          <span className="text-xs bg-green-900 text-green-300 px-2 py-1 rounded">
                            Auto
                          </span>
                        )}
                      </div>
                      <div className="grid grid-cols-2 gap-2 text-xs text-gray-400">
                        <div>Budget: <span className="font-mono">${m.budget}</span></div>
                        <div>Max/Trade: <span className="font-mono">${m.max_risk_per_trade}</span></div>
                        <div>Daily Limit: <span className="font-mono">${m.daily_loss_limit}</span></div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Funds Management */}
            <div className="border border-gray-800 rounded-xl p-4 bg-slate-900/60">
              <div className="text-lg font-semibold mb-4 text-white">Manage Funds</div>
              <form onSubmit={handleFundsUpdate} className="space-y-3">
                <div>
                  <label className="text-sm text-gray-400 mb-1 block">
                    Add/Remove Funds ($)
                  </label>
                  <input
                    type="number"
                    step="0.01"
                    value={fundsDelta}
                    onChange={e => setFundsDelta(e.target.value)}
                    placeholder="e.g. 1000 or -500"
                    className="w-full border border-gray-700 bg-gray-800 text-white rounded-md px-3 py-2 text-sm focus:border-blue-500 focus:ring-blue-500"
                  />
                </div>
                <button
                  type="submit"
                  disabled={!fundsDelta || updating}
                  className="w-full px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-700 disabled:cursor-not-allowed transition-colors text-sm"
                >
                  {updating ? "Updating..." : "Update Funds"}
                </button>
              </form>
            </div>
          </div>
        )}

        {activeTab === 'analytics' && (
          <div className="space-y-6">
            <AnalyticsPanel portfolioId={id} />
            <BucketForm portfolioId={id} onCreated={loadData} />
          </div>
        )}

        {activeTab === 'positions' && (
          <PositionsTable portfolioId={id} />
        )}

        {activeTab === 'transactions' && (
          <TransactionsTable portfolioId={id} />
        )}

        {activeTab === 'import' && (
          <CSVImport portfolioId={id} onImportComplete={handleImportComplete} />
        )}
      </div>
    </div>
  );
}