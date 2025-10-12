import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src'),
    },
  },
  server: {
    host: true,          // 0.0.0.0 în Codespaces
    port: Number(process.env.PORT) || 5173,
    strictPort: true,
    cors: true
  },
  preview: {
    host: true,
    port: 5173
  }
});
