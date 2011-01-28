String.prototype.toAsciiLowerCase = function () {
  var output = "";
  for (var i = 0, len = this.length; i < len; ++i) {
    if (this.charCodeAt(i) >= 0x41 && this.charCodeAt(i) <= 0x5A) {
      output += String.fromCharCode(this.charCodeAt(i) + 0x20)
    } else {
      output += this.charAt(i);
    }
  }
  return output;
}

function indent(ancestors) {
  var str = "";
  if (ancestors > 0) {
    while (ancestors--)
      str += "  ";
  }
  return str;
}

function dom2string(node, ancestors) {
  var str = "";
  if (typeof ancestors == "undefined")
    var ancestors = 0;
  if (!node.firstChild)
    return "\n| ";
  var parent = node;
  var current = node.firstChild;
  var next = null;
  var misnested = null;
  for (;;) {
    str += "\n| " + indent(ancestors);
    switch (current.nodeType) {
      case 10:
        str += '<!DOCTYPE ' + current.nodeName + '>';
        break;
      case 8:
        try {
          str += '<!-- ' + current.nodeValue + ' -->';
        } catch (e) {
          str += '<!--  -->';
        }
        if (parent != current.parentNode) {
          return str += ' (misnested... aborting)';
        }
        break;
      case 7:
        str += '<?' + current.nodeName + current.nodeValue + '>';
        break;
      case 4:
        str += '<![CDATA[ ' + current.nodeValue + ' ]]>';
        break;
      case 3:
        str += '"' + current.nodeValue + '"';
        if (parent != current.parentNode) {
          return str += ' (misnested... aborting)';
        }
        break;
      case 1:
        str += "<" + current.nodeName.toAsciiLowerCase() + '>'; // seems there's no way to get the name in a case-preserving manner :-(
        if (parent != current.parentNode) {
          return str += ' (misnested... aborting)';
        } else {
          if (current.attributes) {
            var arrAttrs = [];
            for (var j = 0; j < current.attributes.length; j += 1) {
              if (current.attributes[j].specified) {
                arrAttrs.push(current.attributes[j].nodeName);
              }
            }
            if (arrAttrs.length > 0) {
              arrAttrs.sort();
              for (var j = 0; j < arrAttrs.length; j += 1) {
                str += "\n| " + indent(1 + ancestors) + arrAttrs[j];
                str += '="' + current.attributes[arrAttrs[j]].nodeValue + '"';
              }
            }
          }
          if (next = current.firstChild) {
            parent = current;
            current = next;
            ancestors++;
            continue;
          }
        }
        break;
    }
    for (;;) {
      if (next = current.nextSibling) {
        current = next;
        break;
      }
      current = current.parentNode;
      parent = parent.parentNode;
      ancestors--;
      if (current == node) {
        return str;
      }
    }
  }
}
