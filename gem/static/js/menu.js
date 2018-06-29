"use strict";
(function() {
  var domReady = function(callback) {
      document.readyState === "interactive" || document.readyState === "complete" ? callback() : document.addEventListener("DOMContentLoaded", callback);
  };

  var menuToggle = function() {
      var menuListLabel = document.getElementById('nav_slide');
      var menuList = document.querySelector('.menu--header');
      menuListLabel.addEventListener('click', function() {
        menuList.classList.toggle('is-open');
      });
  }

  domReady(function() {
    menuToggle();
  });

})();
