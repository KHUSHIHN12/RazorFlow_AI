import React from 'react';
import { ShoppingBag, Zap, Menu } from 'lucide-react';
import { useCart } from '../context/CartContext';

export default function Navbar({ onMenuClick }) {
  const { itemCount, setIsCartOpen } = useCart();

  return (
    <header className="sticky top-0 z-30 w-full border-b border-slate-200 bg-white/95 backdrop-blur-xs shadow-2xs">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        
        {/* Left Section: Mobile Menu Trigger & Title */}
        <div className="flex items-center gap-3">
          <button
            onClick={onMenuClick}
            className="p-2 rounded-xl text-slate-600 hover:text-slate-900 hover:bg-slate-100 border border-slate-200 md:hidden transition-colors"
            title="Open Menu"
          >
            <Menu className="w-5 h-5" />
          </button>

          <div className="flex items-center gap-2.5">
            <span className="font-extrabold text-base sm:text-lg tracking-tight text-slate-900">
              RazorFlow <span className="text-blue-600 font-black">AI</span>
            </span>
            <span className="hidden sm:inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[10px] font-mono font-bold bg-blue-50 text-blue-700 border border-blue-200">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span>
              Online
            </span>
          </div>
        </div>

        {/* Right Section: Razorpay Tag & Cart Button */}
        <div className="flex items-center gap-3">
          <span className="hidden md:inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-slate-100 border border-slate-200 text-[11px] font-mono font-semibold text-slate-700">
            <Zap className="w-3.5 h-3.5 text-blue-600 fill-blue-600/20" /> Razorpay Test Mode
          </span>

          <button
            onClick={() => setIsCartOpen(true)}
            className="relative flex items-center gap-2 px-3.5 py-2 rounded-xl bg-slate-100 hover:bg-slate-200/80 border border-slate-200 text-slate-800 text-sm font-semibold transition-all duration-200 active:scale-95 group shadow-2xs"
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
