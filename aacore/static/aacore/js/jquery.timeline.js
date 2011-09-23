(function ($) {

/**
 * @fileoverview 
 * @author Michael Murtaugh <mm@automatist.org> and the Active Archive contributors
 * @license GNU AGPL

Timeline organizes (HTML) elements by time.
Elements are attached to a timeline with a start time and (optionally) an end time.
A Timeline has a notion of a currentTime, and manages hiding / showing (via a callback) elements accordingly. Timelines follow the element's "timeupdate" events. A Timeline may also be passive and require an external element to "drive" it via calls to setCurrentTime.

*/

////////////////////////////////////////////////////////////////////
// timecode
////////////////////////////////////////////////////////////////////

// hours optional
timecode_tosecs_pat = /^(?:(\d\d):)?(\d\d):(\d\d)(,(\d{1,3}))?$/;

function zeropad (n, toplaces) {
    var ret = ""+n;
    var foo = toplaces - ret.length;
    for (var i=0; i<foo; i++) { ret = "0"+ret; }
    return ret;
}

function zeropostpad (n, toplaces) {
    var ret = ""+n;
    var foo = toplaces - ret.length;
    for (var i=0; i<foo; i++) { ret = ret+"0"; }
    return ret;
}

/**
 * Converts a timecode to seconds.  Seeks and returns first timecode pattern
 * and returns it in secs nb:.  Timecode can appear anywhere in string, will
 * only convert first match.  
 * @private
 * @param {String} tcstr A string containing a timecode pattern.
 * @returns A timecode in secs nb.
 */
function timecode_tosecs (tcstr) {
    r = tcstr.match(timecode_tosecs_pat);
    if (r) {
        ret = 0;
        if (r[1]) {
            // Note that the parseInt(f, 10):avoids "09" being seen as octal (and throws an error)
            ret += 3600 * parseInt(r[1], 10);
        }
        ret += 60 * parseInt(r[2], 10);
        ret += parseInt(r[3], 10);
        if (r[5]) {
            ret = parseFloat(ret+"."+r[5]);
        }
        return ret;
    } else {
        return null;
    }
}

/**
 * Converts seconds to a timecode.  If fract is True, uses .xxx if either
 * necessary (non-zero) OR alwaysfract is True.
 * @private
 * @param {String} rawsecs A String containing a timecode pattern 
 * @param {String} fract A String
 * @param {Boolean} alwaysfract A Boolean
 * @returns A string in HH:MM:SS[.xxx] notation
 */
function timecode_fromsecs (rawsecs, fract, alwaysfract) {
    // console.log("timecode_fromsecs", rawsecs, fract, alwaysfract);
    if (fract === undefined) { fract = true; }
    if (alwaysfract === undefined) { alwaysfract = false; }
    // var hours = Math.floor(rawsecs / 3600);
    // rawsecs -= hours*3600;
    var hours = Math.floor(rawsecs / 3600);
    rawsecs -= hours * 3600;   
    var mins = Math.floor(rawsecs / 60);
    rawsecs -= mins*60;
    var secs;
    if (fract) {
        secs = Math.floor(rawsecs);
        rawsecs -= secs;
        if ((rawsecs > 0) || alwaysfract) {
            fract = zeropostpad((""+rawsecs).substr(2, 3), 3);
            // return zeropad(hours, 2)+":"+zeropad(mins, 2)+":"+zeropad(secs, 2)+","+fract;
            if (hours) {
                return zeropad(hours, 2)+":"+zeropad(mins, 2)+":"+zeropad(secs, 2)+","+fract;
            } else {
                return zeropad(mins, 2)+":"+zeropad(secs, 2)+","+fract;
            }
        } else {
            if (hours) {
                // return zeropad(hours, 2)+":"+zeropad(mins, 2)+":"+zeropad(secs, 2);
                return zeropad(hours, 2)+":"+ zeropad(mins, 2)+":"+zeropad(secs, 2);
            } else {
                // return zeropad(hours, 2)+":"+zeropad(mins, 2)+":"+zeropad(secs, 2);
                return zeropad(mins, 2)+":"+zeropad(secs, 2);
            }
        }
    } else {
        secs = Math.floor(rawsecs);
        // return zeropad(hours, 2)+":"+zeropad(mins, 2)+":"+zeropad(secs, 2);
        if (hours) {
            return zeropad(hours, 2)+":"+zeropad(mins, 2)+":"+zeropad(secs, 2);
        } else {
            return zeropad(mins, 2)+":"+zeropad(secs, 2);
        }
    }
}

/**
 * A lazy version of timecode_tosecs() that accepts both timecode strings and
 * seconds float/integer as parameter.
 * @private
 * @param {String|Integer|Float} val A timecode or seconds. 
 * @returns A timecode in secs nb
 */
function timecode_tosecs_attr(val) {
    if (val) {
        if (typeof(val) == "string") {
            var tc = timecode_tosecs(val);
            if (tc !== null) { return tc; }
        }
        return parseFloat(val);
    }
    return val;
}                        

// export
/**
 * Converts a timecode to seconds.  Seeks and returns first timecode pattern
 * and returns it in secs nb:.  Timecode can appear anywhere in string, will
 * only convert first match.  Note that the parseInt(f, 10), the 10 is
 * necessary to avoid "09" parsing as octal (incorrectly returns 0 then since 9
 * is an invalid octal digit). 
 * @function
 * @param {String} tcstr A string containing a timecode pattern.
 * @returns A timecode in secs nb.
 */
$.timecode_fromsecs = timecode_fromsecs;

/**
 * Converts seconds to a timecode.  If fract is True, uses .xxx if either
 * necessary (non-zero) OR alwaysfract is True.
 * @function
 * @param {String} rawsecs A String containing a timecode pattern 
 * @param {String} fract A String
 * @param {Boolean} alwaysfract A Boolean
 * @returns A string in HH:MM:SS[.xxx] notation
 */
$.timecode_tosecs = timecode_tosecs;

/**
 * A lazy version of timecode_tosecs() that accepts both timecode strings and
 * seconds float/integer as parameter.
 * @function
 * @param {String|Integer|Float} val A timecode or seconds. 
 * @returns A timecode in secs nb
 */
$.timecode_tosecs_attr = timecode_tosecs_attr;

// alternate names

/**
 * Shortcut for {@link $.timecode_tosecs_attr}
 * @function
 */
$.timecode_parse = timecode_tosecs_attr;

/**
 * Shortcut for {@link $.timecode_fromsecs}
 * @function
 */
$.timecode_unparse = timecode_fromsecs;

////////////////////////////////////////
// timeline
////////////////////////////////////////
/*
aTimeline -- private closure-class used by the plugin
*/

var aTimeline = function (options) {
    var that = {};
    var cc_item_uid = 0;

    var settings = {};
    $.extend(settings, options);

    // element wrapper
    var timeline_item = function (elt, start, end, show, hide) {
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

    var currentTime = 0.0;
    var titlesByStart = [];
    var titlesByEnd = [];
    var lastTime = undefined;
    var startIndex = -1;
    var endIndex = -1;
    var toShow = {};
    var toHide = {};
    var activeItems = {};
    
    function addTitle (newtitle) {
        // addTitleByStart
        /* insert annotation in the correct (sorted) location */
        var placed = false;
        for (var i=0; i<titlesByStart.length; i++) {
            if (titlesByStart[i].start > newtitle.start) {
                // insert before this index
                titlesByStart.splice(i, 0, newtitle);
                placed = true;
                break;
            }
        }
        // otherwise simply append
        if (!placed) { titlesByStart.push(newtitle); }

        // addTitleByEnd
        /* insert annotation in the correct (sorted) location */
        placed = false;
        for (i=0; i<titlesByEnd.length; i++) {
            if ((titlesByEnd[i].end > newtitle.end) || (titlesByEnd[i].end === undefined && newtitle.end !== undefined)) {
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

    function updateForTime (time) {
        if (titlesByStart.length === 0) { return; }
        var n;
        /* check against lastTime to optimize search */
        // valid range for i: -1            (pre first title)
        // to titles.length-1 (last title), can't be bigger, as this isn't defined (when would it go last -> post-last)
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
        lastTime = time;

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

        return;
    }

    function add (thing, start, end, itemshow, itemhide) {
        if (typeof(start) == "string") {
            start = $.timecode_tosecs(start);
        }
        if (typeof(end) == "string") {
            end = $.timecode_tosecs(end);
        }
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

    function setCurrentTime (ct, controller) {
        currentTime = ct;
        updateForTime(ct);
    }
    that.setCurrentTime = setCurrentTime;

    that.getCurrentTime = function () { return currentTime; };
    
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
    currentTime: function (elt) { return elt.currentTime; }
}

var methods = {
    init : function( options ) {
        var opts = {};
        $.extend(opts, settings, options);
        return this.each(function(){
            var elt = this;
            var $this = $(this),
            data = $this.data('timeline');
            if ( ! data ) {
                // FIRST TIME INIT
                data = { target : $this };
                data.options = opts;
                $(this).data('timeline', data);
            }
            // init ALWAYS creates a fresh timeline (so it can be used to reset the element and drop evt. dead refs)
            data.timeline = aTimeline({ show: opts.show, hide: opts.hide})
            $this.bind("timeupdate", function (evt) {
                // console.log("timeupdate", evt.target, evt.target.currentTime);
                // allow a wrapped getCurrentTime for the element (via playable?)
                data.timeline.setCurrentTime(opts.currentTime(elt));
            });
        });
    },
    destroy : function( ) {
        return this.each(function(){
            var $this = $(this),
            data = $this.data('timeline');

            // Namespacing FTW
            $(window).unbind('.timeline');
            // data.tooltip.remove();
            $this.removeData('timeline');

        })

    },
    setCurrentTime: function (t) {
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
            if (start) start = timecode_tosecs_attr(start);
            if (end) end = timecode_tosecs_attr(end);
            if (options.debug) console.log("add", this, start, end);
            data.timeline.add(this, start, end, options.show, options.hide);
        });
        // console.log("end of add");
        return this;
    },
};

// boilerplate jquery plugin method dispatch code
$.fn.timeline = function( method ) {
    if ( methods[method] ) {
        return methods[method].apply( this, Array.prototype.slice.call( arguments, 1 ));
    } else if ( typeof method === 'object' || ! method ) {
        return methods.init.apply( this, arguments );
    } else {
        $.error( 'Method ' +  method + ' does not exist on jQuery.timeline' );
    }
};

})(jQuery);


