jQuery(document).ready(function($) {
    
    // Set footer always on the bottom of the page
     

    function footerBottom(footerSelector) {
        footerSelector.css("display", "block")
        var docHeight = $(window).height();
        var footerTop = footerSelector.position().top + footerSelector.height();
        var footerH = footerSelector.height();
        if (footerTop < docHeight) {
            footerSelector.css("margin-top", (docHeight - footerTop) + "px");
        }
    }
    // Apply when page is loading 
    footerBottom($("#footerpb"));

    // Apply when page is resizing
    $(window).resize(function() {
        footerBottom($("#footerpb"));
    });
});
