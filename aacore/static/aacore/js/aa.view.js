// TODO: update the HTML after changing the geometry of a box: right now it
// might be triggering a bug because submit changes "by hand" the code reads
// html data-start and data-stop attributes


(function($) {

var post_geometry = function(event, ui) {
    /*
     * Saves the new geometry in the markdown source
     */

    // RegExp
    var HASH_HEADER_RE = /(^|\n)(#[^#].*?)#*(\n|$)/;
    var STYLE_ATTR_RE = /{@style=.*?}/; 

    // Section related variables 
    var $target = $(event.target);
    var $form = $target.find('form');
    var $textarea = $form.find('textarea');
    var value = $textarea.val();
    var start = parseInt($form.find('input[name="start"]').val());
    var end = parseInt($form.find('input[name="end"]').val());

    // Post form variables
    var new_start;  // start offset
    var end;  // end offset
    var content = "";  //
    var page = window.page;  // TODO: put window.page in its own namespace

    // Matches the annotation header
    var header_match = HASH_HEADER_RE.exec(value);
    if (header_match) {
        // Defines the substring to replace
        var style_match = STYLE_ATTR_RE.exec(header_match[0]);
        if (style_match) {
            new_start = start + style_match.index;
            end = new_start + style_match[0].length;
        } else {
            new_start = start + header_match.slice(1,3).join('').length;
            end = new_start;
            content += " ";  // Adds one space for readability
        };
        // Defines the new position attributes
        content += "{@style=top: " + ui.position.top + "px; left: " + ui.position.left + "px; width: " + $target.width() + "px; height: " + $target.height() + "px;}";
        // Updates the content of the annotation
        var c = style_match ? style_match[0].length : 0;
        $.post($form.attr('action'),
            {
                content: content,
                page: page, 
                start: new_start,
                end: end,
            }, function(data) {
                // Replaces the markdown source with the new value.
                var rel_start = new_start - start;
                var before = value.substring(0, rel_start);
                var after = value.substring(rel_start + c, rel_start + c + value.length)
                $textarea.val(before + content + after);
                //$textarea.val(value.substring(0, new_start) + content + value.substring(end, value.length));
                var delta = value.length - $textarea.val().length;
                var found = null;
                $('input[name="start"],input[name="end"]').each(function() {
                    var val = parseInt($(this).val());
                    if (value !== 0) {
                        $(this).val(val - delta);
                    };
                })
                // TODO: Compute the new HTML
        });
    };
}

function init() {
    // Makes annotations draggable and resizable
    $("section.annotation1").draggable({
        handle:'nav',
        grid: [50, 50],
        zIndex: 2700,
        stop: post_geometry,
    }).resizable({
        grid: 50,
        stop: post_geometry,
    });
}

$(document).ready(function() {
    
    init();
    window.init = init;

    $("a.edit").live("click", function() {
        $(this).parents("section")
            .children()
            .hide()
        .end()
            .find("nav")
            .show()
        .end()
            .find("form.source")
            .show();
    });

    $("input.cancel").live("click", function() {
        $(this).parents("section")
            .children()
            .show()
        .end()
            .find("form.source")
            .hide();
    });

    $("input.submit").live("click", function(e) {
        e.preventDefault();
        var $elt = $(this).parents("section");
        var content = $elt.find("textarea").val();
        var post_url = $elt.find("form").attr("action");
        var start = $elt.find("input[name='start']").val();
        var end = $elt.find("input[name='end']").val();

        $.post(post_url, 
            {
                content: content,
                page: window.page,
                start: start,
                end: end,
            }, function(data) {
                $elt.replaceWith(data) && init();
        });
    });
});
})(jQuery);
