ignite.panels = function() {
    var init,
        hash = window.location.hash;
    init = function() {
        var triggers = $('h2.trigger'),
            open,
            open_trigger;
        triggers.each(function(index) {
            var that = $(this),
                btn = $('<button class="box" tab-index="-1">' + that.text() + ' <span class="inst">(click to expand)</span></button>'),
                nxt = that.next('div.panel');
            that.html(btn);
            if (index === 0) {
                nxt.addClass('open-panel');
                btn.addClass('open-panel');
                open = nxt;
                open_trigger = btn;
            }
            btn.click(function() {
                open.removeClass('open-panel');
                open_trigger.removeClass('open-panel');
                nxt.addClass('open-panel');
                btn.addClass('open-panel');
                open = nxt;
                open_trigger = btn;
                open_trigger.focus();
            });
        });
        // quick fix to ensure that if we're linking direct to an ID the relevant section is open
        if (hash) {
            var origin = $(hash);
            if (origin.length) {
                origin.closest('section').find('button').click();
            }
        }
    };
    return {
        'init': init
    };
}();
