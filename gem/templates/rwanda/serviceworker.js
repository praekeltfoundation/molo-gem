
importScripts('https://www.gstatic.com/firebasejs/3.9.0/firebase-app.js');
importScripts('https://www.gstatic.com/firebasejs/3.9.0/firebase-messaging.js');

firebase.initializeApp({
  'messagingSenderId': '158972131363' //?
});

const messaging = firebase.messaging();

var CACHE = 'app-cache';

self.addEventListener('install', function(evt) {
  evt.waitUntil(precache());
});

self.addEventListener('fetch', function(evt) {
  evt.respondWith(fetch(evt.request).catch(function () {
    return caches.open(CACHE).then(function(cache) {
      return cache.match('/static/offline.html');
    });
  }));
});

function precache() {
  return caches.open(CACHE).then(function (cache) {
    return cache.addAll([

      '/',
      'offline.html',
      '/static/img/appicons/ninyampinga/NN_Favicon_GREEN.svg'
    ]);
  });
}
