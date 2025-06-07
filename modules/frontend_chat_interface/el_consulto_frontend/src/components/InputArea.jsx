import React, { useRef } from "react";
import "./InputArea.css";

const BASE_URL = import.meta.env.DEV
  ? ""
  : "https://el-consulto-backend.onrender.com";
const CHAT_URL = `${BASE_URL}/chat`;
const TRANSCRIBE_URL = `${BASE_URL}/transcribe`;
const USER_ID = "demo_user";

export default function InputArea({
  addMessage,
  recording,
  setRecording,
  recognitionRef,
  audioChunksRef,
}) {
  const textInputRef = useRef("");

  const handleSend = async () => {
    const trimmed = textInputRef.current.value.trim();
    if (!trimmed) return;

    addMessage("user", trimmed);
    textInputRef.current.value = "";

    try {
      const resp = await fetch(CHAT_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_id: USER_ID, text: trimmed }),
      });
      if (!resp.ok) {
        console.error("Chat API error:", resp.status);
        addMessage("assistant", "⚠️ Sorry, I couldn’t process that. Please try again.");
        return;
      }
      const { reply } = await resp.json();
      addMessage("assistant", reply);
    } catch (err) {
      console.error("Error calling /chat:", err);
      addMessage("assistant", "⚠️ Couldn’t reach the server. Please try again.");
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

        recorder.ondataavailable = (e) => {
          if (e.data.size > 0) audioChunksRef.current.push(e.data);
        };

        recorder.onstop = async () => {
          setRecording(false);
          const audioBlob = new Blob(audioChunksRef.current, { type: "audio/webm" });
          addMessage("assistant", "🎙️ Transcribing your voice…");

          const formData = new FormData();
          formData.append("file", audioBlob, "speech.webm");

          try {
            const resp = await fetch(TRANSCRIBE_URL, { method: "POST", body: formData });
            const { text } = await resp.json();
            const transcript = text.trim();
            addMessage("assistant", `📝 You said: "${transcript}"`);
            addMessage("user", transcript);

            // send to chat
            const chatResp = await fetch(CHAT_URL, {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({ user_id: USER_ID, text: transcript }),
            });
            if (!chatResp.ok) {
              console.error("Chat API error:", chatResp.status);
              addMessage("assistant", "⚠️ Something went wrong fetching the response.");
              return;
            }
            const { reply } = await chatResp.json();
            addMessage("assistant", reply);
          } catch (err) {
            console.error("Transcribe/chat error:", err);
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
      recognitionRef.current?.stop();
    }
  };

  return (
    <form
      className="input-area"
      role="region"
      aria-label="Message input area"
      onSubmit={(e) => {
        e.preventDefault();
        handleSend();
      }}
    >
      <input
        type="text"
        aria-label="Type your message"
        placeholder="Type your message…"
        ref={textInputRef}
        onKeyDown={(e) => {
          if (e.key === "Enter") {
            e.preventDefault();
            handleSend();
          }
        }}
      />

      <button
        type="submit"
        className="send-btn"
        aria-label="Send message"
      >
        Send
      </button>

      <button
        type="button"
        className={`record-btn ${recording ? "recording" : ""}`}
        onClick={toggleRecording}
        aria-label={recording ? "Stop recording" : "Start recording"}
      >
        {recording ? "Stop" : "Record"}
      </button>
    </form>
  );
}
