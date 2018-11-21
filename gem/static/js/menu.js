"use strict";
(function() {
  var domReady = function(callback) {
      document.readyState === "interactive" || document.readyState === "complete" ? callback() : document.addEventListener("DOMContentLoaded", callback);
  };

  var menuToggle = function() {
      var menuListLabel     = document.getElementById('burger_nav_label');
      var menuListLabelOpen = document.querySelector('.is__open');
      //Traverse the entire page to look for this specific class
        menuListLabel.addEventListener('click', function(e) {
          if (e.target) {
            menuListLabel.classList.add('is__open');
            //menuListLabel.classList.remove("is__open");
          }
        var $label = e.target;
          console.log($label);
      }, false);
      menuListLabelOpen.addEventListener('click', function(e) {
        if (e.target) {
          menuListLabelOpen.classList.remove("is__open");
        }
      }, false);
  }
  domReady(function() {
    menuToggle();
  });
})();
