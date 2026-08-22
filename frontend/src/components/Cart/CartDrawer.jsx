import React from 'react';
import { X, Trash2, Plus, Minus, ShoppingBag, ShieldCheck, ArrowRight } from 'lucide-react';
import { useCart } from '../../context/CartContext';

export default function CartDrawer() {
  const {
    cart,
    isCartOpen,
    setIsCartOpen,
    cartTotalINR,
    cartTotalPaise,
    addToCart,
    removeFromCart,
    clearCart,
    sendMessage
  } = useCart();

  if (!isCartOpen) return null;

  const handleCheckout = () => {
    setIsCartOpen(false);
    sendMessage("I'm ready to checkout my cart items. Proceed to pay.");
  };

  return (
    <div className="fixed inset-0 z-50 overflow-hidden">
      {/* Backdrop */}
      <div
        onClick={() => setIsCartOpen(false)}
        className="absolute inset-0 bg-slate-950/80 backdrop-blur-sm transition-opacity animate-in fade-in"
      />

      <div className="fixed inset-y-0 right-0 max-w-full flex pl-10">
        <div className="w-screen max-w-md bg-slate-950 border-l border-slate-800 shadow-2xl flex flex-col justify-between">
          
          {/* Drawer Header */}
          <div className="p-4 sm:p-6 border-b border-slate-800 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <ShoppingBag className="w-5 h-5 text-cyan-400" />
              <h2 className="text-lg font-bold text-slate-100">Shopping Cart</h2>
              <span className="px-2 py-0.5 rounded-full text-xs font-mono bg-blue-500/10 text-blue-400 border border-blue-500/30">
                {cart.length} items
              </span>
            </div>

            <button
              onClick={() => setIsCartOpen(false)}
              className="p-1.5 rounded-lg bg-slate-900 hover:bg-slate-800 text-slate-400 hover:text-slate-100 transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Cart Item List */}
          <div className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-4">
            {cart.length === 0 ? (
              <div className="h-full flex flex-col items-center justify-center text-center p-6 text-slate-400 space-y-3">
                <div className="w-16 h-16 rounded-2xl bg-slate-900 border border-slate-800 flex items-center justify-center text-slate-500">
                  <ShoppingBag className="w-8 h-8" />
                </div>
                <p className="text-sm font-medium">Your cart is empty</p>
                <p className="text-xs text-slate-400 max-w-xs">
                  Ask RazorFlow AI in chat to find laptops or accessories under your budget!
                </p>
              </div>
            ) : (
              cart.map((item) => (
                <div
                  key={item.product_id}
                  className="p-3.5 rounded-xl bg-slate-900/90 border border-slate-800 flex items-center gap-3.5 group hover:border-slate-700 transition-all"
                >
                  <img
                    src={item.image_url}
                    alt={item.name}
                    className="w-14 h-14 rounded-lg object-cover bg-slate-950 border border-slate-800 flex-shrink-0"
                  />

                  <div className="flex-1 min-w-0">
                    <h4 className="text-sm font-semibold text-slate-200 truncate">
                      {item.name}
                    </h4>
                    <p className="text-xs text-cyan-400 font-mono font-bold mt-0.5">
                      ₹{item.price.toLocaleString('en-IN')}
                    </p>

                    {/* Quantity controls */}
                    <div className="flex items-center gap-2 mt-2">
                      <button
                        onClick={() => removeFromCart(item.product_id)}
                        className="w-6 h-6 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 flex items-center justify-center text-xs"
                      >
                        <Minus className="w-3 h-3" />
                      </button>
                      <span className="text-xs font-mono font-semibold text-slate-200 w-4 text-center">
                        {item.quantity}
                      </span>
                      <button
                        onClick={() => addToCart({ id: item.product_id, ...item })}
                        className="w-6 h-6 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 flex items-center justify-center text-xs"
                      >
                        <Plus className="w-3 h-3" />
                      </button>
                    </div>
                  </div>

                  <button
                    onClick={() => removeFromCart(item.product_id)}
                    className="p-2 text-slate-400 hover:text-red-400 transition-colors"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              ))
            )}
          </div>

          {/* Drawer Footer */}
          {cart.length > 0 && (
            <div className="p-4 sm:p-6 border-t border-slate-800 bg-slate-950 space-y-4">
              <div className="space-y-1.5">
                <div className="flex items-center justify-between text-xs text-slate-400">
                  <span>Currency Sub-units (Paise):</span>
                  <span className="font-mono text-slate-300">{cartTotalPaise} paise</span>
                </div>
                <div className="flex items-center justify-between text-base font-bold text-white">
                  <span>Cart Total:</span>
                  <span className="text-lg text-emerald-400 font-mono">
                    ₹{cartTotalINR.toLocaleString('en-IN')}
                  </span>
                </div>
              </div>

              <div className="flex gap-2">
                <button
                  onClick={clearCart}
                  className="px-3 py-3 rounded-xl bg-slate-900 hover:bg-slate-800 text-slate-400 hover:text-slate-200 text-xs font-medium border border-slate-800"
                >
                  Clear
                </button>
                <button
                  onClick={handleCheckout}
                  className="flex-1 py-3 px-4 rounded-xl bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-500 hover:to-cyan-500 text-white font-bold text-sm shadow-lg shadow-blue-600/30 flex items-center justify-center gap-2"
                >
                  <span>Proceed to Pay</span>
                  <ArrowRight className="w-4 h-4" />
                </button>
              </div>

              <p className="text-[10px] text-slate-400 font-mono text-center flex items-center justify-center gap-1">
                <ShieldCheck className="w-3 h-3 text-emerald-400" />
                Deterministic Guardrail active before Razorpay order creation
              </p>
            </div>
          )}

        </div>
      </div>
    </div>
  );
}
