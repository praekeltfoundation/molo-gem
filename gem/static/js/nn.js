"use strict";
(function() {
  var domReady = function(callback) {
      document.readyState === "interactive" || document.readyState === "complete" ? callback() : document.addEventListener("DOMContentLoaded", callback);
  };
  var stickyHeader = function() {
    var header = document.getElementById("header");
    var content = document.getElementById("content_wrapper");
    window.addEventListener('scroll', function() {
      var scrollAmount = this.y - window.pageYOffset;
      var scrollPos = window.scrollY;
      var headerHeight = (document.getElementById('header').clientHeight) + 366.66;
      if (window.innerWidth > 768) {
        if (scrollAmount > 0 && scrollPos > headerHeight) {
          header.style.transform = "translate3d(0px, 0px, 0px)";
          header.style.position = "fixed";
        }
        else if (scrollPos > headerHeight) {
          header.style.transform = "translate3d(0px, "+ -headerHeight + "px, 0px)";
          header.style.position = "absolute";
        }
        else if (scrollAmount < 0 || scrollPos < headerHeight) {
          header.style.transform = "translate3d(0px, 0px, 0px)";
        }
      }
      this.y = window.pageYOffset;
    });
  };
  var pluginsSpacingStyle = function() {
    var surveysClass =  document.getElementsByClassName('surveys');
    var pollsClass   =  document.getElementsByClassName('polls');
    var lastSurveysClass = surveysClass[surveysClass.length-1];
    var lastPollsClass = pollsClass[pollsClass.length-1];
    if (surveysClass.length > 0 && pollsClass.length > 0 ) {
        surveysClass[0].classList.add("first");
        lastPollsClass.classList.add("last");
    }
    if (surveysClass.length <= 0 && pollsClass.length > 0) {
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
    pluginsSpacingStyle ();
  });
})();

jQuery(document).ready(function (e) {
  /* ƒ (e,n) {
      return new x.fn.init(e,n,t)
    }
  */
  function t(t) {
    e(t).bind("click", function (t) {
      t.preventDefault();
      e(this).parent().fadeOut();
    })
  }

  e(".dropdown-toggle").click(function () {
      var t = e(this).parents(".dropdown").children(".dropdown-menu").is(":hidden");
      e(".dropdown .dropdown-menu").hide();
      e(".dropdown .dropdown-toggle").removeClass("open");
      if (t) {
        e(this).parents(".dropdown").children(".dropdown-menu").toggle().parents(".dropdown").children(".dropdown-toggle").addClass("open")
      }
  });
  e(document).bind("click", function (t) {
      var n = e(t.target);
      if (!n.parents().hasClass("dropdown")) e(".dropdown .dropdown-menu").hide();
  });
  e(document).bind("click", function (t) {
      var n = e(t.target);
      if (!n.parents().hasClass("dropdown")) e(".dropdown .dropdown-toggle").removeClass("open");
  });
});
