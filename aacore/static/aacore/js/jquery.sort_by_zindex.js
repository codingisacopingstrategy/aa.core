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
    $.fn.sort_by_zindex = function (options) {
        /*
         * Takes a jquery collection and sorts its elements according to their z-index.
         * Returns the sorted collection
         *    
         *    >>> $('section').sort_by_zindex();
         *    >>> $('section').sort_by_zindex({reverse: true});
         */

        var opts = $.extend({}, $.fn.sort_by_zindex.defaults, options);

        var Elts = $(this).toArray()
            .sort(function (a, b) {
                var azi = getComputedStyle(a).getPropertyValue('z-index');
                var bzi = getComputedStyle(b).getPropertyValue('z-index');
                if (azi < bzi) { return -1; } 
                else if (azi > bzi) { return 1; }
                else { return 0; }
            });
        if (opts.reverse) { Elts.reverse(); }
        return $(Elts);
    };

    $.fn.sort_by_zindex.defaults = {
        reverse: false,
    };
})(jQuery);
