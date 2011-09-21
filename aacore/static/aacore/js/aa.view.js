(function($) {
$(document).ready(function() {
    $("section.annotation1 div.wrapper").autoscrollable();

    $("video").each(function(){
        var url = $("[src]:first", this).attr('src');
        $(this).timeline({
            show: function (elt) {
                $(elt).closest('section.annotation1').find('div.wrapper').autoscrollable("scrollto", elt);
                $(elt).addClass("active");
            },
            hide: function (elt) {
                $(elt).removeClass("active");
            },
            start: function (elt) {
                var start = $('[property="aa:start"]:first', $(elt)).attr('content');
                return start;
            },
            end: function (elt) {
                var end = $('[property="aa:end"]:first', $(elt)).attr('content');
                return end;
            }
        }).timeline("add", 'section.annotation1[about="' + url + '"] section.annotation2');
    });

    // Clicking subtitles jumps to that time in the video
    $('span[property="aa:start"],span[property="aa:end"]').click(function () {
        var t = $.timecode_tosecs_attr($(this).attr("content"));
        var video = $('video source[src="' + $(this).parents('section.annotation1').attr('about')  + '"]').parent('video')[0];
        video.currentTime = t;
        video.play();
    });

    $('section.annotation1').aaplaylist();
});
})(jQuery);
