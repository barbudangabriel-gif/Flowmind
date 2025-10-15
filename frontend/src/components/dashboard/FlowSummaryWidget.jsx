import React from "react";
import { Link } from "react-router-dom";

export default function FlowSummaryWidget({ title = "📊 Options Flow", data = [], showSentiment = true, ctaLink = "/flow" }) {
  return (
    <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-6 hover:border-slate-600 transition-colors">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-white">{title}</h3>
        <Link to={ctaLink} className="text-sm text-blue-400 hover:text-blue-300">
          View All →
        </Link>
      </div>

      {data.length === 0 ? (
        <div className="text-center py-8 text-gray-500">No flow data available</div>
      ) : (
        <div className="space-y-3">
          {data.map((item, idx) => (
            <div key={idx} className="bg-slate-900/60 border border-slate-700 rounded-lg p-3 flex justify-between items-center">
              <div>
                <div className="text-white font-bold text-lg">{item.symbol}</div>
                {showSentiment && (
                  <div className={`text-sm ${item.sentiment === 'bullish' ? 'text-green-400' : item.sentiment === 'bearish' ? 'text-red-400' : 'text-gray-400'}`}>
                    {item.sentiment?.toUpperCase()}
                  </div>
                )}
              </div>
              <div className="text-right">
                <div className="text-green-400 font-bold">${(item.net_premium / 1000000).toFixed(1)}M</div>
                <div className="text-xs text-gray-400">Net Premium</div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
