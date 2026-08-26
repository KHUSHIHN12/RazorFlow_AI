import React from 'react';
import { X, Trash2, Plus, Minus, ShoppingBag, ArrowRight, CheckSquare, Square } from 'lucide-react';
import { useCart } from '../../context/CartContext';

export default function CartDrawer() {
  const {
    cart,
    isCartOpen,
    setIsCartOpen,
    cartTotalINR,
    selectedCartItems,
    selectedCount,
    selectedTotalINR,
    userBudget,
    remainingBudget,
    toggleSelectItem,
    selectAllItems,
    clearSelection,
    addToCart,
    removeFromCart,
    clearCart,
    sendMessage
  } = useCart();

  if (!isCartOpen) return null;

  const handleCheckoutSelected = () => {
    if (selectedCartItems.length === 0) {
      alert("Please select at least one item from your cart to checkout.");
      return;
    }
    setIsCartOpen(false);
    const selectedNames = selectedCartItems.map(i => `${i.quantity}x ${i.name}`).join(', ');
    sendMessage(`I want to buy the selected items from my cart (${selectedNames}). Proceed to checkout.`);
  };

  return (
    <div className="fixed inset-0 z-50 overflow-hidden">
      {/* Backdrop */}
      <div
        onClick={() => setIsCartOpen(false)}
        className="absolute inset-0 bg-slate-900/40 backdrop-blur-xs transition-opacity animate-in fade-in"
      />

      <div className="fixed inset-y-0 right-0 max-w-full flex pl-10">
        <div className="w-screen max-w-md bg-white border-l border-slate-200 shadow-2xl flex flex-col justify-between">
          
          {/* Drawer Header */}
          <div className="p-4 sm:p-6 border-b border-slate-200 flex items-center justify-between bg-slate-50/50">
            <div className="flex items-center gap-2.5">
              <ShoppingBag className="w-5 h-5 text-blue-600" />
              <h2 className="text-lg font-bold text-slate-900">Shopping Cart</h2>
              <span className="px-2.5 py-0.5 rounded-full text-xs font-mono bg-blue-50 text-blue-700 border border-blue-200 font-semibold">
                {cart.length} items ({selectedCount} selected)
              </span>
            </div>

            <button
              onClick={() => setIsCartOpen(false)}
              className="p-1.5 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-500 hover:text-slate-900 transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Quick Selection Controls */}
          {cart.length > 0 && (
            <div className="px-6 py-2.5 bg-slate-100/70 border-b border-slate-200 flex items-center justify-between text-xs text-slate-700">
              <span className="font-medium text-slate-600">Checkout Selection:</span>
              <div className="flex items-center gap-3">
                <button
                  onClick={() => selectAllItems(true)}
                  className="text-blue-600 hover:text-blue-800 font-semibold hover:underline"
                >
                  Select All
                </button>
                <span className="text-slate-300">|</span>
                <button
                  onClick={clearSelection}
                  className="text-slate-500 hover:text-slate-700 font-medium hover:underline"
                >
                  Clear Selection
                </button>
              </div>
            </div>
          )}

          {/* Cart Item List with Selection Controls */}
          <div className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-4 bg-slate-50/30">
            {cart.length === 0 ? (
              <div className="h-full flex flex-col items-center justify-center text-center p-6 text-slate-500 space-y-3">
                <div className="w-16 h-16 rounded-2xl bg-slate-100 border border-slate-200 flex items-center justify-center text-slate-400">
                  <ShoppingBag className="w-8 h-8" />
                </div>
                <p className="text-sm font-medium text-slate-700">Your cart is empty</p>
                <p className="text-xs text-slate-500 max-w-xs">
                  Ask RazorFlow AI in chat to find laptops or accessories under your budget!
                </p>
              </div>
            ) : (
              cart.map((item) => {
                const isSelected = item.selected === true;
                return (
                  <div
                    key={item.product_id}
                    className={`p-3.5 rounded-xl border flex items-center gap-3 group transition-all ${
                      isSelected
                        ? 'bg-white border-blue-300 shadow-2xs'
                        : 'bg-slate-50/80 border-slate-200 opacity-75'
                    }`}
                  >
                    {/* Item Selection Checkbox */}
                    <button
                      onClick={() => toggleSelectItem(item.product_id)}
                      className="p-1 text-blue-600 hover:scale-110 transition-transform"
                      title={isSelected ? "Uncheck to exclude from checkout" : "Check to include in checkout"}
                    >
                      {isSelected ? (
                        <CheckSquare className="w-5 h-5 text-blue-600 fill-blue-50" />
                      ) : (
                        <Square className="w-5 h-5 text-slate-400" />
                      )}
                    </button>

                    <img
                      src={item.image_url}
                      alt={item.name}
                      className="w-12 h-12 rounded-lg object-cover bg-slate-100 border border-slate-200 flex-shrink-0"
                    />

                    <div className="flex-1 min-w-0">
                      <h4 className={`text-sm font-semibold truncate ${isSelected ? 'text-slate-900' : 'text-slate-500 line-through'}`}>
                        {item.name}
                      </h4>
                      <p className="text-xs text-blue-700 font-mono font-bold mt-0.5">
                        ₹{item.price.toLocaleString('en-IN')}
                      </p>

                      {/* Quantity controls */}
                      <div className="flex items-center gap-2 mt-1.5">
                        <button
                          onClick={() => removeFromCart(item.product_id)}
                          className="w-5 h-5 rounded bg-slate-100 hover:bg-slate-200 text-slate-700 flex items-center justify-center text-xs border border-slate-200"
                        >
                          <Minus className="w-3 h-3" />
                        </button>
                        <span className="text-xs font-mono font-semibold text-slate-800 w-4 text-center">
                          {item.quantity}
                        </span>
                        <button
                          onClick={() => addToCart({ id: item.product_id, ...item })}
                          className="w-5 h-5 rounded bg-slate-100 hover:bg-slate-200 text-slate-700 flex items-center justify-center text-xs border border-slate-200"
                        >
                          <Plus className="w-3 h-3" />
                        </button>
                      </div>
                    </div>

                    <button
                      onClick={() => removeFromCart(item.product_id)}
                      className="p-2 text-slate-400 hover:text-red-600 transition-colors"
                      title="Remove from cart"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                );
              })
            )}
          </div>

          {/* Drawer Footer displaying Selected Items Subtotal */}
          {cart.length > 0 && (
            <div className="p-4 sm:p-6 border-t border-slate-200 bg-white space-y-4 shadow-sm">
              <div className="space-y-1.5 bg-slate-50 p-3 rounded-xl border border-slate-200">
                <div className="flex items-center justify-between text-xs text-slate-500">
                  <span>Basket Total ({cart.length} items):</span>
                  <span className="font-mono text-slate-700">₹{cartTotalINR.toLocaleString('en-IN')}</span>
                </div>

                <div className="flex items-center justify-between text-base font-bold text-slate-900 pt-1 border-t border-slate-200">
                  <span className="flex items-center gap-1.5 text-blue-800">
                    <span>Selected for Checkout ({selectedCount}):</span>
                  </span>
                  <span className="text-emerald-600 font-mono text-lg">
                    ₹{selectedTotalINR.toLocaleString('en-IN')}
                  </span>
                </div>

                {userBudget !== null && (
                  <div className="flex items-center justify-between text-xs font-semibold pt-1 border-t border-slate-100">
                    <span className="text-slate-600">Remaining Budget (Out of ₹{userBudget.toLocaleString('en-IN')}):</span>
                    <span className={`font-mono ${remainingBudget >= 0 ? 'text-blue-700' : 'text-red-600'}`}>
                      ₹{remainingBudget.toLocaleString('en-IN')}
                    </span>
                  </div>
                )}
              </div>

              <div className="flex gap-2">
                <button
                  onClick={clearCart}
                  className="px-3.5 py-3 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-semibold border border-slate-200"
                >
                  Clear Cart
                </button>

                <button
                  onClick={handleCheckoutSelected}
                  disabled={selectedCartItems.length === 0}
                  className="flex-1 py-3 px-4 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-bold text-sm shadow-md shadow-blue-600/30 flex items-center justify-center gap-2 transition-all active:scale-95 disabled:opacity-50"
                >
                  <span>Buy Selected Items (₹{selectedTotalINR.toLocaleString('en-IN')})</span>
                  <ArrowRight className="w-4 h-4" />
                </button>
              </div>
            </div>
          )}

        </div>
      </div>
    </div>
  );
}
