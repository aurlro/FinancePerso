import { spawn } from 'child_process';
import { createServer } from 'vite';
import path from 'path';
import { fileURLToPath } from 'url';
import http from 'http';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const rootDir = path.join(__dirname, '..');

console.log('🚀 Starting FinancePerso...');

// Attendre que le serveur soit prêt
async function waitForServer(url, timeout = 30000) {
  const start = Date.now();
  while (Date.now() - start < timeout) {
    try {
      const response = await new Promise((resolve, reject) => {
        const req = http.get(url, (res) => resolve(res.statusCode));
        req.on('error', reject);
        req.setTimeout(1000, () => req.destroy());
      });
      if (response === 200) return true;
    } catch (e) {}
    await new Promise(r => setTimeout(r, 500));
  }
  throw new Error('Timeout waiting for server');
}

// 1. Build main et preload
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

// 2. Démarrer Vite
console.log('🌐 Starting Vite dev server...');
const vite = await createServer({
  configFile: path.join(rootDir, 'vite.renderer.config.mjs'),
  root: rootDir,
});

await vite.listen(5173);
console.log('✅ Vite server ready on http://localhost:5173');

// Vérifier que le serveur répond
try {
  await waitForServer('http://localhost:5173');
  console.log('✅ Server is responding');
} catch (e) {
  console.error('❌ Server not responding:', e.message);
  process.exit(1);
}

// 3. Démarrer Electron avec environnement nettoyé
console.log('⚛️  Starting Electron...');

// Crée un environnement propre sans ELECTRON_RUN_AS_NODE
const env = { ...process.env };
delete env.ELECTRON_RUN_AS_NODE;

const electron = spawn('npx', ['electron', '.vite/build/main.js'], {
  cwd: rootDir,
  env: {
    ...env,
    VITE_DEV_SERVER_URL: 'http://localhost:5173'
  },
  stdio: 'inherit'
});

electron.on('close', (code) => {
  console.log(`\n👋 Electron exited with code ${code}`);
  vite.close();
  process.exit(code);
});

process.on('SIGINT', () => {
  console.log('\n👋 Shutting down...');
  electron.kill();
  vite.close();
});
