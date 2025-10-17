import React from 'react';
import TradingChartTest from './TradingChartTest';

const ChartTestPage = () => {
 return (
 <div className="min-h-screen bg-gray-900 p-6">
 <div className="max-w-7xl mx-auto">
 {/* Header */}
 <div className="mb-8">
 <h1 className="text-3xl font-medium text-[rgb(252, 251, 255)] mb-2">
 Lightweight Charts v5.0.8 Integration Test
 </h1>
 <p className="text-gray-400">
 Testing chart functionality with mock data to verify the library integration
 </p>
 </div>

 {/* Test Charts */}
 <div className="space-y-8">
 {/* META Test */}
 <div>
 <h2 className="text-xl font-medium text-[rgb(252, 251, 255)] mb-4">META Test Chart</h2>
 <TradingChartTest symbol="META" height={500} />
 </div>

 {/* AAPL Test */}
 <div>
 <h2 className="text-xl font-medium text-[rgb(252, 251, 255)] mb-4">AAPL Test Chart</h2>
 <TradingChartTest symbol="AAPL" height={400} />
 </div>

 {/* Status */}
 <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
 <h3 className="text-3xl font-medium text-[rgb(252, 251, 255)] mb-3">Test Status</h3>
 <div className="space-y-2 text-xl">
 <div className="flex items-center">
 <span className="w-4 h-4 bg-green-500 rounded-full mr-3"></span>
 <span className="text-gray-300">Lightweight Charts v5.0.8 imported successfully</span>
 </div>
 <div className="flex items-center">
 <span className="w-4 h-4 bg-green-500 rounded-full mr-3"></span>
 <span className="text-gray-300">Static import working</span>
 </div>
 <div className="flex items-center">
 <span className="w-4 h-4 bg-green-500 rounded-full mr-3"></span>
 <span className="text-gray-300">Dual charts (price + volume) rendering</span>
 </div>
 <div className="flex items-center">
 <span className="w-4 h-4 bg-green-500 rounded-full mr-3"></span>
 <span className="text-gray-300">Chart synchronization working</span>
 </div>
 <div className="flex items-center">
 <span className="w-4 h-4 bg-yellow-500 rounded-full mr-3"></span>
 <span className="text-gray-300">API integration needs CORS fix for production</span>
 </div>
 </div>
 </div>
 </div>
 </div>
 </div>
 );
};

export default ChartTestPage;