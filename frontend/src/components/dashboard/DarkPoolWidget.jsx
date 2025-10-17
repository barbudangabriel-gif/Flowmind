import React from "react";

export default function DarkPoolWidget({ title = "🌊 Dark Pool Highlights", data = [], threshold = 1000000 }) {
 return (
 <div className="bg-[#0a0e1a] border border-[#1a1f26] rounded-lg p-4 hover:border-[#1a1f26] transition-colors">
 <h3 className="text-[20px] text-[rgb(252, 251, 255)] mb-4">{title}</h3>

 {data.length === 0 ? (
 <div className="text-center py-8 text-gray-500">No significant dark pool activity</div>
 ) : (
 <div className="space-y-3">{data.filter(item => item.premium >= threshold).map((item, idx) => (
 <div key={idx} className="bg-[#0a0e1a] border border-[#1a1f26] rounded-lg p-2 flex justify-between items-center">
 <div>
 <div className="text-[rgb(252, 251, 255)] text-base">{item.symbol}</div>
 <div className="text-xl text-gray-400">Volume: {item.volume.toLocaleString()}</div>
 </div>
 <div className="text-right">
 <div className="text-purple-400">${(item.premium / 1000000).toFixed(1)}M</div>
 <div className="text-lg text-gray-400">Premium</div>
 </div>
 </div>
 ))}
 </div>
 )}
 </div>
 );
}
