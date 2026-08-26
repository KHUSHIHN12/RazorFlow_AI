import React, { useState, useEffect } from 'react';
import { BarChart3, RefreshCw } from 'lucide-react';
import { api } from '../../services/api';
import KeyMetrics from './KeyMetrics';
import CustomerDemand from './CustomerDemand';
import ProductPerformance from './ProductPerformance';
import AIGrowthActions from './AIGrowthActions';

export default function Dashboard() {
  const [metrics, setMetrics] = useState({
    total_sessions: 150,
    successful_checkouts: 42,
    conversion_rate: 28.0,
    total_revenue_inr: 2478000.0,
    top_intents: [],
    categories_demand: [],
    unfulfilled_requests: [],
    top_products: [],
    high_demand_low_conversion: [],
    ai_growth_actions: []
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
    <div className="max-w-7xl mx-auto p-4 sm:p-6 lg:p-8 space-y-8 bg-slate-50 min-h-[calc(100vh-4rem)]">

      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-200">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-xl sm:text-2xl font-extrabold text-slate-900 tracking-tight flex items-center gap-2">
              <BarChart3 className="w-6 h-6 text-blue-600" />
              Merchant Growth Dashboard
            </h1>
            <span className="px-2 py-0.5 rounded-full text-xs font-mono bg-blue-50 text-blue-700 border border-blue-200 font-bold">
              Demand → Performance → Action
            </span>
          </div>
          <p className="text-xs text-slate-500 mt-0.5">
            Real-time merchant intelligence, customer demand analytics, and AI growth recommendations
          </p>
        </div>

        <button
          onClick={loadMetrics}
          disabled={loading}
          className="flex items-center gap-2 px-3.5 py-2 rounded-xl bg-white hover:bg-slate-100 border border-slate-200 text-slate-700 text-xs font-semibold shadow-2xs transition-all active:scale-95 disabled:opacity-50 self-start sm:self-auto"
        >
          <RefreshCw className={`w-3.5 h-3.5 text-blue-600 ${loading ? 'animate-spin' : ''}`} />
          <span>Refresh Analytics</span>
        </button>
      </div>

      {/* 1. KEY METRICS */}
      <KeyMetrics metrics={metrics} />

      {/* 2. CUSTOMER DEMAND */}
      <CustomerDemand
        categoriesDemand={metrics.categories_demand || []}
        topIntents={metrics.top_intents || []}
        unfulfilledRequests={metrics.unfulfilled_requests || []}
      />

      {/* 3. PRODUCT PERFORMANCE */}
      <ProductPerformance
        topProducts={metrics.top_products || []}
        highDemandLowConv={metrics.high_demand_low_conversion || []}
      />

      {/* 4. AI GROWTH ACTIONS */}
      <AIGrowthActions actions={metrics.ai_growth_actions || []} />

      {/* Minimal Footer */}
      <div className="pt-4 border-t border-slate-200 flex items-center justify-between text-[11px] font-mono text-slate-400">
        <div className="flex items-center gap-2">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span>
          <span>RazorFlow AI Merchant Growth Engine</span>
        </div>
        <span>DEMAND → PERFORMANCE → ACTION</span>
      </div>

    </div>
  );
}
