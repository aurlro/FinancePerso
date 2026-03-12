const electron = require('electron')
console.log('Electron module type:', typeof electron)
console.log('Electron keys:', Object.keys(electron).slice(0, 10))
console.log('app:', typeof electron.app)
if (electron.app) {
  console.log('app.isPackaged:', electron.app.isPackaged)
}
