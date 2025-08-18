import React, { useEffect, useRef, useState } from 'react';
import { createChart, CrosshairMode } from 'lightweight-charts';
import axios from 'axios';

// Get backend URL from environment
const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const TradingChart = ({ symbol, interval = '1D', height = 500 }) => {
  const mainChartRef = useRef();
  const volumeChartRef = useRef();
  const containerRef = useRef();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [mainChart, setMainChart] = useState(null);
  const [volumeChart, setVolumeChart] = useState(null);
  const [selectedInterval, setSelectedInterval] = useState(interval);
  const [selectedIndicators, setSelectedIndicators] = useState(['volume']);
  const [chartData, setChartData] = useState([]);

  // Complete timeframes like professional trading platforms
  const timeframes = [
    { label: '1m', value: '1m', seconds: 60 },
    { label: '5m', value: '5m', seconds: 300 },
    { label: '15m', value: '15m', seconds: 900 },
    { label: '1H', value: '1h', seconds: 3600 },
    { label: '4H', value: '4h', seconds: 14400 },
    { label: '1D', value: '1d', seconds: 86400 },
    { label: '1W', value: '1w', seconds: 604800 },
    { label: '1M', value: '1M', seconds: 2629746 }
  ];

  // Complete technical indicators
  const technicalIndicators = [
    { id: 'sma_9', label: 'SMA 9', type: 'overlay', color: '#FF6B35', period: 9 },
    { id: 'sma_20', label: 'SMA 20', type: 'overlay', color: '#F7931E', period: 20 },
    { id: 'sma_50', label: 'SMA 50', type: 'overlay', color: '#FFD23F', period: 50 },
    { id: 'sma_200', label: 'SMA 200', type: 'overlay', color: '#06FFA5', period: 200 },
    { id: 'ema_9', label: 'EMA 9', type: 'overlay', color: '#3B82F6', period: 9 },
    { id: 'ema_21', label: 'EMA 21', type: 'overlay', color: '#8B5CF6', period: 21 },
    { id: 'ema_50', label: 'EMA 50', type: 'overlay', color: '#EC4899', period: 50 },
    { id: 'bb_20', label: 'Bollinger Bands', type: 'overlay', color: '#6B7280', period: 20 },
    { id: 'rsi_14', label: 'RSI (14)', type: 'oscillator', color: '#EF4444', period: 14 },
    { id: 'macd', label: 'MACD', type: 'oscillator', color: '#10B981' },
    { id: 'stoch', label: 'Stochastic', type: 'oscillator', color: '#F59E0B' },
    { id: 'volume', label: 'Volume', type: 'volume', color: '#6366F1', enabled: true }
  ];

  // Generate realistic market data based on current price
  const generateRealisticMarketData = async (symbol, timeframe, bars = 200) => {
    try {
      // Get real current price
      const priceResponse = await axios.get(`${API}/investments/score/${symbol.toUpperCase()}`);
      const currentPrice = priceResponse.data?.stock_data?.price || 100;
      
      console.log(`Generating ${bars} bars for ${symbol} at $${currentPrice} (${timeframe})`);
      
      const data = [];
      const now = new Date();
      const timeframeSec = timeframes.find(tf => tf.value === timeframe)?.seconds || 86400;
      
      for (let i = bars - 1; i >= 0; i--) {
        const date = new Date(now.getTime() - (i * timeframeSec * 1000));
        
        // Create realistic price movement
        const trend = Math.sin(i / 20) * 0.05; // Long term trend
        const volatility = currentPrice * 0.02; // 2% volatility
        const noise = (Math.random() - 0.5) * volatility;
        
        const basePrice = currentPrice * (1 + trend + (noise * (i / bars)));
        const variation = basePrice * 0.015; // 1.5% intraday variation
        
        const open = basePrice + (Math.random() - 0.5) * variation;
        const close = i === 0 ? currentPrice : basePrice + (Math.random() - 0.5) * variation;
        const high = Math.max(open, close) + Math.random() * variation * 0.5;
        const low = Math.min(open, close) - Math.random() * variation * 0.5;
        
        // Realistic volume based on price movement
        const priceChange = Math.abs((close - open) / open);
        const baseVolume = 500000 + (priceChange * 2000000);
        const volume = Math.floor(baseVolume * (0.5 + Math.random()));
        
        data.push({
          time: Math.floor(date.getTime() / 1000),
          open: parseFloat(open.toFixed(2)),
          high: parseFloat(high.toFixed(2)),
          low: parseFloat(low.toFixed(2)),
          close: parseFloat(close.toFixed(2)),
          volume: volume
        });
      }
      
      return data.sort((a, b) => a.time - b.time);
    } catch (error) {
      console.error('Error generating market data:', error);
      return [];
    }
  };

  // Calculate all technical indicators
  const calculateTechnicalIndicators = (data) => {
    const indicators = {};
    
    // Simple Moving Average
    const calculateSMA = (data, period) => {
      return data.map((item, index) => {
        if (index < period - 1) return null;
        const sum = data.slice(index - period + 1, index + 1)
          .reduce((acc, d) => acc + d.close, 0);
        return {
          time: item.time,
          value: sum / period
        };
      }).filter(item => item !== null);
    };

    // Exponential Moving Average
    const calculateEMA = (data, period) => {
      const multiplier = 2 / (period + 1);
      const ema = [];
      
      data.forEach((item, index) => {
        if (index === 0) {
          ema.push({ time: item.time, value: item.close });
        } else {
          const value = (item.close * multiplier) + (ema[index - 1].value * (1 - multiplier));
          ema.push({ time: item.time, value });
        }
      });
      
      return ema.slice(period - 1);
    };

    // RSI (Relative Strength Index)
    const calculateRSI = (data, period = 14) => {
      const rsi = [];
      const gains = [];
      const losses = [];
      
      for (let i = 1; i < data.length; i++) {
        const change = data[i].close - data[i - 1].close;
        gains.push(change > 0 ? change : 0);
        losses.push(change < 0 ? Math.abs(change) : 0);
        
        if (i >= period) {
          const avgGain = gains.slice(-period).reduce((a, b) => a + b) / period;
          const avgLoss = losses.slice(-period).reduce((a, b) => a + b) / period;
          const rs = avgGain / (avgLoss || 1);
          const rsiValue = 100 - (100 / (1 + rs));
          
          rsi.push({
            time: data[i].time,
            value: rsiValue
          });
        }
      }
      
      return rsi;
    };

    // MACD
    const calculateMACD = (data) => {
      const ema12 = calculateEMA(data, 12);
      const ema26 = calculateEMA(data, 26);
      const macd = [];
      
      const minLength = Math.min(ema12.length, ema26.length);
      for (let i = 0; i < minLength; i++) {
        const macdValue = ema12[i].value - ema26[i].value;
        macd.push({
          time: ema12[i].time,
          value: macdValue
        });
      }
      
      const signal = calculateEMA(macd.map(m => ({ close: m.value, time: m.time })), 9);
      const histogram = macd.map((m, i) => ({
        time: m.time,
        value: signal[i] ? m.value - signal[i].value : 0
      }));
      
      return { macd, signal, histogram };
    };

    // Bollinger Bands
    const calculateBollingerBands = (data, period = 20, stdDev = 2) => {
      const sma = calculateSMA(data, period);
      const bands = { upper: [], middle: [], lower: [] };
      
      sma.forEach((smaPoint, index) => {
        const dataIndex = index + period - 1;
        if (dataIndex >= data.length) return;
        
        const slice = data.slice(dataIndex - period + 1, dataIndex + 1);
        const variance = slice.reduce((acc, d) => acc + Math.pow(d.close - smaPoint.value, 2), 0) / period;
        const standardDeviation = Math.sqrt(variance);
        
        bands.upper.push({ time: smaPoint.time, value: smaPoint.value + (stdDev * standardDeviation) });
        bands.middle.push({ time: smaPoint.time, value: smaPoint.value });
        bands.lower.push({ time: smaPoint.time, value: smaPoint.value - (stdDev * standardDeviation) });
      });
      
      return bands;
    };

    // Stochastic Oscillator
    const calculateStochastic = (data, period = 14) => {
      const stoch = [];
      
      for (let i = period - 1; i < data.length; i++) {
        const slice = data.slice(i - period + 1, i + 1);
        const highest = Math.max(...slice.map(d => d.high));
        const lowest = Math.min(...slice.map(d => d.low));
        const current = data[i].close;
        
        const k = ((current - lowest) / (highest - lowest)) * 100;
        stoch.push({
          time: data[i].time,
          value: k
        });
      }
      
      return stoch;
    };

    // Calculate all indicators
    indicators.sma_9 = calculateSMA(data, 9);
    indicators.sma_20 = calculateSMA(data, 20);
    indicators.sma_50 = calculateSMA(data, 50);
    indicators.sma_200 = calculateSMA(data, 200);
    indicators.ema_9 = calculateEMA(data, 9);
    indicators.ema_21 = calculateEMA(data, 21);
    indicators.ema_50 = calculateEMA(data, 50);
    indicators.bb_20 = calculateBollingerBands(data, 20, 2);
    indicators.rsi_14 = calculateRSI(data, 14);
    indicators.macd = calculateMACD(data);
    indicators.stoch = calculateStochastic(data, 14);
    
    // Volume data
    indicators.volume = data.map(item => ({
      time: item.time,
      value: item.volume,
      color: item.close >= item.open ? '#26a69a80' : '#ef537080'
    }));

    return indicators;
  };

  // Create charts with error handling
  useEffect(() => {
    if (!mainChartRef.current || !volumeChartRef.current || !symbol) return;

    const initializeCharts = async () => {
      setLoading(true);
      setError(null);

      try {
        // Generate realistic market data
        console.log(`Initializing advanced chart for ${symbol}`);
        
        // Get real price
        const priceResponse = await axios.get(`${API}/investments/score/${symbol.toUpperCase()}`);
        const currentPrice = priceResponse.data?.stock_data?.price || 100;
        
        // Generate simple realistic data
        const data = [];
        const now = Date.now();
        const oneDay = 24 * 60 * 60 * 1000;
        
        for (let i = 49; i >= 0; i--) {
          const timestamp = Math.floor((now - (i * oneDay)) / 1000);
          const variation = currentPrice * 0.02 * (Math.random() - 0.5);
          const basePrice = currentPrice + variation;
          
          const open = basePrice * (0.98 + Math.random() * 0.04);
          const close = i === 0 ? currentPrice : basePrice * (0.98 + Math.random() * 0.04);
          const high = Math.max(open, close) * (1 + Math.random() * 0.02);
          const low = Math.min(open, close) * (1 - Math.random() * 0.02);
          const volume = 500000 + Math.random() * 1000000;
          
          data.push({
            time: timestamp,
            open: parseFloat(open.toFixed(2)),
            high: parseFloat(high.toFixed(2)),
            low: parseFloat(low.toFixed(2)),
            close: parseFloat(close.toFixed(2)),
            volume: Math.floor(volume)
          });
        }
        
        setChartData(data);
        console.log(`Generated ${data.length} data points for ${symbol} at $${currentPrice}`);

        // Clear containers
        if (mainChartRef.current) mainChartRef.current.innerHTML = '';
        if (volumeChartRef.current) volumeChartRef.current.innerHTML = '';

        // Create main chart
        const mainChartInstance = createChart(mainChartRef.current, {
          width: mainChartRef.current.clientWidth || 800,
          height: height * 0.7,
          layout: {
            background: { color: '#0f0f0f' },
            textColor: '#d1d5db',
          },
          grid: {
            vertLines: { color: '#1f1f1f' },
            horzLines: { color: '#1f1f1f' },
          },
          crosshair: { mode: CrosshairMode.Normal },
          timeScale: { timeVisible: true },
          rightPriceScale: { textColor: '#d1d5db' }
        });

        // Create volume chart
        const volumeChartInstance = createChart(volumeChartRef.current, {
          width: volumeChartRef.current.clientWidth || 800,
          height: height * 0.3,
          layout: {
            background: { color: '#0f0f0f' },
            textColor: '#d1d5db',
          },
          grid: {
            vertLines: { color: '#1f1f1f' },
            horzLines: { color: '#1f1f1f' },
          },
          timeScale: { timeVisible: true },
          rightPriceScale: { textColor: '#d1d5db' }
        });

        // Add candlestick series
        const candlestickSeries = mainChartInstance.addCandlestickSeries({
          upColor: '#26a69a',
          downColor: '#ef5350',
          borderVisible: false,
          wickUpColor: '#26a69a',
          wickDownColor: '#ef5350',
        });
        candlestickSeries.setData(data);

        // Add volume series
        const volumeData = data.map(item => ({
          time: item.time,
          value: item.volume,
          color: item.close >= item.open ? '#26a69a80' : '#ef535080'
        }));
        
        const volumeSeries = volumeChartInstance.addHistogramSeries({
          color: '#26a69a',
          priceFormat: { type: 'volume' },
        });
        volumeSeries.setData(volumeData);

        setMainChart(mainChartInstance);
        setVolumeChart(volumeChartInstance);
        setLoading(false);

        console.log('Charts initialized successfully');

      } catch (err) {
        console.error('Chart initialization error:', err);
        setError(`Chart Error: ${err.message}`);
        setLoading(false);
      }
    };

    const timeoutId = setTimeout(initializeCharts, 100);
    return () => clearTimeout(timeoutId);
  }, [symbol, selectedInterval, height]);

  const handleTimeframeChange = (timeframe) => {
    setSelectedInterval(timeframe);
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

  if (loading) {
    return (
      <div className="bg-gray-900 rounded-lg p-6 text-center">
        <div className="animate-spin w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full mx-auto mb-4"></div>
        <div className="text-gray-400">Loading advanced chart for {symbol}...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-gray-900 rounded-lg p-6 text-center">
        <div className="text-red-400 mb-2">Chart Error</div>
        <div className="text-gray-400 text-sm mb-4">{error}</div>
        <button 
          onClick={() => setSelectedInterval(selectedInterval)}
          className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm"
        >
          Retry
        </button>
      </div>
    );
  }

  return (
    <div ref={containerRef} className="bg-gray-900 rounded-lg overflow-hidden">
      {/* Chart Controls */}
      <div className="bg-gray-800 p-4 border-b border-gray-700">
        {/* Timeframe Controls */}
        <div className="flex items-center gap-2 mb-4">
          <span className="text-gray-400 text-sm font-medium mr-2">Timeframe:</span>
          {timeframes.map((tf) => (
            <button
              key={tf.value}
              onClick={() => handleTimeframeChange(tf.value)}
              className={`px-3 py-1 text-sm rounded transition-colors ${
                selectedInterval === tf.value
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
              }`}
            >
              {tf.label}
            </button>
          ))}
        </div>

        {/* Technical Indicators */}
        <div className="flex flex-wrap gap-2">
          <span className="text-gray-400 text-sm font-medium mr-2">Indicators:</span>
          {technicalIndicators.map((indicator) => (
            <button
              key={indicator.id}
              onClick={() => toggleIndicator(indicator.id)}
              className={`px-3 py-1 text-xs rounded transition-colors ${
                selectedIndicators.includes(indicator.id)
                  ? 'text-white border'
                  : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
              }`}
              style={{
                backgroundColor: selectedIndicators.includes(indicator.id) ? indicator.color : undefined,
                borderColor: selectedIndicators.includes(indicator.id) ? indicator.color : undefined
              }}
            >
              {indicator.label}
            </button>
          ))}
        </div>
      </div>

      {/* Chart Container */}
      <div className="relative">
        {/* Main Price Chart */}
        <div 
          ref={mainChartRef} 
          className="w-full"
          style={{ height: height * 0.7 }}
        />
        
        {/* Volume Chart */}
        <div 
          ref={volumeChartRef} 
          className="w-full border-t border-gray-700"
          style={{ height: height * 0.3 }}
        />
      </div>

      {/* Chart Info */}
      <div className="bg-gray-800 p-3 border-t border-gray-700">
        <div className="flex items-center justify-between text-xs text-gray-400">
          <div>
            Symbol: <span className="text-white font-medium">{symbol}</span>
            {' • '}
            Interval: <span className="text-white">{selectedInterval}</span>
            {' • '}
            Bars: <span className="text-white">{chartData.length}</span>
          </div>
          <div>
            Indicators: <span className="text-white">{selectedIndicators.length}</span>
            {' • '}
            Last Update: <span className="text-white">{new Date().toLocaleTimeString()}</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TradingChart;