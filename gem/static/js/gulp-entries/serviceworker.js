importScripts('https://www.gstatic.com/firebasejs/3.9.0/firebase-app.js');
importScripts('https://www.gstatic.com/firebasejs/3.9.0/firebase-messaging.js');

firebase.initializeApp({
  'messagingSenderId': '158972131363' //Used by All app?
});

const messaging = firebase.messaging();
const CACHE = 'app-cache';

self.addEventListener('install', function(evt) {
  evt.waitUntil(precache());
});

self.addEventListener('fetch', function(evt) {
  evt.respondWith(fetch(evt.request).catch(function () {
    return caches.open(CACHE).then(function(cache) {
      return cache.match('/offline/'); //? Does this needs an actual file?
    });
  }));
});

function precache() {
  return caches.open(CACHE).then(function (cache) {
    return cache.addAll([
      '/',
      '/offline/',
      '/img/appicons/springster/springster_icon_96.png',
      '/img/appicons/springster/springster_icon_144.png',
      '/img/appicons/springster/springster_icon_192.png'
    ]);
  });
}
