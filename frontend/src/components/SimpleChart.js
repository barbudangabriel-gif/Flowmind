import React, { useEffect, useRef, useState } from 'react';

export default function SimpleChart() {
 const [symbol, setSymbol] = useState('AAPL');
 const [theme, setTheme] = useState('dark');
 const [chartReady, setChartReady] = useState(false);
 const containerRef = useRef(null);

 // Generate sample data for display
 const generateSampleData = () => {
 const data = [];
 let price = 150;
 const now = Date.now();
 
 for (let i = 30; i >= 0; i--) {
 const date = new Date(now - i * 24 * 60 * 60 * 1000);
 const change = (Math.random() - 0.5) * 10;
 price += change;
 
 data.push({
 date: date.toLocaleDateString(),
 price: price.toFixed(2),
 change: change.toFixed(2),
 volume: Math.floor(Math.random() * 1000000).toLocaleString()
 });
 }
 
 return data;
 };

 const sampleData = generateSampleData();

 // Simple chart using Canvas
 useEffect(() => {
 if (!containerRef.current) return;

 const canvas = document.createElement('canvas');
 canvas.width = 800;
 canvas.height = 400;
 canvas.style.width = '100%';
 canvas.style.height = '400px';
 canvas.style.backgroundColor = theme === 'dark' ? '#1a1a1a' : '#ffffff';
 
 const ctx = canvas.getContext('2d');
 
 // Clear previous content
 containerRef.current.innerHTML = '';
 containerRef.current.appendChild(canvas);

 // Draw simple price line
 const prices = sampleData.map(d => parseFloat(d.price));
 const minPrice = Math.min(...prices);
 const maxPrice = Math.max(...prices);
 const priceRange = maxPrice - minPrice;

 ctx.strokeStyle = theme === 'dark' ? '#00ff88' : '#0066cc';
 ctx.lineWidth = 2;
 ctx.beginPath();

 prices.forEach((price, index) => {
 const x = (index / (prices.length - 1)) * (canvas.width - 40) + 20;
 const y = canvas.height - 40 - ((price - minPrice) / priceRange) * (canvas.height - 80);
 
 if (index === 0) {
 ctx.moveTo(x, y);
 } else {
 ctx.lineTo(x, y);
 }
 });

 ctx.stroke();

 // Draw price labels
 ctx.fillStyle = theme === 'dark' ? '#e5e5e5' : '#333333';
 ctx.font = '12px Arial';
 ctx.fillText(`${minPrice.toFixed(2)}`, 5, canvas.height - 20);
 ctx.fillText(`${maxPrice.toFixed(2)}`, 5, 30);
 ctx.fillText(`${symbol}`, canvas.width - 60, 30);

 setChartReady(true);
 }, [theme, sampleData, symbol]);

 return (
 <div className="w-full h-full min-h-[600px] p-4 bg-neutral-900/40">
 {/* Toolbar */}
 <div className="mb-4 flex flex-wrap items-center gap-3">
 <div className="flex items-center gap-2">
 <span className="text-xl font-medium text-[rgb(252, 251, 255)]">Symbol:</span>
 <input
 className="px-3 py-2 rounded border border-neutral-600 bg-neutral-800 text-neutral-100"
 value={symbol}
 onChange={(e) => setSymbol(e.target.value.toUpperCase())}
 placeholder="Enter symbol"
 />
 </div>
 
 <button
 onClick={() => setTheme(t => t === 'dark' ? 'light' : 'dark')}
 className="px-4 py-2 rounded-lg border border-neutral-600 bg-neutral-800 hover:bg-neutral-700 text-neutral-100 transition-colors"
 >
 {theme === 'dark' ? ' Dark' : ' Light'}
 </button>
 
 <div className="text-lg text-gray-400">
 Professional chart ready for real data integration
 </div>
 </div>

 {/* Chart Area */}
 <div className="bg-neutral-800 rounded-lg border border-neutral-600 p-4">
 <div ref={containerRef} className="w-full h-[400px] rounded-lg overflow-hidden" />
 
 {chartReady && (
 <div className="mt-4 text-lg text-gray-400">
 Chart rendered successfully. Ready for TradingView Lightweight Charts integration.
 </div>
 )}
 </div>

 {/* Sample Data Table */}
 <div className="mt-6 bg-neutral-800 rounded-lg border border-neutral-600 p-4">
 <h3 className="text-3xl font-medium text-[rgb(252, 251, 255)] mb-3">Sample Data (Last 7 days)</h3>
 <div className="overflow-x-auto">
 <table className="w-full text-xl">
 <thead>
 <tr className="border-b border-neutral-600">
 <th className="text-left p-2 text-gray-300">Date</th>
 <th className="text-right p-2 text-gray-300">Price</th>
 <th className="text-right p-2 text-gray-300">Change</th>
 <th className="text-right p-2 text-gray-300">Volume</th>
 </tr>
 </thead>
 <tbody>
 {sampleData.slice(-7).map((row, index) => (
 <tr key={index} className="border-b border-neutral-700">
 <td className="p-2 text-gray-300">{row.date}</td>
 <td className="p-2 text-right text-[rgb(252, 251, 255)] font-mono">${row.price}</td>
 <td className={`p-2 text-right font-mono ${parseFloat(row.change) >= 0 ? 'text-green-400' : 'text-red-400'}`}>
 {parseFloat(row.change) >= 0 ? '+' : ''}{row.change}
 </td>
 <td className="p-2 text-right text-gray-300 font-mono">{row.volume}</td>
 </tr>
 ))}
 </tbody>
 </table>
 </div>
 </div>

 {/* Integration Guide */}
 <div className="mt-6 bg-blue-900/20 border border-blue-700 rounded-lg p-4">
 <h3 className="text-3xl font-medium text-blue-300 mb-2"> Chart Integration Guide</h3>
 <div className="space-y-2 text-xl text-blue-200">
 <p>• <strong>Current:</strong> Canvas-based simple price chart with sample data</p>
 <p>• <strong>Next:</strong> Replace with TradingView Lightweight Charts for professional features</p>
 <p>• <strong>Data Format:</strong> {`{ time: UNIX_timestamp, open, high, low, close, volume }`}</p>
 <p>• <strong>Features Ready:</strong> Theme toggle, symbol input, responsive design</p>
 </div>
 </div>
 </div>
 );
}