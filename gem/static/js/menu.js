"use strict";
(function() {
  var domReady = function(callback) {
      document.readyState === "interactive" || document.readyState === "complete" ? callback() : document.addEventListener("DOMContentLoaded", callback);
  };

  var menuToggle = function() {
      var menuListLabel     = document.getElementById('burger_nav_label');
      var menuListLabelOpen = document.querySelector('.is__open');
        menuListLabel.addEventListener('click', function(e) {
          if(e.target.classList.contains('is__open')) {
            e.target.classList.remove('is__open');
            console.log('Class exists!');
          } else {
            menuListLabel.classList.remove('is__open');
            e.target.classList.add('is__open');
          }
      }, false);
  }
  domReady(function() {
    menuToggle();
  });
})();
