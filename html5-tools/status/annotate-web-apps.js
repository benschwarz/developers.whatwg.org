/**
 * Author: Charl van Niekerk <charlvn@charlvn.za.net>
 * Contributor: Simon Pieters <zcorpan@gmail.com>
 */

function annotateToc() {
  var toc = document.getElementById("contents");
  if (toc) {
    toc.innerHTML += " <button onclick=\"parentNode.className = /\ edit$/.test(parentNode.className) ? parentNode.className.replace(' edit','') : parentNode.className += ' edit'; innerHTML = innerHTML == 'Edit markers' ? 'Hide interface' : 'Edit markers'\">Edit markers</button>";
    toc = toc.nextSibling;
    while (toc.nodeType != 1)
      toc = toc.nextSibling;
    var form = document.createElement("form");
    form.method = "post";
    form.action = "http://status.whatwg.org/update-markers.php";
    toc.parentNode.insertBefore(form, toc)
    form.appendChild(toc);
    var div = document.createElement("div");
    div.innerHTML = "<pre id=annotation-log></pre>\
                     <p><label>Email: <input type=email name=email required></label></p>\
                     <p><label>Rationale for changes: <input name=rationale required maxlength=125 size=70></p>\
                     <p><input type=submit value=Save></p>";
    form.appendChild(div);
    var links = toc.getElementsByTagName("a");
    var link;
    var span;
    var id;
    for (var i = 0, len = links.length; i < len; ++i) {
      link = links[i];
      id = link.href.split("#")[1];
      span = document.createElement("span");
      span.innerHTML = " <label><input type=radio name=" + id + " value=TBW>TBW</label>\
                         <label><input type=radio name=" + id + " value=WIP>WIP</label>\
                         <label><input type=radio name=" + id + " value=SCS>SCS</label>\
                         <label><input type=radio name=" + id + " value='' checked>none</label>";
      if (link.nextSibling)
        link.parentNode.insertBefore(span, link.nextSibling)
      else
        link.parentNode.appendChild(span);
    }
  }
}
annotateToc();

function annotateLoad(data) {
	var log = "";
	var sections = data.getElementsByTagName("section");
	for (var i = 0; i < sections.length; i++) {
		var id = sections[i].getAttribute("id");
		var status = sections[i].getAttribute("status");
		var e = document.getElementById(id);
		if (e) {
			var spans = e.getElementsByTagName("span");
			if (spans && spans.length > 0 && spans[0].nextSibling) {
				var span = document.createElement("span");
				span.setAttribute("title", status);
				span.appendChild(document.createTextNode("[" + status + "]"));
				e.insertBefore(span, spans[0].nextSibling);
			}
			var div = document.createElement("div");
			div.className = status;
			e.parentNode.insertBefore(div, e);
			var level = e.tagName.split("H")[1];
			var current = div.nextSibling
			div.appendChild(current);
			while (current = div.nextSibling) {
				var tag = current.tagName;
				if (tag == "DIV" && /^H\d$/.test(current.firstChild.tagName))
					tag = current.firstChild.tagName;
				if (/^H(\d)$/.test(tag) && RegExp.$1 <= level)
					break;
				div.appendChild(current);
			}
		}
		var r = document.forms[0][id];
		if (r) {
			if (status == "TBW") {
				r[0].checked = true;
				r[0].value = "";
				r[0].parentNode.className = "initial";
				r[3].value = "none";
			} else if (status == "WIP") {
				r[1].checked = true;
				r[1].value = "";
				r[1].parentNode.className = "initial";
				r[3].value = "none";
			} else if (status == "SCS") {
				r[2].checked = true;
				r[2].value = "";
				r[2].parentNode.className = "initial";
				r[3].value = "none";
			} else {
				log += "Didn't recognize status " + status + ". Do you have a cached version of the <a href=http://status.whatwg.org/annotate-web-apps.js>annotation script</a>?\n";
			}
		} else {
			log += "The ID " + id + " wasn't found.\n";
		}
	}
	if (log)
	  document.getElementById("annotation-log").innerHTML = log;
}

function annotateHandle() {
	if (req.readyState == 4 && req.status == 200 && req.responseXML) {
		annotateLoad(req.responseXML);
	}
}

var req = new XMLHttpRequest();
req.onreadystatechange = annotateHandle;
req.open("GET", "annotate-data.xml", true); // xhr is relative to the document, not where the script was found
req.send(null);

var style = document.createElement("style");
style.type = "text/css"; // required in html4...
var styleText = document.createTextNode("\
 .TBW, .WIP, .SCS { margin-left:-2em; border-left:.2em solid; padding-left:1.8em; }\
 .TBW { border-color:red; }\
 .WIP { border-color:orange; }\
 .SCS { border-color:green; }\
 .toc label { font-size:x-small; display:none; }\
 .toc input { vertical-align:bottom; }\
 .toc .initial { background-color:yellow; font-weight:bold; }\
 .toc + div { display:none; }\
 .edit button { display:none; }\
 .edit + form .toc label { display:inline; }\
 .edit + form .toc + div { display:block; }\
 ");
var an3err
try { style.appendChild(styleText) } 
catch(an3err) { 
if(an3err.number == -0x7FFF0001) style.styleSheet.cssText =
styleText.nodeValue 
else throw an3err } 
document.getElementsByTagName("head")[0].appendChild(style);


/*
 * Author: Lachlan Hunt - http://lachy.id.au/
 * Date: 2007-08-15
 *
 * getElementsByClassName was wrtten by Tino Zijdel
 * http://therealcrisp.xs4all.nl/blog/2007/08/13/getelementsbyclassname-re-re-re-visited/
 */
 
var getElementsByClassName = function()
{
    // native
    if (document.getElementsByClassName)
    {
        return function(className, nodeName, parentElement)
        {
            var s = (parentElement || document).getElementsByClassName(className);

            if (nodeName && nodeName != '*')
            {
                nodeName = nodeName.toUpperCase();
                return Array.filter(s, function(el) { return el.nodeName == nodeName; });
            }
            else
                return [].slice.call(s, 0);
        }
    }

    // xpath
    if (document.evaluate)
    {
        return  function(className, nodeName, parentElement)
        {
            if (!nodeName) nodeName = '*';
            if (!parentElement) parentElement = document;

            var results = [], s, i = 0, element;

            s = document.evaluate(
                ".//" + nodeName + "[contains(concat(' ', @class, ' '), ' " + className + " ')]",
                parentElement,
                null,
                XPathResult.ORDERED_NODE_SNAPSHOT_TYPE,
                null
            );

            while ((element = s.snapshotItem(i++)))
                results.push(element);

            return results;
        }
    }

    // generic
    return function(className, nodeName, parentElement)
    {
        if (!nodeName) nodeName = '*';
        if (!parentElement) parentElement = document;

        var results = [], s, i = 0, element;
        var re = new RegExp('(^|\s)' + className + '(\s|$)'), elementClassName;

        s = parentElement.getElementsByTagName(nodeName);

        while ((element = s[i++]))
        {
            if (    (elementClassName = element.className) &&
                (elementClassName == className || re.test(elementClassName))
            )
                results.push(element);
        }

        return results;
    }
}();

function markIssue(issue) {
	var marker = document.createElement("strong");
	marker.innerHTML = "Big Issue: ";
	issue.insertBefore(marker, issue.firstChild);
}

var issues = getElementsByClassName("big-issue");
for (var i = 0; i < issues.length; i++) {
	markIssue(issues[i]);
}