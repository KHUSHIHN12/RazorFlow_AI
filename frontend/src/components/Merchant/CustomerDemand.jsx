import React from 'react';
import { Search, Flame, AlertCircle } from 'lucide-react';

export default function CustomerDemand({ categoriesDemand = [], topIntents = [], unfulfilledRequests = [] }) {
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h2 className="text-xs font-mono font-bold uppercase tracking-wider text-slate-500">
          2. CUSTOMER DEMAND
        </h2>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
        {/* Top Searched Categories */}
        <div className="p-5 rounded-2xl bg-white border border-slate-200 shadow-2xs space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2">
              <Search className="w-4 h-4 text-blue-600" />
              Top Searched Categories
            </h3>
            <span className="text-xs text-slate-500 font-mono">Volume</span>
          </div>

          <div className="space-y-3">
            {categoriesDemand.map((cat, idx) => (
              <div key={idx} className="space-y-1">
                <div className="flex justify-between text-xs font-medium text-slate-700">
                  <span>{cat.category}</span>
                  <span className="font-mono text-slate-500">{cat.percentage}% ({cat.search_count})</span>
                </div>
                <div className="w-full bg-slate-100 rounded-full h-2 overflow-hidden">
                  <div
                    className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${cat.percentage}%` }}
                  ></div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Trending Customer Intents */}
        <div className="p-5 rounded-2xl bg-white border border-slate-200 shadow-2xs space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2">
              <Flame className="w-4 h-4 text-amber-500" />
              Trending Customer Intents
            </h3>
            <span className="text-xs text-slate-500 font-mono">Query Count</span>
          </div>

          <div className="space-y-2">
            {topIntents.slice(0, 5).map((intent, idx) => (
              <div
                key={idx}
                className="flex items-center justify-between p-2.5 rounded-xl bg-slate-50 border border-slate-100 hover:bg-slate-100/80 transition-colors"
              >
                <span className="text-xs font-medium text-slate-800 capitalize truncate max-w-[200px]">
                  "{intent.keyword}"
                </span>
                <span className="px-2 py-0.5 rounded-full text-xs font-mono font-bold bg-amber-50 text-amber-700 border border-amber-200">
                  {intent.count}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Unfulfilled Product Requests */}
        <div className="p-5 rounded-2xl bg-white border border-slate-200 shadow-2xs space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2">
              <AlertCircle className="w-4 h-4 text-rose-500" />
              Unfulfilled Requests
            </h3>
            <span className="text-xs text-slate-500 font-mono">Opportunity</span>
          </div>

          <div className="space-y-2.5">
            {unfulfilledRequests.map((req, idx) => (
              <div
                key={idx}
                className="p-2.5 rounded-xl bg-rose-50/50 border border-rose-100 flex items-center justify-between"
              >
                <div>
                  <div className="text-xs font-semibold text-slate-900">{req.query}</div>
                  <div className="text-[11px] text-rose-600 font-medium">{req.reason}</div>
                </div>
                <span className="px-2 py-0.5 rounded-full text-xs font-mono font-bold bg-rose-100 text-rose-700">
                  {req.count} missed
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
