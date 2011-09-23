(function ($) {

// caret functions from
// http://pastebin.parentnode.org/78

function insertAtCaret(obj, text, newline) {
	// MM: added scroll code
	var scrollTop = obj.scrollTop;
	
    if (newline) text += "\n";
	if(document.selection) {
		obj.focus();
		var orig = obj.value.replace(/\r\n/g, "\n");
		var range = document.selection.createRange();
		if(range.parentElement() != obj) {
			return false;
		}
		range.text = text;
		var actual = tmp = obj.value.replace(/\r\n/g, "\n");
		for(var diff = 0; diff < orig.length; diff++) {
			if(orig.charAt(diff) != actual.charAt(diff)) break;
		}
		for(var index = 0, start = 0; 
			tmp.match(text) 
				&& (tmp = tmp.replace(text, "")) 
				&& index <= diff; 
			index = start + text.length
		) {
			start = actual.indexOf(text, index);
		}
	} else if(obj.selectionStart !== undefined) { /* added to allow a selectionStart of 0 */
        // firefox oa
		var start = obj.selectionStart;
		var end   = obj.selectionEnd;
        var pre = obj.value.substr(0, start);
        var post = obj.value.substr(end, obj.value.length);
        if (newline) post = post.replace(/^[\r\n]+/,"");
		obj.value = pre + text + post;
	}
	if(start != null) {
		setCaretTo(obj, start + text.length);
	} else {
		obj.value += text;
	}
	// MM: Restore Scroll
	if (scrollTop) obj.scrollTop = scrollTop;
}

function setCaretTo(obj, pos) {
	if(obj.createTextRange) {
		var range = obj.createTextRange();
		range.move('character', pos);
		range.select();
	} else if(obj.selectionStart) {
		obj.focus();
		obj.setSelectionRange(pos, pos);
	}
}

$.insertAtCaret = insertAtCaret;
$.setCaretTo = setCaretTo;

})(jQuery);

