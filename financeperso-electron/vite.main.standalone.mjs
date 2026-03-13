import { defineConfig } from 'vite';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

export default defineConfig({
  build: {
    lib: {
      entry: path.resolve(__dirname, 'src/main.js'),
      formats: ['cjs'],
      fileName: () => 'main.js',
    },
    outDir: '.vite/build',
    emptyOutDir: false,
    rollupOptions: {
      external: ['electron', 'node:path', 'node:fs', 'node:http', 'node:module', 'node:url'],
    },
  },
});
