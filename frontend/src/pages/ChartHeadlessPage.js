import React from 'react';
import ChartController from '../components/ChartController';

export default function ChartHeadlessPage() {
  // Optional custom fetcher to map your backend response
  const fetcher = async ({ symbol, timeframe, limit }) => {
    try {
      // Example: if your backend uses e.g., /api/kline?symbol=NVDA&tf=60&n=500
      const API_BASE = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;
      const response = await fetch(`${API_BASE}/api/market/chart/${symbol}?timeframe=${timeframe}&limit=${limit}`);
      
      if (!response.ok) {
        // Fallback to demo data if API not available
        console.warn(`Backend chart API not available, using demo data for ${symbol}`);
        throw new Error(`HTTP ${response.status}`);
      }
      
      const data = await response.json();
      
      // Map backend response to normalized format
      return data.map((bar) => ({
        time: bar.time || bar.timestamp || Math.floor(Date.now() / 1000),
        open: parseFloat(bar.open || bar.o || 0),
        high: parseFloat(bar.high || bar.h || 0),
        low: parseFloat(bar.low || bar.l || 0),
        close: parseFloat(bar.close || bar.c || 0),
        volume: parseInt(bar.volume || bar.v || 0),
      }));
      
    } catch (error) {
      console.warn('Chart API fetch failed, using demo data:', error.message);
      // Fallback to demo data generation
      return null; // This will trigger the default fetcher in useOHLCV
    }
  };

  // Optional WebSocket URL builder (if you have live data)
  const wsUrl = ({ symbol, timeframe }) => {
    // Example: return `wss://your-ws.example/ohlcv?symbol=${encodeURIComponent(symbol)}&tf=${timeframe}`;
    return null; // No WebSocket for now
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <div className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 p-4">
        <div className="max-w-7xl mx-auto">
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white flex items-center gap-3">
            <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-indigo-600 rounded-lg flex items-center justify-center text-white">
              📈
            </div>
            Advanced Chart Controller
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">
            Professional TradingView Lightweight Charts cu OHLCV Hook + SWR caching + WebSocket support
          </p>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto p-4">
        {/* Chart Controller */}
        <ChartController 
          defaultSymbol="NVDA" 
          defaultTf="D" 
          limit={500} 
          fetcher={fetcher} 
          wsUrl={null /* or wsUrl */} 
        />
        
        {/* Usage Guide */}
        <div className="mt-6 grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Features */}
          <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-3">✨ Features</h3>
            <ul className="space-y-2 text-sm text-gray-600 dark:text-gray-400">
              <li>• <strong>TradingView Lightweight Charts</strong> - Professional candlestick charts</li>
              <li>• <strong>SWR Caching</strong> - Intelligent data caching și deduplication</li>
              <li>• <strong>WebSocket Support</strong> - Real-time data updates (when available)</li>
              <li>• <strong>Timeframe Selection</strong> - 1m, 5m, 15m, 1h, 4h, Daily, Weekly</li>
              <li>• <strong>Theme Toggle</strong> - Dark/Light mode support</li>
              <li>• <strong>SMA Indicator</strong> - 20-period Simple Moving Average</li>
              <li>• <strong>Volume Display</strong> - Color-coded volume histogram</li>
              <li>• <strong>Auto-refresh</strong> - Configurable polling fallback</li>
            </ul>
          </div>

          {/* Integration */}
          <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-3">🔧 Integration</h3>
            <div className="space-y-3 text-sm text-gray-600 dark:text-gray-400">
              <div>
                <strong>Route:</strong>
                <code className="ml-2 px-2 py-1 bg-gray-100 dark:bg-gray-700 rounded">/chart-headless</code>
              </div>
              <div>
                <strong>Backend API:</strong>
                <code className="ml-2 px-2 py-1 bg-gray-100 dark:bg-gray-700 rounded">
                  GET /api/market/chart/{symbol}?timeframe=D&limit=300
                </code>
              </div>
              <div>
                <strong>Data Format:</strong>
                <code className="ml-2 px-2 py-1 bg-gray-100 dark:bg-gray-700 rounded text-xs">
                  {`{ time: UNIX, open, high, low, close, volume }`}
                </code>
              </div>
              <div>
                <strong>WebSocket:</strong>
                <span className="ml-2 text-gray-500">Ready for real-time integration</span>
              </div>
            </div>
          </div>
        </div>

        {/* Status */}
        <div className="mt-6 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-700 rounded-lg p-4">
          <h3 className="text-lg font-semibold text-blue-900 dark:text-blue-300 mb-2">📊 Implementation Status</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
            <div className="space-y-1">
              <div className="font-medium text-blue-800 dark:text-blue-200">Chart Engine:</div>
              <div className="text-blue-700 dark:text-blue-300">✅ TradingView Lightweight Charts</div>
              <div className="text-blue-700 dark:text-blue-300">✅ Candlestick + Volume + SMA</div>
              <div className="text-blue-700 dark:text-blue-300">✅ Theme support</div>
            </div>
            <div className="space-y-1">
              <div className="font-medium text-blue-800 dark:text-blue-200">Data Management:</div>
              <div className="text-blue-700 dark:text-blue-300">✅ SWR caching system</div>
              <div className="text-blue-700 dark:text-blue-300">✅ Auto-refresh polling</div>
              <div className="text-blue-700 dark:text-blue-300">🔄 WebSocket ready</div>
            </div>
            <div className="space-y-1">
              <div className="font-medium text-blue-800 dark:text-blue-200">Integration:</div>
              <div className="text-blue-700 dark:text-blue-300">✅ Backend API ready</div>
              <div className="text-blue-700 dark:text-blue-300">✅ URL parameters</div>
              <div className="text-blue-700 dark:text-blue-300">✅ Error handling</div>
            </div>
          </div>
        </div>

        {/* Examples */}
        <div className="mt-6 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-3">🎯 Usage Examples</h3>
          <div className="space-y-2 text-sm text-gray-600 dark:text-gray-400">
            <p><code>/chart-headless</code> - Default NVDA daily chart</p>
            <p><code>/chart-headless?symbol=AAPL&tf=1h</code> - Apple hourly chart</p>
            <p><code>/chart-headless?symbol=TSLA&tf=5m</code> - Tesla 5-minute chart</p>
          </div>
        </div>
      </div>
    </div>
  );
}