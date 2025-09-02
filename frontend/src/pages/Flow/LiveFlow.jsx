import React, { useCallback, useEffect, useLayoutEffect, useRef, useState } from 'react';
import { useSearchParams } from 'react-router-dom';

async function fetchJSON(url, {timeoutMs=3200, signal} = {}) {
  const t = new Promise((_, rej) => setTimeout(() => rej(new Error('timeout')), timeoutMs));
  const r = await Promise.race([fetch(url, {signal}), t]);
  if (!r.ok) throw new Error(`HTTP ${r.status}`);
  return r.json();
}

export default function LiveFlow() {
  const [params] = useSearchParams();
  const symbol = params.get('symbol') || '';
  const [rows, setRows] = useState([]);
  const [mode, setMode] = useState('UNKNOWN');
  const [loading, setLoading] = useState(true);
  const [pageReady, setPageReady] = useState(false);
  const [error, setError] = useState(null);

  const readyRef = useRef(false);
  const rafRef = useRef(undefined);
  const timeoutRef = useRef(undefined);
  
  const ensureReady = useCallback(() => {
    if (!readyRef.current) {
      readyRef.current = true;
      setPageReady(true);
      setLoading(false);
    } else {
      setLoading(false);
    }
  }, []);

  // Hard gate (RAF + backstop 1.8s)
  useLayoutEffect(() => {
    const raf1 = requestAnimationFrame(() => {
      const raf2 = requestAnimationFrame(() => ensureReady());
      rafRef.current = raf2;
    });
    rafRef.current = raf1;
    
    const t = window.setTimeout(() => ensureReady(), 1800);
    timeoutRef.current = t;
    
    return () => {
      if (rafRef.current !== undefined) cancelAnimationFrame(rafRef.current);
      if (timeoutRef.current !== undefined) clearTimeout(timeoutRef.current);
    };
  }, [ensureReady]);

  useEffect(() => {
    let alive = true;
    const ctrl = new AbortController();
    
    (async () => {
      setLoading(true);
      setError(null);
      const q = new URLSearchParams();
      if (symbol) q.set('symbol', symbol);
      
      try {
        const j = await fetchJSON(`/api/flow/live?${q.toString()}`, {
          timeoutMs: 3200, 
          signal: ctrl.signal
        });
        if (!alive) return;
        
        setRows(Array.isArray(j?.items) ? j.items : []);
        setMode(j?.mode ?? 'UNKNOWN');
        ensureReady();
      } catch (e) {
        if (!alive) return;
        
        // DEMO fallback
        setRows([
          { time: '10:01:22', side: 'BUY', kind: 'CALL', strike: 250, expiry: '2025-10-17', qty: 100, price: 2.35, premium: 23500, flags: ['sweep'], linkBuilder: '/build/?symbol=TSLA&s=eyJsZWdzIjpbeyJzaWRlIjoiYnV5IiwidHlwZSI6ImNhbGwiLCJzdHJpa2UiOjI1MCwiZXhwaXJ5IjoiMjAyNS0xMC0xNyIsInF0eSI6MX1dfQ%3D%3D' },
          { time: '10:03:10', side: 'BUY', kind: 'PUT', strike: 240, expiry: '2025-10-17', qty: 150, price: 1.95, premium: 29250, flags: [], linkBuilder: '/build/?symbol=TSLA&s=eyJsZWdzIjpbeyJzaWRlIjoiYnV5IiwidHlwZSI6InB1dCIsInN0cmlrZSI6MjQwLCJleHBpcnkiOiIyMDI1LTEwLTE3IiwicXR5IjoxfV19' },
          { time: '10:05:33', side: 'SELL', kind: 'CALL', strike: 260, expiry: '2025-10-17', qty: 75, price: 1.85, premium: 13875, flags: ['block'], linkBuilder: '/build/?symbol=TSLA&s=eyJsZWdzIjpbeyJzaWRlIjoic2VsbCIsInR5cGUiOiJjYWxsIiwic3RyaWtlIjoyNjAsImV4cGlyeSI6IjIwMjUtMTAtMTciLCJxdHkiOjF9XX0%3D' }
        ]);
        setMode('DEMO');
        setError(e instanceof Error ? e : new Error(String(e)));
        ensureReady();
      }
    })();
    
    return () => { alive = false; ctrl.abort(); };
  }, [symbol, ensureReady]);

  return (
    <div className="space-y-6" data-testid="live-flow-page">
      {pageReady ? (
        <>
          <div className="bg-white rounded-2xl shadow overflow-hidden">
            <div className="px-6 py-4 border-b border-gray-200">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-xl font-semibold text-gray-900">
                    Live Flow {symbol && `for ${symbol}`}
                  </h2>
                  <p className="text-sm text-gray-600 mt-1">
                    Real-time options flow data
                  </p>
                </div>
                <div className="flex items-center gap-2">
                  <span className={`text-xs rounded px-2 py-1 border ${
                    mode === 'LIVE' 
                      ? 'border-emerald-500 bg-emerald-50 text-emerald-700' 
                      : mode === 'DEMO' 
                      ? 'border-amber-500 bg-amber-50 text-amber-700'
                      : 'border-slate-500 bg-slate-50 text-slate-700'
                  }`}>
                    {mode === 'LIVE' ? 'LIVE FEED' : mode === 'DEMO' ? 'DEMO DATA' : 'UNKNOWN'}
                  </span>
                  {error && (
                    <span className="text-xs text-amber-600 bg-amber-50 px-2 py-1 rounded border border-amber-200">
                      degraded: using fallback
                    </span>
                  )}
                </div>
              </div>
            </div>

            {rows.length > 0 ? (
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Time</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Side</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Kind</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Strike</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Expiry</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Qty</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Price</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Premium</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Flags</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {rows.map((row, i) => (
                      <tr key={i} className="hover:bg-gray-50">
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {row.time}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`inline-flex px-2 py-1 text-xs rounded-full ${
                            row.side === 'BUY' 
                              ? 'bg-emerald-100 text-emerald-800' 
                              : 'bg-rose-100 text-rose-800'
                          }`}>
                            {row.side}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {row.kind}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          ${row.strike}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {row.expiry}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {row.qty}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          ${row.price}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          ${row.premium.toLocaleString()}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="flex gap-1">
                            {(row.flags || []).map((flag, j) => (
                              <span key={j} className={`inline-flex px-2 py-1 text-xs rounded-full ${
                                flag === 'sweep' ? 'bg-blue-100 text-blue-800' :
                                flag === 'block' ? 'bg-purple-100 text-purple-800' :
                                flag === '0DTE' ? 'bg-red-100 text-red-800' :
                                'bg-gray-100 text-gray-800'
                              }`}>
                                {flag}
                              </span>
                            ))}
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm">
                          {row.linkBuilder && (
                            <a
                              href={row.linkBuilder}
                              className="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-indigo-700 bg-indigo-100 hover:bg-indigo-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                            >
                              Open in Builder
                            </a>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <div className="p-8 text-center text-gray-500">
                No live flow data available (demo fallback active).
              </div>
            )}
          </div>
        </>
      ) : (
        <div className="bg-white rounded-2xl shadow p-8">
          <div className="flex items-center justify-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            <span className="ml-3 text-gray-600">Loading Live Flow…</span>
          </div>
        </div>
      )}
    </div>
  );
}