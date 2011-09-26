(function($) {

var TEXTAREA_MIN_PADDING_BOTTOM = 40;
var currentTextArea = undefined; /* used for timecode pasting */

$(document).ready(function() {
    // in a sense resetting timelines should happen whenever the page has changed (throttled?)

    function resetTimelines () {
        console.log("resetting timelines");
        /* Connect videos to timed sections */
        $("video").each(function(){
            var url = $(this).attr('src') || $("[src]:first", this).attr('src');
            $(this).timeline({
                show: function (elt) {
                    $(elt).addClass("active")
                        .closest('section.section1')
                            .find('div.wrapper:first')
                                .autoscrollable("scrollto", elt);
                },
                hide: function (elt) {
                    $(elt).removeClass("active");
                },
                start: function (elt) { return $(elt).attr('data-start') },
                end: function (elt) { return $(elt).attr('data-end') }
            }).timeline("add", 'section.section1[about="' + url + '"] *[data-start]');
        });
    }

    /// CLICKABLE TIMECODES
    $('span[property="aa:start"],span[property="aa:end"]').live("click", function () {
        var t = $.timecode_tosecs_attr($(this).attr("content"));
        var video = $('video[src="' + $(this).parents('*[about]').attr('about')  + '"]')[0] || $('video source[src="' + $(this).parents('*[about]').attr('about')  + '"]').parent('video')[0];
        // console.log("timecode click", this, t, video);
        if (video) {
            video.currentTime = t;
            video.play();
        }
    });

    /* Activate level-1 sections as (editable) playlists */
    $('section.section1').aaplaylist();
    $("section.section1 > div.wrapper").autoscrollable();

    resetTimelines();

    $("section textarea").live("focus", function () {
        currentTextArea = this;
        // ENSURE TEXTAREA HEIGHT IS OK HACK
        var $this = $(this);
        var textareaheight = $this.height();
        var sectionheight = $this.closest(".section1").height();
        if (textareaheight + TEXTAREA_MIN_PADDING_BOTTOM > sectionheight) {
            $this.css("height", (sectionheight - TEXTAREA_MIN_PADDING_BOTTOM) + "px");
        }
    }).live("blur", function () {
        currentTextArea = undefined;
    });

    /////////////////////////
    // SHORTCUTS

    function firstVideo () {
        /*
         * returns first playing video (unwrapped) element (if one is playing),
         * or just first video otherwise
         */
        $("video").each(function () {
            if (!this.paused) return this;
        });
        var vids = $("video:first");
        if (vids.length) return vids[0];
    }

    shortcut.add("Ctrl+Shift+Down", function () {
        if (currentTextArea) {
            var video = firstVideo();
            if (video) {
                var ct = $.timecode_fromsecs(video.currentTime, true);
                $.insertAtCaret(currentTextArea, ct + " -->", true);
            }
        }
    });

    shortcut.add("Ctrl+Shift+Left", function () {
        $("video").each(function () {
            this.currentTime = this.currentTime - 5;
        });
    });

    shortcut.add("Ctrl+Shift+Right", function () {
        $("video").each(function () {
            this.currentTime = this.currentTime + 5;
        });
    });
    shortcut.add("Ctrl+Shift+Up", function () {
        $("video").each(function () {
            var foo = this.paused ? this.play() : this.pause();
        });
    });
    /* }}} End shortcuts */

    $('div#tabs-2').aalayers({selector: 'section.section1'});
});
})(jQuery);
