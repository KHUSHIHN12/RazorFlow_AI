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
      text: `👋 **Welcome to RazorFlow AI!**\n\nI am your **Intelligent Agentic Shopping Assistant** powered by LangGraph & Razorpay.\n\nHow can I help you today? Try typing or speaking:\n• *"Find laptops for coding under ₹60,000"*\n• *"Show me noise cancelling headphones"*\n• *"I need an ergonomic mouse for programming"*\n• *"I need a complete programming setup under ₹70,000"*`,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      products: [],
      confirmationRequired: false,
      activeOrder: null
    }
  ]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [activePaymentModal, setActivePaymentModal] = useState(null);
  const [userBudget, setUserBudget] = useState(null);
  const [conversationContext, setConversationContext] = useState(null);

  // Cart basket totals (all items)
  const cartTotalINR = cart.reduce((sum, item) => sum + item.price * item.quantity, 0);
  const cartTotalPaise = cart.reduce((sum, item) => sum + item.price_paise * item.quantity, 0);
  const itemCount = cart.reduce((sum, item) => sum + item.quantity, 0);

  // Selected checkout items & subtotals
  const selectedCartItems = cart.filter(item => item.selected === true);
  const selectedCount = selectedCartItems.reduce((sum, item) => sum + item.quantity, 0);
  const selectedTotalINR = selectedCartItems.reduce((sum, item) => sum + item.price * item.quantity, 0);
  const selectedTotalPaise = selectedCartItems.reduce((sum, item) => sum + item.price_paise * item.quantity, 0);
  const remainingBudget = userBudget !== null ? (userBudget - selectedTotalINR) : null;

  const toggleSelectItem = (productId) => {
    setCart(prev => prev.map(item => item.product_id === productId ? { ...item, selected: !item.selected } : item));
  };

  const selectAllItems = (status = true) => {
    setCart(prev => prev.map(item => ({ ...item, selected: status })));
  };

  const clearSelection = () => {
    setCart(prev => prev.map(item => ({ ...item, selected: false })));
  };

  const addToCart = async (product) => {
    try {
      const res = await api.updateCart(cart, 'add', product.id, 1);
      // Preserve selection state - default to false for new items
      const updated = res.cart.map(item => {
        const existing = cart.find(i => i.product_id === item.product_id);
        return {
          ...item,
          selected: existing ? Boolean(existing.selected) : false
        };
      });
      setCart(updated);
    } catch (ex) {
      console.error('Failed to add to cart:', ex);
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
          image_url: product.image_url,
          selected: false
        }]);
      }
    }
  };

  const removeFromCart = async (productId) => {
    try {
      const res = await api.updateCart(cart, 'remove', productId, 1);
      setCart(res.cart.map(item => {
        const existing = cart.find(i => i.product_id === item.product_id);
        return { ...item, selected: existing ? Boolean(existing.selected) : false };
      }));
    } catch (ex) {
      setCart(cart.filter(i => i.product_id !== productId));
    }
  };

  const clearCart = () => {
    setCart([]);
  };

  // Buy Now Isolated Checkout Path: selects target product, keeps other cart items intact
  const buySingleProduct = async (product) => {
    let updatedCart = [...cart];
    const existing = updatedCart.find(i => i.product_id === product.id);
    
    if (existing) {
      updatedCart = updatedCart.map(i => i.product_id === product.id ? { ...i, selected: true } : { ...i, selected: false });
    } else {
      updatedCart = [
        ...updatedCart.map(i => ({ ...i, selected: false })),
        {
          product_id: product.id,
          name: product.name,
          price: product.price,
          price_paise: product.price_paise,
          quantity: 1,
          image_url: product.image_url,
          selected: true
        }
      ];
    }
    
    setCart(updatedCart);
    sendMessage(`I want to buy only the ${product.name}. Proceed to checkout.`);
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

    if (!confirmedPay && userText) {
      const budgetMatch = userText.match(/(?:under|below|max|budget|within|rs\.?|₹)?\s*([\d,]{4,8})/i) || userText.match(/(\d+)\s*k\b/i);
      if (budgetMatch) {
        if (budgetMatch[1].toLowerCase().endsWith('k')) {
          setUserBudget(parseFloat(budgetMatch[1]) * 1000);
        } else {
          const val = parseFloat(budgetMatch[1].replace(',', ''));
          if (val >= 500) setUserBudget(val);
        }
      }
    }

    setIsProcessing(true);

    try {
      // Pass cart items and conversation context to backend API
      const res = await api.sendMessage(userText, cart, confirmedPay, conversationContext);
      
      if (res.context) {
        setConversationContext(res.context);
      }

      if (res.cart) {
        setCart(res.cart.map(item => {
          const existing = cart.find(i => i.product_id === item.product_id);
          return {
            ...item,
            selected: existing ? Boolean(existing.selected) : Boolean(item.selected)
          };
        }));
      }

      const agentMsgId = 'agent_' + Date.now();
      const agentMsg = {
        id: agentMsgId,
        sender: 'agent',
        text: res.response,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        products: res.products || [],
        confirmationRequired: res.confirmation_required || false,
        activeOrder: res.active_order || null,
        bundleData: res.bundle_data || null,
        auditLogs: res.audit_logs || []
      };

      setMessages(prev => [...prev, agentMsg]);

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
        
        // Remove ONLY selected/purchased items from cart, leaving unselected items safely in cart!
        setCart(prev => prev.filter(i => i.selected === false));
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
      selectedCartItems,
      selectedCount,
      selectedTotalINR,
      selectedTotalPaise,
      userBudget,
      remainingBudget,
      setUserBudget,
      toggleSelectItem,
      selectAllItems,
      clearSelection,
      buySingleProduct,
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
