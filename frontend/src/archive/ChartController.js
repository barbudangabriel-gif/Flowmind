import React, { useState, useRef, useEffect } from 'react';
import { useOHLCV, TF_OPTS } from '../hooks/useOHLCV';
import HeadlessChart from './HeadlessChart';

export default function ChartController({
 defaultSymbol = "AAPL",
 defaultTf = "D",
 limit = 300,
 fetcher = null,
 wsUrl = null
}) {
 const [symbol, setSymbol] = useState(defaultSymbol);
 const [tf, setTf] = useState(defaultTf);
 const [theme, setTheme] = useState("dark");
 const [showSMA, setShowSMA] = useState(true);
 
 const chartRef = useRef(null);
 const candlestickSeriesRef = useRef(null);
 const volumeSeriesRef = useRef(null);
 const smaSeriesRef = useRef(null);

 // Use OHLCV hook
 const ohlcv = useOHLCV({
 symbol,
 timeframe: tf,
 limit,
 fetcher,
 wsUrl,
 polling: !wsUrl, // Use polling if no WebSocket
 pollInterval: 30000
 });

 // Calculate SMA20
 const calculateSMA = (data, period = 20) => {
 if (!data || data.length < period) return [];
 
 const sma = [];
 for (let i = period - 1; i < data.length; i++) {
 const sum = data.slice(i - period + 1, i + 1).reduce((s, d) => s + d.close, 0);
 sma.push({
 time: data[i].time,
 value: sum / period
 });
 }
 return sma;
 };

 // Chart ready callback
 const onReady = (api) => {
 console.log(' Chart ready, adding series...');
 
 // Add candlestick series
 const candlestickSeries = api.addCandlestickSeries();
 candlestickSeriesRef.current = candlestickSeries;

 // Add volume series
 const volumeSeries = api.addHistogramSeries();
 volumeSeriesRef.current = volumeSeries;

 // Add SMA series
 const smaSeries = api.addLineSeries({
 color: '#2196F3',
 lineWidth: 2,
 title: 'SMA(20)',
 visible: showSMA
 });
 smaSeriesRef.current = smaSeries;
 };

 // Apply data to chart
 const onDataApplied = (api) => {
 if (ohlcv.data && ohlcv.data.length > 0) {
 // Apply candlestick data
 if (candlestickSeriesRef.current) {
 const candleData = ohlcv.data.map(({ time, open, high, low, close }) => ({
 time, open, high, low, close
 }));
 candlestickSeriesRef.current.setData(candleData);
 }

 // Apply volume data
 if (volumeSeriesRef.current) {
 const volumeData = ohlcv.data.map(({ time, volume, open, close }) => ({
 time, 
 value: volume,
 color: close >= open ? "#16a34a55" : "#dc262655"
 }));
 volumeSeriesRef.current.setData(volumeData);
 }

 // Apply SMA data
 if (smaSeriesRef.current && showSMA) {
 const smaData = calculateSMA(ohlcv.data);
 smaSeriesRef.current.setData(smaData);
 }

 // Fit content
 if (api.chart) {
 api.chart.timeScale().fitContent();
 }
 }
 };

 // Update data when OHLCV changes
 useEffect(() => {
 if (chartRef.current && ohlcv.data && ohlcv.data.length > 0) {
 onDataApplied({ chart: chartRef.current });
 }
 }, [ohlcv.data, showSMA]);

 // Update SMA visibility
 useEffect(() => {
 if (smaSeriesRef.current) {
 smaSeriesRef.current.applyOptions({ visible: showSMA });
 }
 }, [showSMA]);

 return (
 <div className="w-full space-y-4">
 {/* Toolbar */}
 <div className="flex flex-wrap items-center gap-3 p-3 bg-white dark:bg-neutral-800 rounded-lg border border-neutral-200 dark:border-neutral-700">
 <div className="flex items-center gap-2">
 <span className="text-xl font-medium">Symbol:</span>
 <input
 className="px-2 py-1 rounded border border-neutral-300 dark:border-neutral-700 bg-white dark:bg-neutral-800"
 value={symbol}
 onChange={(e) => setSymbol(e.target.value.toUpperCase())}
 placeholder="AAPL"
 />
 </div>

 <div className="flex items-center gap-2">
 <span className="text-xl font-medium">Timeframe:</span>
 <select
 className="px-2 py-1 rounded border border-neutral-300 dark:border-neutral-700 bg-white dark:bg-neutral-800"
 value={tf}
 onChange={(e) => setTf(e.target.value)}
 >
 {TF_OPTS.map((t) => (
 <option key={t.v} value={t.v}>{t.label}</option>
 ))}
 </select>
 </div>

 <button
 onClick={() => setTheme((t) => (t === "dark" ? "light" : "dark"))}
 className="px-3 py-1 rounded border border-neutral-300 dark:border-neutral-700 bg-white dark:bg-neutral-800 hover:bg-neutral-100 dark:hover:bg-neutral-700"
 >
 {theme === "dark" ? " Dark" : " Light"}
 </button>

 <button
 onClick={ohlcv.refresh}
 disabled={ohlcv.loading}
 className="px-3 py-1 rounded border border-neutral-300 dark:border-neutral-700 bg-white dark:bg-neutral-800 hover:bg-neutral-100 dark:hover:bg-neutral-700 disabled:opacity-50"
 title="Force refresh"
 >
 {ohlcv.loading ? "⏳" : "🔄"} Refresh
 </button>

 <label className="flex items-center gap-1 text-xl">
 <input 
 type="checkbox" 
 checked={showSMA} 
 onChange={(e) => setShowSMA(e.target.checked)} 
 /> 
 SMA20
 </label>

 {/* Status */}
 <div className="ml-auto text-lg opacity-70">
 {ohlcv.loading ? (
 <span className="text-blue-600">Loading...</span>
 ) : ohlcv.error ? (
 <span className="text-red-600">Error: {ohlcv.error}</span>
 ) : ohlcv.lastUpdated ? (
 <span className="text-green-600">
 Updated: {new Date(ohlcv.lastUpdated).toLocaleTimeString()}
 </span>
 ) : (
 <span className="text-gray-500">No data</span>
 )}
 
 {ohlcv.wsConnected && (
 <span className="ml-2 text-green-600"> Live</span>
 )}
 </div>
 </div>

 {/* Chart */}
 <div className="bg-white dark:bg-neutral-800 rounded-lg border border-neutral-200 dark:border-neutral-700 p-4">
 <HeadlessChart
 ref={chartRef}
 theme={theme}
 className="w-full h-[640px]"
 onReady={(api) => {
 onReady(api);
 // Apply initial data if available
 if (ohlcv.data && ohlcv.data.length > 0) {
 setTimeout(() => onDataApplied(api), 100);
 }
 }}
 />
 
 {/* Chart Status */}
 <div className="mt-2 flex justify-between items-center text-lg text-gray-500">
 <span>
 {ohlcv.isEmpty ? 'No data available' : `${ohlcv.dataLength} bars loaded`}
 </span>
 <span>
 {symbol} • {TF_OPTS.find(t => t.v === tf)?.label || tf}
 </span>
 </div>
 </div>

 {/* Data Summary */}
 {ohlcv.data && ohlcv.data.length > 0 && (
 <div className="bg-white dark:bg-neutral-800 rounded-lg border border-neutral-200 dark:border-neutral-700 p-4">
 <h4 className="text-xl font-medium mb-2">Market Summary</h4>
 <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-xl">
 {(() => {
 const latest = ohlcv.data[ohlcv.data.length - 1];
 const previous = ohlcv.data[ohlcv.data.length - 2];
 const change = previous ? latest.close - previous.close : 0;
 const changePercent = previous ? (change / previous.close) * 100 : 0;
 
 return (
 <>
 <div>
 <span className="text-gray-500">Last Price:</span>
 <div className="font-mono font-medium">${latest.close.toFixed(2)}</div>
 </div>
 <div>
 <span className="text-gray-500">Change:</span>
 <div className={`font-mono font-medium ${change >= 0 ? 'text-green-600' : 'text-red-600'}`}>
 {change >= 0 ? '+' : ''}{change.toFixed(2)} ({changePercent.toFixed(2)}%)
 </div>
 </div>
 <div>
 <span className="text-gray-500">High:</span>
 <div className="font-mono font-medium">${latest.high.toFixed(2)}</div>
 </div>
 <div>
 <span className="text-gray-500">Low:</span>
 <div className="font-mono font-medium">${latest.low.toFixed(2)}</div>
 </div>
 </>
 );
 })()}
 </div>
 </div>
 )}

 {/* Apply show/hide SMA visually */}
 <style>{`.lw-sma-hidden { opacity: 0; }`}</style>
 </div>
 );
}