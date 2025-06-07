import React from "react";
import "./ChatBubble.css";

export default function ChatBubble({ role, content }) {
  const speaker = role === "user" ? "You" : "Assistant";
  return (
    <div
      className={`chat-bubble ${role}-bubble`}
      role="article"
      aria-label={`${speaker} said: ${content}`}
    >
      {content}
    </div>
  );
}
