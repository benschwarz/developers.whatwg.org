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
// search on keyup
addEvent(
	'keyup',
	q,
	function(e) {
		var queryLowerCase = q.value.toLowerCase(),
			queryStartRe = new RegExp('^'+queryLowerCase, 'i'),
			resultList = [],
			startI = -1,
			allI = -1,
			maxResults = 5 * queryLowerCase.length,
			jsonResponse;
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
// focus search on click
addEvent(
	'click',
	qc,
	function(e) {
		q.focus();
	}
)
// move between query and results with keyboard
addEvent(
	'keydown',
	q,
	function(e) {
		var keyCode = e.keyCode;
		var resultsNodeArray = r.getElementsByTagName('a');
		if (keyCode == 40) resultsNodeArray[0].focus();
		if (keyCode == 38) resultsNodeArray[resultsNodeArray.length - 1].focus();
	}
);
// move between query and results with keyboard
addEvent(
	'keydown',
	r,
	function(e) {
		var target = e.target || e.srcElement;
		var keyCode = e.keyCode;
		var parentLi = target.parentNode;
		var prevNode = parentLi.previousSibling ? parentLi.previousSibling.getElementsByTagName('a')[0] : q;
		var nextNode = parentLi.nextSibling ? parentLi.nextSibling.getElementsByTagName('a')[0] : q;
		if (keyCode == 40) nextNode.focus();
		if (keyCode == 38) prevNode.focus();
	}
);
// focus element on mouse over
addEvent(
	'mousemove',
	r,
	function(e) {
		var target = e.target || e.srcElement;
		if (target && target.nodeName.toLowerCase() == 'a') {
			target.focus();
		}
	}
);

