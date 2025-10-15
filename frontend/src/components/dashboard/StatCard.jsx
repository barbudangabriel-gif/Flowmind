import React from "react";

export default function StatCard({ title, value, change, percentage, subtitle, icon, gradient }) {
  return (
    <div className={`bg-slate-800/50 border border-slate-700 rounded-lg p-6 hover:border-slate-600 transition-colors shadow-lg ${gradient ? `bg-gradient-to-br ${gradient}` : ''}`}>
      <div className="flex items-center gap-3 mb-2">
        <span className="text-2xl">{icon}</span>
        <div className="text-lg font-semibold text-white">{title}</div>
      </div>
      <div className="text-3xl font-bold text-green-400">{value?.toLocaleString?.() ?? value}</div>
      {subtitle && <div className="text-sm text-gray-400 mt-1">{subtitle}</div>}
      {(change || percentage) && (
        <div className="text-sm mt-2">
          {change && <span className={change >= 0 ? "text-green-400" : "text-red-400"}>{change >= 0 ? "+" : ""}{change.toLocaleString?.() ?? change}</span>}
          {percentage && <span className="ml-2 text-gray-400">({percentage > 0 ? "+" : ""}{percentage}%)</span>}
        </div>
      )}
    </div>
  );
}
