import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { ShoppingBag, Bot, BarChart3, Zap, ShieldCheck } from 'lucide-react';
import { useCart } from '../context/CartContext';

export default function Navbar() {
  const location = useLocation();
  const { itemCount, setIsCartOpen } = useCart();
  const isMerchant = location.pathname === '/merchant';

  return (
    <header className="sticky top-0 z-40 w-full border-b border-slate-200 bg-white/90 backdrop-blur-md shadow-xs">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        
        {/* Brand & Track Badge */}
        <div className="flex items-center gap-3">
          <Link to="/" className="flex items-center gap-3 group">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-blue-700 via-blue-600 to-indigo-600 p-[1.5px] shadow-md shadow-blue-600/20 group-hover:scale-105 transition-all duration-300">
              <div className="w-full h-full bg-blue-600 rounded-[10px] flex items-center justify-center text-white">
                <Zap className="w-5 h-5 fill-white/20 group-hover:rotate-12 transition-transform duration-300" />
              </div>
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-extrabold text-lg tracking-tight text-slate-900">
                  RazorFlow <span className="text-blue-600 font-black">AI</span>
                </span>
                <span className="text-[10px] uppercase font-mono font-bold tracking-wider px-2.5 py-0.5 rounded-full bg-blue-50 border border-blue-200 text-blue-700 shadow-2xs">
                  Agentic Commerce
                </span>
              </div>
              <p className="text-[11px] text-slate-500 font-mono flex items-center gap-1 mt-0.5">
                <ShieldCheck className="w-3.5 h-3.5 text-emerald-600 inline" /> Razorpay AI Buildathon • Track 1
              </p>
            </div>
          </Link>
        </div>

        {/* Center Route Navigation Tabs */}
        <nav className="flex items-center p-1 bg-slate-100 rounded-xl border border-slate-200/80 text-sm font-medium">
          <Link
            to="/"
            className={`flex items-center gap-2 px-4 py-1.5 rounded-lg transition-all duration-200 ${
              !isMerchant
                ? 'bg-blue-600 text-white shadow-sm font-semibold'
                : 'text-slate-600 hover:text-slate-900 hover:bg-slate-200/60'
            }`}
          >
            <Bot className="w-4 h-4" />
            <span>Agent Chat</span>
          </Link>
          <Link
            to="/merchant"
            className={`flex items-center gap-2 px-4 py-1.5 rounded-lg transition-all duration-200 ${
              isMerchant
                ? 'bg-blue-600 text-white shadow-sm font-semibold'
                : 'text-slate-600 hover:text-slate-900 hover:bg-slate-200/60'
            }`}
          >
            <BarChart3 className="w-4 h-4" />
            <span>Merchant Growth</span>
          </Link>
        </nav>

        {/* Right Cart Trigger Button */}
        <div className="flex items-center gap-3">
          <button
            onClick={() => setIsCartOpen(true)}
            className="relative flex items-center gap-2.5 px-4 py-2 rounded-xl bg-slate-100 hover:bg-slate-200/80 border border-slate-200 text-slate-800 text-sm font-semibold transition-all duration-200 active:scale-95 group shadow-2xs"
          >
            <ShoppingBag className="w-4 h-4 text-blue-600 group-hover:scale-110 transition-transform duration-200" />
            <span className="hidden sm:inline">Cart</span>
            {itemCount > 0 && (
              <span className="flex items-center justify-center min-w-[20px] h-5 px-1.5 rounded-full bg-blue-600 text-white text-[11px] font-mono font-bold shadow-xs">
                {itemCount}
              </span>
            )}
          </button>
        </div>

      </div>
    </header>
  );
}
