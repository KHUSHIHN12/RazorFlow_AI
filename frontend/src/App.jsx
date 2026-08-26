import React, { useState } from 'react';
import { BrowserRouter as Router } from 'react-router-dom';
import { CartProvider } from './context/CartContext';
import Sidebar from './components/Sidebar';
import Navbar from './components/Navbar';
import ChatContainer from './components/Chat/ChatContainer';
import ProfileView from './components/Profile/ProfileView';
import CartDrawer from './components/Cart/CartDrawer';

export default function App() {
  const [activeTab, setActiveTab] = useState('chat');
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  return (
    <CartProvider>
      <Router>
        <div className="min-h-screen h-screen bg-slate-50 text-slate-900 flex overflow-hidden font-sans selection:bg-blue-600 selection:text-white">
          
          {/* Left Sidebar */}
          <Sidebar
            activeTab={activeTab}
            setActiveTab={setActiveTab}
            isOpen={isSidebarOpen}
            setIsOpen={setIsSidebarOpen}
          />

          {/* Main Layout Area */}
          <div className="flex-1 flex flex-col h-full overflow-hidden">
            <Navbar onMenuClick={() => setIsSidebarOpen(true)} />
            
            <main className="flex-1 overflow-y-auto">
              {activeTab === 'chat' ? (
                <ChatContainer />
              ) : (
                <ProfileView />
              )}
            </main>
          </div>

          {/* Slide-over Cart Drawer */}
          <CartDrawer />
        </div>
      </Router>
    </CartProvider>
  );
}
