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
    searchLabel.addEventListener('click', function(e) {
      if(e.target.classList.contains('is__active')) {
          e.target.classList.remove('is__active');
        } else {
          e.target.classList.add('is__active');
        }
    }, false);
  }
  var stickyHeader = function() {
    var header = document.getElementById("header");
    var content = document.getElementById("content_wrapper");
    window.addEventListener('scroll', function() {
      var scrollAmount = this.y - window.pageYOffset;
      var scrollPos = window.scrollY;
      var headerHeight = document.getElementById('header').clientHeight;
      if (scrollPos > 0 && window.innerWidth > 720 ) {
       header.classList.add("header--fixed");
     }
      if (scrollAmount > 0 && scrollPos > headerHeight && window.innerWidth > 720 ) {
        header.style.transform = "translate3d(0px, 0px, 0px)";
        header.style.position = "fixed";
      }
      else if (scrollPos > headerHeight ) {
        header.style.transform = "translate3d(0px, "+ -headerHeight + "px, 0px)";
        header.style.position = "absolute";
      }
      else if (scrollAmount < 0 || scrollPos < headerHeight) {
        header.style.transform = "translate3d(0px, 0px, 0px)";
      }
      this.y = window.pageYOffset;
    });
  };

  domReady(function() {
    stickyHeader();
    menuToggle();
  });
})();
