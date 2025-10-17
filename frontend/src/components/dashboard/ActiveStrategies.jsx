import React from "react";

export default function ActiveStrategies({ totalStrategies = 0, totalPremium = 0, expiringThisWeek = 0 }) {
 return (
 <div className="bg-[#0a0e1a] border border-[#1a1f26] rounded-lg p-4 mt-6">
 <h3 className="text-[20px] text-[rgb(252, 251, 255)] mb-4"> Active Strategies Summary</h3>
 <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
 <div className="bg-[#0a0e1a] border border-[#1a1f26] rounded-lg p-3 text-center">
 <div className="text-[20px] text-blue-400">{totalStrategies}</div>
 <div className="text-[14px] text-gray-400 mt-1">Active Positions</div>
 </div>
 <div className="bg-[#0a0e1a] border border-[#1a1f26] rounded-lg p-3 text-center">
 <div className="text-[20px] text-green-400">${totalPremium.toLocaleString()}</div>
 <div className="text-[14px] text-gray-400 mt-1">Total Premium Collected</div>
 </div>
 <div className="bg-[#0a0e1a] border border-[#1a1f26] rounded-lg p-3 text-center">
 <div className="text-[20px] text-orange-400">{expiringThisWeek}</div>
 <div className="text-[14px] text-gray-400 mt-1">Expiring This Week</div>
 </div>
 </div>
 </div>
 );
}
