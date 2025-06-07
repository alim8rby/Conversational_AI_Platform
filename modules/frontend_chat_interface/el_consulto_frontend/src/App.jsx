import React, { useState, useRef, useEffect } from "react";
import ChatBubble from "./components/ChatBubble";
import InputArea from "./components/InputArea";
import TypingIndicator from "./components/TypingIndicator";
import SplashScreen from "./components/SplashScreen";
import "./App.css";

export default function App() {
  const [messages, setMessages] = useState([]);
  const [recording, setRecording] = useState(false);
  const [isTyping, setIsTyping] = useState(false);
  const [showSplash, setShowSplash] = useState(true);
  const [theme, setTheme] = useState(
    localStorage.getItem("theme") ||
      (window.matchMedia("(prefers-color-scheme: dark)").matches
        ? "dark"
        : "light")
  );

  const recognitionRef = useRef(null);
  const audioChunksRef = useRef([]);
  const chatWindowRef = useRef(null);

  // Splash timeout
  useEffect(() => {
    const timer = setTimeout(() => setShowSplash(false), 2500);
    return () => clearTimeout(timer);
  }, []);

  // Theme persistence
  useEffect(() => {
    document.documentElement.setAttribute("data-theme", theme);
    localStorage.setItem("theme", theme);
  }, [theme]);

  // Auto-scroll
  useEffect(() => {
    if (chatWindowRef.current) {
      chatWindowRef.current.scrollTop = chatWindowRef.current.scrollHeight;
    }
  }, [messages, isTyping]);

  const toggleTheme = () =>
    setTheme((cur) => (cur === "light" ? "dark" : "light"));

  const addMessage = (role, content) => {
    setMessages((prev) => [...prev, { role, content }]);
  };

  return (
    <>
      {showSplash && <SplashScreen />}

      <div className="app-container">
        <header className="chat-header">
          <h1>El Consulto</h1>
          <button
            className="theme-toggle"
            onClick={toggleTheme}
            aria-label="Toggle light or dark theme"
          >
            {theme === "light" ? "🌙" : "☀️"}
          </button>
        </header>

        <main
          className="chat-window"
          ref={chatWindowRef}
          role="log"
          aria-live="polite"
          aria-label="Chat messages"
        >
          {messages.map((msg, idx) => (
            <ChatBubble key={idx} role={msg.role} content={msg.content} />
          ))}

          {/* typing dots */}
          {isTyping && <TypingIndicator />}
        </main>

        <InputArea
          addMessage={addMessage}
          recording={recording}
          setRecording={setRecording}
          recognitionRef={recognitionRef}
          audioChunksRef={audioChunksRef}
          setIsTyping={setIsTyping}
        />
      </div>
    </>
  );
}
