import React, { useState, useRef, useEffect } from "react";
import SplashScreen from "./components/SplashScreen";
import Sidebar from "./components/Sidebar";
import SettingsPanel from "./components/SettingsPanel";
import ChatBubble from "./components/ChatBubble";
import TypingIndicator from "./components/TypingIndicator";
import InputArea from "./components/InputArea";
import "./App.css";

export default function App() {
  // splash
  const [showSplash, setShowSplash] = useState(true);
  useEffect(() => {
    const t = setTimeout(() => setShowSplash(false), 2500);
    return () => clearTimeout(t);
  }, []);

  // theme
  const [theme, setTheme] = useState(localStorage.getItem("theme") || "light");
  useEffect(() => {
    document.documentElement.setAttribute("data-theme", theme);
    localStorage.setItem("theme", theme);
  }, [theme]);

  // chat
  const [messages, setMessages] = useState([
    {
      role: "assistant",
      content:
        "Hello! I’m here to support you. What would you like to talk about?",
    },
  ]);
  const [isTyping, setIsTyping] = useState(false);
  const chatWindowRef = useRef(null);

  // auto-scroll
  useEffect(() => {
    if (chatWindowRef.current) {
      chatWindowRef.current.scrollTop =
        chatWindowRef.current.scrollHeight;
    }
  }, [messages, isTyping]);

  const addMessage = (role, content) =>
    setMessages((prev) => [...prev, { role, content }]);

  // show splash until ready
  if (showSplash) return <SplashScreen />;

  return (
    <div className="app-container">
      <Sidebar />

      <main className="chat-main">
        <header className="chat-main__header">
          <h1>How can I assist you today?</h1>
        </header>

        <section
          className="chat-main__log"
          ref={chatWindowRef}
          role="log"
          aria-live="polite"
          aria-label="Chat conversation"
        >
          {messages.map((m, i) => (
            <ChatBubble key={i} role={m.role} content={m.content} />
          ))}
          {isTyping && <TypingIndicator />}
        </section>

        <InputArea addMessage={addMessage} setIsTyping={setIsTyping} />
      </main>

      <SettingsPanel theme={theme} setTheme={setTheme} />
    </div>
  );
}
