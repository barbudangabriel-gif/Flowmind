import React, { useEffect, useRef, useState } from 'react';
import { createChart } from 'lightweight-charts';
import axios from 'axios';

// Get backend URL from environment
const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const SimpleTradingChart = ({ symbol, interval = '1D', height = 500 }) => {
 const chartContainerRef = useRef();
 const [loading, setLoading] = useState(true);
 const [error, setError] = useState(null);
 const [selectedInterval, setSelectedInterval] = useState(interval);
 const [selectedIndicators, setSelectedIndicators] = useState(['volume']);

 const intervals = [
 { label: '1D', value: '1D' },
 { label: '4H', value: '4H' }, 
 { label: '1H', value: '1H' },
 { label: '15m', value: '15m' },
 { label: '5m', value: '5m' }
 ];

 const availableIndicators = [
 { id: 'volume', label: 'Volume', color: '#26a69a' },
 { id: 'sma20', label: 'SMA 20', color: '#FF9500' },
 { id: 'sma50', label: 'SMA 50', color: '#9013FE' },
 { id: 'ema12', label: 'EMA 12', color: '#2196F3' }
 ];

 // Calculate Simple Moving Average
 const calculateSMA = (data, period) => {
 const smaData = [];
 for (let i = period - 1; i < data.length; i++) {
 const sum = data.slice(i - period + 1, i + 1).reduce((acc, item) => acc + item.close, 0);
 smaData.push({
 time: data[i].time,
 value: sum / period
 });
 }
 return smaData;
 };

 // Calculate EMA
 const calculateEMA = (data, period) => {
 const emaData = [];
 const multiplier = 2 / (period + 1);
 let emaValue = data[0].close;
 
 data.forEach((item, index) => {
 if (index === 0) {
 emaValue = item.close;
 } else {
 emaValue = (item.close * multiplier) + (emaValue * (1 - multiplier));
 }
 emaData.push({ time: item.time, value: emaValue });
 });
 
 return emaData;
 };

 // Main chart loading function
 useEffect(() => {
 if (!symbol || !chartContainerRef.current) return;

 const loadAndRenderChart = async () => {
 setLoading(true);
 setError(null);

 try {
 console.log(`Loading enhanced chart for ${symbol} (${selectedInterval})`);
 
 // Get chart data
 const response = await axios.get(
 `${API}/stocks/${symbol.toUpperCase()}/historical`,
 {
 params: { interval: selectedInterval, bars_back: 100 },
 timeout: 15000
 }
 );

 if (!response.data?.data || response.data.data.length === 0) {
 throw new Error('No chart data available');
 }

 const chartData = response.data.data;
 console.log(`Loaded ${chartData.length} data points for chart`);

 // Clear container
 chartContainerRef.current.innerHTML = '';

 // Create chart with black theme
 const chart = createChart(chartContainerRef.current, {
 width: chartContainerRef.current.clientWidth || 900,
 height: height,
 layout: {
 background: { color: '#000000' }, // Pure black background
 textColor: '#FFFFFF',
 },
 grid: {
 vertLines: { 
 color: 'transparent', // No vertical lines for cleaner look
 visible: false
 },
 horzLines: { 
 color: '#1a1a1a', // Very subtle horizontal lines
 style: 2, // Dotted style
 visible: true
 },
 },
 crosshair: {
 mode: 1,
 vertLine: {
 color: '#758694',
 width: 1,
 style: 3,
 labelBackgroundColor: '#1a1a1a',
 },
 horzLine: {
 color: '#758694',
 width: 1, 
 style: 3,
 labelBackgroundColor: '#1a1a1a',
 },
 },
 rightPriceScale: {
 borderColor: '#2B2B43',
 textColor: '#FFFFFF',
 entireTextOnly: true,
 },
 timeScale: {
 borderColor: '#2B2B43',
 textColor: '#FFFFFF',
 timeVisible: true,
 secondsVisible: false,
 },
 handleScroll: {
 mouseWheel: true,
 pressedMouseMove: true,
 },
 handleScale: {
 axisPressedMouseMove: true,
 mouseWheel: true,
 pinch: true,
 },
 });

 // Add main candlestick series
 const candlestickSeries = chart.addCandlestickSeries({
 upColor: '#00D4AA', // Bright green for bullish
 downColor: '#FF6B6B', // Bright red for bearish
 borderVisible: false,
 wickUpColor: '#00D4AA',
 wickDownColor: '#FF6B6B',
 priceFormat: {
 type: 'price',
 precision: 2,
 minMove: 0.01,
 },
 });

 candlestickSeries.setData(chartData);

 // Add selected indicators
 selectedIndicators.forEach(indicatorId => {
 try {
 switch (indicatorId) {
 case 'volume':
 const volumeData = chartData.map(item => ({
 time: item.time,
 value: item.volume,
 color: item.close >= item.open ? '#00D4AA40' : '#FF6B6B40'
 }));
 
 const volumeSeries = chart.addHistogramSeries({
 color: '#26a69a',
 priceFormat: { type: 'volume' },
 priceScaleId: '',
 scaleMargins: { top: 0.7, bottom: 0 },
 });
 volumeSeries.setData(volumeData);
 break;

 case 'sma20':
 const sma20Data = calculateSMA(chartData, 20);
 const sma20Series = chart.addLineSeries({
 color: '#FF9500',
 lineWidth: 2,
 priceLineVisible: false,
 crosshairMarkerVisible: true,
 });
 sma20Series.setData(sma20Data);
 break;

 case 'sma50':
 const sma50Data = calculateSMA(chartData, 50);
 const sma50Series = chart.addLineSeries({
 color: '#9013FE',
 lineWidth: 2,
 priceLineVisible: false,
 crosshairMarkerVisible: true,
 });
 sma50Series.setData(sma50Data);
 break;

 case 'ema12':
 const ema12Data = calculateEMA(chartData, 12);
 const ema12Series = chart.addLineSeries({
 color: '#2196F3',
 lineWidth: 1,
 priceLineVisible: false,
 crosshairMarkerVisible: true,
 });
 ema12Series.setData(ema12Data);
 break;

 default:
 break;
 }
 } catch (indicatorError) {
 console.warn(`Error adding indicator ${indicatorId}:`, indicatorError);
 }
 });

 // Fit content and finish
 chart.timeScale().fitContent();
 
 console.log('Enhanced chart rendered successfully!');
 setLoading(false);

 // Handle resize
 const handleResize = () => {
 if (chartContainerRef.current) {
 chart.applyOptions({
 width: chartContainerRef.current.clientWidth,
 });
 }
 };

 window.addEventListener('resize', handleResize);

 // Cleanup
 return () => {
 window.removeEventListener('resize', handleResize);
 chart.remove();
 };

 } catch (err) {
 console.error('Enhanced chart error:', err);
 setError(err.message);
 setLoading(false);
 }
 };

 loadAndRenderChart();
 }, [symbol, selectedInterval, selectedIndicators, height]);

 const handleIntervalChange = (newInterval) => {
 setSelectedInterval(newInterval);
 };

 const toggleIndicator = (indicatorId) => {
 setSelectedIndicators(prev => {
 if (prev.includes(indicatorId)) {
 return prev.filter(id => id !== indicatorId);
 } else {
 return [...prev, indicatorId];
 }
 });
 };

 if (error) {
 return (
 <div className="bg-gray-800 rounded-lg p-6 text-center">
 <div className="text-red-400 mb-2">Chart Error</div>
 <div className="text-gray-400 text-xl">{error}</div>
 <button 
 onClick={() => setSelectedInterval(selectedInterval)}
 className="mt-4 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-[rgb(252, 251, 255)] rounded-lg text-xl"
 >
 Retry
 </button>
 </div>
 );
 }

 return (
 <div className="bg-gray-900 rounded-lg p-4">
 {/* Enhanced Header */}
 <div className="flex flex-col space-y-4 mb-4">
 {/* Title and Intervals */}
 <div className="flex justify-between items-center">
 <div className="flex items-center space-x-3">
 <h3 className="text-xl font-medium text-[rgb(252, 251, 255)]">{symbol} Professional Chart</h3>
 {loading && (
 <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-green-500"></div>
 )}
 </div>
 
 {/* Interval Buttons */}
 <div className="flex space-x-1">
 {intervals.map((int) => (
 <button
 key={int.value}
 onClick={() => handleIntervalChange(int.value)}
 className={`px-4 py-2 text-xl font-medium rounded transition-colors ${
 selectedInterval === int.value
 ? 'bg-green-600 text-[rgb(252, 251, 255)] shadow-lg'
 : 'bg-gray-700 text-gray-300 hover:bg-gray-600 hover:text-[rgb(252, 251, 255)]'
 }`}
 >
 {int.label}
 </button>
 ))}
 </div>
 </div>

 {/* Technical Indicators */}
 <div className="flex flex-wrap items-center gap-2">
 <span className="text-xl font-medium text-gray-300 mr-3">Technical Indicators:</span>
 {availableIndicators.map((indicator) => (
 <button
 key={indicator.id}
 onClick={() => toggleIndicator(indicator.id)}
 className={`px-3 py-1 text-xl rounded-full transition-all duration-200 ${
 selectedIndicators.includes(indicator.id)
 ? 'text-[rgb(252, 251, 255)] shadow-lg'
 : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
 }`}
 style={selectedIndicators.includes(indicator.id) ? {
 backgroundColor: indicator.color,
 } : {}}
 >
 {indicator.label}
 </button>
 ))}
 </div>
 </div>

 {/* Chart Container */}
 <div 
 ref={chartContainerRef}
 className="w-full bg-black rounded-lg border border-gray-800"
 style={{ height: `${height}px` }}
 />
 
 {/* Enhanced Footer */}
 <div className="mt-3 flex justify-between items-center text-lg text-gray-400">
 <div>
 {loading ? (
 'Loading professional chart data...'
 ) : (
 `${symbol?.toUpperCase()} • ${selectedInterval} • ${selectedIndicators.length} indicator${selectedIndicators.length !== 1 ? 's' : ''} active`
 )}
 </div>
 <div className="text-green-400">
 ● Live Data • Enhanced by TradeStation
 </div>
 </div>
 </div>
 );
};

export default SimpleTradingChart;