/**
 * @requires ignite.data
 * @returns {String} string of a URL that we can load in VIA xhr
 */
ignite.media_url = function(loc) {
    var id = ignite.data;
    return id.MEDIA_URL + loc + '?build=' + id.JS_BUILD_ID;
};
/**
 * Object containing file resourced for the site and specific paages
 */
ignite.areas = {
    common : [
        {
            elm : 'form.browserid_form',
            requires : 'https://browserid.org/include.js',
            onload : function() {
                var form = $('form.browserid_form');
                form.find('a.login').bind('click', function(e) {
                    e.preventDefault();
                    navigator.id.getVerifiedEmail(function(assertion) {
                        var $e = form.find('input.id_assertion');
                        $e.val(assertion.toString());
                        $e.parent().submit();
                    });
                });
            }
        }
    ],
    about : {
        requires : ignite.media_url('js/include/panels.js'),
        onload : function() {
            ignite.panels.init();
        }
    },
    show_submission : {
        requires : ignite.media_url('js/include/voting.js'),
        onload : function() {
            ignite.up_votes.init();
        }
    },
    create_submission : {
        requires: [ignite.media_url('js/include/ext/pagedown/Markdown.Converter.js'), ignite.media_url('js/include/ext/pagedown/Markdown.Editor.js'), ignite.media_url('js/include/links.js')],
        onload : function() {
            var ed = $('#wmd-input'),
                converter = new Markdown.Converter(),
                editor = new Markdown.Editor(converter);
            ed.before('<div id="wmd-button-bar"></div>');
            editor.run();
            ignite.idea_links.add_link_set();
        }
    },
    edit_submission : {
        requires: [ignite.media_url('js/include/ext/pagedown/Markdown.Converter.js'), ignite.media_url('js/include/ext/pagedown/Markdown.Editor.js'), ignite.media_url('js/include/links.js')],
        onload: function() {
            var ed = $('#wmd-input'),
                converter = new Markdown.Converter(),
                editor = new Markdown.Editor(converter);
            ed.before('<div id="wmd-button-bar"></div>');
            editor.run();
            ignite.idea_links.delete_link_set();
            ignite.idea_links.add_link_set();
        }
    }
};
/* Initing the sites global JavaScript */
$(function() {
    ignite.lacky  = lacky(ignite.data, ignite.areas);
    ignite.lacky.prepare();
});
