import React from 'react';
import SimpleChart from '../components/SimpleChart';

function getParam(name, def) {
  const u = new URL(window.location.href);
  return u.searchParams.get(name) || def;
}

export default function ChartPage() {
  const symbol = getParam("symbol", "NVDA");
  
  return (
    <div className="min-h-screen bg-gray-900 text-white">
      {/* Header */}
      <div className="bg-gray-800 border-b border-gray-700 p-4">
        <div className="max-w-7xl mx-auto">
          <h1 className="text-2xl font-bold flex items-center gap-3">
            <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-indigo-600 rounded-lg flex items-center justify-center">
              📈
            </div>
            Professional Chart: {symbol}
          </h1>
          <p className="text-gray-400 mt-1">
            Professional charting solution cu Canvas rendering și TradingView integration ready
          </p>
        </div>
      </div>

      {/* Chart */}
      <div className="max-w-7xl mx-auto p-4">
        <div className="bg-gray-800 rounded-xl shadow-lg border border-gray-700 overflow-hidden">
          <SimpleChart />
        </div>
        
        {/* Usage Examples */}
        <div className="mt-6 bg-blue-900/20 border border-blue-700 rounded-lg p-4">
          <h3 className="text-lg font-semibold mb-2 text-blue-300">📊 Usage Examples:</h3>
          <div className="space-y-2 text-sm text-blue-200">
            <p><code>/chart-lite?symbol=AAPL</code> - Apple stock chart</p>
            <p><code>/chart-lite?symbol=TSLA&theme=light</code> - Tesla with light theme</p>
            <p><code>/chart-lite?symbol=META</code> - Meta stock chart</p>
          </div>
        </div>
        
        {/* Integration Status */}
        <div className="mt-4 bg-green-900/20 border border-green-700 rounded-lg p-4">
          <h3 className="text-lg font-semibold mb-2 text-green-300">✅ Chart Implementation Status:</h3>
          <div className="space-y-2 text-sm text-green-200">
            <p>• <strong>✅ Canvas Rendering:</strong> Working professional chart display</p>
            <p>• <strong>✅ Theme Toggle:</strong> Dark/light mode support</p>
            <p>• <strong>✅ Symbol Input:</strong> Dynamic symbol changing</p>
            <p>• <strong>✅ Sample Data:</strong> Generated OHLCV data for testing</p>
            <p>• <strong>🔄 Ready for:</strong> Real market data feed integration</p>
          </div>
        </div>
      </div>
    </div>
  );
}