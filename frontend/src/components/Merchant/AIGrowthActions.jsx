import React from 'react';
import { Sparkles, ArrowRight, Zap } from 'lucide-react';

export default function AIGrowthActions({ actions = [] }) {
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h2 className="text-xs font-mono font-bold uppercase tracking-wider text-slate-500">
          4. AI GROWTH ACTIONS
        </h2>
        <span className="text-xs text-purple-700 font-mono font-bold bg-purple-50 px-2.5 py-0.5 rounded-full border border-purple-200">
          3 Concise Recommendations
        </span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        {actions.slice(0, 3).map((act, idx) => (
          <div
            key={idx}
            className="p-5 rounded-2xl bg-white border border-purple-200/80 shadow-2xs space-y-3 relative overflow-hidden group hover:border-purple-300 transition-all"
          >
            {/* Header Icon */}
            <div className="flex items-center justify-between">
              <span className="text-xs font-mono font-bold text-purple-600 bg-purple-50 px-2 py-0.5 rounded border border-purple-100">
                Action #{idx + 1}
              </span>
              <Sparkles className="w-4 h-4 text-purple-600" />
            </div>

            {/* Insight */}
            <div className="space-y-1">
              <div className="text-[11px] font-mono uppercase text-slate-400 font-bold">Insight</div>
              <p className="text-xs font-semibold text-slate-900 leading-snug">
                "{act.insight}"
              </p>
            </div>

            {/* Recommended Action */}
            <div className="space-y-1 pt-1 border-t border-slate-100">
              <div className="text-[11px] font-mono uppercase text-blue-600 font-bold flex items-center gap-1">
                <ArrowRight className="w-3 h-3 text-blue-600" />
                Recommended Action
              </div>
              <p className="text-xs font-medium text-slate-800 leading-snug">
                {act.action}
              </p>
            </div>

            {/* Expected Impact */}
            <div className="space-y-1 pt-1 border-t border-slate-100">
              <div className="text-[11px] font-mono uppercase text-emerald-600 font-bold flex items-center gap-1">
                <Zap className="w-3 h-3 text-emerald-600" />
                Expected Impact
              </div>
              <div className="text-xs font-mono font-extrabold text-emerald-700 bg-emerald-50 px-2.5 py-1 rounded-lg border border-emerald-200 inline-block">
                {act.impact}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
