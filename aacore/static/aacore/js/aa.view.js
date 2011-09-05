(function($) {

var post_geometry = function(event, ui) {
    // Saves the new geometry in the markdown source
    var target = $(event.target);
    $.post("edit/geometry/", {
            id: "#" + target.find('h1').attr('id'),
            width: target.width(),
            height: target.height(),
            top: ui.position.top,
            left: ui.position.left,
        }, function(data) {
            // Updates the geometry variable
            window.geometry = $.parseJSON(data);
    });
}

function init() {
    // Sets annotation geometry
    if (typeof(geometry) != 'undefined') { 
        for (i in geometry) {
            $(i).parents("section")
                .width(geometry[i]['width'])
                .height(geometry[i]['height'])
                .css('top', geometry[i]['top'] + "px")
                .css('left', geometry[i]['left'] + "px");
        }
    }

    // Makes annotations draggable and resizable
    $("section.annotation1").draggable({
        handle:'nav',
        grid: [50, 50],
        zIndex: 2700,
        //stop: post_geometry,
    }).resizable({
        grid: 50,
        //stop: post_geometry,
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
                page: "{{ page }}",
                start: start,
                end: end,
            }, function(data) {
                $elt.replaceWith(data) && init();
        });
    });
});
})(jQuery);
