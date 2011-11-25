function post_styles (elt, attr) {
    /*
     * Updates and posts the annotation style
     */
    // RegExp
    var HASH_HEADER_RE = /(^|\n)(#{1,2}[^#].*?)#*(\n|$)/;
    var STYLE_ATTR_RE = /{:[^}]*}/;
    var start;
    var end;
    var content = "";

    var clone = $(elt).clone();
    clone.removeClass('section1 section2 ui-droppable ui-draggable ui-resizable ui-draggable-dragging editing highlight drophover');
    clone.css({
        'display': $(elt).is(":visible") ? "" : "none",  // we only want to know if it is hidden or not
        'position': '',
    });

    var $elt = clone;
    var about = $.trim($elt.attr('about'));
    var id = $.trim($elt.attr('id'));
    var style = $.trim($elt.attr('style'));
    var class_ = $.trim($elt.attr('class'));

    var attr_list = "{: ";
    if (about) attr_list += "about='" + about + "' ";
    if (style) attr_list += "style='" + style + "' ";
    if (class_) attr_list += "class='" + class_ + "' ";
    attr_list += "}" ;

    var style = attr_list;

    var section = $(elt).attr("data-section");
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
                section: section,
                type: 'ajax', 
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

var TEXTAREA_MIN_PADDING_BOTTOM = 40;
var currentTextArea = undefined; /* used for timecode pasting */

function ffind (selector, context) {
    // "filter find", like $.find but it also checks the context element itself
    return $(context).filter(selector).add(selector, context);
}

// The refresh event gets fired on body initially
// then on any <section> or other dynamically loaded/created element to "activate" it
$(document).bind("refresh", function (evt) {
    //console.log("refreshing", evt.target);
    var context = evt.target;

    // Draggable Sections
    $("section.section1").draggable({
        handle: 'h1',
        //delay: 100,  // avoids unintentional dragging when (un)collpasing
        //cursorAt: { left: 0, top: 0, },
        snap: ".grid",
        snapTolerance: 5,
        stop: function () { 
            var position = $(this).position();
            if (position.top < 0) {
                $(this).css('top', '0px');
            };
            if (position.left < 0) {
                $(this).css('left', '0px');
            };
            post_styles(this, 'style'); 
        },
        //drag: function (e) {
            //if (e.ctrlKey == true) {
                //$(this).draggable('option', 'grid', [20, 20]);
            //} else {
                //$(this).draggable('option', 'grid', false);
            //}
        //}
    }).resizable({
        stop: function () { post_styles(this, 'style') },
        snap: ".grid",
    });

    // RENUMBER ALL SECTIONS
    $("section:not([data-section='-1'])").each(function (i) {
        $(this).attr("data-section", (i+1));
    });

    // SECTION EDIT LINKS
    // Create & insert edit links in every section's Header that trigger the section's "edit" event
    ffind('section', context).each(function () {
        $("<span>✎</span>").addClass("section_edit_link").click(function () {
            $(this).closest("section").trigger("edit");
        }).prependTo($(":header:first", this));
        
        var about = $(this).closest("section.section1").attr('about');
        $("<span>@</span>").addClass("about").hover(function () {
            $('.player[src="' + about + '"], section[about="' + about + '"]').addClass('highlight');
        }, function() {
            $('.player[src="' + about + '"], section[about="' + about + '"]').removeClass('highlight');
        }).prependTo($("h1:first", this));
        
        $(this).children("h1").bind('dblclick', function(e) {
            var section = $(this).closest("section");
            if (!section.hasClass('editing')) {
                section.trigger("collapse");
            };
        });
        var nonhead = $(this).children(":not(:header)");
        var wrapped = $("<div class=\"wrapper\"></div>").append(nonhead);
        $(this).append(wrapped);
    })

    // IN-PLACE EDITING
    ffind('section', context).bind("collapse", function (evt) {
        $(this).toggleClass('collapsed');
        post_styles(this, 'class');
    })

    ffind('section', context).bind("edit", function (evt) {

        function edit (data) {
            var position = $(that).css("position");
            var section_height = Math.min($(window).height() - 28, $(that).height());
            var use_height = (position == "absolute") ? section_height : section_height;
            var f = $("<div></div>").addClass("section_edit").appendTo(that);
            var textarea = $("<textarea></textarea>").css({height: use_height+"px"}).text(data).appendTo(f);
            $(that).addClass("editing");
            var ok = $("<span>✔</span>").addClass("section_save_link").click(function () {
                // console.log("commencing section edit save...");
                $.ajax("edit/", {
                    type: 'post',
                    data: {
                        section: $(that).attr("data-section"),
                        type: 'ajax',
                        content: textarea.val()
                    },
                    success: function (data) {
                        // console.log("resetting contents of section to: ", data);
                        var new_content = $(data);
                        $(that).replaceWith(new_content);
                        new_content.trigger("refresh");
                    }
                });
            }).appendTo($(that).find(':header:first'));
            $("<span>✘</span>").addClass("section_cancel_link").click(function () {
                // console.log("cancelling section edit save...");
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
            }).appendTo($(that).find(':header:first'));
        }

        evt.stopPropagation();
        var that = this;
        var new_section = false;
        if ($(this).attr('data-section') == "-1") {
            new_section = true;
            edit("# New section");
        } else {
            $.ajax("edit/", {
                data: {
                    section: $(this).attr("data-section"),
                    type: 'ajax'
                },
                success: edit,
            });
        }
    });
    // end of IN-PLACE EDITING

    /* Connect players to timed sections */
    resetTimelines();

    /// CLICKABLE TIMECODES
    $('span[property="aa:start"],span[property="aa:end"]', context).bind("click", function () {
        var t = $.timecode_tosecs_attr($(this).attr("content"));
        var about = $(this).parents('*[about]').attr('about');
        var player = $('[src="' + about + '"]')[0] 
                    || $('source[src="' + about + '"]').parent('.player')[0];
        if (player) {
            player.currentTime = t;
            player.play();
        }
    });

    $("span.swatch", context).each(function () {
        $(this).draggable({helper: function () {
            var $this = $(this);
            var $clone = $(this).clone();
            $clone.find('select:first').val($this.find('select:first').val());
            return $clone.appendTo("body");
        }});
    });
    ffind("section.section2", context).droppable({
        accept: ".swatch",
        hoverClass: "drophover",
        drop: function (evt, ui) {
            var $select = $(ui.helper).find('select');
            var key = $select.attr("name");
            var value = $select.find('option:selected').val();
            var s1 = $(this).closest(".section2");
            s1.css(key, value);
            post_styles(s1, 'style');
        }
    });
    ffind("section.section1", context).droppable({
        accept: ".swatch",
        hoverClass: "drophover",
        drop: function (evt, ui) {
            var $select = $(ui.helper).find('select');
            var key = $select.attr("name");
            var value = $select.find('option:selected').val();
            var s1 = $(this).closest(".section1");
            s1.css(key, value);
            post_styles(s1, 'style');
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
    //$("section.section1").autoscrollable();

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
                    post_styles($(target), 'style');
                });
        },
        post_toggle: function(event, settings, target) {
            target.toggle();
            post_styles(target, 'style');
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
        var elt = $('<section><h1>New</h1></section>').addClass('section1').attr('data-section', '-1');
        $('article').append(elt);
        elt.trigger('refresh').trigger('edit');
    });

    $("a[title='commit']:first").click(function() {
        var message = window.prompt("Summary", "A nice configuration");
        if (message) {
            $.get("flag/", {
                message: "[LAYOUT] " + message,
            });
        };
    });

});
})(jQuery);


//$(document).ready(function() {
//var gutter = 20;
//var width = 200;
//var height= 200;
//var margin = 20;

//console.log($(window).width());

//$('<div></div>').addClass('foo grid').css({
    //position: 'absolute',
    //top: margin,
    //left: margin,
    //bottom: margin,
    //right: margin,
    ////backgroundColor: 'blue',
//}).appendTo($('body'));


//var max_column = Math.floor($('.foo').width() / (width + gutter));
//var max_row = Math.floor($('.foo').height() / (height + gutter));
//console.log(max_column);
//for (var i = 0; i < (max_column * max_row); i++) {
    //var column = $('<div></div>').addClass('column grid').css({
        //width: width,
        //float: 'left',
        //marginRight: gutter,
        //height: "100%",
        //border: "1px dotted red",
        //height: height,
        //marginBottom: gutter,
    //}).appendTo('.foo');
//};
//});
