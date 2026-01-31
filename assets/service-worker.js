/**
 * FinancePerso Service Worker
 * Provides offline support and caching for PWA functionality
 */

const CACHE_NAME = 'financeperso-v1';
const STATIC_ASSETS = [
  '/',
  '/app/static/style.css',
  '/app/static/main.css',
  '/app/static/favicon.ico',
];

// Install event - cache static assets
self.addEventListener('install', (event) => {
  console.log('[SW] Installing Service Worker...');
  
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {
        console.log('[SW] Caching static assets');
        return cache.addAll(STATIC_ASSETS);
      })
      .then(() => {
        console.log('[SW] Skip waiting');
        return self.skipWaiting();
      })
      .catch((err) => {
        console.error('[SW] Cache failed:', err);
      })
  );
});

// Activate event - cleanup old caches
self.addEventListener('activate', (event) => {
  console.log('[SW] Activating Service Worker...');
  
  event.waitUntil(
    caches.keys()
      .then((cacheNames) => {
        return Promise.all(
          cacheNames
            .filter((name) => name !== CACHE_NAME)
            .map((name) => {
              console.log('[SW] Deleting old cache:', name);
              return caches.delete(name);
            })
        );
      })
      .then(() => {
        console.log('[SW] Claiming clients');
        return self.clients.claim();
      })
  );
});

// Fetch event - serve from cache, fallback to network
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);
  
  // Skip non-GET requests
  if (request.method !== 'GET') {
    return;
  }
  
  // Skip Streamlit's WebSocket connections
  if (url.pathname.includes('_stcore')) {
    return;
  }
  
  // Strategy: Network first, fallback to cache for API calls
  // Strategy: Cache first, fallback to network for static assets
  
  if (isStaticAsset(url)) {
    // Cache-first strategy for static assets
    event.respondWith(cacheFirstStrategy(request));
  } else if (isDataAPI(url)) {
    // Network-first strategy for data
    event.respondWith(networkFirstStrategy(request));
  } else {
    // Stale-while-revalidate for everything else
    event.respondWith(staleWhileRevalidateStrategy(request));
  }
});

// Helper functions
function isStaticAsset(url) {
  const staticExtensions = ['.css', '.js', '.png', '.jpg', '.jpeg', '.gif', '.svg', '.woff', '.woff2', '.ttf'];
  return staticExtensions.some(ext => url.pathname.endsWith(ext));
}

function isDataAPI(url) {
  return url.pathname.includes('/api/') || url.pathname.includes('/data/');
}

// Cache-first strategy: Try cache first, then network
async function cacheFirstStrategy(request) {
  const cache = await caches.open(CACHE_NAME);
  const cached = await cache.match(request);
  
  if (cached) {
    console.log('[SW] Serving from cache:', request.url);
    return cached;
  }
  
  try {
    const response = await fetch(request);
    if (response.ok) {
      cache.put(request, response.clone());
    }
    return response;
  } catch (error) {
    console.error('[SW] Fetch failed:', error);
    // Return offline fallback if available
    return cache.match('/offline.html');
  }
}

// Network-first strategy: Try network first, fallback to cache
async function networkFirstStrategy(request) {
  const cache = await caches.open(CACHE_NAME);
  
  try {
    const networkResponse = await fetch(request);
    if (networkResponse.ok) {
      cache.put(request, networkResponse.clone());
    }
    return networkResponse;
  } catch (error) {
    console.log('[SW] Network failed, trying cache:', request.url);
    const cached = await cache.match(request);
    if (cached) {
      return cached;
    }
    
    // Return custom offline response for API calls
    return new Response(
      JSON.stringify({ 
        offline: true, 
        message: 'Vous êtes hors ligne. Les données seront synchronisées à la reconnexion.' 
      }),
      {
        status: 503,
        headers: { 'Content-Type': 'application/json' }
      }
    );
  }
}

// Stale-while-revalidate strategy: Serve from cache, update in background
async function staleWhileRevalidateStrategy(request) {
  const cache = await caches.open(CACHE_NAME);
  const cached = await cache.match(request);
  
  // Fetch update in background
  const fetchPromise = fetch(request)
    .then((networkResponse) => {
      if (networkResponse.ok) {
        cache.put(request, networkResponse.clone());
      }
      return networkResponse;
    })
    .catch((error) => {
      console.log('[SW] Background fetch failed:', error);
      return cached;
    });
  
  // Return cached version immediately if available
  if (cached) {
    fetchPromise; // Trigger background update
    return cached;
  }
  
  // Otherwise wait for network
  return fetchPromise;
}

// Background sync for offline form submissions
self.addEventListener('sync', (event) => {
  if (event.tag === 'sync-transactions') {
    event.waitUntil(syncPendingTransactions());
  }
});

async function syncPendingTransactions() {
  console.log('[SW] Syncing pending transactions...');
  // This would sync any pending transactions stored in IndexedDB
  // Implementation depends on your offline storage strategy
}

// Push notifications (optional)
self.addEventListener('push', (event) => {
  const options = {
    body: event.data?.text() || 'Nouvelle notification FinancePerso',
    icon: '/app/static/favicon-192x192.png',
    badge: '/app/static/favicon-72x72.png',
    tag: 'financeperso-notification',
    requireInteraction: true
  };
  
  event.waitUntil(
    self.registration.showNotification('FinancePerso', options)
  );
});

// Notification click handler
self.addEventListener('notificationclick', (event) => {
  event.notification.close();
  
  event.waitUntil(
    clients.openWindow('/')
  );
});

// Message handler from main thread
self.addEventListener('message', (event) => {
  if (event.data === 'skipWaiting') {
    self.skipWaiting();
  }
});

console.log('[SW] Service Worker loaded');
