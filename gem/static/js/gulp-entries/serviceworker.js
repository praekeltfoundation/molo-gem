importScripts('https://www.gstatic.com/firebasejs/3.9.0/firebase-app.js');
importScripts('https://www.gstatic.com/firebasejs/3.9.0/firebase-messaging.js');


//'messagingSenderId': '158972131363'
firebase.initializeApp({
  'messagingSenderId': '924312861903'
});

const messaging = firebase.messaging();
const CACHE = 'app-cache';

self.addEventListener('install', function(evt) {
    console.info('Event: Install');
  evt.waitUntil(precache());
});

// self.addEventListener('fetch', function(evt) {
//     console.info('Event: Fetch');
//   evt.respondWith(fetch(evt.request).catch(function () {
//     return caches.open(CACHE).then(function(cache) {
//       return cache.match('/static/offline.html');
//     });
//   }));
// });

self.addEventListener('fetch', function(event) {
  var requestUrl = new URL(event.request.url);
    if (requestUrl.origin === location.origin) {
      if ((requestUrl.pathname === '/')) {
        event.respondWith(caches.match('/offline_sw'));
        return;
      }
    }
    event.respondWith(
      caches.match(event.request).then(function(response) {
        return response || fetch(event.request);
      })
    );
});

function precache() {
  console.info('Precached');
  return caches.open(CACHE).then(function (cache) {
    return cache.addAll([
      '/offline_sw'
    ]);
  });
}
