"use strict";!function(){for(var e=document.getElementById("image__identity").src.split(".").slice(-1),t=[{type:"image",ext:["png","jpg","jpeg","gif","svg"]},{type:"media",ext:["mpeg","ogg","jpeg"]}],g=0;g<t.length;g++)if("image"==t[g].type)for(var o=0;o<t[g].ext.length;o++)t[g].ext[o]==e[0]&&(console.log(t[0].ext[o]),document.querySelector("meta[property='og:type']").setAttribute("content",t[0].type+"/"+t[0].ext[o]));else if("media"==t[g].type)for(o=0;o<t[g].ext.length;o++)t[g].ext[o]==e[0]&&document.querySelector("meta[property='og:type']").setAttribute("content",t[0].type+"/"+t[0].ext[o])}();