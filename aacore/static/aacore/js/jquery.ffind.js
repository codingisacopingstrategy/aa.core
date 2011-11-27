/*
 * "filter find", like $.find but it also checks the context element itself.
 */
(function($){
    $.fn.ffind = function(selector) {  
        return $(this).filter(selector).add(selector, this);
    };
})(jQuery);
