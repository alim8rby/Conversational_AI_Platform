import React, { useRef } from "react";
import "./InputArea.css";

const BASE_URL = import.meta.env.VITE_BACKEND_URL || "";
const CHAT_URL = `${BASE_URL}/chat`;
const TRANSCRIBE_URL = `${BASE_URL}/transcribe`;
const SESSION_KEY = "portfolio-chat-session";

function getSessionId() {
  const existing = localStorage.getItem(SESSION_KEY);
  if (existing) return existing;

  const generated =
    globalThis.crypto?.randomUUID?.() ||
    `session-${Date.now()}-${Math.random().toString(36).slice(2)}`;
  localStorage.setItem(SESSION_KEY, generated);
  return generated;
}

export default function InputArea({
  addMessage,
  recording,
  setRecording,
  recognitionRef,
  audioChunksRef,
  setIsTyping,
}) {
  const textInputRef = useRef("");
  const sessionIdRef = useRef(getSessionId());

  const sendToChat = async (text) => {
    const response = await fetch(CHAT_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ user_id: sessionIdRef.current, text }),
    });
    if (!response.ok) throw new Error("Chat request failed");
    return response.json();
  };

  const handleSend = async () => {
    const trimmed = textInputRef.current.value.trim();
    if (!trimmed) return;

    addMessage("user", trimmed);
    textInputRef.current.value = "";
    setIsTyping(true);
    try {
      const { reply } = await sendToChat(trimmed);
      addMessage("assistant", reply);
    } catch {
      addMessage("assistant", "Something went wrong. Please try again.");
    } finally {
      setIsTyping(false);
    }
  };

  const toggleRecording = async () => {
    if (!recording) {
      if (!navigator.mediaDevices?.getUserMedia) {
        alert("Your browser does not support audio recording.");
        return;
      }
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        const recorder = new MediaRecorder(stream);
        recognitionRef.current = recorder;
        audioChunksRef.current = [];
        recorder.ondataavailable = (event) => {
          if (event.data.size) audioChunksRef.current.push(event.data);
        };
        recorder.onstop = async () => {
          setRecording(false);
          const blob = new Blob(audioChunksRef.current, { type: "audio/webm" });
          addMessage("assistant", "Transcribing…");
          const form = new FormData();
          form.append("file", blob, "speech.webm");
          try {
            const transcriptionResponse = await fetch(TRANSCRIBE_URL, {
              method: "POST",
              body: form,
            });
            if (!transcriptionResponse.ok) throw new Error("Transcription failed");
            const { text } = await transcriptionResponse.json();
            const transcript = (text || "").trim();
            if (!transcript) throw new Error("Empty transcription");

            addMessage("assistant", `You said: "${transcript}"`);
            addMessage("user", transcript);
            setIsTyping(true);
            const { reply } = await sendToChat(transcript);
            addMessage("assistant", reply);
          } catch {
            addMessage("assistant", "Audio processing failed. Please try again.");
          } finally {
            setIsTyping(false);
            stream.getTracks().forEach((track) => track.stop());
          }
        };
        recorder.start();
        setRecording(true);
      } catch {
        alert("Could not start recording.");
      }
    } else {
      recognitionRef.current?.stop();
    }
  };

  return (
    <>
      <form
        className="input-area"
        role="region"
        aria-label="Type a message"
        onSubmit={(event) => {
          event.preventDefault();
          handleSend();
        }}
      >
        <input type="text" placeholder="Type your message…" ref={textInputRef} aria-label="Message" />
        <button type="submit" className="send-btn" aria-label="Send message">
          Send
        </button>
      </form>

      <button
        className={`fab-record ${recording ? "recording" : ""}`}
        onClick={toggleRecording}
        aria-label={recording ? "Stop recording" : "Start recording"}
      >
        {recording ? "■" : "🎤"}
      </button>
    </>
  );
}
