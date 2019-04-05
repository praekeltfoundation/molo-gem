"use strict";
(function() {
  function domReady(callback) {
      document.readyState === "interactive" || document.readyState === "complete" ? callback() : document.addEventListener("DOMContentLoaded", callback);
  };
  function kaiosPadNav (e) {
    var childElems = document.querySelectorAll('div, a, input, button, select, textarea,ul,li');
    var currentIndex = 0, lastTabIndex, lastTabIndexElems, values = [];
    var genericTabs = function (a) {
      for(i = 0; i < a.length; i++ ){
        a[i].className += " items";
        a[i].setAttribute('tabindex', i);
        values.push(a[i]);
      }
      return values;
    }
    genericTabs(childElems).forEach(function(item, index, array) {
      lastTabIndex = index;
      lastTabIndexElems = item;
      values = array;
      return lastTabIndex, lastTabIndexElems, values;
    });

    function nav(ev) {
      var next = currentIndex + ev;
      var items = document.querySelectorAll(".items");
      currentIndex = next;
      var targetElement = items[next];
      console.log(targetElement);
      targetElement.focus();
    }

    var handleKeydown = function(e) {
      switch(e.key) {
        case 'ArrowUp':
          nav(-1);
          console.log('You click on ArrowUp', e.which || e.keyCode);
          break;
        case 'ArrowDown':
          nav(1);
          console.log('You click on ArrowDown', e.which || e.keyCode)
          break;
        case 'ArrowRight':
          nav(1);
          console.log('You click on ArrowRight', e.which || e.keyCode)
          break;
        case 'ArrowLeft':
          nav(-1);
          console.log('You click on ArrowLeft', e.which || e.keyCode)
          break;
      }
    };
    document.activeElement.addEventListener('keydown', handleKeydown, true);
  };



  var softkeyCallback = {
    left: function() { console.log('You click on SoftLeft') },
    center: function() {
      console.log('You click on Enter')

    },
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
