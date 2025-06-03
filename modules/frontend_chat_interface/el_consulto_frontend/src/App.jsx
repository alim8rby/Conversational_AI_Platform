// src/App.jsx
import React, { useState, useRef, useEffect } from "react";
import ChatBubble from "./components/ChatBubble";
import InputArea from "./components/InputArea";
import SplashScreen from "./components/SplashScreen";
import "./App.css";

export default function App() {
  const [messages, setMessages] = useState([]);
  const [recording, setRecording] = useState(false);
  const [showSplash, setShowSplash] = useState(true);
  const [theme, setTheme] = useState(
    localStorage.getItem("theme") ||
      (window.matchMedia("(prefers-color-scheme: dark)").matches
        ? "dark"
        : "light")
  );

  // Refs for voice‐recording logic (no change)
  const recognitionRef = useRef(null);
  const audioChunksRef = useRef([]);

  // NEW: Ref for the chat‐window div
  const chatWindowRef = useRef(null);

  // Hide splash screen after 2.5 seconds
  useEffect(() => {
    const timer = setTimeout(() => setShowSplash(false), 2500);
    return () => clearTimeout(timer);
  }, []);

  // Apply theme and persist it
  useEffect(() => {
    document.documentElement.setAttribute("data-theme", theme);
    localStorage.setItem("theme", theme);
  }, [theme]);

  const toggleTheme = () =>
    setTheme((cur) => (cur === "light" ? "dark" : "light"));

  // Helper to append a new message to state
  const addMessage = (role, content) => {
    setMessages((prev) => [...prev, { role, content }]);
  };

  // NEW: Whenever `messages` changes, scroll chatWindow to bottom
  useEffect(() => {
    if (chatWindowRef.current) {
      // - scrollHeight = total height of content
      // - clientHeight = visible height
      chatWindowRef.current.scrollTop = chatWindowRef.current.scrollHeight;
    }
  }, [messages]);

  return (
    <>
      {showSplash && <SplashScreen />}

      <div className="app-container">
        <header className="chat-header">
          <h1>El Consulto</h1>
          <button className="theme-toggle" onClick={toggleTheme}>
            {theme === "light" ? "🌙" : "☀️"}
          </button>
        </header>

        {/* 
          MAIN CHAT AREA
          -> We attach `ref={chatWindowRef}` so we can scroll it programmatically.
        */}
        <main className="chat-window" ref={chatWindowRef}>
          {messages.map((msg, idx) => (
            <ChatBubble key={idx} role={msg.role} content={msg.content} />
          ))}
        </main>

        <InputArea
          addMessage={addMessage}
          recording={recording}
          setRecording={setRecording}
          recognitionRef={recognitionRef}
          audioChunksRef={audioChunksRef}
        />
      </div>
    </>
  );
}
