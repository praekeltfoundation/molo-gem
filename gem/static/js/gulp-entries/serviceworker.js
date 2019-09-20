importScripts('https://www.gstatic.com/firebasejs/3.9.0/firebase-app.js');
importScripts('https://www.gstatic.com/firebasejs/3.9.0/firebase-messaging.js');

firebase.initializeApp({
  'messagingSenderId': '158972131363'
});

const messaging = firebase.messaging();
const CACHE = 'app-cache';

self.addEventListener('install', function(evt) {
  evt.waitUntil(
    caches.open(CACHE).then(function (cache) {
      return cache.addAll([
        '/',
        '/offline'
      ]);
    })
  );
});

self.addEventListener('fetch', function(evt) {
  evt.respondWith(fetch(evt.request).catch(function () {
    return caches.open(CACHE).then(function(cache) {
      return cache.match('/offline'); 
    });
  }));
});
