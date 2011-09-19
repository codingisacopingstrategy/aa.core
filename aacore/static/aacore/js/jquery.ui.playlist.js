(function ($, undefined) {
$.widget("ui.aaplaylist", {
    // default options
    options: {
        option1: "defaultValue",
        hidden: true,
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
                //stop: post_geometry,
            }).resizable({
                grid: 50,
                //stop: post_geometry,
            });
    },
    _doSomething: function() {
        // internal functions should be named with a leading underscore
        // manipulate the widget
    },
    value: function() {
        // calculate some value and return it
        return this._calculate();
    },
    length: function() {
        return this._someOtherValue();
    },
    destroy: function() {
        //this.element.find('nav').remove();
        $.Widget.prototype.destroy.apply(this, arguments); // default destroy
         // now do other stuff particular to this widget
    }
});

$('section').live('dblclick', function(e) {
    e.stopPropagation();
    $('section').editable('destroy');
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
         //cancel    : 'Cancel',
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

//$('a.delete').live("click", function(e) {
    //if (confirm("Are you sure?")) {
        //e.preventDefault();
        //var $elt = $(this).parents("section");
        //$.post("edit/?section=" + $elt.attr("data-section"), 
            //{
                //content: "",
                //page: window.page,
            //}, function(data) {
                //$elt.remove();
                //window.location.reload()
        //});
    //};

//});
})(jQuery);
