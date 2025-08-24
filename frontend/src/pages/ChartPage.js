import React from 'react';
import LightChartDemo from '../components/LightChartDemo';

function getParam(name, def) {
  const u = new URL(window.location.href);
  return u.searchParams.get(name) || def;
}

export default function ChartPage() {
  const symbol = getParam("symbol", "NVDA"); // changeable from URL
  const interval = getParam("interval", "D");
  const theme = getParam("theme", "dark");
  
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
            TradingView Lightweight Charts cu candlesticks, volume și indicators
          </p>
        </div>
      </div>

      {/* Chart */}
      <div className="max-w-7xl mx-auto p-4">
        <div className="bg-gray-800 rounded-xl shadow-lg border border-gray-700 overflow-hidden">
          <LightChartDemo />
        </div>
        
        {/* Usage Examples */}
        <div className="mt-6 bg-blue-900/20 border border-blue-700 rounded-lg p-4">
          <h3 className="text-lg font-semibold mb-2 text-blue-300">📊 Usage Examples:</h3>
          <div className="space-y-2 text-sm text-blue-200">
            <p><code>/chart-lite?symbol=AAPL</code> - Apple stock chart</p>
            <p><code>/chart-lite?symbol=TSLA&interval=60&theme=light</code> - Tesla with light theme</p>
            <p><code>/chart-lite?symbol=NVDA&interval=D&theme=dark</code> - NVIDIA daily chart</p>
          </div>
        </div>
        
        {/* Integration Notes */}
        <div className="mt-4 bg-gray-800 border border-gray-600 rounded-lg p-4">
          <h3 className="text-lg font-semibold mb-2 text-gray-300">🔧 Integration Notes:</h3>
          <div className="space-y-2 text-sm text-gray-400">
            <p>• <strong>Demo Data:</strong> Currently using generated OHLCV data</p>
            <p>• <strong>Real Feed:</strong> Replace genDemoOHLCV() with your API data</p>
            <p>• <strong>Format:</strong> {`{ time: UNIX_seconds, open, high, low, close, volume }`}</p>
            <p>• <strong>Features:</strong> Candlesticks + Volume + SMA(20) + Theme toggle</p>
          </div>
        </div>
      </div>
    </div>
  );
}