import React from "react";
import { Link } from "react-router-dom";

export default function SignalCard({ title, data = [], fields = [], emptyText = "No signals available", ctaLink = "#" }) {
 return (
 <div className="bg-[#0a0e1a] border border-[#1a1f26] rounded-lg p-4 hover:border-[#1a1f26] transition-colors">
 <div className="flex items-center justify-between mb-4">
 <h3 className="text-[20px] text-[rgb(252, 251, 255)]">{title}</h3>
 <Link to={ctaLink} className="text-xl text-blue-400 hover:text-blue-300">
 View All →
 </Link>
 </div>

 {data.length === 0 ? (
 <div className="text-center py-8 text-gray-500">{emptyText}</div>
 ) : (
 <div className="space-y-3">
 {data.slice(0, 5).map((item, idx) => (
 <div key={idx} className="bg-[#0a0e1a] border border-[#1a1f26] rounded-lg p-2 flex justify-between items-center">
 <div className="space-y-1">
 <div className="text-[rgb(252, 251, 255)]">{item[fields[0]]}</div>
 <div className="text-xl text-gray-400">{fields[1]}: {item[fields[1]]}</div>
 </div>
 <div className="text-right space-y-1">
 {fields[2] && <div className="text-green-400">{item[fields[2]]}</div>}
 {fields[3] && <div className="text-xl text-gray-400">{item[fields[3]]}</div>}
 </div>
 </div>
 ))}
 </div>
 )}
 </div>
 );
}
