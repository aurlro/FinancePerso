/**
 * FinancePerso PWA Support
 * Handles service worker registration and offline functionality
 */

// Register Service Worker
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker
      .register('/app/static/service-worker.js')
      .then((registration) => {
        console.log('[PWA] Service Worker registered:', registration.scope);
        
        // Check for updates
        registration.addEventListener('updatefound', () => {
          const newWorker = registration.installing;
          console.log('[PWA] New Service Worker installing...');
          
          newWorker.addEventListener('statechange', () => {
            if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
              // New version available
              showUpdateNotification();
            }
          });
        });
      })
      .catch((error) => {
        console.error('[PWA] Service Worker registration failed:', error);
      });
    
    // Listen for messages from Service Worker
    navigator.serviceWorker.addEventListener('message', (event) => {
      if (event.data.type === 'OFFLINE_STATUS') {
        updateOfflineUI(event.data.isOffline);
      }
    });
  });
}

// Check online/offline status
function updateOnlineStatus() {
  const isOffline = !navigator.onLine;
  updateOfflineUI(isOffline);
  
  if (isOffline) {
    console.log('[PWA] App is offline');
    showOfflineNotification();
  } else {
    console.log('[PWA] App is online');
    hideOfflineNotification();
  }
}

window.addEventListener('online', updateOnlineStatus);
window.addEventListener('offline', updateOnlineStatus);

// Update UI based on offline status
function updateOfflineUI(isOffline) {
  const body = document.body;
  
  if (isOffline) {
    body.classList.add('offline-mode');
  } else {
    body.classList.remove('offline-mode');
  }
}

// Show offline notification banner
function showOfflineNotification() {
  // Check if banner already exists
  if (document.getElementById('offline-banner')) return;
  
  const banner = document.createElement('div');
  banner.id = 'offline-banner';
  banner.innerHTML = `
    <div style="
      position: fixed;
      top: 0;
      left: 0;
      right: 0;
      background: #F59E0B;
      color: white;
      padding: 12px;
      text-align: center;
      font-weight: 600;
      z-index: 999999;
      box-shadow: 0 2px 8px rgba(0,0,0,0.2);
    ">
      📡 Mode hors ligne - Les données seront synchronisées à la reconnexion
    </div>
  `;
  
  document.body.appendChild(banner);
  
  // Adjust body padding
  document.body.style.paddingTop = '48px';
}

function hideOfflineNotification() {
  const banner = document.getElementById('offline-banner');
  if (banner) {
    banner.remove();
    document.body.style.paddingTop = '0';
  }
}

// Show update available notification
function showUpdateNotification() {
  const notification = document.createElement('div');
  notification.id = 'update-notification';
  notification.innerHTML = `
    <div style="
      position: fixed;
      bottom: 80px;
      right: 20px;
      background: #3B82F6;
      color: white;
      padding: 16px 20px;
      border-radius: 12px;
      box-shadow: 0 4px 12px rgba(0,0,0,0.3);
      z-index: 999999;
      display: flex;
      align-items: center;
      gap: 12px;
    ">
      <span>🔄 Nouvelle version disponible</span>
      <button onclick="window.location.reload()" style="
        background: white;
        color: #3B82F6;
        border: none;
        padding: 8px 16px;
        border-radius: 6px;
        font-weight: 600;
        cursor: pointer;
      ">Actualiser</button>
    </div>
  `;
  
  document.body.appendChild(notification);
}

// Request background sync
async function requestBackgroundSync() {
  if ('serviceWorker' in navigator && 'SyncManager' in window) {
    try {
      const registration = await navigator.serviceWorker.ready;
      await registration.sync.register('sync-transactions');
      console.log('[PWA] Background sync registered');
    } catch (error) {
      console.error('[PWA] Background sync failed:', error);
    }
  }
}

// Install prompt for PWA
let deferredPrompt;

window.addEventListener('beforeinstallprompt', (e) => {
  // Prevent the mini-infobar from appearing on mobile
  e.preventDefault();
  
  // Store the event for later use
  deferredPrompt = e;
  
  // Show install button or banner
  showInstallPrompt();
});

function showInstallPrompt() {
  // Check if already installed
  if (window.matchMedia('(display-mode: standalone)').matches) {
    return;
  }
  
  const installBanner = document.createElement('div');
  installBanner.id = 'pwa-install-banner';
  installBanner.innerHTML = `
    <div style="
      position: fixed;
      bottom: 20px;
      left: 50%;
      transform: translateX(-50%);
      background: #0F172A;
      color: white;
      padding: 16px 24px;
      border-radius: 16px;
      box-shadow: 0 8px 24px rgba(0,0,0,0.4);
      z-index: 999999;
      display: flex;
      align-items: center;
      gap: 16px;
      max-width: 90%;
    ">
      <div style="font-size: 2rem;">💰</div>
      <div>
        <div style="font-weight: 700; margin-bottom: 4px;">Installer FinancePerso</div>
        <div style="font-size: 0.9rem; opacity: 0.8;">Accès rapide depuis l'écran d'accueil</div>
      </div>
      <button id="install-btn" style="
        background: #3B82F6;
        color: white;
        border: none;
        padding: 10px 20px;
        border-radius: 8px;
        font-weight: 600;
        cursor: pointer;
        white-space: nowrap;
      ">Installer</button>
      <button onclick="this.parentElement.parentElement.remove()" style="
        background: transparent;
        color: white;
        border: none;
        font-size: 1.5rem;
        cursor: pointer;
        opacity: 0.6;
      ">×</button>
    </div>
  `;
  
  document.body.appendChild(installBanner);
  
  // Handle install button click
  document.getElementById('install-btn').addEventListener('click', async () => {
    if (deferredPrompt) {
      deferredPrompt.prompt();
      
      const { outcome } = await deferredPrompt.userChoice;
      console.log(`[PWA] User response to install prompt: ${outcome}`);
      
      deferredPrompt = null;
      installBanner.remove();
    }
  });
}

// Track installed status
window.addEventListener('appinstalled', () => {
  console.log('[PWA] FinancePerso was installed');
  deferredPrompt = null;
  
  // Remove install banner if exists
  const banner = document.getElementById('pwa-install-banner');
  if (banner) banner.remove();
});

// Check if running as installed PWA
function isRunningAsPWA() {
  return window.matchMedia('(display-mode: standalone)').matches ||
         window.navigator.standalone === true;
}

// Initialize
console.log('[PWA] FinancePerso PWA support loaded');
console.log('[PWA] Running as PWA:', isRunningAsPWA());
