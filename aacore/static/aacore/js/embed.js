(function ($) {

var embed_url = $("link[rel='aa-embed']").attr("href");

$(document).bind("refresh", function (evt) {
    // console.log("refreshing embeds...");
    var context = evt.target;
    $(context).ffind("*[rel='aa:embed']").each(function () {
        var that = this;
        function poll () {
            $.ajax(embed_url, {
                data: {
                    url: $(that).attr("href"),
                    filter: $(that).text()
                },
                success: function (data) {
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
    $(context).ffind("div.aa_embed").each(function () {
        $(this).mouseover(function () {
            $(".links", this).show();
        }).mouseout(function () {
            $(".links", this).hide();
        });
    });

    // DIRECTLINKs
    // Make directlinks draggable
    $("a.directlink", context).each(function () {
        $(this).draggable({
            helper: function () {
                return $(this).clone().appendTo("body");
            }
        });
    });

    // h1's are droppable to set about
    $(context).ffind(".section1").find("h1").droppable({
        accept: ".directlink",
        hoverClass: "drophover",
        drop: function (evt, ui) {
            var href = $(ui.helper).attr("href");
            var s1 = $(this).closest(".section1");
            s1.attr("about", href);
            commit_attributes(s1);
            resetTimelines();
        }
    });
});
})(jQuery);