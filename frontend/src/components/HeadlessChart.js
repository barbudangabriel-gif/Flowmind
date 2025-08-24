import React, { useEffect, useRef, useImperativeHandle, forwardRef } from 'react';

let createChart, ColorType;

// Load lightweight-charts asynchronously
const loadLightweightCharts = async () => {
  try {
    const module = await import('lightweight-charts');
    createChart = module.createChart;
    ColorType = module.ColorType;
    return true;
  } catch (error) {
    console.error('Failed to load lightweight-charts:', error);
    return false;
  }
};

const HeadlessChart = forwardRef(({ 
  theme = "dark", 
  className = "", 
  onReady = null,
  width = 800,
  height = 640
}, ref) => {
  const containerRef = useRef(null);
  const chartRef = useRef(null);
  const seriesRef = useRef({});
  const chartLoadedRef = useRef(false);

  // Expose chart API through ref
  useImperativeHandle(ref, () => ({
    getChart: () => chartRef.current,
    getSeries: (type) => seriesRef.current[type],
    addCandlestickSeries: (options = {}) => {
      if (!chartRef.current) return null;
      const series = chartRef.current.addCandlestickSeries({
        upColor: '#16a34a',
        downColor: '#dc2626',
        borderDownColor: '#dc2626', 
        borderUpColor: '#16a34a',
        wickDownColor: '#dc2626',
        wickUpColor: '#16a34a',
        ...options
      });
      seriesRef.current.candlestick = series;
      return series;
    },
    addLineSeries: (options = {}) => {
      if (!chartRef.current) return null;
      const series = chartRef.current.addLineSeries({
        color: '#2196F3',
        lineWidth: 2,
        ...options
      });
      return series;
    },
    addHistogramSeries: (options = {}) => {
      if (!chartRef.current) return null;
      const series = chartRef.current.addHistogramSeries({
        color: '#26a69a',
        priceFormat: { type: 'volume' },
        priceScaleId: '',
        scaleMargins: { top: 0.7, bottom: 0 },
        ...options
      });
      seriesRef.current.volume = series;
      return series;
    },
    fitContent: () => {
      if (chartRef.current) {
        chartRef.current.timeScale().fitContent();
      }
    },
    remove: () => {
      if (chartRef.current) {
        chartRef.current.remove();
        chartRef.current = null;
        seriesRef.current = {};
      }
    }
  }), []);

  // Initialize chart
  useEffect(() => {
    if (!containerRef.current || chartLoadedRef.current) return;

    let mounted = true;

    const initChart = async () => {
      const success = await loadLightweightCharts();
      if (!success || !mounted || !createChart) return;

      try {
        // Clear container
        if (containerRef.current) {
          containerRef.current.innerHTML = '';
        }

        const chart = createChart(containerRef.current, {
          layout: {
            background: { 
              type: ColorType?.Solid || 0, 
              color: theme === 'dark' ? '#1a1a1a' : '#ffffff' 
            },
            textColor: theme === 'dark' ? '#e5e5e5' : '#333333',
          },
          grid: {
            vertLines: { color: theme === 'dark' ? '#2a2a2a' : '#e0e0e0' },
            horzLines: { color: theme === 'dark' ? '#2a2a2a' : '#e0e0e0' },
          },
          crosshair: { mode: 0 },
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
          width: containerRef.current.clientWidth || width,
          height: height,
        });

        chartRef.current = chart;
        chartLoadedRef.current = true;

        // Handle resize
        const ro = new ResizeObserver(() => {
          if (chart && containerRef.current) {
            chart.applyOptions({ 
              width: containerRef.current.clientWidth,
              height: height 
            });
          }
        });
        
        if (containerRef.current) {
          ro.observe(containerRef.current);
        }

        // Call onReady callback
        if (onReady && typeof onReady === 'function') {
          onReady({
            chart,
            addCandlestickSeries: (opts) => {
              const series = chart.addCandlestickSeries({
                upColor: '#16a34a',
                downColor: '#dc2626',
                borderDownColor: '#dc2626',
                borderUpColor: '#16a34a',
                wickDownColor: '#dc2626',
                wickUpColor: '#16a34a',
                ...opts
              });
              seriesRef.current.candlestick = series;
              return series;
            },
            addLineSeries: (opts) => {
              return chart.addLineSeries({
                color: '#2196F3',
                lineWidth: 2,
                ...opts
              });
            },
            addHistogramSeries: (opts) => {
              const series = chart.addHistogramSeries({
                color: '#26a69a',
                priceFormat: { type: 'volume' },
                priceScaleId: '',
                scaleMargins: { top: 0.7, bottom: 0 },
                ...opts
              });
              seriesRef.current.volume = series;
              return series;
            }
          });
        }

        // Cleanup function
        return () => {
          ro.disconnect();
          if (chart) {
            chart.remove();
          }
        };

      } catch (err) {
        console.error('Chart initialization error:', err);
      }
    };

    initChart();

    return () => {
      mounted = false;
    };
  }, []);

  // Update theme
  useEffect(() => {
    if (!chartRef.current) return;

    chartRef.current.applyOptions({
      layout: {
        background: { 
          type: ColorType?.Solid || 0, 
          color: theme === 'dark' ? '#1a1a1a' : '#ffffff' 
        },
        textColor: theme === 'dark' ? '#e5e5e5' : '#333333',
      },
      grid: {
        vertLines: { color: theme === 'dark' ? '#2a2a2a' : '#e0e0e0' },
        horzLines: { color: theme === 'dark' ? '#2a2a2a' : '#e0e0e0' },
      },
      timeScale: {
        borderColor: theme === 'dark' ? '#485158' : '#cccccc',
      },
      rightPriceScale: {
        borderColor: theme === 'dark' ? '#485158' : '#cccccc',
      },
    });
  }, [theme]);

  return (
    <div className={className}>
      <div 
        ref={containerRef} 
        className="w-full h-full" 
        style={{ minHeight: height }}
      />
    </div>
  );
});

HeadlessChart.displayName = 'HeadlessChart';

export default HeadlessChart;