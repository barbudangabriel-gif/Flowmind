import React from "react";

export default function DarkPoolWidget({ title = "🌊 Dark Pool Highlights", data = [], threshold = 1000000 }) {
  return (
    <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-6 hover:border-slate-600 transition-colors">
      <h3 className="text-lg font-semibold text-white mb-4">{title}</h3>

      {data.length === 0 ? (
        <div className="text-center py-8 text-gray-500">No significant dark pool activity</div>
      ) : (
        <div className="space-y-3">
          {data.filter(item => item.premium >= threshold).map((item, idx) => (
            <div key={idx} className="bg-slate-900/60 border border-slate-700 rounded-lg p-3 flex justify-between items-center">
              <div>
                <div className="text-white font-bold text-lg">{item.symbol}</div>
                <div className="text-sm text-gray-400">Volume: {item.volume.toLocaleString()}</div>
              </div>
              <div className="text-right">
                <div className="text-purple-400 font-bold">${(item.premium / 1000000).toFixed(1)}M</div>
                <div className="text-xs text-gray-400">Premium</div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
