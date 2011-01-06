// when prettify is loaded, run it!
(function loopsiloop(){
  if (window.prettyPrint){ 
   prettyPrint();
  } else {
    setTimeout(loopsiloop,100);
  }
})();


// set up code blocks to get hit by prettyprint:
Array.prototype.slice.call(document.querySelectorAll('pre')).forEach(function(v,k,arra){
  v.className += ' prettyprint';
});