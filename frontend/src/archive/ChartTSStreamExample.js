import React, { useEffect, useRef, useState } from "react";
import { useTSStream } from "../lib/useTSStream";

// Import lightweight-charts dynamically to avoid SSR issues
let createChart;

const loadLightweightCharts = async () => {
 try {
 const module = await import('lightweight-charts');
 createChart = module.createChart;
 return true;
 } catch (error) {
 console.error('Failed to load lightweight-charts:', error);
 return false;
 }
};

export default function ChartTSStreamExample({ 
 symbol = "AAPL", 
 tf = "1", 
 barsBack = 1000 
}) {
 const { bars, status, isConnected, isLive } = useTSStream({ symbol, tf, barsBack });
 const chartRef = useRef(null);
 const seriesRef = useRef(null);
 const [chartReady, setChartReady] = useState(false);

 // Initialize chart
 useEffect(() => {
 if (!chartRef.current) return;

 const initChart = async () => {
 const success = await loadLightweightCharts();
 if (!success || !createChart) return;

 try {
 // Clear container
 chartRef.current.innerHTML = '';

 const chart = createChart(chartRef.current, { 
 autoSize: true,
 layout: {
 background: { color: '#1a1a1a' },
 textColor: '#e5e5e5',
 },
 grid: {
 vertLines: { color: '#2a2a2a' },
 horzLines: { color: '#2a2a2a' },
 },
 timeScale: {
 timeVisible: true,
 secondsVisible: false,
 }
 });

 const candleSeries = chart.addCandlestickSeries({
 upColor: '#16a34a',
 downColor: '#dc2626',
 borderDownColor: '#dc2626',
 borderUpColor: '#16a34a',
 wickDownColor: '#dc2626',
 wickUpColor: '#16a34a',
 });

 seriesRef.current = candleSeries;
 setChartReady(true);

 return () => {
 chart.remove();
 };
 } catch (error) {
 console.error('Chart init error:', error);
 }
 };

 initChart();
 }, []);

 // Update chart data when bars change
 useEffect(() => {
 if (!seriesRef.current || !bars.length || !chartReady) return;

 try {
 seriesRef.current.setData(bars);
 console.log(` Chart updated: ${bars.length} bars`);
 } catch (error) {
 console.error('Chart update error:', error);
 }
 }, [bars, chartReady]);

 const getStatusColor = () => {
 switch (status) {
 case "connected": return "text-blue-500";
 case "live": return "text-green-500";
 case "error": return "text-red-500";
 case "connecting": return "text-yellow-500";
 default: return "text-gray-500";
 }
 };

 const getStatusIcon = () => {
 switch (status) {
 case "connected": return "🔵";
 case "live": return "";
 case "error": return "";
 case "connecting": return "";
 default: return "⚪";
 }
 };

 return (
 <div className="p-4 space-y-3">
 {/* Status Bar */}
 <div className="flex items-center justify-between p-3 bg-gray-800 rounded-lg border border-gray-700">
 <div className="flex items-center gap-3">
 <h3 className="text-3xl font-medium text-[rgb(252, 251, 255)]">
 📡 TradeStation Live Chart
 </h3>
 <div className="text-xl text-gray-300">
 {symbol} • {tf} • {bars.length} bars
 </div>
 </div>
 
 <div className={`flex items-center gap-2 text-xl font-medium ${getStatusColor()}`}>
 <span>{getStatusIcon()}</span>
 <span className="capitalize">{status}</span>
 {isLive && <span className="text-lg text-green-400 ml-2">LIVE DATA</span>}
 </div>
 </div>

 {/* Chart Container */}
 <div className="bg-gray-800 rounded-lg border border-gray-700 p-4">
 <div ref={chartRef} className="h-[480px] w-full rounded-lg" />
 
 {!chartReady && (
 <div className="flex items-center justify-center h-[480px] text-gray-400">
 <div className="text-center">
 <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto mb-2"></div>
 <p>Loading chart...</p>
 </div>
 </div>
 )}
 </div>

 {/* Connection Info */}
 <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xl">
 <div className="bg-gray-800 p-3 rounded border border-gray-700">
 <div className="text-gray-400 mb-1">Connection Status</div>
 <div className={`font-medium ${getStatusColor()}`}>
 {status.toUpperCase()}
 </div>
 </div>
 
 <div className="bg-gray-800 p-3 rounded border border-gray-700">
 <div className="text-gray-400 mb-1">Data Points</div>
 <div className="font-medium text-[rgb(252, 251, 255)]">
 {bars.length.toLocaleString()} bars
 </div>
 </div>
 
 <div className="bg-gray-800 p-3 rounded border border-gray-700">
 <div className="text-gray-400 mb-1">Last Update</div>
 <div className="font-medium text-[rgb(252, 251, 255)]">
 {bars.length > 0 ? new Date(bars[bars.length - 1].time * 1000).toLocaleTimeString() : 'N/A'}
 </div>
 </div>
 </div>

 {/* Latest Bar Info */}
 {bars.length > 0 && (
 <div className="bg-gray-800 p-4 rounded border border-gray-700">
 <h4 className="text-[rgb(252, 251, 255)] font-medium mb-2">Latest Bar</h4>
 <div className="grid grid-cols-2 md:grid-cols-5 gap-4 text-xl">
 {(() => {
 const latest = bars[bars.length - 1];
 return (
 <>
 <div>
 <div className="text-gray-400">Open</div>
 <div className="text-[rgb(252, 251, 255)] font-mono">${latest.open.toFixed(2)}</div>
 </div>
 <div>
 <div className="text-gray-400">High</div>
 <div className="text-green-400 font-mono">${latest.high.toFixed(2)}</div>
 </div>
 <div>
 <div className="text-gray-400">Low</div>
 <div className="text-red-400 font-mono">${latest.low.toFixed(2)}</div>
 </div>
 <div>
 <div className="text-gray-400">Close</div>
 <div className="text-[rgb(252, 251, 255)] font-mono">${latest.close.toFixed(2)}</div>
 </div>
 <div>
 <div className="text-gray-400">Volume</div>
 <div className="text-blue-400 font-mono">{latest.volume.toLocaleString()}</div>
 </div>
 </>
 );
 })()}
 </div>
 </div>
 )}

 {/* Help Text */}
 <div className="text-lg text-gray-500 bg-gray-800 p-3 rounded border border-gray-700">
 <p>
 <strong>TradeStation Live Streaming:</strong> Real-time bar updates via Server-Sent Events. 
 Status: Connected → receiving historical data, Live → real-time updates active.
 </p>
 <p className="mt-1">
 <strong>Requirements:</strong> TradeStation API credentials cu MarketData + offline_access scopes în .env
 </p>
 </div>
 </div>
 );
}