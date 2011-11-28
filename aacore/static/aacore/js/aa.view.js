function commit_attributes (elt) {
    "use strict";
    /*
     * Updates and posts the annotation attributes
     */
    // RegExp
    var HASH_HEADER_RE = /(^|\n)(#{1,2}[^#].*?)#*(\n|$)/;
    var ATTR_RE = /{:[^}]*}/;
    var NON_PERSISTANT_CLASSES = ['section1', 'section2', 'ui-droppable',
            'ui-draggable', 'ui-resizable', 'ui-draggable-dragging', 'editing',
            'highlight', 'drophover'].join(' ');

    // As we don't want all attributes/values to be persistent we need to
    // perform some cleaning first. In order not to alter the original element
    // we create a clone and perform the cleaning on it instead.
    var $elt = $(elt).clone()
        .removeClass(NON_PERSISTANT_CLASSES)
        .css({
            // we only want the record the visibility if the element is hidden...
            'display': $(elt).is(":visible") ? "" : "none",
            'position': '',
        });

    // Removes extra whitespaces
    var about = $.trim($elt.attr('about'));
    var style = $.trim($elt.attr('style'));
    var class_ = $.trim($elt.attr('class'));

    // Constructs the markdown source
    var attr_chunk = "{: ";
    if (about) attr_chunk += "about='" + about + "' ";
    if (style) attr_chunk += "style='" + style + "' ";
    if (class_) attr_chunk += "class='" + class_ + "' ";
    attr_chunk += "}" ;
    attr_chunk = (attr_chunk == "{: }") ? "" : attr_chunk;  // Removes empty attribute list junk


    var section = $(elt).attr("data-section");
    if (section == -1) {
        // cancel anonymous section save -- BUG: duplicates sections by requesting section -1 (last)
        return;
    }

    $.get("edit/", {
        section: section,
    }, function(data) {
        // Searches for Header
        var header_match = HASH_HEADER_RE.exec(data);
        if (header_match) {
            var start, end;
            // Defines the substring to replace
            var attr_match = ATTR_RE.exec(header_match[0]);
            if (attr_match) {
                start = header_match.index + attr_match.index;
                end = start + attr_match[0].length;
            } else {
                start = header_match.slice(1,3).join('').length;
                end = start;
            };
            var before = data.substring(0, start);
            var after = data.substring(end, data.length)
            
            $.post("edit/", {
                content: before + attr_chunk + after,
                section: section,
            });
        }
    });
}

function resetTimelines() {
    // RESET (ALL) TIMELINES
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

(function($) {

var currentTextArea = undefined; /* used for timecode pasting */

// The refresh event gets fired on body initially
// then on any <section> or other dynamically loaded/created element to "activate" it
$(document).bind("refresh", function (evt) {
    var context = evt.target;

    // Draggable Sections
    $("section.section1").draggable({
        handle: 'h1',
        stop: function () { 
            var position = $(this).position();
            if (position.top < 0) {
                $(this).css('top', '0px');
            };
            if (position.left < 0) {
                $(this).css('left', '0px');
            };
            commit_attributes(this); 
        },
    }).resizable({
        stop: function () { commit_attributes(this) },
    });

    // RENUMBER ALL SECTIONS
    $("section:not([data-section='-1'])").each(function (i) {
        $(this).attr("data-section", (i+1));
    });

    // SECTION EDIT LINKS
    // Create & insert edit links in every section's Header that trigger the section's "edit" event
    $(context).ffind('section').each(function () {
        $("<span>✎</span>").addClass("section_edit_link").click(function () {
            $(this).closest("section").trigger("edit");
        }).prependTo($(":header:first", this));
        
        var about = $(this).closest("section.section1").attr('about');
        $("<span>@</span>").addClass("about").hover(function () {
            $('.player[src="' + about + '"], section[about="' + about + '"]').addClass('highlight');
        }, function() {
            $('.player[src="' + about + '"], section[about="' + about + '"]').removeClass('highlight');
        }).prependTo($("h1:first", this));
        
        //$(this).children("h1").bind('dblclick', function(e) {
            //var section = $(this).closest("section");
            //if (!section.hasClass('editing')) {
                //section.trigger("collapse");
            //};
        //});
        $(this).find("h1, h2").bind('dblclick', function(e) {
            e.stopImmediatePropagation();
            var section = $(this).closest("section");
            if (!section.hasClass('editing')) {
                section.trigger("collapse");
            };
        });
        var nonhead = $(this).children(":not(:header)");
        var wrapped = $("<div class=\"wrapper\"></div>").append(nonhead);
        $(this).append(wrapped);
    }).bind("collapse", function (evt) {
        evt.stopPropagation();
        $(this).toggleClass('collapsed');
        commit_attributes(this);
    }).bind("edit", function (evt) {
        function edit (data) {
            var position = $(that).css("position");
            var section_height = Math.min($(window).height() - 28, $(that).height());
            var use_height = (position == "absolute") ? section_height : section_height;
            var f = $("<div></div>").addClass("section_edit").appendTo(that);
            var textarea = $("<textarea></textarea>").css({height: use_height+"px"}).text(data).appendTo(f);
            $(that).addClass("editing");
            var ok = $("<span>✔</span>").addClass("section_save_link").click(function () {
                $.ajax("edit/", {
                    type: 'post',
                    data: {
                        section: $(that).attr("data-section"),
                        content: textarea.val()
                    },
                    success: function (data) {
                        var new_content = $(data);
                        $(that).replaceWith(new_content);
                        new_content.trigger("refresh");
                    }
                });
            }).prependTo($(that).find(':header:first'));
            $("<span>✘</span>").addClass("section_cancel_link").click(function () {
                if (new_section) {
                    // removes the annotation
                    $(that).remove(); 
                    $(this).remove(); 
                    ok.remove(); 
                } else {
                    f.remove();
                    $(this).remove(); 
                    ok.remove(); 
                    $(that).removeClass("editing");
                }
            }).prependTo($(that).find(':header:first'));
        }

        evt.stopPropagation();
        var that = this;
        var new_section = false;
        if ($(this).attr('data-section') == "-1") {
            // Directly enter edit mode
            new_section = true;
            edit("# New");
        } else {
            // Initiate the edit by GETting the markdown source
            $.ajax("edit/", {
                data: {
                    section: $(this).attr("data-section"),
                },
                success: edit,
            });
        }
    });
    // end of IN-PLACE EDITING

    /* Connect players to timed sections */
    resetTimelines();

    /// CLICKABLE TIMECODES
    $(context).ffind('span[property="aa:start"],span[property="aa:end"]').bind("click", function () {
        var t = $.timecode_tosecs_attr($(this).attr("content"));
        var about = $(this).parents('*[about]').attr('about');
        var player = $('[src="' + about + '"]')[0] 
                    || $('source[src="' + about + '"]').parent('.player')[0];
        if (player) {
            player.currentTime = t;
            player.play();
        }
    });

    // Fixes the the clone select value being reset
    $(context).ffind("span.swatch").each(function () {
        $(this).draggable({helper: function () {
            var $this = $(this);
            var $clone = $(this).clone();
            $clone.find('select:first').val($this.find('select:first').val());
            return $clone.appendTo("body");
        }});
    });

    $(context).ffind("section.section1, section.section2").droppable({
        greedy: true,
        accept: ".swatch",
        hoverClass: "drophover",
        drop: function (evt, ui) {
            var $select = $(ui.helper).find('select');
            var key = $select.attr("name");
            var value = $select.find('option:selected').val();
            var s1 = $(this).closest(".section1, .section2");
            s1.css(key, value);
            commit_attributes(s1);
        }
    });
});

$(document).ready(function() {

    /* INIT */
    $(document).trigger("refresh");

    /////////////////////
    /////////////////////
    /////////////////////
    // Once-only page inits

    $("section.section1 > div.wrapper").autoscrollable();

    /////////////////////////
    // SHORTCUTS

    // maintain variable currentTextArea
    $("section textarea").live("focus", function () {
        currentTextArea = this;
    }).live("blur", function () {
        currentTextArea = undefined;
    });

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
    /////////////////////////
    // LAYERS
    $('div#tabs-2').aalayers({
        selector: 'section.section1',
        post_reorder: function(event, ui, settings) {
            var $this = settings.$container;
            $this.find('li')
                .reverse()
                .each(function(i) {
                    var target = $(this).find('a').attr('href');
                    $(target).css('z-index', i);
                    commit_attributes($(target));
                });
        },
        post_toggle: function(event, settings, target) {
            target.toggle();
            commit_attributes(target);
        },
    });

    /////////////////////
    // LAYOUT
    // FIXME: is it really necessary to set enableCursorHotKey for each
    // sidebar?
    $("nav#east-pane").tabs();
    $('body').layout({
        applyDefaultStyles: false,
        enableCursorHotkey: false,
        east: {
            size: 360,
            fxSpeed: "slow",
            initClosed: true,
            enableCursorHotkey: false,
        },
        south: {
            fxName: "slide",
            fxSpeed: "slow",
            size: 200,
            initClosed: true,
            enableCursorHotkey: false,
        }           
    });
    
    $("a[title='add']:first").click(function() {
        $('<section><h1>New section</h1></section>')
            .addClass('section1')
            .css('top', 30)
            .css('left', 30)
            .attr('data-section', '-1')
            .prependTo('article')
            .trigger('refresh')
            .trigger('edit');
    });

    $("a[title='commit']:first").click(function() {
        var message = window.prompt("Summary", "A nice configuration");
        if (message) {
            $.get("flag/", {
                message: "[LAYOUT] " + message,
            });
        };
        return false;
    });

    /////////////////////////////
    // TIMELINE
    $('#timelineslider').slider({
        max: 3600,
        start: function(e) {
        },
        slide: function(e) {
        },
        stop: function(e) {
        },
    });


});
})(jQuery);
