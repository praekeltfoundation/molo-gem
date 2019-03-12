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

  e('.nav-menu-list__anchor').bind('click', function() {
    var current_anchor = $(this);
    var current_item = current_anchor.parent(".nav-menu-list__item");
    if (current_item.hasClass("active")) {
         current_item.removeClass("active").children(".nav-menu-list__anchor").removeClass("active");
     } else {
         current_item.addClass("active").children(".nav-menu-list__anchor").addClass("active");
     }
     if (current_item.children(".nav-menu-list").length > 0) {
      var href = current_anchor.attr("href");
      current_anchor.attr("href", "#");
      setTimeout(function () {
          current_anchor.attr("href", href);
      }, 300);
      e.preventDefault();
    }
  }).each(function() {
    var current_anchor = $(this);
    if (current_anchor.get(0).href === location.href) {
        current_anchor.addClass("active").parents("li").addClass("active");
        return false;
    }
  });
});

(function() {
  var domReady = function(callback) {
      document.readyState === "interactive" || document.readyState === "complete" ? callback() : document.addEventListener("DOMContentLoaded", callback);
  };
  var stickyHeader = function() {
    var header = document.getElementById("header");
    var content = document.getElementById("content");

    window.addEventListener('scroll', function() {
      var scrollAmount = this.y - window.pageYOffset;
      var scrollPos = window.scrollY;
      var headerHeight = (document.getElementById('header').clientHeight) + 366.66;
      if (window.innerWidth > 1024) {
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
  });
})();
