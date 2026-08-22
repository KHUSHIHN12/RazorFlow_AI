import React, { useRef, useEffect } from 'react';
import { Bot, Sparkles, ShieldCheck, ShoppingBag, ArrowRight, Sliders, Cpu, Zap } from 'lucide-react';
import { useCart } from '../../context/CartContext';
import MessageList from './MessageList';
import ChatInput from './ChatInput';
import ChatSkeleton from './ChatSkeleton';

export default function ChatContainer() {
  const { messages, isProcessing, cart, cartTotalINR, setIsCartOpen, sendMessage } = useCart();
  const scrollRef = useRef(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, isProcessing]);

  const presetFilters = [
    { label: 'Coding Laptops < ₹60k', query: 'Find laptops for coding under ₹60,000' },
    { label: 'ANC Headphones', query: 'Show me active noise cancelling headphones' },
    { label: 'Ergonomic Mouse', query: 'I need an ergonomic mouse for programming' },
    { label: '4K Monitors', query: 'Show 4K developer monitors' }
  ];

  return (
    <div className="max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6 flex-1 flex flex-col min-h-[calc(100vh-4rem)]">
      
      {/* Grid Layout: Desktop 2-Column Sidebar + Main Chat */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 flex-1">
        
        {/* Left Sidebar Context & Control Panel (Desktop) */}
        <div className="hidden lg:flex lg:col-span-4 flex-col gap-5">
          
          {/* Engine Card */}
          <div className="p-5 rounded-2xl bg-slate-900/90 border border-slate-800/80 backdrop-blur-xl shadow-xl space-y-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-blue-600 to-cyan-500 flex items-center justify-center text-white shadow-md shadow-blue-500/20">
                <Cpu className="w-5 h-5" />
              </div>
              <div>
                <h3 className="font-bold text-sm text-slate-100 flex items-center gap-2">
                  LangGraph Agentic Engine
                </h3>
                <p className="text-xs text-slate-400 font-mono">Stateful Tool Execution</p>
              </div>
            </div>

            <div className="space-y-2 pt-2 border-t border-slate-800 text-xs">
              <div className="flex items-center justify-between text-slate-300">
                <span className="text-slate-400">Budget Aware Search:</span>
                <span className="font-mono text-cyan-400 font-semibold">Active</span>
              </div>
              <div className="flex items-center justify-between text-slate-300">
                <span className="text-slate-400">Human-In-The-Loop:</span>
                <span className="font-mono text-emerald-400 font-semibold">Enforced</span>
              </div>
              <div className="flex items-center justify-between text-slate-300">
                <span className="text-slate-400">Razorpay API:</span>
                <span className="font-mono text-blue-400 font-semibold">Test SDK v1</span>
              </div>
            </div>
          </div>

          {/* Quick Preset Queries */}
          <div className="p-5 rounded-2xl bg-slate-900/90 border border-slate-800/80 backdrop-blur-xl shadow-xl space-y-3">
            <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-slate-400">
              <Sliders className="w-4 h-4 text-cyan-400" />
              <span>Smart Intent Presets</span>
            </div>

            <div className="space-y-2">
              {presetFilters.map((preset, idx) => (
                <button
                  key={idx}
                  onClick={() => sendMessage(preset.query)}
                  disabled={isProcessing}
                  className="w-full text-left p-3 rounded-xl bg-slate-950/80 hover:bg-slate-800/80 border border-slate-800 hover:border-cyan-500/40 text-xs text-slate-300 hover:text-white transition-all duration-200 flex items-center justify-between group active:scale-[0.98]"
                >
                  <span className="font-medium">{preset.label}</span>
                  <ArrowRight className="w-3.5 h-3.5 text-slate-500 group-hover:text-cyan-400 group-hover:translate-x-1 transition-all" />
                </button>
              ))}
            </div>
          </div>

          {/* Cart Widget */}
          <div className="p-5 rounded-2xl bg-gradient-to-br from-slate-900 via-slate-900 to-blue-950/40 border border-slate-800/80 backdrop-blur-xl shadow-xl space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2 text-slate-200 font-bold text-sm">
                <ShoppingBag className="w-4 h-4 text-cyan-400" />
                <span>Live Shopping Cart</span>
              </div>
              <span className="px-2.5 py-0.5 rounded-full text-xs font-mono bg-blue-500/10 text-blue-400 border border-blue-500/30 font-bold">
                {cart.reduce((s, i) => s + i.quantity, 0)} items
              </span>
            </div>

            {cart.length === 0 ? (
              <p className="text-xs text-slate-400 py-2">Your cart is currently empty. Ask the agent to recommend products!</p>
            ) : (
              <div className="space-y-2">
                <div className="max-h-36 overflow-y-auto space-y-1.5 pr-1">
                  {cart.map((item) => (
                    <div key={item.product_id} className="flex items-center justify-between text-xs text-slate-300 py-1 border-b border-slate-800/50">
                      <span className="truncate max-w-[170px]">{item.name}</span>
                      <span className="font-mono text-cyan-400 font-semibold">₹{(item.price * item.quantity).toLocaleString('en-IN')}</span>
                    </div>
                  ))}
                </div>
                
                <div className="pt-2 flex items-center justify-between text-sm font-bold text-white">
                  <span>Total:</span>
                  <span className="text-emerald-400 font-mono text-base">₹{cartTotalINR.toLocaleString('en-IN')}</span>
                </div>

                <button
                  onClick={() => setIsCartOpen(true)}
                  className="w-full py-2.5 px-3 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-bold text-xs shadow-md shadow-blue-600/30 transition-all flex items-center justify-center gap-2 mt-2"
                >
                  <span>Manage Cart & Checkout</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </button>
              </div>
            )}
          </div>

          {/* Security Banner */}
          <div className="p-3.5 rounded-xl bg-emerald-950/20 border border-emerald-500/20 text-emerald-400 text-xs font-mono flex items-center gap-2">
            <ShieldCheck className="w-4 h-4 text-emerald-400 flex-shrink-0" />
            <span>Deterministic SHA256 HMAC Guardrail Enabled</span>
          </div>

        </div>

        {/* Right Main Chat Panel (Desktop 8-cols, Mobile 12-cols) */}
        <div className="lg:col-span-8 flex flex-col rounded-2xl bg-slate-900/80 border border-slate-800/80 backdrop-blur-xl shadow-2xl overflow-hidden h-[calc(100vh-7rem)]">
          
          {/* Header Bar */}
          <div className="px-6 py-4 border-b border-slate-800/80 bg-slate-950/60 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="relative">
                <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-blue-600 to-cyan-500 flex items-center justify-center text-white shadow-md shadow-blue-500/20">
                  <Bot className="w-5 h-5" />
                </div>
                <span className="absolute bottom-0 right-0 w-2.5 h-2.5 rounded-full bg-emerald-400 border-2 border-slate-900"></span>
              </div>
              <div>
                <h2 className="text-sm font-bold text-slate-100 flex items-center gap-2">
                  RazorFlow AI Assistant
                  <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-blue-500/10 text-cyan-400 border border-blue-500/30">
                    Online
                  </span>
                </h2>
                <p className="text-xs text-slate-400">Contextual e-commerce, budget discovery & instant test checkout</p>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <span className="hidden sm:inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-slate-900 border border-slate-700/80 text-[11px] font-mono text-slate-300">
                <Zap className="w-3 h-3 text-cyan-400" /> Razorpay Test Mode
              </span>
            </div>
          </div>

          {/* Messages Feed */}
          <div
            ref={scrollRef}
            className="flex-1 overflow-y-auto p-4 sm:p-6 bg-slate-950/40 space-y-6"
          >
            <MessageList messages={messages} isProcessing={false} />

            {/* Render loading skeleton when agent is executing */}
            {isProcessing && <ChatSkeleton />}
          </div>

          {/* Chat Input Bar */}
          <ChatInput />

        </div>

      </div>
    </div>
  );
}
