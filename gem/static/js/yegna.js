"use strict";
jQuery(document).ready(function (e) {
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

(function() {
  var domReady = function(callback) {
      document.readyState === "interactive" || document.readyState === "complete" ? callback() : document.addEventListener("DOMContentLoaded", callback);
  };
var stickyHeader = function() {
  var header = document.getElementById("header");
  var content = document.getElementById("content_wrapper");

  console.log(document.getElementById('header').y - window.pageYOffset);
  console.log(window.scrollY);
  console.log((document.getElementById('header').clientHeight) + 366.66);
  console.log(window.innerWidth);

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
domReady(function() {
  stickyHeader();
  pluginsSpacingStyle ();
});
})();
