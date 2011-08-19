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
    $("section.annotation").draggable({
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

    $("a.edit").live("click", function() {
        $(this).parents("section")
            .find("form.source")
            .show()
        .end()
            .find("article.rendered")
            .hide();
    });

    $("input.cancel").live("click", function() {
        $(this).parents("section")
            .find("form.source")
            .hide()
        .end()
            .find("article.rendered")
            .show();
    });

    $("input.submit").live("click", function(e) {
        var $elt = $(this).parents("section");
        var content = $elt.find("textarea").val();
        var post_url = $elt.attr("data-post-url");

        $.post(post_url, 
            {
                content: content,
                page: "{{ page }}",
            }, function(data) {
                $elt.replaceWith(data);
        });
    });
});
})(jQuery);
