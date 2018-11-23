"use strict";
(function() {
  var domReady = function(callback) {
      document.readyState === "interactive" || document.readyState === "complete" ? callback() : document.addEventListener("DOMContentLoaded", callback);
  };

  var menuToggle = function() {
    var menuListLabel = document.getElementsByClassName('toggle-nav'),
      menuClassIndex;
      for (menuClassIndex = 0; menuClassIndex < menuListLabel.length; menuClassIndex++) {
          menuListLabel[menuClassIndex].addEventListener('click', function(e) {
            if(e.target.classList.contains('is__open')) {
              e.target.classList.remove('is__open');
            } else {
              e.target.classList.add('is__open');
            }
        }, false);
      }
  }
  domReady(function() {
    menuToggle();
  });
})();
