
(function() {

  'use strict';

  var domReady = function(callback) {
      document.readyState === "interactive" || document.readyState === "complete" ? callback() : document.addEventListener("DOMContentLoaded", callback);
  };

  var remNoJS = function() {
    var root = document.documentElement;
    root.className = '';
  };

  var hidePagination = function() {
    document.body.classList.add('toggle-hide');
  };

  function getAjax(url, success) {
    var xhr = window.XMLHttpRequest ? new XMLHttpRequest() : new ActiveXObject('Microsoft.XMLHTTP');
    xhr.open('GET', url);
    xhr.onreadystatechange = function() {
        if (xhr.readyState>3 && xhr.status==200) success(xhr.responseText);
    };
    xhr.setRequestHeader('X-Requested-With', 'XMLHttpRequest');
    xhr.send();
    return xhr;
  }

  var stickyHeader = function() {
    var header = document.getElementById("header-wrapper");
    var content = document.getElementById("content-wrapper");
    var menuList = document.getElementById("nav-list");

    var onResizing = function(event) {
      if (window.innerWidth < 1024){
        content.style.backgroundColor =  "#7300ff";
      } else {
        content.style.backgroundColor =  "transparent";
      }
    };

    window.onresize = onResizing;
    window.onload = onResizing;

    window.addEventListener('scroll', function(){
      var scrollAmount = this.y - window.pageYOffset;
      var scrollPos = window.scrollY;
      var headerHeight = document.getElementById('header-wrapper').clientHeight;
      var langHeight = document.getElementById('language-bar').clientHeight;

      if (scrollPos > 0 && window.innerWidth > 320 ) {
       header.classList.add("header-fixed");
       content.style.paddingTop =  headerHeight + "px";
     }

      if(scrollAmount > 0 && scrollPos > headerHeight && window.innerWidth > 320 ){
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
            getAjax(element.getAttribute('data-next'), function(data){
              element.parentNode.insertAdjacentHTML('beforeend', data);
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

  var   ctaButtonPrimary = document.getElementsByClassName('call-to-action__button--primary'),
        numberOfButtons = ctaButtonPrimary.length;
    function iterateButtonsOnPage(buttonsObject) {
        var iterateNum = 0;
        for (var i = 0; i < buttonsObject.length; i++) {
            if (buttonsObject[i]) {
                buttonsObject[i].addEventListener("click", function(e) {
                    var elemCurrent = e.target,
                        state = document.readyState;
                          if(elemCurrent.value) {
                            //Ideal solution is inject / appending to existing button style
                            //Reapplies inline CSS and removes Sass style
                            Object.assign(elemCurrent.style,{
                                "background-image": "url('/static/img/loading.gif'), url('/static/img/buttons/button-sprite.png')",
                                "background-position": "center center, 0 0",
                                "background-size":"auto, 1870px 334px",
                                "background-repeat":"no-repeat, no-repeat"
                            });
                          } else {
                              elemCurrent.innerHTML = "<img src='/static/img/loading.gif' alt='Loading...' />"
                          }
                });
                iterateNum++;
            }
        }
        return iterateNum;
    }
    iterateButtonsOnPage(ctaButtonPrimary);


  domReady(function() {
    remNoJS();
    hidePagination();
    stickyHeader();
    loadMore();
    backTop();
  });

})();
