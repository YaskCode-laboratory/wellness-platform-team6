import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Configuración para AWS Amplify / SPA deployment
export default defineConfig({
  plugins: [react()],
  base: '/',
})
