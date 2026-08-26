import React from 'react';
import { User, ShieldCheck, Zap, CreditCard, Sparkles, CheckCircle2 } from 'lucide-react';
import { useCart } from '../../context/CartContext';

export default function ProfileView() {
  const { cart, selectedCartItems } = useCart();

  return (
    <div className="max-w-4xl mx-auto px-4 py-8 space-y-6">
      
      {/* Profile Header Card */}
      <div className="p-6 rounded-2xl bg-white border border-slate-200 shadow-xs flex flex-col sm:flex-row items-center gap-5">
        <div className="w-16 h-16 rounded-2xl bg-gradient-to-tr from-blue-700 to-indigo-600 flex items-center justify-center text-white text-xl font-bold shadow-md shadow-blue-600/20">
          DC
        </div>
        <div className="text-center sm:text-left flex-1 space-y-1">
          <div className="flex items-center justify-center sm:justify-start gap-2">
            <h2 className="text-xl font-extrabold text-slate-900">Demo Customer</h2>
            <span className="px-2.5 py-0.5 rounded-full text-[11px] font-mono font-bold bg-blue-50 text-blue-700 border border-blue-200">
              Verified Shopper
            </span>
          </div>
          <p className="text-xs text-slate-500 font-mono">customer@razorflow.ai • ID: usr_2026_demo</p>
        </div>
      </div>

      {/* Account Settings & AI Shopping Preferences */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        
        {/* Shopping Preferences */}
        <div className="p-5 rounded-2xl bg-white border border-slate-200 shadow-xs space-y-4">
          <div className="flex items-center gap-2 border-b border-slate-100 pb-3">
            <Sparkles className="w-4 h-4 text-blue-600" />
            <h3 className="text-sm font-extrabold text-slate-900">AI Agent Preferences</h3>
          </div>
          
          <div className="space-y-3 text-xs">
            <div className="flex items-center justify-between p-3 rounded-xl bg-slate-50 border border-slate-100">
              <span className="text-slate-600 font-medium">Budget Discovery Engine</span>
              <span className="text-emerald-600 font-bold flex items-center gap-1">
                <CheckCircle2 className="w-3.5 h-3.5" /> Active
              </span>
            </div>
            
            <div className="flex items-center justify-between p-3 rounded-xl bg-slate-50 border border-slate-100">
              <span className="text-slate-600 font-medium">Category Constraint Locking</span>
              <span className="text-emerald-600 font-bold flex items-center gap-1">
                <CheckCircle2 className="w-3.5 h-3.5" /> Enforced
              </span>
            </div>

            <div className="flex items-center justify-between p-3 rounded-xl bg-slate-50 border border-slate-100">
              <span className="text-slate-600 font-medium">Preferred Currency</span>
              <span className="font-mono font-bold text-slate-900">INR (₹)</span>
            </div>
          </div>
        </div>

        {/* Integration Status */}
        <div className="p-5 rounded-2xl bg-white border border-slate-200 shadow-xs space-y-4">
          <div className="flex items-center gap-2 border-b border-slate-100 pb-3">
            <CreditCard className="w-4 h-4 text-blue-600" />
            <h3 className="text-sm font-extrabold text-slate-900">Checkout & Payment Status</h3>
          </div>

          <div className="space-y-3 text-xs">
            <div className="flex items-center justify-between p-3 rounded-xl bg-slate-50 border border-slate-100">
              <span className="text-slate-600 font-medium">Payment Gateway</span>
              <span className="font-mono font-bold text-blue-600 flex items-center gap-1">
                <Zap className="w-3.5 h-3.5" /> Razorpay Test Mode
              </span>
            </div>

            <div className="flex items-center justify-between p-3 rounded-xl bg-slate-50 border border-slate-100">
              <span className="text-slate-600 font-medium">Buying List Selection</span>
              <span className="font-mono font-bold text-slate-900">
                {selectedCartItems.length} of {cart.length} items
              </span>
            </div>

            <div className="flex items-center justify-between p-3 rounded-xl bg-slate-50 border border-slate-100">
              <span className="text-slate-600 font-medium">Payment Guardrail</span>
              <span className="text-emerald-600 font-bold flex items-center gap-1">
                <ShieldCheck className="w-3.5 h-3.5" /> Enabled
              </span>
            </div>
          </div>
        </div>

      </div>

    </div>
  );
}
