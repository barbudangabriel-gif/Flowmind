import React from 'react';
import ProfessionalTradingChart from './ProfessionalTradingChart';

const ProfessionalChartTest = () => {
  return (
    <div className="min-h-screen bg-gray-900 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-white mb-4">
            🚀 Professional Trading Charts - ApexCharts
          </h1>
          <p className="text-gray-400 text-lg">
            Chart-uri profesionale de trading cu candlestick și volume pentru FlowMind Analytics
          </p>
        </div>

        {/* Professional Charts */}
        <div className="space-y-8">
          {/* META Chart */}
          <div>
            <h2 className="text-2xl font-semibold text-white mb-4 flex items-center">
              📊 META Professional Chart
              <span className="ml-3 text-purple-400 text-lg">ApexCharts Implementation</span>
            </h2>
            <ProfessionalTradingChart symbol="META" height={600} />
          </div>

          {/* AAPL Chart */}
          <div>
            <h2 className="text-2xl font-semibold text-white mb-4 flex items-center">
              🍎 AAPL Professional Chart
              <span className="ml-3 text-blue-400 text-lg">Interactive Tools</span>
            </h2>
            <ProfessionalTradingChart symbol="AAPL" height={600} />
          </div>

          {/* GOOGL Chart */}
          <div>
            <h2 className="text-2xl font-semibold text-white mb-4 flex items-center">
              🌐 GOOGL Professional Chart
              <span className="ml-3 text-green-400 text-lg">Real-time Data</span>
            </h2>
            <ProfessionalTradingChart symbol="GOOGL" height={600} />
          </div>

          {/* Features Overview */}
          <div className="bg-gradient-to-r from-purple-900 to-blue-900 p-8 rounded-lg border border-gray-700">
            <h3 className="text-2xl font-semibold text-white mb-6">
              ✨ Professional Features Implemented
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              <div className="bg-gray-800 p-4 rounded-lg border border-gray-600">
                <div className="text-purple-400 text-xl font-bold mb-2">📈 Candlestick Charts</div>
                <div className="text-gray-300 text-sm">
                  Professional OHLC candlestick visualization with realistic price movements and color coding
                </div>
              </div>
              <div className="bg-gray-800 p-4 rounded-lg border border-gray-600">
                <div className="text-blue-400 text-xl font-bold mb-2">📊 Volume Analysis</div>
                <div className="text-gray-300 text-sm">
                  Synchronized volume charts with brush selection and correlation to price movement
                </div>
              </div>
              <div className="bg-gray-800 p-4 rounded-lg border border-gray-600">
                <div className="text-green-400 text-xl font-bold mb-2">🔧 Interactive Tools</div>
                <div className="text-gray-300 text-sm">
                  Zoom, pan, selection, download, and advanced chart navigation tools
                </div>
              </div>
              <div className="bg-gray-800 p-4 rounded-lg border border-gray-600">
                <div className="text-yellow-400 text-xl font-bold mb-2">🎨 Professional UI</div>
                <div className="text-gray-300 text-sm">
                  Dark theme, gradient headers, real-time price updates, and responsive design
                </div>
              </div>
              <div className="bg-gray-800 p-4 rounded-lg border border-gray-600">
                <div className="text-red-400 text-xl font-bold mb-2">📱 API Integration</div>
                <div className="text-gray-300 text-sm">
                  Real-time data from multiple sources with local development fallbacks
                </div>
              </div>
              <div className="bg-gray-800 p-4 rounded-lg border border-gray-600">
                <div className="text-indigo-400 text-xl font-bold mb-2">⚡ Performance</div>
                <div className="text-gray-300 text-sm">
                  Optimized rendering, smooth animations, and professional tooltip system
                </div>
              </div>
            </div>
          </div>

          {/* Comparison */}
          <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
            <h3 className="text-xl font-semibold text-white mb-4">🔄 Chart Solution Comparison</h3>
            <div className="space-y-3 text-sm">
              <div className="flex items-center">
                <span className="w-4 h-4 bg-red-500 rounded-full mr-3"></span>
                <span className="text-gray-300">
                  <strong>Lightweight Charts v5.0.8:</strong> React 19 compatibility issues, DOM manipulation conflicts
                </span>
              </div>
              <div className="flex items-center">
                <span className="w-4 h-4 bg-yellow-500 rounded-full mr-3"></span>
                <span className="text-gray-300">
                  <strong>Recharts Alternative:</strong> Basic functionality, limited trading features
                </span>
              </div>
              <div className="flex items-center">
                <span className="w-4 h-4 bg-green-500 rounded-full mr-3"></span>
                <span className="text-gray-300">
                  <strong>ApexCharts Professional:</strong> Full React 19 compatibility, professional trading features, interactive tools
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProfessionalChartTest;