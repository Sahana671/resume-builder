import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Vite configuration for the AI Resume Screening System frontend.
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
  },
})
