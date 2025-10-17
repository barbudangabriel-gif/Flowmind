import React from "react";

export default function NewsTickerWidget({ sources = [], limit = 10 }) {
 // TODO: Replace with real API data
 const news = [
 { timestamp: "2025-10-15T10:30:00Z", headline: "Tesla Q3 earnings beat expectations", sentiment: "positive", source: "news" },
 { timestamp: "2025-10-15T09:15:00Z", headline: "Pelosi bought NVDA calls worth $2M", sentiment: "bullish", source: "congress" },
 { timestamp: "2025-10-15T08:45:00Z", headline: "Apple insider sold 50k shares", sentiment: "bearish", source: "insiders" }
 ].slice(0, limit);

 return (
 <div className="bg-[#0a0e1a] border border-[#1a1f26] rounded-lg p-4 mt-6">
 <h3 className="text-[20px] text-[rgb(252, 251, 255)] mb-4"> Breaking News & Activity</h3>
 <div className="space-y-2 max-h-64 overflow-y-auto">
 {news.map((item, idx) => (
 <div key={idx} className="bg-[#0a0e1a] border-l-4 border-blue-500 p-3 rounded">
 <div className="flex justify-between items-start">
 <div className="text-[rgb(252, 251, 255)] text-xl">{item.headline}</div>
 <div className="text-lg text-gray-500 ml-2">{new Date(item.timestamp).toLocaleTimeString()}</div>
 </div>
 <div className="text-lg text-gray-400 mt-1">Source: {item.source}</div>
 </div>
 ))}
 </div>
 </div>
 );
}
