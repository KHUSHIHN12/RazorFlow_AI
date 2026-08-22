import React from 'react';
import { TrendingUp, Users, ShoppingBag, DollarSign, ArrowUpRight } from 'lucide-react';

export default function KeyMetrics({ metrics }) {
  const cards = [
    {
      title: 'Total Settled Revenue',
      value: `₹${(metrics.total_revenue_inr || 0).toLocaleString('en-IN')}`,
      subtext: 'Razorpay Test API Settlements',
      icon: DollarSign,
      color: 'from-emerald-500/20 via-slate-900 to-slate-900',
      borderColor: 'border-emerald-500/30 hover:border-emerald-500/50',
      textColor: 'text-emerald-400',
      glow: 'group-hover:shadow-emerald-500/10'
    },
    {
      title: 'Agent Conversion Rate',
      value: `${metrics.conversion_rate || 0}%`,
      subtext: '+4.2% vs standard checkout',
      icon: TrendingUp,
      color: 'from-blue-500/20 via-slate-900 to-slate-900',
      borderColor: 'border-blue-500/30 hover:border-blue-500/50',
      textColor: 'text-blue-400',
      glow: 'group-hover:shadow-blue-500/10'
    },
    {
      title: 'Successful Checkouts',
      value: metrics.successful_checkouts || 0,
      subtext: 'Completed agent orders',
      icon: ShoppingBag,
      color: 'from-purple-500/20 via-slate-900 to-slate-900',
      borderColor: 'border-purple-500/30 hover:border-purple-500/50',
      textColor: 'text-purple-400',
      glow: 'group-hover:shadow-purple-500/10'
    },
    {
      title: 'LangGraph Chat Sessions',
      value: metrics.total_sessions || 0,
      subtext: 'Stateful sessions logged',
      icon: Users,
      color: 'from-cyan-500/20 via-slate-900 to-slate-900',
      borderColor: 'border-cyan-500/30 hover:border-cyan-500/50',
      textColor: 'text-cyan-400',
      glow: 'group-hover:shadow-cyan-500/10'
    }
  ];

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
      {cards.map((card, idx) => {
        const Icon = card.icon;
        return (
          <div
            key={idx}
            className={`p-6 rounded-2xl bg-gradient-to-br ${card.color} border ${card.borderColor} backdrop-blur-xl shadow-xl relative overflow-hidden group hover:-translate-y-1 transition-all duration-300 ${card.glow}`}
          >
            <div className="flex items-center justify-between">
              <span className="text-xs font-mono font-bold uppercase tracking-wider text-slate-400">
                {card.title}
              </span>
              <div className={`p-2.5 rounded-xl bg-slate-950/80 border border-slate-800 ${card.textColor} group-hover:scale-110 transition-transform duration-300`}>
                <Icon className="w-5 h-5" />
              </div>
            </div>

            <div className="mt-4">
              <h3 className="text-2xl sm:text-3xl font-black text-white font-mono tracking-tight">
                {card.value}
              </h3>
              <p className="text-xs text-slate-400 mt-1.5 flex items-center gap-1 font-mono">
                <ArrowUpRight className="w-3.5 h-3.5 text-emerald-400 inline" />
                {card.subtext}
              </p>
            </div>
          </div>
        );
      })}
    </div>
  );
}
