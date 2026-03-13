console.log('Process versions:', process.versions);
console.log('Electron:', process.versions.electron);

const electron = require('electron');
console.log('Type of electron:', typeof electron);
console.log('Keys:', Object.keys(electron).slice(0, 10));

if (typeof electron === 'object' && electron.app) {
  console.log('app available:', typeof electron.app);
} else {
  console.log('electron value:', electron);
}
