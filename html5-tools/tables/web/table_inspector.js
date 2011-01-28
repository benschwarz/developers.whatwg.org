
Highlighter = function() {
  this.current_displayed_element = null;
  this.heading_id_regexp = new RegExp("^__tableparser_heading_id_.*_\d*");

  this.toggle_heading_information = function(element) {
    toggle_class(element, "__tableparser_active_cell");
  };

  this.toggle_highlight_heading = function(element) {
    toggle_class(element, "__tableparser_active_heading");
  };

  this.is_heading_id = function(id) {
    //Check if a id matches the format for a heading id
    return this.heading_id_regexp.test(id);
  };

  this.heading_ref_ids = function(element) {
    /*Get a list of heading ids on an element*/
    var heading_ids = [];
    if (element.hasAttribute("headers")) {
      var ids = element.getAttribute("headers").split(" ");
      for (var j=0; j<ids.length; j++) {
	//XXX -Not clear this test is actually useful
	if (this.is_heading_id(ids[j])) {
	  heading_ids.push(ids[j]);
	};
      };
    } else {
      var heading_ids = [];
    };
    return heading_ids;
  };

  this.cell_identify_headings = function(element) {
    /*Get an array of heading elements corresponding to a particular cell*/
    var headings = this.heading_ref_ids(element);
    var heading_elements = [];
    for (var i=0; i<headings.length; i++) {
      var heading = document.getElementById(headings[i]);
      if (heading != null) {
	heading_elements.push(heading);
      } else {
	//Otherwise we have an error somewhere
	//Alert here is not very user friendly
	alert("Missing id " + headings[i] + "- this is a bug");
      }
    };
    return heading_elements;
  };

  this.cell_click = function(event) {
    /*Callback when a cell is clicked on*/
    var new_element = event.currentTarget;
    var elements = [this.current_displayed_element, new_element];

    for (var i=0; i<elements.length; i++) {
      var element = elements[i];
      if (element != null) {
	this.toggle_heading_information(element);
	var headings = this.cell_identify_headings(element);
	for (var j=0; j<headings.length; j++) {
	  this.toggle_highlight_heading(headings[j]);
	};
      };
    };
    
    //Save a ref to the element currently being displayed
    this.current_displayed_element = new_element;
  };
}

function toggle_class(element, class_name) {
  //Add or remove a classname from an element
  var element_class = "";
  if (element.hasAttribute("class")) {
    element_class = element.getAttribute("class");
  };
  
  if (element_class.indexOf(class_name) != -1) {
    var new_class = element_class.substr(0, element_class.indexOf(class_name));
    new_class += element_class.substr(element_class.indexOf(class_name)+class_name.length);
    element_class = new_class;
  } else {
    //Need to add the classname
    if (element_class != "") {
      element_class += " ";
    };
    element_class += class_name;
  };
  element.setAttribute("class", element_class);
};

function add_display_options() {
  /*Add a checkbox to display all headings or not when script is enabled*/
    var heading = document.createElement("h2");
    heading.appendChild(document.createTextNode("Display Options"));

    var help = document.createElement("p");
    help.appendChild(document.createTextNode("To highlight the headers associated with a particular cell, click that cell."));

    var label = document.createElement("label");
    label.appendChild(document.createTextNode("Display all headings"));
    
    var checkbox = document.createElement("input");
    checkbox.setAttribute("type", "checkbox");
    checkbox.setAttribute("id", "display_all_headings");
    //checkbox.setAttribute("checked", "checked");
    checkbox.addEventListener("change", function(event){toggle_view_all_headings();}, 
                              false);
    label.appendChild(checkbox);
    
    var p = document.createElement("p");
    p.appendChild(label);
    
    var div = document.createElement("div");
    div.setAttribute("class", "section");
    var form = document.createElement("form");
    form.appendChild(p);
    
    div.appendChild(heading);
    div.appendChild(help);
    div.appendChild(form);
    
    var body = document.getElementsByTagName("body")[0];
    var h1 = document.getElementsByTagName("h1")[0];

    body.insertBefore(div, h1.nextSibling);
};

function toggle_view_all_headings() {
    /*Toggle the display of all the headings at once vs only those
      for the currently selected cell*/
    var view_headings = document.getElementById("display_all_headings").checked;
    if (document.selectedStyleSheetSet) {
      //Use the alternate stylesheets if we have DOM access to them
      if (view_headings) {
        document.selectedStyleSheetSet = 'Headings Visible';
      } else {
        document.selectedStyleSheetSet = 'Headings Hidden';
      };
    } else {
      //Use simple DOM methods
      //Containers and titles should have the same length
      var containers = getElementsByClassName("__tableparser_heading_container");
      var titles = getElementsByClassName("__tableparser_heading_title");
      
      if (view_headings) {
	for (var i=0; i < containers.length; i++) {
	  containers[i].style.display = "block";
	  titles[i].style.display = "block";
	}
      } else {
	for (var i=0; i < containers.length; i++) {
	  containers[i].style.display = "none";
	  titles[i].style.display = "none";
	};
      };
    };
};
    
function getElementsByClassName(searchClass, node) {
  /*Javascript gEBCN that uses native function when avaliable
    adapted from http://www.dustindiaz.com/getelementsbyclass/
   */

    if ( node == null )
        node = document;

    if (node.getElementsByClassName) {
        return node.getElementsByClassName(searchClass);
    };

    var classElements = new Array();
    var els = node.getElementsByTagName('*');
    var elsLen = els.length;
    var pattern = new RegExp("(^|\\s)"+searchClass+"(\\s|$)");
    for (i = 0, j = 0; i < elsLen; i++) {
        if ( pattern.test(els[i].className) ) {
            classElements[j] = els[i];
            j++;
        }
    }
    return classElements;
};

function load_page() {

  highlighter = new Highlighter();

  //Callback close for click events
  function click_callback(event) {
    highlighter.cell_click(event);  
  }

  //Attach event listeners to all td and th elements
  var heading_elements = document.getElementsByTagName("th");
  var data_elements = document.getElementsByTagName("td");
  for (var i=0; i<heading_elements.length; i++) {
    heading_elements[i].addEventListener("click", click_callback, false);
  };
  for (var i=0; i<data_elements.length; i++) {
    data_elements[i].addEventListener("click", click_callback, false);
  };

  add_display_options();
  toggle_view_all_headings();

};
