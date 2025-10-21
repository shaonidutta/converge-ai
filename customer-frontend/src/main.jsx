import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.jsx'
import { CartProvider } from './context/CartContext'
import { ChatProvider } from './context/ChatContext'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <CartProvider>
      <ChatProvider>
        <App />
      </ChatProvider>
    </CartProvider>
  </StrictMode>,
)
