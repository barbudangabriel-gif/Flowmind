import { useState, useEffect, useCallback, useRef } from 'react';
import useSWR from 'swr';

const TF_OPTS = [
  { v: "1m", label: "1min", seconds: 60 },
  { v: "5m", label: "5min", seconds: 300 },
  { v: "15m", label: "15min", seconds: 900 },
  { v: "1h", label: "1hour", seconds: 3600 },
  { v: "4h", label: "4hour", seconds: 14400 },
  { v: "D", label: "Daily", seconds: 86400 },
  { v: "W", label: "Weekly", seconds: 604800 },
];

// Default fetcher function
const defaultFetcher = async ({ symbol, timeframe, limit }) => {
  // Generate demo data
  const data = [];
  let price = 150 + Math.random() * 50;
  const now = Math.floor(Date.now() / 1000);
  const tf = TF_OPTS.find(t => t.v === timeframe) || TF_OPTS[5]; // Default to Daily
  
  for (let i = limit; i >= 0; i--) {
    const time = now - (i * tf.seconds);
    const change = (Math.random() - 0.5) * 4;
    const open = price;
    const close = price + change;
    const high = Math.max(open, close) + Math.random() * 2;
    const low = Math.min(open, close) - Math.random() * 2;
    const volume = Math.floor(Math.random() * 1000000) + 100000;
    
    data.push({
      time,
      open: parseFloat(open.toFixed(2)),
      high: parseFloat(high.toFixed(2)),
      low: parseFloat(low.toFixed(2)),
      close: parseFloat(close.toFixed(2)),
      volume
    });
    
    price = close;
  }
  
  return data;
};

export function useOHLCV({
  symbol = "AAPL",
  timeframe = "D",
  limit = 300,
  fetcher = defaultFetcher,
  wsUrl = null,
  polling = false,
  pollInterval = 30000
}) {
  const [lastUpdated, setLastUpdated] = useState(null);
  const wsRef = useRef(null);
  const [wsConnected, setWsConnected] = useState(false);

  // SWR key for caching
  const key = symbol && timeframe ? `ohlcv:${symbol}:${timeframe}:${limit}` : null;
  
  // Use SWR for data fetching with caching
  const { data, error, isLoading, mutate } = useSWR(
    key,
    () => fetcher({ symbol, timeframe, limit }),
    {
      revalidateOnFocus: false,
      revalidateOnReconnect: true,
      refreshInterval: polling ? pollInterval : 0,
      dedupingInterval: 5000, // 5 second deduplication
      onSuccess: () => setLastUpdated(Date.now()),
      onError: (err) => console.error('OHLCV fetch error:', err)
    }
  );

  // WebSocket connection management
  useEffect(() => {
    if (!wsUrl || !symbol || !timeframe) return;

    try {
      const url = typeof wsUrl === 'function' ? wsUrl({ symbol, timeframe }) : wsUrl;
      const ws = new WebSocket(url);
      wsRef.current = ws;

      ws.onopen = () => {
        console.log('📡 WebSocket connected:', url);
        setWsConnected(true);
      };

      ws.onmessage = (event) => {
        try {
          const newBar = JSON.parse(event.data);
          if (newBar && typeof newBar === 'object') {
            mutate((currentData) => {
              if (!currentData || !Array.isArray(currentData)) return currentData;
              
              // Update or append new bar
              const updatedData = [...currentData];
              const lastIndex = updatedData.length - 1;
              
              if (lastIndex >= 0 && updatedData[lastIndex].time === newBar.time) {
                // Update existing bar
                updatedData[lastIndex] = newBar;
              } else {
                // Append new bar
                updatedData.push(newBar);
                // Keep only the latest 'limit' bars
                if (updatedData.length > limit) {
                  updatedData.shift();
                }
              }
              
              return updatedData;
            }, false); // Don't revalidate
            
            setLastUpdated(Date.now());
          }
        } catch (err) {
          console.error('WebSocket message parse error:', err);
        }
      };

      ws.onclose = () => {
        console.log('📡 WebSocket disconnected');
        setWsConnected(false);
      };

      ws.onerror = (error) => {
        console.error('📡 WebSocket error:', error);
        setWsConnected(false);
      };

    } catch (err) {
      console.error('WebSocket setup error:', err);
    }

    return () => {
      if (wsRef.current) {
        wsRef.current.close();
        wsRef.current = null;
      }
      setWsConnected(false);
    };
  }, [wsUrl, symbol, timeframe, mutate, limit]);

  // Manual refresh function
  const refresh = useCallback(() => {
    console.log('🔄 Manual OHLCV refresh triggered');
    mutate();
  }, [mutate]);

  return {
    data: data || [],
    loading: isLoading,
    error: error?.message || null,
    refresh,
    lastUpdated,
    wsConnected,
    // Computed properties
    isEmpty: !data || data.length === 0,
    dataLength: data ? data.length : 0
  };
}

export { TF_OPTS };