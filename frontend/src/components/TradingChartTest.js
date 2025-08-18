import React, { useEffect, useRef, useState } from 'react';
import { createChart } from 'lightweight-charts';

const TradingChartTest = ({ symbol = 'META', interval = '1D', height = 500 }) => {
  const mainChartRef = useRef();
  const volumeChartRef = useRef();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [chartData, setChartData] = useState([]);

  useEffect(() => {
    if (!mainChartRef.current || !volumeChartRef.current) return;

    const initCharts = async () => {
      try {
        setLoading(true);
        setError(null);

        console.log('🚀 Initializing Lightweight Charts v5.0.8 TEST for', symbol);
        console.log('📊 createChart function type:', typeof createChart);

        if (typeof createChart !== 'function') {
          throw new Error('createChart is not available - lightweight-charts import failed');
        }

        // Use mock data for testing
        const currentPrice = symbol === 'META' ? 785.23 : symbol === 'AAPL' ? 229.20 : 100;
        console.log(`💰 Mock price for ${symbol}: $${currentPrice}`);

        // Generate realistic market data based on current price
        const generateRealisticData = (price) => {
          const data = [];
          const now = Date.now();
          const oneDay = 24 * 60 * 60 * 1000;
          
          for (let i = 60; i >= 0; i--) {
            const timestamp = Math.floor((now - (i * oneDay)) / 1000);
            
            // Create realistic price movement around current price
            const trend = Math.sin(i / 10) * 0.03; // Trend component
            const volatility = price * 0.015; // 1.5% daily volatility
            const noise = (Math.random() - 0.5) * volatility;
            
            const basePrice = price * (1 + trend + (noise * (i / 60)));
            const variation = basePrice * 0.012; // 1.2% intraday variation
            
            const open = basePrice + (Math.random() - 0.5) * variation;
            const close = i === 0 ? price : basePrice + (Math.random() - 0.5) * variation;
            const high = Math.max(open, close) + Math.random() * variation * 0.4;
            const low = Math.min(open, close) - Math.random() * variation * 0.4;
            
            // Realistic volume based on price movement
            const priceChange = Math.abs((close - open) / open);
            const baseVolume = 800000 + (priceChange * 3000000);
            const volume = Math.floor(baseVolume * (0.3 + Math.random() * 1.4));
            
            data.push({
              time: timestamp,
              open: parseFloat(open.toFixed(2)),
              high: parseFloat(high.toFixed(2)),
              low: parseFloat(low.toFixed(2)),
              close: parseFloat(close.toFixed(2)),
              volume: volume
            });
          }
          
          return data.sort((a, b) => a.time - b.time);
        };

        const data = generateRealisticData(currentPrice);
        setChartData(data);
        console.log(`📈 Generated ${data.length} realistic data points`);

        // Clear containers
        mainChartRef.current.innerHTML = '';
        volumeChartRef.current.innerHTML = '';

        console.log('🎨 Creating main price chart...');
        
        // Create main price chart with v5.0.8 configuration
        const mainChart = createChart(mainChartRef.current, {
          width: mainChartRef.current.clientWidth || 800,
          height: height * 0.7,
          layout: {
            background: { color: '#0a0a0a' },
            textColor: '#d1d5db',
          },
          grid: {
            vertLines: { color: '#1f1f1f' },
            horzLines: { color: '#1f1f1f' },
          },
          crosshair: {
            mode: 1, // CrosshairMode.Normal in v5
            vertLine: {
              color: '#6b7280',
              width: 1,
              style: 3, // Dashed
            },
            horzLine: {
              color: '#6b7280',
              width: 1,
              style: 3, // Dashed
            },
          },
          timeScale: {
            timeVisible: true,
            secondsVisible: false,
            borderColor: '#374151',
          },
          rightPriceScale: {
            borderColor: '#374151',
            textColor: '#d1d5db',
          },
        });

        console.log('✅ Main chart created successfully');

        // Add candlestick series
        const candlestickSeries = mainChart.addCandlestickSeries({
          upColor: '#00d4aa',
          downColor: '#ff6b6b',
          borderVisible: false,
          wickUpColor: '#00d4aa',
          wickDownColor: '#ff6b6b',
          priceFormat: {
            type: 'price',
            precision: 2,
            minMove: 0.01,
          },
        });

        candlestickSeries.setData(data);
        console.log('📊 Candlestick data set successfully');

        console.log('📊 Creating volume chart...');
        
        // Create volume chart
        const volumeChart = createChart(volumeChartRef.current, {
          width: volumeChartRef.current.clientWidth || 800,
          height: height * 0.3,
          layout: {
            background: { color: '#0a0a0a' },
            textColor: '#d1d5db',
          },
          grid: {
            vertLines: { color: '#1f1f1f' },
            horzLines: { color: '#1f1f1f' },
          },
          timeScale: {
            timeVisible: true,
            secondsVisible: false,
            borderColor: '#374151',
          },
          rightPriceScale: {
            borderColor: '#374151',
            textColor: '#d1d5db',
          },
        });

        console.log('✅ Volume chart created successfully');

        // Add volume histogram
        const volumeData = data.map(item => ({
          time: item.time,
          value: item.volume,
          color: item.close >= item.open ? '#00d4aa' : '#ff6b6b'
        }));

        const volumeSeries = volumeChart.addHistogramSeries({
          color: '#26a69a',
          priceFormat: {
            type: 'volume',
          },
        });

        volumeSeries.setData(volumeData);
        console.log('📊 Volume data set successfully');

        // Synchronize time scales for v5.0.8
        mainChart.timeScale().subscribeVisibleTimeRangeChange((timeRange) => {
          if (timeRange) {
            volumeChart.timeScale().setVisibleRange(timeRange);
          }
        });

        volumeChart.timeScale().subscribeVisibleTimeRangeChange((timeRange) => {
          if (timeRange) {
            mainChart.timeScale().setVisibleRange(timeRange);
          }
        });

        console.log('🔗 Charts synchronized successfully');
        console.log('🎉 LIGHTWEIGHT CHARTS v5.0.8 TEST SUCCESSFUL!');
        
        setLoading(false);

        // Handle resize
        const handleResize = () => {
          const width = mainChartRef.current?.clientWidth || 800;
          mainChart.applyOptions({ width });
          volumeChart.applyOptions({ width });
        };

        window.addEventListener('resize', handleResize);

        return () => {
          window.removeEventListener('resize', handleResize);
          try {
            mainChart.remove();
            volumeChart.remove();
            console.log('🧹 Charts cleanup completed');
          } catch (e) {
            console.warn('⚠️ Error during charts cleanup:', e);
          }
        };

      } catch (err) {
        console.error('💥 Chart initialization error:', err);
        setError(`Chart Error: ${err.message}`);
        setLoading(false);
      }
    };

    // Initialize with small delay to ensure DOM is ready
    const timer = setTimeout(initCharts, 100);
    return () => clearTimeout(timer);

  }, [symbol, height]);

  if (loading) {
    return (
      <div className="bg-gray-900 rounded-lg border border-green-500" style={{ height }}>
        <div className="flex items-center justify-center h-full">
          <div className="text-center">
            <div className="animate-spin w-10 h-10 border-4 border-green-500 border-t-transparent rounded-full mx-auto mb-4"></div>
            <div className="text-green-400 font-semibold text-lg">🧪 Testing Lightweight Charts v5.0.8</div>
            <div className="text-gray-400 text-sm mt-2">Mock data test for {symbol}</div>
            <div className="text-gray-500 text-xs mt-1">Static import • Mock data • Dual charts</div>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-gray-900 rounded-lg border-2 border-red-500" style={{ height }}>
        <div className="flex items-center justify-center h-full">
          <div className="text-center p-6">
            <div className="text-red-400 text-2xl font-bold mb-3">💥 Test Chart Error</div>
            <div className="text-gray-200 text-sm mb-4 max-w-md bg-gray-800 p-3 rounded-lg border border-gray-600">
              {error}
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-gray-900 rounded-lg overflow-hidden border border-green-500 shadow-2xl">
      {/* Test Header */}
      <div className="bg-green-800 p-4 border-b border-gray-700">
        <div className="text-center">
          <span className="text-white text-lg font-bold">🧪 LIGHTWEIGHT CHARTS v5.0.8 TEST - SUCCESS!</span>
          <div className="text-green-200 text-sm mt-1">
            Chart rendering verified • {symbol} • {chartData.length} data points
          </div>
        </div>
      </div>

      {/* Dual Charts Container */}
      <div className="relative">
        {/* Main Price Chart */}
        <div 
          ref={mainChartRef} 
          className="w-full border-b border-gray-600"
          style={{ height: height * 0.7 }}
        />
        
        {/* Volume Chart (Subgraph) */}
        <div 
          ref={volumeChartRef} 
          className="w-full"
          style={{ height: height * 0.3 }}
        />
      </div>

      {/* Test Footer */}
      <div className="bg-green-800 p-3 border-t border-gray-700">
        <div className="flex items-center justify-between text-xs">
          <div className="text-gray-200">
            ✅ <span className="text-white font-bold">Chart Integration: WORKING</span>
            <span className="text-gray-300 mx-1">•</span>
            <span className="text-green-200 font-medium">Mock data test</span>
            <span className="text-gray-300 mx-1">•</span>
            <span className="text-white font-medium">{chartData.length} bars</span>
          </div>
          <div className="text-gray-300">
            ⚡ <span className="text-green-200 font-bold">Lightweight Charts v5.0.8</span>
            <span className="text-gray-300 mx-1">•</span>
            <span className="text-gray-200">Test Mode</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TradingChartTest;