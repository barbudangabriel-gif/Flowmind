import React, { useEffect, useState } from "react";
import { pfClient } from "../services/portfolioClient";
import { Link } from "react-router-dom";

export default function PortfoliosList() {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [err, setErr] = useState("");

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

  if (loading) {
    return (
      <div className="p-8">
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
            <div className="text-gray-400">Loading portfolios...</div>
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
            <span className="text-2xl">⚠️</span>
            <div>
              <div className="font-semibold text-red-400 mb-2">Error Loading Portfolios</div>
              <div className="text-sm text-gray-400">{err}</div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Calculate totals
  const totalValue = items.reduce((sum, pf) => sum + (pf.cash_balance || 0), 0);
  const totalPortfolios = items.length;

  return (
    <div className="p-8 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white mb-2">💼 Portfolios</h1>
          <p className="text-gray-400">Manage your trading portfolios and track performance</p>
        </div>
        <Link 
          to="/portfolios/new" 
          className="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-semibold transition-all hover:scale-105 shadow-lg"
        >
          + Create Portfolio
        </Link>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-6">
          <div className="text-sm text-gray-400 mb-1">Total Portfolios</div>
          <div className="text-3xl font-bold text-white">{totalPortfolios}</div>
        </div>
        <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-6">
          <div className="text-sm text-gray-400 mb-1">Total Cash</div>
          <div className="text-3xl font-bold text-green-400">
            ${totalValue.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
          </div>
        </div>
        <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-6">
          <div className="text-sm text-gray-400 mb-1">Active Modules</div>
          <div className="text-3xl font-bold text-blue-400">
            {items.reduce((sum, pf) => sum + (pf.modules?.length || 0), 0)}
          </div>
        </div>
      </div>
      
      {items.length === 0 ? (
        <div className="text-center py-16 bg-slate-800/30 border border-slate-700 rounded-lg">
          <div className="text-6xl mb-4">📊</div>
          <div className="text-xl text-gray-300 mb-2">No portfolios yet</div>
          <div className="text-gray-500 mb-6">Create your first portfolio to start tracking your trades</div>
          <Link 
            to="/portfolios/new"
            className="inline-block px-8 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-semibold transition-all hover:scale-105"
          >
            🚀 Create Your First Portfolio
          </Link>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {items.map(p => {
            const statusColors = {
              'ACTIVE': 'bg-green-500/20 text-green-400 border-green-500/30',
              'PAUSED': 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30',
              'CLOSED': 'bg-gray-500/20 text-gray-400 border-gray-500/30'
            };
            
            return (
              <Link 
                key={p.id} 
                to={`/portfolios/${p.id}`} 
                className="group bg-slate-800/50 border border-slate-700 rounded-xl p-6 hover:bg-slate-800 hover:border-slate-600 transition-all hover:shadow-xl hover:scale-105"
              >
                {/* Header */}
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <div className="text-xl font-bold text-white group-hover:text-blue-400 transition-colors mb-1">
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
                  <div className="text-2xl font-bold text-green-400">
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
      )}
    </div>
  );
}