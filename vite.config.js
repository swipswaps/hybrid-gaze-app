import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  base: './',
  build: {
    sourcemap: true,
    rollupOptions: {
      onwarn(warning, warn) {
        console.warn(`[BUILD_BLOCKER_FLAG]: ${warning.code} -> ${warning.message}`);
        warn(warning);
      }
    }
  }
});
