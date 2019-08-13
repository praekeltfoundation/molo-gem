"use strict";
(function(){
  var imageIdentity = document.getElementById("image__identity"),
      getImageArray = imageIdentity.src.split("."),
      imageExt = getImageArray.slice(-1),
      formats = [
        {
          type:"image",
          ext: ["png","jpg","jpeg","gif","svg"]
        },
        {
          type:"media",
          ext: ["mpeg","ogg","jpeg"]
        }
      ];

    for(var i = 0; i < formats.length; i++){
      if(formats[i].type == "image") {
        for(var j = 0; j < formats[i].ext.length; j++) {
          //formats[i].ext.includes(imageExt[0])
          if(formats[i].ext[j] == imageExt[0]) {
            document.querySelector("meta[property='og:type']").setAttribute("content",formats[0].type + "/" + formats[0].ext[j]);
          }
        }
      } else if(formats[i].type == "media") {
        for(var j = 0; j < formats[i].ext.length; j++) {
          if(formats[i].ext[j] == imageExt[0]) {
            document.querySelector("meta[property='og:type']").setAttribute("content",formats[0].type + "/" + formats[0].ext[j]);
          }
        }
      }
    }
})();
