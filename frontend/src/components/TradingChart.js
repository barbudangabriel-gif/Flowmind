import React, { useEffect, useRef, useState } from 'react';
import { createChart } from 'lightweight-charts';
import axios from 'axios';

const API = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;

const TradingChart = ({ symbol, interval = '1D', height = 400 }) => {
  const chartContainerRef = useRef();
  const chartRef = useRef(null);
  const candlestickSeriesRef = useRef(null);
  const volumeSeriesRef = useRef(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedInterval, setSelectedInterval] = useState(interval);

  const intervals = [
    { label: '1D', value: '1D' },
    { label: '1H', value: '1H' },
    { label: '15m', value: '15m' },
    { label: '5m', value: '5m' },
    { label: '1m', value: '1m' }
  ];

  // Initialize chart
  const initChart = () => {
    if (!chartContainerRef.current) return;

    const chart = createChart(chartContainerRef.current, {
      width: chartContainerRef.current.clientWidth,
      height: height,
      layout: {
        background: { type: 'solid', color: '#1a1a1a' },
        textColor: '#DDD',
      },
      grid: {
        vertLines: { color: '#444' },
        horzLines: { color: '#444' },
      },
      crosshair: {
        mode: 1,
      },
      rightPriceScale: {
        borderColor: '#555',
      },
      timeScale: {
        borderColor: '#555',
        timeVisible: true,
        secondsVisible: false,
      },
    });

    // Add candlestick series
    const candlestickSeries = chart.addCandlestickSeries({
      upColor: '#4ade80', // green-400
      downColor: '#f87171', // red-400
      borderVisible: false,
      wickUpColor: '#4ade80',
      wickDownColor: '#f87171',
    });

    // Add volume series
    const volumeSeries = chart.addHistogramSeries({
      color: '#26a69a',
      priceFormat: {
        type: 'volume',
      },
      priceScaleId: '',
      scaleMargins: {
        top: 0.8,
        bottom: 0,
      },
    });

    chartRef.current = chart;
    candlestickSeriesRef.current = candlestickSeries;
    volumeSeriesRef.current = volumeSeries;

    // Handle resize
    const handleResize = () => {
      if (chartContainerRef.current && chartRef.current) {
        chartRef.current.applyOptions({
          width: chartContainerRef.current.clientWidth,
        });
      }
    };

    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
      if (chartRef.current) {
        chartRef.current.remove();
      }
    };
  };

  // Load chart data
  const loadChartData = async (timeframe) => {
    if (!symbol) return;

    setLoading(true);
    setError(null);

    try {
      console.log(`Loading ${timeframe} chart data for ${symbol}`);
      
      const response = await axios.get(
        `${API}/stocks/${symbol.toUpperCase()}/historical`,
        {
          params: {
            interval: timeframe,
            bars_back: timeframe === '1m' ? 100 : timeframe === '5m' ? 200 : 300
          }
        }
      );

      if (response.data?.data && response.data.data.length > 0) {
        const chartData = response.data.data;
        const volumeData = chartData.map(bar => ({
          time: bar.time,
          value: bar.volume,
          color: bar.close >= bar.open ? '#4ade8066' : '#f8717166'
        }));

        // Set data to series
        if (candlestickSeriesRef.current && volumeSeriesRef.current) {
          candlestickSeriesRef.current.setData(chartData);
          volumeSeriesRef.current.setData(volumeData);
          
          // Fit content nicely
          chartRef.current.timeScale().fitContent();
        }

        console.log(`Loaded ${chartData.length} bars for ${symbol} (${timeframe})`);
      } else {
        setError('No chart data available');
      }
    } catch (err) {
      console.error('Error loading chart data:', err);
      setError(`Failed to load chart data: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  // Initialize chart on mount
  useEffect(() => {
    const cleanup = initChart();
    return cleanup;
  }, []);

  // Load data when symbol or interval changes
  useEffect(() => {
    if (chartRef.current && symbol) {
      loadChartData(selectedInterval);
    }
  }, [symbol, selectedInterval]);

  // Handle interval change
  const handleIntervalChange = (newInterval) => {
    setSelectedInterval(newInterval);
  };

  if (error) {
    return (
      <div className="bg-gray-800 rounded-lg p-6 text-center">
        <div className="text-red-400 mb-2">Chart Error</div>
        <div className="text-gray-400 text-sm">{error}</div>
        <button 
          onClick={() => loadChartData(selectedInterval)}
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
      <div className="flex justify-between items-center mb-4">
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

      {/* Chart Container */}
      <div 
        ref={chartContainerRef}
        className="w-full bg-gray-800 rounded"
        style={{ height: `${height}px` }}
      />
      
      {/* Chart Info */}
      <div className="mt-2 text-xs text-gray-400 text-center">
        {loading ? 'Loading chart data...' : `${symbol.toUpperCase()} • ${selectedInterval} • Candlestick + Volume`}
      </div>
    </div>
  );
};

export default TradingChart;