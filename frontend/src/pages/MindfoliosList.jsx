import React, { useEffect, useState } from "react";
import { pfClient } from "../services/mindfolioClient";
import { Link } from "react-router-dom";
import MindfolioTemplateModal from "../components/MindfolioTemplateModal";

// Master Mindfolio Badge Component (NEW - Nov 2, 2025)
const MasterMindfolioBadge = ({ broker, autoSync, lastSync, syncStatus }) => {
  const formatRelativeTime = (isoString) => {
    if (!isoString) return 'Never';
    const date = new Date(isoString);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    
    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    const diffHours = Math.floor(diffMins / 60);
    if (diffHours < 24) return `${diffHours}h ago`;
    const diffDays = Math.floor(diffHours / 24);
    return `${diffDays}d ago`;
  };

  const syncStatusColors = {
    'idle': 'bg-gray-500/20 text-gray-400 border-gray-500/30',
    'syncing': 'bg-blue-500/20 text-blue-400 border-blue-500/30',
    'error': 'bg-red-500/20 text-red-400 border-red-500/30'
  };

  return (
    <div className="flex items-center gap-2 mb-3">
      <span className="px-2 py-1 rounded text-xs bg-purple-500/20 text-purple-400 border border-purple-500/30 font-semibold">
        Master
      </span>
      {autoSync && (
        <span className="px-2 py-1 rounded text-xs bg-green-500/20 text-green-400 border border-green-500/30">
          Auto-Sync
        </span>
      )}
      {syncStatus && (
        <span className={`px-2 py-1 rounded text-xs border ${syncStatusColors[syncStatus] || syncStatusColors.idle}`}>
          {syncStatus === 'syncing' ? '⟳ Syncing...' : syncStatus === 'error' ? '⚠ Error' : '✓ Synced'}
        </span>
      )}
      {lastSync && (
        <span className="text-xs text-gray-400">
          {formatRelativeTime(lastSync)}
        </span>
      )}
    </div>
  );
};

export default function MindfoliosList() {
 const [items, setItems] = useState([]);
 const [loading, setLoading] = useState(true);
 const [err, setErr] = useState("");
 const [searchQuery, setSearchQuery] = useState("");
 const [filterStatus, setFilterStatus] = useState("ALL");
 const [sortBy, setSortBy] = useState("name");
 const [showTemplateModal, setShowTemplateModal] = useState(false);

 useEffect(() => {
 let mounted = true;
 
 pfClient.list()
 .then(data => {
 if (!mounted) return;
 setItems(data);
 })
 .catch(e => setErr(String(e)))
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
 
 if (err) {
 return (
 <div className="p-8">
 <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-6">
 <div className="flex items-start gap-3">
 <span className="text-lg"></span>
 <div>
 <div className="font-semibold text-red-400 mb-2">Error Loading Mindfolios</div>
 <div className="text-sm text-gray-400">{err}</div>
 </div>
 </div>
 </div>
 </div>
 );
 }

 return (
 <>
 <div className="p-8 space-y-6">
 {/* Header */}
 <div className="flex items-center justify-between">
 <div>
 <h1 className="text-xl font-bold text-white mb-2">💼 Mindfolios</h1>
 <p className="text-gray-400">Manage your trading mindfolios and track performance</p>
 </div>
 <button 
 onClick={() => setShowTemplateModal(true)}
 className="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-semibold transition-all hover:scale-105 shadow-lg"
 >
 ✨ Create Mindfolio
 </button>
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
 <option value="ACTIVE"> Active Only</option>
 <option value="PAUSED">⏸️ Paused Only</option>
 <option value="CLOSED"> Closed Only</option>
 </select>
 </div>

 {/* Sort by */}
 <div>
 <select
 value={sortBy}
 onChange={(e) => setSortBy(e.target.value)}
 className="w-full bg-gray-900 border border-gray-700 text-white rounded-lg px-4 py-2 focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-colors"
 >
 <option value="name"> Sort by Name</option>
 <option value="balance">Sort by Balance</option>
 <option value="created"> Sort by Date</option>
 <option value="status"> Sort by Status</option>
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
 ✕ Clear all
 </button>
 </div>
 )}
 </div>
 
 {filteredAndSortedItems.length === 0 ? (
 <div className="text-center py-16 bg-slate-800/30 border border-slate-700 rounded-lg">
 <div className="text-xl mb-4">
 {items.length === 0 ? "" : ""}
 </div>
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
 to="/mindfolios/new"
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
 to={`/mindfolios/${p.id}`} 
 className="group bg-slate-800/50 border border-slate-700 rounded-xl p-6 hover:bg-slate-800 hover:border-slate-600 transition-all hover:shadow-xl hover:scale-105"
 >
 {/* Master Mindfolio Badge */}
 {p.is_master && (
 <MasterMindfolioBadge
 broker={p.broker}
 autoSync={p.auto_sync}
 lastSync={p.last_sync}
 syncStatus={p.sync_status}
 />
 )}
 
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

 {/* Template Selection Modal */}
 <MindfolioTemplateModal
 isOpen={showTemplateModal}
 onClose={() => setShowTemplateModal(false)}
 onCreateFromTemplate={async (templateData) => {
 await pfClient.create(templateData.name, templateData.starting_balance);
 // Refresh list
 const data = await pfClient.list();
 setItems(data);
 }}
 />
 </>
 );
}
