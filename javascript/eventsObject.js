window.addEvent = (window.addEventListener) ? function(type, node, fn) {
	node.addEventListener(type, fn, false);
} : function(type, node, fn) {
	node.attachEvent(
		'on'+type,
		function(e) {
			fn.apply(node, [e]);
		}
	);
};

