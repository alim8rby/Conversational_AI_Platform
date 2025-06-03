// src/components/ChatBubble.jsx
import React from "react";
import "./ChatBubble.css";

/**
 * role: "user" or "assistant"
 * content: text
 */
export default function ChatBubble({ role, content }) {
  return (
    <div className={`chat-bubble ${role}-bubble`}>
      {content}
    </div>
  );
}
