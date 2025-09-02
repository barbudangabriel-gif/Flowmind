import { useEffect, useState } from 'react';
import { portfolioAPI } from '../lib/portfolioAPI';
import EquityChart from './EquityChart';
import EODChart from './EODChart';
import { drawdown, utilization, fmtPct, last } from '../lib/metrics';

// Utility functions for analytics calculations
const calculateDrawdownMetrics = (equityCurve) => {
  if (!equityCurve || equityCurve.length === 0) return { maxDD: 0, currentDD: 0 };
  
  let peak = equityCurve[0]?.equity || 0;
  let maxDrawdown = 0;
  let currentDrawdown = 0;
  
  equityCurve.forEach(point => {
    const equity = point.equity || 0;
    if (equity > peak) {
      peak = equity;
      currentDrawdown = 0;
    } else {
      currentDrawdown = ((peak - equity) / peak) * 100;
      maxDrawdown = Math.max(maxDrawdown, currentDrawdown);
    }
  });
  
  return { 
    maxDD: Math.round(maxDrawdown * 100) / 100, 
    currentDD: Math.round(currentDrawdown * 100) / 100 
  };
};

const calculateUtilization = (currentEquity, startValue) => {
  if (!startValue || startValue === 0) return 0;
  return Math.round(((currentEquity - startValue) / startValue) * 10000) / 100;
};

export default function AnalyticsPanel({ portfolioId }) {
  const [totalEquity, setTotalEquity] = useState([]);
  const [buckets, setBuckets] = useState([]);
  const [bucketSeries, setBucketSeries] = useState({});
  const [loading, setLoading] = useState(true);
  const [analytics, setAnalytics] = useState({});
  const [activeTab, setActiveTab] = useState('equity');
  
  // EOD state
  const [eod, setEod] = useState([]);
  const [eodLoading, setEodLoading] = useState(false);
  const [eodErr, setEodErr] = useState(null);
  const [snapBusy, setSnapBusy] = useState(false);

  // Load EOD data when tab changes to EOD
  useEffect(() => {
    if (activeTab !== 'eod' || !portfolioId) return;
    
    const loadEOD = async () => {
      setEodLoading(true);
      setEodErr(null);
      try {
        const response = await portfolioAPI.eod(portfolioId);
        setEod(response.series || []);
      } catch (error) {
        console.error('Failed to load EOD data:', error);
        setEodErr(error?.message || 'EOD load failed');
      } finally {
        setEodLoading(false);
      }
    };
    
    loadEOD();
  }, [portfolioId, activeTab]);

  // Snapshot Now function
  const snapNow = async () => {
    if (!portfolioId || snapBusy) return;
    
    setSnapBusy(true);
    setEodErr(null);
    try {
      await portfolioAPI.eodSnapshot(portfolioId);
      // Refresh EOD data after snapshot
      const response = await portfolioAPI.eod(portfolioId);
      setEod(response.series || []);
    } catch (error) {
      console.error('Snapshot failed:', error);
      setEodErr(error?.message || 'Snapshot failed');
    } finally {
      setSnapBusy(false);
    }
  };

  useEffect(() => {
    if (!portfolioId) return;

    const loadAnalytics = async () => {
      setLoading(true);
      try {
        // Load total portfolio equity
        const totalData = await portfolioAPI.equity(portfolioId, { start: 0 });
        console.log('Total equity data:', totalData);
        
        let equityCurve = [];
        if (totalData.analytics && totalData.analytics.equity_curve) {
          equityCurve = totalData.analytics.equity_curve;
        } else if (totalData.equity_curve) {
          equityCurve = totalData.equity_curve;
        } else {
          // Generate sample data from summary if available
          const mockData = [{
            date: new Date().toISOString().split('T')[0],
            equity: totalData.analytics?.summary?.current_equity || 10000,
            realizedCum: totalData.analytics?.summary?.total_realized_pnl || 0
          }];
          equityCurve = mockData;
        }
        
        setTotalEquity(equityCurve);
        
        // Calculate portfolio-level analytics
        const portfolioMetrics = calculateDrawdownMetrics(equityCurve);
        const currentEquity = equityCurve.length > 0 ? equityCurve[equityCurve.length - 1].equity : 0;
        
        // Load buckets
        const bucketsResponse = await portfolioAPI.listBuckets(portfolioId);
        const bucketsList = bucketsResponse.buckets || bucketsResponse || [];
        setBuckets(bucketsList);

        // Load equity data for each bucket
        const bucketData = {};
        const bucketAnalytics = {};
        
        for (const bucket of bucketsList) {
          try {
            const bucketEquity = await portfolioAPI.equity(portfolioId, { 
              bucketId: bucket.id, 
              start: bucket.start_value 
            });
            
            let bucketCurve = [];
            if (bucketEquity.analytics && bucketEquity.analytics.equity_curve) {
              bucketCurve = bucketEquity.analytics.equity_curve;
            } else if (bucketEquity.equity_curve) {
              bucketCurve = bucketEquity.equity_curve;
            } else {
              // Generate sample data for bucket
              bucketCurve = [{
                date: new Date().toISOString().split('T')[0],
                equity: bucket.start_value || 100000,
                realizedCum: 0
              }];
            }
            
            bucketData[bucket.id] = bucketCurve;
            
            // Calculate bucket-specific analytics
            const bucketMetrics = calculateDrawdownMetrics(bucketCurve);
            const bucketCurrentEquity = bucketCurve.length > 0 ? bucketCurve[bucketCurve.length - 1].equity : bucket.start_value;
            const utilization = calculateUtilization(bucketCurrentEquity, bucket.start_value);
            
            bucketAnalytics[bucket.id] = {
              ...bucketMetrics,
              utilization,
              currentEquity: bucketCurrentEquity,
              startValue: bucket.start_value
            };
            
          } catch (error) {
            console.warn(`Failed to load equity for bucket ${bucket.id}:`, error);
            bucketData[bucket.id] = [];
            bucketAnalytics[bucket.id] = { maxDD: 0, currentDD: 0, utilization: 0 };
          }
        }
        
        setBucketSeries(bucketData);
        setAnalytics({
          portfolio: {
            ...portfolioMetrics,
            currentEquity
          },
          buckets: bucketAnalytics
        });

      } catch (error) {
        console.error('Failed to load analytics:', error);
      } finally {
        setLoading(false);
      }
    };

    loadAnalytics();
  }, [portfolioId]);

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="bg-white rounded-2xl shadow p-4">
          <div className="animate-pulse h-64 bg-gray-200 rounded"></div>
        </div>
      </div>
    );
  }

  const tabs = [
    { id: 'equity', label: 'Equity (Realized)', icon: '📈' },
    { id: 'eod', label: 'EOD (R+UR)', icon: '🌅' }
  ];

  return (
    <div className="space-y-6">
      {/* Analytics Tab Navigation */}
      <div className="bg-white rounded-2xl shadow p-4">
        <div className="border-b border-gray-200 mb-4">
          <nav className="flex space-x-8">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`py-2 px-1 border-b-2 font-medium text-sm ${
                  activeTab === tab.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <span className="mr-2">{tab.icon}</span>
                {tab.label}
              </button>
            ))}
          </nav>
        </div>

        {/* BADGES pentru tab-ul curent */}
        {activeTab === 'equity' && (() => {
          const dd = drawdown(totalEquity.map(p => ({ equity: p.equity })));
          return (
            <div className="flex gap-3 text-sm mb-4">
              <span className="px-2 py-1 rounded bg-slate-100">MaxDD: <b>{fmtPct(dd.max)}</b></span>
              <span className="px-2 py-1 rounded bg-slate-100">CurDD: <b>{fmtPct(dd.current)}</b></span>
            </div>
          );
        })()}
        {activeTab === 'eod' && (() => {
          const dd = drawdown((eod || []).map(p => ({ equity: p.total })));
          return (
            <div className="flex gap-3 text-sm mb-4">
              <span className="px-2 py-1 rounded bg-slate-100">MaxDD (EOD): <b>{fmtPct(dd.max)}</b></span>
              <span className="px-2 py-1 rounded bg-slate-100">CurDD (EOD): <b>{fmtPct(dd.current)}</b></span>
            </div>
          );
        })()}

        {/* Equity Tab Content */}
        {activeTab === 'equity' && (
          <div>
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-semibold text-lg">Portfolio Total — Equity (realized)</h3>
              <div className="flex items-center gap-4">
                <button
                  onClick={() => {
                    const url = `${import.meta.env.REACT_APP_BACKEND_URL || '/api'}/portfolios/${portfolioId}/analytics/equity.csv`;
                    window.open(url, '_blank');
                  }}
                  className="px-3 py-1 text-xs bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
                >
                  📥 Export CSV
                </button>
                <div className="flex gap-4 text-sm">
                  <div className="text-gray-600">
                    Current DD: <span className="font-mono text-red-600">{analytics.portfolio?.currentDD || 0}%</span>
                  </div>
                  <div className="text-gray-600">
                    Max DD: <span className="font-mono text-red-700">{analytics.portfolio?.maxDD || 0}%</span>
                  </div>
                  <div className="text-gray-600">
                    Equity: <span className="font-mono text-blue-600">${(analytics.portfolio?.currentEquity || 0).toLocaleString()}</span>
                  </div>
                </div>
              </div>
            </div>
            <EquityChart data={totalEquity} />
          </div>
        )}

        {/* EOD Tab Content */}
        {activeTab === 'eod' && (
          <div>
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-semibold text-lg">EOD Total (R+UR) — Europe/Bucharest</h3>
              <div className="flex items-center gap-4">
                <button
                  onClick={snapNow}
                  disabled={snapBusy}
                  className="px-3 py-1.5 text-sm bg-emerald-600 text-white rounded hover:bg-emerald-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
                >
                  {snapBusy ? 'Running…' : '📸 Snapshot Now'}
                </button>
                <div className="text-sm text-gray-600">
                  TZ: Europe/Bucharest
                </div>
              </div>
            </div>

            {eodLoading ? (
              <div className="p-4 text-gray-500">Loading EOD…</div>
            ) : eodErr ? (
              <div className="p-3 bg-rose-50 text-rose-700 rounded border border-rose-200">
                {eodErr}
              </div>
            ) : (
              <EODChart data={eod} title="EOD Total (R+UR)" />
            )}
          </div>
        )}
      </div>
      
      {/* Buckets Analytics */}
      {buckets.length > 0 && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {buckets.map(bucket => {
            const bucketStats = analytics.buckets?.[bucket.id] || {};
            const s = bucketSeries[bucket.id] || [];
            const lastPoint = last(s);
            const util = lastPoint ? utilization(lastPoint.equity, bucket.start_value) : 0;
            const utilizationColor = bucketStats.utilization >= 0 ? 'text-green-600' : 'text-red-600';
            
            return (
              <div key={bucket.id} className="bg-white rounded-2xl shadow p-4">
                <div className="mb-3">
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="font-semibold">{bucket.name}</h4>
                    <div className="flex items-center gap-2">
                      <div className="text-sm text-gray-500">
                        Start: ${bucket.start_value?.toLocaleString() || '0'}
                      </div>
                      <div className={`px-2 py-0.5 rounded text-sm ${util >= 0.8 ? 'bg-rose-100 text-rose-700' : util >= 0.5 ? 'bg-amber-100 text-amber-700' : 'bg-emerald-100 text-emerald-700'}`}>
                        Utilization: <b>{fmtPct(util)}</b>
                      </div>
                    </div>
                  </div>
                  
                  <div className="grid grid-cols-4 gap-3 text-xs">
                    <div className="text-center">
                      <div className="text-gray-500">Utilization</div>
                      <div className={`font-mono font-semibold ${utilizationColor}`}>
                        {bucketStats.utilization || 0}%
                      </div>
                    </div>
                    <div className="text-center">
                      <div className="text-gray-500">Current DD</div>
                      <div className="font-mono text-red-600">
                        {bucketStats.currentDD || 0}%
                      </div>
                    </div>
                    <div className="text-center">
                      <div className="text-gray-500">Max DD</div>
                      <div className="font-mono text-red-700">
                        {bucketStats.maxDD || 0}%
                      </div>
                    </div>
                    <div className="text-center">
                      <div className="text-gray-500">Current</div>
                      <div className="font-mono text-blue-600">
                        ${(bucketStats.currentEquity || 0).toLocaleString()}
                      </div>
                    </div>
                  </div>
                </div>
                
                <EquityChart data={bucketSeries[bucket.id] || []} />
              </div>
            );
          })}
        </div>
      )}
      
      {buckets.length === 0 && (
        <div className="bg-white rounded-2xl shadow p-4 text-center text-gray-500">
          No buckets created yet. Create a bucket to track specific strategies.
        </div>
      )}
    </div>
  );
}