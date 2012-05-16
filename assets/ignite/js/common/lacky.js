/**
 * @namespace Functions used to set up an app page
 * @requires jQuery, LAB.js
 * @param {Object} config - contents to the media location and build_id
 * @param {Object} file_map - file mappings object defining files needed for each site, single page
 * @returns {Object} two helper methods - prepare() and furnish()
 */
lacky = function(config, file_map) {
    var prepare, furnish;
    /**
     * Public function to load dependacies and run fucntions for a specific page
     *
     * @param context {String} either an ID to search for or a CSS selector for jQuery to find
     * @param o {Object} betafarm.page.furnish compatible object
     * @example
     * betafarm.page.furnish()
     * @example
     * betafarm.page.furnish ('myID', {
     *   elm : 'mySelector',
     *   requires : ['js/files/to/load'] (optional),
     *   text : 'location of a JS file containing a localised JS text object (optional)
     *   onload : function() {
     *     alert('called once the contents of required is loaded');
     *    }
     * });
     */
    furnish = function(context,o) {
        var obj, context;
        // if no context is defined we know we're looking at the <body>
        if (!context) { 
            context = document.getElementsByTagName('body')[0];
        } else {
            // checks for a matching ID and falls back to jQuery for non-matches
            context = document.getElementById(context) || $(context);
        }
        // if we sent an object use that otherwise use the one in betafarm.areas
        obj = o || file_map[context.id];
        if (obj) {
            // cache these objects for later re-use
            var req = obj.requires,
                txt = obj.text;
            // set up a custom event that can be called once the locale has been loaded and avoid race-condition
            $(context).bind('locale_loaded', function() {
                // load in the required file and once done call the onload to init it
                if (req && req.length) {
                    $LAB
                    .script(req)
                    .wait(function() {
                        obj.onload();
                    });
                } else {
                    if (typeof obj.onload === 'function') {
                        obj.onload();
                    }
                }
            });
            // load the require localised string file
            if (txt && txt.length) {
                // cascade from a potential local to the default if we get an error
                $.ajax({
                    dataType:'script',
                    url: config.MEDIA_URL + 'js/l10n/en-US/' + txt[0],
                    success:function() {
                        $(context).trigger('locale_loaded');
                    },
                    error:function(data) {
                        $.ajax({
                            url: config.MEDIA_URL + 'js/l10n/' + txt[0],
                            dataType: 'script',
                            success:function() {
                                 $(context).trigger('locale_loaded');
                            }
                        });
                    }
                });
            } else {
                $(context).trigger('locale_loaded'); 
            } 
        }
    };
    /**
     * Public function used to load dependancies and call init functions
     * for common site or UGC code
     *     *
     * @memberOf betafarm.page
     * @param {Object} common
     */
    prepare = function() {
        // i will be 0 indexed
        var common = file_map.common,
            len = common.length - 1;
        console.log(common);
        /**
         * i: the current iteration
         * v: each object in common (above)
         */
        $.each(common, function(i, v) {
            var e = v.elm;
            if ($(e).length) {
                // call furnish with the current DOM reference and object
                furnish(e,v);
            }
            // once we've made it through all common objects call furnish on the page
            if (i === len) {
                furnish();
            }
        });
    }
    return {
        prepare : prepare,
        furnish : furnish
    }

};
