import React, { useState } from 'react';
import { Send, Sparkles, ShoppingBag } from 'lucide-react';
import { useCart } from '../../context/CartContext';

export default function ChatInput() {
  const [input, setInput] = useState('');
  const { sendMessage, isProcessing, cart } = useCart();

  const starterPrompts = [
    "Find laptops for coding under ₹60,000",
    "Show me noise-cancelling headphones",
    "I need an ergonomic mouse for programming",
    "Show 4K developer monitors"
  ];

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!input.trim() || isProcessing) return;
    sendMessage(input);
    setInput('');
  };

  const handleChipClick = (promptText) => {
    if (isProcessing) return;
    sendMessage(promptText);
  };

  return (
    <div className="border-t border-slate-200 bg-white p-4 sm:p-5 rounded-b-2xl">
      
      {/* Quick Intent Starter Chips */}
      <div className="flex items-center gap-2 overflow-x-auto pb-3 scrollbar-none text-xs">
        <span className="flex items-center gap-1.5 text-slate-500 font-mono text-[11px] font-medium whitespace-nowrap flex-shrink-0">
          <Sparkles className="w-3.5 h-3.5 text-blue-600" /> Intent Presets:
        </span>
        {starterPrompts.map((prompt, idx) => (
          <button
            key={idx}
            onClick={() => handleChipClick(prompt)}
            disabled={isProcessing}
            className="px-3.5 py-1.5 rounded-full bg-slate-100 hover:bg-blue-50 border border-slate-200 text-slate-700 hover:text-blue-700 whitespace-nowrap transition-all duration-200 text-xs font-medium active:scale-95 disabled:opacity-50"
          >
            {prompt}
          </button>
        ))}

        {cart.length > 0 && (
          <button
            onClick={() => handleChipClick('Yes, proceed to pay')}
            disabled={isProcessing}
            className="px-3.5 py-1.5 rounded-full bg-emerald-50 hover:bg-emerald-100 border border-emerald-300 text-emerald-800 font-bold whitespace-nowrap transition-all duration-200 text-xs flex items-center gap-1.5 active:scale-95 disabled:opacity-50 shadow-2xs"
          >
            <ShoppingBag className="w-3.5 h-3.5 text-emerald-600" />
            <span>Proceed to Pay (₹{cart.reduce((s, i) => s + i.price * i.quantity, 0).toLocaleString('en-IN')})</span>
          </button>
        )}
      </div>

      {/* Text Input Form */}
      <form onSubmit={handleSubmit} className="relative flex items-center">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask RazorFlow AI (e.g., 'Find laptops for coding under ₹60,000')..."
          disabled={isProcessing}
          className="w-full pl-4 pr-12 py-3.5 rounded-xl bg-white border border-slate-300 text-slate-900 placeholder-slate-400 text-sm font-sans outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-600 transition-all duration-200 shadow-2xs"
        />
        <button
          type="submit"
          disabled={!input.trim() || isProcessing}
          className="absolute right-2 p-2.5 rounded-lg bg-blue-600 hover:bg-blue-700 text-white transition-all duration-200 disabled:opacity-40 active:scale-95 shadow-xs"
        >
          <Send className="w-4 h-4" />
        </button>
      </form>

    </div>
  );
}
