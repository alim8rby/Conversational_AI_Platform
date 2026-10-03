import React, { useState, useRef, useEffect } from "react";
import SplashScreen from "./components/SplashScreen";
import Sidebar from "./components/Sidebar";
import SettingsPanel from "./components/SettingsPanel";
import ChatBubble from "./components/ChatBubble";
import TypingIndicator from "./components/TypingIndicator";
import InputArea from "./components/InputArea";
import "./App.css";

export default function App() {
  const [showSplash, setShowSplash] = useState(true);
  useEffect(() => {
    const timer = setTimeout(() => setShowSplash(false), 2500);
    return () => clearTimeout(timer);
  }, []);

  const [theme, setTheme] = useState(localStorage.getItem("theme") || "light");
  useEffect(() => {
    document.documentElement.setAttribute("data-theme", theme);
    localStorage.setItem("theme", theme);
  }, [theme]);

  const [messages, setMessages] = useState([
    {
      role: "assistant",
      content: "Hello! I’m here to support you. What would you like to talk about?",
    },
  ]);
  const [isTyping, setIsTyping] = useState(false);
  const [recording, setRecording] = useState(false);
  const chatWindowRef = useRef(null);
  const recorderRef = useRef(null);
  const audioChunksRef = useRef([]);

  useEffect(() => {
    if (chatWindowRef.current) {
      chatWindowRef.current.scrollTop = chatWindowRef.current.scrollHeight;
    }
  }, [messages, isTyping]);

  const addMessage = (role, content) =>
    setMessages((previous) => [...previous, { role, content }]);

  if (showSplash) return <SplashScreen />;

  return (
    <div className="app-container">
      <Sidebar />
      <main className="chat-main">
        <header className="chat-main__header">
          <h1>How can I assist you today?</h1>
          <p className="portfolio-notice">
            Portfolio demonstration only — not medical advice or emergency support.
          </p>
        </header>

        <section
          className="chat-main__log"
          ref={chatWindowRef}
          role="log"
          aria-live="polite"
          aria-label="Chat conversation"
        >
          {messages.map((message, index) => (
            <ChatBubble key={index} role={message.role} content={message.content} />
          ))}
          {isTyping && <TypingIndicator />}
        </section>

        <InputArea
          addMessage={addMessage}
          recording={recording}
          setRecording={setRecording}
          recognitionRef={recorderRef}
          audioChunksRef={audioChunksRef}
          setIsTyping={setIsTyping}
        />
      </main>
      <SettingsPanel theme={theme} setTheme={setTheme} />
    </div>
  );
}
