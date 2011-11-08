$(document).ready(function() {
    function adjust_duration ($elt) {
        /*
         * Adjusts the duration of a timebased media
         */
        var max = null;
        var Values = [];
        // Adjusts the player duration
        $('[data-end]').each(function() {
            var data_end = $(this).attr('data-end');
            Values.push($.timecode_tosecs(data_end));
        });
        max = Math.max.apply(Math, Values);
        $elt.voidplayer('duration', max);
    }

    function synchronize(passenger, driver) {
        var newtime = driver.currentTime - $.timecode_tosecs($(passenger).attr('data-start')); 
        passenger.currentTime = newtime;
    }

    // Tiling initialization
    $("article:first").tiling({
        'layouts' : [
            'horizontal',
            'vertical',
            'fair',
        ], 
        'selector' : 'section.section1:visible',
    });
    $("article:first").tiling("tile_fair");

    $(window).resize(function() {
        $("article:first").tiling("update");
    });

    
    //  Creates a void player
    $("body").voidplayer({});

    // Adjusts its duration
    adjust_duration($("body"));

    // Creates the timeline
    $("body").timeline({
        start: function (elt) {
            return $(elt).attr("data-start");
        },
        end: function (elt) {
            return $(elt).attr("data-end");
        },
    }).timeline("add", "audio", {
        show: function (elt) {
            elt.play()
        },
        hide: function (elt) {
            elt.pause()
        }
    }).timeline("add", "section#introduction section.section2", {
        show: function (elt) {
            var $elt = $(elt);
            $elt.fadeIn(1000);
            $elt.css('display', 'table-cell');
            $elt.parents('section.section1').css('display', 'table');
            $("article:first").tiling("update");
        },
        hide: function (elt) {
            var $elt = $(elt)
            $elt.hide()
            $("section.section1:not(:has(section:visible))").hide();
            $("article:first").tiling("update");
        }
    });

    $("audio:first").timeline({
        start: function (elt) {
            return $(elt).attr("data-start");
        },
        end: function (elt) {
            return $(elt).attr("data-end");
        },
    }).timeline("add", "section#chronology section.section2", {
        show: function (elt) {
            var $elt = $(elt);
            $elt.fadeIn(1000);
            $elt.css('display', 'table-cell');
            $elt.parents('section.section1').css('display', 'table');
            $("article:first").tiling("update");
        },
        hide: function (elt) {
            var $elt = $(elt)
            $elt.hide()
            $("section.section1:not(:has(section:visible))").hide();
            $("article:first").tiling("update");
        }
    }).timeline("add", "section#visuals section.section2", {
        show: function (elt) {
            var $elt = $(elt);
            $elt.fadeIn(1000);
            $elt.css('display', 'table-cell');
            $elt.parents('section.section1').css('display', 'table');
            $("article:first").tiling("update");
        },
        hide: function (elt) {
            var $elt = $(elt)
            $elt.hide()
            $("section.section1:not(:has(section:visible))").hide();
            $("article:first").tiling("update");
        }
    //}).timeline("add", "section#related_materials section.section2", {
        //show: function (elt) {
            //var $elt = $(elt);
            //$elt.fadeIn(1000);
            //$elt.css('display', 'table-cell');
            //$elt.parents('section.section1').css('display', 'table');
            //$("article:first").tiling("update");
        //},
        //hide: function (elt) {
            //var $elt = $(elt)
            //$elt.hide()
            //$("section.section1:not(:has(section:visible))").hide();
            //$("article:first").tiling("update");
        //}
    });

    // Scrubber 
    $('#slider').slider({
        max: $("body").voidplayer('duration'),
        animate: true,
        step: 0.1,
        start: function(e) {
            $("body").voidplayer('pause');
            $("audio").attr('muted', true);
        },
        slide: function(e) {
            $("body").voidplayer('currentTime', $(this).slider('value'));
        },
        stop: function(e) {
            console.log($(this).slider('value'));
            $("body").voidplayer('play');
            synchronize($('audio').get(0), $("body").get(0));
            $("audio").attr('muted', false);
        },
    });
        
    $("body").bind('play', function(e) { 
        // console.log('play');
    }).bind('timeupdate', function(e) { 
        // console.log('timeupdate: ' + $(this).voidplayer('currentTime'));
        $("#slider").slider('value', $(this).voidplayer('currentTime'));
        $('#time').text($.timecode_fromsecs($(this).voidplayer('currentTime')) + " / " + $.timecode_fromsecs($(this).voidplayer('duration')));
    }).bind('seeking', function(e) { 
        // console.log('seeking');
        $('audio').get(0).currentTime = $(this).voidplayer('currentTime') - $('audio').attr('data-start');
    }).bind('ended', function(e) { 
        // console.log('ended');
    });

    $("#play").bind('click', function(e) {
        $('body').voidplayer('play');
        $('audio:first').voidplayer('play');
        // $('audio').get(0).play();
    });
    $("#pause").bind('click', function(e) {
        $('body').voidplayer('pause');
        $('audio:first').voidplayer('pause');
    });
});
