
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
      '/static/offline.html',
      '/static/img/appicons/springster_icon_96.png',
      '/static/img/appicons/springster_icon_144.png',
      '/static/img/appicons/springster_icon_192.png'
    ]);
  });
}
