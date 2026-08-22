import React from 'react';
import { Bot, User, ShieldCheck } from 'lucide-react';
import ProductCard from './ProductCard';
import PaymentConfirmModal from './PaymentConfirmModal';

export default function MessageList({ messages }) {
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
              <div className="w-9 h-9 rounded-xl bg-blue-600 flex items-center justify-center text-white shadow-xs flex-shrink-0 mt-0.5">
                <Bot className="w-5 h-5" />
              </div>
            )}

            {/* Bubble Container */}
            <div className={`max-w-2xl flex flex-col ${isAgent ? 'items-start' : 'items-end'}`}>
              
              {/* Message Bubble */}
              <div
                className={`rounded-2xl p-4 text-sm leading-relaxed ${
                  isAgent
                    ? 'bg-slate-100 text-slate-800 rounded-tl-xs border border-slate-200/80 shadow-2xs'
                    : 'bg-blue-600 text-white rounded-tr-xs shadow-sm font-medium'
                }`}
              >
                {/* Text Formatting */}
                <div className="whitespace-pre-wrap font-sans">
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

                {/* Deterministic Confirmation Card */}
                {(msg.confirmationRequired || msg.activeOrder) && (
                  <PaymentConfirmModal
                    activeOrder={msg.activeOrder}
                    confirmationRequired={msg.confirmationRequired}
                  />
                )}

                {/* Verified Payment Receipt Card */}
                {msg.isReceipt && (
                  <div className="mt-3 p-3.5 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs font-mono flex items-start gap-2.5 shadow-2xs">
                    <ShieldCheck className="w-5 h-5 text-emerald-600 flex-shrink-0 mt-0.5" />
                    <div>
                      <p className="font-bold text-emerald-900">Razorpay Verified Payment Signature</p>
                      <p className="text-[11px] text-emerald-700 mt-0.5">HMAC-SHA256 Auth Verified successfully</p>
                    </div>
                  </div>
                )}
              </div>

              {/* Timestamp */}
              <span className="text-[10px] font-mono text-slate-500 mt-1 px-1">
                {msg.timestamp}
              </span>

            </div>

            {/* User Avatar */}
            {!isAgent && (
              <div className="w-9 h-9 rounded-xl bg-slate-200 border border-slate-300 flex items-center justify-center text-slate-700 flex-shrink-0 mt-0.5">
                <User className="w-5 h-5" />
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}
