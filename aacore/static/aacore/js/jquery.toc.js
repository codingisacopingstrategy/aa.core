(function ($) {

/**
 * @fileoverview 
 * @author Michael Murtaugh <mm@automatist.org> and the Active Archive contributors
 * @license GNU AGPL

*/


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
$.fn.toc = function( method ) {
    if ( methods[method] ) {
        return methods[method].apply( this, Array.prototype.slice.call( arguments, 1 ));
    } else if ( typeof method === 'object' || ! method ) {
        return methods.init.apply( this, arguments );
    } else {
        $.error( 'Method ' +  method + ' does not exist on jQuery.toc' );
    }
};

})(jQuery);


