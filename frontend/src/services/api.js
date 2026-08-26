import axios from 'axios';

const API_BASE = '/api';

export const api = {
  async sendMessage(message, cart = [], confirmedPay = false) {
    const response = await axios.post(`${API_BASE}/chat`, {
      message,
      cart,
      confirmed_pay: confirmedPay
    });
    return response.data;
  },

  async updateCart(cart, action, productId, quantity = 1) {
    const response = await axios.post(`${API_BASE}/cart`, {
      cart,
      action,
      product_id: productId,
      quantity
    });
    return response.data;
  },

  async createRazorpayOrder(amountPaise, currency = 'INR') {
    const response = await axios.post(`${API_BASE}/payment/create-order`, {
      amount_paise: Math.round(Number(amountPaise)),
      currency
    });
    return response.data;
  },

  async verifyPayment(razorpayOrderId, razorpayPaymentId, razorpaySignature, amountPaise) {
    const response = await axios.post(`${API_BASE}/payment/verify`, {
      razorpay_order_id: razorpayOrderId,
      razorpay_payment_id: razorpayPaymentId,
      razorpay_signature: razorpaySignature,
      amount_paise: amountPaise
    });
    return response.data;
  }
};
