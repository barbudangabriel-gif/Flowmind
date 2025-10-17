import React, { useEffect, useState } from "react";
import { mfClient } from "../services/mindfolioClient";
import { useParams, Link } from "react-router-dom";
import TransactionsTable from "../components/TransactionsTable";
import PositionsTable from "../components/PositionsTable";
import CSVImport from "../components/CSVImport";
import AnalyticsPanel from "../components/AnalyticsPanel";
import BucketForm from "../components/BucketForm";

export default function MindfolioDetail() {
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
 mfClient.get(id),
 mfClient.stats(id)
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
 await mfClient.funds(id, delta);
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
 <Link to="/mindfolio" className="text-blue-400 hover:text-blue-300 mt-2 inline-block">
 ← Back to portfolios
 </Link>
 </div>
 );
 }

 if (!p) {
 return <div className="p-4 text-sm text-gray-400 bg-gray-950 min-h-screen">Loading portfolio…</div>;
 }

 const tabs = [
 { id: 'overview', label: 'Overview', icon: '', description: 'Summary & fund management' },
 { id: 'analytics', label: 'Analytics', icon: '', description: 'Performance metrics & buckets' },
 { id: 'positions', label: 'Positions', icon: '💼', description: 'Open positions & P&L' },
 { id: 'transactions', label: 'Transactions', icon: '', description: 'Trade history' },
 { id: 'import', label: 'Import CSV', icon: '', description: 'Import trades from file' }
 ];

 return (
 <div className="p-4 space-y-6 bg-gray-950 min-h-screen">
 {/* Header with breadcrumb and actions */}
 <div className="bg-slate-900/60 border border-slate-800 rounded-lg p-6">
 <div className="flex items-center justify-between mb-4">
 <div className="flex-1">
 <div className="flex items-center gap-3 mb-3">
 <Link 
 to="/mindfolio" 
 className="text-blue-400 hover:text-blue-300 transition-colors flex items-center gap-1"
 >
 ← <span className="hidden sm:inline">Back to Portfolios</span>
 </Link>
 <span className="text-gray-600">/</span>
 <h1 className="text-2xl font-bold text-white">{p.name}</h1>
 </div>
 <div className="flex flex-wrap items-center gap-4 text-sm">
 <div className="flex items-center gap-2">
 <span className="text-gray-400">NAV:</span>
 <span className="font-mono text-lg text-green-400 font-semibold">
 ${p.cash_balance?.toFixed?.(2) ?? p.cash_balance}
 </span>
 </div>
 <div className="flex items-center gap-2">
 <span className="text-gray-400">Status:</span>
 <span className={`px-2 py-1 rounded-full text-xs font-semibold ${
 p.status === 'ACTIVE' 
 ? 'bg-green-500/20 text-green-400 border border-green-500/30' 
 : 'bg-gray-500/20 text-gray-400 border border-gray-500/30'
 }`}>
 {p.status}
 </span>
 </div>
 <div className="flex items-center gap-2">
 <span className="text-gray-400">ID:</span>
 <span className="font-mono text-xs text-gray-500">{p.id?.substring?.(0, 8) || p.id}</span>
 </div>
 </div>
 </div>
 
 {/* Quick Actions */}
 <div className="hidden lg:flex items-center gap-3">
 <button
 onClick={() => setActiveTab('import')}
 className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-gray-300 rounded-lg border border-slate-700 transition-colors text-sm"
 >
 Import
 </button>
 <button
 onClick={() => setActiveTab('transactions')}
 className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors text-sm font-semibold"
 >
 + Add Trade
 </button>
 </div>
 </div>

 {/* Created/Updated info */}
 <div className="flex items-center gap-6 text-xs text-gray-500 pt-3 border-t border-slate-800">
 <span>Created: {new Date(p.created_at).toLocaleString()}</span>
 {p.updated_at && (
 <span>Updated: {new Date(p.updated_at).toLocaleString()}</span>
 )}
 </div>
 </div>

 {/* Stats Summary - Enhanced */}
 {stats && (
 <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
 <div className="bg-gradient-to-br from-slate-800/80 to-slate-900/80 border border-slate-700 rounded-lg p-5 hover:border-slate-600 transition-colors">
 <div className="flex items-center justify-between mb-2">
 <div className="text-sm text-gray-400">Realized P&L</div>
 <span className="text-2xl"></span>
 </div>
 <div className={`text-2xl font-bold ${(stats.pnl_realized || 0) >= 0 ? 'text-green-400' : 'text-red-400'}`}>
 ${(stats.pnl_realized || 0).toFixed(2)}
 </div>
 <div className="text-xs text-gray-500 mt-1">
 {(stats.pnl_realized || 0) >= 0 ? '↑ Profit' : '↓ Loss'}
 </div>
 </div>
 
 <div className="bg-gradient-to-br from-slate-800/80 to-slate-900/80 border border-slate-700 rounded-lg p-5 hover:border-slate-600 transition-colors">
 <div className="flex items-center justify-between mb-2">
 <div className="text-sm text-gray-400">Total Trades</div>
 <span className="text-2xl"></span>
 </div>
 <div className="text-2xl font-bold text-white">
 {stats.total_trades || 0}
 </div>
 <div className="text-xs text-gray-500 mt-1">
 All time transactions
 </div>
 </div>
 
 <div className="bg-gradient-to-br from-slate-800/80 to-slate-900/80 border border-slate-700 rounded-lg p-5 hover:border-slate-600 transition-colors">
 <div className="flex items-center justify-between mb-2">
 <div className="text-sm text-gray-400">Open Positions</div>
 <span className="text-2xl">💼</span>
 </div>
 <div className="text-2xl font-bold text-blue-400">
 {stats.positions_count || 0}
 </div>
 <div className="text-xs text-gray-500 mt-1">
 Active holdings
 </div>
 </div>
 
 <div className="bg-gradient-to-br from-slate-800/80 to-slate-900/80 border border-slate-700 rounded-lg p-5 hover:border-slate-600 transition-colors">
 <div className="flex items-center justify-between mb-2">
 <div className="text-sm text-gray-400">Cash Balance</div>
 <span className="text-2xl"></span>
 </div>
 <div className="text-2xl font-bold text-green-400">
 ${p.cash_balance?.toFixed?.(2) ?? 0}
 </div>
 <div className="text-xs text-gray-500 mt-1">
 Available funds
 </div>
 </div>
 </div>
 )}

 {/* Tab Navigation - Enhanced */}
 <div className="bg-slate-900/60 border border-slate-800 rounded-lg overflow-hidden">
 <nav className="flex overflow-x-auto">
 {tabs.map((tab) => (
 <button
 key={tab.id}
 onClick={() => setActiveTab(tab.id)}
 className={`group flex-1 min-w-[140px] py-4 px-4 border-b-2 font-medium text-sm transition-all ${
 activeTab === tab.id
 ? 'border-blue-500 bg-slate-800/50'
 : 'border-transparent hover:bg-slate-800/30 hover:border-slate-700'
 }`}
 >
 <div className="flex flex-col items-center gap-1">
 <span className="text-2xl">{tab.icon}</span>
 <span className={`${
 activeTab === tab.id ? 'text-blue-400' : 'text-gray-400 group-hover:text-gray-300'
 }`}>
 {tab.label}
 </span>
 <span className="text-xs text-gray-600 hidden lg:block">
 {tab.description}
 </span>
 </div>
 </button>
 ))}
 </nav>
 </div>

 {/* Tab Content */}
 <div className="mt-6">
 {/* Tab Content Header - shows current tab info */}
 <div className="mb-4 flex items-center justify-between">
 <div className="flex items-center gap-3">
 <span className="text-3xl">{tabs.find(t => t.id === activeTab)?.icon}</span>
 <div>
 <h2 className="text-xl font-bold text-white">
 {tabs.find(t => t.id === activeTab)?.label}
 </h2>
 <p className="text-sm text-gray-400">
 {tabs.find(t => t.id === activeTab)?.description}
 </p>
 </div>
 </div>
 
 {/* Context actions for current tab */}
 {activeTab === 'transactions' && (
 <button className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm font-semibold">
 + Add Transaction
 </button>
 )}
 {activeTab === 'import' && (
 <div className="text-xs text-gray-500">
 Supports CSV, Excel formats
 </div>
 )}
 </div>

 {activeTab === 'overview' && (
 <div className="grid md:grid-cols-2 gap-6">
 {/* Allocations */}
 <div className="border border-gray-800 rounded-xl p-6 bg-gradient-to-br from-slate-900/80 to-slate-900/60 hover:border-slate-700 transition-colors">
 <div className="flex items-center gap-3 mb-5">
 <span className="text-3xl"></span>
 <div>
 <div className="text-lg font-semibold text-white">Module Allocations</div>
 <div className="text-xs text-gray-500">Configure trading strategies</div>
 </div>
 </div>
 {(!p.modules || p.modules.length === 0) ? (
 <div className="text-center py-8 bg-slate-800/30 rounded-lg border border-slate-700/50">
 <div className="text-xl mb-2"></div>
 <div className="text-sm text-gray-400 mb-3">No module allocations configured yet</div>
 <button className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm rounded-lg transition-colors">
 + Add Module
 </button>
 </div>
 ) : (
 <div className="space-y-3">
 {p.modules.map((m, idx) => (
 <div key={idx} className="border border-gray-700 rounded-lg p-4 bg-slate-800/50 hover:bg-slate-800 transition-colors group">
 <div className="flex items-center justify-between mb-3">
 <div className="flex items-center gap-2">
 <span className="text-lg"></span>
 <div className="text-sm font-medium text-white">{m.module}</div>
 </div>
 {m.autotrade && (
 <span className="text-xs bg-green-900/50 text-green-300 px-3 py-1 rounded-full border border-green-700/30 font-semibold">
 ✓ Auto
 </span>
 )}
 </div>
 <div className="grid grid-cols-3 gap-3 text-xs">
 <div className="bg-slate-900/50 rounded p-2">
 <div className="text-gray-500 mb-1">Budget</div>
 <div className="font-mono text-white">${m.budget}</div>
 </div>
 <div className="bg-slate-900/50 rounded p-2">
 <div className="text-gray-500 mb-1">Max/Trade</div>
 <div className="font-mono text-white">${m.max_risk_per_trade}</div>
 </div>
 <div className="bg-slate-900/50 rounded p-2">
 <div className="text-gray-500 mb-1">Daily Limit</div>
 <div className="font-mono text-white">${m.daily_loss_limit}</div>
 </div>
 </div>
 <button className="mt-3 w-full text-xs text-gray-400 hover:text-white opacity-0 group-hover:opacity-100 transition-opacity">
 Edit Module →
 </button>
 </div>
 ))}
 </div>
 )}
 </div>

 {/* Funds Management */}
 <div className="border border-gray-800 rounded-xl p-6 bg-gradient-to-br from-slate-900/80 to-slate-900/60 hover:border-slate-700 transition-colors">
 <div className="flex items-center gap-3 mb-5">
 <span className="text-3xl"></span>
 <div>
 <div className="text-lg font-semibold text-white">Manage Funds</div>
 <div className="text-xs text-gray-500">Add or remove cash balance</div>
 </div>
 </div>
 <form onSubmit={handleFundsUpdate} className="space-y-4">
 <div>
 <label className="text-sm text-gray-300 mb-2 block font-medium">
 Amount to Add/Remove ($)
 </label>
 <div className="relative">
 <span className="absolute left-3 top-2.5 text-gray-500">$</span>
 <input
 type="number"
 step="0.01"
 value={fundsDelta}
 onChange={e => setFundsDelta(e.target.value)}
 placeholder="e.g. 1000 or -500"
 className="w-full border border-gray-700 bg-gray-800 text-white rounded-lg px-3 py-2 pl-7 text-sm focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-colors"
 />
 </div>
 <div className="text-xs text-gray-500 mt-2 flex items-center gap-2">
 <span></span>
 <span>Use positive numbers to add, negative to remove</span>
 </div>
 </div>
 
 <div className="bg-slate-800/50 rounded-lg p-3 border border-slate-700">
 <div className="flex items-center justify-between text-sm mb-1">
 <span className="text-gray-400">Current Balance:</span>
 <span className="font-mono text-green-400 font-semibold">
 ${p.cash_balance?.toFixed?.(2) ?? 0}
 </span>
 </div>
 {fundsDelta && (
 <div className="flex items-center justify-between text-sm">
 <span className="text-gray-400">New Balance:</span>
 <span className={`font-mono font-semibold ${
 (parseFloat(fundsDelta) + (p.cash_balance || 0)) >= 0 ? 'text-green-400' : 'text-red-400'
 }`}>
 ${((parseFloat(fundsDelta) || 0) + (p.cash_balance || 0)).toFixed(2)}
 </span>
 </div>
 )}
 </div>

 <button
 type="submit"
 disabled={!fundsDelta || updating}
 className="w-full px-4 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-700 disabled:cursor-not-allowed transition-colors text-sm font-semibold"
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