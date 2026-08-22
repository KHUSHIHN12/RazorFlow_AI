import React, { useState } from 'react';
import { Sparkles, Zap, CheckCircle2, ArrowUpRight, Tag } from 'lucide-react';
import { api } from '../../services/api';

export default function CampaignCard({ campaign, onRefresh }) {
  const [isLaunching, setIsLaunching] = useState(false);

  const handleLaunch = async () => {
    setIsLaunching(true);
    try {
      await api.launchCampaign(campaign.id);
      if (onRefresh) onRefresh();
    } catch (ex) {
      console.error('Launch campaign error:', ex);
    } finally {
      setIsLaunching(false);
    }
  };

  const isActive = campaign.status === 'Active';

  return (
    <div className={`p-5 rounded-2xl bg-slate-950/70 border backdrop-blur-xl transition-all duration-300 ${
      isActive ? 'border-emerald-500/40 shadow-xl shadow-emerald-500/10' : 'border-slate-800 hover:border-purple-500/40'
    }`}>
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-purple-600 to-blue-500 flex items-center justify-center text-white shadow-md">
            <Sparkles className="w-5 h-5" />
          </div>
          <div>
            <h4 className="text-base font-bold text-slate-100">{campaign.title}</h4>
            <span className="text-xs text-slate-400 font-mono flex items-center gap-1 mt-0.5">
              <Tag className="w-3.5 h-3.5 text-cyan-400" /> Discount: {campaign.discount_percent}% OFF
            </span>
          </div>
        </div>

        <span className={`px-3 py-1 rounded-full text-xs font-mono font-bold flex items-center gap-1.5 ${
          isActive
            ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30'
            : 'bg-purple-500/10 text-purple-400 border border-purple-500/30'
        }`}>
          {isActive ? <CheckCircle2 className="w-3.5 h-3.5" /> : <Sparkles className="w-3.5 h-3.5" />}
          {campaign.status}
        </span>
      </div>

      {/* Bundle items list */}
      <div className="mt-4 pt-3 border-t border-slate-800/80">
        <span className="text-xs text-slate-400 font-mono">Bundle Items:</span>
        <div className="flex flex-wrap gap-1.5 mt-1.5">
          {campaign.bundle_items.map((item, idx) => (
            <span key={idx} className="px-2.5 py-1 rounded-lg bg-slate-900 border border-slate-800 text-slate-200 text-xs font-medium">
              {item}
            </span>
          ))}
        </div>
      </div>

      {/* Projected Conversion Lift & Launch Action */}
      <div className="mt-4 pt-3 border-t border-slate-800/80 flex items-center justify-between">
        <div className="flex items-center gap-1 text-xs font-mono text-emerald-400 font-semibold">
          <ArrowUpRight className="w-4 h-4" />
          <span>Projected Lift: {campaign.projected_conversion_lift}</span>
        </div>

        {!isActive && (
          <button
            onClick={handleLaunch}
            disabled={isLaunching}
            className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-gradient-to-r from-purple-600 via-blue-600 to-cyan-600 hover:from-purple-500 hover:to-cyan-500 text-white font-bold text-xs shadow-lg shadow-purple-600/20 transition-all duration-200 active:scale-95 disabled:opacity-50"
          >
            <Zap className="w-3.5 h-3.5 fill-white" />
            <span>{isLaunching ? 'Launching...' : 'Launch Bundle Campaign'}</span>
          </button>
        )}
      </div>
    </div>
  );
}
