
"use strict";

var domReady = function(callback) {
  document.readyState === "interactive" || document.readyState === "complete" ? callback() : document.addEventListener("DOMContentLoaded", callback);
};

function debounce(method, delay) {
  clearTimeout(method._tId);
  method._tId= setTimeout(function(){
      method();
  }, delay);
}

var stickyHeader = function() {
  var header = document.getElementById("header");
  var content = document.getElementById("content-wrapper")
  var headerHeight = document.getElementById('header').clientHeight;
  var langHeight = document.getElementById('language-bar').clientHeight;
  
  var headerFixed = function() {
    content.style.top =  headerHeight + "px";
    header.classList.add("header-fixed");
  };
  
  var headerUnfixed = function() {
    content.style.top = "0";
    header.classList.remove("header-fixed");
  };
  
  var headerInit = function() {
    header.style.top = -headerHeight + "px";
  };
  
  window.addEventListener('scroll', function(){ 
    var scrollAmount = this.y - window.pageYOffset;
    var scrollPos = window.scrollY;
    console.log(scrollPos);
    
    if( scrollAmount > 0 && scrollPos > langHeight ){ 
      debounce(headerFixed, 50);
      header.style.top = 0;
    } else if (scrollPos > headerHeight + langHeight ) {
      headerInit();
    } else {
      headerUnfixed();
    } 
    
    this.y = window.pageYOffset;
    
  });
};

var loadMore = function() {
  var articlesMore = document.getElementById('articles-more');
  
  articlesMore.addEventListener("click", function(event){
    event.preventDefault();
    var element = event.target;
    if (element.tagName == 'A' && element.classList.contains("more-link")) {
      element.childNodes[1].innerHTML = "<img src='/static/img/loading.gif' alt='Loading...' />"
      fetch(element.getAttribute('data-next'))
       .then(function(response) {
         return response.text();
       }).then(function(text) { 
         articlesMore.insertAdjacentHTML('beforeend', text);
         articlesMore.removeChild(element);
       });
     }
  });
};

domReady(function() {
  stickyHeader();
  loadMore();
});

