import React, { useEffect, useRef, useState } from 'react';
import { createChart } from 'lightweight-charts';
import axios from 'axios';

// Get backend URL from environment
const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const TradingChart = ({ symbol, interval = '1D', height = 400 }) => {
  const chartContainerRef = useRef();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [chartData, setChartData] = useState(null);
  const [selectedInterval, setSelectedInterval] = useState(interval);

  const intervals = [
    { label: '1D', value: '1D' },
    { label: '1H', value: '1H' },
    { label: '15m', value: '15m' },
    { label: '5m', value: '5m' }
  ];

  // Load chart data from API
  const loadChartData = async (timeframe) => {
    if (!symbol) {
      setError('No symbol provided');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      console.log(`Loading ${timeframe} chart data for ${symbol}`);
      
      const response = await axios.get(
        `${API}/stocks/${symbol.toUpperCase()}/historical`,
        {
          params: {
            interval: timeframe,
            bars_back: 50
          },
          timeout: 10000
        }
      );

      if (response.data?.data && response.data.data.length > 0) {
        setChartData(response.data);
        console.log(`Loaded ${response.data.data.length} bars for ${symbol}`);
      } else {
        setError('No chart data available');
      }
    } catch (err) {
      console.error('Error loading chart data:', err);
      setError(`Failed to load chart: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  // Initialize chart when data is available
  useEffect(() => {
    if (!chartData || !chartContainerRef.current) return;

    try {
      // Create chart
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
        rightPriceScale: {
          borderColor: '#555',
        },
        timeScale: {
          borderColor: '#555',
        },
      });

      // Add candlestick series
      const candlestickSeries = chart.addCandlestickSeries({
        upColor: '#4ade80',
        downColor: '#f87171',
        borderVisible: false,
        wickUpColor: '#4ade80',
        wickDownColor: '#f87171',
      });

      // Set data
      candlestickSeries.setData(chartData.data);

      // Fit content
      chart.timeScale().fitContent();

      // Handle resize
      const handleResize = () => {
        chart.applyOptions({
          width: chartContainerRef.current?.clientWidth || 800,
        });
      };

      window.addEventListener('resize', handleResize);

      // Cleanup
      return () => {
        window.removeEventListener('resize', handleResize);
        chart.remove();
      };
    } catch (chartError) {
      console.error('Chart creation error:', chartError);
      setError(`Chart error: ${chartError.message}`);
    }
  }, [chartData, height]);

  // Load data when symbol or interval changes
  useEffect(() => {
    loadChartData(selectedInterval);
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