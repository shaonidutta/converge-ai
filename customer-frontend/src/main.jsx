import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import "./index.css";
import App from "./App.jsx";
import { AuthProvider } from "./context/AuthContext";
import { CartProvider } from "./context/CartContext";
import { ChatProvider } from "./context/ChatContext";

createRoot(document.getElementById("root")).render(
  <StrictMode>
    <AuthProvider>
      <CartProvider>
        <ChatProvider>
          <App />
        </ChatProvider>
      </CartProvider>
    </AuthProvider>
  </StrictMode>
);
