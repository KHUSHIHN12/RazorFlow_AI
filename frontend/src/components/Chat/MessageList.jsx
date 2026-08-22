import React from 'react';
import { Bot, User, CheckCircle, ShieldCheck } from 'lucide-react';
import ProductCard from './ProductCard';
import PaymentConfirmModal from './PaymentConfirmModal';

export default function MessageList({ messages, isProcessing }) {
  return (
    <div className="space-y-6 pb-4">
      {messages.map((msg) => {
        const isAgent = msg.sender === 'agent';

        return (
          <div
            key={msg.id}
            className={`flex gap-3 sm:gap-4 ${isAgent ? 'justify-start' : 'justify-end'} animate-in fade-in slide-in-from-bottom-2 duration-300`}
          >
            {/* Avatar */}
            {isAgent && (
              <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-blue-600 to-cyan-500 flex items-center justify-center text-white shadow-md shadow-blue-500/20 flex-shrink-0 mt-0.5">
                <Bot className="w-5 h-5" />
              </div>
            )}

            {/* Bubble Container */}
            <div className={`max-w-2xl flex flex-col ${isAgent ? 'items-start' : 'items-end'}`}>
              
              {/* Message Bubble */}
              <div
                className={`rounded-2xl p-4 text-sm leading-relaxed ${
                  isAgent
                    ? 'bg-slate-900/90 border border-slate-800 text-slate-100 rounded-tl-sm shadow-md'
                    : 'bg-blue-600 text-white rounded-tr-sm shadow-lg shadow-blue-600/20 font-medium'
                }`}
              >
                {/* Text Formatting */}
                <div className="whitespace-pre-wrap font-sans text-slate-100">
                  {msg.text}
                </div>

                {/* Inline Product Cards Grid */}
                {msg.products && msg.products.length > 0 && (
                  <div className="mt-4 space-y-3">
                    {msg.products.map((prod) => (
                      <ProductCard key={prod.id} product={prod} />
                    ))}
                  </div>
                )}

                {/* Deterministic Guardrail Confirmation Card */}
                {(msg.confirmationRequired || msg.activeOrder) && (
                  <PaymentConfirmModal
                    activeOrder={msg.activeOrder}
                    confirmationRequired={msg.confirmationRequired}
                  />
                )}

                {/* Verified Payment Receipt Card */}
                {msg.isReceipt && (
                  <div className="mt-3 p-3 rounded-xl bg-emerald-950/40 border border-emerald-500/30 text-emerald-300 text-xs font-mono flex items-start gap-2">
                    <ShieldCheck className="w-5 h-5 text-emerald-400 flex-shrink-0 mt-0.5" />
                    <div>
                      <p className="font-bold text-emerald-200">Razorpay Verified Payment Signature</p>
                      <p className="text-[11px] text-emerald-400/80 mt-0.5">HMAC-SHA256 Auth Verified successfully</p>
                    </div>
                  </div>
                )}
              </div>

              {/* Timestamp */}
              <span className="text-[10px] font-mono text-slate-400 mt-1 px-1">
                {msg.timestamp}
              </span>

            </div>

            {/* User Avatar */}
            {!isAgent && (
              <div className="w-9 h-9 rounded-xl bg-slate-800 border border-slate-700 flex items-center justify-center text-slate-300 flex-shrink-0 mt-0.5">
                <User className="w-5 h-5" />
              </div>
            )}
          </div>
        );
      })}

      {/* Typing Indicator */}
      {isProcessing && (
        <div className="flex gap-3 items-center">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-blue-600 to-cyan-500 flex items-center justify-center text-white shadow-md shadow-blue-500/20 flex-shrink-0">
            <Bot className="w-5 h-5 animate-pulse" />
          </div>
          <div className="px-4 py-3 rounded-2xl bg-slate-900 border border-slate-800 text-slate-400 text-xs font-mono flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-cyan-400 animate-ping"></span>
            <span>RazorFlow AI Agent is searching catalog & evaluating budget tools...</span>
          </div>
        </div>
      )}
    </div>
  );
}
