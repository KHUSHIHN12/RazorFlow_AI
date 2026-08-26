import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { CartProvider } from './context/CartContext';
import Navbar from './components/Navbar';
import ChatContainer from './components/Chat/ChatContainer';
import CartDrawer from './components/Cart/CartDrawer';

export default function App() {
  return (
    <CartProvider>
      <Router>
        <div className="min-h-screen bg-slate-50 text-slate-900 flex flex-col font-sans selection:bg-blue-600 selection:text-white">
          <Navbar />
          <main className="flex-1 flex flex-col">
            <Routes>
              <Route path="/" element={<ChatContainer />} />
            </Routes>
          </main>
          <CartDrawer />
        </div>
      </Router>
    </CartProvider>
  );
}
