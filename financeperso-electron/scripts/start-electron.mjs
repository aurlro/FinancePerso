#!/usr/bin/env node
import { spawn } from 'child_process';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const rootDir = path.join(__dirname, '..');

console.log('🚀 Starting FinancePerso Electron + SQLite...');
console.log('');

// Important: désactive ELECTRON_RUN_AS_NODE pour que Electron fonctionne correctement
const env = {
  ...process.env,
  ELECTRON_RUN_AS_NODE: '0'
};

const forge = spawn('npx', ['electron-forge', 'start'], {
  cwd: rootDir,
  env,
  stdio: 'inherit'
});

forge.on('close', (code) => {
  console.log(`\n👋 Electron exited with code ${code}`);
  process.exit(code);
});

process.on('SIGINT', () => {
  console.log('\n👋 Shutting down...');
  forge.kill('SIGINT');
});
