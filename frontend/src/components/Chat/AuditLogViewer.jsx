import React, { useState } from 'react';
import { Terminal, ChevronDown, ChevronUp, Cpu, ShieldAlert, Sparkles, CheckCircle } from 'lucide-react';

export default function AuditLogViewer({ auditLogs }) {
  const [isOpen, setIsOpen] = useState(false);

  if (!auditLogs || auditLogs.length === 0) return null;

  const getStepIcon = (step) => {
    if (step.includes('GUARDRAIL')) return <ShieldAlert className="w-3.5 h-3.5 text-blue-600" />;
    if (step.includes('RANKING') || step.includes('INTENT')) return <Sparkles className="w-3.5 h-3.5 text-purple-600" />;
    if (step.includes('CART') || step.includes('BUNDLE')) return <CheckCircle className="w-3.5 h-3.5 text-emerald-600" />;
    return <Cpu className="w-3.5 h-3.5 text-slate-500" />;
  };

  return (
    <div className="mt-3.5 rounded-xl border border-slate-200 bg-slate-900/95 text-slate-200 overflow-hidden text-xs font-mono shadow-sm">
      
      {/* Toggle Header */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full px-3.5 py-2.5 bg-slate-900 hover:bg-slate-850 flex items-center justify-between transition-colors border-b border-slate-800"
      >
        <div className="flex items-center gap-2 text-slate-300">
          <Terminal className="w-4 h-4 text-emerald-400" />
          <span className="font-bold tracking-wide">Agent Reasoning & Audit Trail</span>
          <span className="px-2 py-0.5 rounded-full bg-slate-800 text-slate-400 text-[10px]">
            {auditLogs.length} steps logged
          </span>
        </div>
        
        <div className="flex items-center gap-1.5 text-slate-400">
          <span className="text-[11px] font-sans">{isOpen ? 'Hide Trace' : 'View Trace'}</span>
          {isOpen ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
        </div>
      </button>

      {/* Log Feed */}
      {isOpen && (
        <div className="p-3.5 space-y-2 max-h-60 overflow-y-auto bg-slate-950/80 text-[11px] font-mono leading-relaxed">
          {auditLogs.map((log, idx) => (
            <div key={idx} className="flex items-start gap-2 py-1 border-b border-slate-800/60 last:border-0">
              <span className="text-slate-500 text-[10px] whitespace-nowrap mt-0.5">{log.timestamp}</span>
              <div className="mt-0.5">{getStepIcon(log.step)}</div>
              <div className="flex-1">
                <span className="font-bold uppercase tracking-wider text-emerald-400 mr-2">[{log.step}]</span>
                <span className="text-slate-300">{log.details}</span>
              </div>
            </div>
          ))}
        </div>
      )}

    </div>
  );
}
