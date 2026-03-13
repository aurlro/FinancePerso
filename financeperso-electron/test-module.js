// Essaie différentes façons d'accéder au module electron

// Méthode 1: require standard
const electron1 = require('electron');
console.log('Method 1 - require electron:', typeof electron1, electron1 === require('electron'));

// Méthode 2: process._linkedBinding
try {
  const electron2 = process._linkedBinding('electron');
  console.log('Method 2 - _linkedBinding:', typeof electron2);
} catch (e) {
  console.log('Method 2 - _linkedBinding failed:', e.message);
}

// Méthode 3: Module._load
try {
  const Module = require('module');
  const electron3 = Module._load('electron', module);
  console.log('Method 3 - Module._load:', typeof electron3);
} catch (e) {
  console.log('Method 3 - Module._load failed:', e.message);
}

// Méthode 4: global
try {
  const electron4 = global.require('electron');
  console.log('Method 4 - global.require:', typeof electron4);
} catch (e) {
  console.log('Method 4 - global.require failed:', e.message);
}

// Méthode 5: Vérifie si on est dans Electron
console.log('process.versions.electron:', process.versions.electron);
console.log('process.type:', process.type);
