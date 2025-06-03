// vite.config.js
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      // Proxy any /transcribe request to your backend (e.g. running on port 5000)
      '/transcribe': {
        target: 'http://localhost:5000',
        changeOrigin: true,
      },
    },
  },
});
