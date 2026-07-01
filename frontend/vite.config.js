import { defineConfig } from 'vite'

export default defineConfig({
  root: '.',
  server: {
    port: 3000,
    open: true,
    host: true,
    allowedHosts: ['stool-twitter-props.ngrok-free.dev'],
    proxy: {
      '/api': {
        target: 'http://backend:8000',
        changeOrigin: true,
        headers: { 'Origin': 'http://localhost:3000' }
      }
    }
  },
  build: {
    outDir: 'dist'
  }
})
