import React from "react";

export default function SystemHealthWidget({ services = [] }) {
  const getStatusColor = (status) => {
    if (status === "connected") return "text-green-400";
    if (status === "fallback") return "text-yellow-400";
    return "text-red-400";
  };

  const getStatusIcon = (status) => {
    if (status === "connected") return "✅";
    if (status === "fallback") return "⚠️";
    return "❌";
  };

  return (
    <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-6">
      <h3 className="text-lg font-semibold text-white mb-4">🔧 System Health</h3>
      <div className="space-y-3">
        {services.map((service, idx) => (
          <div key={idx} className="bg-slate-900/60 border border-slate-700 rounded-lg p-3 flex justify-between items-center">
            <div className="flex items-center gap-3">
              <span className="text-xl">{getStatusIcon(service.status)}</span>
              <div>
                <div className="text-white font-semibold">{service.name}</div>
                {service.mode && <div className="text-xs text-gray-400">Mode: {service.mode}</div>}
                {service.fallback && <div className="text-xs text-yellow-400">Using in-memory fallback</div>}
              </div>
            </div>
            <div className={`font-bold ${getStatusColor(service.status)}`}>
              {service.status.toUpperCase()}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
