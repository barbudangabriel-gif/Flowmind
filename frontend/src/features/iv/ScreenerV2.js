import React, { useEffect, useMemo, useState } from "react";

// Utils (o singură dată, fără duplicări)
const fmtPct = (x) => (x == null || Number.isNaN(x) ? "-" : (x * 100).toFixed(2) + "%");
const fmtUsd = (x) => (x == null || Number.isNaN(x) ? "-" : x.toFixed(2));
const TS_SEND_URL = (typeof window !== 'undefined' && window.TS_SEND_URL) || "/api/ts/sim/order";

export default function ScreenerV2() {
  const [rule, setRule] = useState("calendar");
  const [mult, setMult] = useState(0.5);
  const [limit, setLimit] = useState(50);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [rows, setRows] = useState([]);
  const [meta, setMeta] = useState({});

  // Filters
  const [q, setQ] = useState("");
  const [emMin, setEmMin] = useState("");
  const [emMax, setEmMax] = useState("");
  const [dteMin, setDteMin] = useState("");
  const [dteMax, setDteMax] = useState("");
  const [hideErrors, setHideErrors] = useState(true);

  // Modal
  const [payloadJson, setPayloadJson] = useState("");
  const [showPayload, setShowPayload] = useState(false);
  const [sendMsg, setSendMsg] = useState("");

  useEffect(() => {
    if (rule === "condor" && mult === 0.5) setMult(1.0);
    if (rule === "calendar" && mult === 1.0) setMult(0.5);
  }, [rule, mult]);

  const fetchBatch = async () => {
    setLoading(true);
    setError(null);
    try {
      const qs = new URLSearchParams({ watchlist: "WL_MAIN", limit: String(limit), rule, mult: String(mult) });
      const res = await fetch(`/api/iv/batch?${qs.toString()}`);
      if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
      const data = await res.json();
      setRows(Array.isArray(data.rows) ? data.rows : []);
      setMeta(data.meta || {});
    } catch (e) {
      setError(e?.message || "fetch error");
      setRows([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchBatch();
  }, [rule, mult, limit]);

  const filtered = useMemo(() => {
    let arr = [...rows];
    if (q) arr = arr.filter(r => r.symbol?.toLowerCase?.().includes(q.toLowerCase()));
    const emn = emMin ? Number(emMin) / 100 : -Infinity;
    const emx = emMax ? Number(emMax) / 100 : Infinity;
    arr = arr.filter(r => (r.em_pct ?? 0) >= emn && (r.em_pct ?? 0) <= emx);
    const dmn = dteMin ? Number(dteMin) : -Infinity;
    const dmx = dteMax ? Number(dteMax) : Infinity;
    arr = arr.filter(r => r.front_dte >= dmn && r.front_dte <= dmx);
    if (hideErrors) arr = arr.filter(r => !r.error);
    return arr.sort((a, b) => a.symbol.localeCompare(b.symbol));
  }, [rows, q, emMin, emMax, dteMin, dteMax, hideErrors]);

  const onBuild = async (r) => {
    try {
      let payload;
      if (rule === "condor") {
        payload = {
          AccountID: "SIM123",
          Strategy: { Name: "IronCondor" },
          Orders: [
            { Symbol: `${r.symbol}_CALL_${r.ic_shorts[1]}`, Quantity: "-1", OrderType: "Market" },
            { Symbol: `${r.symbol}_CALL_${r.ic_wings[1]}`, Quantity: "1", OrderType: "Market" },
            { Symbol: `${r.symbol}_PUT_${r.ic_shorts[0]}`, Quantity: "-1", OrderType: "Market" },
            { Symbol: `${r.symbol}_PUT_${r.ic_wings[0]}`, Quantity: "1", OrderType: "Market" }
          ]
        };
      } else {
        payload = {
          AccountID: "SIM123",
          Strategy: { Name: "DoubleCalendar" },
          Orders: [
            { Symbol: `${r.symbol}_PUT_${r.dc_low}_FRONT`, Quantity: "-1", OrderType: "Market" },
            { Symbol: `${r.symbol}_PUT_${r.dc_low}_BACK`, Quantity: "1", OrderType: "Market" },
            { Symbol: `${r.symbol}_CALL_${r.dc_high}_FRONT`, Quantity: "-1", OrderType: "Market" },
            { Symbol: `${r.symbol}_CALL_${r.dc_high}_BACK`, Quantity: "1", OrderType: "Market" }
          ]
        };
      }
      setPayloadJson(JSON.stringify(payload, null, 2));
      setShowPayload(true);
      setSendMsg("");
    } catch (e) {
      setPayloadJson(JSON.stringify({ error: e?.message || String(e) }, null, 2));
      setShowPayload(true);
    }
  };

  const sendToTS = async () => {
    setSendMsg("");
    try {
      const res = await fetch(TS_SEND_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: payloadJson,
      });
      if (!res.ok) throw new Error(String(res.status));
      setSendMsg(`OK ${res.status}`);
    } catch (e) {
      setSendMsg(`Error: ${e?.message || String(e)}`);
    }
  };

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-2xl font-bold">IV Screener V2</h1>

      {/* Controls */}
      <div className="flex flex-wrap items-end gap-3 p-4 bg-gray-50 dark:bg-gray-800 rounded">
        <div className="flex flex-col">
          <label className="text-sm">Rule</label>
          <select className="border rounded px-2 py-1" value={rule} onChange={e => setRule(e.target.value)}>
            <option value="calendar">calendar</option>
            <option value="condor">condor</option>
          </select>
        </div>
        <div className="flex flex-col">
          <label className="text-sm">Mult</label>
          <input className="border rounded px-2 py-1 w-24" type="number" step="0.1" value={mult} onChange={e => setMult(parseFloat(e.target.value) || 0.5)} />
        </div>
        <div className="flex flex-col">
          <label className="text-sm">Limit</label>
          <input className="border rounded px-2 py-1 w-24" type="number" value={limit} onChange={e => setLimit(parseInt(e.target.value) || 50)} />
        </div>
        <div className="flex flex-col">
          <label className="text-sm">Search</label>
          <input className="border rounded px-2 py-1 w-40" value={q} onChange={e => setQ(e.target.value)} placeholder="symbol" />
        </div>
        <div className="flex flex-col">
          <label className="text-sm">EM% Min</label>
          <input className="border rounded px-2 py-1 w-24" type="number" value={emMin} onChange={e => setEmMin(e.target.value)} />
        </div>
        <div className="flex flex-col">
          <label className="text-sm">EM% Max</label>
          <input className="border rounded px-2 py-1 w-24" type="number" value={emMax} onChange={e => setEmMax(e.target.value)} />
        </div>
        <div className="flex flex-col">
          <label className="text-sm">Front DTE Min</label>
          <input className="border rounded px-2 py-1 w-24" type="number" value={dteMin} onChange={e => setDteMin(e.target.value)} />
        </div>
        <div className="flex flex-col">
          <label className="text-sm">Front DTE Max</label>
          <input className="border rounded px-2 py-1 w-24" type="number" value={dteMax} onChange={e => setDteMax(e.target.value)} />
        </div>
        <label className="inline-flex items-center gap-2">
          <input type="checkbox" checked={hideErrors} onChange={e => setHideErrors(e.target.checked)} />
          <span className="text-sm">Hide Errors</span>
        </label>
        <button onClick={fetchBatch} disabled={loading} className="px-4 py-2 rounded bg-blue-600 text-white disabled:opacity-50">
          {loading ? "Loading..." : "Refresh"}
        </button>
      </div>

      {/* Stats */}
      <div className="text-sm text-gray-600">
        Showing {filtered.length} of {rows.length} rows
        {meta?.warning && <span className="text-amber-600 ml-2">{meta.warning}</span>}
        {error && <span className="text-red-600 ml-2">{error}</span>}
      </div>

      {/* Table */}
      <div className="overflow-auto border rounded">
        <table className="min-w-full text-sm">
          <thead className="bg-gray-50">
            <tr>
              <th className="text-left p-2">Symbol</th>
              <th className="text-right p-2">Spot</th>
              <th className="text-right p-2">EM%</th>
              <th className="text-right p-2">EM$</th>
              <th className="text-right p-2">Front DTE</th>
              <th className="text-right p-2">Back DTE</th>
              <th className="text-right p-2">DC Low</th>
              <th className="text-right p-2">DC High</th>
              {rule === "condor" && (
                <>
                  <th className="text-right p-2">IC Shorts</th>
                  <th className="text-right p-2">IC Wings</th>
                </>
              )}
              <th className="text-left p-2">Actions</th>
            </tr>
          </thead>
          <tbody>
            {filtered.map((r) => (
              <tr key={r.symbol} className="border-t">
                <td className="p-2 font-medium">{r.symbol}</td>
                <td className="p-2 text-right">{fmtUsd(r.spot)}</td>
                <td className="p-2 text-right">{fmtPct(r.em_pct)}</td>
                <td className="p-2 text-right">{fmtUsd(r.em_usd)}</td>
                <td className="p-2 text-right">{r.front_dte}</td>
                <td className="p-2 text-right">{r.back_dte}</td>
                <td className="p-2 text-right">{r.dc_low}</td>
                <td className="p-2 text-right">{r.dc_high}</td>
                {rule === "condor" && (
                  <>
                    <td className="p-2 text-right">{r.ic_shorts ? `${r.ic_shorts[0]}, ${r.ic_shorts[1]}` : "-"}</td>
                    <td className="p-2 text-right">{r.ic_wings ? `${r.ic_wings[0]}, ${r.ic_wings[1]}` : "-"}</td>
                  </>
                )}
                <td className="p-2">
                  <button onClick={() => onBuild(r)} className="px-3 py-1 rounded border hover:bg-gray-50">
                    {rule === "condor" ? "Build Condor" : "Build Calendar"}
                  </button>
                </td>
              </tr>
            ))}
            {filtered.length === 0 && !loading && (
              <tr>
                <td className="p-4 text-gray-500" colSpan={rule === "condor" ? 11 : 9}>No data</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {/* Modal payload */}
      {showPayload && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl shadow-xl w-full max-w-2xl p-4 space-y-3">
            <div className="flex items-center justify-between">
              <h3 className="font-semibold">Order Payload</h3>
              <button onClick={() => setShowPayload(false)} className="px-2 py-1">✕</button>
            </div>
            <pre className="bg-gray-100 rounded p-3 max-h-[60vh] overflow-auto text-xs">{payloadJson}</pre>
            <div className="flex items-center justify-between gap-2">
              <div className="text-xs text-gray-500">TS endpoint: {TS_SEND_URL}</div>
              <div className="flex gap-2">
                <button onClick={() => navigator.clipboard?.writeText(payloadJson)} className="px-3 py-1 rounded border">Copy</button>
                <button onClick={sendToTS} className="px-3 py-1 rounded bg-black text-white">Send to TS (SIM)</button>
                <button onClick={() => setShowPayload(false)} className="px-3 py-1 rounded">Close</button>
              </div>
            </div>
            {sendMsg && (
              <div className={`text-sm ${sendMsg.startsWith('OK') ? 'text-green-700' : 'text-red-600'}`}>{sendMsg}</div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}