// TODO: update the HTML after changing the geometry of a box: right now it
// might be triggering a bug because submit changes "by hand" the code reads
// html data-start and data-stop attributes


(function($) {

var post_geometry = function(event, ui) {
    // Saves the new geometry in the markdown source

    // RegExp
    var HASH_HEADER_RE = /(^|\n)(#[^#].*?)#*(\n|$)/;
    var STYLE_ATTR_RE = /{@style=.*?}/; 

    // Section variables 
    var target = $(event.target);
    var post_url = target.find("form").attr("action");
    var source = target.find('textarea');
    var value = source.val();

    // Post form variables
    var start;
    var end;
    var content;
    var page = window.page;  // TODO: put window.page in its own namespace

    // Matches the annotation header
    var header_match = HASH_HEADER_RE.exec(value);
    if (header_match) {
        // Defines the substring to replace
        var style_match = STYLE_ATTR_RE.exec(header_match[0]);
        var prev_start = parseInt(target.find('input[name="start"]').val()) - 1;
        if (style_match) {
            start = prev_start;
            end = start + style_match[0].length;
        } else {
            start = prev_start + header_match[1].length + header_match[2].length;
            end = start;
        };
        // Defines the new position attributes
        content = "{@style=top: " + ui.position.top + "px; left: " + ui.position.left + "px; width: " + target.width() + "px; height: " + target.height() + "px;}";
        // Updates the content of the annotation
        $.post(post_url,
            {
                content: content,
                page: page, 
                start: start,
                end: end,
            }, function(data) {
                // Replaces the markdown source with the new value.
                source.val(value.substring(0, start) + content + value.substring(end, value.length));
                //var delta = value.length - source.val().length;
                //$('input[name="start"],input[name="end"]').each(function() {
                    //var val = parseInt($(this).val());
                    //if (value !== 0) {
                        //$(this).val(val - delta);
                    //};
                //})
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
