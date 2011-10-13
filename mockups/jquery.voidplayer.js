/*
 * Copyright 2011 Alexandre Leray <http://stdin.fr/>
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
 */


(function($) {

    function _init (data) {
        if (data.autoplay) {
            _play(data, 350);
            data.$elt.trigger('playing');
        };
    }

    function _play (data, delta) {
        data.currentTime += delta / 1000;
        if (data.currentTime < data.duration) {
            //data.$elt.trigger('progress');
            data.$elt.trigger('timeupdate');
            data.timer = setTimeout(_play, delta, data, delta);
        } else {
            data.currentTime = data.duration;
            data.$elt.trigger('ended');
            if (data.loop) {
                data.currentTime = 0;
                data.timer = setTimeout(_play, delta, data, delta);
            }
        }
        data.paused = false;
    }

    function _pause (data) {
        clearTimeout(data.timer);
        data.paused = true;
        data.$elt.trigger('pause');
    }

    function _seek (data, delta) {
        clearTimeout(data.timer);
    }

    var methods = {
        init : function (options) {
            var settings = {
                autoplay: true,
                controls: false,
                loop: false,
                duration: 0,
            };

            return this.each(function() {
                if (options) { $.extend(settings, options) }

                var $this = $(this);
                var data = $this.data('player');

                if (!data) {
                    $this.data('player', {
                        $elt: $this,
                        autoplay: settings.autoplay,
                        controls: settings.controls,
                        loop: settings.loop,
                        duration: settings.duration,
                        timer: null,
                        currentTime: 0,
                        paused: true,
                    });
                    _init($this.data('player'));
                };
            });
        }, 
        play: function () {
            return this.each(function() {
                var $this = $(this);
                var data = $this.data('player');
                if (data.paused) {
                    _play(data, 350);
                };
            });
        }, 
        pause: function () {
            return this.each(function() {
                var $this = $(this);
                var data = $this.data('player');
                _pause(data);
            });
        }, 
        currentTime: function (value) {
            /*
             * returns the current playback position, expressed in seconds.
             */
            if (value) {
                return this.each(function() {
                    var $this = $(this);
                    var data = $this.data('player');
                    data.currentTime = value;
                    $(this).trigger('timeupdate');
                });
            } else {
                var $this = $(this);
                var data = $this.data('player');
                return data.currentTime
            }
        }, 
        paused: function () {
            return this.each(function() {
                var $this = $(this);
                var data = $this.data('player');
                // TODO
                return data.paused
            });
        }, 
        duration: function (value) {
            if (value) {
                return this.each(function() {
                    var $this = $(this);
                    var data = $this.data('player');
                    data.duration = value;
                    // TODO
                    // return data.paused
                });
            } else {
                // TODO: what happens when you have a bunch of elements?
                var $this = $(this);
                var data = $this.data('player');
                return data.duration
            }
        }, 
    };

    $.fn.player = function (method) {
        // Method calling logic
        if ( methods[method] ) {
            return methods[method].apply(this, Array.prototype.slice.call(arguments, 1));
        } else if (typeof method === 'object' || !method) {
            return methods.init.apply(this, arguments);
        } else {
            $.error('Method ' + method + ' does not exist on aa.player');
        }    
    };
})(jQuery);
