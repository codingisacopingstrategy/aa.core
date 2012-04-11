/**
 * This file is part of Active Archives.
 * Copyright 2006-2012 the Active Archives contributors (see AUTHORS)
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Affero General Public License as
 * published by the Free Software Foundation, either version 3 of the
 * License, or (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Affero General Public License for more details.
 *
 * You should have received a copy of the GNU Affero General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 * Also add information on how to contact you by electronic and paper mail.
 *
 *
 * @requires jquery.datetimecode.js
 * @requires jquery.caret.js
 */


(function($) {
    var currentTextArea; /* used for timecode pasting */
    var timelinesByURL = {};
    var $canvas;
    var $sidebar;
    var embedUrl;
    //var actionStack = [];  // Not Implemented


    function commit_attributes (elt) {
        "use strict";
        /*
         * Updates and posts the annotation attributes
         */
        // TODO: update the regex to match timecodes as well
        // RegExp
        // FIXME: find how \s can not match newlines
        var TIMECODE_RE =    /(^|\n)(\d{2}:\d{2}:\d{2}([.,]\d{1,3})?\s*-->\s*(\d{2}:\d{2}:\d{2}([.,]\d{1,3})?)?.*?)(\n|$)/;
        var HASH_HEADER_RE = /(^|\n)(#{1,2}[^#].*?)#*(\n|$)/;
        var ATTR_RE = /{:[^}]*}/;
        var NON_PERSISTANT_CLASSES = ['section1', 'section2', 'ui-droppable',
                'ui-draggable', 'ui-resizable', 'ui-draggable-dragging', 'editing',
                'highlight', 'drophover', 'active'].join(' ');

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


        var section = $(elt).data("section");
        if (section == -1) {
            // cancel anonymous section save -- BUG: duplicates sections by requesting section -1 (last)
            return;
        }

        $.get("edit/", {
            section: section
        }, function(data) {
            // Searches for Header
            //var header_match = HASH_HEADER_RE.exec(data) ? HASH_HEADER_RE.exec(data) : TIMECODE_RE.exec(data);
            var header_match = HASH_HEADER_RE.exec(data);
            if (header_match) {
                var start, end;
                // Defines the substring to replace
                var attr_match = ATTR_RE.exec(header_match[0]);
                if (attr_match) {
                    start = header_match.index + attr_match.index;
                    end = start + attr_match[0].length;
                } else {
                    start = header_match.slice(1, 3).join('').length;
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

    function placeLandmarks () {
        $('#lines').remove();
        var slider_elt = $('#timelineslider');
        var slider_elt_width = slider_elt.width() - 26;
        var left = slider_elt.position().left;
        var right = left + slider_elt.width();
        var duration = $("body").timeline('maxTime');
        var lines = $('<div>').attr('id', 'lines');
        if (typeof(duration) == "object") {
            duration = $.date2secs(duration);
        }
        var j = 0;
        $('section.section1').each(function(i) {
            var section2 = $('section.section2', this);
            if (section2.length) {
                var line = $("<div>").addClass('line');
                section2.each(function() {
                    var $this = $(this);
                    var extraClass = $(this).has('audio').length ? 'audio ' : 'normal'; 
                    //var extraClass = $(this).has('audio').length ? '' : ''; 
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
                    //$('<a>').attr('href', '#' + $(this).attr('id')).addClass('landmark').css({
                    var foo = $('<a>').attr('href', '#').addClass('landmark').css({
                        'left': (100 * offset) + "%",
                        'width': (100 * width) + "%",
                    }).addClass(extraClass).data('position', start)
                        .attr('title', start + " --> " + end)
                        .bind('click', function() {
                            $this.find('span[property="aa:start"]').click();
                        })
                        .appendTo(line);

                    $('a[rel="aa:landmark"]', this).each(function() {
                        //var bar = foo.clone().attr('class', 'landmark2').text('♦').appendTo(line);
                        foo.addClass('foo');
                    });
                });

                line.appendTo(lines);
                j += 1;
            }
            lines.appendTo('#timeline');
        });
    }

    function resetTimelines() {
        /* create timeline */
        $("body").timeline({
            currentTime: function (elt) {
                return $(elt).data("datetime");
            },
            show: function (elt) {
                var modePlay = $canvas.hasClass('play');

                try { $("audio,video", elt).get(0).play(); }
                catch (e) {}


                $(elt).addClass("active")

                if (!modePlay) {
                    $(elt).closest('section.section1')
                       .find('div.wrapper')
                            .autoscrollable("scrollto", elt);
                };
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
                var end = $(elt).data("end");
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
                    $(driver).timeline({
                        show: function (elt) {
                            $(elt).addClass("active")
                                .closest('section.section1')
                                   .find('div.wrapper:first')
                                        .autoscrollable("scrollto", elt);
                        },
                        hide: function (elt) {
                            $(elt).removeClass("active");
                        }
                    });
                } else {
                    //console.log("WARNING, no media found for about=", url);
                }
            }
            return timelinesByURL[url];        
        }

        /* Activate temporal html! */
        $("[data-start]", $canvas).each(function () {
            var about_url = $.trim($(this).closest("[about]").attr("about"));
            // use the body as timeline if no about is given
            var timeline = about_url ? timelineForURL(about_url) : $("body").get(0);
            if (timeline) {
                $(timeline).timeline("add", this);
            }
        });

        /* Hides the slider if there is no titles attached to the body */
        if ($('body').timeline('maxTime') === undefined) {
            $('#timeline, #time, #playpause').hide();
        } else {
            $('#timeline, #time, #playpause').show();
        }
    }

    $(document).ready(function() {
        $canvas = $("#canvas");
        $sidebar = $("#sidebar");
        embedUrl = $("link[rel='aa-embed']").attr("href");

        // The refresh event gets fired on #canvas initially
        // then on any <section> or other dynamically loaded/created element to "activate" it
        $canvas.bind("refresh", function (evt) {
            var context = evt.target;
            //console.log('refresh');

            $("section.section1 > div.wrapper", $canvas).autoscrollable();

            /* Draggable + resizable Sections {{{ */
            $("section.section1", $canvas).bind('mousedown', function(e) {
                e.stopPropagation(); 
            }).draggable({
                cancel: 'span.edit',
                scroll: true,
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
            $('section', $canvas).not('[data-section="-1"]').each(function (i) {
                $(this).attr("data-section", (i + 1));
            });
            /* }}} */

            // Section edit {{{ */
            // Create & insert edit links in every section's Header that trigger the section's "edit" event
            $(context).ffind('section').each(function () {
                var $h1 = $("h1", this);

                $("<span>✎</span>").addClass("edit").attr('title', 'Edit this annotation in place').click(function () {
                    $(this).closest("section").trigger("edit");
                }).prependTo($(":header:first", this));
                
                var about = $(this).closest("section.section1").attr('about');
                $("<span>@</span>").addClass("about").hover(function () {
                    $('.player[src="' + about + '"], section[about="' + about + '"]', $canvas).addClass('highlight');
                }, function() {
                    $('.player[src="' + about + '"], section[about="' + about + '"]', $canvas).removeClass('highlight');
                }).prependTo($h1);
                
                $(this).find("h1, h2").bind('dblclick', function(event) {
                    event.stopImmediatePropagation();
                    var section = $(this).closest("section");
                    if (! section.hasClass('editing')) {
                        section.toggleClass('collapsed');
                        section.trigger("geometrychange");
                    }
                })
                    .filter('h1')
                        .attr('title', 'Drag to move. Double-click to open/close.')
                    .end()
                    .filter('h2')
                        .attr('title', 'Double-click to open/close.');

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
                    var f = $("<div>").addClass("section_edit").appendTo(that);
                    var textarea = $("<textarea>").css({height: use_height + "px"}).text(data).appendTo(f);
                    $(that).addClass("editing");
                    var ok = $("<span>✔</span>").addClass("save").attr('title', 'Save').click(function () {
                        $.ajax("edit/", {
                            type: 'post',
                            data: {
                                section: $(that).data("section"),
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
                if ($(this).data('section') == -1) {
                    // Directly enter edit mode
                    new_section = true;
                    edit("# New");
                } else {
                    // Initiate the edit by GETting the markdown source
                    $.ajax("edit/", {
                        data: {
                            section: $(this).data("section")
                        },
                        success: edit
                    });
                }
            }).droppable({
                greedy: true,
                accept: ".swatch",
                hoverClass: "drophover",
                drop: function (event, ui) {
                    var $select = $(ui.helper).find('select');
                    var key = $select.attr("id");
                    var value = $select.find('option:selected').val();
                    var section = $(this).closest(".section1, .section2");
                    section.css(key, value);
                    section.trigger('geometrychange');
                }
            });
            /* }}} */

            /* Clickable timecodes {{{ */
            $(context).ffind('span[property="aa:start"], span[property="aa:end"]').bind("click", function () {
                var about = $(this).parents('[about]').attr('about');
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

            /* Connect players to timed sections */
            resetTimelines();


            /* Timeupdate Propagation {{{ */
            $(context).ffind("audio,video").bind("timeupdate", function (e) {
                var ct = $(this).get(0).currentTime;
                var containingtimedsection = $(this).closest("[data-start]");
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
            /* }}} */

            if ($('#timelineslider').is(':visible')) {
                placeLandmarks();
            }
            $(context).add('#sidebar').find("[rel='aa:embed']").each(function () {
                var that = this;
                function poll () {
                    $.ajax(embedUrl, {
                        data: {
                            url: $(that).attr("href"),
                            filter: $(that).data("filter")
                        },
                        success: function (data) {
                            if (data.ok) {
                                // NEW: december 16 (Alex)
                                // In addition to content there are three new keys:
                                // - extra_css: loads extra link rel="stylesheet"
                                // - extra_js: load extra script
                                // - script: extra javascript code to execute
                                var toGo = data.extra_css.length + data.extra_js.length;
                                var html = $(data.content);

                                $(that).replaceWith(html);
                                html.trigger("refresh");

                                $.each(data.extra_css, function(index, value) { 
                                    $.getCSS(value, function() {
                                        //console.log('loaded css: ' + value);   
                                        toGo -= 0;
                                        doit();
                                    });
                                });

                                $.each(data.extra_js, function(index, value) { 
                                    $.getScript(value, function() {
                                        //console.log('loaded js: ' + value);   
                                        toGo -= 0;
                                        doit();
                                    });
                                });

                                function doit () {
                                    if (toGo == 0) {
                                        $.globalEval(data.script);
                                    } else {
                                        toGo -= 1;
                                    }
                                }

                                doit();
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
        }).trigger("refresh");

        /* SHORTCUTS */
        // maintain variable currentTextArea
        $("section textarea", $canvas).live("focus", function () {
            currentTextArea = this;
        }).live("blur", function () {
            currentTextArea = undefined;
        });
        shortcut.add("Ctrl+Shift+Down", function () {
            /**
             * returns first playing player (unwrapped) element (if one is playing),
             * or just first player otherwise
             */
            function firstPlayer () {
                $(".player", $canvas).each(function () {
                    if (! this.paused) { return this; }
                });
                var vids = $(".player", $canvas).first();
                if (vids.length) { return vids[0]; }
            }

            if (currentTextArea) {
                var player = firstPlayer();
                if (player) {
                    var ct = $.timecode_fromsecs(player.currentTime, true);
                    $.insertAtCaret(currentTextArea, ct + " -->", true);
                }
                //var d = new Date();
                //var ct = [$.zeropad(d.getHours(), 2), $.zeropad(d.getMinutes(), 2), $.zeropad(d.getSeconds(), 2)].join(':');
                //$.insertAtCaret(currentTextArea, ct + " -->", true);

            }
        });
        shortcut.add("Ctrl+Shift+Left", function () {
            $(".player", $canvas).each(function () {
                this.currentTime -= 5;
            });
        });
        shortcut.add("Ctrl+Shift+Right", function () {
            $(".player", $canvas).each(function () {
                this.currentTime += 5;
            });
        });
        shortcut.add("Ctrl+Shift+Up", function () {
            $(".player", $canvas).each(function () {
                if (this.paused) { 
                    this.play(); 
                } else { 
                    this.pause(); 
                }
            });
        });

        /* Fixes the the clone select value being reset */
        $("#tab-styles span.swatch").each(function () {
            $(this).draggable({
                helper: function () {
                    var $this = $(this);
                    var $clone = $this.clone();
                    $clone.find('select').first().val($this.find('select').first().val());
                    return $clone.appendTo("body");
                }
            });
        });

        $('#tab-layers').aalayers({
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

        $("#help").accordion({
            autoHeight: false,
            collapsible: true
        });

        $("#tab-this").tabs();

        $('body').layout({
            applyDefaultStyles: false,
            enableCursorHotkey: false,
            west: {
                size: "250",
                fxName: "slide",
                fxSpeed: "fast",
                initClosed: false,
                enableCursorHotkey: false,
                slidable: false,
                closable: true,
                resizable: false,
                togglerAlign_closed : 'center',
                togglerAlign_open : 'center',
                togglerContent_open: '&larr;',
                togglerContent_closed: '&rarr;',
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
            slidable: false,
            resizable: false,
            closable: false,
            south: {
                size: "250",
                fxName: "slide",
                fxSpeed: "fast",
                initClosed: true,
                enableCursorHotkey: false,
                slidable: true,
                closable: true,
                resizable: true,
                togglerAlign_closed : 'center',
                togglerAlign_open : 'center',
                togglerContent_open: '&darr;',
                togglerContent_closed: '&uarr;',
                spacing_closed: 0,
                spacing_open: 18,
                togglerLength_open: -1,
                togglerLength_closed: -1,
                showOverflowOnHover: false
            }
        });

        $("#add").click(function() {
            $('<section><h1>New section</h1></section>')
                .addClass('section1')
                .css('top', 30)
                .css('left', 30)
                .attr('data-section', -1)
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
                $("body").layout().close("west");
            } else {
                $("article").removeClass("play");
                $("body").layout().open("west");
            }
        });

        if ($canvas.hasClass('map')) {
            var myScroll = new iScroll('canvas', { 
                zoom: true, 
                //wheelAction: 'zoom', 
                zoomMin: 0.25, 
                zoomMax: 1, 
                hideScrollbar: true 
            });

            $canvas.dblclick(function(event) {
                var x = event.clientX;
                var y = event.clientY;
                var value = $('#zoomslider').slider('value');
                if (event.shiftKey){
                    var newValue = (value - 0.2 <= myScroll.options.zoomMin) 
                                   ? myScroll.options.zoomMin : value - 0.2;
                    myScroll.zoom(x, y, newValue, 300);
                } else {
                    var newValue = (value + 0.2 >= myScroll.options.zoomMax) 
                                   ? myScroll.options.zoomMax : value + 0.2;
                    myScroll.zoom(x, y, newValue, 300);
                };
                $('#zoomslider').slider('value', newValue);
            });

            $("#zoomin").click(function(event) {
                //event.stopImmediatePropagation();
                var value = $('#zoomslider').slider('value');
                var newValue = (value + 0.1 >= myScroll.options.zoomMax) 
                               ? myScroll.options.zoomMax : value + 0.1;
                myScroll.zoom(0, 0, newValue, 300);
                $('#zoomslider').slider('value', newValue);
            });
            $("#zoomout").click(function(event) {
                //event.stopImmediatePropagation();
                var value = $('#zoomslider').slider('value');
                var newValue = (value - 0.1 <= myScroll.options.zoomMin) 
                               ? myScroll.options.zoomMin : value - 0.1;
                myScroll.zoom(0, 0, newValue, 300);
                $('#zoomslider').slider('value', newValue);
            });
            $('#zoomslider').slider({
                orientation: 'vertical',
                max: 1,
                min: 0.25,
                step: 0.01,
                value: 1,
                slide: function(event) {
                    var value = $(this).slider("option", "value");
                    myScroll.zoom(0, 0, value, 300);
                }
            });
        };

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
        
        $('a[href^="#"]').live('click', function() {
            var $target = $($(this).attr('href'));
            var offset = $target.offset();
            //var container_offset = $('div#center').offset();
            
            $canvas.animate({
                scrollTop: offset.top,
                scrollLeft: offset.left
            }, 1000);

            $target.removeClass('collapsed');
            $target.trigger("geometrychange");
            return false;
        });

        $("section.section1 > div.wrapper", $canvas).autoscrollable();  // FIXME: quick fix to make autoscrollable work on load
    });
})(jQuery);

/* vim: set foldmethod=indent: */
