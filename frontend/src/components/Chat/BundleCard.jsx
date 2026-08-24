import React, { useState } from 'react';
import { Layers, ShoppingCart, Check, Zap, DollarSign } from 'lucide-react';
import { useCart } from '../../context/CartContext';

export default function BundleCard({ bundleData }) {
  const { addToCart, sendMessage } = useCart();
  const [added, setAdded] = useState(false);

  if (!bundleData) return null;

  const handleAddBundleToCart = () => {
    bundleData.items.forEach(item => {
      addToCart(item);
    });
    setAdded(true);
  };

  const handleBuyBundleNow = () => {
    handleAddBundleToCart();
    sendMessage(`I want to buy the complete ${bundleData.bundle_title}. Proceed to checkout.`);
  };

  return (
    <div className="mt-4 p-5 rounded-2xl bg-gradient-to-br from-indigo-50/90 via-white to-purple-50/80 border-2 border-indigo-200 shadow-md animate-in fade-in duration-300">
      
      {/* Header Banner */}
      <div className="flex items-center justify-between pb-3.5 border-b border-indigo-100">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-xl bg-purple-600 flex items-center justify-center text-white shadow-xs">
            <Layers className="w-4.5 h-4.5" />
          </div>
          <div>
            <h3 className="font-extrabold text-sm text-slate-900">{bundleData.bundle_title}</h3>
            <p className="text-[11px] text-slate-500 font-mono">Goal-based multi-product setup</p>
          </div>
        </div>

        <span className="px-3 py-1 rounded-full text-xs font-mono font-bold bg-purple-100 text-purple-800 border border-purple-200">
          Budget Match
        </span>
      </div>

      {/* Itemized Products List */}
      <div className="my-4 space-y-2.5">
        {bundleData.items.map((item) => (
          <div
            key={item.id}
            className="flex items-center justify-between p-2.5 rounded-xl bg-white border border-slate-200 shadow-2xs text-xs"
          >
            <div className="flex items-center gap-2.5 min-w-0">
              <img
                src={item.image_url}
                alt={item.name}
                className="w-10 h-10 rounded-lg object-cover bg-slate-100 border border-slate-200 flex-shrink-0"
              />
              <div className="truncate">
                <p className="font-semibold text-slate-900 truncate">{item.name}</p>
                <p className="text-[10px] text-slate-500 font-mono uppercase">{item.category}</p>
              </div>
            </div>

            <span className="font-mono text-blue-700 font-bold text-xs whitespace-nowrap">
              ₹{item.price.toLocaleString('en-IN')}
            </span>
          </div>
        ))}
      </div>

      {/* Pricing Summary */}
      <div className="p-3 rounded-xl bg-white border border-slate-200 flex items-center justify-between text-xs font-mono mb-4">
        <div>
          <span className="text-slate-500">Remaining Budget:</span>
          <span className="font-bold text-emerald-600 ml-1.5">₹{bundleData.remaining_budget.toLocaleString('en-IN')}</span>
        </div>
        <div className="text-right">
          <span className="text-slate-500">Total Setup Cost:</span>
          <span className="text-base font-extrabold text-slate-900 ml-1.5">₹{bundleData.total_cost.toLocaleString('en-IN')}</span>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex gap-2.5">
        <button
          onClick={handleAddBundleToCart}
          className={`flex-1 py-3 px-4 rounded-xl text-xs font-bold transition-all flex items-center justify-center gap-2 ${
            added
              ? 'bg-emerald-50 border border-emerald-300 text-emerald-700'
              : 'bg-indigo-600 hover:bg-indigo-700 text-white shadow-xs active:scale-95'
          }`}
        >
          {added ? <Check className="w-4 h-4 text-emerald-600" /> : <ShoppingCart className="w-4 h-4" />}
          <span>{added ? 'Bundle Added to Cart' : 'Add Entire Bundle to Cart'}</span>
        </button>

        <button
          onClick={handleBuyBundleNow}
          className="py-3 px-4 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-bold text-xs shadow-xs transition-all flex items-center justify-center gap-1.5 active:scale-95"
        >
          <Zap className="w-3.5 h-3.5 fill-white" />
          <span>Checkout Setup</span>
        </button>
      </div>

    </div>
  );
}
