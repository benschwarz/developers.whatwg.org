// when prettify is loaded, run it!
(function loopsiloop(){
  if (window.prettyPrint){ 
   prettyPrint();
  } else {
    setTimeout(loopsiloop,100);
  }
})();


// set up code blocks to get hit by prettyprint:
Array.prototype.slice.call(document.getElementsByTagName('pre')).forEach(function(v,k,arra){
  v.className += ' prettyprint';
});

(function(){

//
// Find as you type search
//
// get elements
var qc = document.getElementById('q-container'),
	q = document.getElementById('q'),
	r = document.getElementById('r');
// request json
window.ajax = (window.XMLHttpRequest) ? new XMLHttpRequest() : new ActiveXObject('Microsoft.XMLHTTP');
window.jsonResponses = [];
ajax.onreadystatechange = function (responseText) {
	if (ajax.readyState == 4) {
		window.jsonResponses = eval('('+ajax.responseText+')');
	}
}
ajax.open('GET', 'search_index.json', true);
ajax.send(null);

// basic feature tests for the livesearch:
if (![].forEach && !document.getElementsByClassName){
  q.parentNode.removeChild(q);
  return;
}

// search on keyup
addEvent('keyup',q, function(e) {
		var queryLowerCase = q.value.toLowerCase(),
			queryStartRe = new RegExp('^'+queryLowerCase, 'i'),
			resultList = [],
			startI = -1,
			allI = -1,
			maxResults = 10,
			jsonResponse,
			keyCode = e.keyCode;
		
		// quit if we're just navigating.
		if (keyCode == 40 || keyCode == 38) return;
  			
		while ((jsonResponse = jsonResponses[++startI])) {
			var resultText = jsonResponse.text,
				resultTextLowerCase = resultText.toLowerCase(),
				resultURL = jsonResponse.uri,
        resultSection = jsonResponse.section;
			if (maxResults && queryStartRe.test(resultTextLowerCase)) {
				resultList.push('<li><a href="http://developers.whatwg.org/'+resultURL+'">'+resultText+' <span>Section '+resultSection+'</span></a></li>');
				--maxResults;
			}
		}
		while ((jsonResponse = jsonResponses[++allI])) {
			var resultText = jsonResponse.text,
				resultTextLowerCase = resultText.toLowerCase(),
				resultURL = jsonResponse.uri,
        resultSection = jsonResponse.section;
			if (maxResults && resultTextLowerCase.indexOf(queryLowerCase) > -1) {
				resultList.push('<li><a href="http://developers.whatwg.org/'+resultURL+'">'+resultText+' <span>Section '+resultSection+'</span></a></li>');
				--maxResults;
			}
		}
		r.innerHTML = resultList.join('');
	}
);

// focus search on click on search area
addEvent('click', qc, function(e) {
		q.focus();
	}
);

// move between query and results with keyboard
addEvent('keydown', q, function(e) {
		var keyCode = e.keyCode;
		var results = r.getElementsByTagName('a');
		var selected = r.getElementsByClassName('selected')[0];

	  if (keyCode == 13) { // enter
	    location.href = selected.href;
	  }
	  		
		Array.prototype.slice.call(results).forEach(function(v,k,arra){
      v.classList.remove('selected');
    });
    
    try {
      
  		if (keyCode == 40) { // down
  		  var elem = !selected ? results[0] : selected.parentNode.nextSibling.firstChild;
  		  elem.classList.add('selected');
  		}
  		if (keyCode == 38) { // up
  		  var elem = !selected ? results[results.length - 1] : selected.parentNode.previousSibling.firstChild;
  		  elem.classList.add('selected');
  	  }
  	  
    } catch(e){}
	}
);


// focus element on mouse over
addEvent('mousemove', r, function(e) {
		var target = e.target || e.srcElement;
		if (target && target.nodeName == 'A') {
		  
		  Array.prototype.slice.call(r.getElementsByTagName('a')).forEach(function(v,k,arra){
        v.classList.remove('selected');
      });
      
			target.classList.add('selected');
		}
	}
);

})();

