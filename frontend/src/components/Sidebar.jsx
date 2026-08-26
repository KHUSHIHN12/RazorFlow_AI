import React from 'react';
import { Bot, ShoppingBag, User, Zap, X } from 'lucide-react';
import { useCart } from '../context/CartContext';

export default function Sidebar({ activeTab, setActiveTab, isOpen, setIsOpen }) {
  const { itemCount, setIsCartOpen } = useCart();

  const handleNav = (tab) => {
    if (tab === 'cart') {
      setIsCartOpen(true);
    } else {
      setActiveTab(tab);
    }
    if (setIsOpen) setIsOpen(false);
  };

  return (
    <>
      {/* Mobile Backdrop Overlay */}
      {isOpen && (
        <div
          onClick={() => setIsOpen(false)}
          className="fixed inset-0 bg-slate-900/40 backdrop-blur-xs z-40 md:hidden transition-opacity"
        />
      )}

      {/* Sidebar Container */}
      <aside
        className={`fixed md:static top-0 left-0 z-50 h-full w-64 bg-white border-r border-slate-200 flex flex-col justify-between transition-transform duration-300 ease-in-out shadow-xs ${
          isOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'
        }`}
      >
        {/* Top Section: Brand & Navigation */}
        <div className="p-4 space-y-6">
          
          {/* Logo / Header */}
          <div className="flex items-center justify-between px-2 pt-1">
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-xl bg-blue-600 flex items-center justify-center text-white shadow-xs shadow-blue-600/30">
                <Zap className="w-5 h-5 fill-white/20" />
              </div>
              <div>
                <h1 className="font-black text-base tracking-tight text-slate-900 leading-tight">
                  RazorFlow <span className="text-blue-600">AI</span>
                </h1>
                <p className="text-[10px] font-mono font-bold uppercase tracking-wider text-blue-600">
                  AI Shopping Agent
                </p>
              </div>
            </div>

            {/* Mobile Close Button */}
            <button
              onClick={() => setIsOpen(false)}
              className="p-1.5 rounded-lg text-slate-400 hover:text-slate-600 hover:bg-slate-100 md:hidden"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Navigation Links */}
          <div className="space-y-1.5 pt-2">
            <p className="px-3 text-[10px] font-mono font-bold uppercase tracking-wider text-slate-400">
              Menu
            </p>

            {/* 1. AI Shopping */}
            <button
              onClick={() => handleNav('chat')}
              className={`w-full flex items-center gap-3 px-3.5 py-2.5 rounded-xl font-semibold text-sm transition-all duration-200 ${
                activeTab === 'chat'
                  ? 'bg-blue-600 text-white shadow-sm shadow-blue-600/20'
                  : 'text-slate-700 hover:bg-slate-100 hover:text-slate-900'
              }`}
            >
              <Bot className="w-4.5 h-4.5" />
              <span>AI Shopping</span>
            </button>

            {/* 2. Cart */}
            <button
              onClick={() => handleNav('cart')}
              className="w-full flex items-center justify-between px-3.5 py-2.5 rounded-xl font-semibold text-sm text-slate-700 hover:bg-slate-100 hover:text-slate-900 transition-all duration-200 group"
            >
              <div className="flex items-center gap-3">
                <ShoppingBag className="w-4.5 h-4.5 text-blue-600 group-hover:scale-105 transition-transform" />
                <span>Cart</span>
              </div>
              {itemCount > 0 && (
                <span className="px-2 py-0.5 rounded-full bg-blue-600 text-white text-[11px] font-mono font-bold shadow-xs">
                  {itemCount}
                </span>
              )}
            </button>

            {/* 3. Profile */}
            <button
              onClick={() => handleNav('profile')}
              className={`w-full flex items-center gap-3 px-3.5 py-2.5 rounded-xl font-semibold text-sm transition-all duration-200 ${
                activeTab === 'profile'
                  ? 'bg-blue-600 text-white shadow-sm shadow-blue-600/20'
                  : 'text-slate-700 hover:bg-slate-100 hover:text-slate-900'
              }`}
            >
              <User className="w-4.5 h-4.5" />
              <span>Profile</span>
            </button>
          </div>
        </div>

        {/* Bottom Section: Status Card */}
        <div className="p-4 border-t border-slate-100">
          <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-200/80 space-y-2">
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
              <span className="text-xs font-mono font-bold text-slate-700">
                Agentic Engine Active
              </span>
            </div>
            <p className="text-[11px] text-slate-500 leading-snug">
              Intent Understanding & Budget Discovery System Online.
            </p>
          </div>
        </div>

      </aside>
    </>
  );
}
