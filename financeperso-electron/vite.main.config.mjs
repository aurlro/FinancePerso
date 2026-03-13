import { defineConfig } from 'vite';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import fs from 'node:fs';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

// Plugin pour copier les fichiers additionnels
const copyFilesPlugin = () => ({
  name: 'copy-files',
  writeBundle() {
    const srcDir = path.resolve(__dirname, 'src/services');
    const electronServicesDir = path.resolve(__dirname, 'electron/services');
    const destDir = path.resolve(__dirname, '.vite/build/services');
    
    if (!fs.existsSync(destDir)) {
      fs.mkdirSync(destDir, { recursive: true });
    }
    
    // Copier depuis src/services
    if (fs.existsSync(path.join(srcDir, 'database.js'))) {
      fs.copyFileSync(
        path.join(srcDir, 'database.js'),
        path.join(destDir, 'database.js')
      );
      console.log('[Build] Copied database.js to', destDir);
    }
    
    if (fs.existsSync(path.join(srcDir, 'file-import.cjs'))) {
      fs.copyFileSync(
        path.join(srcDir, 'file-import.cjs'),
        path.join(destDir, 'file-import.cjs')
      );
      console.log('[Build] Copied file-import.cjs to', destDir);
    }
    
    // Copier depuis electron/services
    if (fs.existsSync(path.join(electronServicesDir, 'ai-service.cjs'))) {
      fs.copyFileSync(
        path.join(electronServicesDir, 'ai-service.cjs'),
        path.join(destDir, 'ai-service.cjs')
      );
      console.log('[Build] Copied ai-service.cjs to', destDir);
    }
    
    if (fs.existsSync(path.join(electronServicesDir, 'updater.cjs'))) {
      fs.copyFileSync(
        path.join(electronServicesDir, 'updater.cjs'),
        path.join(destDir, 'updater.cjs')
      );
      console.log('[Build] Copied updater.cjs to', destDir);
    }
  }
});

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
      external: [
        'electron', 
        'node:path', 
        'node:fs',
        'better-sqlite3'
      ],
    },
  },
  plugins: [copyFilesPlugin()],
});
