import React, { useState, useEffect, useRef } from 'react';
import { Send, Sparkles, ShoppingBag, Mic, MicOff, Trash2 } from 'lucide-react';
import { useCart } from '../../context/CartContext';

export default function ChatInput() {
  const [input, setInput] = useState('');
  const [isListening, setIsListening] = useState(false);
  const { sendMessage, isProcessing, cart, selectedTotalINR } = useCart();
  const recognitionRef = useRef(null);

  const starterPrompts = [
    "Find laptops for coding under ₹60,000",
    "Show me noise-cancelling headphones",
    "I need an ergonomic mouse for programming",
    "Compare the top two laptops",
    "I need a complete programming setup under ₹70,000"
  ];

  useEffect(() => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRecognition) {
      const rec = new SpeechRecognition();
      rec.continuous = false;
      rec.interimResults = false;
      rec.lang = 'en-US';

      rec.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        console.log('[Voice Input Transcribed]:', transcript);
        setInput(transcript);
        setIsListening(false);
        // Manual Send: User can review, edit, or clear transcription before sending
      };

      rec.onerror = (event) => {
        console.warn('[Voice Recognition Error]:', event.error);
        setIsListening(false);
      };

      rec.onend = () => {
        setIsListening(false);
      };

      recognitionRef.current = rec;
    }
  }, []);

  const toggleVoiceInput = () => {
    if (!recognitionRef.current) {
      alert('Speech Recognition is not supported in this browser. Please use Chrome, Edge, or Safari.');
      return;
    }

    if (isListening) {
      recognitionRef.current.stop();
      setIsListening(false);
    } else {
      try {
        recognitionRef.current.start();
        setIsListening(true);
      } catch (err) {
        console.error('Speech recognition start failed:', err);
      }
    }
  };

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
            <span>Proceed to Pay (₹{(selectedTotalINR || cart.reduce((s, i) => s + i.price * i.quantity, 0)).toLocaleString('en-IN')})</span>
          </button>
        )}
      </div>

      {/* Text & Voice Input Form */}
      <form onSubmit={handleSubmit} className="relative flex items-center gap-2">
        <div className="relative flex-1 flex items-center">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder={isListening ? "Listening... Speak your shopping request now..." : "Ask CommercePilot AI (e.g., 'Find laptops for coding under ₹60,000')..."}
            disabled={isProcessing}
            className={`w-full pl-4 pr-20 py-3.5 rounded-xl bg-white border text-slate-900 placeholder-slate-400 text-sm font-sans outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-600 transition-all duration-200 shadow-2xs ${
              isListening ? 'border-red-500 ring-2 ring-red-200 bg-red-50/20' : 'border-slate-300'
            }`}
          />

          <div className="absolute right-2 flex items-center gap-1">
            {/* Clear Input Button */}
            {input.length > 0 && (
              <button
                type="button"
                onClick={() => setInput('')}
                title="Clear input"
                className="p-1.5 rounded-md hover:bg-slate-100 text-slate-400 hover:text-slate-600 transition-colors"
              >
                <Trash2 className="w-4 h-4" />
              </button>
            )}

            {/* Voice Input Microphone Button */}
            <button
              type="button"
              onClick={toggleVoiceInput}
              title={isListening ? "Stop recording" : "Click to speak your shopping query"}
              className={`p-2 rounded-lg transition-all active:scale-95 ${
                isListening
                  ? 'bg-red-600 text-white animate-pulse shadow-md shadow-red-500/50'
                  : 'bg-slate-100 hover:bg-slate-200 text-slate-600 hover:text-blue-600 border border-slate-200'
              }`}
            >
              {isListening ? <MicOff className="w-4 h-4" /> : <Mic className="w-4 h-4" />}
            </button>
          </div>
        </div>

        {/* Submit Button */}
        <button
          type="submit"
          disabled={!input.trim() || isProcessing}
          className="p-3.5 rounded-xl bg-blue-600 hover:bg-blue-700 text-white transition-all duration-200 disabled:opacity-40 active:scale-95 shadow-xs flex-shrink-0"
        >
          <Send className="w-4.5 h-4.5" />
        </button>
      </form>

      {isListening && (
        <p className="text-[11px] text-red-600 font-mono text-center mt-2 animate-pulse flex items-center justify-center gap-1.5">
          <span className="w-2 h-2 rounded-full bg-red-600 animate-ping"></span>
          Recording Voice... Speak your query, then click stop to transcribe.
        </p>
      )}

    </div>
  );
}
