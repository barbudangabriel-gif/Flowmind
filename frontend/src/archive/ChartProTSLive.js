import React, { useState, useRef, useEffect, useCallback, useMemo } from 'react';
import { TF_OPTS } from '../hooks/useOHLCV';
import { useTSStream } from '../lib/useTSStream';
import HeadlessChart from '../components/HeadlessChart';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Tabs, TabsList, TabsTrigger } from '../components/ui/tabs';
import { Separator } from '../components/ui/separator';
import { Switch } from '../components/ui/switch';
import { Label } from '../components/ui/label';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '../components/ui/dialog';
import { Textarea } from '../components/ui/textarea';
import { toast } from 'sonner';

// Technical indicators calculations
function sma(data, period) {
  if (!data || data.length < period) return [];
  const result = [];
  for (let i = period - 1; i < data.length; i++) {
    const sum = data.slice(i - period + 1, i + 1).reduce((s, d) => s + d.close, 0);
    result.push({ time: data[i].time, value: sum / period });
  }
  return result;
}

function ema(data, period) {
  if (!data || data.length < period) return [];
  const result = [];
  const k = 2 / (period + 1);
  let emaValue = data.slice(0, period).reduce((s, d) => s + d.close, 0) / period;
  
  for (let i = period - 1; i < data.length; i++) {
    if (i === period - 1) {
      emaValue = data.slice(0, period).reduce((s, d) => s + d.close, 0) / period;
    } else {
      emaValue = data[i].close * k + emaValue * (1 - k);
    }
    result.push({ time: data[i].time, value: emaValue });
  }
  return result;
}

function bollinger(data, period, stdDev) {
  if (!data || data.length < period) return { mid: [], up: [], dn: [] };
  
  const result = { mid: [], up: [], dn: [] };
  
  for (let i = period - 1; i < data.length; i++) {
    const slice = data.slice(i - period + 1, i + 1);
    const mean = slice.reduce((s, d) => s + d.close, 0) / period;
    const variance = slice.reduce((s, d) => s + Math.pow(d.close - mean, 2), 0) / period;
    const std = Math.sqrt(variance);
    
    result.mid.push({ time: data[i].time, value: mean });
    result.up.push({ time: data[i].time, value: mean + (std * stdDev) });
    result.dn.push({ time: data[i].time, value: mean - (std * stdDev) });
  }
  
  return result;
}

function rsi(data, period) {
  if (!data || data.length < period + 1) return [];
  
  const result = [];
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
      result.push({ time: data[i + 1].time, value: 100 });
    } else {
      const rs = avgGain / avgLoss;
      const rsiValue = 100 - (100 / (1 + rs));
      result.push({ time: data[i + 1].time, value: rsiValue });
    }
  }
  
  return result;
}

export default function ChartProTSLive({ 
  defaultSymbol = "NVDA", 
  defaultTf = "D" 
}) {
  const [symbol, setSymbol] = useState(defaultSymbol);
  const [tf, setTf] = useState(defaultTf);
  const [theme, setTheme] = useState("dark");
  const [live, setLive] = useState(false);
  
  // Indicators state
  const [show, setShow] = useState({
    sma: true,
    ema: false,
    bb: false,
    rsi: false
  });
  
  const [params, setParams] = useState({
    sma: 20,
    ema: 20,
    bbPeriod: 20,
    bbStd: 2,
    rsi: 14
  });

  // Chart references
  const chartRef = useRef(null);
  const series = useRef({});

  // Use TradeStation streaming or fallback to demo data
  const { bars: streamBars, status } = useTSStream({ 
    symbol, 
    tf, 
    barsBack: 1000 
  });

  // Demo data fallback when not live
  const demoData = useMemo(() => {
    if (live && streamBars.length > 0) return [];
    
    // Generate demo data
    const data = [];
    let price = 150 + Math.random() * 50;
    const now = Math.floor(Date.now() / 1000);
    const tfSeconds = { "1": 60, "5": 300, "15": 900, "60": 3600, "1h": 3600, "4h": 14400, "D": 86400, "W": 604800 };
    const seconds = tfSeconds[tf] || 86400;
    
    for (let i = 500; i >= 0; i--) {
      const time = now - (i * seconds);
      const change = (Math.random() - 0.5) * 4;
      const open = price;
      const close = price + change;
      const high = Math.max(open, close) + Math.random() * 2;
      const low = Math.min(open, close) - Math.random() * 2;
      const volume = Math.floor(Math.random() * 1000000) + 100000;
      
      data.push({ time, open, high, low, close, volume });
      price = close;
    }
    
    return data;
  }, [symbol, tf, live, streamBars.length]);

  // Use live stream data when available, otherwise demo data
  const baseData = live && streamBars.length > 0 ? streamBars : demoData;

  // Calculate indicators using memoization for performance
  const sma20 = useMemo(() => (show.sma ? sma(baseData, params.sma) : []), [baseData, show.sma, params.sma]);
  const ema20 = useMemo(() => (show.ema ? ema(baseData, params.ema) : []), [baseData, show.ema, params.ema]);
  const bb = useMemo(() => (show.bb ? bollinger(baseData, params.bbPeriod, params.bbStd) : { mid: [], up: [], dn: [] }), [baseData, show.bb, params.bbPeriod, params.bbStd]);
  const rsiData = useMemo(() => (show.rsi ? rsi(baseData, params.rsi) : []), [baseData, show.rsi, params.rsi]);

  // Chart ready callback
  const onReady = useCallback((api) => {
    console.log('📈 Chart Pro+++ TS Live ready!');
    
    chartRef.current = api.chart;
    
    // Add main candlestick series
    const candleSeries = api.addCandlestickSeries({
      title: symbol,
      upColor: '#16a34a',
      downColor: '#dc2626',
      borderDownColor: '#dc2626',
      borderUpColor: '#16a34a',
      wickDownColor: '#dc2626',
      wickUpColor: '#16a34a',
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

    // Add indicator series
    series.current.sma = api.chart.addLineSeries({
      color: '#2196F3',
      lineWidth: 2,
      title: `SMA(${params.sma})`,
      visible: show.sma
    });

    series.current.ema = api.chart.addLineSeries({
      color: '#FF9800',
      lineWidth: 2,
      title: `EMA(${params.ema})`,
      visible: show.ema
    });

    // Bollinger Bands
    series.current.bbU = api.chart.addLineSeries({
      color: '#9C27B0',
      lineWidth: 1,
      title: `BB Upper`,
      visible: show.bb
    });
    series.current.bbM = api.chart.addLineSeries({
      color: '#9C27B0',
      lineWidth: 1,
      lineStyle: 2,
      title: `BB Middle`,
      visible: show.bb
    });
    series.current.bbD = api.chart.addLineSeries({
      color: '#9C27B0',
      lineWidth: 1,
      title: `BB Lower`,
      visible: show.bb
    });

    // RSI series
    series.current.rsi = api.chart.addLineSeries({
      color: '#E91E63',
      lineWidth: 2,
      title: `RSI(${params.rsi})`,
      priceScaleId: 'rsi',
      scaleMargins: { top: 0.1, bottom: 0.1 },
      visible: show.rsi
    });

  }, [symbol, params, show]);

  // Update chart data when baseData changes
  useEffect(() => {
    if (!series.current.candle || !baseData.length) return;

    try {
      // Update main data
      const candleData = baseData.map(({ time, open, high, low, close }) => ({
        time, open, high, low, close
      }));
      series.current.candle.setData(candleData);

      // Update volume
      const volumeData = baseData.map(({ time, volume, open, close }) => ({
        time, 
        value: volume,
        color: close >= open ? "#16a34a55" : "#dc262655"
      }));
      series.current.volume.setData(volumeData);

      // Fit content
      if (chartRef.current) {
        chartRef.current.timeScale().fitContent();
      }

    } catch (error) {
      console.error('Chart update error:', error);
    }
  }, [baseData]);

  // Update indicators when calculated
  useEffect(() => {
    if (!series.current.candle) return;
    
    try {
      if (series.current.sma) {
        series.current.sma.setData(sma20);
        series.current.sma.applyOptions({ visible: show.sma });
      }
      if (series.current.ema) {
        series.current.ema.setData(ema20);
        series.current.ema.applyOptions({ visible: show.ema });
      }
      if (series.current.bbM) {
        series.current.bbM.setData(bb.mid);
        series.current.bbU.setData(bb.up);
        series.current.bbD.setData(bb.dn);
        series.current.bbM.applyOptions({ visible: show.bb });
        series.current.bbU.applyOptions({ visible: show.bb });
        series.current.bbD.applyOptions({ visible: show.bb });
      }
      if (series.current.rsi) {
        series.current.rsi.setData(rsiData);
        series.current.rsi.applyOptions({ visible: show.rsi });
      }
    } catch (error) {
      console.error('Indicators update error:', error);
    }
  }, [sma20, ema20, bb, rsiData, show]);

  // Export PNG functionality
  const exportPNG = useCallback(() => {
    try {
      const el = document.querySelector('#chart-root');
      const canvas = el?.querySelector('canvas');
      if (!canvas) {
        toast.error('Chart canvas not found');
        return;
      }
      
      const a = document.createElement('a');
      a.download = `${symbol}_${tf}_${new Date().toISOString().slice(0, 19).replace(/[:T]/g, '-')}.png`;
      a.href = canvas.toDataURL('image/png');
      a.click();
      
      toast.success('Chart exported as PNG!');
    } catch (error) {
      toast.error('Export failed: ' + error.message);
    }
  }, [symbol, tf]);

  // Import/Export drawings state
  const [openIO, setOpenIO] = useState(false);
  const [jsonText, setJsonText] = useState('');

  const doCopy = useCallback(() => {
    try {
      navigator.clipboard.writeText(jsonText);
      toast.success('JSON copied to clipboard!');
    } catch {
      toast.error('Copy failed');
    }
  }, [jsonText]);

  // Theme bridge
  useEffect(() => {
    try {
      document.documentElement.classList.toggle('dark', theme === 'dark');
      localStorage.setItem('flowmind.theme', theme);
    } catch {}
  }, [theme]);

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
      case "live": return "🟢";
      case "error": return "🔴";
      case "connecting": return "🟡";
      default: return "⚪";
    }
  };

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
              FlowMind Analytics - Chart Pro+++ Live
            </h1>
            <p className="text-muted-foreground mt-2 text-lg">
              Ultimate Trading Charts cu TradeStation Live Streaming, Technical Indicators și Advanced Tools
            </p>
            <div className="flex items-center justify-center gap-2 mt-3 text-sm">
              <span className="w-2 h-2 bg-brand-500 rounded-full"></span>
              <span className="text-brand-600">Live Trading Platform</span>
              {live && (
                <>
                  <span className={`ml-4 ${getStatusColor()}`}>
                    {getStatusIcon()} {status.toUpperCase()}
                  </span>
                </>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Main Interface */}
      <div className="max-w-7xl mx-auto px-4 py-6 space-y-4" id="chart-root">
        {/* Enhanced Toolbar */}
        <div className="flex flex-wrap items-center gap-3 bg-card p-4 rounded-lg shadow border border-border">
          <Input 
            className="w-[200px] font-semibold"
            value={symbol} 
            onChange={(e) => setSymbol(e.target.value.toUpperCase())} 
            placeholder="Symbol"
          />
          
          <Tabs value={tf} onValueChange={(v) => setTf(v)}>
            <TabsList className="grid w-auto grid-cols-7">
              {TF_OPTS.map(t => (
                <TabsTrigger key={t.v} value={t.v} className="text-xs">
                  {t.label}
                </TabsTrigger>
              ))}
            </TabsList>
          </Tabs>

          <Separator orientation="vertical" className="h-8" />

          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2">
              <Label>Live Stream</Label>
              <Switch checked={live} onCheckedChange={setLive} />
            </div>
            
            <Button 
              variant="outline" 
              onClick={() => setTheme(t => t === 'dark' ? 'light' : 'dark')}
            >
              {theme === 'dark' ? '🌙 Dark' : '☀️ Light'}
            </Button>
            
            <Button variant="outline" onClick={exportPNG}>
              📤 Export PNG
            </Button>
            
            <Button variant="outline" onClick={() => { setJsonText(''); setOpenIO(true); }}>
              📥📤 Import / Export JSON
            </Button>
          </div>

          <div className="ml-auto text-xs text-muted-foreground flex items-center gap-2">
            <span>Status:</span>
            <span className={`font-medium ${getStatusColor()}`}>
              {live ? status : 'Demo Mode'}
            </span>
            {live && status === 'live' && (
              <span className="text-green-500 font-medium">🔴 LIVE</span>
            )}
          </div>
        </div>

        {/* Chart - Super Black Background */}
        <div className="chart-perfect-fit w-full h-[680px]" style={{ backgroundColor: '#000000' }}>
          <HeadlessChart 
            theme={theme} 
            onReady={onReady} 
            className="w-full h-full" 
          />
        </div>

        {/* Technical Indicators Panel */}
        <div className="flex flex-wrap items-center gap-4 text-sm bg-card p-4 rounded-lg border border-border">
          <Label className="font-semibold text-foreground">Technical Indicators:</Label>
          
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

        {/* Live Data Stats */}
        {live && baseData.length > 0 && (
          <div className="bg-card p-4 rounded-lg border border-border">
            <div className="flex items-center justify-between mb-3">
              <Label className="font-semibold">📡 Live Market Data</Label>
              <div className={`text-sm font-medium ${getStatusColor()}`}>
                {getStatusIcon()} {status.toUpperCase()}
              </div>
            </div>
            
            <div className="grid grid-cols-2 md:grid-cols-5 gap-4 text-sm">
              {(() => {
                const latest = baseData[baseData.length - 1];
                return (
                  <>
                    <div>
                      <div className="text-muted-foreground">Open</div>
                      <div className="font-mono font-semibold">${latest.open.toFixed(2)}</div>
                    </div>
                    <div>
                      <div className="text-muted-foreground">High</div>
                      <div className="font-mono font-semibold text-green-600">${latest.high.toFixed(2)}</div>
                    </div>
                    <div>
                      <div className="text-muted-foreground">Low</div>
                      <div className="font-mono font-semibold text-red-600">${latest.low.toFixed(2)}</div>
                    </div>
                    <div>
                      <div className="text-muted-foreground">Close</div>
                      <div className="font-mono font-semibold">${latest.close.toFixed(2)}</div>
                    </div>
                    <div>
                      <div className="text-muted-foreground">Volume</div>
                      <div className="font-mono font-semibold text-blue-600">{latest.volume.toLocaleString()}</div>
                    </div>
                  </>
                );
              })()}
            </div>
          </div>
        )}

        {/* Import/Export Dialog */}
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
                placeholder={`{\n  "hlines": [...],\n  "trends": [...],\n  ...\n}`} 
              />
              <div className="flex gap-2">
                <Button variant="outline" onClick={doCopy}>📋 Copy</Button>
                <Button onClick={() => setOpenIO(false)}>Close</Button>
              </div>
            </div>
            <DialogFooter>
              <div className="text-xs text-muted-foreground">
                Symbol: <strong>{symbol}</strong> • TF: <strong>{tf}</strong> • Stream: <strong>{live ? status : 'off'}</strong>
              </div>
            </DialogFooter>
          </DialogContent>
        </Dialog>

        {/* Status Footer */}
        <div className="text-center text-xs text-muted-foreground bg-card p-3 rounded-lg border border-border">
          <div className="flex justify-center items-center gap-6">
            <div>Symbol: <span className="font-medium">{symbol}</span></div>
            <div>Timeframe: <span className="font-medium">{TF_OPTS.find(t => t.v === tf)?.label || tf}</span></div>
            <div>Data Source: <span className="font-medium">{live ? 'TradeStation Live' : 'Demo Data'}</span></div>
            <div>Bars: <span className="font-medium">{baseData.length}</span></div>
          </div>
          
          {live && (
            <div className="mt-2 text-brand-600">
              📡 Real-time TradeStation market data streaming active
            </div>
          )}
        </div>
      </div>
    </div>
  );
}