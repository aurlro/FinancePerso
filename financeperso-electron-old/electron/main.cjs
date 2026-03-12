/**
 * Electron Main Process
 * Version CommonJS compatible avec Electron
 */

// Import Electron - méthode compatible
const electron = require('electron')
const app = electron.app
const BrowserWindow = electron.BrowserWindow
const ipcMain = electron.ipcMain

const path = require('path')

// En développement, Vite sert sur localhost:5173
const isDev = !app.isPackaged

let mainWindow = null

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    minWidth: 1000,
    minHeight: 600,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      sandbox: true,
      preload: path.join(__dirname, 'preload.cjs'),
    },
    show: false,
  })

  // Charger l'URL
  if (isDev) {
    mainWindow.loadURL('http://localhost:5173')
    mainWindow.webContents.openDevTools()
  } else {
    mainWindow.loadFile(path.join(__dirname, '../dist/index.html'))
  }

  mainWindow.once('ready-to-show', () => {
    mainWindow.show()
  })

  mainWindow.on('closed', () => {
    mainWindow = null
  })
}

// IPC Handlers
ipcMain.handle('app:get-version', () => {
  return app.getVersion()
})

ipcMain.handle('app:get-path', (_, name) => {
  return app.getPath(name)
})

// App events
app.whenReady().then(createWindow)

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit()
  }
})

app.on('activate', () => {
  if (mainWindow === null) {
    createWindow()
  }
})

console.log('🚀 Electron main process started')
