import { useState, useEffect } from "react";

export function useTSStream({ symbol = "AAPL", tf = "1", barsBack = 1000 }) {
  const [bars, setBars] = useState([]);
  const [status, setStatus] = useState("disconnected");

  useEffect(() => {
    if (!symbol || !tf) return;

    console.log(`📡 Starting TS stream: ${symbol} ${tf}`);
    setStatus("connecting");
    setBars([]);

    // Create EventSource for SSE
    const url = new URL("/api/ohlcv/stream", window.location.origin);
    url.searchParams.set("symbol", symbol);
    url.searchParams.set("tf", tf);
    url.searchParams.set("barsBack", String(barsBack));

    const es = new EventSource(url.toString());

    es.addEventListener("open", () => {
      console.log(`📡 TS stream connected: ${symbol} ${tf}`);
      setStatus("connected");
    });

    es.addEventListener("status", (ev) => {
      try {
        const statusData = JSON.parse(ev.data);
        console.log(`📡 TS stream status:`, statusData);
        
        if (statusData.streamStatus === "EndSnapshot") {
          setStatus("live");
        } else if (statusData.streamStatus === "GoAway") {
          setStatus("reconnecting");
        }
      } catch (error) {
        console.warn('Status parse error:', error);
      }
    });

    es.addEventListener("bar", (ev) => {
      try {
        const bar = JSON.parse(ev.data);
        
        setBars((prev) => {
          const last = prev[prev.length - 1];
          
          // If same timestamp, replace last bar (live update)
          if (last && last.time === bar.time) {
            const copy = [...prev];
            copy[copy.length - 1] = bar;
            return copy;
          }
          
          // Otherwise append new bar
          const newBars = [...prev, bar];
          
          // Keep only last 'barsBack' bars for memory efficiency
          if (newBars.length > barsBack * 1.2) {
            return newBars.slice(-barsBack);
          }
          
          return newBars;
        });

        // Update status if this is end of historical data
        if (bar.isEndOfHistory) {
          setStatus("live");
        }
      } catch (parseError) {
        console.warn('Bar parse error:', parseError);
      }
    });

    es.addEventListener("error", (ev) => {
      console.error(`📡 TS stream error:`, ev);
      setStatus("error");
    });

    // Cleanup function
    return () => {
      console.log(`📡 Closing TS stream: ${symbol} ${tf}`);
      es.close();
      setStatus("disconnected");
    };
  }, [symbol, tf, barsBack]);

  return { 
    bars, 
    status,
    isConnected: status === "connected" || status === "live",
    isLive: status === "live",
    hasError: status === "error"
  };
}