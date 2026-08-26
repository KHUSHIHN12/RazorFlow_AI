import React, { useRef, useEffect } from 'react';
import { Bot, Sparkles } from 'lucide-react';
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
    <div className="max-w-5xl w-full mx-auto px-3 sm:px-6 py-4 sm:py-6 flex-1 flex flex-col h-[calc(100vh-4rem)] bg-slate-50 justify-center">
      
      {/* Centered Main Conversational Chat Panel */}
      <div className="flex flex-col rounded-2xl bg-white border border-slate-200/90 shadow-md overflow-hidden h-full w-full transition-all">
        
        {/* Agent Welcome Header Banner */}
        <div className="px-5 py-3.5 border-b border-slate-200/80 bg-slate-50/80 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-blue-600 flex items-center justify-center text-white shadow-xs">
              <Bot className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-sm sm:text-base font-extrabold text-slate-900 flex items-center gap-2">
                👋 Welcome to RazorFlow AI!
              </h2>
              <p className="text-xs text-slate-500 font-medium">
                I'm your Intelligent Agentic Shopping Assistant. How can I help you today?
              </p>
            </div>
          </div>

          <span className="hidden sm:inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[10px] font-mono font-bold bg-blue-50 text-blue-700 border border-blue-200">
            <Sparkles className="w-3 h-3 text-blue-600" />
            Agent Active
          </span>
        </div>

        {/* Messages Feed Area */}
        <div
          ref={scrollRef}
          className="flex-1 overflow-y-auto p-4 sm:p-6 bg-slate-50/50 space-y-6"
        >
          <MessageList messages={messages} isProcessing={false} />

          {/* Render loading skeleton when agent is executing */}
          {isProcessing && <ChatSkeleton />}
        </div>

        {/* Bottom Prominent Chat Input Area */}
        <ChatInput />

      </div>
    </div>
  );
}
