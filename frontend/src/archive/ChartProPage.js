import React from 'react';
import ChartPro from '../components/ChartPro';

export default function ChartProPage() {
  // Custom fetcher for real backend integration
  const fetcher = async ({ symbol, timeframe, limit }) => {
    try {
      const API_BASE = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;
      const response = await fetch(`${API_BASE}/api/market/chart/${symbol}?timeframe=${timeframe}&limit=${limit}`);
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      
      const result = await response.json();
      
      if (result.status === 'success' && result.data) {
        return result.data;
      } else {
        throw new Error('Invalid API response');
      }
      
    } catch (error) {
      console.warn('Chart API error:', error.message);
      throw error;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 text-gray-900 dark:text-white">
      {/* Header */}
      <div className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold flex items-center gap-3">
                <div className="w-10 h-10 bg-gradient-to-r from-purple-500 to-pink-600 rounded-lg flex items-center justify-center text-white">
                  📊
                </div>
                Chart Pro+++
              </h1>
              <p className="text-gray-600 dark:text-gray-400 mt-1">
                Advanced TradingView charts cu persistent drawings, custom labels/colors, snap functionality și JSON import/export
              </p>
            </div>
            
            <div className="flex items-center gap-2 text-sm text-gray-500 dark:text-gray-400">
              <span className="w-2 h-2 bg-green-500 rounded-full"></span>
              Professional Trading Charts Pro
            </div>
          </div>
        </div>
      </div>

      {/* Main Chart */}
      <div className="max-w-7xl mx-auto px-4 py-6">
        <ChartPro 
          defaultSymbol="NVDA" 
          defaultTf="D" 
          limit={500} 
          fetcher={fetcher}
          wsUrl={null}
        />
      </div>

      {/* Enhanced Features Overview */}
      <div className="max-w-7xl mx-auto px-4 pb-6">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {/* Drawing Tools */}
          <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4">
            <h3 className="text-lg font-semibold mb-3 flex items-center gap-2">
              ✏️ Enhanced Drawing Tools
            </h3>
            <ul className="space-y-1 text-sm text-gray-600 dark:text-gray-400">
              <li>• <strong>Trendlines:</strong> 2-click trend analysis</li>
              <li>• <strong>H-Lines:</strong> Support/resistance levels</li>
              <li>• <strong>V-Lines:</strong> Time-based markers</li>
              <li>• <strong>Range Tool:</strong> Performance analysis</li>
              <li>• <strong>Custom Labels:</strong> Personal annotations</li>
              <li>• <strong>Color Coding:</strong> Visual organization</li>
            </ul>
          </div>

          {/* Persistence */}
          <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4">
            <h3 className="text-lg font-semibold mb-3 flex items-center gap-2">
              💾 Persistent Storage
            </h3>
            <ul className="space-y-1 text-sm text-gray-600 dark:text-gray-400">
              <li>• <strong>Auto-Save:</strong> Drawings saved per symbol+TF</li>
              <li>• <strong>LocalStorage:</strong> Cross-session persistence</li>
              <li>• <strong>JSON Export:</strong> Share analysis externally</li>
              <li>• <strong>JSON Import:</strong> Load shared drawings</li>
              <li>• <strong>Settings Sync:</strong> Indicator preferences saved</li>
            </ul>
          </div>

          {/* Smart Features */}
          <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4">
            <h3 className="text-lg font-semibold mb-3 flex items-center gap-2">
              🎯 Smart Features
            </h3>
            <ul className="space-y-1 text-sm text-gray-600 dark:text-gray-400">
              <li>• <strong>Snap to OHLC:</strong> Magnet to exact prices</li>
              <li>• <strong>Range Statistics:</strong> Automatic calculations</li>
              <li>• <strong>Color Management:</strong> Custom color picker</li>
              <li>• <strong>Label Editing:</strong> Real-time annotation</li>
              <li>• <strong>Smart Clearing:</strong> Storage + chart sync</li>
            </ul>
          </div>

          {/* Technical Analysis */}
          <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4">
            <h3 className="text-lg font-semibold mb-3 flex items-center gap-2">
              📈 Complete Analysis Suite
            </h3>
            <ul className="space-y-1 text-sm text-gray-600 dark:text-gray-400">
              <li>• <strong>Moving Averages:</strong> SMA + EMA</li>
              <li>• <strong>Bollinger Bands:</strong> Volatility analysis</li>
              <li>• <strong>RSI:</strong> Momentum oscillator</li>
              <li>• <strong>Volume Profile:</strong> Color-coded volume</li>
              <li>• <strong>Multi-Timeframe:</strong> 1m to Weekly</li>
            </ul>
          </div>
        </div>

        {/* Pro Features Highlight */}
        <div className="mt-6 bg-gradient-to-r from-purple-50 to-pink-50 dark:from-purple-900/20 dark:to-pink-900/20 border border-purple-200 dark:border-purple-700 rounded-lg p-6">
          <h3 className="text-xl font-bold text-purple-900 dark:text-purple-300 mb-4">🚀 Chart Pro+++ Ultimate Features</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div>
              <h4 className="font-semibold text-purple-800 dark:text-purple-200 mb-2">🎨 Advanced Drawing</h4>
              <ul className="space-y-1 text-sm text-purple-700 dark:text-purple-300">
                <li>✅ Persistent drawings per symbol+timeframe</li>
                <li>✅ Custom labels și colors pentru annotations</li>
                <li>✅ Snap to OHLC pentru precision drawing</li>
                <li>✅ Range analysis cu automatic statistics</li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold text-purple-800 dark:text-purple-200 mb-2">💾 Data Management</h4>
              <ul className="space-y-1 text-sm text-purple-700 dark:text-purple-300">
                <li>✅ LocalStorage persistence cross-sessions</li>
                <li>✅ JSON export/import pentru sharing</li>
                <li>✅ SWR caching pentru performance</li>
                <li>✅ Auto-refresh cu WebSocket support</li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold text-purple-800 dark:text-purple-200 mb-2">📊 Professional Tools</h4>
              <ul className="space-y-1 text-sm text-purple-700 dark:text-purple-300">
                <li>✅ Complete technical indicator suite</li>
                <li>✅ Multiple timeframe analysis</li>
                <li>✅ Interactive drawing management</li>
                <li>✅ Professional UI/UX design</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}