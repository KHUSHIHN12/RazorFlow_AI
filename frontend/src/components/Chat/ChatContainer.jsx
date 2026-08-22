import React, { useRef, useEffect } from 'react';
import { Bot, ShoppingBag, ArrowRight, Zap } from 'lucide-react';
import { useCart } from '../../context/CartContext';
import MessageList from './MessageList';
import ChatInput from './ChatInput';
import ChatSkeleton from './ChatSkeleton';

export default function ChatContainer() {
  const { messages, isProcessing, cart, cartTotalINR, setIsCartOpen } = useCart();
  const scrollRef = useRef(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, isProcessing]);

  return (
    <div className="max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6 flex-1 flex flex-col min-h-[calc(100vh-4rem)] bg-slate-50">
      
      {/* Grid Layout: Desktop 2-Column Sidebar + Main Chat */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 flex-1">
        
        {/* Left Sidebar Context & Control Panel (Desktop) */}
        <div className="hidden lg:flex lg:col-span-4 flex-col gap-5">
          
          {/* Live Shopping Cart Card (Clean White, Bold Shadow & Thick Border) */}
          <div className="p-5 rounded-2xl bg-white border-2 border-slate-300 shadow-lg space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2 text-slate-900 font-bold text-sm">
                <ShoppingBag className="w-4 h-4 text-blue-600" />
                <span>Live Shopping Cart</span>
              </div>
              <span className="px-2.5 py-0.5 rounded-full text-xs font-mono bg-blue-50 text-blue-700 border border-blue-200 font-bold">
                {cart.reduce((s, i) => s + i.quantity, 0)} items
              </span>
            </div>

            {cart.length === 0 ? (
              <p className="text-xs text-slate-500 py-2">Your cart is currently empty. Ask the agent to recommend products!</p>
            ) : (
              <div className="space-y-2">
                <div className="max-h-36 overflow-y-auto space-y-1.5 pr-1">
                  {cart.map((item) => (
                    <div key={item.product_id} className="flex items-center justify-between text-xs text-slate-900 py-1 border-b border-slate-100">
                      <span className="truncate max-w-[170px] text-slate-900 font-medium">{item.name}</span>
                      <span className="font-mono text-blue-700 font-semibold">₹{(item.price * item.quantity).toLocaleString('en-IN')}</span>
                    </div>
                  ))}
                </div>
                
                <div className="pt-2 flex items-center justify-between text-sm font-bold text-slate-900">
                  <span>Total:</span>
                  <span className="text-emerald-600 font-mono text-base">₹{cartTotalINR.toLocaleString('en-IN')}</span>
                </div>

                <button
                  onClick={() => setIsCartOpen(true)}
                  className="w-full py-2.5 px-3 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-bold text-xs shadow-sm transition-all flex items-center justify-center gap-2 mt-2 active:scale-95"
                >
                  <span>Manage Cart & Checkout</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </button>
              </div>
            )}
          </div>

        </div>

        {/* Right Main Chat Panel (Clean White, Bold Shadow & Thick Border Floating) */}
        <div className="lg:col-span-8 flex flex-col rounded-2xl bg-white border-2 border-slate-300 shadow-lg overflow-hidden h-[calc(100vh-7rem)]">
          
          {/* Header Bar */}
          <div className="px-6 py-4 border-b border-slate-200 bg-white flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="relative">
                <div className="w-9 h-9 rounded-xl bg-blue-600 flex items-center justify-center text-white shadow-xs">
                  <Bot className="w-5 h-5" />
                </div>
                <span className="absolute bottom-0 right-0 w-2.5 h-2.5 rounded-full bg-emerald-500 border-2 border-white"></span>
              </div>
              <div>
                <h2 className="text-sm font-bold text-slate-900 flex items-center gap-2">
                  RazorFlow AI Assistant
                  <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-blue-50 text-blue-700 border border-blue-200">
                    Online
                  </span>
                </h2>
                <p className="text-xs text-slate-500">Contextual e-commerce, budget discovery & instant test checkout</p>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <span className="hidden sm:inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-slate-100 border border-slate-200 text-[11px] font-mono text-slate-700">
                <Zap className="w-3.5 h-3.5 text-blue-600" /> Razorpay Test Mode
              </span>
            </div>
          </div>

          {/* Messages Feed Area */}
          <div
            ref={scrollRef}
            className="flex-1 overflow-y-auto p-4 sm:p-6 bg-slate-50/70 space-y-6"
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
