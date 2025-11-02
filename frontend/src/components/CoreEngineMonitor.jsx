/**
 * CoreEngineMonitor Component
 * Real-time monitoring dashboard for 198-agent CORE ENGINE system.
 * 
 * Features:
 * - Start/Stop controls
 * - Live agent health per tier
 * - Signal flow metrics
 * - Performance statistics
 * - Recent execution signals
 */

import React, { useState, useEffect } from 'react';

const API = process.env.REACT_APP_BACKEND_URL || "";

const CoreEngineMonitor = () => {
  const [stats, setStats] = useState(null);
  const [health, setHealth] = useState(null);
  const [signals, setSignals] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [starting, setStarting] = useState(false);
  const [stopping, setStopping] = useState(false);

  // Fetch orchestrator stats
  const fetchStats = async () => {
    try {
      const response = await fetch(`${API}/api/core-engine/stats`);
      if (!response.ok) throw new Error('Failed to fetch stats');
      const data = await response.json();
      setStats(data);
      setError(null);
    } catch (err) {
      setError(err.message);
    }
  };

  // Fetch health status
  const fetchHealth = async () => {
    try {
      const response = await fetch(`${API}/api/core-engine/health`);
      if (!response.ok) throw new Error('Failed to fetch health');
      const data = await response.json();
      setHealth(data);
    } catch (err) {
      console.error('Health fetch error:', err);
    }
  };

  // Fetch recent signals
  const fetchSignals = async () => {
    try {
      const response = await fetch(`${API}/api/core-engine/signals?limit=10`);
      if (!response.ok) throw new Error('Failed to fetch signals');
      const data = await response.json();
      setSignals(data);
    } catch (err) {
      console.error('Signals fetch error:', err);
    }
  };

  // Start CORE ENGINE
  const handleStart = async () => {
    setStarting(true);
    try {
      const response = await fetch(`${API}/api/core-engine/start`, {
        method: 'POST',
      });
      if (!response.ok) throw new Error('Failed to start CORE ENGINE');
      const data = await response.json();
      alert(data.message);
      await fetchStats();
      await fetchHealth();
    } catch (err) {
      alert(`Start failed: ${err.message}`);
    } finally {
      setStarting(false);
    }
  };

  // Stop CORE ENGINE
  const handleStop = async () => {
    if (!window.confirm('Stop CORE ENGINE? All 198 agents will halt.')) return;
    
    setStopping(true);
    try {
      const response = await fetch(`${API}/api/core-engine/stop`, {
        method: 'POST',
      });
      if (!response.ok) throw new Error('Failed to stop CORE ENGINE');
      const data = await response.json();
      alert(data.message);
      await fetchStats();
      await fetchHealth();
    } catch (err) {
      alert(`Stop failed: ${err.message}`);
    } finally {
      setStopping(false);
    }
  };

  // Initial load
  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      await Promise.all([fetchStats(), fetchHealth(), fetchSignals()]);
      setLoading(false);
    };
    loadData();
  }, []);

  // Auto-refresh every 5s
  useEffect(() => {
    const interval = setInterval(() => {
      if (stats?.is_running) {
        fetchStats();
        fetchHealth();
        fetchSignals();
      }
    }, 5000);

    return () => clearInterval(interval);
  }, [stats?.is_running]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-slate-400">Loading CORE ENGINE status...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-4 bg-red-900/20 border border-red-700 rounded-lg">
        <div className="text-red-400 font-medium">Error loading CORE ENGINE</div>
        <div className="text-red-300 text-sm mt-1">{error}</div>
      </div>
    );
  }

  const isRunning = stats?.is_running || false;
  const uptimeMinutes = stats ? Math.floor(stats.uptime_seconds / 60) : 0;
  const uptimeHours = Math.floor(uptimeMinutes / 60);
  const uptimeDisplay = uptimeHours > 0 
    ? `${uptimeHours}h ${uptimeMinutes % 60}m`
    : `${uptimeMinutes}m`;

  return (
    <div className="space-y-4">
      {/* Control Panel */}
      <div className="bg-slate-800 border border-slate-700 rounded-lg p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <div className={`w-3 h-3 rounded-full ${isRunning ? 'bg-green-500 animate-pulse' : 'bg-red-500'}`} />
              <span className="text-white font-medium">
                {isRunning ? 'OPERATIONAL' : 'OFFLINE'}
              </span>
            </div>
            {isRunning && (
              <div className="text-slate-400 text-sm">
                Uptime: {uptimeDisplay}
              </div>
            )}
          </div>
          <div className="flex gap-2">
            <button
              onClick={handleStart}
              disabled={isRunning || starting}
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                isRunning || starting
                  ? 'bg-slate-700 text-slate-500 cursor-not-allowed'
                  : 'bg-green-600 hover:bg-green-700 text-white'
              }`}
            >
              {starting ? 'Starting...' : 'Start'}
            </button>
            <button
              onClick={handleStop}
              disabled={!isRunning || stopping}
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                !isRunning || stopping
                  ? 'bg-slate-700 text-slate-500 cursor-not-allowed'
                  : 'bg-red-600 hover:bg-red-700 text-white'
              }`}
            >
              {stopping ? 'Stopping...' : 'Stop'}
            </button>
          </div>
        </div>
      </div>

      {/* Agent Health Grid */}
      {health && (
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          {/* Tier 1: Director */}
          <AgentTierCard
            title="Master Director"
            tier="Tier 1"
            running={health.tiers.tier1_director?.running || 0}
            total={health.tiers.tier1_director?.total || 1}
            status={health.tiers.tier1_director?.status || 'critical'}
          />

          {/* Tier 2: Sector Heads */}
          <AgentTierCard
            title="Sector Heads"
            tier="Tier 2"
            running={health.tiers.tier2_sector_heads?.running || 0}
            total={health.tiers.tier2_sector_heads?.total || 10}
            status={health.tiers.tier2_sector_heads?.status || 'critical'}
          />

          {/* Tier 3: Team Leads */}
          <AgentTierCard
            title="Team Leads"
            tier="Tier 3"
            running={health.tiers.tier3_team_leads?.running || 0}
            total={health.tiers.tier3_team_leads?.total || 20}
            status={health.tiers.tier3_team_leads?.status || 'critical'}
          />

          {/* Tier 4: Scanners */}
          <AgentTierCard
            title="Scanner Agents"
            tier="Tier 4"
            running={health.tiers.tier4_scanners?.running || 0}
            total={health.tiers.tier4_scanners?.total || 167}
            status={health.tiers.tier4_scanners?.status || 'critical'}
          />
        </div>
      )}

      {/* Signal Flow & Performance */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Signal Flow */}
        {stats?.signal_flow && (
          <div className="bg-slate-800 border border-slate-700 rounded-lg p-4">
            <div className="text-white font-medium mb-3">Signal Flow</div>
            <div className="space-y-2">
              <SignalFlowRow
                label="Universe Published"
                value={stats.signal_flow.universe_published}
                color="blue"
              />
              <SignalFlowRow
                label="Validated (Team Leads)"
                value={stats.signal_flow.validated_published}
                color="cyan"
              />
              <SignalFlowRow
                label="Approved (Sector Heads)"
                value={stats.signal_flow.approved_published}
                color="green"
              />
              <SignalFlowRow
                label="Final (Director)"
                value={stats.signal_flow.final_published}
                color="purple"
              />
            </div>
          </div>
        )}

        {/* Performance Metrics */}
        {stats?.performance && (
          <div className="bg-slate-800 border border-slate-700 rounded-lg p-4">
            <div className="text-white font-medium mb-3">Performance</div>
            <div className="space-y-3">
              <PerformanceMetric
                label="Signals/Second"
                value={stats.performance.signals_per_second.toFixed(2)}
              />
              <PerformanceMetric
                label="Win Rate"
                value={`${stats.performance.win_rate_percent.toFixed(1)}%`}
              />
              <PerformanceMetric
                label="Avg Latency"
                value={`${stats.performance.avg_latency_seconds.toFixed(2)}s`}
              />
            </div>
          </div>
        )}
      </div>

      {/* Recent Signals */}
      {signals.length > 0 && (
        <div className="bg-slate-800 border border-slate-700 rounded-lg p-4">
          <div className="text-white font-medium mb-3">Recent Execution Signals</div>
          <div className="space-y-2 max-h-64 overflow-y-auto">
            {signals.map((signal, idx) => (
              <SignalCard key={signal.signal_id || idx} signal={signal} />
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

// Tier Health Card Component
const AgentTierCard = ({ title, tier, running, total, status }) => {
  const healthPct = total > 0 ? (running / total * 100) : 0;
  const statusColor = {
    healthy: 'border-green-500 bg-green-900/20',
    degraded: 'border-yellow-500 bg-yellow-900/20',
    critical: 'border-red-500 bg-red-900/20',
  }[status] || 'border-slate-700 bg-slate-900/20';

  return (
    <div className={`border rounded-lg p-3 ${statusColor}`}>
      <div className="text-slate-400 text-xs mb-1">{tier}</div>
      <div className="text-white font-medium mb-2">{title}</div>
      <div className="flex items-end justify-between">
        <div>
          <div className="text-2xl font-bold text-white">{running}</div>
          <div className="text-slate-400 text-xs">/ {total} agents</div>
        </div>
        <div className="text-right">
          <div className="text-lg font-medium text-white">{healthPct.toFixed(0)}%</div>
          <div className="text-slate-400 text-xs">{status}</div>
        </div>
      </div>
    </div>
  );
};

// Signal Flow Row Component
const SignalFlowRow = ({ label, value, color }) => {
  const colorClass = {
    blue: 'text-blue-400',
    cyan: 'text-cyan-400',
    green: 'text-green-400',
    purple: 'text-purple-400',
  }[color] || 'text-slate-400';

  return (
    <div className="flex justify-between items-center">
      <span className="text-slate-400 text-sm">{label}</span>
      <span className={`font-medium ${colorClass}`}>{value}</span>
    </div>
  );
};

// Performance Metric Component
const PerformanceMetric = ({ label, value }) => (
  <div className="flex justify-between items-center">
    <span className="text-slate-400 text-sm">{label}</span>
    <span className="text-white font-medium">{value}</span>
  </div>
);

// Signal Card Component
const SignalCard = ({ signal }) => (
  <div className="bg-slate-900/50 border border-slate-700 rounded p-3">
    <div className="flex items-start justify-between mb-2">
      <div>
        <span className="text-white font-medium text-lg">{signal.ticker}</span>
        <span className="ml-2 text-cyan-400 text-sm">{signal.action}</span>
      </div>
      <span className="text-slate-400 text-xs">{signal.confidence.toFixed(0)}% conf</span>
    </div>
    <div className="grid grid-cols-2 gap-2 text-sm mb-2">
      <div>
        <span className="text-slate-500">Position:</span>
        <span className="text-white ml-1">${signal.position_size.toLocaleString()}</span>
      </div>
      <div>
        <span className="text-slate-500">Max Loss:</span>
        <span className="text-red-400 ml-1">${signal.max_loss.toLocaleString()}</span>
      </div>
    </div>
    {signal.reasoning && (
      <div className="text-slate-400 text-xs truncate">{signal.reasoning}</div>
    )}
  </div>
);

export default CoreEngineMonitor;
