import React from 'react';
import { Bot, Sparkles } from 'lucide-react';

export default function ChatSkeleton() {
  return (
    <div className="flex gap-4 items-start animate-in fade-in duration-300">
      <div className="w-9 h-9 rounded-xl bg-blue-600 flex items-center justify-center text-white shadow-xs flex-shrink-0">
        <Bot className="w-5 h-5 animate-pulse" />
      </div>

      <div className="flex-1 max-w-xl space-y-3">
        {/* Status pill */}
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-50 border border-blue-200 text-xs font-mono text-blue-700">
          <Sparkles className="w-3.5 h-3.5 animate-spin" />
          <span>Evaluating catalog, specs & budget guardrails...</span>
        </div>

        {/* Skeleton Card 1 */}
        <div className="p-4 rounded-2xl bg-white border border-slate-200 shadow-2xs space-y-3">
          <div className="h-4 w-3/4 rounded bg-slate-200 animate-shimmer"></div>
          <div className="h-3 w-5/6 rounded bg-slate-100 animate-shimmer"></div>
          
          <div className="flex gap-2 pt-2">
            <div className="h-6 w-20 rounded-md bg-slate-100 animate-shimmer"></div>
            <div className="h-6 w-24 rounded-md bg-slate-100 animate-shimmer"></div>
            <div className="h-6 w-16 rounded-md bg-slate-100 animate-shimmer"></div>
          </div>
        </div>

        {/* Skeleton Card 2 */}
        <div className="p-4 rounded-2xl bg-white border border-slate-200 shadow-2xs space-y-3">
          <div className="h-4 w-2/3 rounded bg-slate-200 animate-shimmer"></div>
          <div className="h-3 w-4/5 rounded bg-slate-100 animate-shimmer"></div>
        </div>
      </div>
    </div>
  );
}
