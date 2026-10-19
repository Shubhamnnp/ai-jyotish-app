// ब्रह्महोरा (BrahmaHora) वैदिक ज्योतिष OS - PWA Service Worker
const CACHE_NAME = 'brahmahora-jyotish-cache-v2';
const ASSETS_TO_CACHE = [
  '/',
  '/app/static/manifest.json',
  '/app/static/icon-192.png',
  '/app/static/icon-512.png',
  '/static/manifest.json',
  '/static/icon-192.png',
  '/static/icon-512.png'
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(ASSETS_TO_CACHE).catch((err) => {
        console.log('BrahmaHora SW cache partial install:', err);
      });
    })
  );
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) => {
      return Promise.all(
        keys.map((key) => {
          if (key !== CACHE_NAME) {
            return caches.delete(key);
          }
        })
      );
    })
  );
  self.clients.claim();
});

self.addEventListener('fetch', (event) => {
  // Pass through Streamlit WebSocket, streaming, and live calculation endpoints
  if (
    event.request.url.includes('/_stcore/') ||
    event.request.url.includes('stream') ||
    event.request.url.includes('websocket')
  ) {
    return;
  }
  event.respondWith(
    fetch(event.request).catch(() => {
      return caches.match(event.request);
    })
  );
});
