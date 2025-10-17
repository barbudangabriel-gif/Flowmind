import React, { useState, useRef, useEffect, useCallback } from 'react';
import { useOHLCV, TF_OPTS } from '../hooks/useOHLCV';
import HeadlessChart from './HeadlessChart';

// LocalStorage persistence
const LS_DRAW_PREFIX = "flowmind_chart_drawings";
const LS_SETTINGS_PREFIX = "flowmind_chart_settings";

// Utility functions
const clamp = (value, min, max) => Math.min(Math.max(value, min), max);
const fmt = (n) => n.toFixed(2);

// Generate unique ID for drawings
const generateId = () => Date.now().toString(36) + Math.random().toString(36).substr(2);

// Snap functionality
const snapToPrice = (clickPrice, barData, snapEnabled = true) => {
 if (!snapEnabled || !barData) return clickPrice;
 
 const { open, high, low, close } = barData;
 const prices = [open, high, low, close];
 
 // Find closest price point
 let closest = clickPrice;
 let minDistance = Math.abs(clickPrice - close);
 
 prices.forEach(price => {
 const distance = Math.abs(clickPrice - price);
 if (distance < minDistance) {
 minDistance = distance;
 closest = price;
 }
 });
 
 // Snap if within 0.5% of any OHLC value
 return minDistance / clickPrice < 0.005 ? closest : clickPrice;
};

// Calculate technical indicators
const calculateSMA = (data, period) => {
 if (!data || data.length < period) return [];
 const sma = [];
 for (let i = period - 1; i < data.length; i++) {
 const sum = data.slice(i - period + 1, i + 1).reduce((s, d) => s + d.close, 0);
 sma.push({ time: data[i].time, value: sum / period });
 }
 return sma;
};

const calculateEMA = (data, period) => {
 if (!data || data.length < period) return [];
 const ema = [];
 const k = 2 / (period + 1);
 let emaValue = data.slice(0, period).reduce((s, d) => s + d.close, 0) / period;
 
 for (let i = period - 1; i < data.length; i++) {
 if (i === period - 1) {
 emaValue = data.slice(0, period).reduce((s, d) => s + d.close, 0) / period;
 } else {
 emaValue = data[i].close * k + emaValue * (1 - k);
 }
 ema.push({ time: data[i].time, value: emaValue });
 }
 return ema;
};

const calculateBollingerBands = (data, period, stdDev) => {
 if (!data || data.length < period) return { upper: [], middle: [], lower: [] };
 
 const bands = { upper: [], middle: [], lower: [] };
 
 for (let i = period - 1; i < data.length; i++) {
 const slice = data.slice(i - period + 1, i + 1);
 const mean = slice.reduce((s, d) => s + d.close, 0) / period;
 const variance = slice.reduce((s, d) => s + Math.pow(d.close - mean, 2), 0) / period;
 const std = Math.sqrt(variance);
 
 bands.middle.push({ time: data[i].time, value: mean });
 bands.upper.push({ time: data[i].time, value: mean + (std * stdDev) });
 bands.lower.push({ time: data[i].time, value: mean - (std * stdDev) });
 }
 
 return bands;
};

const calculateRSI = (data, period) => {
 if (!data || data.length < period + 1) return [];
 
 const rsi = [];
 const gains = [];
 const losses = [];
 
 for (let i = 1; i < data.length; i++) {
 const change = data[i].close - data[i - 1].close;
 gains.push(change > 0 ? change : 0);
 losses.push(change < 0 ? Math.abs(change) : 0);
 }
 
 for (let i = period - 1; i < gains.length; i++) {
 const avgGain = gains.slice(i - period + 1, i + 1).reduce((s, g) => s + g, 0) / period;
 const avgLoss = losses.slice(i - period + 1, i + 1).reduce((s, l) => s + l, 0) / period;
 
 if (avgLoss === 0) {
 rsi.push({ time: data[i + 1].time, value: 100 });
 } else {
 const rs = avgGain / avgLoss;
 const rsiValue = 100 - (100 / (1 + rs));
 rsi.push({ time: data[i + 1].time, value: rsiValue });
 }
 }
 
 return rsi;
};

export default function ChartProPlus({
 defaultSymbol = "NVDA",
 defaultTf = "D",
 limit = 500,
 fetcher = null,
 wsUrl = null
}) {
 const [symbol, setSymbol] = useState(defaultSymbol);
 const [tf, setTf] = useState(defaultTf);
 const [theme, setTheme] = useState("dark");
 const [tool, setTool] = useState(null);
 const [snapEnabled, setSnapEnabled] = useState(true);
 
 // Indicators show/hide with localStorage persistence
 const [show, setShow] = useState(() => {
 try {
 const saved = localStorage.getItem(`${LS_SETTINGS_PREFIX}:indicators`);
 return saved ? JSON.parse(saved) : { sma: true, ema: false, bb: false, rsi: false };
 } catch {
 return { sma: true, ema: false, bb: false, rsi: false };
 }
 });
 
 // Indicator parameters with localStorage persistence
 const [params, setParams] = useState(() => {
 try {
 const saved = localStorage.getItem(`${LS_SETTINGS_PREFIX}:params`);
 return saved ? JSON.parse(saved) : { sma: 20, ema: 14, bbPeriod: 20, bbStd: 2, rsi: 14 };
 } catch {
 return { sma: 20, ema: 14, bbPeriod: 20, bbStd: 2, rsi: 14 };
 }
 });

 // Chart references
 const chartRef = useRef(null);
 const series = useRef({});
 const drawings = useRef({ 
 priceLines: [], 
 trends: [],
 vlines: [],
 ranges: []
 });
 const trendTmp = useRef([]);
 const rangeTmp = useRef([]);
 
 // Drawings state for management
 const [items, setItems] = useState({
 hlines: [],
 vlines: [],
 trends: [],
 ranges: []
 });
 const [rangesInfo, setRangesInfo] = useState([]);

 // Use OHLCV hook
 const ohlcv = useOHLCV({
 symbol,
 timeframe: tf,
 limit,
 fetcher,
 wsUrl,
 polling: !wsUrl,
 pollInterval: 30000
 });

 // Save settings to localStorage
 useEffect(() => {
 localStorage.setItem(`${LS_SETTINGS_PREFIX}:indicators`, JSON.stringify(show));
 }, [show]);

 useEffect(() => {
 localStorage.setItem(`${LS_SETTINGS_PREFIX}:params`, JSON.stringify(params));
 }, [params]);

 // Load drawings from localStorage
 const loadDrawings = useCallback(() => {
 try {
 const key = `${LS_DRAW_PREFIX}:${symbol}:${tf}`;
 const saved = localStorage.getItem(key);
 if (saved) {
 const drawings = JSON.parse(saved);
 setItems(drawings);
 console.log('📥 Loaded drawings from localStorage:', drawings);
 return drawings;
 }
 } catch (error) {
 console.error('Error loading drawings:', error);
 }
 return { hlines: [], vlines: [], trends: [], ranges: [] };
 }, [symbol, tf]);

 // Save drawings to localStorage
 const saveDrawings = useCallback((drawingsToSave = items) => {
 try {
 const key = `${LS_DRAW_PREFIX}:${symbol}:${tf}`;
 localStorage.setItem(key, JSON.stringify(drawingsToSave));
 console.log('💾 Saved drawings to localStorage');
 } catch (error) {
 console.error('Error saving drawings:', error);
 }
 }, [symbol, tf, items]);

 // Manual save/load functions
 const manualSave = useCallback(() => {
 saveDrawings();
 alert('Drawings saved to localStorage!');
 }, [saveDrawings]);

 const manualLoad = useCallback(() => {
 const loaded = loadDrawings();
 // Re-apply drawings to chart
 if (series.current.candle && chartRef.current) {
 applyDrawingsToChart(loaded);
 }
 }, [loadDrawings]);

 // Export drawings as JSON
 const exportDrawings = useCallback(() => {
 const data = JSON.stringify(items, null, 2);
 const blob = new Blob([data], { type: 'application/json' });
 const url = URL.createObjectURL(blob);
 const a = document.createElement('a');
 a.href = url;
 a.download = `flowmind_chart_${symbol}_${tf}_${Date.now()}.json`;
 a.click();
 URL.revokeObjectURL(url);
 }, [items, symbol, tf]);

 // Import drawings from JSON
 const importDrawings = useCallback((event) => {
 const file = event.target.files[0];
 if (!file) return;

 const reader = new FileReader();
 reader.onload = (e) => {
 try {
 const imported = JSON.parse(e.target.result);
 setItems(imported);
 saveDrawings(imported);
 
 // Re-apply to chart
 if (series.current.candle && chartRef.current) {
 applyDrawingsToChart(imported);
 }
 
 alert('Drawings imported successfully!');
 } catch (error) {
 alert('Error importing drawings: ' + error.message);
 }
 };
 reader.readAsText(file);
 }, [saveDrawings]);

 // Apply drawings to chart
 const applyDrawingsToChart = useCallback((drawingsData) => {
 if (!series.current.candle || !chartRef.current) return;

 // Clear existing drawings
 drawings.current.priceLines.forEach(pl => {
 try { series.current.candle?.removePriceLine(pl); } catch(e) {}
 });
 drawings.current.priceLines = [];

 // Apply H-Lines
 drawingsData.hlines?.forEach(hline => {
 try {
 const priceLine = series.current.candle.createPriceLine({
 price: hline.price,
 color: hline.color || '#2196F3',
 lineWidth: 2,
 lineStyle: 0,
 axisLabelVisible: true,
 title: hline.label || `H-Line ${hline.price.toFixed(2)}`
 });
 drawings.current.priceLines.push(priceLine);
 } catch (error) {
 console.error('Error applying H-Line:', error);
 }
 });

 // Apply V-Lines
 drawingsData.vlines?.forEach(vline => {
 try {
 // V-Lines are implemented as price lines at specific times
 const priceLine = series.current.candle.createPriceLine({
 price: vline.price,
 color: vline.color || '#FF9800',
 lineWidth: 1,
 lineStyle: 1, // Dotted
 axisLabelVisible: false,
 title: vline.label || `V-Line ${new Date(vline.time * 1000).toLocaleDateString()}`
 });
 drawings.current.priceLines.push(priceLine);
 } catch (error) {
 console.error('Error applying V-Line:', error);
 }
 });

 // Apply Trendlines (simplified as price lines)
 drawingsData.trends?.forEach(trend => {
 try {
 const line1 = series.current.candle.createPriceLine({
 price: trend.aPrice,
 color: trend.color || '#FF6B6B',
 lineWidth: 2,
 lineStyle: 2, // Dashed
 axisLabelVisible: false,
 title: trend.label || `Trend ${trend.aPrice.toFixed(2)}-${trend.bPrice.toFixed(2)}`
 });
 const line2 = series.current.candle.createPriceLine({
 price: trend.bPrice,
 color: trend.color || '#FF6B6B',
 lineWidth: 2,
 lineStyle: 2,
 axisLabelVisible: false,
 title: ''
 });
 drawings.current.priceLines.push(line1, line2);
 } catch (error) {
 console.error('Error applying Trendline:', error);
 }
 });

 }, []);

 // Update item functions
 const updateHLine = useCallback((idx, updates) => {
 setItems(prev => {
 const newItems = { ...prev };
 newItems.hlines = [...newItems.hlines];
 newItems.hlines[idx] = { ...newItems.hlines[idx], ...updates };
 return newItems;
 });
 }, []);

 const updateVLine = useCallback((idx, updates) => {
 setItems(prev => {
 const newItems = { ...prev };
 newItems.vlines = [...newItems.vlines];
 newItems.vlines[idx] = { ...newItems.vlines[idx], ...updates };
 return newItems;
 });
 }, []);

 const updateTrend = useCallback((idx, updates) => {
 setItems(prev => {
 const newItems = { ...prev };
 newItems.trends = [...newItems.trends];
 newItems.trends[idx] = { ...newItems.trends[idx], ...updates };
 return newItems;
 });
 }, []);

 const updateRange = useCallback((idx, updates) => {
 setItems(prev => {
 const newItems = { ...prev };
 newItems.ranges = [...newItems.ranges];
 newItems.ranges[idx] = { ...newItems.ranges[idx], ...updates };
 return newItems;
 });
 }, []);

 // Chart ready callback
 const onReady = useCallback((api) => {
 console.log(' Chart Pro+++ ready, setting up series...');
 
 // Store chart reference
 chartRef.current = api.chart;
 
 // Add main candlestick series
 const candleSeries = api.addCandlestickSeries({
 title: symbol
 });
 series.current.candle = candleSeries;

 // Add volume series
 const volumeSeries = api.addHistogramSeries({
 color: '#26a69a',
 priceFormat: { type: 'volume' },
 priceScaleId: '',
 scaleMargins: { top: 0.7, bottom: 0 }
 });
 series.current.volume = volumeSeries;

 // Load and apply saved drawings
 const savedDrawings = loadDrawings();
 applyDrawingsToChart(savedDrawings);

 // Setup chart click handler for drawing tools
 if (api.chart) {
 api.chart.subscribeClick((param) => {
 if (!tool || !param.time) return;
 
 const priceData = param.seriesData?.get(candleSeries);
 if (!priceData) return;
 
 const clickPrice = snapToPrice(priceData.close, priceData, snapEnabled);
 
 if (tool === 'hline') {
 // Add horizontal line
 const newHLine = {
 id: generateId(),
 price: clickPrice,
 color: '#2196F3',
 label: `H-Line ${clickPrice.toFixed(2)}`,
 time: param.time
 };
 
 setItems(prev => ({
 ...prev,
 hlines: [...prev.hlines, newHLine]
 }));
 
 setTool(null);
 } 
 else if (tool === 'vline') {
 // Add vertical line
 const newVLine = {
 id: generateId(),
 time: param.time,
 price: clickPrice,
 color: '#FF9800',
 label: `V-Line ${new Date(param.time * 1000).toLocaleDateString()}`
 };
 
 setItems(prev => ({
 ...prev,
 vlines: [...prev.vlines, newVLine]
 }));
 
 setTool(null);
 }
 else if (tool === 'trend') {
 // Trendline logic (2 clicks)
 trendTmp.current.push({ time: param.time, price: clickPrice });
 
 if (trendTmp.current.length === 2) {
 const [p1, p2] = trendTmp.current;
 const newTrend = {
 id: generateId(),
 aTime: p1.time,
 aPrice: p1.price,
 bTime: p2.time,
 bPrice: p2.price,
 color: '#FF6B6B',
 label: `Trend ${p1.price.toFixed(2)}-${p2.price.toFixed(2)}`
 };
 
 setItems(prev => ({
 ...prev,
 trends: [...prev.trends, newTrend]
 }));
 
 trendTmp.current = [];
 setTool(null);
 }
 }
 else if (tool === 'range') {
 // Range selection (2 clicks)
 rangeTmp.current.push({ time: param.time, price: clickPrice });
 
 if (rangeTmp.current.length === 2) {
 const [p1, p2] = rangeTmp.current;
 const startTime = Math.min(p1.time, p2.time);
 const endTime = Math.max(p1.time, p2.time);
 
 // Calculate range statistics
 const rangeData = ohlcv.data.filter(d => d.time >= startTime && d.time <= endTime);
 if (rangeData.length > 0) {
 const startPrice = rangeData[0].close;
 const endPrice = rangeData[rangeData.length - 1].close;
 const high = Math.max(...rangeData.map(d => d.high));
 const low = Math.min(...rangeData.map(d => d.low));
 const pctChange = ((endPrice - startPrice) / startPrice) * 100;
 
 const rangeStats = {
 bars: rangeData.length,
 delt: endPrice - startPrice,
 pct: pctChange,
 hi: high,
 lo: low,
 a: startTime,
 b: endTime
 };
 
 setRangesInfo(prev => [...prev, rangeStats]);
 
 const newRange = {
 id: generateId(),
 aTime: startTime,
 bTime: endTime,
 aPrice: startPrice,
 bPrice: endPrice,
 color: '#9C27B0',
 label: `Range ${rangeStats.bars} bars (${rangeStats.pct.toFixed(2)}%)`
 };
 
 setItems(prev => ({
 ...prev,
 ranges: [...prev.ranges, newRange]
 }));
 }
 
 rangeTmp.current = [];
 setTool(null);
 }
 }
 });
 }

 }, [symbol, tool, snapEnabled, loadDrawings, applyDrawingsToChart, ohlcv.data]);

 // Clear all drawings
 const clearDrawings = useCallback((clearStorage = false) => {
 if (!series.current.candle) return;
 
 // Remove from chart
 drawings.current.priceLines.forEach(pl => { 
 try { 
 series.current.candle?.removePriceLine(pl); 
 } catch(e) {} 
 });
 drawings.current.priceLines = [];
 
 // Clear state
 setItems({ hlines: [], vlines: [], trends: [], ranges: [] });
 setRangesInfo([]);
 trendTmp.current = [];
 rangeTmp.current = [];
 setTool(null);
 
 // Clear from localStorage if requested
 if (clearStorage) {
 const key = `${LS_DRAW_PREFIX}:${symbol}:${tf}`;
 localStorage.removeItem(key);
 console.log('🗑️ Cleared drawings from localStorage');
 }
 }, [symbol, tf]);

 // Auto-save drawings when items change
 useEffect(() => {
 if (items.hlines.length > 0 || items.vlines.length > 0 || items.trends.length > 0 || items.ranges.length > 0) {
 saveDrawings();
 }
 }, [items, saveDrawings]);

 // Load drawings when symbol/timeframe changes
 useEffect(() => {
 loadDrawings();
 }, [symbol, tf, loadDrawings]);

 // Update indicators when data or settings change
 useEffect(() => {
 if (!ohlcv.data || ohlcv.data.length === 0 || !series.current.candle) return;

 try {
 // Update main candlestick data
 const candleData = ohlcv.data.map(({ time, open, high, low, close }) => ({
 time, open, high, low, close
 }));
 series.current.candle.setData(candleData);

 // Update volume data
 if (series.current.volume) {
 const volumeData = ohlcv.data.map(({ time, volume, open, close }) => ({
 time, 
 value: volume,
 color: close >= open ? "#16a34a55" : "#dc262655"
 }));
 series.current.volume.setData(volumeData);
 }

 // Update indicators (same logic as before)
 // SMA, EMA, BB, RSI - keeping existing implementation
 
 // SMA Indicator
 if (show.sma) {
 if (!series.current.sma) {
 series.current.sma = chartRef.current.addLineSeries({
 color: '#2196F3',
 lineWidth: 2,
 title: `SMA(${params.sma})`
 });
 }
 const smaData = calculateSMA(ohlcv.data, params.sma);
 series.current.sma.setData(smaData);
 series.current.sma.applyOptions({ visible: true });
 } else if (series.current.sma) {
 series.current.sma.applyOptions({ visible: false });
 }

 // EMA Indicator 
 if (show.ema) {
 if (!series.current.ema) {
 series.current.ema = chartRef.current.addLineSeries({
 color: '#FF9800',
 lineWidth: 2,
 title: `EMA(${params.ema})`
 });
 }
 const emaData = calculateEMA(ohlcv.data, params.ema);
 series.current.ema.setData(emaData);
 series.current.ema.applyOptions({ visible: true });
 } else if (series.current.ema) {
 series.current.ema.applyOptions({ visible: false });
 }

 // Bollinger Bands
 if (show.bb) {
 const bbData = calculateBollingerBands(ohlcv.data, params.bbPeriod, params.bbStd);
 
 if (!series.current.bbUpper) {
 series.current.bbUpper = chartRef.current.addLineSeries({
 color: '#9C27B0',
 lineWidth: 1,
 title: `BB Upper(${params.bbPeriod}, ${params.bbStd})`
 });
 series.current.bbMiddle = chartRef.current.addLineSeries({
 color: '#9C27B0',
 lineWidth: 1,
 lineStyle: 2,
 title: `BB Middle`
 });
 series.current.bbLower = chartRef.current.addLineSeries({
 color: '#9C27B0',
 lineWidth: 1,
 title: `BB Lower`
 });
 }

 series.current.bbUpper.setData(bbData.upper);
 series.current.bbMiddle.setData(bbData.middle);
 series.current.bbLower.setData(bbData.lower);
 
 series.current.bbUpper.applyOptions({ visible: true });
 series.current.bbMiddle.applyOptions({ visible: true });
 series.current.bbLower.applyOptions({ visible: true });
 } else {
 if (series.current.bbUpper) series.current.bbUpper.applyOptions({ visible: false });
 if (series.current.bbMiddle) series.current.bbMiddle.applyOptions({ visible: false });
 if (series.current.bbLower) series.current.bbLower.applyOptions({ visible: false });
 }

 // RSI Indicator
 if (show.rsi) {
 if (!series.current.rsi) {
 series.current.rsi = chartRef.current.addLineSeries({
 color: '#E91E63',
 lineWidth: 2,
 title: `RSI(${params.rsi})`,
 priceScaleId: 'rsi',
 scaleMargins: { top: 0.1, bottom: 0.1 }
 });
 }
 
 const rsiData = calculateRSI(ohlcv.data, params.rsi);
 series.current.rsi.setData(rsiData);
 series.current.rsi.applyOptions({ visible: true });
 } else if (series.current.rsi) {
 series.current.rsi.applyOptions({ visible: false });
 }

 // Fit content
 if (chartRef.current) {
 chartRef.current.timeScale().fitContent();
 }

 // Re-apply drawings after data update
 applyDrawingsToChart(items);

 } catch (error) {
 console.error('Error updating indicators:', error);
 }
 }, [ohlcv.data, show, params, items, applyDrawingsToChart]);

 return (
 <div className="p-4 space-y-3">
 {/* Toolbar top */}
 <div className="flex flex-wrap items-center gap-2">
 <input 
 className="px-2 py-1 rounded border border-neutral-300 dark:border-neutral-700 bg-white dark:bg-neutral-800"
 value={symbol} 
 onChange={(e) => setSymbol(e.target.value.toUpperCase())} 
 placeholder="Symbol"
 />
 
 {TF_OPTS.map(t => (
 <button 
 key={t.v} 
 onClick={() => setTf(t.v)}
 className={`px-2 py-1 rounded border ${
 tf === t.v 
 ? 'bg-neutral-200 dark:bg-neutral-700 border-neutral-400 dark:border-neutral-600' 
 : 'bg-transparent border-neutral-300 dark:border-neutral-700'
 } hover:bg-neutral-100 dark:hover:bg-neutral-700`}
 >
 {t.label}
 </button>
 ))}
 
 <button 
 onClick={() => setTheme(t => t === 'dark' ? 'light' : 'dark')}
 className="ml-2 px-3 py-1 rounded border border-neutral-300 dark:border-neutral-700 bg-white dark:bg-neutral-800"
 >
 {theme === 'dark' ? ' Dark' : ' Light'}
 </button>
 
 <button 
 onClick={ohlcv.refresh}
 disabled={ohlcv.loading}
 className="px-3 py-1 rounded border border-neutral-300 dark:border-neutral-700 bg-white dark:bg-neutral-800 disabled:opacity-50"
 >
 {ohlcv.loading ? '⏳' : '🔄'} Refresh
 </button>
 
 <label className="flex items-center gap-1 ml-3">
 <input 
 type="checkbox" 
 checked={snapEnabled} 
 onChange={(e) => setSnapEnabled(e.target.checked)}
 />
 Snap to OHLC
 </label>
 
 <div className="ml-auto text-lg opacity-70">
 {ohlcv.loading ? 'loading…' : ohlcv.error ? `err: ${ohlcv.error}` : ohlcv.lastUpdated ? `updated ${new Date(ohlcv.lastUpdated).toLocaleTimeString()}` : ''}
 </div>
 </div>

 {/* Indicators Panel */}
 <div className="flex flex-wrap items-center gap-2 text-xl bg-neutral-50 dark:bg-neutral-800 p-2 rounded border border-neutral-200 dark:border-neutral-700">
 <label className="flex items-center gap-1">
 <input type="checkbox" checked={show.sma} onChange={(e) => setShow(s => ({...s, sma: e.target.checked}))} />
 SMA
 </label>
 <input type="number" min={2} max={200} value={params.sma} onChange={(e) => setParams(p => ({...p, sma: clamp(+e.target.value, 2, 200)}))} className="w-16 px-2 py-1 rounded border border-neutral-300 dark:border-neutral-700 bg-white dark:bg-neutral-800" />
 
 <label className="flex items-center gap-1 ml-3">
 <input type="checkbox" checked={show.ema} onChange={(e) => setShow(s => ({...s, ema: e.target.checked}))} />
 EMA
 </label>
 <input type="number" min={2} max={200} value={params.ema} onChange={(e) => setParams(p => ({...p, ema: clamp(+e.target.value, 2, 200)}))} className="w-16 px-2 py-1 rounded border border-neutral-300 dark:border-neutral-700 bg-white dark:bg-neutral-800" />
 
 <label className="flex items-center gap-1 ml-3">
 <input type="checkbox" checked={show.bb} onChange={(e) => setShow(s => ({...s, bb: e.target.checked}))} />
 BB
 </label>
 <span className="text-lg">Period:</span>
 <input type="number" min={5} max={200} value={params.bbPeriod} onChange={(e) => setParams(p => ({...p, bbPeriod: clamp(+e.target.value, 5, 200)}))} className="w-16 px-2 py-1 rounded border border-neutral-300 dark:border-neutral-700 bg-white dark:bg-neutral-800" />
 <span className="text-lg">σ:</span>
 <input type="number" step={0.5} min={0.5} max={4} value={params.bbStd} onChange={(e) => setParams(p => ({...p, bbStd: clamp(+e.target.value, 0.5, 4)}))} className="w-16 px-2 py-1 rounded border border-neutral-300 dark:border-neutral-700 bg-white dark:bg-neutral-800" />
 
 <label className="flex items-center gap-1 ml-3">
 <input type="checkbox" checked={show.rsi} onChange={(e) => setShow(s => ({...s, rsi: e.target.checked}))} />
 RSI
 </label>
 <input type="number" min={2} max={100} value={params.rsi} onChange={(e) => setParams(p => ({...p, rsi: clamp(+e.target.value, 2, 100)}))} className="w-16 px-2 py-1 rounded border border-neutral-300 dark:border-neutral-700 bg-white dark:bg-neutral-800" />
 </div>

 {/* Drawing Tools Enhanced */}
 <div className="flex flex-wrap items-center gap-2 bg-neutral-50 dark:bg-neutral-800 p-2 rounded border border-neutral-200 dark:border-neutral-700">
 <button onClick={() => setTool('trend')} className={`px-3 py-1 rounded border ${tool === 'trend' ? 'bg-neutral-200 dark:bg-neutral-700' : ''} border-neutral-300 dark:border-neutral-700`}>
 Trendline
 </button>
 <button onClick={() => setTool('hline')} className={`px-3 py-1 rounded border ${tool === 'hline' ? 'bg-neutral-200 dark:bg-neutral-700' : ''} border-neutral-300 dark:border-neutral-700`}>
 ➖ H-Line
 </button>
 <button onClick={() => setTool('vline')} className={`px-3 py-1 rounded border ${tool === 'vline' ? 'bg-neutral-200 dark:bg-neutral-700' : ''} border-neutral-300 dark:border-neutral-700`}>
 | V-Line
 </button>
 <button onClick={() => setTool('range')} className={`px-3 py-1 rounded border ${tool === 'range' ? 'bg-neutral-200 dark:bg-neutral-700' : ''} border-neutral-300 dark:border-neutral-700`}>
 📏 Range
 </button>
 <button onClick={() => clearDrawings(true)} className="px-3 py-1 rounded border border-neutral-300 dark:border-neutral-700 bg-red-50 dark:bg-red-900/20 text-red-600">
 🗑️ Clear
 </button>
 
 <div className="ml-auto flex items-center gap-2 text-lg">
 <button onClick={manualSave} className="px-2 py-1 rounded border border-neutral-300 dark:border-neutral-700 bg-green-50 dark:bg-green-900/20 text-green-600">
 💾 Save
 </button>
 <button onClick={manualLoad} className="px-2 py-1 rounded border border-neutral-300 dark:border-neutral-700 bg-blue-50 dark:bg-blue-900/20 text-blue-600">
 📥 Load
 </button>
 <button onClick={exportDrawings} className="px-2 py-1 rounded border border-neutral-300 dark:border-neutral-700 bg-purple-50 dark:bg-purple-900/20 text-purple-600">
 Export
 </button>
 <label className="px-2 py-1 rounded border border-neutral-300 dark:border-neutral-700 bg-orange-50 dark:bg-orange-900/20 text-orange-600 cursor-pointer">
 📥 Import
 <input 
 type="file" 
 accept=".json" 
 onChange={importDrawings} 
 className="hidden" 
 />
 </label>
 </div>
 
 <span className="text-lg opacity-70 ml-2">
 Tip: Click pe chart după selectare tool. Trendline + Range: 2 clickuri.
 {tool && <span className="text-blue-600 ml-1">Mode: {tool}</span>}
 {tool === 'trend' && trendTmp.current.length === 1 && <span className="text-orange-600 ml-1">(Click pentru al 2-lea punct)</span>}
 {tool === 'range' && rangeTmp.current.length === 1 && <span className="text-orange-600 ml-1">(Click pentru sfârșit range)</span>}
 </span>
 </div>

 {/* Drawing Management Panel */}
 {(items.hlines.length > 0 || items.vlines.length > 0 || items.trends.length > 0 || items.ranges.length > 0) && (
 <div className="bg-neutral-50 dark:bg-neutral-800 p-3 rounded border border-neutral-200 dark:border-neutral-700">
 <h4 className="font-medium mb-2 text-xl">Drawing Management</h4>
 <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3 text-lg">
 {/* H-Lines */}
 <div className="p-2 rounded border border-neutral-300 dark:border-neutral-700">
 <div className="font-medium mb-1">H-Lines ({items.hlines.length})</div>
 {items.hlines.length === 0 && <div className="opacity-60">—</div>}
 {items.hlines.map((it, idx) => (
 <div key={idx} className="flex items-center gap-2 mb-1">
 <span className="w-16 font-mono">${it.price.toFixed(2)}</span>
 <input 
 className="px-1 py-0.5 rounded border border-neutral-300 dark:border-neutral-700 flex-1 text-lg" 
 placeholder="label" 
 value={it.label || ''} 
 onChange={e => updateHLine(idx, { label: e.target.value })} 
 />
 <input 
 type="color" 
 value={it.color} 
 onChange={e => updateHLine(idx, { color: e.target.value })} 
 className="w-6 h-6" 
 />
 </div>
 ))}
 </div>

 {/* V-Lines */}
 <div className="p-2 rounded border border-neutral-300 dark:border-neutral-700">
 <div className="font-medium mb-1">V-Lines ({items.vlines.length})</div>
 {items.vlines.length === 0 && <div className="opacity-60">—</div>}
 {items.vlines.map((it, idx) => (
 <div key={idx} className="flex items-center gap-2 mb-1">
 <span className="w-20 text-lg">{new Date(it.time * 1000).toLocaleDateString()}</span>
 <input 
 className="px-1 py-0.5 rounded border border-neutral-300 dark:border-neutral-700 flex-1 text-lg" 
 placeholder="label" 
 value={it.label || ''} 
 onChange={e => updateVLine(idx, { label: e.target.value })} 
 />
 <input 
 type="color" 
 value={it.color} 
 onChange={e => updateVLine(idx, { color: e.target.value })} 
 className="w-6 h-6" 
 />
 </div>
 ))}
 </div>

 {/* Trends */}
 <div className="p-2 rounded border border-neutral-300 dark:border-neutral-700">
 <div className="font-medium mb-1">Trends ({items.trends.length})</div>
 {items.trends.length === 0 && <div className="opacity-60">—</div>}
 {items.trends.map((it, idx) => (
 <div key={idx} className="flex items-center gap-2 mb-1">
 <span className="w-24 text-lg font-mono">${it.aPrice.toFixed(2)}-${it.bPrice.toFixed(2)}</span>
 <input 
 className="px-1 py-0.5 rounded border border-neutral-300 dark:border-neutral-700 flex-1 text-lg" 
 placeholder="label" 
 value={it.label || ''} 
 onChange={e => updateTrend(idx, { label: e.target.value })} 
 />
 <input 
 type="color" 
 value={it.color} 
 onChange={e => updateTrend(idx, { color: e.target.value })} 
 className="w-6 h-6" 
 />
 </div>
 ))}
 </div>

 {/* Ranges */}
 <div className="p-2 rounded border border-neutral-300 dark:border-neutral-700">
 <div className="font-medium mb-1">Ranges ({items.ranges.length})</div>
 {items.ranges.length === 0 && <div className="opacity-60">—</div>}
 {items.ranges.map((it, idx) => (
 <div key={idx} className="flex items-center gap-2 mb-1">
 <span className="w-20 text-lg">{new Date(it.aTime * 1000).toLocaleDateString()} → {new Date(it.bTime * 1000).toLocaleDateString()}</span>
 <input 
 className="px-1 py-0.5 rounded border border-neutral-300 dark:border-neutral-700 flex-1 text-lg" 
 placeholder="label" 
 value={it.label || ''} 
 onChange={e => updateRange(idx, { label: e.target.value })} 
 />
 <input 
 type="color" 
 value={it.color} 
 onChange={e => updateRange(idx, { color: e.target.value })} 
 className="w-6 h-6" 
 />
 </div>
 ))}
 </div>
 </div>
 </div>
 )}

 {/* Chart */}
 <div className="bg-white dark:bg-neutral-800 rounded-2xl shadow-lg border border-neutral-200 dark:border-neutral-700 overflow-hidden">
 <HeadlessChart 
 theme={theme} 
 onReady={onReady} 
 className="w-full h-[680px]" 
 />
 </div>

 {/* Range Stats */}
 {rangesInfo.length > 0 && (
 <div className="text-lg p-2 rounded border border-neutral-300 dark:border-neutral-700 bg-neutral-50 dark:bg-neutral-800">
 <div className="font-medium mb-1">Range Statistics</div>
 <div className="space-y-1">
 {rangesInfo.map((r, idx) => (
 <div key={idx} className="flex flex-wrap gap-x-4 gap-y-1">
 <span>#{idx + 1}</span>
 <span>bars: <b>{r.bars}</b></span>
 <span>Δ: <b>{fmt(r.delt)}</b></span>
 <span>%: <b>{fmt(r.pct)}</b></span>
 <span>Hi: <b>{fmt(r.hi)}</b></span>
 <span>Lo: <b>{fmt(r.lo)}</b></span>
 <span>from: <b>{new Date(r.a * 1000).toISOString().slice(0, 10)}</b></span>
 <span>to: <b>{new Date(r.b * 1000).toISOString().slice(0, 10)}</b></span>
 </div>
 ))}
 </div>
 </div>
 )}

 <div className="text-lg opacity-70">
 <p>
 Desenele se salvează automat per simbol+TF sub cheia: <code>{`${LS_DRAW_PREFIX}:${symbol}:${tf}`}</code>. 
 Export/Import transferă structuri JSON complete. Snap to OHLC magnetizează la valorile exacte.
 </p>
 </div>
 </div>
 );
}