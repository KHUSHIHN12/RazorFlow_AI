import React, { useState, useEffect } from 'react';
import { BarChart3, RefreshCw, Sparkles, ShieldCheck, Layers } from 'lucide-react';
import { api } from '../../services/api';
import KeyMetrics from './KeyMetrics';
import IntentChart from './IntentChart';
import CampaignCard from './CampaignCard';

export default function Dashboard() {
  const [metrics, setMetrics] = useState({
    total_sessions: 150,
    successful_checkouts: 42,
    conversion_rate: 28.0,
    total_revenue_inr: 2478000.0,
    top_intents: [],
    campaigns: []
  });
  const [loading, setLoading] = useState(true);

  const loadMetrics = async () => {
    try {
      setLoading(true);
      const data = await api.fetchMerchantMetrics();
      setMetrics(data);
    } catch (ex) {
      console.error('Failed to load merchant metrics:', ex);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadMetrics();
  }, []);

  return (
    <div className="max-w-7xl mx-auto p-4 sm:p-6 lg:p-8 space-y-8">
      
      {/* Dashboard Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b border-slate-800">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-extrabold text-white tracking-tight flex items-center gap-2">
              <BarChart3 className="w-7 h-7 text-cyan-400" />
              Merchant Growth & Agent Analytics
            </h1>
            <span className="px-2.5 py-0.5 rounded-full text-xs font-mono bg-blue-500/10 text-blue-400 border border-blue-500/30">
              Live Insights
            </span>
          </div>
          <p className="text-sm text-slate-400 mt-1">
            Real-time intent discovery, conversion tracking, and AI-driven campaign bundle recommendations
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={loadMetrics}
            disabled={loading}
            className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-slate-900 hover:bg-slate-800 border border-slate-700 text-slate-200 text-xs font-semibold transition-all active:scale-95 disabled:opacity-50"
          >
            <RefreshCw className={`w-4 h-4 text-cyan-400 ${loading ? 'animate-spin' : ''}`} />
            <span>Refresh Metrics</span>
          </button>
        </div>
      </div>

      {/* 1. Key Metrics Cards */}
      <KeyMetrics metrics={metrics} />

      {/* 2. Main Content Grid: Intent Chart & AI Campaigns */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        
        {/* Left Column: Intent Chart */}
        <IntentChart intents={metrics.top_intents || []} />

        {/* Right Column: AI Bundle Campaigns */}
        <div className="p-6 rounded-2xl bg-slate-900/90 border border-slate-800 backdrop-blur-md space-y-5">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-base font-bold text-slate-100 flex items-center gap-2">
                <Sparkles className="w-5 h-5 text-purple-400" />
                AI-Suggested Bundle Campaigns
              </h3>
              <p className="text-xs text-slate-400 mt-0.5">
                Automatically generated cross-sell bundles based on frequent query co-occurrences
              </p>
            </div>
            <span className="flex items-center gap-1 text-xs font-mono font-bold text-purple-400 bg-purple-500/10 px-3 py-1 rounded-full border border-purple-500/20">
              <Layers className="w-3.5 h-3.5" /> High Lift
            </span>
          </div>

          <div className="space-y-4">
            {metrics.campaigns && metrics.campaigns.map((camp) => (
              <CampaignCard key={camp.id} campaign={camp} onRefresh={loadMetrics} />
            ))}
          </div>
        </div>

      </div>

      {/* Footer System Status Banner */}
      <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 flex flex-col sm:flex-row items-center justify-between gap-3 text-xs font-mono text-slate-400">
        <div className="flex items-center gap-2">
          <ShieldCheck className="w-4 h-4 text-emerald-400" />
          <span>Razorpay AI Buildathon — Track 1: AI Growth & Agentic Commerce</span>
        </div>
        <span className="text-slate-400">
          Stateful LangGraph + FastAPI + React SPA Architecture
        </span>
      </div>

    </div>
  );
}
