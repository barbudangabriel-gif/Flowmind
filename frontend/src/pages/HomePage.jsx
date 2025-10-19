// =============================================
// FlowMind — Dashboard (HomePage)
// =============================================
import React from 'react';
import { Link } from 'react-router-dom';
import { TrendingUp, Activity, Wallet, BarChart3, Zap, ArrowRight } from 'lucide-react';

export default function HomePage() {
  const quickActions = [
    {
      title: 'Strategy Builder',
      description: 'Build & analyze 54+ options strategies',
      icon: TrendingUp,
      link: '/builder',
      color: 'emerald',
      badge: '54+ Strategies'
    },
    {
      title: 'Options Flow',
      description: 'Real-time unusual options activity',
      icon: Activity,
      link: '/flow',
      color: 'blue',
      badge: 'Live'
    },
    {
      title: 'Mindfolio Manager',
      description: 'Track positions & performance',
      icon: Wallet,
      link: '/portfolios',
      color: 'purple',
      badge: 'Multi-Portfolio'
    },
    {
      title: 'Optimize',
      description: 'AI-powered strategy recommendations',
      icon: BarChart3,
      link: '/optimize',
      color: 'amber',
      badge: 'AI'
    }
  ];

  const stats = [
    { label: 'Strategies Available', value: '54+', icon: TrendingUp },
    { label: 'Live Data Feeds', value: '2', icon: Activity },
    { label: 'Real-time Updates', value: '24/7', icon: Activity },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#0a0e1a] via-[#0f1419] to-[#0a0e1a] p-8">
      {/* Hero Section */}
      <div className="max-w-7xl mx-auto">
        <div className="mb-12 flex items-end gap-8">
          <div className="flex-1 space-y-8">
            <div>
              <h1 className="text-5xl font-medium text-white mb-4">
                Welcome to <span className="text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 to-blue-500">FlowMind Analytics</span>
              </h1>
              <p className="text-xl text-slate-300 max-w-3xl">
                Professional-grade stocks and options analytics with real-time flow monitoring, 
                strategy building, and AI-powered <span className="text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 to-blue-500 font-semibold">algos</span> and recommendations.
              </p>
            </div>
            
            {/* Stats Bar - moved up next to brain */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {stats.map((stat, idx) => (
                <div key={idx} className="bg-slate-900/50 border border-slate-800 rounded-lg p-6 backdrop-blur-sm">
                  <div className="flex items-center gap-3 mb-2">
                    <stat.icon className="w-4 h-4 text-emerald-400" />
                    <span className="text-slate-400 text-sm">{stat.label}</span>
                  </div>
                  <div className="text-[26px] font-normal text-white">{stat.value}</div>
                </div>
              ))}
            </div>
          </div>
          
          {/* Brain logo on the right */}
          <div className="shrink-0">
            <img 
              src="/assets/logos/flowmind_brain_orange_transparent_10s.gif" 
              alt="FlowMind Brain" 
              className="w-[320px] h-auto"
            />
          </div>
        </div>

        {/* Quick Actions Grid */}
        <div className="mb-12">
          <h2 className="text-2xl font-normal text-white mb-6">
            Quick Actions
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {quickActions.map((action, idx) => {
              const colorClasses = {
                emerald: 'from-emerald-500/20 to-emerald-600/10 border-emerald-500/30 hover:border-emerald-400',
                blue: 'from-blue-500/20 to-blue-600/10 border-blue-500/30 hover:border-blue-400',
                purple: 'from-purple-500/20 to-purple-600/10 border-purple-500/30 hover:border-purple-400',
                amber: 'from-amber-500/20 to-amber-600/10 border-amber-500/30 hover:border-amber-400',
              };

              const iconColorClasses = {
                emerald: 'text-emerald-400',
                blue: 'text-blue-400',
                purple: 'text-purple-400',
                amber: 'text-amber-400',
              };

              return (
                <Link
                  key={idx}
                  to={action.link}
                  className={`group relative overflow-hidden bg-gradient-to-br ${colorClasses[action.color]} border rounded-xl p-6 transition-all duration-300 hover:scale-105 hover:shadow-2xl`}
                >
                  <div className="relative z-10">
                    <div className="flex items-start justify-between mb-4">
                      <action.icon className={`w-4 h-4 ${iconColorClasses[action.color]}`} />
                      {action.badge && (
                        <span className="px-2 py-1 bg-slate-900/70 backdrop-blur-sm text-white text-xs font-medium rounded-full border border-slate-700">
                          {action.badge}
                        </span>
                      )}
                    </div>
                    
                    <h3 className="text-xl font-normal text-white mb-2 group-hover:text-white transition-colors">
                      {action.title}
                    </h3>
                    <p className="text-slate-300 text-sm mb-4">
                      {action.description}
                    </p>
                    
                    <div className="flex items-center gap-2 text-white text-sm font-medium">
                      <span>Get Started</span>
                      <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                    </div>
                  </div>
                  
                  {/* Gradient overlay on hover */}
                  <div className="absolute inset-0 bg-gradient-to-br from-white/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity"></div>
                </Link>
              );
            })}
          </div>
        </div>

        {/* Feature Highlights */}
        <div className="bg-slate-900/30 border border-slate-800 rounded-xl p-8 backdrop-blur-sm">
          <h2 className="text-2xl font-normal text-white mb-6">Platform Features</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="flex gap-4">
              <div className="shrink-0">
                <TrendingUp className="w-4 h-4 text-emerald-400" />
              </div>
              <div>
                <h3 className="text-white font-normal mb-1">Advanced Strategy Builder</h3>
                <p className="text-slate-400 text-sm">
                  54+ pre-built strategies with real-time P&L visualization, Greeks calculation, and quality scoring.
                </p>
              </div>
            </div>

            <div className="flex gap-4">
              <div className="shrink-0">
                <Activity className="w-4 h-4 text-blue-400" />
              </div>
              <div>
                <h3 className="text-white font-normal mb-1">Real-Time Options Flow</h3>
                <p className="text-slate-400 text-sm">
                  Monitor unusual options activity, sweeps, and blocks from institutional traders.
                </p>
              </div>
            </div>

            <div className="flex gap-4">
              <div className="shrink-0">
                <Wallet className="w-4 h-4 text-purple-400" />
              </div>
              <div>
                <h3 className="text-white font-normal mb-1">Mindfolio Management</h3>
                <p className="text-slate-400 text-sm">
                  Multi-portfolio support with budget allocation, FIFO position tracking, and performance analytics.
                </p>
              </div>
            </div>

            <div className="flex gap-4">
              <div className="shrink-0">
                <BarChart3 className="w-4 h-4 text-amber-400" />
              </div>
              <div>
                <h3 className="text-white font-normal mb-1">AI-Powered Optimization</h3>
                <p className="text-slate-400 text-sm">
                  Get strategy recommendations based on market conditions, sentiment, and risk tolerance.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
