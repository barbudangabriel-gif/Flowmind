import React, { useEffect, useState } from "react";
import { mfClient } from "../services/mindfolioClient";
import { Link } from "react-router-dom";

export default function MindfolioList() {
 const [items, setItems] = useState([]);
 const [loading, setLoading] = useState(true);
 const [err, setErr] = useState("");
 const [searchQuery, setSearchQuery] = useState("");
 const [filterStatus, setFilterStatus] = useState("ALL");
 const [sortBy, setSortBy] = useState("name");
 const [importing, setImporting] = useState(false);

 const handleImportFromTradeStation = async () => {
 if (!window.confirm('Import all positions and cash from TradeStation?')) {
 return;
 }
 
 setImporting(true);
 try {
 // TODO: Get account_id from user selection if multiple accounts
 const account_id = "11775499"; // Hardcoded for now
 
 const result = await mfClient.importFromTradeStation(account_id);
 
 alert(`Successfully imported ${result.positions_imported} positions!\nCash: $${result.cash_balance.toFixed(2)}`);
 
 // Reload mindfolios list
 const data = await mfClient.list();
 const active = (data || []).filter(m => m.status !== 'DELETED');
 setItems(active);
 } catch (error) {
 console.error('Import failed:', error);
 alert('Import failed: ' + error.message);
 } finally {
 setImporting(false);
 }
 };

 useEffect(() => {
 let mounted = true;
 
 mfClient.list()
 .then(data => {
 if (!mounted) return;
 // Filter out DELETED mindfolios
 const active = (data || []).filter(m => m.status !== 'DELETED');
 setItems(active);
 })
 .catch(e => {
 console.error('Mindfolio list error:', e);
 setErr(String(e));
 // No fallback - show empty list if API fails
 if (!mounted) return;
 setItems([]);
 })
 .finally(() => setLoading(false));
 
 return () => { mounted = false; };
 }, []);

 // Filter and sort logic - MUST be before early returns to maintain consistent hook order
 const filteredAndSortedItems = React.useMemo(() => {
 let result = [...items];

 // Apply search filter
 if (searchQuery.trim()) {
 const query = searchQuery.toLowerCase();
 result = result.filter(p => 
 p.name?.toLowerCase().includes(query) ||
 p.id?.toLowerCase().includes(query) ||
 p.modules?.some(m => m.module?.toLowerCase().includes(query))
 );
 }

 // Apply status filter
 if (filterStatus !== "ALL") {
 result = result.filter(p => p.status === filterStatus);
 }

 // Apply sorting
 result.sort((a, b) => {
 switch (sortBy) {
 case "name":
 return (a.name || "").localeCompare(b.name || "");
 case "balance":
 return (b.cash_balance || 0) - (a.cash_balance || 0);
 case "created":
 return new Date(b.created_at) - new Date(a.created_at);
 case "status":
 return (a.status || "").localeCompare(b.status || "");
 default:
 return 0;
 }
 });

 return result;
 }, [items, searchQuery, filterStatus, sortBy]);

 // Calculate totals and counts
 const totalValue = items.reduce((sum, pf) => sum + (pf.cash_balance || 0), 0);
 const totalMindfolios = items.length;
 const activeCount = items.filter(p => p.status === 'ACTIVE').length;
 const pausedCount = items.filter(p => p.status === 'PAUSED').length;

 // Early returns AFTER all hooks
 if (loading) {
 return (
 <div className="p-8">
 <div className="flex items-center justify-center h-64">
 <div className="text-center">
 <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
 <div className="text-gray-400">Loading mindfolios...</div>
 </div>
 </div>
 </div>
 );
 }
 
 // Don't show error screen - let fallback data render
 // if (err) {
 // return (
 // <div className="p-8">
 // <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-6">
 // <div className="flex items-start gap-3">
 // <span className="text-lg"></span>
 // <div>
 // <div className="font-semibold text-red-400 mb-2">Error Loading Mindfolios</div>
 // <div className="text-sm text-gray-400">{err}</div>
 // </div>
 // </div>
 // </div>
 // </div>
 // );
 // }

 return (
 <div className="p-8 space-y-6">
 {/* Header */}
 <div className="flex items-center justify-between">
 <div>
 <h1 className="text-xl font-bold text-white mb-2">Mindfolio Manager</h1>
 <p className="text-gray-400">Import live portfolio or create empty mindfolio to track manually</p>
 </div>
 <div className="flex gap-3">
 <Link
 to="/mindfolio/import"
 className="px-6 py-3 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white rounded-lg font-semibold transition-all hover:scale-105 shadow-lg flex items-center gap-2"
 >
 <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
 <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
 </svg>
 Import from TradeStation
 </Link>
 <Link 
 to="/mindfolio/new" 
 className="px-6 py-3 bg-slate-700 hover:bg-slate-600 text-white rounded-lg font-semibold transition-all hover:scale-105 shadow-lg flex items-center gap-2"
 >
 <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
 <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
 </svg>
 Create Empty Mindfolio
 </Link>
 </div>
 </div>

 {/* Stats Cards */}
 <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
 <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-6">
 <div className="text-sm text-gray-400 mb-1">Total Mindfolios</div>
 <div className="text-xl font-bold text-white">{totalMindfolios}</div>
 </div>
 <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-6">
 <div className="text-sm text-gray-400 mb-1">Total Cash</div>
 <div className="text-xl font-bold text-green-400">
 ${totalValue.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
 </div>
 </div>
 <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-6">
 <div className="text-sm text-gray-400 mb-1">Active</div>
 <div className="text-xl font-bold text-green-400">{activeCount}</div>
 </div>
 <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-6">
 <div className="text-sm text-gray-400 mb-1">Paused</div>
 <div className="text-xl font-bold text-yellow-400">{pausedCount}</div>
 </div>
 </div>

 {/* Search, Filter, Sort Controls */}
 <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-4">
 <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
 {/* Search */}
 <div className="relative">
 <input
 type="text"
 placeholder="Search mindfolios..."
 value={searchQuery}
 onChange={(e) => setSearchQuery(e.target.value)}
 className="w-full bg-gray-900 border border-gray-700 text-white rounded-lg px-4 py-2 pl-10 focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-colors"
 />
 </div>

 {/* Filter by Status */}
 <div>
 <select
 value={filterStatus}
 onChange={(e) => setFilterStatus(e.target.value)}
 className="w-full bg-gray-900 border border-gray-700 text-white rounded-lg px-4 py-2 focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-colors"
 >
 <option value="ALL">All Status</option>
 <option value="ACTIVE">Active Only</option>
 <option value="PAUSED">Paused Only</option>
 <option value="CLOSED">Closed Only</option>
 </select>
 </div>

 {/* Sort by */}
 <div>
 <select
 value={sortBy}
 onChange={(e) => setSortBy(e.target.value)}
 className="w-full bg-gray-900 border border-gray-700 text-white rounded-lg px-4 py-2 focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-colors"
 >
 <option value="name">Sort by Name</option>
 <option value="balance">Sort by Balance</option>
 <option value="created">Sort by Date</option>
 <option value="status">Sort by Status</option>
 </select>
 </div>
 </div>

 {/* Active filters indicator */}
 {(searchQuery || filterStatus !== "ALL") && (
 <div className="mt-3 flex items-center gap-2 text-sm">
 <span className="text-gray-400">Active filters:</span>
 {searchQuery && (
 <span className="px-2 py-1 bg-blue-500/20 text-blue-400 rounded border border-blue-500/30">
 Search: "{searchQuery}"
 </span>
 )}
 {filterStatus !== "ALL" && (
 <span className="px-2 py-1 bg-green-500/20 text-green-400 rounded border border-green-500/30">
 Status: {filterStatus}
 </span>
 )}
 <button
 onClick={() => {
 setSearchQuery("");
 setFilterStatus("ALL");
 }}
 className="ml-2 text-xs text-gray-400 hover:text-white transition-colors"
 >
 Clear all
 </button>
 </div>
 )}
 </div>
 
 {filteredAndSortedItems.length === 0 ? (
 <div className="text-center py-16 bg-slate-800/30 border border-slate-700 rounded-lg">
 <div className="text-base text-gray-300 mb-2">
 {items.length === 0 ? "No mindfolios yet" : "No mindfolios match your filters"}
 </div>
 <div className="text-gray-500 mb-6">
 {items.length === 0 
 ? "Create your first mindfolio to start tracking your trades"
 : "Try adjusting your search or filter criteria"
 }
 </div>
 {items.length === 0 ? (
 <Link 
 to="/mindfolio/new"
 className="inline-block px-8 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-semibold transition-all hover:scale-105"
 >
 Create Your First Mindfolio
 </Link>
 ) : (
 <button
 onClick={() => {
 setSearchQuery("");
 setFilterStatus("ALL");
 }}
 className="inline-block px-8 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-semibold transition-all hover:scale-105"
 >
 Clear Filters
 </button>
 )}
 </div>
 ) : (
 <>
 {/* Results count */}
 <div className="flex items-center justify-between text-sm text-gray-400">
 <span>
 Showing {filteredAndSortedItems.length} of {totalMindfolios} mindfolio{totalMindfolios !== 1 ? 's' : ''}
 </span>
 <span>
 Sorted by: <span className="text-blue-400 font-semibold">
 {sortBy === 'name' ? 'Name' : sortBy === 'balance' ? 'Balance' : sortBy === 'created' ? 'Date' : 'Status'}
 </span>
 </span>
 </div>

 <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
 {filteredAndSortedItems.map(p => {
 const statusColors = {
 'ACTIVE': 'bg-green-500/20 text-green-400 border-green-500/30',
 'PAUSED': 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30',
 'CLOSED': 'bg-gray-500/20 text-gray-400 border-gray-500/30'
 };
 
 return (
 <Link 
 key={p.id} 
 to={`/mindfolio/${p.id}`} 
 className="group bg-slate-800/50 border border-slate-700 rounded-xl p-6 hover:bg-slate-800 hover:border-slate-600 transition-all hover:shadow-xl hover:scale-105"
 >
 {/* Header */}
 <div className="flex items-start justify-between mb-4">
 <div className="flex-1">
 <div className="text-base font-bold text-white group-hover:text-blue-400 transition-colors mb-1">
 {p.name}
 </div>
 <div className="text-xs text-gray-500">
 ID: {p.id?.substring?.(0, 8) || p.id}
 </div>
 </div>
 <div className={`px-3 py-1 rounded-full text-xs font-semibold border ${statusColors[p.status] || statusColors.CLOSED}`}>
 {p.status}
 </div>
 </div>

 {/* Cash Balance */}
 <div className="bg-slate-900/50 rounded-lg p-4 mb-4">
 <div className="text-sm text-gray-400 mb-1">Cash Balance</div>
 <div className="text-lg font-bold text-green-400">
 ${(p.cash_balance || 0).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
 </div>
 </div>

 {/* Modules */}
 <div className="space-y-2">
 <div className="text-sm text-gray-400 font-semibold">Modules ({p.modules?.length || 0})</div>
 {p.modules && p.modules.length > 0 ? (
 <div className="flex flex-wrap gap-2">
 {p.modules.map((m, idx) => (
 <div 
 key={idx}
 className="px-2 py-1 bg-blue-500/20 text-blue-400 text-xs rounded border border-blue-500/30"
 >
 {m.module}
 </div>
 ))}
 </div>
 ) : (
 <div className="text-xs text-gray-500">No modules configured</div>
 )}
 </div>

 {/* Footer - Dates */}
 <div className="mt-4 pt-4 border-t border-slate-700/50 flex items-center justify-between text-xs text-gray-500">
 <span>Created: {new Date(p.created_at).toLocaleDateString()}</span>
 <span className="text-blue-400 group-hover:text-blue-300">View →</span>
 </div>
 </Link>
 );
 })}
 </div>
 </>
 )}
 </div>
 );
}