(function ($) {

/**
 * @fileoverview 
 * @author Michael Murtaugh <mm@automatist.org> and the Active Archive contributors
 * @license GNU AGPL
 * @requires jquery.datetimecode.js

Timeline organizes (HTML) elements by time.
Elements are attached to a timeline with a start time and (optionally) an end time.
A Timeline has a notion of a currentTime, and manages hiding / showing (via a callback) elements accordingly.
Timelines follow the element's "timeupdate" events.
A Timeline may also be passive and require an external element to "drive" it via calls to setCurrentTime.
*/

var aTimeline = function (options) {
    /*
     * aTimeline
     * private closure-class used by the plugin
     */
    var that = {},
        cc_item_uid = 0,
        minTime, 
        maxTime,
        currentTime = 0.0,
        titlesByStart = [],
        titlesByEnd = [],
        lastTime,
        startIndex = -1,
        endIndex = -1,
        toShow = {},
        toHide = {},
        activeItems = {},
        settings = {};

    $.extend(settings, options);

    // element wrapper
    function timeline_item (elt, start, end, show, hide) {
        var that = {};

        cc_item_uid += 1;
        that.id = "T" + cc_item_uid;
        that.start = start;
        that.end = end;
        that.elt = elt;

        if (show) { that.show = show; }
        if (hide) { that.hide = hide; }

        return that;
    };

    function addTitle (newtitle) {
        var placed = false;

        // addTitleByStart
        /* maintain min/maxTime */
        /* FIXME: timecodes using a period rather than a comma lead cannot be parsed */
        if ((minTime === undefined) || (newtitle.start < minTime)) { minTime = newtitle.start; }
        if ((maxTime === undefined) || (newtitle.start > maxTime)) { maxTime = newtitle.start; }
        if ((maxTime === undefined) || (newtitle.end && (newtitle.end > maxTime))) { maxTime = newtitle.end; }
        //console.log(newtitle.elt);
        //console.log(minTime, maxTime);

        /* insert annotation in the correct (sorted) location */
        for (var i=0; i<titlesByStart.length; i++) {
            if (titlesByStart[i].start > newtitle.start) {
                // insert before this index
                titlesByStart.splice(i, 0, newtitle);
                placed = true;
                break;
            }
        }

        // otherwise simply append
        if (! placed) { titlesByStart.push(newtitle); }

        // addTitleByEnd
        /* insert annotation in the correct (sorted) location */
        placed = false;
        for (i=0; i<titlesByEnd.length; i++) {
            if ((titlesByEnd[i].end > newtitle.end) || ((titlesByEnd[i].end === undefined) && (newtitle.end !== undefined))) {
                // insert before this index
                titlesByEnd.splice(i, 0, newtitle);
                placed = true;
                return;
            }
        }

        // otherwise simply append
        if (!placed) { titlesByEnd.push(newtitle); }
    }
    
    function markToShow (t) {
        if (toHide[t.id]) {
            delete toHide[t.id];
        } else {
            toShow[t.id] = t;
        }
    }

    function markToHide (t) {
        if (toShow[t.id]) {
            delete toShow[t.id];
        } else {
            toHide[t.id] = t;
        }
    }
    
    function show (item) {
        if (item.show) {
            item.show(item.elt);
        } else if (settings.show) {
            settings.show(item.elt);
        }
    }

    function hide (item) {
        if (item.hide) {
            item.hide(item.elt);
        } else if (settings.hide) {
            settings.hide(item.elt);
        }
    }

    function updateForTime (time, controller) {
        if (titlesByStart.length === 0) { return; }
        var n;
        /* check against lastTime to optimize search */
        // valid range for i: -1            (pre first title)
        // to titles.length-1 (last title), can't be bigger, as this isn't defined (when would it go last -> post-last)
        // console.log("updateForTime", time, lastTime);
        if (time < lastTime) {
            // SLIDE BACKWARD
            //
            n = titlesByStart.length;
            // [start: 50, start: 70]
            // [end: 55, end: 75]
            // time = 80
            // startIndex = 1 (at end)
            // process ends first! (as shows of same element will override!! when going backwards, dus)
            while (endIndex >= 0 && time < titlesByEnd[endIndex].end) {
                markToShow(titlesByEnd[endIndex]);
                endIndex--;
            }
            while (startIndex >= 0 && time < titlesByStart[startIndex].start) {
                markToHide(titlesByStart[startIndex]);
                startIndex--;
            }
        } else {
            // SLIDE FORWARD
            // 
            // process starts first! (as hides of same element will override!!)
            n = titlesByStart.length;
            while ((startIndex+1) < n && time >= titlesByStart[startIndex+1].start) {
                startIndex++;
                if (startIndex < n) { markToShow(titlesByStart[startIndex]); }
            }    
            n = titlesByEnd.length;
            while ((endIndex+1) < n && time >= titlesByEnd[endIndex+1].end) {
                endIndex++;
                if (endIndex < n) { markToHide(titlesByEnd[endIndex]); }
            }    
        }
        // if (this.startIndex != si) this.setStartIndex(si);

        // COPY lastTime (if Date)
        if (time instanceof Date) {
            lastTime = new Date();
            lastTime.setTime(time.getTime());
        } else {
            lastTime = time;
        }

        // perform show/hides
        var clearFlag = false;
        var tid;
        for (tid in toShow) {
            if (toShow.hasOwnProperty(tid)) { // JSLint (not strictly necessary)
                show(toShow[tid]);
                activeItems[tid] = toShow[tid];
                clearFlag = true;
            }
        }
        if (clearFlag) { toShow = {}; }
        clearFlag = false;
        for (tid in toHide) {
            if (toHide.hasOwnProperty(tid)) { // JSLint (not strictly necessary)
                hide(toHide[tid]);
                delete activeItems[tid];
                clearFlag = true;
            }
        }
        if (clearFlag) { toHide = {}; }

        /* setCurrentTime : MM: new NOV 2011 */
        // console.log("setCurrentTime", settings);
        if (settings.setCurrentTime) {
            for (tid in activeItems) {
                var elt = activeItems[tid];
                // console.log("timeline.setCurrentTime", elt.elt, controller);
                if (elt.elt !== controller) {
                    settings.setCurrentTime(elt.elt, time-elt.start, controller); 
                } else {
                    // console.log("SKIPPING");
                }
            }
        }

        return;
    }

    function add (thing, start, end, itemshow, itemhide) {
        /*
        if (typeof(start) == "string") {
            start = $.datetimecode_parse(start);
        }
        if (typeof(end) == "string") {
            end = $.datetimecode_parse(end);
        }
        */
        // do some sanity checking
        if (start === undefined) { return "no start time"; }
        if (end && (end < start)) { return "end is before start"; }
        // wrap & add elt
        var item = timeline_item(thing, start, end, itemshow, itemhide);
        addTitle(item);

        // show/hide as appropriate, add to activeItems if needed
        if (currentTime >= start && (end === undefined || currentTime < end)) {
            show(item);
            activeItems[item.id] = item;
        } else {
            hide(item);
        }
        setCurrentTime(currentTime);
    }
    that.add = add;

    function setCurrentTime (ct, evt_controller) {
        currentTime = ct;
        updateForTime(ct, evt_controller);
    }
    that.setCurrentTime = setCurrentTime;
    that.getCurrentTime = function () { return currentTime; };    
    that.getMinTime = function () { return minTime; }
    that.getMaxTime = function () { return maxTime; }

    function debug () {
        $.log("titlesByStart");
        for (var i=0; i<titlesByStart.length; i++) {
            var t = titlesByStart[i];
            $.log("    ", t.elt, t.start, "("+t.end+")");
        }
        $.log("titlesByEnd");
        for (var i=0; i<titlesByEnd.length; i++) {
            var t = titlesByEnd[i];
            $.log("    ", t.elt, t.end, "("+t.start+")");
        }
    }
    that.debug = debug;
    return that;
};

// finally the plugin method itself
// based on http://docs.jquery.com/Plugins/Authoring

var settings = {
    currentTime: function (elt) { return elt.currentTime; },
    start : function (elt) { return $.timecode_parse($(elt).attr("data-start")); },
    end : function (elt) { return $.timecode_parse($(elt).attr("data-end")); }
}

var methods = {
    init : function(options) {
        var opts = {};
        $.extend(opts, settings, options);

        return this.each(function() {
            var elt = this;
            var $this = $(this),

            data = $this.data('timeline');
            if (! data) {
                // FIRST TIME INIT
                data = {target: $this};
                data.options = opts;
                $(this).data('timeline', data);
            }

            // init ALWAYS creates a fresh timeline (so it can be used to reset
            // the element and drop evt. dead refs)
            data.timeline = aTimeline({ 
                show: opts.show, 
                hide: opts.hide, 
                setCurrentTime: opts.setCurrentTime
            });

            $this.bind("timeupdate", function (event, controller) {
                //console.log("timeline: timeupdate", event);
                // allow a wrapped getCurrentTime for the element (via playable?)
                var ct = opts.currentTime(elt);
                //console.log("timeline: timeupdate", event.target, ct);
                data.timeline.setCurrentTime(ct, controller);
                return true;
            });
        });
    },
    destroy : function( ) {
        // console.log("timeline.destroy", this);
        return this.each(function(){
            var $this = $(this),
            data = $this.data('timeline');

            // Namespacing FTW
            $(window).unbind('.timeline');
            // data.tooltip.remove();
            $this.removeData('timeline');

        })

    },
    currentTime: function (t) {
        var data = this.data('timeline');
        if (t === undefined) {
            return data.timeline.getCurrentTime();
        } else {
            data.timeline.setCurrentTime(t);
            // $(this.elt).trigger("updatetime");
            return this;
        }
    },
    minTime: function () {
        return this.data('timeline').timeline.getMinTime();
    },
    maxTime: function () {
        return this.data('timeline').timeline.getMaxTime();
    },
    add : function( selector, options ) {
        var data = this.data('timeline');
        options = options || {};
        $(selector).each(function () {
            var start = options.start || data.options.start;
            var end = options.end || data.options.end;
            if (typeof(start) == "function") {
                start = start(this);
            }
            if (typeof(end) == "function") {
                end = end(this);
            }
            // if (start) start = datetimecode_parse(start);
            // if (end) end = datetimecode_parse(end, start);
            if (options.debug) console.log("add", this, start, end);
            data.timeline.add(this, start, end, options.show, options.hide);

            // NEW (Dec 2011) Watch added elements for timeupdate events
            $(this).bind("timeupdate", function (e) {
                // console.log("NEW timeline.timeupdate", this, e);
                var sectionTime = $(this).data("currentTime");
                // console.log("timeupdate", sectionTime, start);
                var newDate = new Date();
                newDate.setTime(start.getTime() + (sectionTime*1000));
                data.timeline.setCurrentTime(newDate, this);
                // data.timeline.setCurrentTimeFromChild(this, );
                return false;
            });
        });
        // console.log("end of add");
        return this;
    },
};

// boilerplate jquery plugin method dispatch code
$.fn.timeline = function(method) {
    if (methods[method]) {
        return methods[method].apply(this, Array.prototype.slice.call(arguments, 1));
    } else if (typeof method === 'object' || ! method) {
        return methods.init.apply(this, arguments);
    } else {
        $.error('Method ' +  method + ' does not exist on jQuery.timeline');
    }
};

})(jQuery);
