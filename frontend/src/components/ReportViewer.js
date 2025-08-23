import React from 'react';

export default function ReportViewer() {
  const src = '/reports/flowmind_summary.html?v=' + Date.now();
  return (
    <div className="min-h-screen bg-slate-900 text-white p-4">
      <div className="max-w-7xl mx-auto bg-slate-800 border border-slate-700 rounded-xl overflow-hidden shadow">
        <div className="px-4 py-3 border-b border-slate-700 flex items-center justify-between">
          <div className="text-lg font-semibold">Project Report (PDF preview)</div>
          <a href="/reports/flowmind_summary.html" target="_blank" rel="noopener noreferrer" className="text-sm text-blue-300 hover:text-blue-200 underline">Open in new tab</a>
        </div>
        <div style={{ height: 'calc(100vh - 160px)' }}>
          <iframe title="report" src={src} style={{ width: '100%', height: '100%', border: 0, background: '#0b1220' }} />
        </div>
      </div>
    </div>
  );
}