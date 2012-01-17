/**
 * @requires jquery.datetimecode.js
 * @requires jquery.caret.js
 */

var timelinesByURL = {};


/* Edit {{{ */
function commit_attributes (elt) {
    "use strict";
    /*
     * Updates and posts the annotation attributes
     */
    // TODO: update the regex to match timecodes as well
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
            'position': ''
        });

    // Removes extra whitespaces
    var about = $.trim($elt.attr('about'));
    var style = $.trim($elt.attr('style'));
    var class_ = $.trim($elt.attr('class'));

    // Constructs the markdown source
    var attr_chunk = "{: ";
    if (about) { attr_chunk += "about='" + about + "' "; }
    if (style) { attr_chunk += "style='" + style + "' "; }
    if (class_) { attr_chunk += "class='" + class_ + "' "; }
    attr_chunk += "}" ;
    attr_chunk = (attr_chunk == "{: }") ? "" : attr_chunk;  // Removes empty attribute list junk


    var section = $(elt).attr("data-section");
    if (section == -1) {
        // cancel anonymous section save -- BUG: duplicates sections by requesting section -1 (last)
        return;
    }

    $.get("edit/", {
        section: section
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
            }
            var before = data.substring(0, start);
            var after = data.substring(end, data.length);
            
            $.post("edit/", {
                content: before + attr_chunk + after,
                section: section
            });
        }
    });
}
/* }}} */


/* helpers {{{ */
function secs2date (s, baseDate) {
    var d = baseDate ? baseDate : new Date();
    var hours = Math.floor(s / 3600);
    s -= hours * 3600;   
    var mins = Math.floor(s / 60);
    s -= mins*60;
    var secs = Math.floor(s);
    var millis = (s - secs);
    millis = millis*1000;
    return new Date(d.getFullYear(), d.getMonth(), d.getDate(), hours, mins, secs, millis);
}


function date2secs (date) {
    return date.getSeconds() + (date.getMinutes() * 60);
}
/* }}} */


function resetTimelines() {
    $("body").timeline({
        currentTime: function (elt) {
            return $(elt).data("datetime");
        },
        show: function (elt) {
            try { $("audio,video", elt).get(0).play(); }
            catch (e) {}

            $(elt).addClass("active")
                .closest('article[class!="play"]')
                    .find('section.section1')
                       .find('div.wrapper')
                            .autoscrollable("scrollto", elt);
        },
        hide: function (elt) {
            try { $("audio,video", elt).get(0).pause(); }
            catch (e) {}
            $(elt).removeClass("active");
        },
        start: function (elt) {
            // console.log("body start for", elt);
            return $.datetimecode_parse($(elt).attr("data-start"));
        },
        end: function (elt) {
            // console.log("body end for", elt);
            // start is defaultDate for end
            var start = $.datetimecode_parse($(elt).attr("data-start"));
            var end = $(elt).attr("data-end");
            if (end) { return $.datetimecode_parse(end, start); }
        },
        setCurrentTime: function (elt, t) {
            // console.log("body.timeline.setCurrentTime", t);
            // shoot a setCurrentTime "event" to any contained player
            // $(".aaplayer", elt).aaplayer("setCurrentTime", (t/1000));
            try { $("audio,video", elt).get(0).currentTime = (t/1000); }
            catch (e) {}

        }
    });

    /* Find/Init/Return a timeline-enabled media element for a given (about) url */
    function timelineForURL(url) {
        if (timelinesByURL[url] === undefined) {
            var driver = $("video[src='" + url + "'], audio[src='" + url + "']").first();
            if (driver) {
                driver = driver.get(0);
                timelinesByURL[url] = driver;
                // console.log("timelinesByURL", url, driver);
                $(driver).timeline({
                    show: function (elt) {
                        // console.log("timelinesByURL, show", elt);
                        $(elt).addClass("active")
                            .closest('section.section1')
                               .find('div.wrapper:first')
                                    .autoscrollable("scrollto", elt);
                    },
                    hide: function (elt) {
                        // console.log("hide", elt);
//                        $(elt).hide();
                        $(elt).removeClass("active");
                    }
                });
            } else {
                //console.log("WARNING, no media found for about=", url);
            }
        }
        return timelinesByURL[url];        
    }

    // Activate temporal html!
    $("*[data-start]").each(function () {
        var about_url = $.trim($(this).closest("*[about]").attr("about"));
        // use the body as timeline if no about is given
        var timeline = about_url ? timelineForURL(about_url) : $("body").get(0);
        if (timeline) {
            $(timeline).timeline("add", this);
        }
    });

    // Hides the slider if there is no titles attached to the body
    if (typeof($('body').timeline('maxTime')) == "undefined") {
        $('nav#timeline').hide();
        $('#time').hide();
        $('#playpause').hide();
    } else {
        $('nav#timeline').show();
        $('#time').show();
        $('#playpause').show();
    }


    /*    debuggin
    var start = $("body").timeline("minTime");
    var end = $("body").timeline("maxTime");
    console.log("body start:", start, ", end: ", end);
    */
}

(function($) {

var currentTextArea; /* used for timecode pasting */

/* REFRESH {{{ */
// The refresh event gets fired on body initially
// then on any <section> or other dynamically loaded/created element to "activate" it
$(document).bind("refresh", function (evt) {
    var context = evt.target;

    /* Draggable + resizable Sections {{{ */
    $("section.section1").bind('mousedown', function(e) {
        e.stopPropagation(); 
    }).draggable({
        //helper: 'clone',
        containment: 'parent',
        cancel: 'span.edit',
        scroll: true,
        appendTo: '#wrapper',
        handle: 'h1',
        delay: 200,  // NOTE: Prevents unwanted saves 
        stop: function () { 
            // Makes sur the annotation doesn't get a negative offset
            var position = $(this).position();
            if (position.top < 0) {
                $(this).css('top', 0);
            }
            if (position.left < 0) {
                $(this).css('left', 0);
            }
            $(this).trigger('geometrychange');
        }
    }).resizable({
        stop: function () { 
            $(this).trigger('geometrychange');
         }
    });
    /* }}} */

    /* Renumber all sections {{{ */
    $("section:not([data-section='-1'])").each(function (i) {
        $(this).attr("data-section", (i + 1));
    });
    /* }}} */

    // Section edit {{{ */
    // Create & insert edit links in every section's Header that trigger the section's "edit" event
    $(context).ffind('section').each(function () {
        $("<span>✎</span>").addClass("edit").attr('title', 'Edit this annotation in place').click(function () {
            $(this).closest("section").trigger("edit");
        }).prependTo($(":header:first", this));
        
        var about = $(this).closest("section.section1").attr('about');
        $("<span>@</span>").addClass("about").hover(function () {
            $('.player[src="' + about + '"], section[about="' + about + '"]').addClass('highlight');
        }, function() {
            $('.player[src="' + about + '"], section[about="' + about + '"]').removeClass('highlight');
        }).prependTo($("h1", this).first());
        
        $(this).find("h1, h2").bind('dblclick', function(event) {
            event.stopImmediatePropagation();
            var section = $(this).closest("section");
            if (! section.hasClass('editing')) {
                section.toggleClass('collapsed');
                section.trigger("geometrychange");
            }
        });
        var nonhead = $(this).children(":not(:header)");
        var wrapped = $('<div class="wrapper"></div>').append(nonhead);
        $(this).append(wrapped);
    }).bind("geometrychange", function (event) {
        event.stopPropagation();
        if (! $('body').hasClass('anonymous')) {
            // Prevents anonymous users from recording the changes
            commit_attributes(this);
        }
    }).bind("edit", function (evt) {
        function edit (data) {
            var position = $(that).css("position");
            var section_height = Math.min($(window).height() - 28, $(that).height());
            var use_height = (position == "absolute") ? section_height : section_height;
            var f = $("<div></div>").addClass("section_edit").appendTo(that);
            var textarea = $("<textarea></textarea>").css({height: use_height + "px"}).text(data).appendTo(f);
            $(that).addClass("editing");
            var ok = $("<span>✔</span>").addClass("save").attr('title', 'Save').click(function () {
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
            $("<span>✘</span>").addClass("cancel").attr('title', 'Cancel').click(function () {
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
        if ($(this).data('section') == "-1") {
            // Directly enter edit mode
            new_section = true;
            edit("# New");
        } else {
            // Initiate the edit by GETting the markdown source
            $.ajax("edit/", {
                data: {
                    section: $(this).attr("data-section")
                },
                success: edit
            });
        }
    });
    /* }}} */

    /* Connect players to timed sections */
    resetTimelines();

    /* Clickable timecodes {{{ */
    $(context).ffind('span[property="aa:start"],span[property="aa:end"]').bind("click", function () {
        var about = $(this).parents('*[about]').attr('about');
        var timeline;
        if (about) {
            timeline = timelinesByURL[about];
        } else {
            timeline = $("body").get(0);
        }
        if (timeline) {
            var t = $.datetimecode_parse($(this).attr("content"));
            $(timeline).timeline("currentTime", t);
        }
        var t = $.timecode_tosecs_attr($(this).attr("content"));
        var player = $('[src="' + about + '"]')[0] 
                  || $('source[src="' + about + '"]').parent('.player')[0];
        if (player) {
            player.currentTime = t;
            player.play();
        }
    });
    /* }}} */

    /* Swatches {{{ */
    /* Fixes the the clone select value being reset */
    $(context).ffind("span.swatch").each(function () {
        $(this).draggable({helper: function () {
            var $this = $(this);
            var $clone = $this.clone();
            $clone.find('select').first().val($this.find('select').first().val());
            return $clone.appendTo("body");
        }});
    });

    $(context).ffind("section.section1, section.section2").droppable({
        greedy: true,
        accept: ".swatch",
        hoverClass: "drophover",
        drop: function (event, ui) {
            var $select = $(ui.helper).find('select');
            var key = $select.attr("name");
            var value = $select.find('option:selected').val();
            var section = $(this).closest(".section1, .section2");
            section.css(key, value);
            section.trigger('geometrychange');
        }
    });
    /* }}} */


    // Timeupdate Propagation
    $(context).ffind("audio,video").bind("timeupdate", function (e) {
        var ct = $(this).get(0).currentTime;
        var containingtimedsection = $(this).closest("*[data-start]");
        // console.log("timeupdate", containingtimedsection, ct);
        if (containingtimedsection) {
            $(containingtimedsection).data("currentTime", ct);
            $(containingtimedsection).trigger("timeupdate");
        }
        // need to get the containing (parent) timeline of this section
        // or simply ASSERT the "currentTime" of this section in a way that it's parent timeline reponds to
        // (and which does NOT cycle the child time back)
        // parent.setTimeFromChild(elt, t) --> or via a timeupdate event 
    });

    /* Landmarks {{{ */
    function placeLandmarks () {
        var slider_elt = $('#timelineslider');
        var slider_elt_width = slider_elt.width() - 26;
        var left = slider_elt.position().left;
        var right = left + slider_elt.width();
        var duration = $("body").timeline('maxTime');
        if (typeof(duration) == "object") {
            duration = date2secs(duration);
        }
        $('section.section2').each(function() {
            var start = $(this).data('start');
            if (typeof(start) == "undefined") {
                return;
            }
            var end = $(this).data('end');
            if (typeof(end) == "undefined") {
                return;
            }
            var offset = $.timecode_tosecs(start) / duration;
            var width = ($.timecode_tosecs(end) - $.timecode_tosecs(start)) / duration;
            $('<a>').attr('href', '#' + $(this).attr('id')).addClass('landmark').css({
                'position': 'absolute',
                'left': (100 * offset) + "%",
                'width': (100 * width) + "%",
                'top': 75
            }).data('position', start)
                .attr('title', start + " --> " + end)
                //.bind('click', function() {
                    //$("body").timeline('currentTime', elt_duration + 0.01);
                //})
                .appendTo('#timeline');
        });
        
        $('a[rel="aa:landmark"]').each(function() {
            var data_start = $(this).closest('section').data('start');
            var elt_duration = $.timecode_tosecs(data_start);
            var elt_pos = elt_duration / duration;
            $('<a href="#"><img src="/static/aacore/img/landmark.png" /></a>').css({
                'position': 'absolute',
                'left': (100 * elt_pos) + "%"
            }).data('position', data_start)
                .attr('title', $(this).text())
                //.bind('click', function() {
                    //$("body").timeline('currentTime', elt_duration + 0.01);
                //})
                .appendTo('#timeline');
        });

        
    }
    if ($('#timelineslider').is(':visible')) {
        placeLandmarks();
    }
    /* }}} */

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
            if (! this.paused) { return this; }
        });
        var vids = $(".player").first();
        if (vids.length) { return vids[0]; }
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
            this.currentTime -= 5;
        });
    });
    shortcut.add("Ctrl+Shift+Right", function () {
        $(".player").each(function () {
            this.currentTime += 5;
        });
    });
    shortcut.add("Ctrl+Shift+Up", function () {
        $(".player").each(function () {
            if (this.paused) { 
                this.play(); 
            } else { 
                this.pause(); 
            }
        });
    });

/* Layers {{{ */
$('div#tab-layers').aalayers({
    selector: 'section.section1',
    post_reorder: function(event, ui, settings) {
        var $this = settings.$container;
        $this.find('li')
            .reverse()
            .each(function(i) {
                $($(this).find('label a').attr('href'))
                    .css('z-index', i)
                    .trigger('geometrychange');
            });
    },
    post_toggle: function(event, settings, target) {
        target.toggle().trigger('geometrychange');
    }
});
/* }}} */

/* Layout {{{ */
$("nav#sidebar div#tab-this").tabs();
$('body').layout({
    applyDefaultStyles: false,
    enableCursorHotkey: false,
    west: {
        size: "350",
        fxName: "slide",
        fxSpeed: "fast",
        initClosed: true,
        enableCursorHotkey: false,
        slidable: false,
        resizable: false,
        togglerAlign_closed : 'center',
        togglerAlign_open : 'center',
        togglerContent_open: '-',
        togglerContent_closed: '+',
        spacing_closed: 16,
        spacing_open: 16,
        togglerLength_open: -1,
        togglerLength_closed: -1,
        showOverflowOnHover: false
    }
});
$('#center').layout({
    applyDefaultStyles: false,
    enableCursorHotkey: false,
    //slidable: false,
    //resizable: false,
    //closable: false,
});

var myScroll = new iScroll('canvas', { zoom: true, wheelAction: 'zoom', zoomMin: 0.25, zoomMax: 1, hideScrollbar: true });
/* }}} */

$("#add").click(function() {
    $('<section><h1>New section</h1></section>')
        .addClass('section1')
        .css('top', 30)
        .css('left', 30)
        .data('section', '-1')
        .prependTo('article')
        .trigger('refresh')
        .trigger('edit');
});

$("#save").click(function() {
    var message = window.prompt("Summary", "A nice configuration");
    if (message) {
        $.get("flag/", {
            message: "[LAYOUT] " + message
        });
    }
    return false;
});


$("#mode").buttonset();
$("#playpause, #time").button();

$("#modeedit, #modeplay").change(function() {
    var mode = $(this).val();
    if (mode == "play") {
        $("article").addClass("play");
    } else {
        $("article").removeClass("play");
    }
});

/* Navigation {{{ */
$("#zoomin").click(function() {
    var value = $('#zoomslider').slider('value');
    $('#zoomslider').slider('value', value + 0.1);
    //myScroll.zoom(0, 0, value + 0.1, 300);
});
$("#zoomout").click(function() {
    var value = $('#zoomslider').slider('value');
    $('#zoomslider').slider('value', value - 0.1);
    //myScroll.zoom(0, 0, 0.25, 300);
});
$('#zoomslider').slider({
    orientation: 'vertical',
    max: 1,
    min: 0.25,
    step: 0.01,
    value: 1,
    change: function(event) {
        var value = $(this).slider("option", "value");
        //var centerx = $('#canvas').width() / 2;
        //var centery = $('#canvas').height() / 2;
        myScroll.zoom(0, 0, value, 300);
        //myScroll.zoom(centerx, centery, value, 300);
    }
});

function createMap() {
    var mapWidth = 200;
    var mapHeight = 200;
    var $elts = $('section.section1'); 
    var maxLeft = 0;
    var maxTop = 0;

    $elts.each(function() {
        var $this = $(this);
        var position = $this.position();
        var width = $this.width();
        var height = $this.height();
        var offsetLeft = position.left + width;
        var offsetTop = position.top + height;
        maxLeft = (offsetLeft > maxLeft) ? offsetLeft : maxLeft;
        maxTop = (offsetTop > maxTop) ? offsetTop : maxTop;
    });

    $elts.each(function() {
        var $this = $(this);
        var position = $this.position();
        var width = $this.width();
        var height = $this.height();
        var offsetLeft = position.left + width;
        var offsetTop = position.top + height;
        var h1 = $(this).find('h1').first().clone()
        h1.find('span').remove();
        $('<div>').css({
            border: '1px solid black',
            overflow: 'hidden',
            //backgroundColor: 'red',
            position: 'absolute',
            fontSize: 7,
            color: 'gray',
            width: width / (maxLeft / 200),
            height: height / (maxLeft / 200),
            left: offsetLeft / (maxLeft / 200),
            top: offsetTop / (maxLeft / 200),
        }).text(h1.text()).appendTo($('#map'));
    });
}

//createMap();

/* }}} */

/* Timeline {{{ */
$("body").bind("timeupdate", function () {
    var currentTime, minTime, maxTime, nextTime, $body;

    $body = $('body');
    currentTime = $body.data("currentTime");
    minTime = $body.timeline("minTime");
    maxTime = $body.timeline("maxTime");
    nextTime =  (currentTime / (maxTime - minTime)) * 100000;

    $('#timeslider').slider("option", "value", nextTime);
});

$('#timelineslider').slider({
    max: 100000,
    slide: function(event) {
        var value, currentTime, minTime, maxTime, nextTime, $body;

        value = $(this).slider("option", "value");

        $body = $('body');
        currentTime = $body.data("currentTime");
        minTime = $body.timeline("minTime");
        maxTime = $body.timeline("maxTime");

        nextTime = minTime.getTime() + ((maxTime - minTime) * (value/100000));

        if (! currentTime) {
            currentTime = new Date();
            $body.data("currentTime", currentTime);
        }
        currentTime.setTime(nextTime);

        $body.timeline("currentTime", currentTime);
    }
});

/* }}} */
    
    /* Smooth scrolling to and uncollapsing of anchors {{{ */
    $('a[href^="#"]').live('click', function() {
    //$('div#center a[href^="#"]').live('click', function() {
    //$('div#center').delegate('a[href^="#"]', 'click', function() {
        
        var $target = $($(this).attr('href'));
        var offset = $target.offset();
        //var container_offset = $('div#center').offset();
        
        $('div#canvas').animate({
            scrollTop: offset.top,
            scrollLeft: offset.left
        }, 1000);

        $target.removeClass('collapsed');
        $target.trigger("geometrychange");
        return false;
    });
    /* }}} */


});
/* }}} */
})(jQuery);

/* vim: set foldmethod=marker: */
