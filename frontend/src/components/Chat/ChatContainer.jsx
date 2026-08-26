import React, { useRef, useEffect } from 'react';
import { Bot, Zap } from 'lucide-react';
import { useCart } from '../../context/CartContext';
import MessageList from './MessageList';
import ChatInput from './ChatInput';
import ChatSkeleton from './ChatSkeleton';

export default function ChatContainer() {
  const { messages, isProcessing } = useCart();
  const scrollRef = useRef(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, isProcessing]);

  return (
    <div className="max-w-5xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6 flex-1 flex flex-col min-h-[calc(100vh-4rem)] bg-slate-50 justify-center">
      
      {/* Centered Main Chat Panel */}
      <div className="flex flex-col rounded-2xl bg-white border-2 border-slate-300 shadow-xl overflow-hidden h-[calc(100vh-7.5rem)] w-full transition-all">
        
        {/* Header Bar */}
        <div className="px-6 py-4 border-b border-slate-200 bg-white flex items-center justify-between shadow-2xs">
          <div className="flex items-center gap-3">
            <div className="relative">
              <div className="w-10 h-10 rounded-xl bg-blue-600 flex items-center justify-center text-white shadow-xs">
                <Bot className="w-5.5 h-5.5" />
              </div>
              <span className="absolute bottom-0 right-0 w-2.5 h-2.5 rounded-full bg-emerald-500 border-2 border-white"></span>
            </div>
            <div>
              <h2 className="text-base font-extrabold text-slate-900 flex items-center gap-2">
                RazorFlow AI Assistant
                <span className="px-2.5 py-0.5 rounded-full text-[10px] font-mono font-bold bg-blue-50 text-blue-700 border border-blue-200">
                  Online
                </span>
              </h2>
              <p className="text-xs text-slate-500">Contextual e-commerce, budget discovery & instant test checkout</p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <span className="hidden sm:inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-slate-100 border border-slate-200 text-[11px] font-mono font-semibold text-slate-700">
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
  );
}
