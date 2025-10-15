import React from "react";

export default function TopMindfolios({ limit = 3 }) {
  // TODO: Replace with real API data
  const top = [
    { id: "pf_abc", name: "Main Trading", value: 75000, pnl_today: 1500 },
    { id: "pf_def", name: "Income Strategy", value: 45000, pnl_today: 850 },
    { id: "pf_ghi", name: "Experimental", value: 5000, pnl_today: 100 }
  ].slice(0, limit);

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4">
      {top.map((pf) => (
        <div key={pf.id} className="bg-slate-900/60 border border-slate-700 rounded-lg p-4 flex flex-col gap-2">
          <div className="text-white font-semibold text-lg">{pf.name}</div>
          <div className="text-gray-400 text-sm">ID: {pf.id}</div>
          <div className="text-green-400 font-bold text-xl">${pf.value.toLocaleString()}</div>
          <div className="text-sm text-gray-400">Today's P&L: <span className="text-green-400">${pf.pnl_today}</span></div>
        </div>
      ))}
    </div>
  );
}
