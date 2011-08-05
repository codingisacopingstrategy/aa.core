/*
 * Copyright 2010-2011 Alexandre Leray <http://stdin.fr/>
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
    var methods = {
        init : function (options) {
            var settings = {
                'layouts' : [
                    'horizontal',
                    'vertical',
                    'fair',
                ], 
                'selector': 'div.box', 
                'post_init': function() {},
            };

            return this.each(function() {
                var $this = $(this);

                if (options) {
                    $.extend(settings, options)
                }

                var data = $this.data('tiling');
                // If the plugin hasn't been initialized yet
                if (!data) {
                    /*
                     Do more setup stuff here
                    */
                    $this.data('tiling', {
                        target : $this,
                        settings: settings,
                        layout_map: {
                            'horizontal': 'tile_horizontally',
                            'vertical': 'tile_vertically',
                            'fair': 'tile_fair',
                        },
                    });
                }

               // TODO: find out how to bind events/hooks with arguments
               if (settings.post_init) {
                   //$this.bind('post_init', settings.post_init);
                   //$this.trigger('post_init', [$this]);
                   //var e = arguments[0];
                   //e.settings = settings;
                   //settings.post_init.call($this);
                   settings.post_init();
               }
            });
        },  
        update: function () {
            return this.each(function() {
                var $this = $(this);
                var data = $this.data('tiling');
                // Applies the methods mapped to the current layout
                $this.tiling(data.layout_map[data.current_layout]);
            });
        },
        next: function () {
            return this.each(function() {
                var $this = $(this);
                var data = $this.data('tiling');
                var current_layout_index = jQuery.inArray(data.current_layout, data.settings.layouts);
                if (current_layout_index === -1) {
                    throw "current layout isn't the settings";
                }
                var next_layout_index = (current_layout_index + 1) % data.settings.layouts.length;
                var next_layout = data.settings.layouts[next_layout_index];
                var next_layout_method = data.layout_map[next_layout];
                $this.tiling(next_layout_method);
            });
        },
        previous: function () {
            return this.each(function() {
                var $this = $(this);
                var data = $this.data('tiling');
                var current_layout_index = jQuery.inArray(data.current_layout, data.settings.layouts);
                if (current_layout_index === -1) {
                    throw "current layout isn't the settings";
                }
                // FIXME: The remainder operator doesn't work on negative numbers.
                // The trick here is to add the length of data.settings.layouts to avoid
                // negative numbers, but it is not very elegant, is it?
                var next_layout_index = (data.settings.layouts.length + current_layout_index - 1) % data.settings.layouts.length;
                var next_layout = data.settings.layouts[next_layout_index];
                var next_layout_method = data.layout_map[next_layout];
                $this.tiling(next_layout_method);
            });
        },
        //relax: function () {
            //return this.each(function() {
                //// apply default css
            //});
        //},
        toogle: function () {
            return this.each(function() {
                var $this = $(this);
                var data = $this.data('tiling');
                //data.current_layout;
                if (data.current_layout == "vertical") {
                    $this.tiling("tile_horizontally");
                } else if (data.current_layout == "horizontal") {
                    $this.tiling("tile_vertically");
                    // $this.tiling("tile_fair");
                } else {
                    $this.tiling("tile_vertically");
                }
            });
        },
        tile_vertically : function () {
            return this.each(function() {
                var $this = $(this);
                var width = $this.innerWidth();
                var height = $this.innerHeight();
                var data = $this.data('tiling');
                data.current_layout = "vertical";
                var elts = $this.find(data.settings.selector);
                var len = elts.length;
                elts.css({
                    'position': '',
                    'float': 'left',
                    'height': Math.floor(height / len),
                    'width': width,
                });
            });
        },
        tile_horizontally : function () {
            return this.each(function() {
                var $this = $(this);
                var width = $this.innerWidth();
                var height = $this.innerHeight();
                var data = $this.data('tiling');
                data.current_layout = "horizontal";
                var elts = $this.find(data.settings.selector);
                var len = elts.length;
                elts.css({
                    'position': '',
                    'float': 'left',
                    'height': height,
                    'width': Math.floor(width / len),
                });
            });
        },
        tile_fair : function() {
            return this.each(function() {
                var $this = $(this);
                var width = $this.innerWidth();
                var height = $this.innerHeight();
                var data = $this.data('tiling');
                var elts = $this.find(data.settings.selector);
                var cols = Math.ceil(Math.sqrt(elts.length));
                var rows = Math.ceil(elts.length / cols);
                var col = 0;
                var row = 0;
                elts.each(function() {
                    var geometry = {};

                    if ((elts.length < (rows * cols)) &&  (row == (rows - 1))) {
                        geometry.width = width / (cols - ((rows * cols) - elts.length));
                    } else {
                        geometry.width = width / cols;
                    }
                    geometry.height = height / rows;
                    geometry.left = col * geometry.width;
                    geometry.top = row * geometry.height;

                    $(this).css({
                        'position': 'absolute',
                        'width': geometry.width,
                        'height': geometry.height,
                        'left': geometry.left,
                        'top': geometry.top,
                    });

                    col += 1;
                    if (col === cols) {
                        col = 0;
                        row += 1;
                    }
                });

                data.current_layout = "fair";
            });
        },
        adapt_fontsize : function() {
            return this.each(function() {
                var $this = $(this);
                var width = $this.innerWidth();
                var data = $this.data('tiling');
                $this.find(data.settings.selector)
                    .each(function() {
                        var $this = $(this);
                        $this.css('font-size', ($this.innerWidth() / 20) + 'px');
                    });
            });
        },
    };

    $.fn.tiling = function (method) {
        // Method calling logic
        if ( methods[method] ) {
            return methods[ method ].apply( this, Array.prototype.slice.call( arguments, 1 ));
        } else if ( typeof method === 'object' || ! method ) {
            return methods.init.apply( this, arguments );
        } else {
            $.error( 'Method ' +  method + ' does not exist on jQuery.tiling' );
        }    
    };
})(jQuery);
