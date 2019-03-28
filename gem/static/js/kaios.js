(function() {
  var domReady = function(callback) {
      document.readyState === "interactive" || document.readyState === "complete" ? callback() : document.addEventListener("DOMContentLoaded", callback);
  };
  function handleKeydown(e) {
    switch(e.key) {
      case 'ArrowUp':
        nav(-1);
        break;
      case 'ArrowDown':
        nav(1);
        break;
      case 'ArrowRight':
        nav(1);
        break;
      case 'ArrowLeft':
        nav(-1);
        break;
    }
  };

  var kaiosPadNav = function(e) {
    var childElem = document.querySelectorAll('div, a, input, button, select, textarea,li');
    for (var i = 0, len = childElem.length; i < len; i++) {
      childElem[i].className += " items";
      childElem[i].setAttribute('tabindex', i);
      childElem[i].onfocus = function() {
        var activeElem = document.activeElement;
        setInterval(function() {
          activeElem.addEventListener('keydown', handleKeydown);
        }, 1000);
      };
    }
  };
  //STEP 6 Do not work and does not make sense - Already applied focus
  /*function nav (e) {
    var currentIndex = document.activeElement;
    var next = currentIndex + e;
    var items = document.querySelectorAll('.items');
    var targetElement = items[next];
    targetElement.focus();
  };*/



  var softkeyCallback = {
      left: function() { console.log('You click on SoftLeft') },
      center: function() { console.log('You click on Enter') },
      right: function() { console.log('You click on SoftRight') }
  };
  function handleKeyDownEvent(evt) {
    switch (evt.key) {
        case 'SoftLeft':
            // Action case press left key
            softkeyCallback.left();
        break;

        case 'SoftRight':
            // Action case press right key
            softkeyCallback.right();
        break;

        case 'Enter':
            // Action case press center key
            softkeyCallback.center();
        break;
    }
  };
  document.addEventListener('keydown', handleKeyDownEvent);


  domReady(function() {
    kaiosPadNav();
    nav();
    softkeyCallback();
    updateSoftKey();
  });
})();
