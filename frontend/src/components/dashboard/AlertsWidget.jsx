import React from "react";

export default function AlertsWidget({ alerts = [], types = [], limit = 5 }) {
  const getSeverityColor = (severity) => {
    if (severity === "error") return "border-red-500 bg-red-500/10";
    if (severity === "warning") return "border-yellow-500 bg-yellow-500/10";
    return "border-blue-500 bg-blue-500/10";
  };

  const getSeverityIcon = (severity) => {
    if (severity === "error") return "🔴";
    if (severity === "warning") return "⚠️";
    return "ℹ️";
  };

  return (
    <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-6">
      <h3 className="text-lg font-semibold text-white mb-4">🚨 Recent Alerts</h3>
      {alerts.length === 0 ? (
        <div className="text-center py-8 text-gray-500">No recent alerts</div>
      ) : (
        <div className="space-y-3 max-h-64 overflow-y-auto">
          {alerts.slice(0, limit).map((alert, idx) => (
            <div key={idx} className={`border-l-4 p-3 rounded ${getSeverityColor(alert.severity)}`}>
              <div className="flex items-start gap-2">
                <span className="text-lg">{getSeverityIcon(alert.severity)}</span>
                <div className="flex-1">
                  <div className="text-white text-sm font-semibold">{alert.message}</div>
                  <div className="text-xs text-gray-400 mt-1">
                    {new Date(alert.timestamp).toLocaleString()} • {alert.type}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
