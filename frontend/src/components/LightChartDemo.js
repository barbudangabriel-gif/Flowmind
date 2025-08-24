import React, { useEffect, useRef, useState } from 'react';
import { createChart, ColorType } from 'lightweight-charts';

// Demo data generator for testing
function genDemoOHLCV(bars = 300) {
  const data = [];
  const sma = [];
  let price = 100 + Math.random() * 50;
  let time = Math.floor(Date.now() / 1000) - bars * 86400; // Daily bars
  
  for (let i = 0; i < bars; i++) {
    const change = (Math.random() - 0.5) * 4;
    const open = price;
    const close = price + change;
    const high = Math.max(open, close) + Math.random() * 2;
    const low = Math.min(open, close) - Math.random() * 2;
    const volume = Math.floor(Math.random() * 1000000) + 100000;
    const up = close > open;
    
    data.push({ time, open, high, low, close, volume, up });
    
    // Simple Moving Average (20)
    if (i >= 19) {
      const sum = data.slice(i - 19, i + 1).reduce((s, d) => s + d.close, 0);
      sma.push({ time, value: sum / 20 });
    }
    
    price = close;
    time += 86400; // Next day
  }
  
  return { data, sma20: sma };
}

export default function LightChartDemo() {
  const containerRef = useRef(null);
  const chartRef = useRef(null);
  const candleRef = useRef(null);
  const volRef = useRef(null);
  const smaRef = useRef(null);
  
  const [symbol, setSymbol] = useState('AAPL');
  const [theme, setTheme] = useState('dark');
  const [bars, setBars] = useState(300);
  
  // Generate demo data
  const { data, sma20 } = genDemoOHLCV(bars);

  // Initialize chart
  useEffect(() => {
    if (!containerRef.current) return;

    const chart = createChart(containerRef.current, {
      layout: {
        background: { type: ColorType.Solid, color: theme === 'dark' ? '#1a1a1a' : '#ffffff' },
        textColor: theme === 'dark' ? '#e5e5e5' : '#333333',
      },
      grid: {
        vertLines: { color: theme === 'dark' ? '#2a2a2a' : '#e0e0e0' },
        horzLines: { color: theme === 'dark' ? '#2a2a2a' : '#e0e0e0' },
      },
      crosshair: {
        mode: 0, // Normal crosshair
      },
      timeScale: {
        borderColor: theme === 'dark' ? '#485158' : '#cccccc',
        timeVisible: true,
        secondsVisible: false,
      },
      rightPriceScale: {
        borderColor: theme === 'dark' ? '#485158' : '#cccccc',
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

    chartRef.current = chart;

    // Add candlestick series
    const candlestickSeries = chart.addCandlestickSeries({
      upColor: '#16a34a',
      downColor: '#dc2626',
      borderDownColor: '#dc2626',
      borderUpColor: '#16a34a',
      wickDownColor: '#dc2626',
      wickUpColor: '#16a34a',
    });
    candleRef.current = candlestickSeries;

    // Add volume series
    const volumeSeries = chart.addHistogramSeries({
      color: '#26a69a',
      priceFormat: {
        type: 'volume',
      },
      priceScaleId: '',
      scaleMargins: {
        top: 0.7,
        bottom: 0,
      },
    });
    volRef.current = volumeSeries;

    // Add SMA series
    const smaSeries = chart.addLineSeries({
      color: '#2196F3',
      lineWidth: 2,
      title: 'SMA(20)',
    });
    smaRef.current = smaSeries;

    // Handle resize
    const ro = new ResizeObserver(() => chart.applyOptions({ autoSize: true }));
    ro.observe(containerRef.current);

    return () => { 
      ro.disconnect(); 
      chart.remove(); 
    };
  }, [theme]);

  // Update data when changes
  useEffect(() => {
    if (!candleRef.current || !volRef.current || !smaRef.current) return;
    
    candleRef.current.setData(data.map(({ time, open, high, low, close }) => ({ time, open, high, low, close })));
    volRef.current.setData(data.map(({ time, volume, up }) => ({ time, value: volume, color: up ? "#16a34a55" : "#dc262655" })));
    smaRef.current.setData(sma20);
    chartRef.current?.timeScale().fitContent();
  }, [data, sma20]);

  return (
    <div className="w-full h-full min-h-[720px] p-4 bg-neutral-900/40 dark:bg-neutral-900/40">
      {/* Toolbar */}
      <div className="mb-3 flex flex-wrap items-center gap-2">
        <span className="text-sm opacity-70 text-white">Symbol</span>
        <input
          className="px-2 py-1 rounded border border-neutral-700 bg-neutral-800 text-neutral-100"
          value={symbol}
          onChange={(e) => setSymbol(e.target.value.toUpperCase())}
          title="Placeholder vizual; feed-ul de date este demo"
        />
        <span className="text-xs opacity-60 text-gray-400">(demo data – nu schimbă feed-ul)</span>
        <div className="ml-auto flex items-center gap-2">
          <button
            onClick={() => setTheme((t) => (t === "dark" ? "light" : "dark"))}
            className="px-3 py-1 rounded-lg shadow border border-neutral-700 hover:bg-neutral-800 text-neutral-100"
            title="Toggle theme"
          >
            {theme === "dark" ? "🌙 Dark" : "☀️ Light"}
          </button>
          <select
            className="px-2 py-1 rounded border border-neutral-700 bg-neutral-800 text-neutral-100"
            value={bars}
            onChange={(e) => setBars(Number(e.target.value))}
            title="Număr de bare (demo)"
          >
            <option value={150}>150 bars</option>
            <option value={300}>300 bars</option>
            <option value={600}>600 bars</option>
          </select>
        </div>
      </div>

      {/* Chart container */}
      <div ref={containerRef} className="w-full h-[640px] rounded-2xl shadow-inner bg-neutral-800" />

      {/* Helper text */}
      <div className="mt-3 text-xs opacity-70 text-gray-400">
        <p>
          Professional TradingView Lightweight Charts cu candlesticks + volume + SMA(20).
          Integrare: importați <code>LightChartDemo</code> într-o rută React, ex: <code>/chart-lite</code>.
          Înlocuiți <em>genDemoOHLCV</em> cu feed-ul vostru de OHLCV (UNIX seconds + OHLCV).
        </p>
      </div>
    </div>
  );
}