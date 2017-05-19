
"use strict";

var domReady = function(callback) {
  document.readyState === "interactive" || document.readyState === "complete" ? callback() : document.addEventListener("DOMContentLoaded", callback);
};

var hidePagination = function() {
  document.body.classList.add('toggle-hide');
}

var stickyHeader = function() {
  var header = document.getElementById("header");
  var content = document.getElementById("content-wrapper")
  var headerHeight = document.getElementById('header').clientHeight;
  var langHeight = document.getElementById('language-bar').clientHeight;
  
  window.addEventListener('scroll', function(){ 
    var scrollAmount = this.y - window.pageYOffset;
    var scrollPos = window.scrollY;
    
    if( scrollAmount > 0 && scrollPos > langHeight ){ 
      header.style.top = 0;
      content.style.top =  headerHeight + "px";
      header.classList.add("header-fixed");
    } else if (scrollPos > headerHeight + langHeight ) {
      header.style.top = -headerHeight + "px";
    } else if (scrollAmount < 0 || scrollPos < headerHeight){
      content.style.top = "0";
      header.classList.remove("header-fixed");
    } 
    
    this.y = window.pageYOffset;
    
  });
};

var loadMore = function() {
  var moreLink = document.getElementById('more-link');
  if (moreLink) {
    var articlesMore = document.getElementById('articles-more');
    
    if (articlesMore === null) {
      var wrapper = document.createElement('div');
      moreLink.parentNode.insertBefore(wrapper, moreLink);
      wrapper.appendChild(moreLink);
      wrapper.setAttribute("id", "articles-more");
    };
    
    wrapper.addEventListener("click", function(event){
      
      var element = event.target;
      console.log(element);
      if (element.tagName == 'A' && element.classList.contains("more-link")) {
        event.preventDefault();
        element.childNodes[1].innerHTML = "<img src='/static/img/loading.gif' alt='Loading...' />"
        fetch(element.getAttribute('data-next'))
         .then(function(response) {
           return response.text();
         }).then(function(text) {
           element.parentNode.insertAdjacentHTML('beforeend', text);
           element.parentNode.removeChild(element);
        });
       }
    });
  }
};

var scrollTo = function(element, to, duration) {
  if (duration < 0) return;
  var difference = to - element.scrollTop;
  var perTick = difference / duration * 2;

setTimeout(function() {
  element.scrollTop = element.scrollTop + perTick;
  scrollTo(element, to, duration - 2);
}, 10);
};

var backTop = function() {
  document.getElementById("back-to-top").onclick = function (event) {
    event.preventDefault();
    scrollTo(document.body, 0, 100);
  }
};

domReady(function() {
  stickyHeader();
  loadMore();
  hidePagination();
  backTop();
});

