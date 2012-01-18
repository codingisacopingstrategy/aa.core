(function ($) {


// Stéphanie's code
$(document).ready(function(){
    var hover = false;
    $(".index-slideshow .wrapper").live("mouseenter", function() {
        var $this = $(this)
        function scrollme() {
            hover = true;
            scrollto = $this.scrollTop();
            $this.animate({
                scrollTop: scrollto + 100,
            }, 500, function() {
                if (hover === true) scrollme();
            });
        }
        scrollme();
    }).live("mouseleave", function(){
       hover = false; 
    });
});

})(jQuery);
