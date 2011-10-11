(function($) {

var TEXTAREA_MIN_PADDING_BOTTOM = 40;
var currentTextArea = undefined; /* used for timecode pasting */

$(document).ready(function() {
    // in a sense resetting timelines should happen whenever the page has changed (throttled?)

    function resetTimelines () {
        /* Connect players to timed sections */
        $(".player").each(function(){
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
        var about = $(this).parents('*[about]').attr('about');
        var player = $('[src="' + about + '"]')[0] 
                    || $('source[src="' + about + '"]').parent('.player')[0];
        if (player) {
            player.currentTime = t;
            player.play();
        }
    });

    $("section").draggable({
        'helper' : 'clone',
        start: function () {
            // $(this).css({background: "black", color: "white"});
        },
        'containment': 'window'
    });

    var post_styles = function(event, ui) {
        /*
         * Updates and posts the annotation style
         */
        // RegExp
        var HASH_HEADER_RE = /(^|\n)(#[^#].*?)#*(\n|$)/;
        var STYLE_ATTR_RE = /{@style=.*?}/; 
        var start;
        var end;
        var content = "";

        var style = "{@style=" + $.trim($(this).attr('style')) + "}";

        var section = $(this).attr("data-section");
        $.get("edit/", {
            section: section,
            type: 'ajax', 
        }, function(data) {
            // Searches for Header
            var header_match = HASH_HEADER_RE.exec(data);
            if (header_match) {
                // Defines the substring to replace
                var style_match = STYLE_ATTR_RE.exec(header_match[0]);
                if (style_match) {
                    start = header_match.index + style_match.index;
                    end = start + style_match[0].length;
                } else {
                    start = header_match.slice(1,3).join('').length;
                    end = start;
                };
                var before = data.substring(0, start);
                var after = data.substring(end, data.length)
                content = before + style + after;
                
                $.post("edit/", {
                    content: content,
                    message: "[LAYOUT] Changed",
                    section: section,
                    type: 'ajax', 
                });
            }
        });
    }

    /* Activate level-1 sections as (editable) playlists */
    $('section.section1').aaplaylist({
        post_draggable: post_styles,
        post_resizable: post_styles,
    });
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

    function firstPlayer () {
        /*
         * returns first playing player (unwrapped) element (if one is playing),
         * or just first player otherwise
         */
        $(".player").each(function () {
            if (!this.paused) return this;
        });
        var vids = $(".player:first");
        if (vids.length) return vids[0];
    }

    shortcut.add("Ctrl+Shift+Down", function () {
        if (currentTextArea) {
            var player = firstPlayer();
            if (player) {
                var ct = $.timecode_fromsecs(player.currentTime, true);
                $.insertAtCaret(currentTextArea, ct + " -->", true);
            }
        }
    });

    shortcut.add("Ctrl+Shift+Left", function () {
        $(".player").each(function () {
            this.currentTime = this.currentTime - 5;
        });
    });

    shortcut.add("Ctrl+Shift+Right", function () {
        $(".player").each(function () {
            this.currentTime = this.currentTime + 5;
        });
    });
    shortcut.add("Ctrl+Shift+Up", function () {
        $(".player").each(function () {
            var foo = this.paused ? this.play() : this.pause();
        });
    });
    /* }}} End shortcuts */

    $('div#tabs-2').aalayers({
        selector: 'section.section1',
        post_reorder: function(event, ui, settings) {
            var $this = settings.$container;
            $this.find('li')
                .reverse()
                .each(function(i) {
                    var target = $(this).find('a').attr('href');
                    $(target).css('z-index', i);
                    post_styles.apply($(target), [event, ui]);
                });
        },
        post_toggle: function(event, settings, target) {
            target.toggle();
            post_styles.apply(target, [event]);
        },
    });

	// Animate scrolls
    $("a").click(function(event){
		//prevent the default action for the click event
        if ($(this).attr('href').match('^#')) {
            event.preventDefault();
            //get the full url - like mysitecom/index.htm#home
            var full_url = this.href;

            //split the url by # and get the anchor target name - home in mysitecom/index.htm#home
            var parts = full_url.split("#");
            var target = $('#' + parts[1]);
            target.closest('section.section1')
                .find('div.wrapper:first')
                    .autoscrollable("scrollto", target);
        };
	});
$('.foldable').hide();
 
$('.foldable_toggle').each(function() {
	$(this).append('<span class="toggle">&nbsp;</span>');
	$(this).wrapInner('<a href="#"></a>');
});
 
$('.foldable_toggle a').click(function() {
	$(this).parent().next('.foldable').slideToggle('slow');
	$(this).toggleClass('unfolded');
	return false;
});

});
})(jQuery);


