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
  setIsTyping,
}) {
  const textInputRef = useRef("");

  const handleSend = async () => {
    const trimmed = textInputRef.current.value.trim();
    if (!trimmed) return;
    addMessage("user", trimmed);
    textInputRef.current.value = "";
    setIsTyping(true);
    try {
      const resp = await fetch(CHAT_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_id: USER_ID, text: trimmed }),
      });
      const { reply } = await resp.json();
      addMessage("assistant", reply);
    } catch {
      addMessage("assistant", "⚠️ Something went wrong.");
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
        recorder.ondataavailable = (e) => {
          if (e.data.size) audioChunksRef.current.push(e.data);
        };
        recorder.onstop = async () => {
          setRecording(false);
          const blob = new Blob(audioChunksRef.current, {type:"audio/webm"});
          addMessage("assistant", "🎙️ Transcribing…");
          const form = new FormData();
          form.append("file", blob, "speech.webm");
          try {
            const tResp = await fetch(TRANSCRIBE_URL, { method: "POST", body: form });
            const { text } = await tResp.json();
            const transcript = text.trim();
            addMessage("assistant", `📝 You said: "${transcript}"`);
            addMessage("user", transcript);
            setIsTyping(true);
            const cResp = await fetch(CHAT_URL, {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({ user_id: USER_ID, text: transcript }),
            });
            const { reply } = await cResp.json();
            addMessage("assistant", reply);
          } catch {
            addMessage("assistant", "⚠️ Transcription failed.");
          } finally {
            setIsTyping(false);
            stream.getTracks().forEach((t) => t.stop());
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
        onSubmit={(e) => {
          e.preventDefault();
          handleSend();
        }}
      >
        <input
          type="text"
          placeholder="Type your message…"
          ref={textInputRef}
          aria-label="Message"
        />
        <button
          type="submit"
          className="send-btn"
          aria-label="Send message"
        >
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
