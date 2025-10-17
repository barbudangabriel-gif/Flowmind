import React from 'react';
import TradeStationAuth from './TradeStationAuth';

const SettingsPage = () => {
 return (
 <div className="min-h-screen bg-gray-900 p-6">
 <div className="max-w-4xl mx-auto">
 {/* Header */}
 <div className="mb-8">
 <h1 className="text-3xl font-medium text-[rgb(252, 251, 255)] mb-2">
 FlowMind Analytics Settings
 </h1>
 <p className="text-gray-400">
 Manage your platform connections and configuration
 </p>
 </div>

 {/* TradeStation Authentication Section */}
 <div className="mb-8">
 <h2 className="text-2xl font-medium text-[rgb(252, 251, 255)] mb-4">
 🔐 API Connections
 </h2>
 <TradeStationAuth />
 </div>

 {/* Additional Settings Sections */}
 <div className="space-y-8">
 {/* Theme Settings */}
 <div className="bg-gray-900 p-6 rounded-lg border border-gray-700">
 <h3 className="text-xl font-medium text-[rgb(252, 251, 255)] mb-4"> Theme Settings</h3>
 <div className="text-gray-400">
 <p>Dark theme is currently active (matches trading platform standards)</p>
 </div>
 </div>

 {/* Chart Settings */}
 <div className="bg-gray-900 p-6 rounded-lg border border-gray-700">
 <h3 className="text-xl font-medium text-[rgb(252, 251, 255)] mb-4"> Chart Configuration</h3>
 <div className="space-y-3 text-gray-400">
 <div className="flex items-center justify-between">
 <span>Chart Library:</span>
 <span className="text-[rgb(252, 251, 255)] font-medium">ApexCharts Professional</span>
 </div>
 <div className="flex items-center justify-between">
 <span>Data Source Priority:</span>
 <span className="text-[rgb(252, 251, 255)] font-medium">TradeStation API</span>
 </div>
 <div className="flex items-center justify-between">
 <span>Price Scale Position:</span>
 <span className="text-[rgb(252, 251, 255)] font-medium">Right Side</span>
 </div>
 <div className="flex items-center justify-between">
 <span>Default Timeframe:</span>
 <span className="text-[rgb(252, 251, 255)] font-medium">Daily (1D)</span>
 </div>
 </div>
 </div>

 {/* Data Sources */}
 <div className="bg-gray-900 p-6 rounded-lg border border-gray-700">
 <h3 className="text-xl font-medium text-[rgb(252, 251, 255)] mb-4">🔌 Data Sources Status</h3>
 <div className="space-y-3">
 <div className="flex items-center justify-between p-3 bg-gray-800 rounded-lg">
 <div>
 <div className="text-[rgb(252, 251, 255)] font-medium">TradeStation API</div>
 <div className="text-gray-400 text-xl">Real-time market data & trading</div>
 </div>
 <div className="text-yellow-400 font-medium">Authentication Required</div>
 </div>
 <div className="flex items-center justify-between p-3 bg-gray-800 rounded-lg">
 <div>
 <div className="text-[rgb(252, 251, 255)] font-medium">Investment Scoring Engine</div>
 <div className="text-gray-400 text-xl">AI-powered stock analysis</div>
 </div>
 <div className="text-green-400 font-medium">Active</div>
 </div>
 <div className="flex items-center justify-between p-3 bg-gray-800 rounded-lg">
 <div>
 <div className="text-[rgb(252, 251, 255)] font-medium">Technical Analysis Agent</div>
 <div className="text-gray-400 text-xl">Smart Money Concepts & indicators</div>
 </div>
 <div className="text-green-400 font-medium">Active</div>
 </div>
 </div>
 </div>

 {/* System Information */}
 <div className="bg-gray-900 p-6 rounded-lg border border-gray-700">
 <h3 className="text-xl font-medium text-[rgb(252, 251, 255)] mb-4"> System Information</h3>
 <div className="grid grid-cols-2 gap-4 text-xl">
 <div>
 <span className="text-gray-400">Platform:</span>
 <span className="text-[rgb(252, 251, 255)] ml-2">FlowMind Analytics</span>
 </div>
 <div>
 <span className="text-gray-400">Version:</span>
 <span className="text-[rgb(252, 251, 255)] ml-2">Professional v2.0</span>
 </div>
 <div>
 <span className="text-gray-400">Backend:</span>
 <span className="text-[rgb(252, 251, 255)] ml-2">FastAPI Python</span>
 </div>
 <div>
 <span className="text-gray-400">Frontend:</span>
 <span className="text-[rgb(252, 251, 255)] ml-2">React 19 + TailwindCSS</span>
 </div>
 <div>
 <span className="text-gray-400">Charts:</span>
 <span className="text-[rgb(252, 251, 255)] ml-2">ApexCharts Professional</span>
 </div>
 <div>
 <span className="text-gray-400">Database:</span>
 <span className="text-[rgb(252, 251, 255)] ml-2">MongoDB</span>
 </div>
 </div>
 </div>
 </div>
 </div>
 </div>
 );
};

export default SettingsPage;