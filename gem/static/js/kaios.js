"use strict";
(function() {
  function domReady(callback) {
      document.readyState === "interactive" || document.readyState === "complete" ? callback() : document.addEventListener("DOMContentLoaded", callback);
  };

  function kaiosPadNav (e) {
    var childElem = document.querySelectorAll('div, a, input, button, select, textarea,li');
    function nav(num) {
      var currentIndex = childElem[num];
      var next = currentIndex + num;
      var items = document.querySelectorAll('.items');
      var targetElement = items[next];
      targetElement.focus();
      console.log("My value: ", targetElement);
    }
    for (var i = 0, len = childElem.length; i < len; i++) {
      childElem[i].className += " items";
      childElem[i].setAttribute('tabindex', i);
      nav(i);
    }

    var handleKeydown = function(e) {
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
    document.activeElement.addEventListener('keydown', handleKeydown);
  };

  var softkeyCallback = {
    left: function() { /*console.log('You click on SoftLeft')*/ },
    center: function() { /*console.log('You click on Enter')*/ },
    right: function() { /*console.log('You click on SoftRight')*/ }
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

  domReady(function() {
    kaiosPadNav();
    document.addEventListener('keydown', handleKeyDownEvent);
  });
})();
