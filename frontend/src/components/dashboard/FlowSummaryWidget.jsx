import React from "react";
import { Link } from "react-router-dom";

export default function FlowSummaryWidget({ title = " Options Flow", data = [], showSentiment = true, ctaLink = "/flow" }) {
 return (
 <div className="bg-[#0a0e1a] border border-[#1a1f26] rounded-lg p-4 hover:border-[#1a1f26] transition-colors">
 <div className="flex items-center justify-between mb-4">
 <h3 className="text-[20px] text-[rgb(252, 251, 255)]">{title}</h3>
 <Link to={ctaLink} className="text-xl text-blue-400 hover:text-blue-300">
 View All →
 </Link>
 </div>

 {data.length === 0 ? (
 <div className="text-center py-8 text-gray-500">No flow data available</div>
 ) : (
 <div className="space-y-3">
 {data.map((item, idx) => (
 <div key={idx} className="bg-[#0a0e1a] border border-[#1a1f26] rounded-lg p-2 flex justify-between items-center">
 <div>
 <div className="text-[rgb(252, 251, 255)] text-base">{item.symbol}</div>
 {showSentiment && (
 <div className={`text-xl ${item.sentiment === 'bullish' ? 'text-green-400' : item.sentiment === 'bearish' ? 'text-red-400' : 'text-gray-400'}`}>
 {item.sentiment?.toUpperCase()}
 </div>
 )}
 </div>
 <div className="text-right">
 <div className="text-green-400">${(item.net_premium / 1000000).toFixed(1)}M</div>
 <div className="text-lg text-gray-400">Net Premium</div>
 </div>
 </div>
 ))}
 </div>
 )}
 </div>
 );
}
