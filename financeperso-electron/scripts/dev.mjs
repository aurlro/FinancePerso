import { spawn } from 'child_process';
import { createServer } from 'vite';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const rootDir = path.join(__dirname, '..');

console.log('🚀 Starting development server...');

// 1. Start Vite dev server
const vite = await createServer({
  configFile: path.join(rootDir, 'vite.renderer.config.mjs'),
  root: rootDir,
});

await vite.listen(5173);
console.log('✅ Vite server ready on http://localhost:5173');

// 2. Build main and preload
console.log('🔨 Building main process...');
await new Promise((resolve, reject) => {
  const build = spawn('npx', ['vite', 'build', '--config', 'vite.main.config.mjs'], {
    cwd: rootDir,
    stdio: 'inherit'
  });
  build.on('close', (code) => code === 0 ? resolve() : reject(new Error(`Build failed: ${code}`)));
});

console.log('🔨 Building preload...');
await new Promise((resolve, reject) => {
  const build = spawn('npx', ['vite', 'build', '--config', 'vite.preload.config.mjs'], {
    cwd: rootDir,
    stdio: 'inherit'
  });
  build.on('close', (code) => code === 0 ? resolve() : reject(new Error(`Build failed: ${code}`)));
});

// 3. Start Electron
console.log('🚀 Starting Electron...');
const electron = spawn('npx', ['electron', '.vite/build/main.js'], {
  cwd: rootDir,
  env: { ...process.env, VITE_DEV_SERVER_URL: 'http://localhost:5173' },
  stdio: 'inherit'
});

electron.on('close', (code) => {
  console.log(`Electron exited with code ${code}`);
  vite.close();
  process.exit(code);
});

process.on('SIGINT', () => {
  console.log('\n👋 Shutting down...');
  electron.kill();
  vite.close();
});
