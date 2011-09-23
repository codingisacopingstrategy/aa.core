(function($) {

var TEXTAREA_MIN_PADDING_BOTTOM = 30;
var currentTextArea = undefined; /* used for timecode pasting */

$(document).ready(function() {

    function resetTimelines () {
        /* Connect videos to timed sections */
        $("video").each(function(){
            var url = $(this).attr('src') || $("[src]:first", this).attr('src');
            $(this).timeline({
                show: function (elt) {
                    $(elt).closest('section.section1').find('div.wrapper').autoscrollable("scrollto", elt);
                    $(elt).addClass("active");
                },
                hide: function (elt) {
                    $(elt).removeClass("active");
                },
                start: function (elt) { return $(elt).attr('data-start') },
                end: function (elt) { return $(elt).attr('data-end') }
            }).timeline("add", 'section.section1[about="' + url + '"] *[data-start]', {debug:true});
        });

        // Make timecodes clickable (jump to time in matching videos)
        $('span[property="aa:start"],span[property="aa:end"]').click(function () {
            var t = $.timecode_tosecs_attr($(this).attr("content"));
            var video = $('video source[src="' + $(this).parents('section.section1').attr('about')  + '"]').parent('video')[0];
            video.currentTime = t;
            video.play();
        });

    }

    /* Activate level-1 sections as (editable) playlists */
    $('section.section1').aaplaylist();
    // $("section.section1 > div.wrapper").autoscrollable();
    $("section.section1").autoscrollable();

    resetTimelines();

    $("section textarea").live("focus", function () {
        console.log("textarea focus", this);
        currentTextArea = this;
        // ENSURE TEXTAREA HEIGHT IS OK HACK
        var textareaheight = $this.height();
        var sectionheight = $this.closest(".section1").height();
        console.log("hh", sectionheight, textareaheight);
        if (textareaheight + TEXTAREA_MIN_PADDING_BOTTOM > sectionheight) {
            $this.css("height", (sectionheight - TEXTAREA_MIN_PADDING_BOTTOM)+"px");
        }
    }).live("blur", function () {
        currentTextArea = undefined;
    });

    /////////////////////////
    // SHORTCUTS

    function firstVideo () {
        // returns first playing video (unwrapped) element (if one is playing), or just first video otherwise
        $("video").each(function () {
            if (!this.paused) return this;
        });
        var vids = $("video:first");
        if (vids.length) return vids[0];
    }
    shortcut.add("Ctrl+Shift+Down", function () {
        console.log("pastetimecode");
        if (currentTextArea) {
            var vid = firstVideo();
            if (vid) {
                var ct = vid.currentTime;
                $.insertAtCaret(currentTextArea, $.timecode_fromsecs(ct, true)+" -->", true);
            }
        }
    });
    shortcut.add("Ctrl+Shift+Left", function () {
        // console.log("seek back");
        $("video").each(function () {
            this.currentTime = this.currentTime - 5;
        });
    });
    shortcut.add("Ctrl+Shift+Right", function () {
        // console.log("seek forward");
        $("video").each(function () {
            this.currentTime = this.currentTime + 5;
        });
    });
    shortcut.add("Ctrl+Shift+Up", function () {
        $("video").each(function () {
            var foo = this.paused ? this.play() : this.pause();
        });
    });
    /////////////////////////////////////



});
})(jQuery);
