import React, { useMemo, useState } from "react";
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, ReferenceLine, CartesianGrid, Area } from "recharts";

// ---- UI PRIMITIVES (Tailwind) ----
const Card = ({ children, className = "" }) => (
  <div className={`rounded-2xl bg-[#0f1320] border border-[#3a3f66] shadow-[0_0_0_1px_rgba(74,85,163,0.35)] ${className}`}>{children}</div>
);
const CardHeader = ({ children, className = "" }) => <div className={`px-5 pt-4 ${className}`}>{children}</div>;
const CardContent = ({ children, className = "" }) => <div className={`px-5 pb-5 ${className}`}>{children}</div>;
const Pill = ({ children, active }) => (
  <div className={`px-3 py-1 rounded-lg text-xs border ${active ? "bg-emerald-600/20 border-emerald-500/40 text-emerald-300" : "bg-white/5 border-white/10 text-white/70"}`}>{children}</div>
);
const Button = ({ children, className = "", ...props }) => (
  <button className={`px-3 py-2 rounded-xl text-sm font-medium bg-[#10b7d6] hover:brightness-110 text-white transition ${className}`} {...props}>
    {children}
  </button>
);

// ---- HELPERS ----
function genRange(min, max, n) { const step = (max - min) / (n - 1); return Array.from({ length: n }, (_, i) => +(min + i * step).toFixed(2)); }
function formatUSD(n) { const sign = n < 0 ? "-" : ""; const v = Math.abs(n); return `${sign}$${v.toLocaleString(undefined, { maximumFractionDigits: 2 })}`; }
function splitPosNeg(data) { return data.map((d) => ({ x: d.x, pos: d.y > 0 ? d.y : null, neg: d.y < 0 ? d.y : null })); }

// ---- PAYOFF MODELS (simplificate pentru mock) ----
function payoffLongCall(S) {
  const K = Math.round(S); const premium = Math.max(1.5, +(S * 0.06).toFixed(2));
  const xs = genRange(Math.max(0, S * 0.2), S * 2.2, 140);
  const pts = xs.map((x) => ({ x, y: Math.max(0, x - K) - premium }));
  return { K, premium, cost: premium * 100, points: pts, profitAt: (t) => (Math.max(0, t - K) - premium) * 100 };
}
function payoffCoveredCall(S) {
  const K = Math.round(S * 1.35); const premium = Math.max(1.2, +(S * 0.04).toFixed(2));
  const xs = genRange(Math.max(0, S * 0.2), S * 2.2, 140);
  const pts = xs.map((x) => ({ x, y: (x - S) + Math.min(0, K - x) + premium }));
  const risk = S * 100 - premium * 100; return { K, premium, risk, points: pts, profitAt: (t) => ((t - S) + Math.min(0, K - t) + premium) * 100 };
}
function payoffCashSecuredPut(S) {
  const K = Math.round(S * 0.85); const premium = Math.max(1.25, +(S * 0.03).toFixed(2));
  const xs = genRange(Math.max(0, S * 0.2), S * 2.2, 140);
  const pts = xs.map((x) => ({ x, y: -(Math.max(0, K - x)) + premium }));
  const collateral = K * 100; return { K, premium, collateral, points: pts, profitAt: (t) => (-(Math.max(0, K - t)) + premium) * 100 };
}
function payoffShortPut(S) {
  const K = Math.round(S * 0.75); const premium = Math.max(0.9, +(S * 0.02).toFixed(2));
  const xs = genRange(Math.max(0, S * 0.2), S * 2.2, 140);
  const pts = xs.map((x) => ({ x, y: -(Math.max(0, K - x)) + premium }));
  const collateral = K * 100 * 0.5; return { K, premium, collateral, points: pts, profitAt: (t) => (-(Math.max(0, K - t)) + premium) * 100 };
}
function payoffBullCallSpread(S) {
  const K1 = Math.round(S), K2 = Math.round(S * 1.3); const c1 = Math.max(1.6, +(S * 0.06).toFixed(2)), c2 = Math.max(0.8, +(S * 0.025).toFixed(2));
  const premium = c1 - c2; const xs = genRange(Math.max(0, S * 0.2), S * 2.2, 140);
  const pts = xs.map((x) => ({ x, y: Math.min(Math.max(0, x - K1), K2 - K1) - premium }));
  const risk = premium * 100, maxProfit = (K2 - K1 - premium) * 100; return { K1, K2, premium, risk, maxProfit, points: pts, profitAt: (t) => (Math.min(Math.max(0, t - K1), K2 - K1) - premium) * 100 };
}
function payoffBullPutSpread(S) {
  const K1 = Math.round(S * 0.95), K2 = Math.round(S * 0.75); const p1 = Math.max(1.3, +(S * 0.03).toFixed(2)), p2 = Math.max(0.7, +(S * 0.015).toFixed(2));
  const credit = p1 - p2; const xs = genRange(Math.max(0, S * 0.2), S * 2.2, 140);
  const pts = xs.map((x) => ({ x, y: credit - Math.min(Math.max(0, K1 - x), K1 - K2) }));
  const risk = (K1 - K2 - credit) * 100; return { K1, K2, credit, risk, points: pts, profitAt: (t) => (credit - Math.min(Math.max(0, K1 - t), K1 - K2)) * 100 };
}

// compute breakeven approx where y crosses 0 first time
function breakevenX(points) { for (let i = 1; i < points.length; i++) { if (points[i-1].y <= 0 && points[i].y >= 0) return points[i].x; } return null; }

function StrategyCard({ title, subtitle, dataset, S, target }) {
  const profitAtTarget = dataset.profitAt(target);
  const risk = dataset.risk ?? dataset.cost ?? dataset.collateral ?? 0;
  const retOn = risk ? (profitAtTarget / risk) * 100 : 0;
  const chance = Math.max(27, Math.min(74, Math.round(50 + (target - S) / (S * 0.02))));
  const data = splitPosNeg(dataset.points);
  const idKey = title.toLowerCase().replace(/[^a-z0-9]/g, "");
  const be = breakevenX(dataset.points);

  return (
    <Card className="flex flex-col">
      <CardHeader>
        <div className="flex items-baseline justify-between">
          <div>
            <h3 className="text-white text-lg font-semibold">{title}</h3>
            <p className="text-white/60 text-xs mt-0.5">{subtitle}</p>
          </div>
          <div className="text-right">
            <div className="text-emerald-400 text-sm font-semibold">{Math.round(Math.max(-999, Math.min(999, retOn)))}% Return on risk</div>
            <div className="text-white/70 text-xs">{chance}% Chance</div>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div className="h-40 w-full">
          <ResponsiveContainer>
            <LineChart data={data} margin={{ left: 6, right: 6, top: 6, bottom: 6 }}>
              {/* Gradient fills unique per card */}
              <defs>
                <linearGradient id={`gradPos-${idKey}`} x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#22c55e" stopOpacity={0.55} />
                  <stop offset="100%" stopColor="#22c55e" stopOpacity={0} />
                </linearGradient>
                <linearGradient id={`gradNeg-${idKey}`} x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#ef4444" stopOpacity={0.55} />
                  <stop offset="100%" stopColor="#ef4444" stopOpacity={0} />
                </linearGradient>
              </defs>

              <CartesianGrid stroke="#ffffff14" strokeDasharray="4 4" />
              <XAxis dataKey="x" tickFormatter={(v) => `$${Math.round(v)}`} tick={{ fill: "#9ca3af", fontSize: 10 }} axisLine={{ stroke: "#ffffff22" }} tickLine={{ stroke: "#ffffff22" }} />
              <YAxis tickFormatter={(v) => (v >= 0 ? `$${Math.round(v)}` : `-$${Math.round(Math.abs(v))}`)} tick={{ fill: "#9ca3af", fontSize: 10 }} axisLine={{ stroke: "#ffffff22" }} tickLine={{ stroke: "#ffffff22" }} />
              <Tooltip formatter={(v) => formatUSD(v)} labelFormatter={(v) => `Price: $${v}`} contentStyle={{ background: "#0b0f1a", border: "1px solid #1f2937", color: "white" }} />
              <ReferenceLine y={0} stroke="#ffffffb3" strokeDasharray="6 6" strokeWidth={1.5} />
              <ReferenceLine x={S} stroke="#60a5fa" strokeDasharray="4 4" label={{ value: `Spot`, position: "insideTopRight", fill: "#60a5fa", fontSize: 10 }} />
              <ReferenceLine x={target} stroke="#f59e0b" strokeDasharray="4 4" label={{ value: `Target`, position: "insideTopRight", fill: "#fbbf24", fontSize: 10 }} />
              {be && <ReferenceLine x={be} stroke="#10b981" strokeDasharray="2 2" label={{ value: `BE`, position: "insideTopRight", fill: "#10b981", fontSize: 10 }} />}

              {/* Profit (verde) / Pierdere (roșu) ca trepte */}
              <Area type="stepAfter" dataKey="pos" stroke="#22c55e" fill={`url(#gradPos-${idKey})`} baseValue={0} connectNulls />
              <Area type="stepAfter" dataKey="neg" stroke="#ef4444" fill={`url(#gradNeg-${idKey})`} baseValue={0} connectNulls />
              <Line type="stepAfter" dataKey="pos" stroke="#22c55e" dot={false} strokeWidth={2} connectNulls />
              <Line type="stepAfter" dataKey="neg" stroke="#ef4444" dot={false} strokeWidth={2} connectNulls />
            </LineChart>
          </ResponsiveContainer>
        </div>
        <div className="flex items-center justify-between mt-3 text-sm">
          <div className="text-white/80">Profit at target: <span className={profitAtTarget >= 0 ? "text-emerald-400" : "text-rose-400"}>{formatUSD(profitAtTarget)}</span></div>
          <div className="text-white/60">Risk/Collat: <span className="text-white/80">{formatUSD(risk)}</span></div>
          <Button onClick={() => alert("Builder mock — de implementat")}>Open in Builder</Button>
        </div>
      </CardContent>
    </Card>
  );
}

export default function OptionsModule() {
  const [symbol, setSymbol] = useState("CRCL");
  const [spot, setSpot] = useState(149.53);
  const [target, setTarget] = useState(263.91);
  const [budget, setBudget] = useState(0);
  const [slider, setSlider] = useState(65);

  const longCall = useMemo(() => payoffLongCall(spot), [spot]);
  const covered = useMemo(() => payoffCoveredCall(spot), [spot]);
  const csp = useMemo(() => payoffCashSecuredPut(spot), [spot]);
  const shortPut = useMemo(() => payoffShortPut(spot), [spot]);
  const bullCall = useMemo(() => payoffBullCallSpread(spot), [spot]);
  const bullPut = useMemo(() => payoffBullPutSpread(spot), [spot]);

  return (
    <div className="min-h-screen w-full text-white bg-gradient-to-b from-[#0c1222] via-[#0c1220] to-[#0b0f19]">
      {/* TOP BAR */}
      <div className="mx-auto max-w-7xl px-4 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-cyan-400 to-emerald-400">FlowMind Options</div>
            <nav className="hidden md:flex gap-4 text-sm text-white/70">
              <span className="px-2 py-1 rounded-md bg-white/5">Build</span>
              <span className="px-2 py-1 hover:bg-white/5 rounded-md">Optimize</span>
              <span className="px-2 py-1 hover:bg-white/5 rounded-md">Flow</span>
            </nav>
          </div>
          <div className="text-xs text-white/60">Tutorials · Blog · My Account</div>
        </div>
      </div>

      {/* SYMBOL/NEWS/CONTROLS */}
      <div className="mx-auto max-w-7xl px-4">
        <Card className="bg-[#10172a]">
          <CardHeader>
            <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-3">
              <div className="flex items-center gap-3">
                <div className="text-sm text-white/70">Symbol:</div>
                <input value={symbol} onChange={(e) => setSymbol(e.target.value.toUpperCase())} className="bg-white/5 text-white px-3 py-2 rounded-lg w-24 outline-none" />
                <div className="text-xl font-semibold">${spot.toFixed(2)}</div>
                <div className="text-emerald-400 text-sm font-medium">+7.40% (+$10.30)</div>
                <span className="text-xs text-white/60">Real‑time</span>
              </div>
              <div className="text-xs bg-sky-900/50 border border-sky-700/40 px-3 py-2 rounded-lg text-sky-200 max-w-xl">
                <b>{symbol}</b> shares are trading higher. The company announced a public offering of 10 million shares at $130 per share. (mock banner)
              </div>
            </div>

            <div className="mt-4 grid grid-cols-3 sm:grid-cols-6 gap-2 text-center">
              {["Very Bearish","Bearish","Neutral","Directional","Bullish","Very Bullish"].map((s, i) => (
                <Pill key={s} active={i >= 4}>{s}</Pill>
              ))}
            </div>

            <div className="mt-4 grid grid-cols-1 md:grid-cols-3 gap-4 items-center">
              <div className="flex items-center gap-2 text-sm">
                <span className="text-white/60">Target Price:</span>
                <input type="number" step="0.01" value={target} onChange={(e) => setTarget(parseFloat(e.target.value) || 0)} className="w-28 bg-white/5 px-2 py-1 rounded-md" />
                <span className="text-white/60">(+{Math.round(((target - spot) / spot) * 100)}%)</span>
              </div>
              <div className="flex items-center gap-2 text-sm">
                <span className="text-white/60">Budget:</span>
                <input type="number" step="100" value={budget} onChange={(e) => setBudget(parseFloat(e.target.value) || 0)} className="w-28 bg-white/5 px-2 py-1 rounded-md" />
              </div>
              <div className="flex items-center gap-3 text-xs">
                <span className="text-white/60">Max Return</span>
                <input type="range" min={0} max={100} value={slider} onChange={(e) => setSlider(parseInt(e.target.value))} className="w-full" />
                <span className="text-white/60">Max Chance</span>
              </div>
            </div>

            {/* Months pills row (mock) */}
            <div className="mt-4 flex flex-wrap gap-2 text-xs">
              {["Sep","Oct","Nov","Dec","Jan '26","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec","Jan '27"].map((m, i) => (
                <div key={i} className={`px-2.5 py-1 rounded-lg border ${i===3?"bg-white/10 border-white/20":"bg-white/5 border-white/10"}`}>{m}</div>
              ))}
            </div>
          </CardHeader>
        </Card>
      </div>

      {/* STRATEGY GRID */}
      <div className="mx-auto max-w-7xl px-4 mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <StrategyCard title="Long Call" subtitle={`Buy ${Math.round(spot)}C`} dataset={longCall} S={spot} target={target} />
        <StrategyCard title="Covered Call" subtitle={`Own the underlying, Sell ${Math.round(spot*1.35)}C`} dataset={covered} S={spot} target={target} />
        <StrategyCard title="Cash‑Secured Put" subtitle={`Sell ${Math.round(spot*0.85)}P, cash to buy if assigned`} dataset={csp} S={spot} target={target} />
        <StrategyCard title="Short Put" subtitle={`Sell ${Math.round(spot*0.75)}P`} dataset={shortPut} S={spot} target={target} />
        <StrategyCard title="Bull Call Spread" subtitle={`Buy ${Math.round(spot)}C, sell ${Math.round(spot*1.3)}C`} dataset={bullCall} S={spot} target={target} />
        <StrategyCard title="Bull Put Spread" subtitle={`Sell ${Math.round(spot*0.95)}P, buy ${Math.round(spot*0.75)}P`} dataset={bullPut} S={spot} target={target} />
      </div>

      <div className="mx-auto max-w-7xl px-4 py-10 text-center text-xs text-white/50">*Mock educațional. Valorile sunt ilustrative, nu recomandări de tranzacționare.*</div>
    </div>
  );
}