// src/components/InputArea.jsx

import React, { useRef } from "react";
import "./InputArea.css";

// In DEV, relative URLs will be proxied by Vite to your local FastAPI.
// In PROD, we override BASE_URL to point at the deployed backend.
const BASE_URL = import.meta.env.PROD
  ? "https://el-consulto-mvp-static.onrender.com/"
  : ""; // empty string means “same host/origin” in dev

// Now compose full endpoints
const CHAT_URL = `${BASE_URL}/chat`;
const TRANSCRIBE_URL = `${BASE_URL}/transcribe`;

// For now, hardcode a demo user_id
const USER_ID = "demo_user";

export default function InputArea({
  addMessage,
  recording,
  setRecording,
  recognitionRef,
  audioChunksRef,
}) {
  const textInputRef = useRef("");

  // 1) Send a typed message to the chat backend:
  const handleSend = async () => {
    const trimmed = textInputRef.current.value.trim();
    if (!trimmed) return;

    // Show the user’s message immediately in the UI
    addMessage("user", trimmed);

    // Clear the text box
    textInputRef.current.value = "";

    // Call /chat endpoint and show the assistant’s reply
    try {
      const resp = await fetch(CHAT_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          user_id: USER_ID,
          text: trimmed,
        }),
      });

      if (!resp.ok) {
        console.error("Chat API returned status:", resp.status);
        addMessage(
          "assistant",
          "⚠️ Sorry, I couldn’t process that. Please try again."
        );
        return;
      }

      const data = await resp.json(); // { reply: "…" }
      addMessage("assistant", data.reply);
    } catch (err) {
      console.error("Error calling /chat:", err);
      addMessage(
        "assistant",
        "⚠️ Sorry, I couldn’t reach the server. Please try again."
      );
    }
  };

  // 2) Start or stop recording + transcription + chat
  const toggleRecording = async () => {
    if (!recording) {
      // ====== START RECORDING ======
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
          if (event.data.size > 0) {
            audioChunksRef.current.push(event.data);
          }
        };

        recorder.onstop = async () => {
          setRecording(false);

          const audioBlob = new Blob(audioChunksRef.current, { type: "audio/webm" });

          // Tell user we’re transcribing
          addMessage("assistant", "🎙️ Transcribing your voice…");

          const formData = new FormData();
          formData.append("file", audioBlob, "speech.webm");

          try {
            const resp = await fetch(TRANSCRIBE_URL, {
              method: "POST",
              body: formData,
            });
            const data = await resp.json();
            const transcript = data.text.trim();

            // Show “You said:” and the user transcript
            addMessage("assistant", `📝 You said: "${transcript}"`);
            addMessage("user", transcript);

            // Now send that transcript to /chat
            try {
              const chatResp = await fetch(CHAT_URL, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                  user_id: USER_ID,
                  text: transcript,
                }),
              });
              if (!chatResp.ok) {
                console.error("Chat API returned status:", chatResp.status);
                addMessage(
                  "assistant",
                  "⚠️ Sorry, something went wrong when fetching the response."
                );
                return;
              }
              const chatData = await chatResp.json();
              addMessage("assistant", chatData.reply);
            } catch (chatErr) {
              console.error("Error calling /chat:", chatErr);
              addMessage(
                "assistant",
                "⚠️ Sorry, something went wrong when fetching the response."
              );
            }
          } catch (transErr) {
            console.error("Error calling /transcribe:", transErr);
            addMessage("assistant", "⚠️ Transcription failed. Please try again.");
          }

          stream.getTracks().forEach((t) => t.stop());
        };

        recorder.start();
        setRecording(true);
      } catch (err) {
        console.error("Could not start microphone:", err);
        alert("Unable to record: " + err.message);
      }
    } else {
      // ====== STOP RECORDING ======
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
      // `setRecording(false)` happens inside recorder.onstop()
    }
  };

  return (
    <div className="input-area">
      <input
        type="text"
        placeholder="Type your message…"
        ref={textInputRef}
        onKeyDown={(e) => {
          if (e.key === "Enter") {
            e.preventDefault();
            handleSend();
          }
        }}
      />

      <button className="send-btn" onClick={handleSend}>
        Send
      </button>

      <button
        className={`record-btn ${recording ? "recording" : ""}`}
        onClick={toggleRecording}
      >
        {recording ? "Stop" : "Record"}
      </button>
    </div>
  );
}
