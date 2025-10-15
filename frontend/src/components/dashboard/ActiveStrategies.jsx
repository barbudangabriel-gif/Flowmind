import React from "react";

export default function ActiveStrategies({ totalStrategies = 0, totalPremium = 0, expiringThisWeek = 0 }) {
  return (
    <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-6 mt-6">
      <h3 className="text-lg font-semibold text-white mb-4">📊 Active Strategies Summary</h3>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-slate-900/60 border border-slate-700 rounded-lg p-4 text-center">
          <div className="text-3xl font-bold text-blue-400">{totalStrategies}</div>
          <div className="text-sm text-gray-400 mt-1">Active Positions</div>
        </div>
        <div className="bg-slate-900/60 border border-slate-700 rounded-lg p-4 text-center">
          <div className="text-3xl font-bold text-green-400">${totalPremium.toLocaleString()}</div>
          <div className="text-sm text-gray-400 mt-1">Total Premium Collected</div>
        </div>
        <div className="bg-slate-900/60 border border-slate-700 rounded-lg p-4 text-center">
          <div className="text-3xl font-bold text-orange-400">{expiringThisWeek}</div>
          <div className="text-sm text-gray-400 mt-1">Expiring This Week</div>
        </div>
      </div>
    </div>
  );
}
