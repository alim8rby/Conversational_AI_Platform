import React from 'react';
import './TypingIndicator.css';

export default function TypingIndicator() {
  return (
    <div
      className="typing-indicator"
      role="status"
      aria-label="Assistant is typing"
    >
      <div className="dot" />
      <div className="dot" />
      <div className="dot" />
    </div>
  );
}
