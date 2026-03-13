import { defineConfig } from 'vite';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

export default defineConfig({
  build: {
    lib: {
      entry: path.resolve(__dirname, 'src/preload.js'),
      formats: ['cjs'],
      fileName: () => 'preload.js',
    },
    outDir: '.vite/build',
    emptyOutDir: false,
    rollupOptions: {
      external: ['electron'],
    },
  },
});
