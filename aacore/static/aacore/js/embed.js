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
                    filter: $(that).attr("data-filter")
                },
                success: function (data) {
                    if (data.ok) {
                        // NEW: december 16 (Alex)
                        // In addition to content there are three new keys:
                        // - extra_css: loads extra link rel="stylesheet"
                        // - extra_js: load extra script
                        // - script: extra javascript code to execute
                        for (var i = 0; i < data.extra_css.length; i++) {
                            var href = data.extra_css[i];
                            //if (!$('link[href="' + href + '"]').length) {
                            $('<link rel="stylesheet" type="text/css" media="screen">')
                                .attr("href", href)
                                .appendTo($('head'));
                            //};
                        };
                        for (var i = 0; i < data.extra_js.length; i++) {
                            var src = data.extra_js[i];
                            $('<script>').attr("src", src).appendTo($('head'));
                        };

                        var new_content = $(data.content);
                        $(that).replaceWith(new_content);

                        // FIXME: This is a hack to make sure the html is load before executing the script.
                        //new_content.ready(function() {
                        setTimeout(function() {
                            var script_elt = document.createElement('script');
                            script_elt.text = data.script
                            var head = document.getElementsByTagName('body')[0].appendChild(script_elt);
                            //$(script_elt).appendTo($('head'));
                        }, 1000);
                        //});

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
