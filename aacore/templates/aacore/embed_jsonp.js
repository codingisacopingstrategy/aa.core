var activearchives = {};

activearchives.init_embeds = function () {
    $("*[rel='aa:embed']").each(function () {
        // $(this).html("foo");
        var that = this;
        function poll () {
            $.ajax("{{embed_url}}", {
                method: 'GET',
                dataType: "jsonp",
                data: {
                    url: $(this).attr("href"),
                    filter: $(this).attr("data-filter")
                },
                success: function (data) {
                    if (data.ok) {
                        $(that).html(data.content);
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
};

$(function () {
    activearchives.init_embeds();
});

