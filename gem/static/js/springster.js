
"use strict";

var domReady = function(callback) {
    document.readyState === "interactive" || document.readyState === "complete" ? callback() : document.addEventListener("DOMContentLoaded", callback);
};

var hidePagination = function() {
  document.body.classList.add('toggle-hide');
};

var stickyHeader = function() {
  var header = document.getElementById("header-wrapper");
  var content = document.getElementById("content-wrapper");
  var headerHeight = document.getElementById('header-wrapper').clientHeight;
  var langHeight = document.getElementById('language-bar').clientHeight;
  var frameWidth = window.innerWidth;
  
  var onResizing = function(event) {
    if (window.innerWidth < 1024 ){
      content.style.backgroundColor =  "#7300ff";
    } else if (window.innerWidth < 320 ){
      content.style.paddingTop =  "0px";
    } else {
      content.style.paddingTop =  headerHeight + "px";
      content.style.backgroundColor =  "transparent";
    }
  };

  window.onresize = onResizing;
  window.onload = onResizing;
  
  content.style.paddingTop =  headerHeight + "px";
    
  window.addEventListener("resize", function(){
    if(this.innerWidth < 1024 ){
      content.style.backgroundColor =  "#7300ff";
    } else {
      content.style.backgroundColor =  "transparent";
    }
    
    if(this.innerWidth < 320 ){
      content.style.paddingTop =  "0px";
    } else {
      content.style.paddingTop =  headerHeight + "px";
    }
  });

  window.addEventListener('scroll', function(){
    var scrollAmount = this.y - window.pageYOffset;
    var scrollPos = window.scrollY;

    if(scrollAmount > 0 && scrollPos > headerHeight && frameWidth > 320 ){
      header.style.transform = "translate3d(0px, "+ -langHeight + "px, 0px)";
      content.style.paddingTop =  headerHeight + "px";
    } else if (scrollPos > headerHeight ) {
      header.style.transform = "translate3d(0px, "+ -headerHeight + "px, 0px)";
    } else if (scrollAmount < 0 || scrollPos < headerHeight){
      header.style.transform = "translate3d(0px, 0px, 0px)";
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
      
      wrapper.addEventListener("click", function(event){
        var element = event.target;
        if (element.tagName == 'A' && element.classList.contains("more-link")) {
          event.preventDefault();
          element.childNodes[1].innerHTML = "<img src='/static/img/loading.gif' alt='Loading...' />";
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
  }
};

var scrollToX = function(element, to, duration) {
  if (duration < 0 || element.scrollTop == to) return;
  var difference = to - element.scrollTop;
  var perTick = difference / duration * 2;

  setTimeout(function() {
    element.scrollTop = element.scrollTop + perTick;
    scrollToX(element, to, duration - 2);
  }, 10);
};

var backTop = function() {
  document.getElementById("back-to-top").onclick = function (event) {
    event.preventDefault();
    scrollToX(document.body, 0, 100);
  };
};

var formUI = function() {
  var replaceValidationUI = function(form) {
      form.addEventListener("invalid", function(event) {
        event.preventDefault();
      }, true);
      form.addEventListener("submit", function(event) {
        if (!this.checkValidity() ) {
            event.preventDefault();
        }
      });
      var errorList = form.querySelectorAll('.errorlist');
      if (errorList.length > 0) {
        for (var i = 0; i < errorList.length; i++) {
          parent = errorList[i].parentNode;
          parent.classList.add("input-error");
        }
      }

      var submitButton = form.querySelector("button:not([type=button]), input[type=submit]");
      var headerHeight = document.getElementById('header-wrapper').clientHeight;
      submitButton.addEventListener("click", function(event) {
        var invalidFields = form.querySelectorAll(":invalid"),
          errorMessages = form.querySelectorAll(".error-message"),
          parent;

        for (var i = 0; i < errorMessages.length; i++) {
          errorMessages[i].parentNode.removeChild( errorMessages[i]);
        }

        for (var j = 0; j < invalidFields.length; j++) {
          parent = invalidFields[j].parentNode;
          parent.insertAdjacentHTML("beforeend", "<div class='error-message'>" +
            invalidFields[j].validationMessage +
            "</div>" );
          parent.classList.add("input-error");
        }

        if (invalidFields.length > 0) {
          scrollToX(document.body, invalidFields[0].offsetTop - headerHeight, 100);
        }
      });
  };

  var forms = document.querySelectorAll("form");
  for (var i = 0; i < forms.length; i++) {
    replaceValidationUI(forms[i]);
  }
};

domReady(function() {
  stickyHeader();
  loadMore();
  hidePagination();
  backTop();
  formUI();
});

