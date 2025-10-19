import React, { useState } from "react";
import { priceStrategy } from "../lib/builderApi";

// FlowMind font family
const FONT = 'Inter, ui-sans-serif, system-ui, -apple-system, "Segoe UI", Roboto, Helvetica, Arial';

// Card component with FlowMind dark theme
function Card({ title, value }) {
  return (
    <div className="rounded-xl border border-[#232334] bg-[#18181c] p-3" style={{fontFamily: FONT}}>
      <div className="text-xs text-[#94a3b8]">{title}</div>
      <div className="text-base font-medium text-[rgb(252,251,255)]">{value}</div>
    </div>
  );
}

// Button with FlowMind dark theme
function Button({ children, ...props }) {
  return (
    <button {...props} className="h-9 px-3 rounded-lg border border-[#232334] bg-[#18181c] text-[rgb(252,251,255)] hover:bg-[#232334] disabled:opacity-60" style={{fontFamily: FONT}}>
      {children}
    </button>
  );
}

// Slider with FlowMind dark theme
function Slider({ label, value, min, max, onChange }) {
  return (
    <div className="flex items-center gap-3 py-2" style={{fontFamily: FONT}}>
      <div className="w-40 text-sm text-[#94a3b8]">{label}</div>
      <input type="range" min={min} max={max} value={value} onChange={e=>onChange(Number(e.target.value))} className="flex-1 accent-[#6366f1]" />
      <div className="w-16 text-right text-sm tabular-nums text-[#94a3b8]">{value}%</div>
    </div>
  );
}

export default function SimulatorPage() {
  const [symbol, setSymbol] = useState("AMZN");
  const [expiry, setExpiry] = useState("2028-01-21");
  const [legs, setLegs] = useState([
    { type: "CALL", side: "BUY", strike: 210 },
    { type: "CALL", side: "SELL", strike: 260 }
  ]);
  const [spot, setSpot] = useState(213.04);
  const [iv, setIv] = useState(35.4);
  const [rangePct, setRangePct] = useState(53);
  const [metrics, setMetrics] = useState({});
  const [greeks, setGreeks] = useState({});
  const [loading, setLoading] = useState(false);

  const fetchPricing = async () => {
    setLoading(true);
    try {
      const res = await priceStrategy({
        symbol, expiry, legs, spot, iv: iv / 100, rangePct: rangePct / 100
      });
      setMetrics(res.metrics);
      setGreeks(res.greeks);
    } catch (e) {
      setMetrics({});
      setGreeks({});
    }
    setLoading(false);
  };

  return (
    <div className="min-h-screen bg-[#18181c] text-[rgb(252,251,255)]" style={{fontFamily: FONT}}>
      {/* HeaderBar */}
      <div className="flex items-center justify-between p-4">
        <h2 className="text-xl font-bold text-[rgb(252,251,255)]" style={{fontFamily: FONT}}>Bull Call Spread</h2>
        <div>
          <span className="font-mono text-lg text-[#94a3b8]">{symbol}</span>
          <span className="ml-2 text-[#94a3b8]">${spot}</span>
        </div>
        <span className="px-2 py-1 rounded bg-[#232334] text-[#22d3ee] text-xs">Real-time</span>
      </div>

      {/* MetricsBar */}
      <div className="grid grid-cols-5 gap-2 p-4">
        <Card title="Net Debit" value={loading ? "…" : metrics.netDebit !== undefined ? `$${metrics.netDebit}` : "—"} />
        <Card title="Max Loss" value={loading ? "…" : metrics.maxLoss !== undefined ? `$${metrics.maxLoss}` : "—"} />
        <Card title="Max Profit" value={loading ? "…" : metrics.maxProfit !== undefined ? `$${metrics.maxProfit}` : "—"} />
        <Card title="Chance of Profit" value={loading ? "…" : metrics.prob !== undefined ? `${Math.round(metrics.prob * 100)}%` : "—"} />
        <Card title="Breakeven" value={loading ? "…" : metrics.breakeven !== undefined ? `$${metrics.breakeven}` : "—"} />
      </div>

      {/* ControlsPanel */}
      <div className="flex gap-4 p-4">
        <Slider label="Range" value={rangePct} min={0} max={100} onChange={setRangePct} />
        <Slider label="Implied Volatility" value={iv} min={0} max={100} onChange={setIv} />
      </div>

      {/* Action Button */}
      <div className="p-4">
        <Button onClick={fetchPricing} disabled={loading}>Simulate</Button>
      </div>
    </div>
  );
}