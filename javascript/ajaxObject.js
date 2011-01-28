function ajaxObject(url, callbackFunction) {
	var instance = this;
	instance.updating = false;
	instance.abort = function () {
		if (instance.updating) {
			instance.updating = false;
			instance.AJAX.abort();
			instance.AJAX = null;
		}
	}
	instance.update = function (passData, postMethod) {
		if (instance.updating) return false;
		instance.AJAX = null;
		instance.AJAX = (window.XMLHttpRequest) ? new XMLHttpRequest() : new ActiveXObject('Microsoft.XMLHTTP');
		if (instance.AJAX == null) return false;
		instance.AJAX.onreadystatechange = function () {
			if (instance.AJAX.readyState == 4) {
				instance.updating = false;
				instance.callback(instance.AJAX.responseText, instance.AJAX.status, instance.AJAX.responseXML);
				instance.AJAX = null;
			}
		}
		instance.updating = new Date();
		if (/post/i.test(postMethod)) {
			var uri = urlCall+'?'+instance.updating.getTime();
			instance.AJAX.open('POST', uri, true);
			instance.AJAX.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
			instance.AJAX.setRequestHeader('Content-Length', passData.length);
			instance.AJAX.send(passData);
		} else {
			var uri = urlCall+'?'+passData+'&timestamp='+(instance.updating.getTime());
			instance.AJAX.open('GET', uri, true);
			instance.AJAX.send(null);
		}
		return true;
	}
	var urlCall = url;
	instance.callback = callbackFunction || function () {};
}

