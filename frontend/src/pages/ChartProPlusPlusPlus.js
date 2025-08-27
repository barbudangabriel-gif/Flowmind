import React, { useState, useRef, useEffect, useCallback } from 'react';
import { useOHLCV, TF_OPTS } from '../hooks/useOHLCV';
import HeadlessChart from '../components/HeadlessChart';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Tabs, TabsList, TabsTrigger } from '../components/ui/tabs';
import { Separator } from '../components/ui/separator';
import { Switch } from '../components/ui/switch';
import { Label } from '../components/ui/label';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '../components/ui/dialog';
import { Textarea } from '../components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { cn } from '../lib/utils';
import { toast } from 'sonner';

// LocalStorage persistence
const LS_DRAW_PREFIX = "flowmind_chart_drawings";
const LS_SETTINGS_PREFIX = "flowmind_chart_settings";

// Utility functions
const clamp = (value, min, max) => Math.min(Math.max(value, min), max);
const fmt = (n, decimals = 2) => n.toFixed(decimals);

// Generate unique ID for drawings
const generateId = () => Date.now().toString(36) + Math.random().toString(36).substr(2);

// Snap options
const SNAP_OPTIONS = [
  { value: 'none', label: 'None' },
  { value: 'close', label: 'Close' },
  { value: 'hl', label: 'High-Low' },
  { value: 'ohlc', label: 'OHLC' }
];

// Snap functionality
const snapToPrice = (clickPrice, barData, snapMode = 'none') => {
  if (snapMode === 'none' || !barData) return clickPrice;
  
  const { open, high, low, close } = barData;
  let prices = [];
  
  switch (snapMode) {
    case 'close':
      prices = [close];
      break;
    case 'hl':
      prices = [high, low];
      break;
    case 'ohlc':
      prices = [open, high, low, close];
      break;
    default:
      return clickPrice;
  }
  
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
  
  // Snap if within 0.5% of any selected price
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

export default function ChartProPlusPlusPlus() {
  const [symbol, setSymbol] = useState("NVDA");
  const [tf, setTf] = useState("D");
  const [theme, setTheme] = useState("dark");
  const [tool, setTool] = useState(null);
  const [snapMode, setSnapMode] = useState('ohlc');
  
  // Dialog state
  const [openIO, setOpenIO] = useState(false);
  const [jsonText, setJsonText] = useState('');
  
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
  const drawings = useRef({ priceLines: [] });
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

  // Custom fetcher for FlowMind backend
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

  // Use OHLCV hook
  const ohlcv = useOHLCV({
    symbol,
    timeframe: tf,
    limit: 500,
    fetcher,
    wsUrl: null,
    polling: true,
    pollInterval: 30000
  });

  // BRIDGE: sync cu <html class="dark"> + persist în localStorage
  useEffect(() => {
    try {
      document.documentElement.classList.toggle('dark', theme === 'dark');
      localStorage.setItem('flowmind.theme', theme);
    } catch {}
  }, [theme]);

  // Load saved theme on mount
  useEffect(() => {
    try {
      const saved = localStorage.getItem('flowmind.theme');
      if (saved === 'dark' || saved === 'light') {
        setTheme(saved);
      }
    } catch {}
  }, []);

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
      toast.success('Drawings saved successfully!');
    } catch (error) {
      toast.error('Error saving drawings: ' + error.message);
    }
  }, [symbol, tf, items]);

  // Export functions
  const exportPNG = useCallback(() => {
    toast.info('PNG export feature coming soon!');
  }, []);

  const resetLayout = useCallback(() => {
    clearDrawings(true);
    toast.info('Layout reset complete!');
  }, [clearDrawings]);

  const openExport = useCallback(() => {
    const data = JSON.stringify(items, null, 2);
    setJsonText(data);
    toast.success('Current drawings exported to dialog');
  }, [items]);

  const doCopy = useCallback(() => {
    navigator.clipboard.writeText(jsonText);
    toast.success('JSON copied to clipboard!');
  }, [jsonText]);

  const doDownload = useCallback(() => {
    const blob = new Blob([jsonText], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `flowmind_chart_${symbol}_${tf}_${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
    toast.success('JSON file downloaded!');
  }, [jsonText, symbol, tf]);

  const doImport = useCallback(() => {
    try {
      const imported = JSON.parse(jsonText);
      setItems(imported);
      saveDrawings(imported);
      setOpenIO(false);
      toast.success('Drawings imported successfully!');
    } catch (error) {
      toast.error('Error importing JSON: ' + error.message);
    }
  }, [jsonText, saveDrawings]);

  // Chart ready callback
  const onReady = useCallback((api) => {
    console.log('📈 Chart Pro+++ Ultimate ready!');
    
    chartRef.current = api.chart;
    
    // Add main series
    const candleSeries = api.addCandlestickSeries({ title: symbol });
    series.current.candle = candleSeries;

    const volumeSeries = api.addHistogramSeries({
      color: '#26a69a',
      priceFormat: { type: 'volume' },
      priceScaleId: '',
      scaleMargins: { top: 0.7, bottom: 0 }
    });
    series.current.volume = volumeSeries;

    // Enhanced click handler
    if (api.chart) {
      api.chart.subscribeClick((param) => {
        if (!tool || !param.time) return;
        
        const priceData = param.seriesData?.get(candleSeries);
        if (!priceData) return;
        
        const clickPrice = snapToPrice(priceData.close, priceData, snapMode);
        
        if (tool === 'hline') {
          const newHLine = {
            id: generateId(),
            price: clickPrice,
            color: '#2196F3',
            label: `H-Line ${clickPrice.toFixed(2)}`
          };
          setItems(prev => ({ ...prev, hlines: [...prev.hlines, newHLine] }));
          setTool(null);
          toast.success('H-Line added');
        } 
        else if (tool === 'vline') {
          const newVLine = {
            id: generateId(),
            time: param.time,
            price: clickPrice,
            color: '#FF9800',
            label: `V-Line ${new Date(param.time * 1000).toLocaleDateString()}`
          };
          setItems(prev => ({ ...prev, vlines: [...prev.vlines, newVLine] }));
          setTool(null);
          toast.success('V-Line added');
        }
        else if (tool === 'trend') {
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
            setItems(prev => ({ ...prev, trends: [...prev.trends, newTrend] }));
            trendTmp.current = [];
            setTool(null);
            toast.success('Trendline added');
          } else {
            toast.info('Click for second point');
          }
        }
        else if (tool === 'range') {
          rangeTmp.current.push({ time: param.time, price: clickPrice });
          
          if (rangeTmp.current.length === 2) {
            const [p1, p2] = rangeTmp.current;
            const startTime = Math.min(p1.time, p2.time);
            const endTime = Math.max(p1.time, p2.time);
            
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
                color: '#9C27B0',
                label: `Range ${rangeStats.bars} bars (${rangeStats.pct.toFixed(2)}%)`
              };
              
              setItems(prev => ({ ...prev, ranges: [...prev.ranges, newRange] }));
            }
            
            rangeTmp.current = [];
            setTool(null);
            toast.success('Range added with statistics');
          } else {
            toast.info('Click for end point');
          }
        }
      });
    }

  }, [symbol, tool, snapMode, ohlcv.data]);

  // Clear all drawings
  const clearDrawings = useCallback((clearStorage = false) => {
    setItems({ hlines: [], vlines: [], trends: [], ranges: [] });
    setRangesInfo([]);
    trendTmp.current = [];
    rangeTmp.current = [];
    setTool(null);
    
    if (clearStorage) {
      const key = `${LS_DRAW_PREFIX}:${symbol}:${tf}`;
      localStorage.removeItem(key);
      toast.success('All drawings cleared!');
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

  const drawKey = `${LS_DRAW_PREFIX}:${symbol}:${tf}`;

  // Update functions for drawings
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

  return (
    <div className="min-h-screen bg-background text-foreground">
      {/* Header */}
      <div className="bg-card border-b border-border shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <div className="text-center">
            <h1 className="text-3xl font-bold flex items-center justify-center gap-3">
              <div className="w-12 h-12 bg-gradient-to-r from-brand-500 to-brand-600 rounded-xl flex items-center justify-center text-white">
                📊
              </div>
              FlowMind Analytics - Chart Pro+++
            </h1>
            <p className="text-muted-foreground mt-2 text-lg">
              Ultimate Professional Trading Charts cu Persistent Drawings, Technical Indicators și Advanced Analysis Tools
            </p>
            <div className="flex items-center justify-center gap-2 mt-3 text-sm text-brand-600">
              <span className="w-2 h-2 bg-brand-500 rounded-full"></span>
              Default Dashboard - Professional Trading Platform
            </div>
          </div>
        </div>
      </div>

      {/* Main Chart Interface */}
      <div className="max-w-7xl mx-auto px-4 py-6 space-y-4" id="chart-root">
          {/* Enhanced Toolbar cu shadcn/ui */}
          <div className="flex flex-wrap items-center gap-3 bg-card p-4 rounded-lg shadow border border-border">
            <Input 
              className="w-[180px] font-semibold"
              value={symbol} 
              onChange={(e) => setSymbol(e.target.value.toUpperCase())} 
              placeholder="Symbol"
            />
            
            <Tabs value={tf} onValueChange={setTf}>
              <TabsList className="grid w-auto grid-cols-7">
                {TF_OPTS.map(t => (
                  <TabsTrigger key={t.v} value={t.v} className="text-xs">
                    {t.label}
                  </TabsTrigger>
                ))}
              </TabsList>
            </Tabs>
            
            <Separator orientation="vertical" className="h-8" />
            
            <Button 
              variant="outline" 
              onClick={() => setTheme(t => t === 'dark' ? 'light' : 'dark')}
            >
              {theme === 'dark' ? '🌙 Dark' : '☀️ Light'}
            </Button>
            
            <Button 
              variant="outline"
              onClick={ohlcv.refresh}
              disabled={ohlcv.loading}
            >
              {ohlcv.loading ? '⏳' : '🔄'} Refresh
            </Button>
            
            <Select value={snapMode} onValueChange={setSnapMode}>
              <SelectTrigger className="w-[120px]">
                <SelectValue placeholder="Snap mode" />
              </SelectTrigger>
              <SelectContent>
                {SNAP_OPTIONS.map(opt => (
                  <SelectItem key={opt.value} value={opt.value}>
                    {opt.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            
            <div className="ml-auto text-sm font-medium">
              {ohlcv.loading ? (
                <span className="text-brand-600">🔄 Loading...</span>
              ) : ohlcv.error ? (
                <span className="text-destructive">❌ Error: {ohlcv.error}</span>
              ) : ohlcv.lastUpdated ? (
                <span className="text-brand-600">
                  ✅ Updated: {new Date(ohlcv.lastUpdated).toLocaleTimeString()}
                </span>
              ) : ''}
            </div>
          </div>

        {/* Enhanced Indicators Panel cu shadcn/ui */}
        <div className="flex flex-wrap items-center gap-4 text-sm bg-card p-4 rounded-lg border border-border">
          <Label className="font-semibold">Technical Indicators:</Label>
          
          <div className="flex items-center gap-2">
            <Switch checked={show.sma} onCheckedChange={(v) => setShow(s => ({...s, sma: !!v}))} />
            <Label>SMA</Label>
            <Input 
              type="number" 
              className="w-16" 
              value={params.sma} 
              onChange={e => setParams(s => ({...s, sma: Math.max(1, Number(e.target.value) || 1)}))} 
            />
          </div>
          
          <div className="flex items-center gap-2">
            <Switch checked={show.ema} onCheckedChange={(v) => setShow(s => ({...s, ema: !!v}))} />
            <Label>EMA</Label>
            <Input 
              type="number" 
              className="w-16" 
              value={params.ema} 
              onChange={e => setParams(s => ({...s, ema: Math.max(1, Number(e.target.value) || 1)}))} 
            />
          </div>
          
          <div className="flex items-center gap-2">
            <Switch checked={show.bb} onCheckedChange={(v) => setShow(s => ({...s, bb: !!v}))} />
            <Label>BB</Label>
            <Input 
              type="number" 
              className="w-16" 
              value={params.bbPeriod} 
              onChange={e => setParams(s => ({...s, bbPeriod: Math.max(2, Number(e.target.value) || 20)}))} 
            />
            <Label>σ</Label>
            <Input 
              type="number" 
              className="w-16" 
              value={params.bbStd} 
              onChange={e => setParams(s => ({...s, bbStd: Math.max(1, Number(e.target.value) || 2)}))} 
            />
          </div>
          
          <div className="flex items-center gap-2">
            <Switch checked={show.rsi} onCheckedChange={(v) => setShow(s => ({...s, rsi: !!v}))} />
            <Label>RSI</Label>
            <Input 
              type="number" 
              className="w-16" 
              value={params.rsi} 
              onChange={e => setParams(s => ({...s, rsi: Math.max(2, Number(e.target.value) || 14)}))} 
            />
          </div>
        </div>

        {/* Enhanced Drawing Tools cu shadcn/ui */}
        <div className="flex flex-wrap items-center gap-2 bg-card p-4 rounded-lg border border-border">
          <Label className="font-semibold">Drawing Tools:</Label>
          
          <Button 
            variant={tool === 'trend' ? 'default' : 'outline'} 
            size="sm"
            onClick={() => setTool('trend')}
          >
            📈 Trend
          </Button>
          
          <Button 
            variant={tool === 'hline' ? 'default' : 'outline'} 
            size="sm"
            onClick={() => setTool('hline')}
          >
            ➖ H‑Line
          </Button>
          
          <Button 
            variant={tool === 'vline' ? 'default' : 'outline'} 
            size="sm"
            onClick={() => setTool('vline')}
          >
            | V‑Line
          </Button>
          
          <Button 
            variant={tool === 'range' ? 'default' : 'outline'} 
            size="sm"
            onClick={() => setTool('range')}
          >
            📏 Range
          </Button>
          
          <Button 
            variant="destructive" 
            size="sm"
            onClick={() => clearDrawings(true)}
          >
            🗑️ Clear
          </Button>
          
          <Separator orientation="vertical" className="h-6" />
            
            <Button variant="outline" onClick={exportPNG}>
              📤 Export PNG
            </Button>
            
            <Button variant="outline" onClick={() => saveDrawings()}>
              💾 Save
            </Button>
            
            <Button variant="outline" onClick={() => { setJsonText(''); setOpenIO(true); }}>
              📥📤 Import / Export JSON
            </Button>
            
            <Button variant="outline" onClick={resetLayout}>
              🔄 Reset
            </Button>
            
            <div className="ml-auto text-xs text-muted-foreground">
              💡 Click pe chart după selectare tool. Trendline + Range: 2 clickuri.
              {tool && <span className="text-brand-600 ml-2 font-medium">🎯 Mode: {tool}</span>}
            </div>
          </div>

        {/* Chart */}
        <div className="chart-container">
          <HeadlessChart 
            theme={theme} 
            onReady={onReady} 
            className="w-full h-[680px] rounded-2xl shadow-inner" 
          />
        </div>

        {/* Range Stats cu shadcn/ui styling */}
        {rangesInfo.length > 0 && (
          <div className="text-xs grid gap-1 bg-card p-3 rounded-lg border border-border">
            <Label className="font-medium">Range Statistics:</Label>
            {rangesInfo.slice(-5).map((r, i) => (
              <div key={i} className="flex gap-3 text-muted-foreground">
                <div>{new Date(r.a * 1000).toISOString().slice(0, 10)} → {new Date(r.b * 1000).toISOString().slice(0, 10)}</div>
                <div>bars: <span className="font-medium">{r.bars}</span></div>
                <div>Δ: <span className={`font-medium ${r.delt >= 0 ? 'text-green-600' : 'text-red-600'}`}>{fmt(r.delt)} ({fmt(r.pct)}%)</span></div>
                <div>hi: <span className="text-green-600 font-medium">{fmt(r.hi)}</span> lo: <span className="text-red-600 font-medium">{fmt(r.lo)}</span></div>
              </div>
            ))}
          </div>
        )}

        {/* Import/Export JSON Dialog cu shadcn/ui */}
        <Dialog open={openIO} onOpenChange={setOpenIO}>
          <DialogContent className="sm:max-w-[800px]">
            <DialogHeader>
              <DialogTitle>Import / Export Drawings JSON</DialogTitle>
            </DialogHeader>
            <div className="grid gap-4">
              <div className="text-sm text-muted-foreground">
                Export: apasă <strong>Export</strong> ca să vezi JSON-ul curent. Import: lipește JSON și apasă <strong>Import</strong>.
              </div>
              <Textarea 
                value={jsonText} 
                onChange={(e) => setJsonText(e.target.value)} 
                className="min-h-[260px] font-mono text-xs" 
                placeholder='{ "hlines": [...], "trends": [...], ... }' 
              />
              <div className="flex flex-wrap gap-2">
                <Button variant="outline" onClick={openExport}>Export</Button>
                <Button variant="outline" onClick={doCopy}>Copy</Button>
                <Button variant="outline" onClick={doDownload}>Download .json</Button>
                <Button onClick={doImport}>Import</Button>
              </div>
            </div>
            <DialogFooter>
              <div className="text-xs text-muted-foreground">
                Key: <code className="bg-muted px-1 rounded">{drawKey}</code>
              </div>
            </DialogFooter>
          </DialogContent>
        </Dialog>

        {/* Footer Info */}
        <div className="text-center text-xs text-muted-foreground bg-card p-3 rounded-lg border border-border">
          <p>
            Desenele se salvează automat per simbol+TF sub cheia: 
            <code className="bg-muted px-1 rounded ml-1">{`${LS_DRAW_PREFIX}:${symbol}:${tf}`}</code>
          </p>
          <p className="mt-1">
            Export/Import transferă structuri JSON complete. Snap mode: OHLC precision drawing.
          </p>
        </div>
      </div>
    </div>
  );
}