ignite.up_votes = function() {
    var init;
    init = function() {
        var form = $('#user_vote').attr('tab-index', '-1'),
            message = false,
            text_values = {
                up: {
                    url_suffix:"up",
                    input_txt:"Give this a thumbs up",
                    input_cls:"thumb cta do"
                },
                clear:{
                    url_suffix:"clear",
                    input_txt:"Clear my vote",
                    input_cls:"cancel cta do"
                }
            };
        form.bind('submit', function() {
            var action, csrf, trigger, parent_node;
            action = form.attr('action');
            csrf = form.find('input[name="csrfmiddlewaretoken"]').attr('value');
            trigger = form.find('input.cta');
            parent_node = form.parent();
            parent_node.addClass('loading');
            // Stop the message from loading more than once
            if (!message) {
                message = $('<p class="loader" tab-index="-1">Registering your vote</p>').insertBefore(form);
            }
            message.focus();
            $.ajax({
                type:"POST",
                dataType:"json",
                url:action,
                data:"csrfmiddlewaretoken=" + csrf,
                success:function(data) {
                    if (trigger.is('.thumb')) {
                        obj = text_values.clear;
                    } else {
                        obj = text_values.up;
                    } 
                    $('span.score').html(data.score.num_votes);
                    form.find('.cta').attr({
                        'value' : obj.input_txt,
                        'class' : obj.input_cls
                    });
                    form.attr('action',action.replace(/[a-z]{2,5}$/,obj.url_suffix));
                    $('span.total_votes').html(data.score.num_votes);
                    parent_node.removeClass('loading');
                    form.focus();
                }
            });
            return false;
        });
    };
    return {
        'init': init
    };
}();
