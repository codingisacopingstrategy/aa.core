(function ($, undefined) {
$.widget("ui.aaplaylist", {
    // default options
    options: {
        option1: "defaultValue",
        hidden: true,
    },
    _post_geometry: function() {
        // RegExp
        var HASH_HEADER_RE = /(^|\n)(#[^#].*?)#*(\n|$)/;
        var STYLE_ATTR_RE = /{@style=.*?}/; 
        var start;
        var end;
        var content = "";

        var style = "{@style=" + $.trim($(this).attr('style')) + "}";

        var section = $(this).attr("data-section");
        $.get("edit/", {
            section: section,
            type: 'ajax', 
        }, function(data) {
            // Searches for Header
            var header_match = HASH_HEADER_RE.exec(data);
            if (header_match) {
                // Defines the substring to replace
                var style_match = STYLE_ATTR_RE.exec(header_match[0]);
                if (style_match) {
                    start = header_match.index + style_match.index;
                    end = start + style_match[0].length;
                } else {
                    start = header_match.slice(1,3).join('').length;
                    end = start;
                };
                var before = data.substring(0, start);
                var after = data.substring(end, data.length)
                content = before + style + after;
                
                $.post("edit/", {
                    content: content,
                    section: section,
                    type: 'ajax', 
                });
            }
        });
    },
    _create: function() {
        // creation code for mywidget
        // can use this.options
        this.element
            .draggable('destroy')
            .draggable({
                handle:'nav',
                grid: [50, 50],
                //zIndex: 2700,
                stop: this._post_geometry,
            }).resizable({
                grid: 50,
                stop: this._post_geometry,
            });
    },
    destroy: function() {
        //this.element.find('nav').remove();
        $.Widget.prototype.destroy.apply(this, arguments); // default destroy
         // now do other stuff particular to this widget
    }
});

$('section').live('dblclick', function(e) {
    e.stopImmediatePropagation();
    $(this).editable('edit/', { 
         loadurl   : 'edit/',
         //id        : 'section',
         name      : 'content',
         submitdata  : function(value, settings) {
             var section = $(this).attr("data-section");
             return {
                 section: section,
                 type: 'ajax',
             }
         },
         loaddata  : function(value, settings) {
             var section = $(this).attr("data-section");
             return {
                 section: section,
                 type: 'ajax',
             }
         },
         rows      : 6,
         width     : '100%',
         type      : 'textarea',
         cancel    : 'Cancel',
         submit    : 'OK',
         indicator : 'Saving changes',
         tooltip   : "Doubleclick to edit...",
         onblur    : 'ignore',
         event     : "edit",
         style     : 'inherit',
         callback : function(value, settings) {
            $(this).replaceWith(function() {
                return $(this).contents();
            });

            // Updates section number
            $('section[class^="annotation"]').each(function(index) {
                $(this).attr('data-section', index + 1);
            })

            $('section.annotation1').aaplaylist('destroy');
            $('section.annotation1').aaplaylist();
        }
    }).trigger('edit');
});

$("a.edit").live("click", function(e) {
    e.preventDefault();
    $(this).closest('section')
        .find('div.wrapper')
        .trigger('dblclick');
});
})(jQuery);
