import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  root: '.',
  base: './',
  build: {
    outDir: 'dist',
    emptyOutDir: true,
  },
  optimizeDeps: {
    exclude: ['better-sqlite3'],
  },
})
