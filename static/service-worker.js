// service-worker.js - متطور مع Offline Mode
const CACHE_NAME = 'studyhub-v2';
const urlsToCache = [
  '/',
  '/static/favicon.ico',
  '/static/manifest.json',
  '/login',
  '/register',
  '/dashboard'
];

// تثبيت Service Worker
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {
        console.log('✅ تم تخزين الملفات الأساسية');
        return cache.addAll(urlsToCache);
      })
  );
  self.skipWaiting();
});

// تفعيل Service Worker
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cache) => {
          if (cache !== CACHE_NAME) {
            console.log('🗑️ حذف الكاش القديم:', cache);
            return caches.delete(cache);
          }
        })
      );
    })
  );
  return self.clients.claim();
});

// استراتيجية: Network First, ثم Cache
self.addEventListener('fetch', (event) => {
  event.respondWith(
    fetch(event.request)
      .then((response) => {
        // تخزين النسخة الجديدة في الكاش
        const responseClone = response.clone();
        caches.open(CACHE_NAME).then((cache) => {
          cache.put(event.request, responseClone);
        });
        return response;
      })
      .catch(() => {
        // لو النت مش شغال، إرجع من الكاش
        return caches.match(event.request);
      })
  );
});

// Push Notifications
self.addEventListener('push', (event) => {
  const options = {
    body: event.data ? event.data.text() : 'عندك إشعار جديد من Study Hub! 🎉',
    icon: '/static/favicon.ico',
    badge: '/static/favicon.ico',
    vibrate: [200, 100, 200],
    tag: 'studyhub-notification'
  };
  event.waitUntil(
    self.registration.showNotification('📚 Study Hub', options)
  );
});

self.addEventListener('notificationclick', (event) => {
  event.notification.close();
  event.waitUntil(
    clients.openWindow('/dashboard')
  );
});