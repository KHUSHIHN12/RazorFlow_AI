import React from 'react';
import { Search, Flame } from 'lucide-react';

export default function IntentChart({ intents = [] }) {
  const maxCount = Math.max(...intents.map(i => i.count), 1);

  return (
    <div className="p-6 rounded-2xl bg-slate-900/90 border border-slate-800/90 backdrop-blur-xl shadow-xl space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-base font-bold text-slate-100 flex items-center gap-2">
            <Search className="w-5 h-5 text-cyan-400" />
            Top Customer Search Intent Keywords
          </h3>
          <p className="text-xs text-slate-400 mt-1">
            Real-time intent extraction from natural language buyer queries
          </p>
        </div>
        <span className="flex items-center gap-1.5 text-xs font-mono font-bold text-amber-400 bg-amber-500/10 px-3 py-1 rounded-full border border-amber-500/30 shadow-sm">
          <Flame className="w-3.5 h-3.5 fill-amber-400" /> Live Signals
        </span>
      </div>

      <div className="space-y-4.5">
        {intents.map((item, idx) => {
          const percent = Math.round((item.count / maxCount) * 100);
          return (
            <div key={idx} className="space-y-2">
              <div className="flex items-center justify-between text-xs font-medium">
                <span className="text-slate-200 font-mono capitalize flex items-center gap-2.5">
                  <span className="w-5 h-5 rounded-md bg-slate-950 border border-slate-800 flex items-center justify-center text-[10px] text-slate-400 font-bold">
                    {idx + 1}
                  </span>
                  "{item.keyword}"
                </span>
                <span className="text-cyan-400 font-mono font-bold">
                  {item.count} queries
                </span>
              </div>

              {/* Multi-Stop Gradient Progress Bar */}
              <div className="w-full h-3 rounded-full bg-slate-950 border border-slate-800/80 p-0.5 overflow-hidden">
                <div
                  className="h-full rounded-full bg-gradient-to-r from-blue-600 via-cyan-500 to-emerald-400 transition-all duration-700 ease-out shadow-sm"
                  style={{ width: `${percent}%` }}
                />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
