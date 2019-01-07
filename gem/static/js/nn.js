"use strict";
(function() {
  var domReady = function(callback) {
      document.readyState === "interactive" || document.readyState === "complete" ? callback() : document.addEventListener("DOMContentLoaded", callback);
  };
  var menuToggle = function() {
    var menuListLabel = document.getElementsByClassName('toggle-nav');
    var menuClassIndex;
    for (menuClassIndex = 0; menuClassIndex < menuListLabel.length; menuClassIndex++) {
      var checkboxElements = menuListLabel[menuClassIndex].nextElementSibling;
      checkboxElements.onclick = function(e) {
        e.target.checked = true;
        if(e.target.checked = true) {
          checkboxElements.checked = false;
        } else {
          e.target.checked = true;
        }
      }
    }
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
  var pluginsSpacingStyle = function () {
    var surveysClass =  document.getElementsByClassName('surveys');
    var pollsClass   =  document.getElementsByClassName('polls');
    var lastSurveysClass = surveysClass[surveysClass.length-1];
    var lastPollsClass = pollsClass[pollsClass.length-1];
    if (surveysClass.length > 0 && pollsClass.length > 0 ) {
        surveysClass[0].classList.add("first");
        lastPollsClass.classList.add("last");
    }
    if (surveysClass.length <= 0 && pollsClass.length > 0) {
      console.log('Survey is not here and Polls is here');
      if (pollsClass.length == 1) {
        pollsClass[0].classList.add('only');
      } else {
        pollsClass[0].classList.add('first');
      }
      if (pollsClass.length > 1) {
        lastPollsClass.classList.add("last");
      }
    }
    if (pollsClass.length <= 0 && surveysClass.length > 0) {
      console.log('Polls is not here and Surveys is here');
      if (surveysClass.length == 1) {
        surveysClass[0].classList.add('only');
      } else {
        surveysClass[0].classList.add('first');
      }
      if (surveysClass.length > 1) {
        lastSurveysClass.classList.add("last");
      }
    }
  }
  domReady(function() {
    stickyHeader();
    menuToggle();
    pluginsSpacingStyle();
  });
})();
