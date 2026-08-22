import React from 'react';
import { ShoppingCart, Zap, Star, Check } from 'lucide-react';
import { useCart } from '../../context/CartContext';

export default function ProductCard({ product }) {
  const { cart, addToCart, sendMessage } = useCart();
  const isInCart = cart.some(i => i.product_id === product.id);

  const handleBuyNow = (e) => {
    e.stopPropagation();
    addToCart(product);
    sendMessage(`I want to buy the ${product.name}. Proceed to checkout.`);
  };

  return (
    <div className="group relative rounded-2xl bg-slate-900/90 border border-slate-800/90 p-4 transition-all duration-300 hover:border-cyan-500/50 hover:shadow-2xl hover:shadow-cyan-500/10 hover:-translate-y-1 flex flex-col sm:flex-row gap-4.5">
      
      {/* Product Image Preview */}
      <div className="relative sm:w-44 h-44 rounded-xl overflow-hidden bg-slate-950 flex-shrink-0 border border-slate-800/80 group-hover:border-cyan-500/30 transition-colors">
        <img
          src={product.image_url}
          alt={product.name}
          className="w-full h-full object-cover group-hover:scale-108 transition-transform duration-500 ease-out"
        />
        <span className="absolute top-2.5 left-2.5 px-2.5 py-0.5 rounded-full text-[10px] font-mono font-bold uppercase tracking-wider bg-slate-950/85 backdrop-blur-md text-cyan-300 border border-cyan-500/40 shadow-sm">
          {product.category}
        </span>
      </div>

      {/* Product Details */}
      <div className="flex-1 flex flex-col justify-between">
        <div>
          <div className="flex items-start justify-between gap-2">
            <h3 className="text-base font-bold text-slate-100 group-hover:text-cyan-300 transition-colors duration-200">
              {product.name}
            </h3>
            <div className="flex items-center gap-1 px-2.5 py-0.5 rounded-md bg-amber-500/10 border border-amber-500/30 text-amber-400 text-xs font-semibold flex-shrink-0">
              <Star className="w-3.5 h-3.5 fill-amber-400 text-amber-400" />
              <span>{product.rating}</span>
            </div>
          </div>

          <p className="text-xs text-slate-300/90 mt-1.5 line-clamp-2 leading-relaxed">
            {product.description}
          </p>

          {/* Key Specs Tags */}
          {product.specs && (
            <div className="flex flex-wrap gap-1.5 mt-3">
              {Object.entries(product.specs).slice(0, 3).map(([key, val]) => (
                <span
                  key={key}
                  className="px-2 py-0.5 rounded-md bg-slate-950/80 border border-slate-800 text-[11px] text-slate-300 font-mono"
                >
                  <strong className="text-slate-400 font-normal uppercase text-[10px]">{key}:</strong> {val}
                </span>
              ))}
            </div>
          )}
        </div>

        {/* Pricing & CTA Actions */}
        <div className="mt-4 pt-3 border-t border-slate-800/80 flex items-center justify-between gap-3">
          <div>
            <span className="text-[11px] text-slate-400 font-mono uppercase tracking-wider">Price</span>
            <div className="text-xl font-extrabold text-white tracking-tight font-mono">
              ₹{product.price.toLocaleString('en-IN')}
            </div>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={() => addToCart(product)}
              className={`flex items-center gap-1.5 px-3.5 py-2 rounded-xl text-xs font-semibold transition-all duration-200 active:scale-95 border ${
                isInCart
                  ? 'bg-emerald-500/15 border-emerald-500/40 text-emerald-400'
                  : 'bg-slate-800 hover:bg-slate-700 text-slate-200 border-slate-700/80 hover:border-cyan-500/30'
              }`}
            >
              {isInCart ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <ShoppingCart className="w-3.5 h-3.5 text-cyan-400" />}
              <span>{isInCart ? 'Added' : 'Add'}</span>
            </button>
            
            <button
              onClick={handleBuyNow}
              className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-gradient-to-r from-blue-600 via-cyan-600 to-cyan-500 hover:from-blue-500 hover:to-cyan-400 text-white text-xs font-bold shadow-lg shadow-blue-600/30 hover:shadow-cyan-500/20 transition-all duration-200 active:scale-95"
            >
              <Zap className="w-3.5 h-3.5 fill-white" />
              <span>Buy Now</span>
            </button>
          </div>
        </div>

      </div>
    </div>
  );
}
