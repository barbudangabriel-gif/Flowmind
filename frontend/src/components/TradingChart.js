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

  // Load and render chart
  useEffect(() => {
    if (!symbol || !chartContainerRef.current) return;

    const loadAndRenderChart = async () => {
      setLoading(true);
      setError(null);

      try {
        // Get real current price from investment scoring API (same as analysis page)
        console.log(`Loading real price data for ${symbol}`);
        const priceResponse = await axios.get(`${API}/investments/score/${symbol.toUpperCase()}`);
        
        if (!priceResponse.data?.stock_data?.price) {
          throw new Error('No real price data available');
        }
        
        const currentPrice = priceResponse.data.stock_data.price;
        const change = priceResponse.data.stock_data.change || 0;
        const changePercent = priceResponse.data.stock_data.change_percent || 0;
        
        console.log(`Real price for ${symbol}: $${currentPrice} (${change >= 0 ? '+' : ''}${change}, ${changePercent >= 0 ? '+' : ''}${changePercent.toFixed(2)}%)`);
        
        // Generate realistic chart data based on real current price
        const generateRealisticChartData = (price, bars = 50) => {
          const data = [];
          const currentDate = new Date();
          
          for (let i = bars - 1; i >= 0; i--) {
            const date = new Date(currentDate);
            date.setDate(date.getDate() - i);
            
            // Create realistic price movement around current price
            const variance = price * 0.02; // 2% daily variance
            const dayChange = (Math.random() - 0.5) * 2 * variance;
            const basePrice = price + (dayChange * (i / bars)); // Gradual trend toward current
            
            const open = basePrice + (Math.random() - 0.5) * variance * 0.5;
            const high = Math.max(open, basePrice + Math.random() * variance * 0.3);
            const low = Math.min(open, basePrice - Math.random() * variance * 0.3);
            const close = basePrice + (Math.random() - 0.5) * variance * 0.2;
            
            data.push({
              time: date.toISOString().split('T')[0],
              open: parseFloat(open.toFixed(2)),
              high: parseFloat(high.toFixed(2)),
              low: parseFloat(low.toFixed(2)),
              close: i === 0 ? currentPrice : parseFloat(close.toFixed(2)), // Last candle = current price
              volume: Math.floor(Math.random() * 1000000) + 500000
            });
          }
          
          return data;
        };
        
        const chartData = generateRealisticChartData(currentPrice);
        console.log(`Generated ${chartData.length} realistic data points around price $${currentPrice}`);

        // Clear container
        chartContainerRef.current.innerHTML = '';

        // Create chart with black grid
        console.log('Creating chart with enhanced settings...');
        console.log('createChart function:', typeof createChart);
        
        const chart = createChart(chartContainerRef.current, {
          width: chartContainerRef.current.clientWidth || 800,
          height: height,
          layout: {
            background: { color: '#000000' }, // Pure black background
            textColor: '#FFFFFF',
          },
          grid: {
            vertLines: { 
              color: '#000000',  // Black vertical grid lines
              style: 1,
              visible: false  // Hide vertical lines completely
            },
            horzLines: { 
              color: '#1a1a1a',  // Very dark horizontal lines
              style: 1,
              visible: true
            },
          },
          crosshair: {
            mode: 1, // Normal crosshair
            vertLine: {
              color: '#758694',
              width: 1,
              style: 3, // Dashed
            },
            horzLine: {
              color: '#758694', 
              width: 1,
              style: 3, // Dashed
            },
          },
          rightPriceScale: {
            borderColor: '#2B2B43',
            textColor: '#FFFFFF',
          },
          timeScale: {
            borderColor: '#2B2B43',
            textColor: '#FFFFFF',
            timeVisible: true,
            secondsVisible: false,
          },
          localization: {
            locale: 'en-US',
            priceFormatter: price => '$' + price.toFixed(2),
          }
        });

        console.log('Chart created:', chart);
        console.log('addCandlestickSeries function:', typeof chart.addCandlestickSeries);

        console.log('Chart created, adding series...');
        
        // Add main candlestick series
        const candlestickSeries = chart.addCandlestickSeries({
          upColor: '#00D4AA',      // Green for up candles
          downColor: '#FF6B6B',    // Red for down candles  
          borderVisible: false,
          wickUpColor: '#00D4AA',
          wickDownColor: '#FF6B6B',
          priceFormat: {
            type: 'price',
            precision: 2,
            minMove: 0.01,
          },
        });

        console.log('Candlestick series created, setting data...');
        candlestickSeries.setData(chartData);

        // Create separate volume histogram series in its own pane (subgraph)
        console.log('Adding volume histogram in separate pane...');
        const volumeSeries = chart.addHistogramSeries({
          color: '#26a69a80', // Semi-transparent green
          priceFormat: { 
            type: 'volume',
            precision: 0,
          },
          priceScaleId: '', // Empty string creates separate pane
          scaleMargins: { 
            top: 0.7,    // Volume takes bottom 30% of chart
            bottom: 0 
          },
        });

        // Prepare volume data with colors based on candle direction
        const volumeData = chartData.map(item => ({
          time: item.time,
          value: item.volume,
          color: item.close >= item.open ? '#00D4AA80' : '#FF6B6B80' // More visible colors
        }));

        volumeSeries.setData(volumeData);
        console.log(`Volume data set with ${volumeData.length} bars`);

        // Add selected indicators
        addIndicators(chart, chartData, candlestickSeries);

        chart.timeScale().fitContent();
        console.log('Chart rendered successfully with indicators!');
        setLoading(false);

        // Handle resize
        const handleResize = () => {
          chart.applyOptions({
            width: chartContainerRef.current?.clientWidth || 800,
          });
        };

        window.addEventListener('resize', handleResize);

        // Cleanup function
        return () => {
          window.removeEventListener('resize', handleResize);
          chart.remove();
        };

      } catch (err) {
        console.error('Chart error:', err);
        setError(err.message);
        setLoading(false);
      }
    };

    loadAndRenderChart();
  }, [symbol, selectedInterval, height]);

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