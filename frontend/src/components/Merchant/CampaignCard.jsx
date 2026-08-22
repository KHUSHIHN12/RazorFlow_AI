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
    <div className={`p-5 rounded-2xl bg-white border transition-all duration-200 ${
      isActive ? 'border-emerald-300 shadow-xs' : 'border-slate-200 hover:border-blue-300'
    }`}>
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-purple-50 border border-purple-200 flex items-center justify-center text-purple-700 shadow-2xs">
            <Sparkles className="w-5 h-5" />
          </div>
          <div>
            <h4 className="text-base font-bold text-slate-900">{campaign.title}</h4>
            <span className="text-xs text-slate-500 font-mono flex items-center gap-1 mt-0.5">
              <Tag className="w-3.5 h-3.5 text-blue-600" /> Discount: {campaign.discount_percent}% OFF
            </span>
          </div>
        </div>

        <span className={`px-3 py-1 rounded-full text-xs font-mono font-bold flex items-center gap-1.5 ${
          isActive
            ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
            : 'bg-purple-50 text-purple-700 border border-purple-200'
        }`}>
          {isActive ? <CheckCircle2 className="w-3.5 h-3.5" /> : <Sparkles className="w-3.5 h-3.5" />}
          {campaign.status}
        </span>
      </div>

      {/* Bundle items list */}
      <div className="mt-4 pt-3 border-t border-slate-100">
        <span className="text-xs text-slate-500 font-mono">Bundle Items:</span>
        <div className="flex flex-wrap gap-1.5 mt-1.5">
          {campaign.bundle_items.map((item, idx) => (
            <span key={idx} className="px-2.5 py-1 rounded-lg bg-slate-100 border border-slate-200 text-slate-800 text-xs font-medium">
              {item}
            </span>
          ))}
        </div>
      </div>

      {/* Projected Conversion Lift & Launch Action */}
      <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between">
        <div className="flex items-center gap-1 text-xs font-mono text-emerald-700 font-semibold">
          <ArrowUpRight className="w-4 h-4" />
          <span>Projected Lift: {campaign.projected_conversion_lift}</span>
        </div>

        {!isActive && (
          <button
            onClick={handleLaunch}
            disabled={isLaunching}
            className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-bold text-xs shadow-xs transition-all duration-200 active:scale-95 disabled:opacity-50"
          >
            <Zap className="w-3.5 h-3.5 fill-white" />
            <span>{isLaunching ? 'Launching...' : 'Launch Bundle Campaign'}</span>
          </button>
        )}
      </div>
    </div>
  );
}
