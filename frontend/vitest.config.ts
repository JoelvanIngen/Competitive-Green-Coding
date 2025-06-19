import { defineConfig } from 'vitest/config';
import path from 'path';

export default defineConfig({
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./tests/setup/vitest.setup.ts'],
  },

  resolve: {
    alias: {
      '@': path.resolve(__dirname),

      // 👇 FOR *ALL* CJS & ESM IMPORTS
      react:     path.resolve(__dirname, 'node_modules/react'),
      'react-dom': path.resolve(__dirname, 'node_modules/react-dom'),
    },
    // still useful for deep ESM deps
    dedupe: ['react', 'react-dom'],
  },
});
