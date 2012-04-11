(function ($) {

var loading = false;

function resolveRelativeLink(base, link) {
    if (!(link.match("^(/|http)") !== null)) {
        // link is relative...
        var base_parts = base.split("/");
        base_parts.pop();
        var link_parts = link.split("/");
        var has_base = (base_parts.length > 0);
        
        for (var i=0; i<link_parts.length; i++) {
            var lp = link_parts[i];
            if (lp == "..") {
                if (has_base) {
                    base_parts.pop();
                    has_base = (base_parts.length > 0);
                } else {
                    base_parts.push("..");
                }
            } else {
                base_parts.push(link_parts[i]);
            }
        }
        ret = base_parts.join("/");
        // $.log("resolveRelativeLink", base, link, ret);
        return ret;
    }
}

$(document).bind("refresh", function (evt) {
    // console.log("refreshing browser links...");
    var context = evt.target;
    $("a[target='browser']", context).click(function () {
        loadbrowserpage($(this).attr("href"));
        return false;
    });
});

function loadbrowserpage (url, targetsel, expandWhenLoaded, success_callback) {
    $("iframe#browser-panel").attr('src', url);
    $("#center").layout().open("south");
    //targetsel = targetsel || "#browser";
    //if (expandWhenLoaded === undefined) expandWhenLoaded = true;
    //loading = true;
    //$(targetsel).addClass('loading');
    //// var mitem = menuLinksByURL[url];
    //// $.log("setActive", mitem, url);
    //// setActiveMenuLink(mitem);

    //$(targetsel + " .minipage").load(url+" #minipage", function () {
        //loading = false;
        //$(targetsel).removeClass('loading');
        //window.setTimeout(function () { $(targetsel).scrollTop(0); }, 250);
        
        //// load for any onload code
        //$(targetsel + " .minipage .minipage_onload").each(function () {
            //var text = $(this).text();
            //// console.log("minipage.onload", text);
            //eval(text);
        //});
    
        //if (expandWhenLoaded) { $("body").layout().open("south");  }// expand(targetsel);
        //if (success_callback) { success_callback(); }

        //// retarget links
        //$(targetsel+" .minipage a").not("a.directlink").click(function () {
            //loadbrowserpage($(this).attr("href"));
            //return false;
        //});

        //// Fire a refresh at the browser content!
        //$(targetsel).trigger("refresh");

        //// resolve (relative) links
        //[>
        //$(targetsel+" .minipage *[href]").each(function () {
            //$(this).attr("href", resolveRelativeLink(url, $(this).attr("href")));
        //});
        //$(targetsel+" .minipage *[src]").each(function () {
            //$(this).attr("src", resolveRelativeLink(url, $(this).attr("src")));
        //});
        //*/


    //});
}


})(jQuery);
