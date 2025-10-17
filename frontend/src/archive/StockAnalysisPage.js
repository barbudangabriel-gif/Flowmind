import React from 'react';
import { useParams } from 'react-router-dom';

const StockAnalysisPage = () => {
 const { symbol } = useParams();

 return (
 <div className="min-h-screen bg-gray-900 text-[rgb(252, 251, 255)] p-8">
 <div className="max-w-7xl mx-auto">
 <h1 className="text-3xl font-medium mb-6">Stock Analysis: {symbol}</h1>
 <div className="bg-gray-800 rounded-lg p-6">
 <p className="text-gray-400">
 Stock analysis for {symbol} is currently being updated. 
 Please check back soon for detailed analysis.
 </p>
 <div className="mt-4 p-4 bg-blue-900 rounded border border-blue-700">
 <h2 className="text-3xl font-medium mb-2">Coming Soon:</h2>
 <ul className="text-xl space-y-1">
 <li>• Investment Analysis</li>
 <li>• Technical Analysis</li>
 <li>• Options Strategies</li>
 <li>• Fundamentals</li>
 <li>• Real-time Data</li>
 </ul>
 </div>
 </div>
 </div>
 </div>
 );
};

export default StockAnalysisPage;