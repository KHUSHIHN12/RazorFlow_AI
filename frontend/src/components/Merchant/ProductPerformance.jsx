import React from 'react';
import { Package, Star, AlertTriangle, TrendingUp } from 'lucide-react';

export default function ProductPerformance({ topProducts = [], highDemandLowConv = [] }) {
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h2 className="text-xs font-mono font-bold uppercase tracking-wider text-slate-500">
          3. PRODUCT PERFORMANCE
        </h2>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
        {/* Top Products Table */}
        <div className="lg:col-span-2 p-5 rounded-2xl bg-white border border-slate-200 shadow-2xs space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2">
              <Package className="w-4 h-4 text-emerald-600" />
              Top Products
            </h3>
            <span className="text-xs text-slate-500 font-mono">By Settled Revenue</span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-slate-100 text-[11px] font-mono font-bold uppercase text-slate-400">
                  <th className="pb-2">Product Name</th>
                  <th className="pb-2">Category</th>
                  <th className="pb-2 text-right">Price</th>
                  <th className="pb-2 text-right">Orders</th>
                  <th className="pb-2 text-right">Revenue</th>
                  <th className="pb-2 text-right">Rating</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-50 text-xs">
                {topProducts.map((prod, idx) => (
                  <tr key={idx} className="hover:bg-slate-50/80 transition-colors">
                    <td className="py-2.5 font-semibold text-slate-900">{prod.name}</td>
                    <td className="py-2.5 text-slate-500">{prod.category}</td>
                    <td className="py-2.5 text-right font-mono text-slate-700">₹{prod.price.toLocaleString('en-IN')}</td>
                    <td className="py-2.5 text-right font-mono font-bold text-purple-700">{prod.orders}</td>
                    <td className="py-2.5 text-right font-mono font-bold text-emerald-700">₹{prod.revenue.toLocaleString('en-IN')}</td>
                    <td className="py-2.5 text-right">
                      <span className="inline-flex items-center gap-0.5 font-mono text-amber-600 font-bold bg-amber-50 px-1.5 py-0.5 rounded border border-amber-200">
                        <Star className="w-3 h-3 fill-amber-400 text-amber-400" />
                        {prod.rating}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* High-Demand / Low-Conversion Products */}
        <div className="p-5 rounded-2xl bg-white border border-slate-200 shadow-2xs space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 text-amber-500" />
              High Demand / Low Conversion
            </h3>
            <span className="text-xs text-slate-500 font-mono">Friction</span>
          </div>

          <div className="space-y-3">
            {highDemandLowConv.map((item, idx) => (
              <div
                key={idx}
                className="p-3 rounded-xl bg-amber-50/40 border border-amber-200 space-y-1.5"
              >
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-slate-900 truncate max-w-[170px]">{item.name}</span>
                  <span className="text-[11px] font-mono font-bold text-amber-700">{item.conversion} conv.</span>
                </div>
                <div className="flex items-center justify-between text-[11px] text-slate-500 font-mono">
                  <span>₹{item.price.toLocaleString('en-IN')}</span>
                  <span>{item.searches} searches</span>
                </div>
                <div className="text-[11px] text-amber-800 font-medium bg-amber-100/60 px-2 py-0.5 rounded text-center">
                  Friction: {item.issue}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
