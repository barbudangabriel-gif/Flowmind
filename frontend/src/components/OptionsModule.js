import React, { useMemo, useState } from "react";
import { ComposedChart, Line, Area, XAxis, YAxis, Tooltip, ResponsiveContainer, ReferenceLine, CartesianGrid, Legend } from "recharts";

/**
 * Option-like payoff calculators (simplified). All values per 1 share for clarity.
 */

function range(start, end, step = 5) {
  const out = [];
  for (let x = start; x <= end; x += step) out.push(x);
  return out;
}

function clamp(n, a, b) { return Math.max(a, Math.min(b, n)); }

// --- Payoff functions
const payoffs = {
  longCall: ({ S, K, premium }) => Math.max(0, S - K) - premium,
  shortPut: ({ S, K, premium }) => premium - Math.max(0, K - S),
  coveredCall: ({ S, S0, K, premium }) => (S - S0) - Math.max(0, S - K) + premium,
  bullCallSpread: ({ S, K1, K2, premium1, premium2 }) => Math.max(0, S - K1) - premium1 - (Math.max(0, S - K2) - premium2),
  bullPutSpread: ({ S, K1, K2, premium1, premium2 }) => (premium2 - premium1) - Math.max(0, K2 - S) + Math.max(0, K1 - S),
};

/**
 * Generate chart data with positive/negative split for area gradients
 */
function buildChartData({ xMin = 0, xMax = 400, step = 5, fn }) {
  const xs = range(xMin, xMax, step);
  let minY = Infinity, maxY = -Infinity;
  const raw = xs.map((x) => {
    const y = fn(x);
    if (y < minY) minY = y;
    if (y > maxY) maxY = y;
    return { x, y };
  });
  // Split into positive/negative for gradient fill
  return raw.map((d) => ({
    ...d,
    pos: d.y > 0 ? d.y : 0,
    neg: d.y < 0 ? d.y : 0,
  }));
}

function pretty(n, digits = 2) {
  const sign = n < 0 ? "-" : "";
  const v = Math.abs(n);
  return sign + "$" + v.toLocaleString(undefined, { maximumFractionDigits: digits, minimumFractionDigits: digits });
}

// --- Reusable payoff mini chart
function PnLChart({ data, xMarker, idSuffix }) {
  return (
    <div className="h-52 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <ComposedChart data={data} margin={{ top: 10, right: 10, bottom: 0, left: 0 }}>
          <defs>
            <linearGradient id={`greenGrad-${idSuffix}`} x1="0" x2="0" y1="0" y2="1">
              <stop offset="0%" stopColor="#2ecc71" stopOpacity={0.7} />
              <stop offset="100%" stopColor="#2ecc71" stopOpacity={0.15} />
            </linearGradient>
            <linearGradient id={`redGrad-${idSuffix}`} x1="0" x2="0" y1="0" y2="1">
              <stop offset="0%" stopColor="#ff4d4f" stopOpacity={0.7} />
              <stop offset="100%" stopColor="#ff4d4f" stopOpacity={0.15} />
            </linearGradient>
          </defs>
          <CartesianGrid stroke="#263143" vertical={false} />
          <XAxis dataKey="x" stroke="#8a97ad" tick={{ fontSize: 11 }} />
          <YAxis stroke="#8a97ad" tick={{ fontSize: 11 }} />
          <ReferenceLine y={0} stroke="#8a97ad" strokeDasharray="4 4" />
          {typeof xMarker === "number" && (
            <ReferenceLine x={xMarker} stroke="#8a97ad" strokeDasharray="4 4" />
          )}
          {/* Fill positive/negative areas */}
          <Area type="monotone" dataKey="pos" stroke="none" fill={`url(#greenGrad-${idSuffix})`} />
          <Area type="monotone" dataKey="neg" stroke="none" fill={`url(#redGrad-${idSuffix})`} />
          {/* PnL line */}
          <Line type="monotone" dataKey="y" stroke="#89a3ff" dot={false} strokeWidth={2} />
          <Tooltip
            formatter={(value, name) => {
              if (name === "x") return value;
              return [pretty(value), "PnL"];
            }}
            labelFormatter={(label) => `Preț la expirare: $${label}`}
            contentStyle={{ background: "#0f1626", border: "1px solid #263143", borderRadius: 12 }}
            itemStyle={{ color: "#d1d7e0" }}
          />
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  );
}

function Metric({ label, value, accent = "#d1d7e0" }) {
  return (
    <div className="flex items-center gap-2 text-[13px]">
      <span className="text-[#8a97ad]">{label}</span>
      <span className="font-semibold" style={{ color: accent }}>{value}</span>
    </div>
  );
}

function StrategyCard({ title, subtitleLeft, subtitleRight, children }) {
  return (
    <div className="rounded-2xl bg-[#0f1626] border border-[#263143] p-4 flex flex-col gap-3 shadow-xl">
      <div>
        <div className="text-[15px] font-semibold text-white">{title}</div>
        <div className="mt-1 flex items-center justify-between">
          <Metric label="Return on risk" value={subtitleLeft} accent="#ffde69" />
          <Metric label="Chance" value={subtitleRight} accent="#9be28c" />
        </div>
      </div>
      {children}
      <button className="mt-auto self-start px-3 py-1.5 text-sm rounded-xl bg-[#1b2033] border border-[#2a3550] hover:bg-[#222a44] transition">Open in Builder</button>
    </div>
  );
}

export default function OptionsModule() {
  const [symbol, setSymbol] = useState("CRCL");
  const [spot, setSpot] = useState(149.53);
  const [target, setTarget] = useState(263.91);

  // Example parameter set inspired by screenshot
  const params = useMemo(() => ({
    longCall: { K: 95, premium: 60 },
    coveredCall: { S0: spot, K: 200, premium: 12.85 },
    cashSecPut: { K: 125, premium: 26.15 },
    shortPut: { K: 115, premium: 24.05 },
    bullCallSpread: { K1: 95, K2: 265, premium1: 60, premium2: 5 },
    bullPutSpread: { K1: 90, K2: 185, premium1: 8.5, premium2: 26.15 },
  }), [spot]);

  // Chart data builders
  const dataLongCall = useMemo(() => buildChartData({ fn: (S) => payoffs.longCall({ S, ...params.longCall }) }), [params]);
  const dataCoveredCall = useMemo(() => buildChartData({ fn: (S) => payoffs.coveredCall({ S, ...params.coveredCall }) }), [params]);
  const dataCashPut = useMemo(() => buildChartData({ fn: (S) => payoffs.shortPut({ S, ...params.cashSecPut }) }), [params]);
  const dataShortPut = useMemo(() => buildChartData({ fn: (S) => payoffs.shortPut({ S, ...params.shortPut }) }), [params]);
  const dataBullCall = useMemo(() => buildChartData({ fn: (S) => payoffs.bullCallSpread({ S, ...params.bullCallSpread }) }), [params]);
  const dataBullPut = useMemo(() => buildChartData({ fn: (S) => payoffs.bullPutSpread({ S, ...params.bullPutSpread }) }), [params]);

  const headerChip = (label, active=false) => (
    <button className={`px-3 py-1 rounded-xl border text-sm ${active?"bg-[#213352] border-[#2f4772] text-white":"bg-[#0f1626] border-[#263143] text-[#c4ccda]"}`}>{label}</button>
  );

  return (
    <div className="min-h-screen w-full text-[#d1d7e0] bg-[#0b0f1a]">
      {/* Top bar */}
      <div className="flex items-center justify-between px-5 py-3 border-b border-[#1c2438] bg-[#0e1422] sticky top-0 z-10">
        <div className="flex items-center gap-2 font-semibold text-white">
          <div className="w-2.5 h-2.5 rounded-full bg-[#5aa9ff]" />
          <span>FlowMind Options</span>
        </div>
        <div className="flex items-center gap-2 text-sm">
          <span className="opacity-70">Symbol:</span>
          <input value={symbol} onChange={(e)=>setSymbol(e.target.value.toUpperCase())} className="w-16 bg-transparent border border-[#263143] rounded-lg px-2 py-1"/>
          <span className="border border-[#263143] rounded-lg px-2 py-1">${spot.toFixed(2)} <span className="text-[#64d98a] ml-1">+7.40%</span></span>
          <span className="text-[11px] px-2 py-0.5 rounded bg-[#142033] border border-[#223153] ml-1">Real‑time</span>
        </div>
        <div />
      </div>

      {/* Banner */}
      <div className="px-5 pt-4">
        <div className="rounded-xl bg-[#0f1b2d] border border-[#243250] p-3 text-sm">
          <span className="inline-flex items-center gap-2">
            <span className="w-6 h-6 rounded-full bg-[#1b2a46] flex items-center justify-center">ℹ️</span>
            {symbol} shares are trading higher. The company announced a public offering of 10 million shares at $130 per share. <span className="opacity-60">(updated 8/15/25, 8:06 PM)</span>
          </span>
        </div>
      </div>

      {/* Sentiment buttons */}
      <div className="px-5 mt-4 flex items-center gap-2 overflow-x-auto">
        {headerChip("Very Bearish")}
        {headerChip("Bearish")}
        {headerChip("Neutral", true)}
        {headerChip("Directional")}
        {headerChip("Bullish")}
        {headerChip("Very Bullish")}
      </div>

      {/* Target + Budget */}
      <div className="px-5 mt-4 grid grid-cols-1 md:grid-cols-2 gap-4 items-center">
        <div className="rounded-xl bg-[#0f1626] border border-[#263143] p-4">
          <div className="text-sm opacity-70">Target Price</div>
          <div className="mt-1 text-2xl font-semibold">${target.toFixed(2)} <span className="text-[#64d98a] text-base align-middle">({(((target/spot)-1)*100).toFixed(0)}%)</span></div>
          <input type="range" min={0} max={400} step={1} value={target} onChange={(e)=>setTarget(Number(e.target.value))} className="w-full mt-3"/>
        </div>
        <div className="rounded-xl bg-[#0f1626] border border-[#263143] p-4 flex items-center gap-2">
          <div className="text-sm opacity-70">Budget</div>
          <input type="number" placeholder="$" className="ml-3 flex-1 bg-transparent border border-[#263143] rounded-lg px-3 py-2"/>
        </div>
      </div>

      {/* Months row */}
      <div className="px-5 mt-3">
        <div className="flex flex-wrap gap-2 items-center text-sm">
          {['Sep','Oct','Nov','Dec','Jan '26','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec','Jan '27'].map((m,i)=> (
            <button key={i} className={`px-3 py-1 rounded-xl border ${i===3?"bg-[#213352] border-[#2f4772] text-white":"bg-[#0f1626] border-[#263143] text-[#c4ccda]"}`}>{m}</button>
          ))}
        </div>
        <div className="mt-3">
          <input type="range" min={12} max={31} defaultValue={18} className="w-full"/>
          <div className="flex justify-between text-xs text-[#8a97ad] mt-1">
            <span>← Max Return</span>
            <span>Max Chance →</span>
          </div>
        </div>
      </div>

      {/* Strategy grid */}
      <div className="px-5 py-6 grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-5">
        <StrategyCard title="Long Call" subtitleLeft="162%" subtitleRight="47%">
          <PnLChart idSuffix="lc" data={dataLongCall} xMarker={target} />
        </StrategyCard>

        <StrategyCard title="Covered Call" subtitleLeft="63%" subtitleRight="58%">
          <PnLChart idSuffix="cc" data={dataCoveredCall} xMarker={target} />
        </StrategyCard>

        <StrategyCard title="Cash‑Secured Put" subtitleLeft="27%" subtitleRight="74%">
          <PnLChart idSuffix="csp" data={dataCashPut} xMarker={target} />
        </StrategyCard>

        <StrategyCard title="Short Put" subtitleLeft="209%" subtitleRight="74%">
          <PnLChart idSuffix="sp" data={dataShortPut} xMarker={target} />
        </StrategyCard>

        <StrategyCard title="Bull Call Spread" subtitleLeft="236%" subtitleRight="52%"> 
          <PnLChart idSuffix="bcs" data={dataBullCall} xMarker={target} />
        </StrategyCard>

        <StrategyCard title="Bull Put Spread" subtitleLeft="124%" subtitleRight="58%">
          <PnLChart idSuffix="bps" data={dataBullPut} xMarker={target} />
        </StrategyCard>
      </div>

      <div className="px-5 pb-10 text-xs text-[#8a97ad]">
        * Mockup educațional. Nu reprezintă recomandări financiare. Formulele sunt simplificate; valorile sunt per acțiune.
      </div>
    </div>
  );
}