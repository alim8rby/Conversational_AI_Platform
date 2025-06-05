// vite.config.js
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      // In development, proxy /transcribe → http://localhost:8002/transcribe
      "/transcribe": {
        target: "http://localhost:8002",
        changeOrigin: true,
      },
      // In development, proxy /chat → http://localhost:8002/chat
      "/chat": {
        target: "http://localhost:8002",
        changeOrigin: true,
      },
    },
  },
});
