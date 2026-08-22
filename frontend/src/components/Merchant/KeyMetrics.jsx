import React from 'react';
import { TrendingUp, Users, ShoppingBag, DollarSign, ArrowUpRight } from 'lucide-react';

export default function KeyMetrics({ metrics }) {
  const cards = [
    {
      title: 'Total Settled Revenue',
      value: `₹${(metrics.total_revenue_inr || 0).toLocaleString('en-IN')}`,
      subtext: 'Razorpay Test API Settlements',
      icon: DollarSign,
      color: 'bg-emerald-50/60 border-emerald-200',
      textColor: 'text-emerald-700',
      iconBg: 'bg-emerald-100 text-emerald-700'
    },
    {
      title: 'Agent Conversion Rate',
      value: `${metrics.conversion_rate || 0}%`,
      subtext: '+4.2% vs standard checkout',
      icon: TrendingUp,
      color: 'bg-blue-50/60 border-blue-200',
      textColor: 'text-blue-700',
      iconBg: 'bg-blue-100 text-blue-700'
    },
    {
      title: 'Successful Checkouts',
      value: metrics.successful_checkouts || 0,
      subtext: 'Completed agent orders',
      icon: ShoppingBag,
      color: 'bg-purple-50/60 border-purple-200',
      textColor: 'text-purple-700',
      iconBg: 'bg-purple-100 text-purple-700'
    },
    {
      title: 'LangGraph Chat Sessions',
      value: metrics.total_sessions || 0,
      subtext: 'Stateful sessions logged',
      icon: Users,
      color: 'bg-cyan-50/60 border-cyan-200',
      textColor: 'text-cyan-800',
      iconBg: 'bg-cyan-100 text-cyan-800'
    }
  ];

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
      {cards.map((card, idx) => {
        const Icon = card.icon;
        return (
          <div
            key={idx}
            className={`p-6 rounded-2xl bg-white border ${card.color} shadow-2xs relative overflow-hidden group hover:-translate-y-0.5 transition-all duration-200`}
          >
            <div className="flex items-center justify-between">
              <span className="text-xs font-mono font-bold uppercase tracking-wider text-slate-500">
                {card.title}
              </span>
              <div className={`p-2.5 rounded-xl ${card.iconBg} group-hover:scale-105 transition-transform duration-200`}>
                <Icon className="w-5 h-5" />
              </div>
            </div>

            <div className="mt-4">
              <h3 className="text-2xl sm:text-3xl font-extrabold text-slate-900 font-mono tracking-tight">
                {card.value}
              </h3>
              <p className="text-xs text-slate-500 mt-1.5 flex items-center gap-1 font-mono">
                <ArrowUpRight className="w-3.5 h-3.5 text-emerald-600 inline" />
                {card.subtext}
              </p>
            </div>
          </div>
        );
      })}
    </div>
  );
}
