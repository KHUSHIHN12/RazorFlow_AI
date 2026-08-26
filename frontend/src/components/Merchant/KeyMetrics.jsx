import React from 'react';
import { TrendingUp, Users, ShoppingBag, IndianRupee, ArrowUpRight } from 'lucide-react';

export default function KeyMetrics({ metrics }) {
  const cards = [
    {
      title: 'Revenue',
      value: `₹${(metrics.total_revenue_inr || 0).toLocaleString('en-IN')}`,
      subtext: '+14.2% vs last week',
      icon: IndianRupee,
      color: 'border-emerald-200 bg-emerald-50/40',
      iconBg: 'bg-emerald-100 text-emerald-700'
    },
    {
      title: 'Orders',
      value: metrics.successful_checkouts || 0,
      subtext: 'Completed checkouts',
      icon: ShoppingBag,
      color: 'border-purple-200 bg-purple-50/40',
      iconBg: 'bg-purple-100 text-purple-700'
    },
    {
      title: 'Agent Conversion',
      value: `${metrics.conversion_rate || 0}%`,
      subtext: '+4.2% vs baseline',
      icon: TrendingUp,
      color: 'border-blue-200 bg-blue-50/40',
      iconBg: 'bg-blue-100 text-blue-700'
    },
    {
      title: 'AI Shopping Sessions',
      value: metrics.total_sessions || 0,
      subtext: 'Active chat sessions',
      icon: Users,
      color: 'border-slate-200 bg-slate-50/60',
      iconBg: 'bg-slate-200 text-slate-700'
    }
  ];

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h2 className="text-xs font-mono font-bold uppercase tracking-wider text-slate-500">
          1. KEY METRICS
        </h2>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {cards.map((card, idx) => {
          const Icon = card.icon;
          return (
            <div
              key={idx}
              className={`p-5 rounded-2xl bg-white border ${card.color} shadow-2xs transition-all duration-200`}
            >
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold text-slate-500">
                  {card.title}
                </span>
                <div className={`p-2 rounded-xl ${card.iconBg}`}>
                  <Icon className="w-4 h-4" />
                </div>
              </div>

              <div className="mt-3">
                <h3 className="text-2xl font-extrabold text-slate-900 font-mono tracking-tight">
                  {card.value}
                </h3>
                <p className="text-xs text-slate-500 mt-1 flex items-center gap-1 font-mono">
                  <ArrowUpRight className="w-3.5 h-3.5 text-emerald-600 inline" />
                  {card.subtext}
                </p>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
