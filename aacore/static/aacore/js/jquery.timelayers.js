(function ($) {
// based on http://docs.jquery.com/Plugins/Authoring

var aItem = function (elt, layer, title) {
    var that = {
        layer: layer,
        title: title
    };
    var start, end;
    // console.log(this);
    var start = $.timecode_tosecs_attr($(title).attr("data-start"));
    var end = $(title).attr("data-end") ? $.timecode_tosecs_attr($(title).attr("data-end")) : undefined;

    var width = 1;
    if (start !== undefined && end !== undefined) {
        duration = (end - start);
        width = Math.ceil(layer.seq.pixelsPerSecond * duration);
    }

    $(elt).addClass("aa_timelayers_title").css({
        float: 'left',
        width: width + 'px',
        height: '100%',
        borderLeft: "1px solid black"
    });
    return that;
}

var aLayer = function (elt, seq, section, options) {
    var that = {};
    that.seq = seq;
    that.elt = elt;
    options = options || {};
    var label = $("h1", section).text() || $(section).attr("id") || options.label;
    $(elt).addClass("aa_timelayers_section").css({
        width: '500px',
        height: '20px',
        position: 'relative',
        background: 'gray',
        marginRight: '5px'
    }).draggable({containment: "parent"}).resizable({handles: 'e, w'});

    var labeldiv = $("<div></div>").addClass("aa_sequence_layer_label").text(label).css({
        fontSize: '12px',
        fontFamily: 'Monospace',
        fontWeight: 'bold',
        textTransform: 'uppercase',
        zIndex: '10',
        position: 'absolute',
        left: '0px',
        top: '0px',
        color: 'black'
    }).appendTo(elt);

    $("*[data-start]", section).each (function () {
        // console.log("item", this);
        var itemelt = $("<div></div>").appendTo(elt).get(0);
        var item = aItem(itemelt, that, this);
    });

    return that;
}

var aSequence = function (elt, options) {
    var that = {};
    that.pixelsPerSecond = 0.5;
    var duration;
    // $.extend(settings, options);

    $(elt).addClass("aa_sequence");
    var thumb = $("<div></div>").addClass("aa_sequence_thumb").css({
        position: 'absolute',
        background: 'white',
        top: 0,
        left: 0,
        width: "10px",
        height: '100%',
        zIndex: '10'
    }).appendTo(elt).draggable({"containment": "parent"});

    $("video").each(function () {
        var sectionelt = $("<div></div>").get(0);
        var layer = aLayer(sectionelt, that, this, {label: "video"});
        $(layer.elt).appendTo(elt);
    });
    $(".section").each(function () {
        var sectionelt = $("<div></div>").get(0);
        var layer = aLayer(sectionelt, that, this);
        $(layer.elt).appendTo(elt);
    });


    var zoom = $("<div></div>").addClass("aa_sequence_zoom").css({
        position: 'absolute',
        right: '0',
        bottom: '0',
        width: '100px',
        height: '10px',
        background: 'white'
    }).appendTo(elt);
    var zoomThumb = $("<div></div>").addClass("aa_sequence_zoom_thumb").css({
        height: '100%',
        width: '10px',
        background: 'black'
    }).appendTo(zoom).draggable({
        'containment': 'parent',
        stop: function () {
            console.log("stop");
        }
    });

    return that;
}


var settings = {};

var methods = {
    init : function( options ) {
        var opts = {};
        $.extend(opts, settings, options);
        return this.each(function(){
            var elt = this;
            var $this = $(this),
            data = $this.data('aasequence');
            if ( ! data ) {
                // FIRST TIME INIT
                data = aSequence(this, opts);
                $(this).data('aasequence', data);
            }
        });
    },
    destroy : function( ) {
        return this.each(function(){
            var $this = $(this),
            data = $this.data('aasequence');
            // data.destroy();
            // Namespacing FTW
            $(window).unbind('.aasequence');
            // data.tooltip.remove();
            $this.removeData('aasequence');

        })

    },
    setCurrentTime: function (t) {
    },
    add : function() {
        var data = this.data('aasequence');
        options = options || {};
        return this;
    },
};

// boilerplate jquery plugin method dispatch code
$.fn.timelayers = function( method ) {
    if ( methods[method] ) {
        return methods[method].apply( this, Array.prototype.slice.call( arguments, 1 ));
    } else if ( typeof method === 'object' || ! method ) {
        return methods.init.apply( this, arguments );
    } else {
        $.error( 'Method ' +  method + ' does not exist on jQuery.timelayers' );
    }
};

})(jQuery);


