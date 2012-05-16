ignite.idea_links = function() {
    var links = $('fieldset.external_links'),
        box = links.find('div.ed'),
        add_link_set,
        delete_link_set;
    add_link_set = function() {
        var add_link = $('<a href="#" class="cta do add_link">Add another link</a>').appendTo(links),
            total_links = $('#id_externals-TOTAL_FORMS');
        add_link.click(function() {
            var rows = links.find('div.inline_field'),
                index = rows.length,
                dupe = $(rows[0]).clone();
            dupe.find('label, input').map(function() {
                var that = $(this),
                    id_val = that.attr('id'),
                    name_val = that.attr('name'),
                    for_val = that.attr('for');
                if (name_val) {
                    that.attr({
                        'name': name_val.replace(/\d/g, index),
                        'id': id_val.replace(/\d/g, index),
                        'value': ''
                    });
                } else {
                    that.attr('for', for_val.replace(/\d/g, index));
                }
            });
            total_links.attr('value', index + 1);
            box.append(dupe);
            dupe.find('input:first').focus();
            return false;
        });
    };
    delete_link_set = function() {
        links.bind('click', function(event) {
            var that = $(event.target);
            if (that.is('.delete_link')) {
                var row = that.closest('div.inline_field'),
                    elm = row.detach();
                /*
                 * Looping through labels so not to blank the hidden inputs
                 */
                elm.find('label').map(function() {
                    $(this).next('input').attr('value', '');
                });
                that.remove();
                elm.appendTo(box);
                return false;
            }
        });
        links.find('div.inline_field').each(function() {
            var that = $(this);
            if (that.find('input:first').attr('value')) {
                that.append('<a href="#" class="cta do delete_link">Remove link</a>');
            } 
        });
    };
    return {
        'add_link_set': add_link_set,
        'delete_link_set': delete_link_set
    };
}();
