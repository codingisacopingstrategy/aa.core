(function ($, undefined) {
$.widget("ui.aaplaylist", {
    // default options
    options: {
        option1: "defaultValue",
        hidden: true,
        post_draggable: function(event, ui) {},
        post_resizable: function(event, ui) {},
    },
    _create: function() {
        this.element
            .draggable('destroy')
            .draggable({
                handle:'nav',
                grid: [50, 50],
                stop: this.options.post_draggable,
            }).resizable({
                grid: 50,
                stop: this.options.post_resizable,
            });
    },
    destroy: function() {
        $.Widget.prototype.destroy.apply(this, arguments); // default destroy
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
         // width     : '100%',
         type      : 'textarea',
         cancel    : 'Cancel',
         submit    : 'Save',
         indicator : 'Saving changes',
         tooltip   : "Doubleclick to edit...",
         onblur    : 'ignore',
         event     : "edit",
         callback : function(value, settings) {
            $(this).replaceWith(function() {
                return $(this).contents();
            });
            // Updates section number
            $('section[class^="section"]').each(function(index) {
                $(this).attr('data-section', index + 1);
            })

            $('section.section1').aaplaylist('destroy');
            $('section.section1').aaplaylist();
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
