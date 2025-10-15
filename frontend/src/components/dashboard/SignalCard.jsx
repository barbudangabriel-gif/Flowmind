import React from "react";
import { Link } from "react-router-dom";

export default function SignalCard({ title, data = [], fields = [], emptyText = "No signals available", ctaLink = "#" }) {
  return (
    <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-6 hover:border-slate-600 transition-colors">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-white">{title}</h3>
        <Link to={ctaLink} className="text-sm text-blue-400 hover:text-blue-300">
          View All →
        </Link>
      </div>

      {data.length === 0 ? (
        <div className="text-center py-8 text-gray-500">{emptyText}</div>
      ) : (
        <div className="space-y-3">
          {data.slice(0, 5).map((item, idx) => (
            <div key={idx} className="bg-slate-900/60 border border-slate-700 rounded-lg p-3 flex justify-between items-center">
              <div className="space-y-1">
                <div className="text-white font-semibold">{item[fields[0]]}</div>
                <div className="text-sm text-gray-400">{fields[1]}: {item[fields[1]]}</div>
              </div>
              <div className="text-right space-y-1">
                {fields[2] && <div className="text-green-400 font-bold">{item[fields[2]]}</div>}
                {fields[3] && <div className="text-sm text-gray-400">{item[fields[3]]}</div>}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
