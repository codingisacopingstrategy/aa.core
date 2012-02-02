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
                selector: 'section',
                post_reorder: function(event, ui, settings) {},
                post_toggle: function(event, settings, target) {},
            };

            return this.each(function() {
                if (options) { $.extend(settings, options) }

                var $this = $(this);
                var data = $this.data('aalayers');

                if (!data) {
                    $this.data('aalayers', {
                        $container: $this,
                        selector: settings.selector,
                        post_reorder: settings.post_reorder,
                        post_toggle: settings.post_toggle,
                    });
                    _create($this.data('aalayers'));
                };
            });
        }, 
        populate : function() {
            return this.each(function(){
                var $this = $(this);
                var data = $this.data('aalayers');
                _populate(data);
            })
        },
    };

    function _create(data) {
        data.$container.append($(""
            + "<form>"
            + "    <fieldset>"
            + "        <legend>annotations</legend>"
            + "        <ul></ul>"
            + "    </fieldset>"
            + "</form>"
        ).find('ul').sortable({
            axis: 'y',
            stop : function(event, ui) {
                data.post_reorder.apply(data.$container, [event, ui, data]);
            },
        }));
        _populate(data);
    }

    function _populate(data) {
        data.$container.find('ul').empty();
        $(data.selector).sort_by_zindex({reverse: true})
            .each(function() {
                var $this = $(this);
                var $h1 = $this.find('h1').clone();
                var $li = $('<li></li>');

                var $input = $('<input type="checkbox" name="some_name" value="bla"/>')
                    .attr('checked', $this.is(':visible'))
                    .bind('change', function(event) {
                        data.post_toggle.apply(data.container, [event, data, $this]);
                    });

                var $label = $('<label for="name"><a href="#' + $this.attr('id')+ '">' + $h1.find('span.edit, span.about').remove().end().text() + '</a></label>');
                //var $label = $('<label for="name"><a href="#' + $this.attr('id')+ '">' + $h1.text() + '</a></label>');
                //var $label = $('<label>').attr('for', 'name').append(
                        //$('a').attr('href', '#' + $this.attr('id')).text($h1.text())
                    //);

                var export_link = $("<a>").text("⤍ ")
                    .attr('title', 'export to audacity markers')
                    .attr('href', './annotations/' + $this.attr('data-section'))
                    .attr('target', '_blank')
                    .addClass('audacity')
                    .css('float', 'right');

                var import_link = $("<a>").text("⤌ ")
                    .attr('title', 'import from audacity markers')
                    .attr('href', './annotations/' + $this.attr('data-section') + '/import')
                    //.attr('target', '_blank')
                    .addClass('audacity')
                    .css('float', 'right');

                $li.append($input, export_link, import_link)
                    .append($label);
                data.$container.find('ul').append($li);
            });
    }

    $.fn.reverse = [].reverse;

    $.fn.aalayers = function (method) {
        /*
         * Depends on jquery.sort_by_zindex.js
         */
        // Method calling logic
        if ( methods[method] ) {
            return methods[method].apply(this, Array.prototype.slice.call(arguments, 1));
        } else if (typeof method === 'object' || !method) {
            return methods.init.apply(this, arguments);
        } else {
            $.error('Method ' + method + ' does not exist on aa.layers');
        }    
    };
})(jQuery);
