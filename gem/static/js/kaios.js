"use strict";
(function() {
  function domReady(callback) {
      document.readyState === "interactive" || document.readyState === "complete" ? callback() : document.addEventListener("DOMContentLoaded", callback);
  };

  function kaiosPadNav (e) {
    var childElems = document.querySelectorAll('div, a, input, button, select, textarea,li');
    var currentIndex, bigScopeChildElems;
    for (var i = 0, len = childElems.length; i < len; i++ ) {
      childElems[i].className += " items";
      childElems[i].setAttribute('tabindex', i);
      if (childElems[i].getAttribute('tabindex') !== -1 ) {
        currentIndex = i;
      }
    }
    bigScopeChildElems = childElems[currentIndex];
    function nav(event) {
      var next = (parseInt(bigScopeChildElems.getAttribute('tabindex'), 10) + event);
      var items = document.querySelectorAll('.items');
      var targetElement = items[next];
        targetElement.focus();
        console.log(items);
    };
    var handleKeydown = function(e) {
      switch(e.key) {
        case 'ArrowUp':
          nav(-1);
          console.log('You click on ArrowUp', e.which || e.keyCode || 0);
          break;
        case 'ArrowDown':
          nav(1);
          console.log('You click on ArrowDown', e.which || e.keyCode || 0)
          break;
        case 'ArrowRight':
          nav(1);
          console.log('You click on ArrowRight', e.which || e.keyCode || 0)
          break;
        case 'ArrowLeft':
          nav(-1);
          console.log('You click on ArrowLeft', e.which || e.keyCode || 0)
          break;
      }
    };
    document.activeElement.addEventListener('keydown', handleKeydown, true);
  };



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

  domReady(function() {
    kaiosPadNav();
    document.addEventListener('keydown', handleKeyDownEvent);
  });
})();
