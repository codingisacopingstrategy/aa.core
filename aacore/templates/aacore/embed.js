(function ($) {

function ffind (selector, context, each) {
    // "filter find", like $.find but it also checks the context element itself
    return $(context).filter(selector).add(selector, context);
}

$(document).bind("refresh", function (evt) {
    // console.log("refreshing embeds...");
    var context = evt.target;
    ffind("*[rel='aa:embed']", context).each(function () {
        // $(this).html("foo");
        var that = this;
        function poll () {
            $.ajax("{{embed_url}}", {
                // type: 'GET',
                // dataType: "jsonp",
                data: {
                    url: $(that).attr("href"),
                    // filter: $(that).attr("data-filter")
                    filter: $(that).text()
                },
                success: function (data) {
                    // console.log("data", data, data.ok);
                    if (data.ok) {
                        var new_content = $(data.content);
                        $(that).replaceWith(new_content);
                        $(new_content).trigger("refresh");
                    } else {
                        if (data.content) {
                            $(that).html(data.content);
                        }
                        window.setTimeout(poll, 2500);
                    }
                },
                error: function (a, b, c) {
                    // console.log("error", a, b, c);
                }
            });
        }
        poll();
    });

    // Embed Links show/hide on rollover 
    ffind("div.aa_embed", context).each(function () {
        $(this).mouseover(function () {
            // console.log("mouseover", this);
            $(".links", this).show();
        }).mouseout(function () {
            $(".links", this).hide();
        });
    });

    // DIRECTLINKs
    // Make directlinks draggable
    $("a.directlink", context).each(function () {
        // console.log("directlink", this);
        $(this).draggable({helper: function () {
            return $(this).clone().appendTo("body");
        }});
    });
    // h1's are droppable to set about
    ffind(".section1", context).find("h1").droppable({
        accept: ".directlink",
        hoverClass: "drophover",
        drop: function (evt, ui) {
            // console.log("drop", evt, ui);
            var href = $(ui.helper).attr("href");
            var s1 = $(this).closest(".section1");
            s1.attr("about", href);
            // console.log("href", href, this);
            // post_styles(s1);
            // TODO:
           //  post_about(s1);
            resetTimelines();
            // s1.trigger("refresh");
        }
    });

});

})(jQuery);
