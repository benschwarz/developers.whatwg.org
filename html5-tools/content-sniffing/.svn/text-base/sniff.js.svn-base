var s = '';
var pos = 0;
var output = document.getElementById("output");

function sniff(input) {
	var type = null;
	pos = 0;
	s = input.slice(0, 512);
	while (s[pos] && !type) {
		switch (s[pos]) {
		case '\t':
		case ' ':
		case '\n':
		case '\r':
			pos++;
			break;
		case '<':
			pos++;
			if (findComment() || findMarkedSection() || findPI()) break; // Steps 6 to 8

			if (isAtom()) { // Step 9
				type = "application/atom+xml";
			} else if (isRSS() || isRDF()) {
				type = "application/rss+xml"
			} else {
				type = "text/html";
			}
			break;
		default:
			type = "text/html";
			break;
		}
	}
	return type || "text/html";
}

function isAtom() {
	return (s.substr(pos, 4) == "feed");
}

function isRSS() {
	return (s.substr(pos, 3) == "rss");
}

function isRDF() {
	// This is not yet fully implemented because it's not fully specced yet!
	return (s.substr(pos, 7) == "rdf:RDF");
}

function findComment() {
	if (s.substr(pos, 3) == "!--") { // 6
		pos += 3; // 6.1
		while (s[pos]) {
			if (s.substr(pos, 3) == "-->") { // 6.2
				pos += 3;
				break;
			}
			pos++; // 6.3
		} // 6.4
		return true;
	}
	return false;
}

function findMarkedSection() {
	if (s[pos] == '!') {
		pos++;
		while (s[pos] && s[pos++] != '>');
		return true;
	}
	return false;
}

function findPI() {
	if (s[pos] == '?') {
		pos++;
		while (s[pos]) {
			if (s.substr(pos, 2) == "?>") {
				pos += 2;
				break;
			}
			pos++;
		}
		return true;
	}
	return false;
}

function w(text) {
	output.innerHTML += text + "\n";
}

function clearLog() {
	output.innerHTML = "";
}
