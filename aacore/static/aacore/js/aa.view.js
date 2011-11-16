function post_styles (elt, attr) {
    /*
     * Updates and posts the annotation style
     */
    // RegExp
    var HASH_HEADER_RE = /(^|\n)(#[^#].*?)#*(\n|$)/;
    var STYLE_ATTR_RE = /{:[^}]*}/;
    var start;
    var end;
    var content = "";

    var clone = $(elt).clone();
    clone.removeClass('section1 ui-draggable ui-resizable ui-draggable-dragging editing');
    clone.css({
        'display': '',
        'position': '',
    });

    var $elt = clone;
    var about = $.trim($elt.attr('about'));
    var id = $.trim($elt.attr('id'));
    var style = $.trim($elt.attr('style'));
    var class_ = $.trim($elt.attr('class'));

    var width = $elt.css('width');
    var height = $elt.css('height');
    var left = $elt.css('left');
    var top = $elt.css('top');

    var attr_list = "{: ";
    if (about) attr_list += "about='" + about + "' ";
    if (style) attr_list += "style='" + style + "' ";
    if (class_) attr_list += "class='" + class_ + "' ";
    attr_list += "}" ;


    //var style = " {: " + attr + "='" + $.trim($(elt).attr(attr)) + "' }";
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

//
// The refresh event gets fired on body initially
// then on any <section> or other dynamically loaded/created element to "activate" it
//
$(document).bind("refresh", function (evt) {
    // console.log("refreshing", evt.target);
    var context = evt.target;

    // Draggable Sections
    $("section.section1").draggable({
        handle: 'h1',
        stop: function () { post_styles(this, 'style') }
    }).resizable({
        stop: function () { post_styles(this, 'style') }
    });

    // RENUMBER ALL SECTIONS
    // console.log("renumber sections");
    $("section:not([data-section='-1'])").each(function (i) {
        $(this).attr("data-section", (i+1));
    });

    // SECTION EDIT LINKS
    // Create & insert edit links in every section's Header that trigger the section's "edit" event
    ffind('section', context).each(function () {
        // console.log("adding edit link");

        $("<span>✎</span>").addClass("section_edit_link").click(function () {
            $(this).closest("section").trigger("edit");
        }).prependTo($(":header:first", this));
        
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

    //$(this).find(':header:first').position({
          //my: "top left",
          //at: "top left",
          //of: 'section.section1:first',
    //});
    // IN-PLACE EDITING
    ffind('section', context).bind("collapse", function (evt) {
        $(this).toggleClass('collapsed');
        post_styles(this, 'class');
    })

    ffind('section', context).bind("edit", function (evt) {

        function edit (data) {
            var position = $(that).css("position");
            var section_height = Math.min($(window).height() - 20, $(that).height());
            var use_height = (position == "absolute") ? (section_height - 36) : section_height;
            var f = $("<div></div>").addClass("section_edit").appendTo(that);
            var textarea = $("<textarea></textarea>").css({height: use_height+"px"}).text(data).appendTo(f);
            $(that).addClass("editing");
            $("<button>save</button>").click(function () {
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
            }).appendTo(f);
            $("<button>cancel</button>").click(function () {
                // console.log("cancelling section edit save...");
                if (new_section) {
                    // removes the annotation
                    $(that).remove(); 
                } else {
                    f.remove();
                    $(that).removeClass("editing");
                }
            }).appendTo(f);
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
/*
 *    /////////////////////
 *    // Animate scrolls
 *    $("a").click(function(event){
 *        //prevent the default action for the click event
 *        if ($(this).attr('href').match('^#')) {
 *            event.preventDefault();
 *            //get the full url - like mysitecom/index.htm#home
 *            var full_url = this.href;
 *
 *            //split the url by # and get the anchor target name - home in mysitecom/index.htm#home
 *            var parts = full_url.split("#");
 *            var target = $('#' + parts[1]);
 *            target.closest('section.section1')
 *                .find('div.wrapper:first')
 *                    .autoscrollable("scrollto", target);
 *        };
 *    });
 *    /////////////////////
 *    $('.foldable').hide();
 *    $('.foldable_toggle').each(function() {
 *        $(this).append('<span class="toggle">&nbsp;</span>');
 *        $(this).wrapInner('<a href="#"></a>');
 *    });
 *    $('.foldable_toggle a').click(function() {
 *        $(this).parent().next('.foldable').slideToggle('slow');
 *        $(this).toggleClass('unfolded');
 *        return false;
 *    });
 */
    /////////////////////
    // LAYOUT
    $("nav#east-pane").tabs();
    $('body').layout({
        applyDefaultStyles: false,
        enableCursorHotkey: false,
        east: {
            size: 360,
            fxSpeed: "slow",
            initClosed: true,
        },
        south: {
            fxName: "slide",
            fxSpeed: "slow",
            size: 200,
            initClosed: true,
        }           
    });
    // $("nav#south-pane").tabs();
    //
    
    $("a[title='add']:first").click(function() {
        var elt = $('<section><h1>New</h1></section>').addClass('section1').attr('data-section', '-1');
        $('article').append(elt);
        elt.trigger('refresh').trigger('edit');
    });

    $("a[title='commit']:first").click(function() {
        var message = "[LAYOUT] " + window.prompt("Summary", "A nice configuration");
        $.get("flag/", {
            message: message,
        });
    });

});
})(jQuery);


