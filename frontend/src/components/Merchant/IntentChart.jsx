import React from 'react';
import { Search, Flame } from 'lucide-react';

export default function IntentChart({ intents = [] }) {
  const maxCount = Math.max(...intents.map(i => i.count), 1);

  return (
    <div className="p-6 rounded-2xl bg-white border border-slate-200 shadow-2xs space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-base font-bold text-slate-900 flex items-center gap-2">
            <Search className="w-5 h-5 text-blue-600" />
            Top Customer Search Intent Keywords
          </h3>
          <p className="text-xs text-slate-500 mt-1">
            Real-time intent extraction from natural language buyer queries
          </p>
        </div>
        <span className="flex items-center gap-1.5 text-xs font-mono font-bold text-amber-700 bg-amber-50 px-3 py-1 rounded-full border border-amber-200 shadow-2xs">
          <Flame className="w-3.5 h-3.5 fill-amber-500 text-amber-500" /> Live Signals
        </span>
      </div>

      <div className="space-y-4.5">
        {intents.map((item, idx) => {
          const percent = Math.round((item.count / maxCount) * 100);
          return (
            <div key={idx} className="space-y-2">
              <div className="flex items-center justify-between text-xs font-medium">
                <span className="text-slate-800 font-mono capitalize flex items-center gap-2.5">
                  <span className="w-5 h-5 rounded-md bg-slate-100 border border-slate-200 flex items-center justify-center text-[10px] text-slate-500 font-bold">
                    {idx + 1}
                  </span>
                  "{item.keyword}"
                </span>
                <span className="text-blue-700 font-mono font-bold">
                  {item.count} queries
                </span>
              </div>

              {/* Progress Bar */}
              <div className="w-full h-3 rounded-full bg-slate-100 border border-slate-200/80 p-0.5 overflow-hidden">
                <div
                  className="h-full rounded-full bg-gradient-to-r from-blue-700 via-blue-600 to-indigo-500 transition-all duration-700 ease-out shadow-2xs"
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
