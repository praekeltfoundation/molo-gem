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
    var searchLabel = document.getElementById('search_nav');
    console.log(searchLabel);
    searchLabel.addEventListener('click', function(e) {
      if(e.target.classList.contains('is__active')) {
        e.target.classList.remove('is__active');
      } else {
        e.target.classList.add('is__active');
      }
  }, false);
  }


  domReady(function() {
    menuToggle();
  });
})();
