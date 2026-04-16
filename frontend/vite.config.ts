import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': {
        // BACKEND_URL is set to http://backend:8000 by docker-compose so the
        // Vite dev server (running inside Docker) can reach the backend container.
        // Falls back to localhost when running Vite directly on the host.
        target: process.env.BACKEND_URL || 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
    },
  },
})
