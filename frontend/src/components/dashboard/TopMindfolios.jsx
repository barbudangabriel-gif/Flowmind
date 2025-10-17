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
 <div key={pf.id} className="bg-[#0a0e1a] border border-[#1a1f26] rounded-lg p-4 flex flex-col gap-2">
 <div className="text-[rgb(252, 251, 255)] text-[20px]">{pf.name}</div>
 <div className="text-gray-400 text-xl">ID: {pf.id}</div>
 <div className="text-green-400 text-xl">${pf.value.toLocaleString()}</div>
 <div className="text-xl text-gray-400">Today's P&L: <span className="text-green-400">${pf.pnl_today}</span></div>
 </div>
 ))}
 </div>
 );
}
