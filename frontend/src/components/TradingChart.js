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

  // Calculate technical indicators
  const calculateIndicators = (data) => {
    const indicators = {};

    // Simple Moving Average
    const calculateSMA = (period) => {
      return data.map((item, index) => {
        if (index < period - 1) return { time: item.time, value: null };
        const sum = data.slice(index - period + 1, index + 1).reduce((acc, d) => acc + d.close, 0);
        return { time: item.time, value: sum / period };
      }).filter(item => item.value !== null);
    };

    // Exponential Moving Average
    const calculateEMA = (period) => {
      const multiplier = 2 / (period + 1);
      const ema = [];
      let emaValue = data[0].close; // Start with first close price
      
      data.forEach((item, index) => {
        if (index === 0) {
          emaValue = item.close;
        } else {
          emaValue = (item.close * multiplier) + (emaValue * (1 - multiplier));
        }
        ema.push({ time: item.time, value: emaValue });
      });
      
      return ema;
    };

    // RSI Calculation
    const calculateRSI = (period = 14) => {
      if (data.length < period + 1) return [];
      
      const rsiData = [];
      let gains = 0;
      let losses = 0;
      
      // Calculate initial average gain/loss
      for (let i = 1; i <= period; i++) {
        const change = data[i].close - data[i - 1].close;
        if (change > 0) gains += change;
        else losses += Math.abs(change);
      }
      
      let avgGain = gains / period;
      let avgLoss = losses / period;
      
      for (let i = period; i < data.length; i++) {
        const change = data[i].close - data[i - 1].close;
        const gain = change > 0 ? change : 0;
        const loss = change < 0 ? Math.abs(change) : 0;
        
        avgGain = ((avgGain * (period - 1)) + gain) / period;
        avgLoss = ((avgLoss * (period - 1)) + loss) / period;
        
        const rs = avgGain / avgLoss;
        const rsi = 100 - (100 / (1 + rs));
        
        rsiData.push({ time: data[i].time, value: rsi });
      }
      
      return rsiData;
    };

    // Calculate Bollinger Bands
    const calculateBollingerBands = (period = 20, stdDev = 2) => {
      const sma = calculateSMA(period);
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

    // Calculate volume data for histogram
    const volumeData = data.map(item => ({
      time: item.time,
      value: item.volume,
      color: item.close >= item.open ? '#00D4AA33' : '#FF6B6B33'
    }));

    // Store calculated indicators
    indicators.sma20 = calculateSMA(20);
    indicators.sma50 = calculateSMA(50);
    indicators.ema12 = calculateEMA(12);
    indicators.ema26 = calculateEMA(26);
    indicators.rsi = calculateRSI(14);
    indicators.bollinger = calculateBollingerBands(20, 2);
    indicators.volume = volumeData;

    return indicators;
  };

  // Add indicators to chart (excluding volume since it's already in subgraph)
  const addIndicators = (chart, chartData, mainSeries) => {
    if (!selectedIndicators.length) return;

    const indicators = calculateIndicators(chartData);

    selectedIndicators.forEach(indicatorId => {
      switch (indicatorId) {
        case 'volume':
          // Volume is already added as separate histogram, skip here
          console.log('Volume already added in separate pane');
          break;

        case 'sma20':
          const sma20Series = chart.addLineSeries({
            color: '#FF9500',
            lineWidth: 2,
            title: 'SMA 20',
          });
          sma20Series.setData(indicators.sma20);
          break;

        case 'sma50':
          const sma50Series = chart.addLineSeries({
            color: '#9013FE',
            lineWidth: 2,
            title: 'SMA 50',
          });
          sma50Series.setData(indicators.sma50);
          break;

        case 'ema12':
          const ema12Series = chart.addLineSeries({
            color: '#2196F3',
            lineWidth: 1,
            title: 'EMA 12',
          });
          ema12Series.setData(indicators.ema12);
          break;

        case 'ema26':
          const ema26Series = chart.addLineSeries({
            color: '#FF5722',
            lineWidth: 1,
            title: 'EMA 26',
          });
          ema26Series.setData(indicators.ema26);
          break;

        case 'bollinger':
          const upperSeries = chart.addLineSeries({
            color: '#E91E63',
            lineWidth: 1,
            title: 'BB Upper',
          });
          const middleSeries = chart.addLineSeries({
            color: '#795548',
            lineWidth: 1,
            title: 'BB Middle',
          });
          const lowerSeries = chart.addLineSeries({
            color: '#E91E63',
            lineWidth: 1,
            title: 'BB Lower',
          });
          upperSeries.setData(indicators.bollinger.upper);
          middleSeries.setData(indicators.bollinger.middle);
          lowerSeries.setData(indicators.bollinger.lower);
          break;

        default:
          break;
      }
    });
  };

  // Handle indicator selection
  const toggleIndicator = (indicatorId) => {
    setSelectedIndicators(prev => {
      const newSelection = prev.includes(indicatorId)
        ? prev.filter(id => id !== indicatorId)
        : [...prev, indicatorId];
      return newSelection;
    });
  };

  const handleIntervalChange = (newInterval) => {
    console.log(`Changing interval to ${newInterval}`);
    setSelectedInterval(newInterval);
  };

  if (error) {
    return (
      <div className="bg-gray-800 rounded-lg p-6 text-center">
        <div className="text-red-400 mb-2">Chart Error</div>
        <div className="text-gray-400 text-sm">{error}</div>
        <button 
          onClick={() => setSelectedInterval(selectedInterval)} // Trigger reload
          className="mt-4 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm"
        >
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="bg-gray-900 rounded-lg p-4">
      {/* Chart Header */}
      <div className="flex flex-col space-y-4 mb-4">
        <div className="flex justify-between items-center">
          <div className="flex items-center space-x-2">
            <h3 className="text-lg font-semibold text-white">{symbol} Chart</h3>
            {loading && (
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-500"></div>
            )}
          </div>
          
          {/* Interval Selector */}
          <div className="flex space-x-1">
            {intervals.map((int) => (
              <button
                key={int.value}
                onClick={() => handleIntervalChange(int.value)}
                className={`px-3 py-1 text-xs rounded transition-colors ${
                  selectedInterval === int.value
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                }`}
              >
                {int.label}
              </button>
            ))}
          </div>
        </div>

        {/* Indicators Selector */}
        <div className="flex flex-wrap gap-2">
          <span className="text-sm text-gray-400 mr-2">Indicators:</span>
          {availableIndicators.map((indicator) => (
            <button
              key={indicator.id}
              onClick={() => toggleIndicator(indicator.id)}
              className={`px-2 py-1 text-xs rounded transition-colors ${
                selectedIndicators.includes(indicator.id)
                  ? 'bg-green-600 text-white'
                  : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
              }`}
            >
              {indicator.label}
            </button>
          ))}
        </div>
      </div>

      {/* Chart Container */}
      <div 
        ref={chartContainerRef}
        className="w-full bg-black rounded" // Black background for chart
        style={{ height: `${height}px` }}
      />
      
      {/* Chart Info */}
      <div className="mt-2 text-xs text-gray-400 text-center">
        {loading ? 'Loading chart data...' : `${symbol?.toUpperCase()} • ${selectedInterval} • ${selectedIndicators.length} indicators`}
      </div>
    </div>
  );
};

export default TradingChart;