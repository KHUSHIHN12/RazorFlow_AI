import React, { createContext, useContext, useState } from 'react';
import { api } from '../services/api';

const CartContext = createContext();

export function CartProvider({ children }) {
  const [cart, setCart] = useState([]);
  const [isCartOpen, setIsCartOpen] = useState(false);
  const [messages, setMessages] = useState([
    {
      id: 'msg_welcome',
      sender: 'agent',
      text: `👋 **Welcome to RazorFlow AI!**\n\nI am your **Intelligent Agentic Shopping Assistant** powered by LangGraph & Razorpay.\n\nHow can I help you today? Try typing something like:\n• *"Find laptops for coding under ₹60,000"*\n• *"Show me active noise cancelling headphones"*\n• *"I need an ergonomic mouse for programming"*`,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      products: [],
      confirmationRequired: false,
      activeOrder: null
    }
  ]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [activePaymentModal, setActivePaymentModal] = useState(null);

  const cartTotalINR = cart.reduce((sum, item) => sum + item.price * item.quantity, 0);
  const cartTotalPaise = cart.reduce((sum, item) => sum + item.price_paise * item.quantity, 0);
  const itemCount = cart.reduce((sum, item) => sum + item.quantity, 0);

  const addToCart = async (product) => {
    try {
      const res = await api.updateCart(cart, 'add', product.id, 1);
      setCart(res.cart);
    } catch (ex) {
      console.error('Failed to add to cart:', ex);
      // Fallback local addition
      const existing = cart.find(i => i.product_id === product.id);
      if (existing) {
        setCart(cart.map(i => i.product_id === product.id ? { ...i, quantity: i.quantity + 1 } : i));
      } else {
        setCart([...cart, {
          product_id: product.id,
          name: product.name,
          price: product.price,
          price_paise: product.price_paise,
          quantity: 1,
          image_url: product.image_url
        }]);
      }
    }
  };

  const removeFromCart = async (productId) => {
    try {
      const res = await api.updateCart(cart, 'remove', productId, 1);
      setCart(res.cart);
    } catch (ex) {
      setCart(cart.filter(i => i.product_id !== productId));
    }
  };

  const clearCart = () => {
    setCart([]);
  };

  const sendMessage = async (userText, confirmedPay = false) => {
    if (!userText.trim() && !confirmedPay) return;

    const userMsgId = 'user_' + Date.now();
    const currentTimestamp = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

    if (!confirmedPay) {
      setMessages(prev => [
        ...prev,
        {
          id: userMsgId,
          sender: 'user',
          text: userText,
          timestamp: currentTimestamp
        }
      ]);
    }

    setIsProcessing(true);

    try {
      const res = await api.sendMessage(userText, cart, confirmedPay);
      
      if (res.cart) {
        setCart(res.cart);
      }

      const agentMsgId = 'agent_' + Date.now();
      const agentMsg = {
        id: agentMsgId,
        sender: 'agent',
        text: res.response,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        products: res.products || [],
        confirmationRequired: res.confirmation_required || false,
        activeOrder: res.active_order || null
      };

      setMessages(prev => [...prev, agentMsg]);

      // If active order returned, set active payment modal state
      if (res.active_order) {
        setActivePaymentModal(res.active_order);
      }

    } catch (ex) {
      console.error('Chat error:', ex);
      setMessages(prev => [
        ...prev,
        {
          id: 'err_' + Date.now(),
          sender: 'agent',
          text: '⚠️ Connection issue communicating with RazorFlow AI agent backend. Please ensure backend server is running.',
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        }
      ]);
    } finally {
      setIsProcessing(false);
    }
  };

  const handlePaymentSuccess = async (orderId, paymentId, signature, amountPaise) => {
    try {
      const verifyRes = await api.verifyPayment(orderId, paymentId, signature, amountPaise);
      
      if (verifyRes.verified) {
        const receiptMsg = {
          id: 'receipt_' + Date.now(),
          sender: 'agent',
          text: `🎉 **Payment Verified Successfully!**\n\n` +
                `• **Razorpay Payment ID:** \`${paymentId}\`\n` +
                `• **Order ID:** \`${orderId}\`\n` +
                `• **Amount Paid:** ₹${(amountPaise / 100).toLocaleString('en-IN')}\n` +
                `• **Status:** Verified Signature (SHA256 HMAC)\n\n` +
                `Thank you for shopping with RazorFlow AI! Your items are now being prepared for express delivery. 🚚⚡`,
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
          isReceipt: true,
          paymentId,
          orderId
        };
        setMessages(prev => [...prev, receiptMsg]);
        clearCart();
        setActivePaymentModal(null);
      }
    } catch (ex) {
      console.error('Payment verification error:', ex);
    }
  };

  return (
    <CartContext.Provider value={{
      cart,
      itemCount,
      cartTotalINR,
      cartTotalPaise,
      isCartOpen,
      setIsCartOpen,
      messages,
      isProcessing,
      activePaymentModal,
      setActivePaymentModal,
      addToCart,
      removeFromCart,
      clearCart,
      sendMessage,
      handlePaymentSuccess
    }}>
      {children}
    </CartContext.Provider>
  );
}

export function useCart() {
  return useContext(CartContext);
}
