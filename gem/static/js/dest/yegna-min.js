"use strict";jQuery(document).ready(function(o){o(".dropdown-toggle").click(function(){var e=o(this).parents(".dropdown").children(".dropdown-menu").is(":hidden");o(".dropdown .dropdown-menu").hide(),o(".dropdown .dropdown-toggle").removeClass("open"),e&&o(this).parents(".dropdown").children(".dropdown-menu").toggle().parents(".dropdown").children(".dropdown-toggle").addClass("open")}),o(document).bind("click",function(e){o(e.target).parents().hasClass("dropdown")||o(".dropdown .dropdown-menu").hide()}),o(document).bind("click",function(e){o(e.target).parents().hasClass("dropdown")||o(".dropdown .dropdown-toggle").removeClass("open")}),o(".nav-menu-list__anchor").bind("click",function(){var e=$(this),t=e.parent(".nav-menu-list__item");if(t.hasClass("active")?t.removeClass("active").children(".nav-menu-list__anchor").removeClass("active"):t.addClass("active").children(".nav-menu-list__anchor").addClass("active"),0<t.children(".nav-menu-list").length){var n=e.attr("href");e.attr("href","#"),setTimeout(function(){e.attr("href",n)},300),o.preventDefault()}}).each(function(){var e=$(this);if(e.get(0).href===location.href)return e.addClass("active").parents("li").addClass("active"),!1})}),function(){var e;e=function(){!function(){var o=document.getElementById("header");document.getElementById("content");window.addEventListener("scroll",function(){var e=this.y-window.pageYOffset,t=window.scrollY,n=document.getElementById("header").clientHeight+366.66;1024<window.innerWidth&&(0<e&&n<t?(o.style.transform="translate3d(0px, 0px, 0px)",o.style.transition="transform 300ms ease 3ms",o.style.position="sticky"):n<t?(o.style.transform="translate3d(0px, "+-n+"px, 0px)",o.style.transition="transform 300ms ease 3ms",o.style.position="absolute"):(e<0||t<n)&&(o.style.transform="translate3d(0px, 0px, 0px)",o.style.transition="transform 300ms ease 3ms")),this.y=window.pageYOffset})}()},"interactive"===document.readyState||"complete"===document.readyState?e():document.addEventListener("DOMContentLoaded",e)}();