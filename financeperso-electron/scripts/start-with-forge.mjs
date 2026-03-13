import { spawn } from 'child_process';
import { createServer } from 'vite';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const rootDir = path.join(__dirname, '..');

console.log('🚀 Starting development environment...');

// 1. Démarrer Vite
console.log('🌐 Starting Vite dev server...');
const vite = await createServer({
  configFile: path.join(rootDir, 'vite.renderer.config.mjs'),
  root: rootDir,
});

await vite.listen(5173);
console.log('✅ Vite server ready on http://localhost:5173');

// 2. Démarrer electron-forge (qui utilisera notre serveur)
console.log('⚛️  Starting Electron via electron-forge...');
const forge = spawn('npx', ['electron-forge', 'start'], {
  cwd: rootDir,
  env: { 
    ...process.env, 
    VITE_DEV_SERVER_URL: 'http://localhost:5173',
    // Empêche electron-forge de démarrer son propre serveur
    FORGE_VITE_USE_EXTERNAL: 'true'
  },
  stdio: 'inherit'
});

forge.on('close', (code) => {
  console.log(`\n👋 Electron exited with code ${code}`);
  vite.close();
  process.exit(code);
});

process.on('SIGINT', () => {
  console.log('\n👋 Shutting down...');
  forge.kill();
  vite.close();
});
