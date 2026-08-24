import React from 'react';
import { ShoppingCart, Zap, Star, Check, ThumbsUp, AlertCircle } from 'lucide-react';
import { useCart } from '../../context/CartContext';

export default function ProductCard({ product }) {
  const { cart, addToCart, buySingleProduct, sendMessage } = useCart();
  const isInCart = cart.some(i => i.product_id === product.id);

  const handleBuyNow = (e) => {
    e.stopPropagation();
    buySingleProduct(product);
  };

  const handleCompare = (e) => {
    e.stopPropagation();
    sendMessage(`Compare ${product.name} with top alternatives.`);
  };

  const posTheme = product.review_themes?.positive?.[0];
  const negTheme = product.review_themes?.negative?.[0];

  return (
    <div className="group relative rounded-2xl bg-white border border-slate-200 p-4 transition-all duration-300 hover:border-blue-300 hover:shadow-md hover:-translate-y-0.5 flex flex-col sm:flex-row gap-4">
      
      {/* Product Image Preview */}
      <div className="relative sm:w-44 h-44 rounded-xl overflow-hidden bg-slate-100 flex-shrink-0 border border-slate-200 group-hover:border-blue-200 transition-colors">
        <img
          src={product.image_url}
          alt={product.name}
          className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500 ease-out"
        />
        <span className="absolute top-2.5 left-2.5 px-2.5 py-0.5 rounded-full text-[10px] font-mono font-bold uppercase tracking-wider bg-white/90 backdrop-blur-md text-blue-700 border border-blue-200 shadow-2xs">
          {product.category}
        </span>
      </div>

      {/* Product Details */}
      <div className="flex-1 flex flex-col justify-between">
        <div>
          <div className="flex items-start justify-between gap-2">
            <h3 className="text-base font-bold text-slate-900 group-hover:text-blue-600 transition-colors duration-200">
              {product.name}
            </h3>
            
            {/* Rating + Review Count Badge */}
            <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-amber-50 border border-amber-200 text-amber-800 text-xs font-semibold flex-shrink-0">
              <Star className="w-3.5 h-3.5 fill-amber-400 text-amber-400" />
              <span>{product.rating}</span>
              <span className="text-[10px] text-amber-600 font-mono">({product.reviews_count?.toLocaleString() || 0})</span>
            </div>
          </div>

          <p className="text-xs text-slate-600 mt-1.5 line-clamp-2 leading-relaxed">
            {product.description}
          </p>

          {/* Key Specs Tags */}
          {product.specs && (
            <div className="flex flex-wrap gap-1.5 mt-2.5">
              {Object.entries(product.specs).slice(0, 3).map(([key, val]) => (
                <span
                  key={key}
                  className="px-2 py-0.5 rounded-md bg-slate-100 border border-slate-200 text-[10px] text-slate-700 font-mono"
                >
                  <strong className="text-slate-500 font-normal uppercase text-[9px]">{key}:</strong> {val}
                </span>
              ))}
            </div>
          )}

          {/* Review Sentiment Highlights */}
          {(posTheme || negTheme) && (
            <div className="mt-2.5 pt-2 border-t border-slate-100 space-y-1 text-[11px]">
              {posTheme && (
                <div className="flex items-center gap-1.5 text-emerald-700">
                  <ThumbsUp className="w-3 h-3 text-emerald-600 flex-shrink-0" />
                  <span className="truncate"><strong>Key Pro:</strong> {posTheme}</span>
                </div>
              )}
              {negTheme && (
                <div className="flex items-center gap-1.5 text-slate-500">
                  <AlertCircle className="w-3 h-3 text-amber-500 flex-shrink-0" />
                  <span className="truncate"><strong>Drawback:</strong> {negTheme}</span>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Pricing & CTA Actions */}
        <div className="mt-3.5 pt-3 border-t border-slate-100 flex items-center justify-between gap-3">
          <div>
            <span className="text-[10px] text-slate-500 font-mono uppercase tracking-wider">Price</span>
            <div className="text-xl font-extrabold text-slate-900 tracking-tight font-mono">
              ₹{product.price.toLocaleString('en-IN')}
            </div>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={handleCompare}
              className="px-2.5 py-2 rounded-xl text-xs font-medium text-slate-600 hover:text-blue-700 bg-slate-100 hover:bg-blue-50 border border-slate-200 transition-all active:scale-95"
              title="Compare with other products"
            >
              Compare
            </button>

            <button
              onClick={() => addToCart(product)}
              className={`flex items-center gap-1.5 px-3 py-2 rounded-xl text-xs font-semibold transition-all duration-200 active:scale-95 border ${
                isInCart
                  ? 'bg-emerald-50 border-emerald-200 text-emerald-700'
                  : 'bg-slate-100 hover:bg-slate-200/80 text-slate-800 border-slate-200'
              }`}
            >
              {isInCart ? <Check className="w-3.5 h-3.5 text-emerald-600" /> : <ShoppingCart className="w-3.5 h-3.5 text-blue-600" />}
              <span>{isInCart ? 'Added' : 'Add'}</span>
            </button>
            
            <button
              onClick={handleBuyNow}
              className="flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-blue-600 hover:bg-blue-700 text-white text-xs font-bold shadow-xs transition-all duration-200 active:scale-95"
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
