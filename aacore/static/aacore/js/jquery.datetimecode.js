(function ($) {

/**
 * @fileoverview 
 * @author Michael Murtaugh <mm@automatist.org> and the Active Archive contributors
 * @license GNU AGPL

Nov 2011: Changed to use Date objects.
provides timecode_parse, datetimecode_parse but doesn't require one or the other.
custom start, end functions should parse the given date as necessary


*/


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

// hours optional
timecode_tosecs_pat = /^(?:(\d\d):)?(\d\d):(\d\d)(,(\d{1,3}))?$/;

function zeropad (n, toplaces) {
    var ret = "" + n;
    var foo = toplaces - ret.length;
    for (var i = 0; i < foo; i++) { ret = "0" + ret; }
    return ret;
}

function zeropostpad (n, toplaces) {
    var ret = "" + n;
    var foo = toplaces - ret.length;
    for (var i = 0; i < foo; i++) { ret = ret + "0"; }
    return ret;
}

/**
 * Converts a timecode to seconds (float).  Seeks and returns first timecode pattern
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
            ret = parseFloat(ret + "." + r[5]);
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
            //if (hours) {
                return zeropad(hours, 2)+":"+zeropad(mins, 2)+":"+zeropad(secs, 2)+","+fract;
            //} else {
                //return zeropad(mins, 2)+":"+zeropad(secs, 2)+","+fract;
            //}
        } else {
            //if (hours) {
                // return zeropad(hours, 2)+":"+zeropad(mins, 2)+":"+zeropad(secs, 2);
                return zeropad(hours, 2)+":"+ zeropad(mins, 2)+":"+zeropad(secs, 2);
            //} else {
                //// return zeropad(hours, 2)+":"+zeropad(mins, 2)+":"+zeropad(secs, 2);
                //return zeropad(mins, 2)+":"+zeropad(secs, 2);
            //}
        }
    } else {
        secs = Math.floor(rawsecs);
        // return zeropad(hours, 2)+":"+zeropad(mins, 2)+":"+zeropad(secs, 2);
        //if (hours) {
            return zeropad(hours, 2)+":"+zeropad(mins, 2)+":"+zeropad(secs, 2);
        //} else {
            //return zeropad(mins, 2)+":"+zeropad(secs, 2);
        //}
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

// yyyy-mm-dd HH:MM:SS,ms
// 1    2  3  4  5  6  7
datetimecode_pat = /^(?:(?:(\d\d\d\d)-(\d\d)-(\d\d))?[ T]?(\d\d):)(\d\d)(?::(\d\d))?(?:,(\d{1,3}))?$/;
// Date is optional (defaults to current day)
// Seconds & Milliseconds optional.

function datetimecode_parse (str, defaultDate) {
    // defaultDate == undefined : uses new Date() (ie NOW)
    // returns javascript Date object
    r = str.match(datetimecode_pat);

    if (r) {
        // console.log("datetimecode_parse, match", r);
        var year, month, date;
        if (r[1] && r[2] && r[3]) {
            // console.log("parsing datetime with date");
            year = parseInt(r[1], 10);
            month = parseInt(r[2], 10) - 1;
            date = parseInt(r[3], 10);
        } else {
            if (!defaultDate) { defaultDate = new Date() }
            year = defaultDate.getFullYear();
            month = defaultDate.getMonth();
            date = defaultDate.getDate();
        }
        var hour, minute, second, millis;
        hour = parseInt(r[4], 10);
        minute = parseInt(r[5], 10);
        second = r[6] ? parseInt(r[6], 10) : 0;
        millis = r[7] ? parseInt(r[7], 10) : 0;
        // console.log(year, month, date, hour, minute, second, millis);
        return new Date(year, month, date, hour, minute, second, millis);
    } else {
        return null;
    }
}
$.datetimecode_parse = datetimecode_parse;


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


$.secs2date = secs2date;

$.date2secs = date2secs;

$.zeropad = zeropad;
$.zeropostpad = zeropostpad;
})(jQuery);


