import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { ShoppingBag, Bot, BarChart3, Zap, ShieldCheck } from 'lucide-react';
import { useCart } from '../context/CartContext';

export default function Navbar() {
  const location = useLocation();
  const { itemCount, setIsCartOpen } = useCart();
  const isMerchant = location.pathname === '/merchant';

  return (
    <header className="sticky top-0 z-40 w-full border-b border-slate-800/80 bg-slate-950/85 backdrop-blur-xl">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        
        {/* Brand & Track Badge */}
        <div className="flex items-center gap-3">
          <Link to="/" className="flex items-center gap-3 group">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-blue-600 via-indigo-500 to-cyan-400 p-[1.5px] shadow-lg shadow-blue-500/20 group-hover:scale-105 group-hover:shadow-cyan-500/30 transition-all duration-300">
              <div className="w-full h-full bg-slate-950 rounded-[10px] flex items-center justify-center">
                <Zap className="w-5 h-5 text-cyan-400 fill-cyan-400/20 group-hover:rotate-12 transition-transform duration-300" />
              </div>
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-extrabold text-lg tracking-tight bg-gradient-to-r from-white via-slate-100 to-cyan-300 bg-clip-text text-transparent">
                  RazorFlow <span className="text-cyan-400 font-black">AI</span>
                </span>
                <span className="text-[10px] uppercase font-mono font-extrabold tracking-wider px-2.5 py-0.5 rounded-full bg-blue-500/10 border border-blue-500/30 text-cyan-300 shadow-sm">
                  Agentic Commerce
                </span>
              </div>
              <p className="text-[11px] text-slate-400 font-mono flex items-center gap-1 mt-0.5">
                <ShieldCheck className="w-3.5 h-3.5 text-emerald-400 inline" /> Razorpay AI Buildathon • Track 1
              </p>
            </div>
          </Link>
        </div>

        {/* Center Route Navigation Tabs */}
        <nav className="flex items-center p-1 bg-slate-900/90 rounded-xl border border-slate-800 text-sm font-medium shadow-inner">
          <Link
            to="/"
            className={`flex items-center gap-2 px-4 py-1.5 rounded-lg transition-all duration-300 ${
              !isMerchant
                ? 'bg-gradient-to-r from-blue-600 to-cyan-600 text-white shadow-md shadow-blue-600/30 font-semibold scale-100'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
            }`}
          >
            <Bot className="w-4 h-4" />
            <span>Agent Chat</span>
          </Link>
          <Link
            to="/merchant"
            className={`flex items-center gap-2 px-4 py-1.5 rounded-lg transition-all duration-300 ${
              isMerchant
                ? 'bg-gradient-to-r from-blue-600 to-cyan-600 text-white shadow-md shadow-blue-600/30 font-semibold scale-100'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
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
            className="relative flex items-center gap-2.5 px-4 py-2 rounded-xl bg-slate-900/90 hover:bg-slate-800 border border-slate-700/80 hover:border-cyan-500/40 text-slate-200 text-sm font-semibold transition-all duration-300 hover:shadow-lg hover:shadow-cyan-500/10 active:scale-95 group"
          >
            <ShoppingBag className="w-4 h-4 text-cyan-400 group-hover:scale-110 transition-transform duration-300" />
            <span className="hidden sm:inline">Cart</span>
            {itemCount > 0 && (
              <span className="flex items-center justify-center min-w-[20px] h-5 px-1.5 rounded-full bg-blue-600 text-white text-[11px] font-mono font-bold shadow-md shadow-blue-600/50 animate-pulse">
                {itemCount}
              </span>
            )}
          </button>
        </div>

      </div>
    </header>
  );
}
