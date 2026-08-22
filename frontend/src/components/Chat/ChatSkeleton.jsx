import React from 'react';
import { Bot, Sparkles } from 'lucide-react';

export default function ChatSkeleton() {
  return (
    <div className="flex gap-4 items-start animate-in fade-in duration-300">
      <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-blue-600 via-indigo-500 to-cyan-400 p-[1.5px] shadow-lg shadow-blue-500/20 flex-shrink-0">
        <div className="w-full h-full bg-slate-950 rounded-[10px] flex items-center justify-center">
          <Bot className="w-5 h-5 text-cyan-400 animate-pulse" />
        </div>
      </div>

      <div className="flex-1 max-w-xl space-y-3">
        {/* Status pill */}
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-500/10 border border-blue-500/20 text-xs font-mono text-cyan-400">
          <Sparkles className="w-3.5 h-3.5 animate-spin" />
          <span>Evaluating catalog, specs & budget guardrails...</span>
        </div>

        {/* Skeleton Card 1 */}
        <div className="p-4 rounded-2xl bg-slate-900/80 border border-slate-800 space-y-3">
          <div className="h-4 w-3/4 rounded bg-slate-800 animate-shimmer"></div>
          <div className="h-3 w-5/6 rounded bg-slate-800/60 animate-shimmer"></div>
          
          <div className="flex gap-2 pt-2">
            <div className="h-6 w-20 rounded-md bg-slate-800 animate-shimmer"></div>
            <div className="h-6 w-24 rounded-md bg-slate-800 animate-shimmer"></div>
            <div className="h-6 w-16 rounded-md bg-slate-800 animate-shimmer"></div>
          </div>
        </div>

        {/* Skeleton Card 2 */}
        <div className="p-4 rounded-2xl bg-slate-900/80 border border-slate-800 space-y-3">
          <div className="h-4 w-2/3 rounded bg-slate-800 animate-shimmer"></div>
          <div className="h-3 w-4/5 rounded bg-slate-800/60 animate-shimmer"></div>
        </div>
      </div>
    </div>
  );
}
