/* This Source Code Form is subject to the terms of the MIT license
 * If a copy of the MIT license was not distributed with this file, you can
 * obtain one at http://www.mozillapopcorn.org/butter-license.txt */

(function () {

/**
 * almond 0.0.3 Copyright (c) 2011, The Dojo Foundation All Rights Reserved.
 * Available via the MIT or new BSD license.
 * see: http://github.com/jrburke/almond for details
 */
/*jslint strict: false, plusplus: false */
/*global setTimeout: false */

var requirejs, require, define;
(function (undef) {

    var defined = {},
        waiting = {},
        aps = [].slice,
        main, req;

    if (typeof define === "function") {
        //If a define is already in play via another AMD loader,
        //do not overwrite.
        return;
    }

    /**
     * Given a relative module name, like ./something, normalize it to
     * a real name that can be mapped to a path.
     * @param {String} name the relative name
     * @param {String} baseName a real name that the name arg is relative
     * to.
     * @returns {String} normalized name
     */
    function normalize(name, baseName) {
        //Adjust any relative paths.
        if (name && name.charAt(0) === ".") {
            //If have a base name, try to normalize against it,
            //otherwise, assume it is a top-level require that will
            //be relative to baseUrl in the end.
            if (baseName) {
                //Convert baseName to array, and lop off the last part,
                //so that . matches that "directory" and not name of the baseName's
                //module. For instance, baseName of "one/two/three", maps to
                //"one/two/three.js", but we want the directory, "one/two" for
                //this normalization.
                baseName = baseName.split("/");
                baseName = baseName.slice(0, baseName.length - 1);

                name = baseName.concat(name.split("/"));

                //start trimDots
                var i, part;
                for (i = 0; (part = name[i]); i++) {
                    if (part === ".") {
                        name.splice(i, 1);
                        i -= 1;
                    } else if (part === "..") {
                        if (i === 1 && (name[2] === '..' || name[0] === '..')) {
                            //End of the line. Keep at least one non-dot
                            //path segment at the front so it can be mapped
                            //correctly to disk. Otherwise, there is likely
                            //no path mapping for a path starting with '..'.
                            //This can still fail, but catches the most reasonable
                            //uses of ..
                            break;
                        } else if (i > 0) {
                            name.splice(i - 1, 2);
                            i -= 2;
                        }
                    }
                }
                //end trimDots

                name = name.join("/");
            }
        }
        return name;
    }

    function makeRequire(relName, forceSync) {
        return function () {
            //A version of a require function that passes a moduleName
            //value for items that may need to
            //look up paths relative to the moduleName
            return req.apply(undef, aps.call(arguments, 0).concat([relName, forceSync]));
        };
    }

    function makeNormalize(relName) {
        return function (name) {
            return normalize(name, relName);
        };
    }

    function makeLoad(depName) {
        return function (value) {
            defined[depName] = value;
        };
    }

    function callDep(name) {
        if (waiting.hasOwnProperty(name)) {
            var args = waiting[name];
            delete waiting[name];
            main.apply(undef, args);
        }
        return defined[name];
    }

    /**
     * Makes a name map, normalizing the name, and using a plugin
     * for normalization if necessary. Grabs a ref to plugin
     * too, as an optimization.
     */
    function makeMap(name, relName) {
        var prefix, plugin,
            index = name.indexOf('!');

        if (index !== -1) {
            prefix = normalize(name.slice(0, index), relName);
            name = name.slice(index + 1);
            plugin = callDep(prefix);

            //Normalize according
            if (plugin && plugin.normalize) {
                name = plugin.normalize(name, makeNormalize(relName));
            } else {
                name = normalize(name, relName);
            }
        } else {
            name = normalize(name, relName);
        }

        //Using ridiculous property names for space reasons
        return {
            f: prefix ? prefix + '!' + name : name, //fullName
            n: name,
            p: plugin
        };
    }

    main = function (name, deps, callback, relName) {
        var args = [],
            usingExports,
            cjsModule, depName, i, ret, map;

        //Use name if no relName
        if (!relName) {
            relName = name;
        }

        //Call the callback to define the module, if necessary.
        if (typeof callback === 'function') {

            //Default to require, exports, module if no deps if
            //the factory arg has any arguments specified.
            if (!deps.length && callback.length) {
                deps = ['require', 'exports', 'module'];
            }

            //Pull out the defined dependencies and pass the ordered
            //values to the callback.
            for (i = 0; i < deps.length; i++) {
                map = makeMap(deps[i], relName);
                depName = map.f;

                //Fast path CommonJS standard dependencies.
                if (depName === "require") {
                    args[i] = makeRequire(name);
                } else if (depName === "exports") {
                    //CommonJS module spec 1.1
                    args[i] = defined[name] = {};
                    usingExports = true;
                } else if (depName === "module") {
                    //CommonJS module spec 1.1
                    cjsModule = args[i] = {
                        id: name,
                        uri: '',
                        exports: defined[name]
                    };
                } else if (defined.hasOwnProperty(depName) || waiting.hasOwnProperty(depName)) {
                    args[i] = callDep(depName);
                } else if (map.p) {
                    map.p.load(map.n, makeRequire(relName, true), makeLoad(depName), {});
                    args[i] = defined[depName];
                } else {
                    throw name + ' missing ' + depName;
                }
            }

            ret = callback.apply(defined[name], args);

            if (name) {
                //If setting exports via "module" is in play,
                //favor that over return value and exports. After that,
                //favor a non-undefined return value over exports use.
                if (cjsModule && cjsModule.exports !== undef) {
                    defined[name] = cjsModule.exports;
                } else if (!usingExports) {
                    //Use the return value from the function.
                    defined[name] = ret;
                }
            }
        } else if (name) {
            //May just be an object definition for the module. Only
            //worry about defining if have a module name.
            defined[name] = callback;
        }
    };

    requirejs = req = function (deps, callback, relName, forceSync) {
        if (typeof deps === "string") {

            //Just return the module wanted. In this scenario, the
            //deps arg is the module name, and second arg (if passed)
            //is just the relName.
            //Normalize module name, if it contains . or ..
            return callDep(makeMap(deps, callback).f);
        } else if (!deps.splice) {
            //deps is a config object, not an array.
            //Drop the config stuff on the ground.
            if (callback.splice) {
                //callback is an array, which means it is a dependency list.
                //Adjust args if there are dependencies
                deps = callback;
                callback = arguments[2];
            } else {
                deps = [];
            }
        }

        //Simulate async callback;
        if (forceSync) {
            main(undef, deps, callback, relName);
        } else {
            setTimeout(function () {
                main(undef, deps, callback, relName);
            }, 15);
        }

        return req;
    };

    /**
     * Just drops the config on the floor, but returns req in case
     * the config return value is used.
     */
    req.config = function () {
        return req;
    };

    /**
     * Export require as a global, but only if it does not already exist.
     */
    if (!require) {
        require = req;
    }

    define = function (name, deps, callback) {

        //This module may not have dependencies
        if (!deps.splice) {
            //deps is not an array, so probably means
            //an object literal or factory function for
            //the value. Adjust args.
            callback = deps;
            deps = [];
        }

        if (define.unordered) {
            waiting[name] = [name, deps, callback];
        } else {
            main(name, deps, callback);
        }
    };

    define.amd = {
        jQuery: true
    };
}());

define("../tools/almond", function(){});

/*! This Source Code Form is subject to the terms of the MIT license
 * If a copy of the MIT license was not distributed with this file, you can
 * obtain one at http://www.mozillapopcorn.org/butter-license.txt */

/*jshint white: false, strict: false, plusplus: false, evil: true,
  onevar: false, nomen: false */
/*global require: false, document: false, console: false, window: false,
  setTimeout: false */

/**
 * In the source case, use document.write to write out the require tag,
 * and load all moduels as distinct scripts for debugging. After a build,
 * all the modules are inlined, so will not use the document.write path.
 * Use has() testing module, since the requirejs optimizer will convert
 * the has test to false, and minification will strip the false code
 * branch. http://requirejs.org/docs/optimization.html#hasjs
 */
(function () {
    // Stub for has function.
    function has() {
        return true;
    }

    var Butter = function() {
      if ( !Butter.__waiting ) {
        Butter.__waiting = [];
      } //if
      Butter.__waiting.push( arguments );
    };

    if ( !window.Butter ) {
      window.Butter = Butter;
    } //if

    if ( false ) {
        // Get the location of the butter source.
        // The last script tag should be the butter source
        // tag since in dev, it will be a blocking script tag,
        // so latest tag is the one for this script.
        var scripts = document.getElementsByTagName( 'script' ),
        path = scripts[scripts.length - 1].src;
        path = path.split( '/' );
        path.pop();
        path = path.join( '/' ) + '/';

        if ( !window.require ) {
          document.write( '<script data-main="' + path + 'config" data-butter-exclude="true" src="' + path + '../external/require/require.js"></' + 'script>' );
        } //if
    }

}());

define("butter", function(){});

/* This Source Code Form is subject to the terms of the MIT license
 * If a copy of the MIT license was not distributed with this file, you can
 * obtain one at http://www.mozillapopcorn.org/butter-license.txt */

define('core/eventmanager',[], function(){

  /**
   * EventManagerWrapper - an event queue wrapper
   *
   * Takes an object `object` and extends it with methods necessary to
   * allow object to become an event source.  Other objects can register
   * event listeners with an event source, and have their callback invoked
   * when an event occurs.  Event sources can also be used to dispatch
   * events to registered listeners.
   *
   * To create an event source, pass an object to EventManagerWrapper:
   *
   *    var o = new SomeObject();
   *    EventManagerWrapper( someObject );
   *    o.listen( "some-event", function(){...} );
   *    ...
   *    o.dispatch( "some-event", data );
   *
   * By default, all event dispatching is done asynchronously, meaning
   * calls to dispatch() return immediately, and callbacks are executed
   * later.  It is also possible to force a synchronous, blocking call
   * to dispatch() by passing `true` as the value of the optional third
   * argument:
   *
   *    o.listen( "some-event", function handler(){...} );
   *    o.dispatch( "some-event", data, true );
   *    // the handler function will have executed by this point...
   *
   * Event source objects wrapped with EventManagerWrapper have the
   * following methods attached:
   *
   * 1. object.listen( eventName, listener )
   *
   *    eventName [String] - the name of an event to listen for
   *    listener  [Function] - a callback function to execute
   *
   *    Register a new listener with the object.  The listener callback
   *    should accept an argument `e`, which is an event containing:
   *    type [String], target [Object], and data [Object].
   *
   * 2. object.unlisten( eventName, listener )
   *
   *    eventName [String] - the name of an event
   *    listener  [Function] - the callback previously registered or null
   *
   *    Unregister an existing listener, or remove all listeners for a given
   *    event name.  The listener callback should be the one you used in
   *    a previous call to listen.  If you supply no listener argument, all
   *    listeners for the `eventName` event will be removed.
   *
   * 3. object.dispatch( eventName, eventData, [optional] synchronous=false )
   *
   *    eventName [String] - the name of an event to dispatch
   *    eventData [Object] - an object to attach to the event's `data` property
   *    synchronous [Boolean] - an optional argument indicating that the callback
   *                            should be fired synchronously with dispatch(). By
   *                            default this is `false` and done asynchronously.
   *
   *    Dispatch takes an `eventName` and creates a new event object, using
   *    `eventData` as its data property.  It then invokes any and all listeners
   *    which were previously registered with `listen`.  Depending on the presence/
   *    value of `synchronous`, this is either done synchronously or asynchronously.
   *
   * 4. object.chain( eventManagerWrappedObject, events )
   *
   *    eventManagerWrappedObject [Object] - an object wrapped by EventManagerWrapper
   *    events [Array] - an array of event names [String]
   *
   *    Chain allows the events of one event source to be chained to another,
   *    such that dispatching an event through one will also cause it to invoke
   *    listeners on the other.  This is a form of event bubbling.
   *
   * 5. object.unchain( eventManagerWrappedObject, events )
   *
   *    eventManagerWrappedObject [Object] - an object wrapped by EventManagerWrapper
   *    events [Array] - an array of event names [String]
   *
   *    Unchain allows one event source to be unchained from from another,
   *    which was previously chained using `chain`.
   **/

  /**
   * Static, shared functions for all event source wrapped objects.
   **/
  function __isWrapped( object ){
    return object.listen && object.unlisten;
  }

  function __chain( a, b, events ){
    if( !__isWrapped(b) ){
      throw "Error: Object is not a valid event source: " + b;
    }

    var i = events.length;
    while( i-- ){
      b.listen( events[ i ], a.dispatch );
    }
  }

  function __unchain( a, b, events ){
    if( !__isWrapped(b) ){
      throw "Error: Object is not a valid event source: " + b;
    }

    var i = events.length;
    while( i-- ){
      b.unlisten( events[ i ], a.dispatch );
    }
  }

  function __invoke( eventName, listeners, data ){
    var these, i;

    if( listeners[ eventName ] ){
      these = listeners[ eventName ].slice();
      i = these.length;
      while( i-- ){
        these[ i ]( data );
      }
    }
  }

  function __dispatch( target, namespace, eventName, eventData, listeners, sync ){
    var customEvent, e, namespacedEventName;

    if( typeof( eventName ) === "object" ){
      e = {
        type: eventName.type,
        target: eventName.target,
        data: eventName.data
      };
      eventName = e.type;
    } else {
      e = {
        type: eventName + "",
        target: target,
        data: eventData
      };
    }

    namespacedEventName = namespace + eventName;

    // XXXhumph - Force synchronous code path until we test more
    // https://webmademovies.lighthouseapp.com/projects/65733/tickets/1130
    sync = true;

    if ( sync ){
      __invoke( namespacedEventName, listeners, e );
    } else /* async */ {
      customEvent = document.createEvent( "CustomEvent" );
      customEvent.initCustomEvent( namespacedEventName, false, false, e );
      document.dispatchEvent( customEvent );
    }
  }

  function __listen( o, namespace, eventName, listener, listeners, handler ){
    var i, namespacedEventName;

    if( typeof( eventName ) === "object" ){
      for( i in eventName ){
        if( eventName.hasOwnProperty( i ) ){
          o.listen( i, eventName[ i ] );
        }
      }
    } else {
      namespacedEventName = namespace + eventName;

      if( !listeners[ namespacedEventName ] ){
        listeners[ namespacedEventName ] = [];
        document.addEventListener( namespacedEventName, function( e ){
          handler( namespacedEventName, e );
        }, false);
      }
      listeners[ namespacedEventName ].push( listener );
    }
  }

  function __unlisten( o, namespace, eventName, listener, listeners, handler ){
    var these, idx, i,
        namespacedEventName = namespace + eventName;

    if( typeof( eventName ) === "object" ){
      for( i in eventName ){
        if( eventName.hasOwnProperty( i ) ){
          o.unlisten( i, eventName[ i ] );
        }
      }
    } else {
      these = listeners[ namespacedEventName ];
      if ( !these ){
        return;
      }

      if ( listener ){
        idx = these.indexOf( listener );
        if ( idx > -1 ){
          these.splice( idx, 1 );
        }
      }

      if ( !listener || these.length === 0 ){
        delete listeners[ namespacedEventName ];

        document.removeEventListener( namespacedEventName, function( e ){
          handler( namespacedEventName, e );
        }, false);
      }
    }
  }

  var __seed = Date.now();

  /**
   * EventManagerWrapper objects maintain a few internal items.
   * First, a list of listeners is kept for this object's events.
   * Second, all event names are namespaced so there is no
   * leakage into other event sources.  Third, an event handler
   * is created, which has access to the appropriate listeners.
   **/
  function EventManagerWrapper( object ){

    if ( !object || __isWrapped( object) ){
      return;
    }

    var
        // A list of listeners, keyed by namespaced event name.
        _listeners = {},

        // A unique namespace for events to avoid collisions. An
        // event name "event" with namespace "butter-1336504666771:"
        // would become "butter-1336504666771:event".
        _namespace = "butter-" + __seed++ + ":",

        // An event handler used to invoke listeners, with scope
        // such that it can get at *this* object's listeners.
        _handler = function( eventName, domEvent ){
          __invoke( eventName, _listeners, domEvent.detail );
        };

    // Thin wrapper around calls to static functions

    object.chain = function( eventManagerWrappedObject , events ){
      __chain( this, eventManagerWrappedObject, events );
    };

    object.unchain = function( eventManagerWrappedObject, events ){
      __unchain( this, eventManagerWrappedObject, events );
    };

    object.dispatch = function( eventName, eventData, sync ){
      __dispatch( this, _namespace, eventName, eventData, _listeners, !!sync );
    };

    object.listen = function( eventName, listener ){
      __listen( this, _namespace, eventName , listener, _listeners, _handler );
    };

    object.unlisten = function( eventName, listener ){
      __unlisten( this, _namespace, eventName, listener, _listeners, _handler );
    };

    return object;
  }

  return EventManagerWrapper;

});

/* This Source Code Form is subject to the terms of the MIT license
 * If a copy of the MIT license was not distributed with this file, you can
 * obtain one at http://www.mozillapopcorn.org/butter-license.txt */

(function( undefined ) {

  // By default, logging is off.
  var __debug = false;

  /**
   * Module: Logger
   *
   * Supplies customized logging functionality to Butter.
   */
  define('core/logger',[], function() {

    /**
     * Class: Logger
     *
     * Controls logging for a specific object instance.
     *
     * @param {String} name: Name of the object to report in the log.
     */
    function Logger( name ) {

      /**
       * Member: log
       *
       * Logs a message to the console prefixed by the given name.
       *
       * @param {String} message: Contents of the log message
       */
      this.log = function( message ) {
        if ( __debug ) {
          console.log( "[" + name + "] " + message );
        }
      };

      /**
       * Member: error
       *
       * Throws an error with the given message prefixed by the given name.
       *
       * @param {String} message: Contents of the error
       * @throws: Obligatory, since this is an error
       */
      this.error = function( message ) {
        if ( __debug ) {
          throw new Error( "[" + name + "] " + message );
        }
      };

    }

    /**
     * Class Function: enabled
     *
     * Whether the logger is enabled or not.
     *
     * @param {Boolean} value: State of the logger.
     */
    Logger.enabled = function( value ) {
      if ( value !== undefined ) {
        __debug = !!value;
      }
      return __debug;
    };

    return Logger;
  });

}());

/* This Source Code Form is subject to the terms of the MIT license
 * If a copy of the MIT license was not distributed with this file, you can
 * obtain one at http://www.mozillapopcorn.org/butter-license.txt */

(function( undefined ) {

  /**
   * Variables allowed in config files.  Variables take the form:
   *
   * "foo": "value",
   * "bar": "{{foo}}"
   *
   * The name of the variable is enclosed in {{..}} when used.
   * A defaultValue can be specified as well as a validate()
   * function, to validate/clean values when being set.
   */
  var __variables = {

    // The base-dir prefix used in paths, often something like ../
    "baseDir": {
      name: "{{baseDir}}",
      defaultValue: "./",
      validate: function( value ){
        // Make sure value ends in a trailing /
        return value.replace( /\/?$/, '/' );
      }
    }

  };

  /**
   * Validates any variable value being set, for example,
   * making sure paths end in '/'.
   */
  function __validateVariable( property, value, config ){
    var variable = __variables[ property ];

    if( !( variable && variable.validate ) ){
      return value;
    }

    return variable.validate( value );
  }

  /**
   * Module: Config
   *
   * Manages configuration info for the app.
   */
  define('core/config',[], function() {

    /**
     * Class: Configuration
     *
     * Manages access to config properties, doing variable substitution.
     *
     * @param {Object} configObject: A parsed config object, see config.parse().
     * @throws config is not a parsed object (e.g., if string is passed).
     */
    function Configuration( configObject ) {

      // Constructor should be called by Config.parse()
      if (typeof configObject !== "object"){
        throw "Config Error: expected parsed config object";
      }

      // Cache the config object
      var _config = configObject,
          _merged = [];

      // Find the first config that has a given property, starting
      // with the most recently merged Configuration (if any) and
      // ending with our internal _config object.
      function _findConfig( property ){
        var i = _merged.length;
        while( i-- ){
          if( _merged[ i ].value( property ) !== undefined ){
            return _merged[ i ];
          }
        }
        return _config;
      }

      /**
       * Replace any variable {{foo}} with the value of "foo" from the config.
       * If value is a branch of config, descend into it and replace values.
       */
      function _replaceVariable( value, config ){
        if( value === undefined ){
          return value;
        }

        var newValue = value,
            variable,
            configValue,
            substitution,
            overrideConfig;

        for( var variableName in __variables ){
          if( __variables.hasOwnProperty( variableName ) ){
            variable = __variables[ variableName ];

            // Find the right config override for this value
            // (if any) or use the one in our internal _config
            overrideConfig = _findConfig( variableName );
            configValue = overrideConfig instanceof Configuration ?
              overrideConfig.value( variableName ) :
              overrideConfig[ variableName ];

            substitution = configValue ? configValue : variable.defaultValue;
            newValue = newValue.replace ?
              newValue.replace( variable.name, substitution, "g" ) :
              newValue;
          }
        }

        return newValue;
      }

      function _replaceVariableBranch( property, config ){
        if( property === undefined ){
          return property;
        }

        for( var prop in property ){
          if( property.hasOwnProperty( prop ) ){
            if( typeof property[ prop ] === "object" ){
              property[ prop ] = _replaceVariableBranch( property[ prop ], config );
            } else {
              property[ prop ] = _replaceVariable( property[ prop ], config );
            }
          }
        }

        return property;
      }

      /**
       * Member: value
       *
       * Gets or overrides the value of a config property, doing
       * variable replacement as needed. If only one argument is passed,
       * the name of a property, the value is returned. If two arguments
       * are passed, the second is used in order to override the property's
       * value. If a known variable is overriden, its validate() method
       * is called (if any). The value is returned in both cases.
       *
       * @param {String} property: The config property to get.
       * @param {Object} newValue: [Optional] A new value to use.
       */
      this.value = function( property, newValue ){
        var config = _findConfig( property );

        if( config instanceof Configuration ){
          return config.value( property, newValue );
        } else {
          if( newValue !== undefined ){
            config[ property ] = __validateVariable( property, newValue, config );
          }

          // If we're giving back a property branch, replace values deep before
          // handing it back to the user.
          if( typeof config[ property ] === "object" ){
            return _replaceVariableBranch( config[ property ], config );
          } else {
            return _replaceVariable( config[ property ], config );
          }
        }
      };

      this.merge = function( configuration ){
        _merged.push( configuration );
      };
    }

    /**
     * Class: Config
     *
     * Manages creation of Configuration objects
     */
    var Config = {

      /**
       * Member: parse
       *
       * Parses a JSON config string, creating a Configuration object.
       *
       * @param {String} configJSON: The config's JSON string.
       * @throws JSON is malformed or otherwise can't be parsed.
       */
      parse: function( configJSON ){
        var config;
        try {
          config = JSON.parse( configJSON );
          return new Configuration( config );
        } catch( e ){
          throw "Config.parse Error: unable to parse config string. Error was: " + e.message;
        }
      }

    };

    return Config;
  });

}());

/* This Source Code Form is subject to the terms of the MIT license
 * If a copy of the MIT license was not distributed with this file, you can
 * obtain one at http://www.mozillapopcorn.org/butter-license.txt */

define('util/dragndrop',[], function(){

  var SCROLL_INTERVAL = 16,
      DEFAULT_SCROLL_AMOUNT = 10,
      SCROLL_WINDOW = 20,
      MAXIMUM_Z_INDEX = 2147483647,
      MIN_WIDTH = 15;

  var __droppables = [],
      __mouseDown = false,
      __selectedDraggables = [],
      __mousePos = [ 0, 0 ],
      __mouseLast = [ 0, 0 ],
      __scroll = false,
      __helpers = [];

  // for what seems like a bug in chrome. :/
  // dataTransfer.getData seems to report nothing
  var __currentDraggingElement;

  var __nullRect = {
    top: 0,
    left: 0,
    bottom: 0,
    right: 0
  };

  function updateTimeout(){
    __scroll = false;
    if( __mouseDown ){
      for( var i = __selectedDraggables.length - 1; i >= 0; --i ){
        __selectedDraggables[ i ].update();
      } //for
      window.setTimeout( updateTimeout, SCROLL_INTERVAL );
    } //if
  }

  function onDragged( e ){
    __mouseLast[ 0 ] = __mousePos[ 0 ];
    __mouseLast[ 1 ] = __mousePos[ 1 ];
    __mousePos = [ e.clientX, e.clientY ];

    var remembers = [],
        droppable,
        remember,
        i, j;

    if( __mouseDown ){
      for( i = __selectedDraggables.length - 1; i >= 0; --i ){
        remembers.push( __selectedDraggables[ i ] );
      } //for
    }else{
      var selectedDraggable;
      __mouseDown = true;
      window.setTimeout( updateTimeout, SCROLL_INTERVAL );

      for( i = __selectedDraggables.length - 1; i >= 0; --i ){
        selectedDraggable = __selectedDraggables[ i ];
        selectedDraggable.start( e );
        remembers.push( __selectedDraggables[ i ] );
      } //for
    } //if

    for( i = remembers.length - 1; i >= 0; --i ){
      remember = remembers[ i ];
      for( j = __droppables.length - 1; j >= 0; --j ){
        droppable = __droppables[ j ];
        if( !droppable.element.id ||
            remember.element.id === droppable.element.id ||
            !droppable.drag( remember.element.getBoundingClientRect() ) ){
          droppable.forget( remember );
        }else{
          droppable.remember( remember );
        } //if
      } //for
    } //for
  }

  function onMouseUp( e ){
    __mouseDown = false;
    window.removeEventListener( "mousemove", onDragged, false );

    var selectedDraggable;

    for( var i = __selectedDraggables.length - 1; i >= 0; --i ){
      selectedDraggable = __selectedDraggables[ i ];
      if( selectedDraggable.dragging ){
        selectedDraggable.stop();
      } //if
    } //for
  }

  function onMouseDown( e ){
    if( e.which !== 1 ){
      return;
    }
    e.preventDefault();
    e.stopPropagation();
    window.addEventListener( "mousemove", onDragged, false );
    window.addEventListener( "mouseup", onMouseUp, false );
  }

  function getPaddingRect( element ){
    var style = getComputedStyle( element ),
          top = style.getPropertyValue( "padding-top" ),
          left = style.getPropertyValue( "padding-left" ),
          bottom = style.getPropertyValue( "padding-bottom" ),
          right = style.getPropertyValue( "padding-right" );

      return {
        top: Number(top.substring( 0, top.indexOf( "px" ) ) ),
        left: Number(left.substring( 0, left.indexOf( "px" ) ) ),
        bottom: Number(bottom.substring( 0, bottom.indexOf( "px" ) ) ),
        right: Number(right.substring( 0, right.indexOf( "px" ) ) )
      };
  }

  function __getWindowRect(){
    return {
      top: 0,
      left: 0,
      right: window.innerWidth,
      bottom: window.innerHeight
    };
  }

  function checkParent ( parent, child ) {
    var parentNode = child.parentNode;
    while( parentNode ) {
      if ( parentNode === parent ) {
        return true;
      }
      parentNode = parentNode.parentNode;
    }
    return false;
  }

  function getHighestZIndex ( element ) {
    var z = getComputedStyle( element ).zIndex;
    if ( isNaN( z ) ) {
      z = 0;
      var parentNode = element.parentNode;
      while ( parentNode && [ window, document ].indexOf( parentNode ) === -1 ) {
        var style = getComputedStyle( parentNode );
        if ( style ) {
          var nextZ = style.zIndex;
          if ( isNaN( nextZ ) && nextZ > z ) {
            z = nextZ;
          }
        }
        parentNode = parentNode.parentNode;
      }
    }
    
  }

  function __sortDroppables(){
    __droppables = __droppables.sort( function ( a, b ) {

      var elementA = a.element,
          elementB = b.element,
          zA = getHighestZIndex( elementA ),
          zB = getHighestZIndex( elementB );

      if ( checkParent( elementA, elementB ) ) {
        return -1;
      }
      else if ( checkParent( elementB, elementA ) ) {
        return 1;
      }

      return zA - zB;
    });
  }

  function Resizable( element, options ){
    var _leftHandle = document.createElement( "div" ),
        _rightHandle = document.createElement( "div" ),
        _onStart = options.start || function(){},
        _onStop = options.stop || function(){},
        _updateInterval = -1,
        _scroll = options.scroll,
        _scrollRect,
        _elementRect;

    _leftHandle.className = "handle left-handle";
    _rightHandle.className = "handle right-handle";

    element.appendChild( _leftHandle );
    element.appendChild( _rightHandle );

    function onLeftMouseDown( e ){
      e.stopPropagation();

      var originalRect = element.getBoundingClientRect(),
          originalPosition = element.offsetLeft,
          originalWidth = element.offsetWidth,
          mouseDownPosition = e.clientX,
          mousePosition,
          mouseOffset;

      function update(){

        var diff = mousePosition - mouseDownPosition,
            newX = originalPosition + diff,
            newW = originalWidth - diff;

        if( newW < MIN_WIDTH ){
          return;
        }

        if( _scroll && _scroll.scrollLeft > 0 ){
          if( originalRect.left + diff < _scrollRect.left - SCROLL_WINDOW ){
            _scroll.scrollLeft -= DEFAULT_SCROLL_AMOUNT;
            newX -= DEFAULT_SCROLL_AMOUNT;
            newW += DEFAULT_SCROLL_AMOUNT;
            mouseDownPosition += DEFAULT_SCROLL_AMOUNT;
          }
        }

        if( newX < 0 ){
          newW += newX;
          newX = 0;
        }

        element.style.left = newX + "px";
        element.style.width = newW + "px";
        _elementRect = element.getBoundingClientRect();
      }

      function onMouseUp( e ){
        window.removeEventListener( "mousemove", onMouseMove, false );
        window.removeEventListener( "mouseup", onMouseUp, false );
        clearInterval( _updateInterval );
        _updateInterval = -1;
        _onStop();
      }

      function onMouseMove( e ){
        mousePosition = e.clientX;
        if( _updateInterval === -1 ){
          _updateInterval = setInterval( update, SCROLL_INTERVAL );
          _onStart();
        }
      }

      _elementRect = element.getBoundingClientRect();
      mouseOffset = e.clientX - _elementRect.left;
      _scrollRect = _scroll.getBoundingClientRect();

      window.addEventListener( "mousemove", onMouseMove, false );
      window.addEventListener( "mouseup", onMouseUp, false );
    }

    function onRightMouseDown( e ){
      e.stopPropagation();

      var originalPosition = element.offsetLeft,
          originalWidth = element.offsetWidth,
          mouseDownPosition = e.clientX,
          mousePosition,
          mouseOffset;

      function update(){
        var diff = mousePosition - mouseDownPosition,
            newW = originalWidth + diff;

        if( newW < MIN_WIDTH ){
          return;
        }

        if( _scroll && _scroll.scrollLeft < _scroll.scrollWidth - _scrollRect.width ){
          if( mousePosition > _scrollRect.right + SCROLL_WINDOW ){
            _scroll.scrollLeft += DEFAULT_SCROLL_AMOUNT;
            mouseDownPosition -= DEFAULT_SCROLL_AMOUNT;
          }
        }

        if( newW + originalPosition > element.offsetParent.offsetWidth ){
          newW = element.offsetParent.offsetWidth - originalPosition;
        }

        element.style.width = newW + "px";
        _elementRect = element.getBoundingClientRect();
      }

      function onMouseUp( e ){
        window.removeEventListener( "mousemove", onMouseMove, false );
        window.removeEventListener( "mouseup", onMouseUp, false );
        clearInterval( _updateInterval );
        _updateInterval = -1;
        _onStop();
      }

      function onMouseMove( e ){
        mousePosition = e.clientX;
        if( _updateInterval === -1 ){
          _updateInterval = setInterval( update, SCROLL_INTERVAL );
          _onStart();
        }
      }

      _elementRect = element.getBoundingClientRect();
      if( _scroll ){
        _scrollRect = _scroll.getBoundingClientRect();
      }
      mouseOffset = e.clientX - _elementRect.left;

      window.addEventListener( "mousemove", onMouseMove, false );
      window.addEventListener( "mouseup", onMouseUp, false );
    }

    _leftHandle.addEventListener( "mousedown", onLeftMouseDown, false );
    _rightHandle.addEventListener( "mousedown", onRightMouseDown, false );

    return {
      destroy: function(){
        _leftHandle.removeEventListener( "mousedown", onLeftMouseDown, false );
        _rightHandle.removeEventListener( "mousedown", onRightMouseDown, false );
        element.removeChild( _leftHandle );
        element.removeChild( _rightHandle );
      }
    };
  }

  function Helper( element, options ){
    var _image = options.image,
        _onStart = options.start || function(){},
        _onStop = options.stop || function(){},
        _id = __helpers.length;

    __helpers[ _id ] = element;

    element.setAttribute( "draggable", true );

    element.addEventListener( "dragstart", function( e ){
      __currentDraggingElement = element;
      e.dataTransfer.effectAllowed = "all";
      e.dataTransfer.setData( "text", _id );
      if( _image ){
        var img = document.createElement( "img" );
        img.src = _image.src;
        e.dataTransfer.setDragImage( img, img.width / 2, img.height / 2 );
      }
      _onStart();
    });

    element.addEventListener( "dragend", function( e ){
      __currentDraggingElement = null;
      _onStop();
    });

    element.addEventListener( "drop", function( e ){
    });
  }

  function Droppable( element, options ){
    options = options || {};
    var _hoverClass = options.hoverClass,
        _onDrop = options.drop || function(){},
        _onOver = options.over || function(){},
        _onOut = options.out || function(){},
        _droppable = {},
        _draggedElements = {},
        _draggedCount = 0;

    function onDrop( e ) {
      e.preventDefault();
      e.stopPropagation();

      if( _hoverClass ){
        element.classList.remove( _hoverClass );
      }
      var transferData = e.dataTransfer.getData( "text" ),
          helper = __helpers[ transferData ] || __currentDraggingElement;
      if( helper ){
        _onDrop( helper, [ e.clientX, e.clientY ] );
      }
    }

    function onDragOver( e ) {
      e.preventDefault();
      e.stopPropagation();
      e.dataTransfer.dropEffect = "copy";
    }

    function onDragEnter( e ) {
      if( _hoverClass ) {
        element.classList.add( _hoverClass );
      }
      var transferData = e.dataTransfer.getData( "text" ),
          helper = __helpers[ transferData ] || __currentDraggingElement;
      if( helper ){
        _onOver( helper, [ e.clientX, e.clientY ] );
      }
    }

    function onDragLeave( e ) {
      if ( _hoverClass ) {
        element.classList.remove( _hoverClass );
      }
      var transferData = e.dataTransfer.getData( "text" ),
          helper = __helpers[ transferData ] || __currentDraggingElement;
      if( helper ){
        _onOut( helper, [ e.clientX, e.clientY ] );
      }
    }

    element.addEventListener( "drop", onDrop, false );
    element.addEventListener( "dragover", onDragOver, false );
    element.addEventListener( "dragenter", onDragEnter, false );
    element.addEventListener( "dragleave", onDragLeave, false );

    _droppable = {
      element: element,
      remember: function( draggable ){
        if( !_draggedElements[ draggable.element.id ] && !draggable.droppable ){
          _draggedCount++;
          element.classList.add( _hoverClass );
          _draggedElements[ draggable.element.id ] = draggable;
          draggable.droppable = _droppable;
          _onOver( draggable.element );
        } //if
      },
      forget: function( draggable ){
        // we only care to forget if it is currently dragging
        if( _draggedElements[ draggable.element.id ] && draggable.droppable ){
          if( --_draggedCount === 0 ){
            element.classList.remove( _hoverClass );
          } //if
          draggable.droppable = null;
          _onOut( draggable.element );
          delete _draggedElements[ draggable.element.id ];
        } // if
      },
      drop: function( draggable ){
        if( _draggedElements[ draggable.element.id ] ){
          if( --_draggedCount === 0 ){
            element.classList.remove( _hoverClass );
          } //if
          draggable.droppable = null;
          _onDrop( draggable.element, __mousePos );
          delete _draggedElements[ draggable.element.id ];
        } //if
      },
      drag: function( dragElementRect ){
        var rect = element.getBoundingClientRect();

        var maxL = Math.max( dragElementRect.left, rect.left ),
            maxT = Math.max( dragElementRect.top, rect.top ),
            minR = Math.min( dragElementRect.right, rect.right ),
            minB = Math.min( dragElementRect.bottom, rect.bottom );

        if( minR < maxL || minB < maxT ){
          return false;
        }

        var overlapDims = [ minR - maxL, minB - maxT ];

        if( overlapDims[ 0 ] * overlapDims[ 1 ] / 2 > dragElementRect.width * dragElementRect.height / 4 ){

          return true;
        }

        return false;
      },
      destroy: function(){
        var idx = __droppables.indexOf( _droppable );
        if ( idx > -1 ) {
          __droppables.splice( idx, 1 );
        }
        element.removeEventListener( "drop", onDrop, false );
        element.removeEventListener( "dragover", onDragOver, false );
        element.removeEventListener( "dragenter", onDragEnter, false );
        element.removeEventListener( "dragleave", onDragLeave, false );
      }
    };

    __droppables.push( _droppable );
    __sortDroppables();

    return _droppable;
  }

  function Draggable( element, options ){
    options = options || {};

    var _containment = options.containment,
        _scroll = options.scroll,
        _axis = options.axis,
        _revert = options.revert,
        _mouseOffset,
        _element = element,
        _elementRect,
        _scrollRect,
        _offsetParentRect,
        _containmentRect,
        _scrollAmount = options.scrollAmount || DEFAULT_SCROLL_AMOUNT,
        _oldZIndex,
        _onStart = options.start || function(){},
        _onStop = options.stop || function(){ return false; },
        _originalPosition,
        _droppable = null,
        _draggable = {
          destroy: function(){
            element.removeEventListener( "mousedown", onMouseDown, false );
          }
        },
        _dragging = false,
        _containmentPadding = __nullRect;

    if( _containment ){
      _containmentPadding = getPaddingRect( _containment );
    }

    _draggable.updateRects = function(){
      _containmentRect = _containment ? _containment.getBoundingClientRect() : __getWindowRect();
      _offsetParentRect = element.offsetParent ? element.offsetParent.getBoundingClientRect() : _containmentRect;
      _scrollRect = _scroll ? _scroll.getBoundingClientRect() : _containmentRect;
      _elementRect = element.getBoundingClientRect();
    };

    function updatePosition(){

      var x = __mousePos[ 0 ] - _mouseOffset[ 0 ],
          y = __mousePos[ 1 ] - _mouseOffset[ 1 ];

      if( !_axis || _axis.indexOf( "x" ) > -1 ){
        element.style.left = ( x - _offsetParentRect.left ) + "px";
      }

      if( !_axis || _axis.indexOf( "y" ) > -1 ){
        element.style.top = ( y - _offsetParentRect.top ) + "px";
      }

      _elementRect = element.getBoundingClientRect();
    }

    function checkScroll(){
      if( !__scroll ){
        if( _elementRect.right > _scrollRect.right + SCROLL_WINDOW ){
          __scroll = true;
          _scroll.scrollLeft += _scrollAmount;
        }
        else if( _elementRect.left < _scrollRect.left - SCROLL_WINDOW ){
          __scroll = true;
          _scroll.scrollLeft -= _scrollAmount;
        } //if
      } //if
      _draggable.updateRects();
    }

    function checkContainment(){
      var x = _elementRect.left,
          y = _elementRect.top,
          r = x + _elementRect.width,
          b = y + _elementRect.height;

      if( !_axis || _axis.indexOf( "y" ) > -1 ){

        if( y < _containmentRect.top ){
          y = _containmentRect.top;
        }
        else if( b > _containmentRect.bottom ){
          y = _containmentRect.bottom - _elementRect.height;
        }
        //TODO: Scrolling for Y
        element.style.top = ( y - _offsetParentRect.top - _containmentPadding.top ) + "px";
      }

      if( !_axis || _axis.indexOf( "x" ) > -1 ){
        if( r > _scrollRect.right + SCROLL_WINDOW ){
          x = _scrollRect.right + SCROLL_WINDOW - _elementRect.width;
          r = x + _elementRect.width;
        }
        else if( x < _scrollRect.left - SCROLL_WINDOW ){
          x = _scrollRect.left - SCROLL_WINDOW;
          r = x + _elementRect.width;
        }
        if( x < _containmentRect.left ){
          x = _containmentRect.left;
        }
        else if( r > _containmentRect.right ){
          x = _containmentRect.right - _elementRect.width;
        }
        element.style.left = ( x - _offsetParentRect.left - _containmentPadding.left ) + "px";
      }

      _elementRect = element.getBoundingClientRect();
    }

    element.addEventListener( "mousedown", onMouseDown, false );

    _draggable.update = function(){

      updatePosition();
      if( _scroll ){
        checkScroll();
      }
      checkContainment();
    };

    _draggable.start = function( e ){
      _dragging = true;
      _originalPosition = [ element.offsetLeft, element.offsetTop ];
      _draggable.updateRects();
      _mouseOffset = [ e.clientX - _elementRect.left, e.clientY - _elementRect.top ];
      _onStart();
    };

    _draggable.stop = function(){
      _dragging = false;
      _onStop();
      if( !_droppable && _revert ){
        element.style.left = _originalPosition[ 0 ] + "px";
        element.style.top = _originalPosition[ 1 ] + "px";
      } else if ( _droppable ){
        _droppable.drop( _draggable );
      } //if
    };

    Object.defineProperties( _draggable, {
      selected: {
        enumerable: true,
        get: function(){
          for( var i = __selectedDraggables.length - 1; i >= 0; --i ){
            if( __selectedDraggables[ i ].element.id === _element.id ){
              return true;
            } //if
          } //for
          return false;
        },
        set: function( val ){
          if ( val ) {
            _oldZIndex = getComputedStyle( element ).getPropertyValue( "z-index" );
            element.style.zIndex = MAXIMUM_Z_INDEX;
            __selectedDraggables.push( _draggable );
          } else {
            element.style.zIndex = _oldZIndex;
            for( var i = __selectedDraggables.length - 1; i >= 0; --i ){
              if( __selectedDraggables[ i ].element.id === _element.id ){
                __selectedDraggables.splice( i, 1 );
                return;
              } //if
            } //for
          } //if
        }
      },
      dragging: {
        enumerable: true,
        get: function(){
          return _dragging;
        }
      },
      element: {
        enumerable: true,
        get: function(){
          return _element;
        }
      },
      droppable: {
        enumerable: true,
        get: function(){
          return _droppable;
        },
        set: function( val ){
          _droppable = val;
        }
      }
    });

    return _draggable;
  }

  function Sortable( parentElement, options ){

    var _onChange = options.change || function(){},
        _elements = [],
        _instance = {},
        _mouseDownPosition = 0,
        _draggingElement,
        _draggingOriginalPosition,
        _moved,
        _hoverElement,
        _placeHolder,
        _oldZIndex;


    function createPlaceholder( victim ){
      var placeholder = victim.cloneNode( false );
      placeholder.classList.add( "placeholder" );
      parentElement.replaceChild( placeholder, victim );
      return placeholder;
    }

    function positionElement( diff ){
      _draggingElement.style.top = _draggingOriginalPosition - diff + "px";
    }

    function onElementMouseMove( e ){
      if( !_moved ){
        _moved = true;
        _placeHolder = createPlaceholder( _draggingElement );
        parentElement.appendChild( _draggingElement );
        _draggingElement.style.position = "absolute";
        _draggingElement.style.zIndex = MAXIMUM_Z_INDEX;
        positionElement( 0 );
      }
      else{
        var diff = _mouseDownPosition - e.clientY;
        positionElement( diff );
        var dragElementRect = _draggingElement.getBoundingClientRect();
        for( var i=_elements.length - 1; i>=0; --i ){
          var element = _elements[ i ];

          if( element === _draggingElement ){
            continue;
          }

          var rect = element.getBoundingClientRect();

          var maxL = Math.max( dragElementRect.left, rect.left ),
              maxT = Math.max( dragElementRect.top, rect.top ),
              minR = Math.min( dragElementRect.right, rect.right ),
              minB = Math.min( dragElementRect.bottom, rect.bottom );

          if( minR < maxL || minB < maxT ){
            continue;
          }

          var overlapDims = [ minR - maxL, minB - maxT ];

          if( overlapDims[ 0 ] * overlapDims[ 1 ] / 2 > dragElementRect.width * dragElementRect.height / 4 ){
            _hoverElement = element;
            var newPlaceHolder = createPlaceholder( _hoverElement );
            parentElement.replaceChild( _hoverElement, _placeHolder );
            _placeHolder = newPlaceHolder;
            var orderedElements = [],
                childNodes = parentElement.childNodes;
            for( var j=0, l=childNodes.length; j<l; ++j ){
              var child = childNodes[ j ];
              if( child !== _draggingElement ){
                if( child !== _placeHolder ){
                  orderedElements.push( child );
                }
                else{
                  orderedElements.push( _draggingElement );
                }
              }
            }
            _onChange( orderedElements );
          }
        }
      }
    }

    function onElementMouseDown( e ){
      if( e.which !== 1 ){
        return;
      }
      _moved = false;
      _draggingElement = e.target;
      _draggingOriginalPosition = _draggingElement.offsetTop;

      var style = getComputedStyle( _draggingElement );

      _oldZIndex = style.getPropertyValue( "z-index" );
      _mouseDownPosition = e.clientY;

      window.addEventListener( "mouseup", onElementMouseUp, false );
      window.addEventListener( "mousemove", onElementMouseMove, false );
    }

    function onElementMouseUp( e ){
      _draggingElement.style.zIndex = _oldZIndex;
      window.removeEventListener( "mouseup", onElementMouseUp, false );
      window.removeEventListener( "mousemove", onElementMouseMove, false );
      _moved = false;
      if( _placeHolder ){
        _draggingElement.style.zIndex = "";
        _draggingElement.style.position = "";
        _draggingElement.style.top = "";
        parentElement.replaceChild( _draggingElement, _placeHolder );
        _placeHolder = null;
      }
    }

    _instance.addItem = function( item ){
      _elements.push( item );
      item.addEventListener( "mousedown", onElementMouseDown, false );
    };

    _instance.removeItem = function( item ){
      _elements.splice( _elements.indexOf( item ), 1 );
      item.removeEventListener( "mousedown", onElementMouseDown, false );
    };

    return _instance;
  }

  return {
    draggable: Draggable,
    droppable: Droppable,
    helper: Helper,
    resizable: Resizable,
    sortable: Sortable
  };

});


define('ui/position-tracker',[], function(){

  var POLL_INTERVAL = 20;
  
  return function( object, movedCallback ){
    var _rect = {},
        interval;

    interval = setInterval( function(){
      var newPos = object.getBoundingClientRect();
      if( newPos.left !== _rect.left ||
          newPos.right !== _rect.right ||
          newPos.top !== _rect.top ||
          newPos.bottom !== _rect.bottom ){
        _rect = newPos;
        movedCallback( _rect );
      }
    }, POLL_INTERVAL );

    return {
      destroy: function(){
        clearInterval(interval);
      }
    };
  };

});
/* This Source Code Form is subject to the terms of the MIT license
 * If a copy of the MIT license was not distributed with this file, you can
 * obtain one at http://www.mozillapopcorn.org/butter-license.txt */

define('ui/page-element',[ "core/logger", "core/eventmanager", "util/dragndrop", "ui/position-tracker" ],
        function( Logger, EventManagerWrapper, DragNDrop, PositionTracker ) {

  var __nullFunction = function(){};

  return function( element, events, options ){

    var _element = typeof( element ) === "string" ? document.getElementById( element ) : element,
        _highlightElement = document.createElement( "div" ),
        _events = events || {},
        _options = options || {},
        _blinkFunction,
        _positionTracker,
        _droppable,
        _highlighting = false,
        _draggingGlobal = false,
        _this = this;

    EventManagerWrapper( _this );

    _positionTracker = PositionTracker( _element, function( rect ){
      _highlightElement.style.left = rect.left + "px";
      _highlightElement.style.top = rect.top + "px";
      _highlightElement.style.width = rect.width + "px";
      _highlightElement.style.height = rect.height + "px";
      _this.dispatch( "moved", rect );
    });

    this.highlight = function( state ){
      if( state ){
        _this.blink = __nullFunction;
        _highlighting = true;
        _highlightElement.style.visibility = "visible";
        _highlightElement.classList.add( "on" );
        _highlightElement.classList.remove( "blink" );
        _highlightElement.removeEventListener( 'transitionend', onTransitionEnd, false );
        _highlightElement.removeEventListener( 'oTransitionEnd', onTransitionEnd, false );
        _highlightElement.removeEventListener( 'webkitTransitionEnd', onTransitionEnd, false );
      }
      else {
        _this.blink = _blinkFunction;
        _highlighting = false;
        _highlightElement.classList.remove( "on" );
        if ( !_draggingGlobal ) {
          _highlightElement.style.visibility = "hidden";
        }
      }
    };

    window.addEventListener( "dragstart", function( e ) {
      _highlightElement.style.visibility = "visible";
      _draggingGlobal = true;
    }, false );

    window.addEventListener( "dragend", function( e ) {
      if ( !_highlightElement.classList.contains( "blink" ) ) {
        _highlightElement.style.visibility = "hidden";
      }
      _draggingGlobal = false;
    }, false );

    this.destroy = function(){
      _positionTracker.destroy();
      if( _highlightElement.parentNode ){
        _highlightElement.parentNode.removeChild( _highlightElement );
      } //if

      if ( _droppable ) {
        _droppable.destroy();
      }
    }; //destroy

    _highlightElement.className = "butter-highlight ";
    _highlightElement.setAttribute( "data-butter-exclude", "true" );
    if( _options.highlightClass ){
      _highlightElement.className += _options.highlightClass;
    } //if
    _highlightElement.style.visibility = "hidden";

    function onTransitionEnd(){
      _highlightElement.classList.remove( "blink" );
      if ( !_draggingGlobal && !_highlighting ) {
        _highlightElement.style.visibility = "hidden";
      }
      if ( !_highlighting ) {
        _highlightElement.classList.remove( "on" );
        _this.blink = _blinkFunction;
      }
      _highlightElement.removeEventListener( 'transitionend', onTransitionEnd, false );
      _highlightElement.removeEventListener( 'oTransitionEnd', onTransitionEnd, false );
      _highlightElement.removeEventListener( 'webkitTransitionEnd', onTransitionEnd, false );
    }

    this.blink = _blinkFunction = function(){
      _this.blink = __nullFunction;
      _highlightElement.classList.add( "on" );
      setTimeout(function(){
        _highlightElement.classList.add( "blink", "true" );
      }, 0);
      _highlightElement.style.visibility = "visible";
      _highlightElement.addEventListener( 'transitionend', onTransitionEnd, false );
      _highlightElement.addEventListener( 'oTransitionEnd', onTransitionEnd, false );
      _highlightElement.addEventListener( 'webkitTransitionEnd', onTransitionEnd, false );
    }; //blink

    if( _element ){
      document.body.appendChild( _highlightElement );

      _element.setAttribute( "butter-clean", "true" );

      _droppable = DragNDrop.droppable( _highlightElement, {
        over: function( dragElement ){
          if( dragElement.getAttribute( "data-butter-draggable-type" ) !== "plugin" ){
            return;
          }
          _this.highlight( true );
          if( _events.over ){
            _events.over();
          } //if
        }, //over
        out: function( dragElement ){
          if( dragElement.getAttribute( "data-butter-draggable-type" ) !== "plugin" ){
            return;
          }
          _this.highlight( false );
          if( _events.out ){
            _events.out();
          } //if
        }, //out
        drop: function( dragElement ){
          if( dragElement.getAttribute( "data-butter-draggable-type" ) !== "plugin" ){
            return;
          }
          _this.highlight( false );
          if( _events.drop ){
            _events.drop( dragElement );
          } //if
        } //drop
      });

    } //if

    Object.defineProperties( this, {
      element: {
        enumerable: true,
        get: function(){
          return _element;
        }
      }
    });

  }; //Element

});


/* This Source Code Form is subject to the terms of the MIT license
 * If a copy of the MIT license was not distributed with this file, you can
 * obtain one at http://www.mozillapopcorn.org/butter-license.txt */

(function() {
  define('core/target',[ "core/logger", "core/eventmanager", "ui/page-element" ],
          function( Logger, EventManagerWrapper, PageElement ) {

    var __guid = 0;

    var Target = function ( options ) {
      options = options || {};

      var _id = "Target" + __guid++,
          _logger = new Logger( _id ),
          _name = options.name || _id,
          _element = options.element,
          _pageElement,
          _this = this;

      EventManagerWrapper( _this );

      if( typeof( _element ) === "string" ){
        _element = document.getElementById( _element );
      } //if

      if( !_element ){
        _logger.log( "Warning: Target element is null." );
      }
      else {
        _pageElement = new PageElement( _element, {
          drop: function( element ){
            _this.dispatch( "trackeventrequested", {
              element: element,
              target: _this
            });
          }
        },
        {
          highlightClass: "butter-target-highlight"
        });
      } //if

      this.destroy = function () {
        if ( _pageElement ) {
          _pageElement.destroy();
        }
      };

      Object.defineProperties( this, {
        view: {
          enumerable: true,
          get: function(){
            return _pageElement;
          }
        },
        name: {
          enumerable: true,
          get: function(){
            return _name;
          }
        },
        id: {
          enumerable: true,
          get: function(){
            return _id;
          }
        },
        elementID: {
          enumerable: true,
          get: function(){
            if( _element ){
              return _element.id;
            } //if
          }
        },
        element: {
          enumerable: true,
          get: function(){
            return _element;
          }
        },
        isDefault: {
          enumerable: true,
          get: function(){
            if( _element && _element.hasAttribute( "data-butter-default" ) ){
              return true;
            } //if
            return false;
          }
        },
        json: {
          enumerable: true,
          get: function(){
            var elem = "";
            if( _element && _element.id ){
              elem = _element.id;
            } //if
            return {
              id: _id,
              name: _name,
              element: elem
            };
          },
          set: function( importData ){
            if( importData.name ){
              _name = importData.name;
            } //if
            if( importData.element ){
              _element = document.getElementById( importData.element );
            } //if
          }
        }
      });

    }; //Target

    return Target;

  }); //define
}());

/* This Source Code Form is subject to the terms of the MIT license
 * If a copy of the MIT license was not distributed with this file, you can
 * obtain one at http://www.mozillapopcorn.org/butter-license.txt */

define('util/time',[], function(){

  var __timeAccuracy = 3;

  function roundTime( time ){
    return Math.round( time * ( Math.pow( 10, __timeAccuracy ) ) ) / Math.pow( 10, __timeAccuracy );
  } //roundTime

  var utils = {
    roundTime: roundTime
  }; //utils

  Object.defineProperties( utils, {
    timeAccuracy: {
      enumerable: true,
      get: function(){
        return __timeAccuracy;
      },
      set: function( val ){
        __timeAccuracy = val;
      }
    }
  });

  return utils;

});

/* This Source Code Form is subject to the terms of the MIT license
 * If a copy of the MIT license was not distributed with this file, you can
 * obtain one at http://www.mozillapopcorn.org/butter-license.txt */

define('core/views/trackevent-view',[ "core/logger", "core/eventmanager", "util/dragndrop" ], function( Logger, EventManagerWrapper, DragNDrop ){
  
  var __guid = 0;

  return function( trackEvent, type, inputOptions ){

    var _id = "TrackEventView" + __guid++,
        _element = document.createElement( "div" ),
        _zoom = 1,
        _duration = 1,
        _type = type,
        _start = inputOptions.start || 0,
        _end = inputOptions.end || _start + 1,
        _parent,
        _handles,
        _typeElement = document.createElement( "div" ),
        _draggable,
        _resizable,
        _this = this;

    EventManagerWrapper( _this );

    _element.appendChild( _typeElement );

    function toggleHandles( state ){
      _handles[ 0 ].style.visibility = state ? "visible" : "hidden";
      _handles[ 1 ].style.visibility = state ? "visible" : "hidden";
    } //toggleHandles

    function resetContainer(){
      _element.style.left = ( _start / _duration * _zoom ) + "px";
      _element.style.width = ( ( _end - _start ) / _duration * _zoom ) + "px";
    } //resetContainer

    this.setToolTip = function( title ){
      _element.title = title;
    };

    this.update = function( options ){
      options = options || {};
      _element.style.top = "0px";
      if ( !isNaN( options.start ) ) {
        _start = options.start;
      }
      if ( !isNaN( options.end ) ) {
        _end = options.end;
      }
      resetContainer();
    }; //update

    Object.defineProperties( this, {
      trackEvent: {
        enumerable: true,
        get: function(){
          return trackEvent;
        }
      },
      element: {
        enumerable: true,
        get: function(){ return _element; }
      },
      start: {
        enumerable: true,
        get: function(){ return _start; },
        set: function( val ){
          _start = val;
          resetContainer();
        }
      },
      end: {
        enumerable: true,
        get: function(){ return _end; },
        set: function( val ){
          _end = val;
          resetContainer();
        }
      },
      type: {
        enumerable: true,
        get: function(){ return _type; },
        set: function( val ){
          _type = val;
          _typeElement.innerHTML = _type;
          _element.setAttribute( "data-butter-trackevent-type", _type );
        }
      },
      selected: {
        enumerable: true,
        get: function(){ return _draggable.selected; },
        set: function( val ){
          if( val ){
            select();
          }
          else {
            deselect();
          } //if
        }
      },
      zoom: {
        enumerable: true,
        get: function(){
          return _zoom;
        },
        set: function( val ){
          _zoom = val;
          resetContainer();
        }
      },
      duration: {
        enumerable: true,
        get: function(){
          return _element.getBoundingClientRect().width / _zoom;
        },
        set: function( val ){
          resetContainer();
        }
      },
      id: {
        enumerable: true,
        configurable: false,
        get: function(){
          return _id;
        }
      },
      parent: {
        enumerabled: true,
        get: function(){
          return _parent;
        },
        set: function( val ){
          _parent = val;

          if( _draggable ){
            _draggable.destroy();
            _draggable = null;
          }

          if( _resizable ){
            toggleHandles( false );
            _resizable.destroy();
            _resizable = null;
            _handles = null;
          }

          if( _parent ){

            if( _parent.element && _parent.element.parentNode && _parent.element.parentNode.parentNode ){

              _draggable = DragNDrop.draggable( _element, {
                containment: _parent.element.parentNode,
                scroll: _parent.element.parentNode.parentNode,
                start: function(){
                  _this.dispatch( "trackeventdragstarted" );
                },
                stop: function(){
                  _this.dispatch( "trackeventdragstopped" );
                  movedCallback();
                },
                revert: true
              });

              _resizable = DragNDrop.resizable( _element, {
                containment: _parent.element.parentNode,
                scroll: _parent.element.parentNode.parentNode,
                stop: movedCallback
              });

              _element.setAttribute( "data-butter-draggable-type", "trackevent" );
              _element.setAttribute( "data-butter-trackevent-id", trackEvent.id );

              if( !_handles ){
                _handles = _element.querySelectorAll( ".handle" );
                if( _handles && _handles.length === 2 ){
                  _element.addEventListener( "mouseover", function( e ){
                    toggleHandles( true );
                  }, false );
                  _element.addEventListener( "mouseout", function( e ){
                    toggleHandles( false );
                  }, false );
                  toggleHandles( false );
                }
              }

            }

            resetContainer();
          } //if
        } //set
      }
    });

    function movedCallback() {
      _element.style.top = "0px";
      var rect = _element.getClientRects()[ 0 ];
      _start = _element.offsetLeft / _zoom;
      _end = _start + rect.width / _zoom;
      _this.dispatch( "trackeventviewupdated" );
    } //movedCallback

    _element.className = "butter-track-event";
    _this.type = _type;

    _element.id = _id;
    _this.update( inputOptions );

    _element.addEventListener( "mousedown", function ( e ) {
      _this.dispatch( "trackeventmousedown", { originalEvent: e, trackEvent: trackEvent } );
    }, true);
    _element.addEventListener( "mouseup", function ( e ) {
      _this.dispatch( "trackeventmouseup", { originalEvent: e, trackEvent: trackEvent } );
    }, false);
    _element.addEventListener( "mouseover", function ( e ) {
      _this.dispatch( "trackeventmouseover", { originalEvent: e, trackEvent: trackEvent } );
    }, false );
    _element.addEventListener( "mouseout", function ( e ) {
      _this.dispatch( "trackeventmouseout", { originalEvent: e, trackEvent: trackEvent } );
    }, false );

    _element.addEventListener( "dblclick", function ( e ) {
      _this.dispatch( "trackeventdoubleclicked", { originalEvent: e, trackEvent: trackEvent } );
    }, false);

    function select( e ){
      _draggable.selected = true;
      _element.setAttribute( "selected", true );
    } //select

    function deselect( e ) {
      _draggable.selected = false;
      _element.removeAttribute( "selected" );
    } //deselect

  };

});

/* This Source Code Form is subject to the terms of the MIT license
 * If a copy of the MIT license was not distributed with this file, you can
 * obtain one at http://www.mozillapopcorn.org/butter-license.txt */

define('core/views/track-view',[ "core/logger",
          "core/eventmanager",
          "util/dragndrop"
        ],
        function(
          Logger,
          EventManagerWrapper,
          DragNDrop
        ){

  var __guid = 0;

  return function( track ){

    var _id = "TrackView" + __guid++,
        _track = track,
        _this = this,
        _trackEvents = [],
        _trackEventElements = [],
        _element = document.createElement( "div" ),
        _duration = 1,
        _parent,
        _droppable,
        _zoom = 1;

    EventManagerWrapper( _this );

    _element.className = "butter-track";
    _element.id = _id;

    function setupDroppable(){
      _droppable = DragNDrop.droppable( _element, {
        hoverClass: "draggable-hover",
        drop: function( dropped, mousePosition ) {

          var draggableType = dropped.getAttribute( "data-butter-draggable-type" );
          
          var start,
              left,
              trackRect = _element.getBoundingClientRect();

          if( draggableType === "plugin" ){
            left = mousePosition[ 0 ] - trackRect.left;
            start = left / trackRect.width * _duration;
            _this.dispatch( "plugindropped", {
              start: start,
              track: _track,
              type: dropped.getAttribute( "data-butter-plugin-type" )
            });
          }
          else if( draggableType === "trackevent" ) {
            if( dropped.parentNode !== _element ){
              left = dropped.offsetLeft;
              start = left / trackRect.width * _duration;
              _this.dispatch( "trackeventdropped", {
                start: start,
                track: _track,
                trackEvent: dropped.getAttribute( "data-butter-trackevent-id" )
              });
            }
          } //if
        }
      });
    }

    function resetContainer(){
      _element.style.width = ( _duration * _zoom ) + "px";
    } //resetContainer

    Object.defineProperties( this, {
      element: {
        enumerable: true,
        configurable: false,
        get: function(){
          return _element;
        }
      },
      zoom: {
        enumerable: true,
        get: function(){
          return _zoom;
        },
        set: function( val ){
          _zoom = val;
          resetContainer();
          for( var i=0, l=_trackEvents.length; i<l; ++i ){
            _trackEvents[ i ].zoom = _zoom;
          } //for
        }
      },
      duration: {
        enumerable: true,
        get: function(){
          return _duration;
        },
        set: function( val ){
          _duration = val;
          resetContainer();
          for( var i=0, l=_trackEvents.length; i<l; ++i ){
            _trackEvents[ i ].duration = _duration;
          } //for
        }
      },
      parent: {
        enumerable: true,
        get: function(){
          return _parent;
        },
        set: function( val ){
          _parent = val;
          if ( _droppable ) {
            _droppable.destroy();
            _droppable = null;
          }
          if ( _parent ) {
            setupDroppable();
          }
          for( var i=0, l=_trackEvents.length; i<l; ++i ){
            _trackEvents[ i ].parent = _this;
          }
        }
      }
    });

    this.addTrackEvent = function( trackEvent ){
      var trackEventElement = trackEvent.view.element;
      _element.appendChild( trackEventElement );
      _trackEvents.push( trackEvent.view );
      _trackEventElements.push( trackEvent.view.element );
      trackEvent.view.zoom = _zoom;
      trackEvent.view.duration = _duration;
      trackEvent.view.parent = _this;
      _this.chain( trackEvent, [
        "trackeventmousedown",
        "trackeventmouseover",
        "trackeventmouseout"
      ]);
    }; //addTrackEvent

    this.removeTrackEvent = function( trackEvent ){
      var trackEventElement = trackEvent.view.element;
      _element.removeChild( trackEventElement );
      _trackEvents.splice( _trackEvents.indexOf( trackEvent.view ), 1 );
      _trackEventElements.splice( _trackEvents.indexOf( trackEvent.view.element ), 1 );
      trackEvent.view.parent = null;
      _this.unchain( trackEvent, [
        "trackeventmousedown",
        "trackeventmouseover",
        "trackeventmouseout"
      ]);
    }; //removeTrackEvent

  }; //TrackView

});

/* This Source Code Form is subject to the terms of the MIT license
 * If a copy of the MIT license was not distributed with this file, you can
 * obtain one at http://www.mozillapopcorn.org/butter-license.txt */
/*jshint evil:true*/

define('core/popcorn-wrapper',[ "core/logger", "core/eventmanager" ], function( Logger, EventManager ) {

  // regex to determine the type of player we need to use based on the provided url
  var __urlRegex = /(?:http:\/\/www\.|http:\/\/|www\.|\.|^)(youtu|vimeo|soundcloud|baseplayer)/;

      // how long to wait for the status of something in checkTimeoutLoop
  var STATUS_INTERVAL = 100,
      // timeout duration to wait for popcorn players to exist
      PLAYER_WAIT_DURATION = 10000,
      // timeout duration to wait for media to be ready
      MEDIA_WAIT_DURATION = 10000;

  /* The Popcorn-Wrapper wraps various functionality and setup associated with
   * creating, updating, and removing associated data with Popcorn.js.
   */
  return function ( mediaId, options ){

    var _id = mediaId,
        _logger = new Logger( _id + "::PopcornWrapper" ),
        _popcornEvents = options.popcornEvents || {},
        _onPrepare = options.prepare || function(){},
        _onConstructing = options.constructing || function(){},
        _onFail = options.fail || function(){},
        _onPlayerTypeRequired = options.playerTypeRequired || function(){},
        _onTimeout = options.timeout || function(){},
        _popcorn,
        _mediaType,
        _butterEventMap = {},
        _interruptLoad = false,
        _this = this;

    /* Destroy popcorn bindings specfically without touching other discovered
     * settings
     */
    this.unbind = function(){
      try{
        _popcorn.destroy();
        _popcorn = undefined;
      }
      catch( e ){
        _logger.log( "WARNING: Popcorn did NOT get destroyed properly: \n" + e.message + "\n" + e.stack );
      } //try
    };

    /* Setup any handlers that were defined in the options passed into
     * popcorn wrapper. Events such as timeupdate, paused, etc
     */
    function addPopcornHandlers(){
      for( var eventName in _popcornEvents ){
        if( _popcornEvents.hasOwnProperty( eventName ) ) {
          _popcorn.on( eventName, _popcornEvents[ eventName ] );
        }
      } //for
    } //addPopcornHandlers

    // Cancel loading or preparing of media whilst attempting to setup
    this.interruptLoad = function(){
      _interruptLoad = true;
    }; //interrupt

    // Update Popcorn events with data from a butter trackevent
    this.updateEvent = function( trackEvent ){
      var options = trackEvent.popcornOptions,
          butterId = trackEvent.id,
          popcornId = _butterEventMap[ butterId ],
          popcornEvent = null;
      /* ensure that the trackevent actually exists before removal.
      * we remove the trackevent because there is no easy way
      * to ensure what data has changed on any given track. It
      * is easier to remove the old and create a new trackevent with the updated
      * options
      */
      if( _popcorn ){
        if( popcornId && _popcorn.getTrackEvent( popcornId ) ){
          _popcorn.removeTrackEvent( popcornId );
        } //if
        // make sure the plugin is still included
        if( _popcorn[ trackEvent.type ] ){
          // create the trackevent
          _popcorn[ trackEvent.type ]( options );
          // store a local reference to the newly created trackevent
          _butterEventMap[ butterId ] = _popcorn.getLastTrackEventId();

          popcornEvent = _popcorn.getTrackEvent( _butterEventMap[ butterId ] );
          trackEvent.popcornTrackEvent = popcornEvent;

          if( trackEvent.view ){
            if( popcornEvent.toString ){
              trackEvent.view.setToolTip( popcornEvent.toString() );
            }
            else{
              trackEvent.view.setToolTip( JSON.stringify( options ) );
            }
          }
        } //if
      } //if
    }; //updateEvent

    // Destroy a Popcorn trackevent
    this.destroyEvent = function( trackEvent ){
      var butterId = trackEvent.id,
          popcornId = _butterEventMap[ butterId ];

      // ensure the trackevent actually exists before we remove it
      if( _popcorn ){
        if( popcornId && _popcorn.getTrackEvent( popcornId ) ){
          _popcorn.removeTrackEvent( popcornId );
        } //if

        // remove the reference to the trackevent id that we stored in updateEvent
        delete _butterEventMap[ butterId ];
      } //if
    }; //destroyEvent

    /* Create functions for various failure and success cases,
     * generate the Popcorn string and ensures our player is ready
     * before we actually create the Popcorn instance and notify the
     * user.
     */
    this.prepare = function( url, target, popcornOptions, callbacks, scripts ){

      // called when timeout occurs preparing popcorn or the media
      function timeoutWrapper( e ){
        _interruptLoad = true;
        _onTimeout( e );
      }

      // called when there's a serious failure in preparing popcorn
      function failureWrapper( e ){
        _interruptLoad = true;
        _logger.log( e );
        _onFail( e );
      }

      // attempt to grab the first url for a type inspection
      var firstUrl = url;
      if ( typeof( url ) !== "string" ) {
        if ( !url.length ) {
          throw "URL is invalid: empty array or not a string.";
        }
        else {
          firstUrl = url[ 0 ];
        }
      }

      // discover and stash the type of media as dictated by the url
      findMediaType( firstUrl );

      // if there isn't a target, we can't really set anything up, so stop here
      if( !target ){
        _logger.log( "Warning: tried to prepare media with null target." );
        return;
      }

      // only enter this block if popcorn doesn't already exist (call clear() first to destroy it)
      if( !_popcorn ) {
        try {
          // make sure popcorn is setup properly: players, etc
          waitForPopcorn( function(){
            // construct the correct dom infrastructure if required
            constructPlayer( target );
            // generate a function which will create a popcorn instance when entered into the page
            createPopcorn( generatePopcornString( popcornOptions, url, target, null, callbacks, scripts ) );
            // once popcorn is created, attach listeners to it to detect state
            addPopcornHandlers();
            if( _onConstructing ){
              _onConstructing();
            }
            // wait for the media to become available and notify the user, or timeout
            waitForMedia( _onPrepare, timeoutWrapper );
          }, timeoutWrapper );
        }
        catch( e ) {
          // if we've reached here, we have an internal failure in butter or popcorn
          failureWrapper( e );
        }
      }

    };

    /* Determine the type of media that is going to be used
     * based on the specified url
     */
    function findMediaType( url ){
      var regexResult = __urlRegex.exec( url );
      if ( regexResult ) {
        _mediaType = regexResult[ 1 ];
        // our regex only handles youtu ( incase the url looks something like youtu.be )
        if ( _mediaType === "youtu" ) {
          _mediaType = "youtube";
        }
      }
      else {
        // if the regex didn't return anything we know it's an HTML5 source
        _mediaType = "object";
      }
      return _mediaType;
    }

    /* If possible and necessary, reformat the dom to conform to the url type specified
     * for the media. For example, youtube/vimeo players like <div>'s, not <video>'s to
     * dwell in.
     */
    function constructPlayer( target ){
      var targetElement = document.getElementById( target );

      if( _mediaType !== "object" && targetElement ) {
        if( [ "VIDEO", "AUDIO" ].indexOf( targetElement.nodeName ) !== -1 ) {
          var parentNode = targetElement.parentNode,
              newElement = document.createElement( "div" ),
              attributes;

          newElement.id = targetElement.id;
          attributes = targetElement.attributes;
          if( attributes ){
            for( var i = attributes.length - 1; i >= 0; i-- ) {
              var name = attributes[ i ].nodeName;
              newElement.setAttribute( name, targetElement.getAttribute( name ) );
            }
          }
          if( targetElement.className ){
            newElement.className = targetElement.className;
          }
          parentNode.replaceChild( newElement, targetElement );
          newElement.setAttribute( "data-butter", "media" );
        }
      }
    }

    /* Determine which player is needed (usually based on the result of findMediaType)
     * and create a stringified representation of the Popcorn constructor (usually to
     * insert in a script tag).
     */
    var generatePopcornString = this.generatePopcornString = function( popcornOptions, url, target, method, callbacks, scripts, trackEvents ){

      callbacks = callbacks || {};
      scripts = scripts || {};

      var popcornString = "",
          optionString,
          saveOptions,
          i,
          option;

      if ( typeof( url ) !== "string" ) {
        url = JSON.stringify( url );
      }
      else {
        url = "'" + url + "'";
      }

      // prepare popcornOptions as a string
      if ( popcornOptions ) {
        popcornOptions = ", " + JSON.stringify( popcornOptions );
      } else {
        popcornOptions = ", {}";
      }

      // attempt to get the target element, and continue with a warning if a failure occurs
      if( typeof( target ) !== "string" ){
        if( target && target.id ){
          target = target.id;
        }
        else{
          _logger.log( "WARNING: Unexpected non-string Popcorn target: " + target );
        }
      } //if

      // if the media type hasn't been discovered yet, bail, since it's pointless to continue
      if( !_mediaType ){
        throw new Error( "Media type not generated yet. Please specify a url for media objects before generating a popcorn string." );
      }

      if( scripts.init ){
        popcornString += scripts.init + "\n";
      }
      if( callbacks.init ){
        popcornString += callbacks.init + "();\n";
      }

      // special case for basePlayer, since it doesn't require as much of a harness
      if( _mediaType === "baseplayer" ) {
        popcornString +=  "Popcorn.player( 'baseplayer' );\n" +
                          "var popcorn = Popcorn.baseplayer( '#" + target + "' " + popcornOptions + " );\n";
      }
      else{
        // just try to use Popcorn.smart to detect/setup video
        popcornString += "var popcorn = Popcorn.smart( '#" + target + "', " + url + popcornOptions + " );\n";
      }

      if( scripts.beforeEvents ){
        popcornString += scripts.beforeEvents + "\n";
      }
      if( callbacks.beforeEvents ){
        popcornString += callbacks.beforeEvents + "( popcorn );\n";
      }

      // if popcorn was built successfully
      if ( _popcorn ) {

        if ( trackEvents ) {
          for ( i = trackEvents.length - 1; i >= 0; i-- ) {
            popcornOptions = trackEvents[ i ].popcornOptions;
          
            saveOptions = {};
            for ( option in popcornOptions ) {
              if ( popcornOptions.hasOwnProperty( option ) ) {
                if ( popcornOptions[ option ] !== undefined ) {
                  saveOptions[ option ] = popcornOptions[ option ];
                }
              }
            }

            //stringify will throw an error on circular data structures
            try {
              //pretty print with 4 spaces per indent
              optionString = JSON.stringify( saveOptions, null, 4 );
            } catch ( jsonError ) {
              optionString = false;
              _logger.log( "WARNING: Unable to export event options: \n" + jsonError.message );
            }

            if ( optionString ) {
              popcornString += "popcorn." + trackEvents[ i ].type + "(" +
                optionString + ");\n";
            }

          }

        }

      }

      if( scripts.afterEvents ){
        popcornString += scripts.afterEvents + "\n";
      }
      if( callbacks.afterEvents ){
        popcornString += callbacks.afterEvents + "( popcorn );\n";
      }

      // if the `method` var is blank, the user probably just wanted an inline function without an onLoad wrapper
      method = method || "inline";

      // ... otherwise, wrap the function in an onLoad wrapper
      if ( method === "event" ) {
        popcornString = "\ndocument.addEventListener('DOMContentLoaded',function(e){\n" + popcornString;
        popcornString += "\n},false);";
      }
      else {
        popcornString = popcornString + "\n return popcorn;";
      } //if

      return popcornString;
    };

    /* Create a Popcorn instace in the page. Try just running the generated function first (from popcornString)
     * and insert it as a script in the head if that fails.
     */
    function createPopcorn( popcornString ){
      var popcornFunction = new Function( "", popcornString ),
          popcorn = popcornFunction();
      if ( !popcorn ) {
        var popcornScript = document.createElement( "script" );
        popcornScript.innerHTML = popcornString;
        document.head.appendChild( popcornScript );
        popcorn = window.Popcorn.instances[ window.Popcorn.instances.length - 1 ];
      }
      _popcorn = popcorn;
    }

    /* Abstract the problem of waiting for some condition to occur with a timeout. Loop on checkFunction,
     * calling readyCallback when it succeeds, or calling timeoutCallback after timeoutDuration milliseconds.
     */
    function checkTimeoutLoop( checkFunction, readyCallback, timeoutCallback, timeoutDuration ){
      var stop = false,
          ready = false;

      // perform one check
      function doCheck(){
        // if timeout occurred already, bail
        if ( stop ) {
          return;
        }
        // run the check function
        if ( checkFunction() ) {
          // if success, raise the ready flag and call the ready callback
          ready = true;
          readyCallback();
        }
        else {
          // otherwise, prepare for another loop
          setTimeout( doCheck, STATUS_INTERVAL );
        }
      }

      // set a timeout to occur after timeoutDuration milliseconds
      setTimeout(function(){
        // if success hasn't already occured, raise the stop flag and call timeoutCallback
        if ( !ready ) {
          stop = true;
          timeoutCallback();
        }
      }, MEDIA_WAIT_DURATION );

      //init
      doCheck();
    }

    /* Wait for the media to return a sane readyState and duration so we can interact
     * with it (uses checkTimeoutLoop).
     */
    function waitForMedia( readyCallback, timeoutCallback ){
      checkTimeoutLoop(function(){
        return ( _popcorn && /* Make sure _popcorn still exists (e.g., destroy() hasn't been called) */
                 ( _popcorn.media.readyState >= 1 &&
                   _popcorn.duration() > 0
                 )
               );
      }, readyCallback, timeoutCallback, MEDIA_WAIT_DURATION );
    }

    /* Wait for Popcorn to be set up and to have the required players load (uses
     * checkTimeoutLoop).
     */
    function waitForPopcorn( readyCallback, timeoutCallback ){
      if( _mediaType !== "object" ){
        _onPlayerTypeRequired( _mediaType );
        checkTimeoutLoop(function(){
          return ( !!window.Popcorn[ _mediaType ] );
        }, readyCallback, timeoutCallback, PLAYER_WAIT_DURATION );
      }
      else{
        readyCallback();
      }
    }

    // Passthrough to the Popcorn instances play method
    this.play = function(){
      _popcorn.play();
    };

    // Passthrough to the Popcorn instances pause method
    this.pause = function(){
      _popcorn.pause();
    };

    // Wipe the current Popcorn instance and anything it created
    this.clear = function( container ) {
      if( typeof( container ) === "string" ){
        container = document.getElementById( container );
      } //if
      if( !container ){
        _logger.log( "Warning: tried to clear media with null target." );
        return;
      } //if
      if( _popcorn ){
        _this.unbind();
      } //if
      while( container.firstChild ) {
        container.removeChild( container.firstChild );
      } //while
      if ( [ "AUDIO", "VIDEO" ].indexOf( container.nodeName ) > -1 ) {
        container.currentSrc = "";
        container.src = "";
        container.removeAttribute( "src" );
      } //if
    };

    Object.defineProperties( this, {
      volume: {
        enumerable: true,
        set: function( val ){
          if( _popcorn ){
            _popcorn.volume( val );
          } //if
        },
        get: function(){
          if( _popcorn ){
            return _popcorn.volume();
          }
          return false;
        }
      },
      muted: {
        enumerable: true,
        set: function( val ){
          if( _popcorn ){
            if( val ){
              _popcorn.mute();
            }
            else {
              _popcorn.unmute();
            } //if
          } //if
        },
        get: function(){
          if( _popcorn ){
            return _popcorn.muted();
          }
          return false;
        }
      },
      currentTime: {
        enumerable: true,
        set: function( val ){
          if( _popcorn ){
            _popcorn.currentTime( val );
          } //if
        },
        get: function(){
          if( _popcorn ){
            return _popcorn.currentTime();
          }
          return 0;
        }
      },
      duration: {
        enumerable: true,
        get: function(){
          if( _popcorn ){
            return _popcorn.duration();
          } //if
          return 0;
        }
      },
      popcorn: {
        enumerable: true,
        get: function(){
          return _popcorn;
        }
      },
      paused: {
        enumerable: true,
        get: function(){
          if( _popcorn ){
            return _popcorn.paused();
          } //if
          return true;
        },
        set: function( val ){
          if( _popcorn ){
            if( val ){
              _popcorn.pause();
            }
            else {
              _popcorn.play();
            } //if
          } //if
        }
      } //paused
    });

  };

});

define('ui/logo-spinner',[], function(){
  
  return function( parentElement ){

    var outerElement = document.createElement( "div" ),
        innerElement = document.createElement( "div" );

    outerElement.className = "butter-logo-spin-outer";
    innerElement.className = "butter-logo-spin-inner";

    outerElement.appendChild( innerElement );

    if( parentElement ){
      parentElement.appendChild( outerElement );
    }

    return {
      element: outerElement,
      start: function(){
        outerElement.classList.remove( "fade-out" );
        innerElement.classList.add( "active" );
      },
      stop: function( callback ){
        outerElement.classList.add( "fade-out" );
        setTimeout(function(){
          innerElement.classList.remove( "active" );
          if( callback ){
            callback();
          }
        }, 500 );
      }
    };

  };

});
/* This Source Code Form is subject to the terms of the MIT license
 * If a copy of the MIT license was not distributed with this file, you can
 * obtain one at http://www.mozillapopcorn.org/butter-license.txt */

/**
 * Butter Textbox Widget Wrapper
 *
 * A simple input textbox with cross-browser click-to-select functionality.
 * Clicking this textbox will cause the contents to be selected.  The next
 * click will position the cursor.  Getting this to work cross-browser is
 * harder than it should be, especially on Chrome.  See:
 * http://code.google.com/p/chromium/issues/detail?id=4505
 *
 * The textbox manages listeners carefully in order to have mouse clicks
 * do what the user expects.  On creation, `focus` and `mouseup` handlers
 * are added to the element.  When the first `focus` event happens, the
 * contents of the element are selected, and the `focus` handler is removed,
 * so that the next click doesn't re-select.  The `mouseup` event that
 * follows the `focus` click is ignored (needed on WebKit), but subsequent
 * `mouseup` events are processed normally, so the selection can be broken.
 * Once the element receives `blur` the handlers are added back.
 **/

define('ui/widget/textbox',[], function(){

  function __highlight( e ){
    var input = e.target;
    input.select();
    input.removeEventListener( "focus", __highlight, false );
  }

  function __ignoreMouseUp( e ){
    e.preventDefault();
    var input = e.target;
    input.removeEventListener( "mouseup", __ignoreMouseUp, false );
  }

  function __addListeners( input ){
    input.addEventListener( "focus", __highlight, false );
    input.addEventListener( "mouseup", __ignoreMouseUp, false );
  }

  return function( input ){
    if( !(input && input.type === "text" ) ){
      throw "Textbox: Expected an input element of type text";
    }

    input.addEventListener( "blur", function( e ){
        __addListeners( e.target );
    }, false);

    __addListeners( input );

    return input;
  };

});

/* This Source Code Form is subject to the terms of the MIT license
 * If a copy of the MIT license was not distributed with this file, you can
 * obtain one at http://www.mozillapopcorn.org/butter-license.txt */

define('core/page',[ "core/logger", "core/eventmanager" ], function( Logger, EventManagerWrapper ) {

  return function( loader, config ) {

    var PLAYER_TYPE_URL = "{popcorn-js}/players/{type}/popcorn.{type}.js";

    var _snapshot;

    EventManagerWrapper( this );

    this.scrape = function() {
      var rootNode = document.body,
          targets = rootNode.querySelectorAll("*[data-butter='target']"),
          medias = rootNode.querySelectorAll("*[data-butter='media']");

      return {
        media: medias,
        target: targets
      };
    }; // scrape

    this.prepare = function( readyCallback ){
      loader.load([
        {
          type: "js",
          url: "{popcorn-js}/popcorn.js",
          check: function(){
            return !!window.Popcorn;
          }
        },
        {
          type: "js",
          url: "{popcorn-js}/modules/player/popcorn.player.js",
          check: function(){
            return !!window.Popcorn && !!window.Popcorn.player;
          }
        }
      ], readyCallback, null, true );
    };

    this.addPlayerType = function( type, callback ){
      loader.load({
        type: "js",
        url: PLAYER_TYPE_URL.replace( /\{type\}/g, type ),
        check: function(){
          return !!Popcorn[ type ];
        }
      }, callback );
    };

    this.getHTML = function( popcornStrings ){
      var html, head, body, i, l, toClean, toExclude, node, newNode, base, mediaElements;

      //html tag to which body and head are appended below
      html = document.createElement( "html" );

      // if there is already a snapshot, clone it instead of cloning the current dom
      if( !_snapshot ){
        body = document.getElementsByTagName( "body" )[ 0 ].cloneNode( true );
      }
      else {
        body = _snapshot.body.cloneNode( true );
      }

      head = document.getElementsByTagName( "head" )[ 0 ].cloneNode( true );

      toExclude = Array.prototype.slice.call( head.querySelectorAll( "*[data-butter-exclude]" ) );
      toExclude = toExclude.concat( Array.prototype.slice.call( head.querySelectorAll( "*[data-requiremodule]" ) ) );
      for ( i = 0, l = toExclude.length; i < l; ++i ) {
        node = toExclude[ i ];
        node.parentNode.removeChild( node );
      }

      mediaElements = body.querySelectorAll( "*[data-butter='media']" );

      for ( i = 0, l = mediaElements.length; i < l; ++i ) {
        node = mediaElements[ i ];
        newNode = document.getElementById( node.id ).cloneNode( true );

        if( [ "VIDEO", "AUDIO" ].indexOf( newNode.nodeName ) === -1 ){
          newNode.innerHTML = "";
        }
        node.parentNode.replaceChild( newNode, node );
        newNode.removeAttribute( "data-butter-source" );
      }

      toClean = body.querySelectorAll( "*[butter-clean=\"true\"]" );
      for ( i = 0, l = toClean.length; i < l; ++i ) {
        node = toClean[ i ];

        node.removeAttribute( "butter-clean" );
        node.removeAttribute( "data-butter" );
        node.removeAttribute( "data-butter-default" );

        // obviously, classList is preferred (https://developer.mozilla.org/en/DOM/element.classList)
        if( node.classList ){
          node.classList.remove( "ui-droppable" );
        }
        else{
          node.className = node.className.replace( /ui-droppable/g, "" );
        } //if
      } //for

      toExclude = body.querySelectorAll( "*[data-butter-exclude]" );
      for ( i = 0, l = toExclude.length; i < l; ++i ) {
        node = toExclude[ i ];
        node.parentNode.removeChild( node );
      } //for

      // Add <base> tag, but only for export
      base = document.createElement("base");
      base.href = window.location.href.substring( 0, window.location.href.lastIndexOf( "/" ) + 1 );
      head.insertBefore( base, head.firstChild );

      html.appendChild( head );
      html.appendChild( body );

      if( popcornStrings ){
        for ( i = 0; i < popcornStrings.length; ++i ) {
          var script = document.createElement( "script" );
          script.type = "text/javascript";
          script.innerHTML = "(function(){\n" + popcornStrings[ i ] + "\n}());";
          body.appendChild( script );
        } //for
      } //if

      this.dispatch( "getHTML", html );

      return "<html>" + html.innerHTML + "</html>";
    }; //getHTML

    /* Take a snapshot of the current DOM and store it.
     * Mainly for use with generatePopcornString() so as to not export unwanted DOM objects,
     * a snapshot can be taken at any time (usually up to the template author).
     */
    this.snapshotHTML = function(){
      _snapshot = {
        head: document.getElementsByTagName( "head" )[ 0 ].cloneNode( true ),
        body: document.getElementsByTagName( "body" )[ 0 ].cloneNode( true )
      };
    };

    /* Forget DOM snapshots previously taken
     */
    this.eraseSnapshot = function(){
      _snapshot = null;
    };

  }; // page
});

/* This Source Code Form is subject to the terms of the MIT license
 * If a copy of the MIT license was not distributed with this file, you can
 * obtain one at http://www.mozillapopcorn.org/butter-license.txt */


/**
 * Module: Comm
 *
 * Allows communication between entities through postMessage.
 */
define('core/comm',[ "./eventmanager" ], function( EventManagerWrapper ){

  var __context = 1;

  /**
   * Class: Comm
   *
   * Lets entities communicate when communication restrictions exist by passing messages through postMessage.
   *
   * @param {Window} clientWindow: Window from/to which to send/receive messages
   * @param {Function} readyCallback: Function to be called when link is set up
   */
  var Comm = function( clientWindow, readyCallback ) {
    var _this = this,
        _readyInterval,
        _context = __context++,
        _destroyed = false,
        _ponged = false;

    EventManagerWrapper( _this );

    clientWindow.addEventListener( "message", function( e ){
      if( e.source === clientWindow && typeof e.data === "object" && e.data.context ){
        if( e.data.type === "pong" ){
          _ponged = true;
        }
        else {
          _this.dispatch( e.data.type, e.data.data );
        } //if
      } //if
    }, false );

    function checkPing(){
      if( !_destroyed ){
        if( !_ponged ){
          _this.dispatch( "error", {
            type: "connectionclosed"
          });
        } //if
        ping();
      } //if
    } //checkPing

    function ping(){
      _ponged = false;
      _this.send( "ping" );
      setTimeout( checkPing, 1000 );
    } //ping

    _this.listen( "ready", function( e ){
      clearInterval( _readyInterval );
      readyCallback();
      ping();
    });

    _readyInterval = setInterval( function(){
      _this.send( "ready", "ready" );
    }, 100 );

    this.send = function( type, data ){
      clientWindow.postMessage({
        type: type,
        context: _context,
        data: data
      }, "*" );
    }; //send

    this.destroy = function(){
      _destroyed = true;
      clearInterval( _readyInterval );
    }; //destroy
  }; //Comm

  return Comm;
});

/* This Source Code Form is subject to the terms of the MIT license
 * If a copy of the MIT license was not distributed with this file, you can
 * obtain one at http://www.mozillapopcorn.org/butter-license.txt */

define('dialog/modal',[], function(){

  var __container;

  return function( state ){

    if( !__container ){
      __container = document.createElement( "div" );
      __container.id = "butter-modal-container";
      __container.setAttribute( "data-butter-exclude", true );
      document.body.appendChild( __container );
    } //if

    var _element = document.createElement( "div" );

    _element.className = "layer";

    if( state && typeof( state ) === "string" ){
      _element.className += state;
    } //if

    __container.appendChild( _element );

    // need to wait an event-loop cycle to apply this class
    // ow, opacity transition fails to render
    setTimeout( function(){
      _element.className += " fade-in";
    }, 10 );

    this.destroy = function(){
      __container.removeChild( _element );
    }; //destroy

    Object.defineProperties( this, {
      element: {
        enumerable: true,
        get: function(){
          return _element;
        }
      }
    });

  }; //Modal

});

/* This Source Code Form is subject to the terms of the MIT license
 * If a copy of the MIT license was not distributed with this file, you can
 * obtain one at http://www.mozillapopcorn.org/butter-license.txt */

define('dialog/iframe-dialog',[
          "core/comm",
          "core/eventmanager",
          "dialog/modal"
        ],
        function( Comm, EventManagerWrapper, Modal ){

  return function( dialogOptions ) {
    dialogOptions = dialogOptions || {};

    if( !dialogOptions.url ){
      throw new Error( "IFRAME dialog requires a url." );
    } //if

    var _this = this,
        _url = dialogOptions.url,
        _parent = dialogOptions.parent,
        _open = false,
        _iframe,
        _commQueue = [],
        _comm,
        _modalLayer,
        _listeners = dialogOptions.events || {};

    EventManagerWrapper( _this );

    this.modal = dialogOptions.modal;

    function onSubmit( e ){
      _this.dispatch( e.type, e.data );
    } //onSubmit

    function onCancel( e ){
      _this.dispatch( e.type, e.data );
      _this.close();
    } //onCancel

    this.close = function(){
      // Send a close message to the dialog first, then actually close the dialog.
      // A setTimeout is used here to ensure that its associated function will be run
      // almost right after the postMessage happens. This ensures that messages get to
      // their destination before we remove the dom element (which will basically ruin
      // everything) by placing callbacks in the browser's event loop in the correct order.
      _this.send( "close" );
      setTimeout( function(){
        _parent.removeChild( _iframe );
        if( _modalLayer ){
          _modalLayer.destroy();
          _modalLayer = undefined;
        } //if
        _comm.unlisten( "submit", onSubmit );
        _comm.unlisten( "cancel", onCancel );
        _comm.unlisten( "close", _this.close );
        _comm.destroy();
        _open = false;
        window.removeEventListener( "beforeunload",  _this.close, false );
        for( var e in _listeners ){
          if( e !== "close" ){
            _this.unlisten( e, _listeners[ e ] );
          }
        } //for
        _this.dispatch( "close" );
        _this.unlisten( "close", _listeners.close );
      }, 0 );
    }; //close

    this.open = function( listeners ){
      if( _open ){
        return;
      } //if
      if( _this.modal ){
        _modalLayer = new Modal( _this.modal );
      } //if
      for( var e in listeners ){
        if( listeners.hasOwnProperty( e ) ){
          _listeners[ e ] = listeners[ e ];
        }
      } //for
      var defaultParent = _modalLayer ? _modalLayer.element : document.body;
      _parent = _parent || defaultParent;
      _iframe = document.createElement( "iframe" );
      _iframe.src = _url;
      _iframe.addEventListener( "load", function( e ){
        _comm = new Comm( _iframe.contentWindow, function(){
          _comm.listen( "submit", onSubmit );
          _comm.listen( "cancel", onCancel );
          _comm.listen( "close", _this.close );
          window.addEventListener( "beforeunload",  _this.close, false );
          for( var e in _listeners ){
            if( _listeners.hasOwnProperty( e ) ){
              _this.listen( e, _listeners[ e ] );
            }
          } //for
          while( _commQueue.length > 0 ){
            var popped = _commQueue.pop();
            _this.send( popped.type, popped.data );
          } //while
          _open = true;
          // Immediately set focus
          setTimeout( function() {
            _this.focus();
          }, 0 );
          _this.dispatch( "open" );
        });
      }, false );
      _parent.appendChild( _iframe );

      // need to wait an event-loop cycle to apply this class
      // ow, opacity transition fails to render
      setTimeout( function(){
        _iframe.className += " fade-in";
      }, 10 );
    }; //open

    this.send = function( type, data ){
      if( _comm ){
        _comm.send( type, data );
      }
      else {
        _commQueue.push({ type: type, data: data });
      } //if
    }; //send

    this.focus = function() {
      _iframe.contentWindow.focus();
    }; //focus

    Object.defineProperties( this, {
      iframe: {
        enumerable: true,
        get: function(){
          return _iframe;
        }
      },
      closed: {
        enumerable: true,
        get: function(){
          return !_open;
        }
      }
    });
  }; //IFrameDialog
});

/* This Source Code Form is subject to the terms of the MIT license
 * If a copy of the MIT license was not distributed with this file, you can
 * obtain one at http://www.mozillapopcorn.org/butter-license.txt */

define('dialog/window-dialog',[
          "core/comm",
          "core/eventmanager",
          "dialog/modal"
        ],
        function( Comm, EventManagerWrapper, Modal ){

  var DEFAULT_WINDOW_WIDTH = 640,
      DEFAULT_WINDOW_HEIGHT = 479,
      WINDOW_CHECK_INTERVAL = 300;

  return function( dialogOptions ) {
    dialogOptions = dialogOptions || {};

    if( !dialogOptions.url ){
      throw new Error( "Window dialog requires a url." );
    } //if

    var _this = this,
        _url = dialogOptions.url,
        _comm,
        _window,
        _modalLayer,
        _statusInterval,
        _commQueue = [],
        _open = false,
        _features = [
          "width=" + ( dialogOptions.width || DEFAULT_WINDOW_WIDTH ),
          "height=" + ( dialogOptions.height || DEFAULT_WINDOW_HEIGHT ),
          "toolbar=no",
          "menubar=no",
          "titlebar=yes",
          "location=no",
          "resizable=yes"
        ],
        _listeners = dialogOptions.events || {};

    EventManagerWrapper( _this );

    _this.modal = dialogOptions.modal;

    function onSubmit( e ){
      _this.dispatch( e.type, e.data );
    } //onSubmit

    function onCancel( e ){
      _this.dispatch( e.type, e.data );
      _this.close();
    } //onCancel

    function onError( e ){
      if( e.data.type === "connectionclosed" ){
        _this.close();
      } //if
      _this.dispatch( "error", e.data );
    } //onError

    this.close = function(){
      // Send a close message to the dialog first, then actually close the dialog.
      // A setTimeout is used here to ensure that its associated function will be run
      // almost right after the postMessage happens. This ensures that messages get to
      // their destination before we remove the dom element (which will basically ruin
      // everything) by placing callbacks in the browser's event loop in the correct order.
      _this.send( "close" );
      setTimeout( function(){
        if( _modalLayer ){
          _modalLayer.destroy();
          _modalLayer = undefined;
        } //if
        _comm.unlisten( "submit", onSubmit );
        _comm.unlisten( "cancel", onCancel );
        _comm.unlisten( "close", _this.close );
        _comm.destroy();
        if( _window.close ){
          _window.close();
        } //if
        clearInterval( _statusInterval );
        window.removeEventListener( "beforeunload",  _this.close, false );
        _comm = _window = undefined;
        _open = false;
        for( var e in _listeners ){
          if( _listeners.hasOwnProperty( e ) ){
            _this.unlisten( e, _listeners[ e ] );
          }
        } //for
        _this.dispatch( "close" );
      }, 0 );
    }; //close

    function checkWindowStatus(){
      if( _window && _window.closed === true ) {
        _this.close();
      } //if
    } //checkWindowStatus

    this.open = function( listeners ){
      if( _this.modal ){
        _modalLayer = new Modal( _this.modal );
      } //if
      for ( var e in listeners ){
        if( listeners.hasOwnProperty( e ) ){
          _listeners[ e ] = listeners[ e ];
        }
      } //for
      _window = window.open( _url, "dialog-window:" + _url, _features.join( "," ) );
      window.addEventListener( "beforeunload",  _this.close, false );
      _comm = new Comm( _window, function(){
        _comm.listen( "error", onError );
        _comm.listen( "submit", onSubmit );
        _comm.listen( "cancel", onCancel );
        _comm.listen( "close", _this.close );
        for( var e in _listeners ){
          if( _listeners.hasOwnProperty( e ) ){
            _this.listen( e, _listeners[ e ] );
          }
        } //for
        _statusInterval = setInterval( checkWindowStatus, WINDOW_CHECK_INTERVAL );
        while( _commQueue.length > 0 ){
          var popped = _commQueue.pop();
          _this.send( popped.type, popped.data );
        } //while
        _open = true;
        _this.dispatch( "open" );
      });
    }; //open

    this.focus = function() {
      _window.focus();
    };

    this.send = function( type, data ){
      if( _comm ){
        _comm.send( type, data );
      }
      else {
        _commQueue.push({ type: type, data: data });
      } //if
    }; //send

    Object.defineProperties( this, {
      closed: {
        enumerable: true,
        get: function(){
          return !_open;
        }
      }
    });

  }; //WindowDialog

});

/* This Source Code Form is subject to the terms of the MIT license
 * If a copy of the MIT license was not distributed with this file, you can
 * obtain one at http://www.mozillapopcorn.org/butter-license.txt */

define('editor/editor',[ "core/eventmanager", "dialog/iframe-dialog", "dialog/window-dialog", "util/time" ],
        function( EventManagerWrapper, IFrameDialog, WindowDialog, TimeUtil ) {

  var DEFAULT_DIMS = [ 400, 400 ],
      DEFAULT_FRAME_TYPE = "iframe";

  function Editor( butter, source, type, frameType, parentElement, options ){
    options = options || {};

    var _frameType = frameType || DEFAULT_FRAME_TYPE,
        _type = type,
        _dims = DEFAULT_DIMS.slice(),
        _dialog,
        _dialogOptions = {
          type: _frameType,
          modal: "behind-timeline",
          url: source,
          parent: parentElement
        },
        _currentTarget,
        _currentTrackEvent,
        _this = this;

    EventManagerWrapper( _this );

    _dims[ 0 ] = options.width || _dims[ 0 ];
    _dims[ 1 ] = options.height || _dims[ 1 ];

    function blinkTarget(){
      if( _currentTarget === "Media Element" ){
        butter.currentMedia.view.blink();
      }
      else{
        var target = butter.getTargetByType( "elementID", _currentTarget );
        if( target ){
          target.view.blink();
        } //if
      } //if
    }

    function onTrackEventUpdated( e ){
      var popcornData = _currentTrackEvent.popcornOptions;
      if( popcornData.target !== _currentTarget ){
        _currentTarget = popcornData.target;
        blinkTarget();
      } //if
      _dialog.send( "trackeventupdated", _currentTrackEvent.popcornOptions );
    } //onTrackEventUpdated

    function onTrackEventUpdateFailed( e ){
      _dialog.send( "trackeventupdatefailed", e.data );
    } //onTrackEventUpdateFailed

    function onClose(){
      _dialog = null;
      _currentTrackEvent.unlisten( "trackeventupdated", onTrackEventUpdated );
      _currentTrackEvent.unlisten( "trackeventupdatefailed", onTrackEventUpdateFailed );
      _this.dispatch( "close" );
    }

    this.open = function( trackEvent ) {
      if( !_dialog ){
        if( _frameType === "window" ){
          _dialog = new WindowDialog( _dialogOptions );
        }
        else{
          _dialog = new IFrameDialog( _dialogOptions );
        } //if
      } //if

      if( !_dialog.closed && _dialog.focus ){
        _dialog.focus();
        return;
      } //if

      _currentTrackEvent = trackEvent;

      _dialog.open({
        open: function( e ){
          var targets = [],
              media = {
                name: butter.currentMedia.name,
                target: butter.currentMedia.target
              };
          for( var i = 0, l = butter.targets.length; i < l; i++ ) {
            targets.push( butter.targets[ i ].element.id );
          }
          var corn = trackEvent.popcornOptions;
          _dialog.send( "trackeventdata", {
            manifest: Popcorn.manifest[ trackEvent.type ],
            popcornOptions: corn,
            targets: targets,
            media: media
          });
          _currentTarget = corn.target;
          blinkTarget();
          trackEvent.listen( "trackeventupdated", onTrackEventUpdated );
          trackEvent.listen( "trackeventupdatefailed", onTrackEventUpdateFailed );
          _this.dispatch( "open" );
        },
        submit: function( e ){
          var popcornData = e.data.eventData,
              alsoClose = e.data.alsoClose;
          if( popcornData ){
            trackEvent.update( popcornData );
            if( alsoClose ){
              _dialog.close();
            } //if
          } //if
        },
        close: function( e ){
          onClose();
        }
      });
    }; //open

    this.close = function(){
      if( _currentTrackEvent && _dialog ){
        _dialog.close();
      }
    };

    Object.defineProperties( _this, {
      isOpen: {
        enumerable: true,
        get: function(){
          return !!_dialog;
        }
      },
      type: {
        enumerable: true,
        get: function(){
          return _type;
        }
      },
      frame: {
        enumerable: true,
        get: function(){
          return _frameType;
        }
      },
      size: {
        enumerable: true,
        get: function(){
          return { width: _dims[ 0 ], height: _dims[ 1 ] };
        },
        set: function( val ){
          val = val || {};
          _dims[ 0 ] = val.width || _dims[ 0 ];
          _dims[ 1 ] = val.height || _dims[ 1 ];
        }
      }
    });

  } //Editor

  return Editor;

});



/* This Source Code Form is subject to the terms of the MIT license
 * If a copy of the MIT license was not distributed with this file, you can
 * obtain one at http://www.mozillapopcorn.org/butter-license.txt */

define('timeline/track-container',[
  "core/logger",
  "util/dragndrop"
],
function(
  Logger,
  DragNDrop
) {

  return function( butter, media ){

    var _media = media,
        _zoom = 1,
        _this = this;

    var _element = document.createElement( "div" ),
        _container = document.createElement( "div" );

    var _hScrollbar,
        _vScrollbar;

    var _droppable;

    _element.appendChild( _container );

    _element.className = "tracks-container-wrapper";
    _container.className = "tracks-container";

    _container.addEventListener( "mousedown", function( e ){
      _this.deselectOthers();
    }, false );

    _droppable = DragNDrop.droppable( _element, {
      drop: function( dropped, mousePosition ) {
        if ( dropped.getAttribute( "data-butter-draggable-type" ) === "plugin" ) {
          var newTrack = butter.currentMedia.addTrack(),
              trackRect = newTrack.view.element.getBoundingClientRect(),
              left = mousePosition[ 0 ] - trackRect.left,
              start = left / trackRect.width * newTrack.view.duration;

          newTrack.view.dispatch( "plugindropped", {
            start: start,
            track: newTrack,
            type: dropped.getAttribute( "data-butter-plugin-type" )
          });
        }
      }
    });

    this.setScrollbars = function( hScrollbar, vScrollbar ){
      _hScrollbar = hScrollbar;
      _vScrollbar = vScrollbar;
    };

    this.orderTracks = function( orderedTracks ){
      for( var i=0, l=orderedTracks.length; i<l; ++i ){
        var trackElement = orderedTracks[ i ].view.element;
        if( trackElement !== _container.childNodes[ i ] ){
          orderedTracks[ i ].order = i;
          _container.insertBefore( trackElement, _container.childNodes[ i + 1 ] );
        } //if
      } //for
    }; //orderTracks

    this.deselectOthers = function() {
      for( var i = 0; i < butter.selectedEvents.length; i++ ) {
        butter.selectedEvents[ i ].selected = false;
      } // for
      butter.selectedEvents = [];
      return _this;
    }; //deselectOthers

    function resetContainer() {
      _container.style.width = _media.duration * _zoom + "px";
    } //resetContainer

    _media.listen( "mediaready", function(){
      resetContainer();
      var tracks = _media.tracks;
      for( var i=0, il=tracks.length; i<il; ++i ){
        var trackView = tracks[ i ].view;
        _container.appendChild( trackView.element );
        trackView.duration = _media.duration;
        trackView.zoom = _zoom;
        trackView.parent = _this;
      } //for
    });

    butter.listen( "mediaremoved", function ( e ) {
      if ( e.data === _media && _droppable ){
        _droppable.destroy();
      }
    });

    function onTrackAdded( e ){
      var trackView = e.data.view;
      _container.appendChild( trackView.element );
      trackView.duration = _media.duration;
      trackView.zoom = _zoom;
      trackView.parent = _this;
      _vScrollbar.update();
    }

    var existingTracks = _media.tracks;
    for( var i=0; i<existingTracks.length; ++i ){
      onTrackAdded({
        data: existingTracks[ i ]
      });
    }

    _media.listen( "trackadded", onTrackAdded );

    _media.listen( "trackremoved", function( e ){
      var trackView = e.data.view;
      _container.removeChild( trackView.element );
      if( _vScrollbar ){
        _vScrollbar.update();
      }
    });

    _this.update = function(){
      resetContainer();
    };

    _this.snapTo = function( time ){
      var p = time / _media.duration,
          newScroll = _element.scrollWidth * p;
      if ( newScroll < _element.scrollLeft || newScroll > _element.scrollLeft + _element.clientWidth ) {
        _element.scrollLeft = newScroll;
      }
    };

    Object.defineProperties( this, {
      zoom: {
        enumerable: true,
        get: function(){ return _zoom; },
        set: function( val ){
          _zoom = val;
          resetContainer();
          var tracks = _media.tracks;
          for( var i=0, il=tracks.length; i<il; ++i ){
            tracks[ i ].view.zoom = _zoom;
          } //for
        }
      },
      element: {
        enumerable: true,
        get: function(){
          return _element;
        }
      },
      container: {
        enumerable: true,
        get: function(){
          return _container;
        }
      }
    });

  };

});


/* This Source Code Form is subject to the terms of the MIT license
 * If a copy of the MIT license was not distributed with this file, you can
 * obtain one at http://www.mozillapopcorn.org/butter-license.txt */

define('timeline/scrollbars',[ "core/eventmanager" ], function( EventManagerWrapper ){

  var VERTICAL_SIZE_REDUCTION_FACTOR = 3;

  function Vertical( tracksContainer, scrollTarget ){
    var _element = document.createElement( "div" ),
        _handle = document.createElement( "div" ),
        _containerParent = tracksContainer.element,
        _containerChild = tracksContainer.container,
        _scrollTarget = scrollTarget || _containerParent,
        _elementHeight,
        _parentHeight,
        _handleHeight,
        _mousePos = 0,
        _this = this;

    EventManagerWrapper( _this );

    _element.className = "scroll-bar scroll-bar-v";
    _handle.className = "scroll-handle";

    _element.appendChild( _handle );

    function setup(){
      _parentHeight = _containerParent.getBoundingClientRect().height;
      _elementHeight = _element.getBoundingClientRect().height;
      _handleHeight = _elementHeight - ( _containerChild.scrollHeight - _parentHeight ) / VERTICAL_SIZE_REDUCTION_FACTOR;
      _handleHeight = Math.max( 20, Math.min( _elementHeight, _handleHeight ) );
      _handle.style.height = _handleHeight + "px";
      setHandlePosition();
    } //setup

    function onMouseUp(){
      window.removeEventListener( "mouseup", onMouseUp, false );
      window.removeEventListener( "mousemove", onMouseMove, false );
      _handle.addEventListener( "mousedown", onMouseDown, false );
    } //onMouseUp

    function onMouseMove( e ){
      var diff = e.pageY - _mousePos;
      diff = Math.max( 0, Math.min( diff, _elementHeight - _handleHeight ) );
      _handle.style.top = diff + "px";
      var p = _handle.offsetTop / ( _elementHeight - _handleHeight );
      _containerParent.scrollTop = ( _containerChild.scrollHeight - _parentHeight ) * p;
      _this.dispatch( "scroll", _containerParent.scrollTop );
    } //onMouseMove

    function onMouseDown( e ){
      if( e.button === 0 ){
        var handleY = _handle.offsetTop;
        _mousePos = e.pageY - handleY;
        window.addEventListener( "mouseup", onMouseUp, false );
        window.addEventListener( "mousemove", onMouseMove, false );
        _handle.removeEventListener( "mousedown", onMouseDown, false );
      } //if
    } //onMouseDown

    this.update = function(){
      setup();
    }; //update

    function setHandlePosition(){
      if( _containerChild.scrollHeight - _elementHeight > 0 ){
        _handle.style.top = ( _elementHeight - _handleHeight ) *
          ( _containerParent.scrollTop / ( _containerChild.scrollHeight - _parentHeight ) ) + "px";
      }
      else{
        _handle.style.top = "0px";
      }
    }

    _containerParent.addEventListener( "scroll", function( e ){
      setHandlePosition();
    }, false );

    _scrollTarget.addEventListener( "mousewheel", function( e ){
      if( e.wheelDeltaY ){
        _containerParent.scrollTop -= e.wheelDeltaY;
        setHandlePosition();
        e.preventDefault();
      }
    }, false );

    // For Firefox
    _scrollTarget.addEventListener( "DOMMouseScroll", function( e ){
      if( e.axis === e.VERTICAL_AXIS && !e.shiftKey ){
        _containerParent.scrollTop += e.detail * 2;
        setHandlePosition();
        e.preventDefault();
      }
    }, false );

    _element.addEventListener( "click", function( e ) {
      // bail early if this event is coming from the handle
      if( e.srcElement === _handle || e.button > 0 ) {
        return;
      }

      var posY = e.pageY,
          handleRect = _handle.getBoundingClientRect(),
          elementRect = _element.getBoundingClientRect(),
          p;

      if( posY > handleRect.bottom ) {
        _handle.style.top = ( ( posY - elementRect.top ) - _handleHeight ) + "px";
      } else if( posY < handleRect.top ) {
        _handle.style.top = posY - elementRect.top + "px";
      }

      p = _handle.offsetTop / ( _elementHeight - _handleHeight );
      _containerParent.scrollTop = ( _containerChild.scrollHeight - _elementHeight ) * p;
    }, false);

    window.addEventListener( "resize", setup, false );
    _handle.addEventListener( "mousedown", onMouseDown, false );

    setup();

    Object.defineProperties( this, {
      element: {
        enumerable: true,
        get: function(){
          return _element;
        }
      }
    });

  } //Vertical

  function Horizontal( tracksContainer, scrollTarget ){
    var _element = document.createElement( "div" ),
        _handle = document.createElement( "div" ),
        _containerParent = tracksContainer.element,
        _containerChild = tracksContainer.container,
        _scrollTarget = scrollTarget || _containerChild,
        _elementWidth,
        _parentWidth,
        _childWidth,
        _scrollWidth,
        _handleWidth,
        _mousePos = 0,
        _this = this;

    EventManagerWrapper( _this );

    _element.className = "scroll-bar scroll-bar-h";
    _handle.className = "scroll-handle";

    _element.appendChild( _handle );

    function setup(){
      _parentWidth = _containerParent.getBoundingClientRect().width;
      _childWidth = _containerChild.getBoundingClientRect().width;
      _elementWidth = _element.getBoundingClientRect().width;
      _scrollWidth = _containerChild.scrollWidth;
      _handleWidth = _elementWidth - ( _scrollWidth - _parentWidth );
      _handleWidth = Math.max( 20, Math.min( _elementWidth, _handleWidth ) );
      _handle.style.width = _handleWidth + "px";
      setHandlePosition();
    } //setup

    function onMouseUp(){
      window.removeEventListener( "mouseup", onMouseUp, false );
      window.removeEventListener( "mousemove", onMouseMove, false );
      _handle.addEventListener( "mousedown", onMouseDown, false );
    } //onMouseUp

    function onMouseMove( e ){
      var diff = e.pageX - _mousePos;
      diff = Math.max( 0, Math.min( diff, _elementWidth - _handleWidth ) );
      _handle.style.left = diff + "px";
      var p = _handle.offsetLeft / ( _elementWidth - _handleWidth );
      _containerParent.scrollLeft = ( _scrollWidth - _elementWidth ) * p;
      _this.dispatch( "scroll", _containerParent.scrollLeft );
    } //onMouseMove

    function onMouseDown( e ){
      if( e.button === 0 ){
        var handleX = _handle.offsetLeft;
        _mousePos = e.pageX - handleX;
        window.addEventListener( "mouseup", onMouseUp, false );
        window.addEventListener( "mousemove", onMouseMove, false );
        _handle.removeEventListener( "mousedown", onMouseDown, false );
      } //if
    } //onMouseDown

    function setHandlePosition(){
      if( _scrollWidth - _elementWidth > 0 ) {
        _handle.style.left = ( _elementWidth - _handleWidth ) *
          ( _containerParent.scrollLeft / ( _scrollWidth - _elementWidth )) + "px";
      }else{
        _handle.style.left = "0px";
      }
    }

    _containerParent.addEventListener( "scroll", function( e ){
      setHandlePosition();
    }, false );

    _scrollTarget.addEventListener( "mousewheel", function( e ){
      if( e.wheelDeltaX ){
        _containerParent.scrollLeft -= e.wheelDeltaX;
        setHandlePosition();
        e.preventDefault();
      }
    }, false );

    // For Firefox
    _scrollTarget.addEventListener( "DOMMouseScroll", function( e ){
      if( e.axis === e.HORIZONTAL_AXIS || ( e.axis === e.VERTICAL_AXIS && e.shiftKey )){
        _containerParent.scrollLeft += e.detail * 2;
        setHandlePosition();
        e.preventDefault();
      }
    }, false );

    _element.addEventListener( "click", function( e ) {
      // bail early if this event is coming from the handle
      if( e.srcElement === _handle || e.button > 0 ) {
        return;
      }

      var posX = e.pageX,
          handleRect = _handle.getBoundingClientRect(),
          elementRect = _element.getBoundingClientRect(),
          p;

      if( posX > handleRect.right ) {
        _handle.style.left = ( ( posX - elementRect.left ) - _handleWidth ) + "px";
      }
      else if( posX < handleRect.left ) {
        _handle.style.left = posX - elementRect.left + "px";
      }

      p = _handle.offsetLeft / ( _elementWidth - _handleWidth );
      _containerParent.scrollLeft = ( _scrollWidth - _elementWidth ) * p;
    }, false);

    window.addEventListener( "resize", setup, false );
    _handle.addEventListener( "mousedown", onMouseDown, false );

    this.update = function(){
      setup();
    }; //update

    setup();

    Object.defineProperties( this, {
      element: {
        enumerable: true,
        get: function(){
          return _element;
        }
      }
    });

  } //Horizontal

  return {
    Vertical: Vertical,
    Horizontal: Horizontal
  };

}); //define

;
/* This Source Code Form is subject to the terms of the MIT license
 * If a copy of the MIT license was not distributed with this file, you can
 * obtain one at http://www.mozillapopcorn.org/butter-license.txt */

define('timeline/scrubber',[], function(){

  var CHECK_MEDIA_INTERVAL = 50,
      SCROLL_INTERVAL = 16,
      SCROLL_DISTANCE = 20,
      MOUSE_SCRUBBER_PIXEL_WINDOW = 3;

  return function( butter, parentElement, media, tracksContainer, hScrollbar ){
    var _container = document.createElement( "div" ),
        _node = document.createElement( "div" ),
        _line = document.createElement( "div" ),
        _fill = document.createElement( "div" ),
        _tracksContainer = tracksContainer,
        _tracksContainerWidth,
        _element = parentElement,
        _media = media,
        _mouseDownPos,
        _currentMousePos,
        _zoom = 1,
        _scrollInterval = -1,
        _rect,
        _width,
        _isPlaying = false,
        _isScrubbing = false,
        _lastTime = -1,
        _lastScroll = _tracksContainer.element.scrollLeft,
        _lastZoom = -1,
        _lineWidth = 0;

    _container.className = "time-bar-scrubber-container";
    _node.className = "time-bar-scrubber-node";
    _line.className = "time-bar-scrubber-line";
    _node.title = _line.title = "Displays the media's current time. Drag to seek through the media.";
    _fill.className = "fill-bar";

    _node.appendChild( _line );
    _container.appendChild( _fill );
    _container.appendChild( _node );
    _element.appendChild( _container );

    butter.ui.registerStateToggleFunctions( "timeline", {
      transitionIn: function(){
        _line.removeAttribute( "data-butter-shortened" );
      },
      transitionOut: function(){
        _line.setAttribute( "data-butter-shortened", true );
      }
    });

    function setNodePosition(){
      var duration = _media.duration,
          currentTime = _media.currentTime,
          tracksElement = _tracksContainer.element,
          scrollLeft = tracksElement.scrollLeft;

      // if we can avoid re-setting position and visibility, then do so
      if( _lastTime !== currentTime || _lastScroll !== scrollLeft || _lastZoom !== _zoom ){

        var pos = currentTime / duration * _tracksContainerWidth,
            adjustedPos = pos - scrollLeft;

        // If the node position is outside of the viewing window, hide it.
        // Otherwise, show it and adjust its position.
        // Note the use of clientWidth here to account for padding/margin width fuzziness.
        if( pos < scrollLeft || pos - _lineWidth > _container.clientWidth + scrollLeft ){
          _node.style.display = "none";
        }
        else {
          _node.style.left = adjustedPos + "px";
          _node.style.display = "block";
        } //if

        if( pos < scrollLeft ){
          _fill.style.display = "none";
        }
        else {
          if( pos > _width + scrollLeft ){
            _fill.style.width = ( _width - 2 ) + "px";
          }
          else {
            _fill.style.width = adjustedPos + "px";
          } //if
          _fill.style.display = "block";
        } //if

      } //if

      _lastTime = currentTime;
      _lastScroll = scrollLeft;
      _lastZoom = _zoom;

    } //setNodePosition

    hScrollbar.listen( "scroll", setNodePosition );

    function onMouseUp( e ){
      if( _isPlaying ){
        _media.play();
        _isScrubbing = false;
      }

      clearInterval( _scrollInterval );
      _scrollInterval = -1;

      window.removeEventListener( "mouseup", onMouseUp, false );
      window.removeEventListener( "mousemove", onMouseMove, false );
    } //onMouseUp

    function scrollTracksContainer( direction ){
      if( direction === "right" ){
        _scrollInterval = setInterval(function(){
          if( _currentMousePos < _rect.right - MOUSE_SCRUBBER_PIXEL_WINDOW ){
            clearInterval( _scrollInterval );
            _scrollInterval = -1;
          }
          else{
            _currentMousePos += SCROLL_DISTANCE;
            _tracksContainer.element.scrollLeft += SCROLL_DISTANCE;
            evalMousePosition();
            setNodePosition();
          }
        }, SCROLL_INTERVAL );
      }
      else{
        _scrollInterval = setInterval(function(){
          if( _currentMousePos > _rect.left + MOUSE_SCRUBBER_PIXEL_WINDOW ){
            clearInterval( _scrollInterval );
            _scrollInterval = -1;
          }
          else{
            _currentMousePos -= SCROLL_DISTANCE;
            _tracksContainer.element.scrollLeft -= SCROLL_DISTANCE;
            evalMousePosition();
            setNodePosition();
          }
        }, SCROLL_INTERVAL );
      }
    } //scrollTracksContainer

    function evalMousePosition(){
      var diff = _currentMousePos - _mouseDownPos;
      diff = Math.max( 0, Math.min( diff, _width ) );
      _media.currentTime = ( diff + _tracksContainer.element.scrollLeft ) / _tracksContainerWidth * _media.duration;
    } //evalMousePosition

    function onMouseMove( e ){
      _currentMousePos = e.pageX;

      if( _scrollInterval === -1 ){
        if( _currentMousePos > _rect.right - MOUSE_SCRUBBER_PIXEL_WINDOW ){
          scrollTracksContainer( "right" );
        }
        else if( _currentMousePos < _rect.left + MOUSE_SCRUBBER_PIXEL_WINDOW ){
          scrollTracksContainer( "left" );
        } //if
      } //if

      evalMousePosition();
      setNodePosition();
    } //onMouseMove

    function onScrubberMouseDown( e ){
      _mouseDownPos = e.pageX - _node.offsetLeft;

      if( _isPlaying ){
        _media.pause();
        _isScrubbing = true;
      }

      _node.removeEventListener( "mousedown", onScrubberMouseDown, false );
      window.addEventListener( "mousemove", onMouseMove, false );
      window.addEventListener( "mouseup", onMouseUp, false );
    } //onMouesDown

    var onMouseDown = this.onMouseDown = function( e ){
      var pos = e.pageX - _container.getBoundingClientRect().left;
      _media.currentTime = ( pos + _tracksContainer.element.scrollLeft ) / _tracksContainerWidth * _media.duration;
      setNodePosition();
      onScrubberMouseDown( e );
    }; //onMouseDown

    _node.addEventListener( "mousedown", onScrubberMouseDown, false );
    _container.addEventListener( "mousedown", onMouseDown, false );

    this.update = function( containerWidth, zoom ){
      _zoom = zoom || _zoom;
      _width = containerWidth;
      _tracksContainerWidth = _tracksContainer.container.getBoundingClientRect().width;
      _container.style.width = _width + "px";
      _rect = _container.getBoundingClientRect();
      _lineWidth = _line.clientWidth;
      setNodePosition();
    }; //update

    function checkMedia(){
      setNodePosition();
    } //checkMedia

    _media.listen( "mediaplaying", function( e ){
      _isPlaying = true;
    });

    _media.listen( "mediapause", function( e ){
      if( !_isScrubbing ){
        _isPlaying = false;
      }
    });

    var _checkMediaInterval = setInterval( checkMedia, CHECK_MEDIA_INTERVAL );

    this.destroy = function(){
      clearInterval( _checkMediaInterval );
    }; //destroy
  };
});

/* This Source Code Form is subject to the terms of the MIT license
 * If a copy of the MIT license was not distributed with this file, you can
 * obtain one at http://www.mozillapopcorn.org/butter-license.txt */


define('timeline/zoombar',[], function(){
  var ZOOM_LEVELS = 6;

  return function( zoomCallback ){

    var _element = document.createElement( "div" ),
        _handle = document.createElement( "div" ),
        _rect,
        _mousePos,
        _handleWidth,
        _elementWidth,
        _this = this;

    _element.className = "zoom-bar scroll-bar";
    _handle.className = "scroll-handle";
    _handle.title = "Change the zoom level of the timeline";

    _element.appendChild( _handle );

    function onMouseUp(){
      window.removeEventListener( "mouseup", onMouseUp, false );
      window.removeEventListener( "mousemove", onMouseMove, false );
      _handle.addEventListener( "mousedown", onMouseDown, false );
      zoomCallback( _handle.offsetLeft / ( _rect.width - _handle.clientWidth ) );
    } //onMouseUp

    function onMouseMove( e ){
      var diff = e.pageX - _mousePos;
      diff = Math.max( 0, Math.min( diff, _elementWidth - _handleWidth ) );
      _handle.style.left = diff + "px";
      zoomCallback( _handle.offsetLeft / ( _rect.width - _handle.clientWidth ) );
    } //onMouseMove

    function onMouseDown( e ){
      if( e.button === 0 ){
        var handleX = _handle.offsetLeft;
        _mousePos = e.pageX - handleX;
        window.addEventListener( "mouseup", onMouseUp, false );
        window.addEventListener( "mousemove", onMouseMove, false );
        _handle.removeEventListener( "mousedown", onMouseDown, false );
      } //if
    } //onMouseDown

    _handle.addEventListener( "mousedown", onMouseDown, false );

    this.update = function() {
      _rect = _element.getBoundingClientRect();
      _handleWidth = ( _rect.width / ZOOM_LEVELS );
      _handle.style.width = _handleWidth + "px";
      _elementWidth = _rect.width;
    };

    this.zoom = function( level ) {
      _this.update();
      _handle.style.left = ( _rect.width - _handle.clientWidth ) * level + "px";
      zoomCallback( _handle.offsetLeft / ( _rect.width - _handle.clientWidth ) );
    };

    _element.addEventListener( "click", function( e ) {
      // bail early if this event is coming from the handle
      if( e.srcElement === _handle ) {
        return;
      }

      var posX = e.pageX,
          handleRect = _handle.getBoundingClientRect(),
          elementRect = _element.getBoundingClientRect();

      if( posX > handleRect.right ) {
        _handle.style.left = ( ( posX - elementRect.left ) - _handleWidth ) + "px";
      } else {
        _handle.style.left = posX - elementRect.left + "px";
      }

      onMouseMove( e );
    }, false);

    _element.addEventListener( "resize", function( e ){
      _this.update();
    }, false );

    Object.defineProperties( this, {
      element: {
        enumerable: true,
        get: function(){
          return _element;
        }
      }
    });

  }; //ZoomBar
});

/* This Source Code Form is subject to the terms of the MIT license
 * If a copy of the MIT license was not distributed with this file, you can
 * obtain one at http://www.mozillapopcorn.org/butter-license.txt */

define('timeline/status',[], function(){

  function Button( className, onClick, toolTip ){
    var _container = document.createElement( "div" ),
        _button = document.createElement( "div" ),
        _icon = document.createElement( "div" ),
        _state = true;

    _container.className = className;
    _button.className = "status-button";
    _button.title = toolTip || "";
    _icon.className = "status-button-icon";

    _container.appendChild( _button );
    _button.appendChild( _icon );

    function update(){
      if( _state ){
        _icon.removeAttribute( "state" );
      }
      else {
        _icon.setAttribute( "state", true );
      } //if
    } //update

    function onMouseUp( e ){
      _button.removeAttribute( "mouse-state" );
      window.removeEventListener( "mouseup", onMouseUp, false );
    } //onMouseUp

    _button.addEventListener( "mousedown", function( e ){
      _button.setAttribute( "mouse-state", "depressed" );
      window.addEventListener( "mouseup", onMouseUp, false );
    }, false );

    _button.addEventListener( "click", onClick, false );

    Object.defineProperties( this, {
      element: {
        enumerable: true,
        get: function(){ return _container; }
      },
      state: {
        enumerable: true,
        get: function(){
          return _state;
        },
        set: function( val ){
          _state = val;
          update();
        }
      }
    });

  } //Button

  function Time( media ){
    var _container = document.createElement( "div" ),
        _timeBox = document.createElement( "input" ),
        _media = media,
        _oldValue = 0;

    _container.className = "time-container";
    _container.appendChild( _timeBox );
    _timeBox.type = "text";

    function setTime( time, setCurrentTime ){
      if( typeof( time ) === "string" || !isNaN( time ) ){
        if( setCurrentTime ){
          try {
            _media.currentTime = Popcorn.util.toSeconds( time );
          }
          catch( e ){
            time = _media.currentTime;
          } //try
        } //if

        var timeStamp = new Date( 1970, 0, 1 ),
            seconds;

        timeStamp.setSeconds( time );
        seconds = timeStamp.toTimeString().substr( 0, 8 );

        if( seconds > 86399 ){
          seconds = Math.floor( ( timeStamp - Date.parse( "1/1/70" ) ) / 3600000 ) + seconds.substr( 2 );
        } //if

        _timeBox.value = seconds;
      }
      else {
        _timeBox.value = _oldValue;
      } //if
    } //setTime

    _media.listen( "mediatimeupdate", function( e ){
      setTime( _media.currentTime, false );
    });

    _timeBox.addEventListener( "focus", function( e ){
      _oldValue = _timeBox.value;
    }, false );

    _timeBox.addEventListener( "blur", function( e ){
      if( _timeBox.value !== _oldValue ){
        setTime( _timeBox.value, true );
      } //if
    }, false );

    _timeBox.addEventListener( "keydown", function( e ){
      if( e.which === 13 ){
        _timeBox.blur();
      }
      else if( e.which === 27 ){
        _timeBox.value = _oldValue;
        _timeBox.blur();
      } //if
    }, false );

    setTime( 0, false );

    Object.defineProperties( this, {
      element: {
        enumerable: true,
        get: function(){
          return _container;
        }
      }
    });

  } //Time

  return function( media ){

    var _media = media,
        _statusContainer = document.createElement( "div" ),
        _muteButton,
        _playButton,
        _time,
        _this = this;

    _statusContainer.className = "status-container";

    _time = new Time( _media );

    _muteButton = new Button( "mute-button-container", function( e ){
      _media.muted = !_media.muted;
    }, "Toggle volume on/off" );

    _playButton = new Button( "play-button-container", function( e ){
      if( _media.ended ){
        _media.paused = false;
      }
      else{
        _media.paused = !_media.paused;
      }
    }, "Play/Pause media");

    _media.listen( "mediamuted", function( e ){
      _muteButton.state = false;
    });

    _media.listen( "mediaunmuted", function( e ){
      _muteButton.state = true;
    });

    _media.listen( "mediavolumechange", function( e ){
      _muteButton.state = !_media.muted;
    });

    _media.listen( "mediaended", function( e ){
      _playButton.state = true;
    });

    _media.listen( "mediaplaying", function( e ){
      _playButton.state = false;
    });

    _media.listen( "mediapause", function( e ){
      _playButton.state = true;
    });

    _statusContainer.appendChild( _time.element );
    _statusContainer.appendChild( _playButton.element );

    _this.update = function(){
    }; //update

    _this.destroy = function(){
    }; //destroy

    Object.defineProperties( this, {
      statusElement: {
        enumerable: true,
        get: function(){
          return _statusContainer;
        }
      },
      muteElement: {
        enumerable: true,
        get: function(){
          return _muteButton.element;
        }
      }
    });

  }; //Status

});


/* This Source Code Form is subject to the terms of the MIT license
 * If a copy of the MIT license was not distributed with this file, you can
 * obtain one at http://www.mozillapopcorn.org/butter-license.txt */

define('timeline/trackhandles',[
          "dialog/iframe-dialog",
          "util/dragndrop"
        ],
        function( IFrameDialog, DragNDrop ){

  var ADD_TRACK_BUTTON_Y_ADJUSTMENT = 35;

  return function( butter, media, tracksContainer, orderChangedCallback ){

    var _media = media,
        _container = document.createElement( "div" ),
        _listElement = document.createElement( "div" ),
        _addTrackButton = document.createElement( "button" ),
        _tracks = {},
        _menus = [],
        _this = this;

    _container.className = "track-handle-container";
    _listElement.className = "handle-list";

    _container.appendChild( _listElement );

    _addTrackButton.id = "add-track";
    _addTrackButton.innerHTML = "+Track";
    _addTrackButton.title = "Add a new Track for your events";

    _container.appendChild( _addTrackButton );

    _addTrackButton.addEventListener( "click", function( e ){
      butter.currentMedia.addTrack();
    }, false );

    var _sortable = DragNDrop.sortable( _listElement, {
      change: function( elements ){
        var orderedTracks = [];
        for( var i=0, l=elements.length; i<l; ++i ){
          var id = elements[ i ].getAttribute( "data-butter-track-id" );
          orderedTracks.push( _tracks[ id ].track );
        }
        orderChangedCallback( orderedTracks );
      }
    });

    function onTrackAdded( e ){
      var track = e.data,
          trackId = track.id,
          trackName = track.name,
          trackDiv = document.createElement( "div" ),
          menuDiv = document.createElement( "div" ),
          deleteButton = document.createElement( "div" );

      menuDiv.className = "menu";
      deleteButton.className = "delete";
      menuDiv.appendChild( deleteButton );

      deleteButton.addEventListener( "click", function( e ){
        var dialog = new IFrameDialog({
          type: "iframe",
          modal: true,
          url: butter.ui.dialogDir + "delete-track.html",
          events: {
            open: function( e ){
              dialog.send( "trackdata", trackName );
            },
            submit: function( e ){
              if( e.data === true ){
                media.removeTrack( track );
              } //if
              dialog.close();
            },
            cancel: function( e ){
              dialog.close();
            },
            trackupdated: function( e ) {
              dialog.send( "trackupdated", { success: false });
            }
          }
        });
        dialog.trackupdated = function( e ) {
          console.log( "called", e );
        };
        dialog.open();
      }, false );

      trackDiv.addEventListener( "dblclick", function( e ){
        var dialog = new IFrameDialog({
          type: "iframe",
          modal: true,
          url: butter.ui.dialogDir + "track-data.html",
          events: {
            open: function( e ) {
              dialog.send( "trackdata", track.json );
            },
            submit: function( e ) {
              // wrap in a try catch so we know right away about any malformed JSON
              try {
                var trackData = JSON.parse( e.data ),
                    trackEvents = track.trackEvents,
                    trackDataEvents = trackData.trackEvents,
                    dontRemove = {},
                    toAdd = [],
                    i,
                    l;

                trackDiv.childNodes[ 0 ].textContent = track.name = trackData.name;
                // update every trackevent with it's new data
                for ( i = 0, l = trackDataEvents.length; i < l; i++ ) {
                  var teData = trackDataEvents[ i ],
                      te = track.getTrackEventById( teData.id );

                  // check to see if the current track event exists already
                  if ( te ) {
                    te.update( teData.popcornOptions );
                    /* remove it from our reference to the array of track events so we know
                     * which ones to remove later
                     */
                    dontRemove[ teData.id ] = teData;
                  // if we couldn't find the track event, it must be a new one
                  } else {
                    toAdd.push( { type: teData.type, popcornOptions: teData.popcornOptions } );
                  }
                }

                // remove all trackEvents that wern't updated
                for ( i = trackEvents.length, l = 0; i >= l; i-- ) {
                  if ( trackEvents[ i ] && !dontRemove[ trackEvents[ i ].id ] ) {
                    track.removeTrackEvent( trackEvents[ i ] );
                  }
                }

                // add all the trackEvents that didn't exist so far
                for ( i = 0, l = toAdd.length; i < l; i++ ) {
                  track.addTrackEvent( toAdd[ i ] );
                }
                // let the dialog know things went well
                dialog.send( "trackupdated", true );
              } catch ( error ) {
                // inform the dialog about the issue
                console.log( error );
                dialog.send( "trackupdated", false );
              }
            }
          }
        });
        dialog.open();
      }, false );

      _menus.push( menuDiv );

      trackDiv.className = "track-handle";
      trackDiv.id = "track-handle-" + trackId;
      trackDiv.setAttribute( "data-butter-track-id", trackId );
      trackDiv.appendChild( document.createTextNode( trackName ) );
      trackDiv.appendChild( menuDiv );

      _sortable.addItem( trackDiv );

      _listElement.appendChild( trackDiv );

      _tracks[ trackId ] = {
        id: trackId,
        track: track,
        element: trackDiv,
        menu: menuDiv
      };

      _addTrackButton.style.top = _listElement.offsetHeight - ADD_TRACK_BUTTON_Y_ADJUSTMENT + "px";
    }

    var existingTracks = _media.tracks;
    for( var i=0; i<existingTracks.length; ++i ){
      onTrackAdded({
        data: existingTracks[ i ]
      });
    }

    _media.listen( "trackadded", onTrackAdded );

    _media.listen( "trackremoved", function( e ){
      var trackId = e.data.id;
      _listElement.removeChild( _tracks[ trackId ].element );
      _sortable.removeItem( _tracks[ trackId ].element );
      _menus.splice( _menus.indexOf( _tracks[ trackId ].menu ), 1 );
      delete _tracks[ trackId ];
      _addTrackButton.style.top = _listElement.offsetHeight - ADD_TRACK_BUTTON_Y_ADJUSTMENT + "px";
    });

    tracksContainer.element.addEventListener( "scroll", function( e ){
      _container.scrollTop = tracksContainer.element.scrollTop;
    }, false );

    this.update = function(){
      _container.scrollTop = tracksContainer.element.scrollTop;
      _addTrackButton.style.top = _listElement.offsetHeight - ADD_TRACK_BUTTON_Y_ADJUSTMENT + "px";
    }; //update

    _this.update();

    Object.defineProperties( this, {
      element: {
        enumerable: true,
        get: function(){
          return _container;
        }
      }
    });

  }; //TrackHandles

});

/* This Source Code Form is subject to the terms of the MIT license
 * If a copy of the MIT license was not distributed with this file, you can
 * obtain one at http://www.mozillapopcorn.org/butter-license.txt */

define('util/scrollbars',[ "core/eventmanager" ], function( EventManagerWrapper ){

  var VERTICAL_SIZE_REDUCTION_FACTOR = 3;

  function Vertical( outerElement, innerElement ){
    var _element = document.createElement( "div" ),
        _handle = document.createElement( "div" ),
        _elementHeight,
        _parentHeight,
        _childHeight,
        _scrollHeight,
        _handleHeight,
        _mousePos = 0,
        _this = this;

    EventManagerWrapper( _this );

    _element.className = "scroll-bar scroll-bar-v";
    _handle.className = "scroll-handle";

    _element.appendChild( _handle );

    function setup(){
      _parentHeight = outerElement.getBoundingClientRect().height;
      _childHeight = innerElement.getBoundingClientRect().height;
      _elementHeight = _element.getBoundingClientRect().height;
      _scrollHeight = outerElement.scrollHeight;
      _handleHeight = _elementHeight - ( _scrollHeight - _parentHeight ) / VERTICAL_SIZE_REDUCTION_FACTOR;
      _handleHeight = Math.max( 20, Math.min( _elementHeight, _handleHeight ) );
      _handle.style.height = _handleHeight + "px";
      setHandlePosition();
    } //setup

    function onMouseUp(){
      window.removeEventListener( "mouseup", onMouseUp, false );
      window.removeEventListener( "mousemove", onMouseMove, false );
      _handle.addEventListener( "mousedown", onMouseDown, false );
    } //onMouseUp

    function onMouseMove( e ){
      var diff = e.pageY - _mousePos,
          maxDiff = _elementHeight - _handleHeight;
      diff = Math.max( 0, Math.min( diff, maxDiff ) );
      var p = diff / maxDiff;
      _handle.style.top = diff + "px";
      outerElement.scrollTop = ( _scrollHeight - _parentHeight ) * p;
      _this.dispatch( "scroll", outerElement.scrollTop );
    } //onMouseMove

    function onMouseDown( e ){
      if( e.button === 0 ){
        var handleY = _handle.offsetTop;
        _mousePos = e.pageY - handleY;
        window.addEventListener( "mouseup", onMouseUp, false );
        window.addEventListener( "mousemove", onMouseMove, false );
        _handle.removeEventListener( "mousedown", onMouseDown, false );
      } //if
    } //onMouseDown

    this.update = function(){
      setup();
    }; //update

    function setHandlePosition(){
      if( innerElement.scrollHeight - _elementHeight > 0 ) {
        _handle.style.top = ( _elementHeight - _handleHeight ) *
          ( outerElement.scrollTop / ( outerElement.scrollHeight - _elementHeight ) ) + "px";
      }else{
        _handle.style.top = "0px";
      }
    }

    innerElement.addEventListener( "scroll", function( e ){
      setHandlePosition();
    }, false );

    innerElement.addEventListener( "mousewheel", function( e ){
      if( e.wheelDeltaY ){
        outerElement.scrollTop -= e.wheelDeltaY;
        setHandlePosition();
        e.preventDefault();
      }
    }, false );

    // For Firefox
    innerElement.addEventListener( "DOMMouseScroll", function( e ){
      if( e.axis === e.VERTICAL_AXIS && !e.shiftKey ){
        innerElement.scrollTop += e.detail * 2;
        setHandlePosition();
        e.preventDefault();
      }
    }, false );

    _element.addEventListener( "click", function( e ) {
      // bail early if this event is coming from the handle
      if( e.srcElement === _handle || e.button > 0 ) {
        return;
      }

      var posY = e.pageY,
          handleRect = _handle.getBoundingClientRect(),
          elementRect = _element.getBoundingClientRect(),
          p;

      if( posY > handleRect.bottom ) {
        _handle.style.top = ( ( posY - elementRect.top ) - _handleHeight ) + "px";
      } else if( posY < handleRect.top ) {
        _handle.style.top = posY - elementRect.top + "px";
      }

      p = _handle.offsetTop / ( _elementHeight - _handleHeight );
      innerElement.scrollTop = ( _scrollHeight - _elementHeight ) * p;
    }, false);

    window.addEventListener( "resize", setup, false );
    _handle.addEventListener( "mousedown", onMouseDown, false );

    setup();

    Object.defineProperties( this, {
      element: {
        enumerable: true,
        get: function(){
          return _element;
        }
      }
    });

  } //Vertical

  function Horizontal( outerElement, innerElement ){
    var _element = document.createElement( "div" ),
        _handle = document.createElement( "div" ),
        _elementWidth,
        _parentWidth,
        _childWidth,
        _scrollWidth,
        _handleWidth,
        _mousePos = 0,
        _this = this;

    EventManagerWrapper( _this );

    _element.className = "scroll-bar scroll-bar-h";
    _handle.className = "scroll-handle";

    _element.appendChild( _handle );

    function setup(){
      _parentWidth = outerElement.getBoundingClientRect().width;
      _childWidth = innerElement.getBoundingClientRect().width;
      _elementWidth = _element.getBoundingClientRect().width;
      _scrollWidth = innerElement.scrollWidth;
      _handleWidth = _elementWidth - ( _scrollWidth - _parentWidth );
      _handleWidth = Math.max( 20, Math.min( _elementWidth, _handleWidth ) );
      _handle.style.width = _handleWidth + "px";
      setHandlePosition();
    } //setup

    function onMouseUp(){
      window.removeEventListener( "mouseup", onMouseUp, false );
      window.removeEventListener( "mousemove", onMouseMove, false );
      _handle.addEventListener( "mousedown", onMouseDown, false );
    } //onMouseUp

    function onMouseMove( e ){
      var diff = e.pageX - _mousePos;
      diff = Math.max( 0, Math.min( diff, _elementWidth - _handleWidth ) );
      _handle.style.left = diff + "px";
      var p = _handle.offsetLeft / ( _elementWidth - _handleWidth );
      innerElement.scrollLeft = ( _scrollWidth - _elementWidth ) * p;
      _this.dispatch( "scroll", innerElement.scrollLeft );
    } //onMouseMove

    function onMouseDown( e ){
      if( e.button === 0 ){
        var handleX = _handle.offsetLeft;
        _mousePos = e.pageX - handleX;
        window.addEventListener( "mouseup", onMouseUp, false );
        window.addEventListener( "mousemove", onMouseMove, false );
        _handle.removeEventListener( "mousedown", onMouseDown, false );
      } //if
    } //onMouseDown

    function setHandlePosition(){
      if( _scrollWidth - _elementWidth > 0 ) {
        _handle.style.left = ( _elementWidth - _handleWidth ) *
          ( innerElement.scrollLeft / ( _scrollWidth - _elementWidth )) + "px";
      }else{
        _handle.style.left = "0px";
      }
    }

    innerElement.addEventListener( "scroll", function( e ){
      setHandlePosition();
    }, false );

    innerElement.addEventListener( "mousewheel", function( e ){
      if( e.wheelDeltaX ){
        innerElement.scrollLeft -= e.wheelDeltaX;
        setHandlePosition();
        e.preventDefault();
      }
    }, false );

    // For Firefox
    innerElement.addEventListener( "DOMMouseScroll", function( e ){
      if( e.axis === e.HORIZONTAL_AXIS || ( e.axis === e.VERTICAL_AXIS && e.shiftKey )){
        innerElement.scrollLeft += e.detail * 2;
        setHandlePosition();
        e.preventDefault();
      }
    }, false );

    _element.addEventListener( "click", function( e ) {
      // bail early if this event is coming from the handle
      if( e.srcElement === _handle || e.button > 0 ) {
        return;
      }

      var posX = e.pageX,
          handleRect = _handle.getBoundingClientRect(),
          elementRect = _element.getBoundingClientRect(),
          p;

      if( posX > handleRect.right ) {
        _handle.style.left = ( ( posX - elementRect.left ) - _handleWidth ) + "px";
      }
      else if( posX < handleRect.left ) {
        _handle.style.left = posX - elementRect.left + "px";
      }

      p = _handle.offsetLeft / ( _elementWidth - _handleWidth );
      innerElement.scrollLeft = ( _scrollWidth - _elementWidth ) * p;
    }, false);

    window.addEventListener( "resize", setup, false );
    _handle.addEventListener( "mousedown", onMouseDown, false );

    this.update = function(){
      setup();
    }; //update

    setup();

    Object.defineProperties( this, {
      element: {
        enumerable: true,
        get: function(){
          return _element;
        }
      }
    });

  } //Horizontal

  return {
    Vertical: Vertical,
    Horizontal: Horizontal
  };

}); //define

;
/* This Source Code Form is subject to the terms of the MIT license
 * If a copy of the MIT license was not distributed with this file, you can
 * obtain one at http://www.mozillapopcorn.org/butter-license.txt */

define('plugin/plugin-list',[ "util/dragndrop" ], function( DragNDrop ){
	
	return function( butter ){
    var _parentElement = document.createElement( "div" ),
        _containerElement = document.createElement( "div" );

    _parentElement.id = "plugin-list";
    _containerElement.className = "container";
    _parentElement.appendChild( _containerElement );

    butter.ui.areas.work.addComponent( _parentElement, {
      states: [ "add-popcorn" ],
      transitionIn: function(){
        _parentElement.style.display = "block";
        setTimeout(function(){
          _parentElement.style.opacity = "1";
        }, 0);
      },
      transitionOut: function(){
        _parentElement.style.opacity = "0";
      },
      transitionInComplete: function(){

      },
      transitionOutComplete: function(){
        _parentElement.style.display = "none";
      }
    });

    butter.listen( "pluginadded", function( e ){
      var element = document.createElement( "div" ),
          iconImg = e.data.helper,
          icon = document.createElement( "span" ),
          text = document.createElement( "span" );

      DragNDrop.helper( element, {
        start: function(){
          var targets = butter.targets,
              media = butter.currentMedia;
          media.view.blink();
          for( var i=0, l=targets.length; i<l; ++i ){
            targets[ i ].view.blink();
          }
        },
        stop: function(){
          
        }
      });

      if( iconImg ) {
        icon.style.backgroundImage = "url('" + iconImg.src + "')";
        icon.className = "icon";
        element.appendChild( icon );
      }
      text.className = "label";
      text.innerHTML = e.data.type;
      element.appendChild( text );

      element.setAttribute( "data-butter-plugin-type", e.data.type );
      element.setAttribute( "data-butter-draggable-type", "plugin" );
      
      _containerElement.appendChild( element );
    });

    _parentElement.style.display = "none";
    _parentElement.classList.add( "fadable" );

	};

});
/* This Source Code Form is subject to the terms of the MIT license
 * If a copy of the MIT license was not distributed with this file, you can
 * obtain one at http://www.mozillapopcorn.org/butter-license.txt */

define('dependencies',[], function(){

  var DEFAULT_DIRS = {
        "popcorn-js": "../external/popcorn-js",
        "css": "css"
      },
      VAR_REGEX = /\{([\w\-\._]+)\}/,
      CSS_POLL_INTERVAL = 10;

  var DEFAULT_CHECK_FUNCTION = function(){
    var index = 0;
    return function(){
      return index++ > 0;
    };
  };

  return function( config ){

    var _configDirs = config.value( "dirs" );

    function fixUrl( url ){
      var match,
          replacement;

      while ( VAR_REGEX.test( url ) ) {
        match = VAR_REGEX.exec( url );
        replacement = _configDirs[ match[ 1 ] ] || DEFAULT_DIRS[ match[ 1 ] ] || "";
        url = url.replace( match[0], replacement );
      }

      return url.replace( "//", "/" );
    }

    var _loaders = {
      js: function( url, exclude, callback, checkFn ){
        checkFn = checkFn || DEFAULT_CHECK_FUNCTION();

        url = fixUrl( url );

        if( !checkFn() ){
          var scriptElement = document.createElement( "script" );
          scriptElement.src = url;
          scriptElement.type = "text/javascript";
          document.head.appendChild( scriptElement );
          scriptElement.onload = scriptElement.onreadystatechange = callback;
        }
        else if( callback ){
          callback();
        }
      },
      css: function( url, exclude, callback, checkFn, error ){
        var scriptElement,
            interval;

        checkFn = checkFn || function(){
          return !!scriptElement;
        };

        function runCheckFn() {
          interval = setInterval( function(){
            if( checkFn() ){
              clearInterval( interval );
              if( callback ){
                callback();
              }
            }
          }, CSS_POLL_INTERVAL );
        }

        url = fixUrl( url );

        if( !checkFn() ){
          scriptElement = document.createElement( "link" );
          scriptElement.rel = "stylesheet";
          scriptElement.onload =  runCheckFn;
          scriptElement.onerror = error;
          scriptElement.href = url;
          document.head.appendChild( scriptElement );
        }
        else if( callback ){
          callback();
        }
      }
    };

    function generateLoaderCallback( items, callback ){
      var loaded = 0;
      return function(){
        ++loaded;
        if( loaded === items.length ){
          if( callback ){
            callback();
          }
        }
      };
    }

    function generateNextFunction( items, callback ){
      var index = 0;
      function next(){
        if( index === items.length ){
          callback();
        }
        else{
          Loader.load( items[ index++ ], next );
        }
      }
      return next;
    }

    var Loader = {

      load: function( items, callback, error, ordered ){
        if( items instanceof Array && items.length > 0 ){
          var onLoad = generateLoaderCallback( items, callback );
          if( !ordered ){
            for( var i = 0; i < items.length; ++i ){
              Loader.load( items[ i ], onLoad );
            }
          }
          else {
            var next = generateNextFunction( items, callback );
            next();
          }

        }
        else {
          var item = items;

          if( _loaders[ item.type ] ){
            if( item.url ){
              _loaders[ item.type ]( item.url, item.exclude, callback, item.check, error );
            }
            else{
              throw new Error( "Attempted to load resource without url." );
            }
          }
          else {
            throw new Error( "Loader type " + item.type + " not found! Attempted: " + item.url );
          }

        }
      }
    };

    return Loader;

  };

});

/* This Source Code Form is subject to the terms of the MIT license
 * If a copy of the MIT license was not distributed with this file, you can
 * obtain one at http://www.mozillapopcorn.org/butter-license.txt */

define('ui/toggler',[], function(){
  return function( butter, parentElement ){
    var _butter = butter,
        _parent = parentElement,
        _element = document.createElement( "div" ),
        _img = document.createElement( "div" ),
        _this = this;

    _element.id = "toggle-button";
    _element.title = "Show/Hide Timeline";
    _element.appendChild( _img );
    _parent.appendChild( _element );

    _element.addEventListener( "click", function( e ){
      _butter.ui.visible = !_butter.ui.visible;
    }, false );

    Object.defineProperties( _this, {
      visible: {
        enumerable: true,
        get: function(){
          return _element.style.display !== "none";
        },
        set: function( val ){
          _element.style.display = val ? "block" : "none";
        }
      }
    });

  };
});

define('ui/context-button',[], function(){

  return function( butter ){
    var _button = document.createElement( "button" );

    _button.id = "add-popcorn";
    _button.title = "Add Popcorn Events to the timeline";
    _button.innerHTML = "+Popcorn";

    _button.addEventListener( "click", function(){
      if( butter.ui.contentState === "timeline" ){
        butter.ui.setContentState( "add-popcorn" );
        butter.ui.contentStateLocked = true;
      }
      else{
        butter.ui.contentStateLocked = false;
        butter.ui.setContentState( "timeline" );
      }
    }, false );

    butter.ui.areas.tools.addComponent( _button, {
      states: [ "add-popcorn", "editor" ],
      transitionIn: function(){
        _button.setAttribute( "disabled", true );
        _button.innerHTML = "Done";
        _button.title = "Finish adding Popcorn Events";
        _button.classList.add( "add-popcorn-done" );
      },
      transitionInComplete: function(){
        _button.removeAttribute( "disabled" );
      },
      transitionOut: function(){
        _button.setAttribute( "disabled", true );
        _button.innerHTML = "+Popcorn";
        _button.title = "Add Popcorn Events to the timeline";
        _button.classList.remove( "add-popcorn-done" );
      },
      transitionOutComplete: function(){
        _button.removeAttribute( "disabled" );
      }
    });
  };
});
/* This Source Code Form is subject to the terms of the MIT license
 * If a copy of the MIT license was not distributed with this file, you can
 * obtain one at http://www.mozillapopcorn.org/butter-license.txt */

(function() {

  function parameterize(data) {
    var s = [];

    if ( !data ) {
      return null;
    }

    for(var key in data){
      if( data.hasOwnProperty( key ) ){
        s[s.length] = encodeURIComponent(key) + "=" + encodeURIComponent(data[key]);
      }
    }

    return s.join("&").replace("/%20/g", "+");
  }

  define('util/xhr',[], function() {

    function setCSRFToken() {
      var element = document.getElementById("csrf_token_id");
      if ( element ) {
        csrf_token = element.value;
      }
    }

    var csrf_token;

    if ( document.readyState !== "loading" ) {
      setCSRFToken();
    } else {
      document.addEventListener( "DOMContentLoaded", setCSRFToken, false );
    }

    var XHR = {
      "get": function(url, callback) {
        var xhr = new XMLHttpRequest();
        xhr.open("GET", url, true);
        xhr.onreadystatechange = callback;
        xhr.setRequestHeader( "X-Requested-With", "XMLHttpRequest" );
        xhr.send(null);
      },
      "post": function(url, data, callback, type) {
        var xhr = new XMLHttpRequest();
        xhr.open("POST", url, true);
        xhr.onreadystatechange = callback;
        xhr.setRequestHeader( "X-Requested-With", "XMLHttpRequest" );
        if ( csrf_token ) {
          xhr.setRequestHeader( "X-CSRFToken", csrf_token );
        }
        if ( !type ) {
          xhr.setRequestHeader( "Content-Type", "application/x-www-form-urlencoded" );
          xhr.send( parameterize( data ));
        } else {
          xhr.setRequestHeader( "Content-Type", type );
          xhr.send( data );
        }
      }
    };

    return XHR;

  }); //define
}());

/* This Source Code Form is subject to the terms of the MIT license
 * If a copy of the MIT license was not distributed with this file, you can
 * obtain one at http://www.mozillapopcorn.org/butter-license.txt */

define('cornfield/module',['util/xhr'], function(XHR) {

  function audience() {
    return location.protocol + "//" + location.hostname + ( location.port ? ":" + location.port : "" );
  }

  var Cornfield = function( butter, config ) {

    var authenticated = false,
        email,
        name,
        username,
        server = audience();

    if ( !navigator.id ) {
      var script = document.createElement( "script" );
      script.src = "https://browserid.org/include.js";
      script.type = "text/javascript";
      script.setAttribute( "data-butter-exclude", true );
      document.head.appendChild( script );
    }

    this.login = function(callback) {
      navigator.id.get(function(assertion) {
        if (assertion) {
          XHR.post(server + "/browserid/verify",
            { audience: server, assertion: assertion },
            function() {
              if (this.readyState === 4) {
                try {
                  var response = JSON.parse(this.response);
                  if (response.status === "okay") {

                    // Get email, name, and username after logging in successfully
                    butter.cornfield.whoami( function( data ) {
                      callback( data );
                    });
                    return;
                  }

                  // If there was an error of some sort, callback on that
                  callback(response);
                } catch (err) {
                  callback({ error: "an unknown error occured" });
                }
              }
            });
        } else {
          callback(undefined);
        }
      });
    };

    this.whoami = function( callback ) {
      XHR.get( server + "/api/whoami", function() {
        if ( this.readyState === 4 ) {
          var response;

          try {
            response = JSON.parse( this.response );
            if ( this.status === 200 ) {
              authenticated = true;
              email = response.email;
              username = response.username;
              name = response.name;
            }
          } catch ( err ) {
            response = {
              error: "failed to parse data from server: \n" + this.response
            };
          }

          if ( callback ) {
            callback( response );
          }
        }
      });
    };

    // Check to see if we're already logged in
    butter.listen( "ready", function onMediaReady() {
      butter.unlisten( "ready", onMediaReady );

      butter.cornfield.whoami( function( response ) {
        if ( !response.error ) {
          butter.dispatch( "autologinsucceeded", response );
        }
      });
    });

    this.email = function() {
      return email;
    };

    this.name = function() {
      return name;
    };

    this.username = function() {
      return username;
    };

    this.authenticated = function() {
      return authenticated;
    };

    this.publish = function(id, callback) {
      XHR.post(server + "/api/publish/" + id, null, function() {
        if (this.readyState === 4) {
          try {
            var response = JSON.parse(this.response);
            callback(response);
          } catch (err) {
            callback({ error: "an unknown error occured" });
          }
        }
      });
    };

    this.logout = function(callback) {
      XHR.get(server + "/browserid/logout", function() {
        email = null;
        if (this.readyState === 4) {
          try {
            var response = JSON.parse(this.response);
            authenticated = false;
            email = undefined;
            username = undefined;
            name = undefined;
            callback(response);
          } catch (err) {
            callback({ error: "an unknown error occured" });
          }
        }
      });
    };

    this.list = function(callback) {
      XHR.get(server + "/api/projects", function() {
        if (this.readyState === 4) {
          try {
            var response = JSON.parse(this.response);
            callback(response);
          } catch (err) {
            callback({ error: "an unknown error occured" });
          }
        }
      });
    };

    this.load = function(id, callback) {
      XHR.get(server + "/api/project/" + id, function() {
        if (this.readyState === 4) {
          try {
            var response = JSON.parse(this.response);
            callback(response);
          } catch (err) {
            callback({ error: "an unknown error occured" });
          }
        }
      });
    };

    this.save = function(id, data, callback) {
      var url = server + "/api/project/";

      if ( id ) {
        url += id;
      }

      XHR.post( url, data, function() {
        if (this.readyState === 4) {
          try {
            var response = JSON.parse(this.response);
            callback(response);
          } catch (err) {
            callback({ error: "an unknown error occured" });
          }
        }
      }, "application/json" );
    };
  };

  Cornfield.__moduleName = "cornfield";

  return Cornfield;
});

/* This Source Code Form is subject to the terms of the MIT license
 * If a copy of the MIT license was not distributed with this file, you can
 * obtain one at http://www.mozillapopcorn.org/butter-license.txt */

define('util/lang',[], function(){

  /*************************************************************************/
  // Support createContextualFragment when missing (IE9)
  if ( 'Range' in window &&
       !Range.prototype.createContextualFragment ) {

    // Implementation used under MIT License, http://code.google.com/p/rangy/
    // Copyright (c) 2010 Tim Down

    // Implementation as per HTML parsing spec, trusting in the browser's
    // implementation of innerHTML. See discussion and base code for this
    // implementation at issue 67. Spec:
    // http://html5.org/specs/dom-parsing.html#extensions-to-the-range-interface
    // Thanks to Aleks Williams.

    var dom = {
      getDocument: function getDocument( node ) {
        if ( node.nodeType === 9 ) {
          return node;
        } else if ( typeof node.ownerDocument !== "undefined" ) {
          return node.ownerDocument;
        } else if ( typeof node.document !== "undefined" ) {
          return node.document;
        } else if ( node.parentNode ) {
          return this.getDocument( node.parentNode );
        } else {
          throw "No document found for node.";
        }
      },

      isCharacterDataNode: function( node ) {
        var t = node.nodeType;
        // Text, CDataSection or Comment
        return t === 3 || t === 4 || t === 8;
      },

      parentElement: function( node ) {
        var parent = node.parentNode;
        return parent.nodeType === 1 ? parent : null;
      },

      isHtmlNamespace: function( node ) {
        // Opera 11 puts HTML elements in the null namespace,
        // it seems, and IE 7 has undefined namespaceURI
        var ns;
        return typeof node.namespaceURI === "undefined" ||
               ( ( ns = node.namespaceURI ) === null ||
                 ns === "http://www.w3.org/1999/xhtml" );
      },

      fragmentFromNodeChildren: function( node ) {
        var fragment = this.getDocument( node ).createDocumentFragment(), child;
        while ( !!( child = node.firstChild ) ) {
          fragment.appendChild(child);
        }
        return fragment;
      }
    };

    Range.prototype.createContextualFragment = function( fragmentStr ) {
      // "Let node the context object's start's node."
      var node = this.startContainer,
        doc = dom.getDocument(node);

      // "If the context object's start's node is null, raise an INVALID_STATE_ERR
      // exception and abort these steps."
      if (!node) {
        throw new DOMException( "INVALID_STATE_ERR" );
      }

      // "Let element be as follows, depending on node's interface:"
      // Document, Document Fragment: null
      var el = null;

      // "Element: node"
      if ( node.nodeType === 1 ) {
        el = node;

      // "Text, Comment: node's parentElement"
      } else if ( dom.isCharacterDataNode( node ) ) {
        el = dom.parentElement( node );
      }

      // "If either element is null or element's ownerDocument is an HTML document
      // and element's local name is "html" and element's namespace is the HTML
      // namespace"
      if ( el === null ||
           ( el.nodeName === "HTML" &&
             dom.isHtmlNamespace( dom.getDocument( el ).documentElement ) &&
             dom.isHtmlNamespace( el )
           )
         ) {
        // "let element be a new Element with "body" as its local name and the HTML
        // namespace as its namespace.""
        el = doc.createElement( "body" );
      } else {
        el = el.cloneNode( false );
      }

      // "If the node's document is an HTML document: Invoke the HTML fragment parsing algorithm."
      // "If the node's document is an XML document: Invoke the XML fragment parsing algorithm."
      // "In either case, the algorithm must be invoked with fragment as the input
      // and element as the context element."
      el.innerHTML = fragmentStr;

      // "If this raises an exception, then abort these steps. Otherwise, let new
      // children be the nodes returned."

      // "Let fragment be a new DocumentFragment."
      // "Append all new children to fragment."
      // "Return fragment."
      return dom.fragmentFromNodeChildren( el );
    };
  }
  /*************************************************************************/

  /***************************************************************************
   * Cross-browser full element.classList implementation for IE9 and friends.
   * 2011-06-15
   *
   * By Eli Grey, http://purl.eligrey.com/github/classList.js/blob/master/classList.js
   * Public Domain.
   * NO WARRANTY EXPRESSED OR IMPLIED. USE AT YOUR OWN RISK.
   */
  /*global self, document, DOMException */
  if (typeof document !== "undefined" && !("classList" in document.createElement("a"))) {
    (function (view) {
      

      var classListProp = "classList",
        protoProp = "prototype",
        elemCtrProto = (view.HTMLElement || view.Element)[protoProp],
        objCtr = Object,
        strTrim = String[protoProp].trim || function () {
          return this.replace(/^\s+|\s+$/g, "");
        },
        arrIndexOf = Array[protoProp].indexOf || function (item) {
          var i = 0,
            len = this.length;
          for (; i < len; i++) {
            if (i in this && this[i] === item) {
              return i;
            }
          }
          return -1;
        },
        // Vendors: please allow content code to instantiate DOMExceptions
        DOMEx = function (type, message) {
          this.name = type;
          this.code = DOMException[type];
          this.message = message;
        },
        checkTokenAndGetIndex = function (classList, token) {
          if (token === "") {
            throw new DOMEx("SYNTAX_ERR", "An invalid or illegal string was specified");
          }
          if (/\s/.test(token)) {
            throw new DOMEx("INVALID_CHARACTER_ERR", "String contains an invalid character");
          }
          return arrIndexOf.call(classList, token);
        },
        ClassList = function (elem) {
          var trimmedClasses = strTrim.call(elem.className),
            classes = trimmedClasses ? trimmedClasses.split(/\s+/) : [],
            i = 0,
            len = classes.length;
          for (; i < len; i++) {
            this.push(classes[i]);
          }
          this._updateClassName = function () {
            elem.className = this.toString();
          };
        },
        classListProto = ClassList[protoProp] = [],
        classListGetter = function () {
          return new ClassList(this);
        };

      // Most DOMException implementations don't allow calling DOMException's toString()
      // on non-DOMExceptions. Error's toString() is sufficient here.
      DOMEx[protoProp] = Error[protoProp];
      classListProto.item = function (i) {
        return this[i] || null;
      };
      classListProto.contains = function (token) {
        token += "";
        return checkTokenAndGetIndex(this, token) !== -1;
      };
      classListProto.add = function (token) {
        token += "";
        if (checkTokenAndGetIndex(this, token) === -1) {
          this.push(token);
          this._updateClassName();
        }
      };
      classListProto.remove = function (token) {
        token += "";
        var index = checkTokenAndGetIndex(this, token);
        if (index !== -1) {
          this.splice(index, 1);
          this._updateClassName();
        }
      };
      classListProto.toggle = function (token) {
        token += "";
        if (checkTokenAndGetIndex(this, token) === -1) {
          this.add(token);
        } else {
          this.remove(token);
        }
      };
      classListProto.toString = function () {
        return this.join(" ");
      };

      if (objCtr.defineProperty) {
        var classListPropDesc = {
          get: classListGetter,
          enumerable: true,
          configurable: true
        };
        try {
          objCtr.defineProperty(elemCtrProto, classListProp, classListPropDesc);
        } catch (ex) { // IE 8 doesn't support enumerable:true
          if (ex.number === -0x7FF5EC54) {
            classListPropDesc.enumerable = false;
            objCtr.defineProperty(elemCtrProto, classListProp, classListPropDesc);
          }
        }
      } else if (objCtr[protoProp].__defineGetter__) {
        elemCtrProto.__defineGetter__(classListProp, classListGetter);
      }
    }(self));
  }
  /***************************************************************************/

  return {

    extend: function ( obj /* , extra arguments ... */) {
      var dest = obj, src = [].slice.call( arguments, 1 );
      src.forEach( function( copy ) {
        for( var prop in copy ){
          if( copy.hasOwnProperty( prop ) ){
            dest[ prop ] = copy[ prop ];
          }
        }
      });
    }, //extend

    // Convert an SMPTE timestamp to seconds
    smpteToSeconds: function( smpte ){
      var t = smpte.split( ":" );
      if( t.length === 1 ){
        return parseFloat( t[ 0 ], 10 );
      }
      if( t.length === 2 ){
        return parseFloat( t[ 0 ], 10 ) + parseFloat( t[ 1 ] / 12, 10 );
      }
      if( t.length === 3 ){
        return parseInt( t[ 0 ] * 60, 10 ) + parseFloat( t[ 1 ], 10 ) + parseFloat( t[ 2 ] / 12, 10 );
      }
      if( t.length === 4 ){
        return parseInt( t[ 0 ] * 3600, 10 ) + parseInt( t[ 1 ] * 60, 10 ) + parseFloat( t[ 2 ], 10 ) + parseFloat( t[ 3 ] / 12, 10 );
      }
    }, //smpteToSeconds

    secondsToSMPTE: function( time ){
      var timeStamp = new Date( 1970,0,1 ),
          seconds;
      timeStamp.setSeconds( time );
      seconds = timeStamp.toTimeString().substr( 0, 8 );
      if( seconds > 86399 ){
        seconds = Math.floor( (timeStamp - Date.parse("1/1/70") ) / 3600000) + seconds.substr(2);
      }
      return seconds;
    }, //secondsToSMPTE

    clone: function( obj ) {
      var newObj = {};
      for ( var prop in obj ) {
        if ( obj.hasOwnProperty( prop ) ) {
          newObj[ prop ] = obj[ prop ];
        } //if
      } //for
      return newObj;
    },

    // Fill in a given object with default properties.  Based on underscore (MIT License).
    // https://github.com/documentcloud/underscore/blob/master/underscore.js
    defaults: function( obj, source ){
      for( var prop in source ){
        if( obj[ prop ] === undefined ){
          obj[ prop ] = source[ prop ];
        }
      }
      return obj;
    },

    domFragment: function( inputString ) {
      var range = document.createRange(),
          fragment;
      range.selectNode( document.body.firstChild );
      fragment = range.createContextualFragment( inputString );

      if( fragment.childNodes.length === 1 ){
        var child = fragment.firstChild;
        fragment.removeChild( child );
        return child;
      }

      return fragment;
    }

  };

});

/* This Source Code Form is subject to the terms of the MIT license
 * If a copy of the MIT license was not distributed with this file, you can
 * obtain one at http://www.mozillapopcorn.org/butter-license.txt */

/**
 * Module: TrackEvent
 *
 * Supports a single event in the Media > Track > TrackEvent model.
 */
define('core/trackevent',[
          "./logger",
          "./eventmanager",
          "util/lang",
          "util/time",
          "./views/trackevent-view"
        ],
        function(
          Logger,
          EventManagerWrapper,
          LangUtil,
          TimeUtil,
          TrackEventView
        ){

  var __guid = 0;

  /**
   * Class: TrackEvent
   *
   * Represents and governs a single popcorn event.
   *
   * @param {Object} options: Options for initialization. Can contain the properties type, name, and popcornOptions. If the popcornOptions property is specified, its contents will be used to initialize the plugin instance associated with this TrackEvent.
   */
  var TrackEvent = function ( options ) {

    options = options || {};

    var _this = this,
        _id = "TrackEvent" + __guid++,
        _name = options.name || _id,
        _logger = new Logger( _id ),
        _track,
        _type = options.type + "",
        _popcornOptions = options.popcornOptions || {
          start: 0,
          end: 1
        },
        _view = new TrackEventView( this, _type, _popcornOptions ),
        _selected = false;

    EventManagerWrapper( _this );

    _this.popcornOptions = _popcornOptions;
    _this.popcornTrackEvent = null;

    function defaultValue( item ) {
      if ( item.default ) {
        return item.default;
      }
      return item.type === "number" ? 0 : "";
    }

    if( !_type ){
      _logger.log( "Warning: " + _id + " has no type." );
    } //if

    _popcornOptions.start = _popcornOptions.start || 0;
    _popcornOptions.start = TimeUtil.roundTime( _popcornOptions.start );
    _popcornOptions.end = _popcornOptions.end || _popcornOptions.start + 1;
    _popcornOptions.end = TimeUtil.roundTime( _popcornOptions.end );

    /**
     * Member: update
     *
     * Updates the event properties and runs sanity checks on input.
     *
     * @param {Object} updateOptions: Object containing plugin-specific properties to be updated for this TrackEvent.
     * @event trackeventupdatefailed: Occurs when an update operation failed because of conflicting times or other serious property problems. As the data property on this event is a string which represents the reason for failure.
     * @event trackeventupdated: Occurs whenan update operation succeeded.
     */
    this.update = function( updateOptions, applyDefaults ) {
      var failed = false,
          newStart = _popcornOptions.start,
          newEnd = _popcornOptions.end;

      if ( !isNaN( updateOptions.start ) ) {
        newStart = TimeUtil.roundTime( updateOptions.start );
      }
      if ( !isNaN( updateOptions.end ) ) {
        newEnd = TimeUtil.roundTime( updateOptions.end );
      }

      if ( newStart >= newEnd ){
        failed = "invalidtime";
      }
      else {
        if( _track && _track._media ){
          var media = _track._media;
          if( ( newStart > media.duration ) ||
              ( newEnd > media.duration ) ||
              ( newStart < 0 ) ) {
            failed = "invalidtime";
          }
        }
      }

      if( failed ){
        _this.dispatch( "trackeventupdatefailed", failed );
      } else {
        var _manifest = Popcorn.manifest[ _type ] && Popcorn.manifest[ _type ].options;
        if( _manifest ){
          for ( var prop in _manifest ) {
            if ( _manifest.hasOwnProperty( prop ) ) {
              if ( updateOptions[ prop ] === undefined ) {
                if ( applyDefaults ) {
                  _popcornOptions[ prop ] = defaultValue( _manifest[ prop ] );
                }
              } else {
                _popcornOptions[ prop ] = updateOptions[ prop ];
              }
            }
          }

          if ( !( "target" in _manifest ) && updateOptions.target ) {
            _popcornOptions.target = updateOptions.target;
          }
        }

        if( newStart ){
          _popcornOptions.start = newStart;
        }
        if( newEnd ){
          _popcornOptions.end = newEnd;
        }
        _view.update( _popcornOptions );
        _this.popcornOptions = _popcornOptions;
        _this.dispatch( "trackeventupdated", _this );
      }

    }; //update

    /**
     * Member: moveFrameLeft
     *
     * Moves the event to the left, or shrinks it by a specified amount.
     *
     * @param {Number} inc: Amount by which the event is to move or grow.
     * @param {Boolean} metaKey: State of the metaKey (windows, command, etc.). When true, the event duration is shortened.
     * @event trackeventupdated: Occurs whenan update operation succeeded.
     */
    this.moveFrameLeft = function( inc, metaKey ){
      if( !metaKey ) {
        if( _popcornOptions.start > inc ) {
          _popcornOptions.start -= inc;
          _popcornOptions.end -= inc;
        } else {
          _popcornOptions.end = _popcornOptions.end - _popcornOptions.start;
          _popcornOptions.start = 0;
        } // if
      } else if ( _popcornOptions.end - _popcornOptions.start > inc ) {
        _popcornOptions.end -= inc;
      } else {
        _popcornOptions.end = _popcornOptions.start;
      } // if
      _this.dispatch( "trackeventupdated", _this );
      _view.update( _popcornOptions );
    }; //moveFrameLeft

    /**
     * Member: moveFrameRight
     *
     * Moves the event to the right, or elongates it by a specified amount.
     *
     * @param {Number} inc: Amount by which the event is to move or grow.
     * @param {Boolean} metaKey: State of the metaKey (windows, command, etc.). When true, the event duration is lengthened.
     * @event trackeventupdated: Occurs whenan update operation succeeded.
     */
    this.moveFrameRight = function( inc, metaKey ){
      if( _popcornOptions.end < _track._media.duration - inc ) {
        _popcornOptions.end += inc;
        if( !metaKey ) {
          _popcornOptions.start += inc;
        }
      } else {
        if( !metaKey ) {
          _popcornOptions.start += _track._media.duration - _popcornOptions.end;
        }
        _popcornOptions.end = _track._media.duration;
      }
      _this.dispatch( "trackeventupdated", _this );
      _view.update( _popcornOptions );
    }; //moveFrameRight

    _view.listen( "trackeventviewupdated", function( e ){
      _popcornOptions.start = _view.start;
      _popcornOptions.end = _view.end;
      _this.dispatch( "trackeventupdated" );
    });

    Object.defineProperties( this, {

      /**
       * Property: _track
       *
       * Specifies the track on which this TrackEvent currently sites. When set, an update occurs.
       * @malleable: Yes, but not recommended. Butter will manipulate this value automatically. Other uses may yield unexpected results.
       */
      _track: {
        enumerable: true,
        get: function(){
          return _track;
        },
        set: function( val ){
          _track = val;
          _this.update( _popcornOptions );
        }
      },

      /**
       * Property: view
       *
       * A reference to the view object generated for this TrackEvent.
       * @malleable: No.
       */
      view: {
        enumerable: true,
        configurable: false,
        get: function(){
          return _view;
        }
      },

      /**
       * Property: type
       *
       * The type representing the popcorn plugin created and manipulated by this TrackEvent.
       * @malleable: No.
       */
      type: {
        enumerable: true,
        get: function(){
          return _type;
        }
      },

      /**
       * Property: name
       *
       * Name of this TrackEvent.
       * @malleable: No.
       */
      name: {
        enumerable: true,
        get: function(){
          return _name;
        }
      },

      /**
       * Property: id
       *
       * Name of this TrackEvent.
       * @malleable: No.
       */
      id: {
        enumerable: true,
        get: function(){
          return _id;
        }
      },

      /**
       * Property: selected
       *
       * Specifies the state of selection. When true, this TrackEvent is selected.
       *
       * @malleable: Yes.
       * @event trackeventselected: Dispatched when selected state changes to true.
       * @event trackeventdeselected: Dispatched when selected state changes to false.
       */
      selected: {
        enumerable: true,
        get: function(){
          return _selected;
        },
        set: function( val ){
          if( val !== _selected ){
            _selected = val;
            _view.selected = _selected;
            if( _selected ){
              _this.dispatch( "trackeventselected" );
            }
            else {
              _this.dispatch( "trackeventdeselected" );
            } //if
          } //if
        }
      },

      /**
       * Property: json
       *
       * Represents this TrackEvent in a portable JSON format.
       *
       * @malleable: Yes. Will import JSON in the same format that it was exported.
       * @event trackeventupdated: When this property is set, the TrackEvent's data will change, so a trackeventupdated event will be dispatched.
       */
      json: {
        enumerable: true,
        get: function(){
          return {
            id: _id,
            type: _type,
            popcornOptions: LangUtil.clone( _popcornOptions ),
            track: _track ? _track.name : undefined,
            name: _name
          };
        },
        set: function( importData ){
          _type = _popcornOptions.type = importData.type;
          if( importData.name ){
            _name = importData.name;
          }
          _popcornOptions = importData.popcornOptions;
          _this.popcornOptions = _popcornOptions;
          _view.type = _type;
          _view.update( _popcornOptions );
          _this.dispatch( "trackeventupdated", _this );
        }
      }
    }); //properties

  }; //TrackEvent

  return TrackEvent;

}); //define
;
/* This Source Code Form is subject to the terms of the MIT license
 * If a copy of the MIT license was not distributed with this file, you can
 * obtain one at http://www.mozillapopcorn.org/butter-license.txt */

define('core/track',[
          "./logger",
          "./eventmanager",
          "./trackevent",
          "./views/track-view"
        ],
        function(
          Logger,
          EventManagerWrapper,
          TrackEvent,
          TrackView
        ){

  var __guid = 0;

  var Track = function( options ){
    options = options || {};

    var _trackEvents = [],
        _id = "Track" + __guid++,
        _target = options.target,
        _logger = new Logger( _id ),
        _name = options.name || _id,
        _order = options.order || 0,
        _view = new TrackView( this ),
        _this = this;

    _this._media = null;

    EventManagerWrapper( _this );

    Object.defineProperties( this, {
      view: {
        enumerable: true,
        configurable: false,
        get: function(){
          return _view;
        }
      },
      order: {
        enumerable: true,
        get: function(){
          return _order;
        },
        set: function( val ){
          _order = val;
          _this.dispatch( "trackorderchanged", _order );
        }
      },
      target: {
        enumerable: true,
        get: function(){
          return _target;
        },
        set: function( val ){
          _target = val;
          _this.dispatch( "tracktargetchanged", _this );
          for( var i=0, l=_trackEvents.length; i<l; i++ ) {
            _trackEvents[ i ].target = val;
            _trackEvents[ i ].update({ target: val });
          } //for
          _logger.log( "target changed: " + val );
        }
      },
      name: {
        enumerable: true,
        get: function(){
          return _name;
        },
        set: function( name ) {
          _name = name;
          _this.dispatch( "tracknamechanged", _this );
        }
      },
      id: {
        enumerable: true,
        configurable: false,
        get: function(){
          return _id;
        }
      },
      json: {
        enumerable: true,
        get: function(){
          var exportJSONTrackEvents = [];
          for ( var i=0, l=_trackEvents.length; i<l; ++i ) {
            exportJSONTrackEvents.push( _trackEvents[ i ].json );
          }
          return {
            name: _name,
            id: _id,
            trackEvents: exportJSONTrackEvents
          };
        },
        set: function( importData ){
          if( importData.name ){
            _name = importData.name;
          }
          if( importData.trackEvents ){
            var importTrackEvents = importData.trackEvents;
            for( var i=0, l=importTrackEvents.length; i<l; ++i ){
              var newTrackEvent = new TrackEvent();
              newTrackEvent.json = importTrackEvents[ i ];
              _this.addTrackEvent( newTrackEvent );
            }
          }
        }
      },
      trackEvents: {
        enumerable: true,
        configurable: false,
        get: function(){
          return _trackEvents;
        }
      }
    });

    this.getTrackEventById = function( id ){
      for ( var i=0, l=_trackEvents.length; i<l; ++i) {
        if( _trackEvents[ i ].id === id ) {
          return _trackEvents[ i ];
        } //if
      } //for
    }; //getTrackEventById

    this.getTrackEventByName = function( name ){
      for ( var i=0, l=_trackEvents.length; i<l; ++i) {
        if( _trackEvents[ i ].name === name ) {
          return _trackEvents[ i ];
        } //if
      } //for
    }; //getTrackEventByName

    this.addTrackEvent = function ( trackEvent ){
      if( !( trackEvent instanceof TrackEvent ) ){
        trackEvent = new TrackEvent( trackEvent );
        trackEvent.update( trackEvent.popcornOptions, true );
      } //if
      if( _target ){
        trackEvent.target = _target;
      } //if
      trackEvent._track = _this;
      _trackEvents.push( trackEvent );
      trackEvent.track = _this;
      _this.chain( trackEvent, [
        "trackeventupdated",
        "trackeventselected",
        "trackeventdeselected",
        "trackeventeditrequested"
      ]);
      _view.addTrackEvent( trackEvent );
      trackEvent.track = _this;
      _this.dispatch( "trackeventadded", trackEvent );
      return trackEvent;
    }; //addTrackEvent

    this.removeTrackEvent = function( trackEvent ){
      var idx = _trackEvents.indexOf( trackEvent );
      if ( idx > -1 ) {
        _trackEvents.splice( idx, 1 );
        _this.unchain( trackEvent, [
          "trackeventupdated",
          "trackeventselected",
          "trackeventdeselected",
          "trackeventeditrequested"
        ]);
        _view.removeTrackEvent( trackEvent );
        trackEvent._track = null;
        _this.dispatch( "trackeventremoved", trackEvent );
        return trackEvent;
      } //if

    }; //removeEvent

    this.deselectEvents = function( except ){
      for( var i=0, l=_trackEvents.length; i<l; ++i ){
        if( _trackEvents[ i ] !== except ){
          _trackEvents[ i ].selected = false;
        } //if
      } //for
    }; //deselectEvents

  }; //Track

  return Track;

}); //define
;
/* This Source Code Form is subject to the terms of the MIT license
 * If a copy of the MIT license was not distributed with this file, you can
 * obtain one at http://www.mozillapopcorn.org/butter-license.txt */

(function() {

  define('editor/module',[ "core/eventmanager",
            "core/trackevent",
            "./editor"
          ], function(
            EventManagerWrapper,
            TrackEvent,
            Editor
          ){

    function EventEditor( butter, moduleOptions ){

      moduleOptions = moduleOptions || {};

      var _editors = {},
          _editorContainer,
          _openEditor,
          _this = this;

      EventManagerWrapper( _this );

      butter.listen( "trackeventcreated", function( e ){
        if( [ "target", "media" ].indexOf( e.data.by ) > -1 && butter.ui.contentState === "timeline" ){
          _this.edit( e.data.trackEvent );
        }
      });

      function editorClosed( e ){
        if( _openEditor.frame === "iframe" ){
          if( butter.ui.contentState === "editor" ){
            butter.ui.popContentState( "editor" );
          }
        }
        _openEditor.unlisten( "close", editorClosed );
        _openEditor = null;
      }

      function editorOpened( e ){
        if( _openEditor.frame === "iframe" ){
          if( butter.ui.contentState !== "editor" ){
            butter.ui.pushContentState( "editor" );
          }
        }
      }

      this.edit = function( trackEvent ){
        if ( !trackEvent || !( trackEvent instanceof TrackEvent ) ){
          throw new Error( "trackEvent must be valid to start an editor." );
        } //if

        var type = trackEvent.type;
        if ( !_editors[ type ] ){
          type = "default";
        } //if
        if( !_openEditor ){
          var editor = _editors[ type ];
          if( editor ){
            _openEditor = editor;
            editor.listen( "open", editorOpened );
            editor.open( trackEvent );
            editor.listen( "close", editorClosed );
          }
          else{
            throw new Error( "Editor " + type + " not found." );
          }
        }
      }; //edit

      this.add = function( source, type, frameType ){
        if ( !type || !source ) {
          throw new Error( "Can't create an editor without a plugin type and editor source" );
        } //if
        var editor = _editors[ type ] = new Editor( butter, source, type, frameType, _editorContainer );
        return editor;
      }; //add

      this.remove = function( type ){
        if ( !type ) {
          return;
        }
        var oldSource = _editors[ type ];
        _editors[ type ] = undefined;
       return oldSource;
      }; //remove

      function trackEventDoubleClicked( e ){
        _this.edit( e.target.trackEvent );
      } //trackEventDoubleClicked

      butter.listen( "trackeventadded", function( e ){
        e.data.view.listen( "trackeventdoubleclicked", trackEventDoubleClicked, false );
      });

      butter.listen( "trackeventremoved", function( e ){
        e.data.view.unlisten( "trackeventdoubleclicked", trackEventDoubleClicked, false );
      });

      this._start = function( onModuleReady ){
        var parentElement = document.createElement( "div" );
        parentElement.id = "butter-editor";

        _editorContainer = document.createElement( "div" );
        _editorContainer.id = "editor-container";
        parentElement.appendChild( _editorContainer );

        parentElement.classList.add( "fadable" );

        butter.ui.areas.work.addComponent( parentElement, {
          states: [ "editor" ],
          transitionIn: function(){
            parentElement.style.display = "block";
            setTimeout(function(){
              parentElement.style.opacity = "1";
            }, 0);
          },
          transitionInComplete: function(){

          },
          transitionOut: function(){
            if( _openEditor ){
              _openEditor.close();
            }
            parentElement.style.opacity = "0";
          },
          transitionOutComplete: function(){
            parentElement.style.display = "none";
          }
        });

        parentElement.style.display = "none";

        for( var editorName in moduleOptions ){
          if( moduleOptions.hasOwnProperty( editorName ) ){
            _this.add( moduleOptions[ editorName ], editorName );
          }
        }

        onModuleReady();
      }; //start

      butter.listen( "trackeventeditrequested", function( e ){
        _this.edit( e.target );
      });

    }

    EventEditor.__moduleName = "editor";

    return EventEditor;

  }); //define
}());

/* This Source Code Form is subject to the terms of the MIT license
 * If a copy of the MIT license was not distributed with this file, you can
 * obtain one at http://www.mozillapopcorn.org/butter-license.txt */

define('timeline/timebar',[ "util/lang", "./scrubber" ], function( util, Scrubber ) {

  var CANVAS_CONTAINER_PADDING = 5;

  return function( butter, media, tracksContainer, hScrollbar ){

    var _element = document.createElement( "div" ),
        _canvas = document.createElement( "canvas" ),
        _canvasContainer = document.createElement( "div" ),
        _media = media,
        _tracksContainer = tracksContainer,
        _scrubber = new Scrubber( butter, _element, _media, _tracksContainer, hScrollbar );

    _element.className = "time-bar";
    _canvasContainer.className = "time-bar-canvas-container";
    _canvasContainer.appendChild( _canvas );
    _element.appendChild( _canvasContainer );

    _canvas.addEventListener( "mousedown", _scrubber.onMouseDown, false );

    function drawTicks( zoom ) {
      var tracksContainerWidth = tracksContainer.container.getBoundingClientRect().width,
          width = Math.min( tracksContainerWidth, _tracksContainer.container.scrollWidth ),
          containerWidth = Math.min( width, _tracksContainer.element.offsetWidth - CANVAS_CONTAINER_PADDING );

      _canvasContainer.style.width = containerWidth + "px";

      var context = _canvas.getContext( "2d" );

      if ( _canvas.height !== _canvas.offsetHeight ) {
        _canvas.height = _canvas.offsetHeight;
      }
      if ( _canvas.width !== containerWidth ) {
        _canvas.width = containerWidth;
      }

      var inc = _tracksContainer.container.scrollWidth / _media.duration,
          textWidth = context.measureText( util.secondsToSMPTE( 5 ) ).width,
          padding = 20,
          lastPosition = 0,
          lastTimeDisplayed = -( ( textWidth + padding ) / 2 ),
          start = _tracksContainer.element.scrollLeft / inc,
          end = ( _tracksContainer.element.scrollLeft + containerWidth ) / inc;

      context.clearRect ( 0, 0, _canvas.width, _canvas.height );
      context.translate( -_tracksContainer.element.scrollLeft, 0 );
      context.beginPath();

      for ( var i = 1, l = _media.duration + 1; i < l; i++ ) {

        // If the current time is not in the viewport, just skip it
        if ( i + 1 < start ) {
          continue;
        }
        if ( i - 1 > end ) {
          break;
        }

        var position = i * inc;
        var spaceBetween = -~( position ) + ~( lastPosition );

        // ensure there is enough space to draw a seconds tick
        if ( spaceBetween > 3 ) {

          // ensure there is enough space to draw a half second tick
          if ( spaceBetween > 6 ) {

            context.moveTo( -~position - spaceBetween / 2, 0 );
            context.lineTo( -~position - spaceBetween / 2, 7 );

            // ensure there is enough space for quarter ticks
            if ( spaceBetween > 12 ) {

              context.moveTo( -~position - spaceBetween / 4 * 3, 0 );
              context.lineTo( -~position - spaceBetween / 4 * 3, 4 );

              context.moveTo( -~position - spaceBetween / 4, 0 );
              context.lineTo( -~position - spaceBetween / 4, 4 );

            }
          }
          context.moveTo( -~position, 0 );
          context.lineTo( -~position, 10 );

          if ( ( position - lastTimeDisplayed ) > textWidth + padding ) {

            lastTimeDisplayed = position;
            // text color
            context.fillStyle = "#999999";
            context.fillText( util.secondsToSMPTE( i ), -~position - ( textWidth / 2 ), 21 );
          }

          lastPosition = position;
        }
      }
      // stroke color
      context.strokeStyle = "#999999";
      context.stroke();
      context.translate( _tracksContainer.element.scrollLeft, 0 );

      _scrubber.update( containerWidth, zoom );
    }

    _tracksContainer.element.addEventListener( "scroll", drawTicks, false );

    window.addEventListener( "resize", drawTicks, false );

    this.update = function( zoom ) {
      drawTicks( zoom );
    };

    this.destroy = function(){
      _scrubber.destroy();
    }; //destroy

    Object.defineProperties( this, {
      element: {
        enumerable: true,
        get: function(){
          return _element;
        }
      }
    });

  }; //TimeBar

});

/* This Source Code Form is subject to the terms of the MIT license
 * If a copy of the MIT license was not distributed with this file, you can
 * obtain one at http://www.mozillapopcorn.org/butter-license.txt */

define('timeline/media',[
          "core/trackevent",
          "core/track",
          "core/eventmanager",
          "./track-container",
          "./scrollbars",
          "./timebar",
          "./zoombar",
          "./status",
          "./trackhandles",
          // Include util/lang so we have access to our classList shim for browsers that don't support it
          "util/lang"
        ],
        function(
          TrackEvent,
          Track,
          EventManagerWrapper,
          TrackContainer,
          Scrollbars,
          TimeBar,
          ZoomBar,
          Status,
          TrackHandles,
          LangUtil ) {

  var MIN_ZOOM = 300,
      DEFAULT_ZOOM = 0.5;

  function MediaInstance( butter, media ){
    function onTrackOrderChanged( orderedTracks ){
      _tracksContainer.orderTracks( orderedTracks );
    } //onTrackOrderChanged

    function zoomCallback( zoomLevel ){
      var nextZoom = MIN_ZOOM * zoomLevel + _zoomFactor;
      if( nextZoom !== _zoom ){
        _zoom = nextZoom;
        _tracksContainer.zoom = _zoom;
        updateUI();
      } //if
    } //zoomCallback

    var _this = this,
        _media = media,
        _tracksContainer = new TrackContainer( butter, media ),
        _rootElement = document.createElement( "div" ),
        _container = document.createElement( "div" ),
        _mediaStatusContainer = document.createElement( "div" ),
        _selectedTrackEvents = [],
        _hScrollBar = new Scrollbars.Horizontal( _tracksContainer ),
        _vScrollBar = new Scrollbars.Vertical( _tracksContainer, _rootElement ),
        _shrunken = false,
        _timebar = new TimeBar( butter, _media, _tracksContainer, _hScrollBar ),
        _zoombar = new ZoomBar( zoomCallback ),
        _status = new Status( _media ),
        _trackHandles = new TrackHandles( butter, _media, _tracksContainer, onTrackOrderChanged ),
        _trackEventHighlight = butter.config.value( "ui" ).trackEventHighlight || "click",
        _currentMouseDownTrackEvent,
        _zoomFactor,
        _zoom;

    _tracksContainer.setScrollbars( _hScrollBar, _vScrollBar );

    EventManagerWrapper( _this );

    _rootElement.className = "media-instance";
    _rootElement.id = "media-instance" + media.id;
    _container.className = "media-container";

    _mediaStatusContainer.className = "media-status-container";

    function snapToCurrentTime(){
      _tracksContainer.snapTo( _media.currentTime );
      _hScrollBar.update();
    }

    _media.listen( "mediaplaying", snapToCurrentTime );
    _media.listen( "mediapause", snapToCurrentTime );

    _media.listen( "trackeventselected", function( e ){
      _selectedTrackEvents.push( e.target );
    });

    _media.listen( "trackeventdeselected", function( e ){
      _selectedTrackEvents.splice( _selectedTrackEvents.indexOf( e.target ), 1 );
    });

    function blinkTarget( target ){
      if( target !== "Media Element" ){
        target = butter.getTargetByType( "elementID", target );
        if( target ){
          target.view.blink();
        } //if
      }
      else {
        _media.view.blink();
      } //if
    } //blinkTarget

    function onTrackEventMouseOver( e ){
      var trackEvent = e.trackEvent,
          corn = trackEvent.popcornOptions;

      if( corn.target ){
        blinkTarget( corn.target );
      } //if
    } //onTrackEventMouseOver

    function onTrackEventMouseOut( e ){
    }

    function onTrackEventMouseUp( e ){
      if( _currentMouseDownTrackEvent && _trackEventHighlight === "click" ){
        var corn = _currentMouseDownTrackEvent.popcornOptions;
        if( corn.target ){
          blinkTarget( corn.target );
        }
      }
    }

    function onTrackEventDragStarted( e ){
      _currentMouseDownTrackEvent = null;
    }

    function onTrackEventMouseDown( e ){
      var trackEvent = e.data.trackEvent,
          originalEvent = e.data.originalEvent;

      _currentMouseDownTrackEvent = trackEvent;

      trackEvent.selected = true;
      if( !originalEvent.shiftKey ){
        var tracks = _media.tracks;
        for( var t in tracks ){
          if( tracks.hasOwnProperty( t ) ){
            tracks[ t ].deselectEvents( trackEvent );
          } //if
        } //for
        butter.selectedEvents = [ trackEvent ];
      }
      else {
        butter.selectedEvents.push( trackEvent );
      } //if
    } //onTrackEventSelected

    function onMediaReady(){
      _zoomFactor = _container.clientWidth / _media.duration;
      _zoom = DEFAULT_ZOOM;
      _zoombar.zoom( _zoom );
      _tracksContainer.zoom = _zoom;
      updateUI();
      _this.dispatch( "ready" );
    }

    function onMediaReadyFirst(){
      _media.unlisten( "mediaready", onMediaReadyFirst );
      _media.listen( "mediaready", onMediaReady );

      _container.appendChild( _tracksContainer.element );
      _container.appendChild( _hScrollBar.element );
      _container.appendChild( _vScrollBar.element );
      _mediaStatusContainer.appendChild( _timebar.element );
      _mediaStatusContainer.appendChild( _status.statusElement );
      _mediaStatusContainer.appendChild( _status.muteElement );
      butter.ui.areas.statusbar.element.appendChild( _mediaStatusContainer );
      _rootElement.appendChild( _trackHandles.element );
      _rootElement.appendChild( _zoombar.element );
      _rootElement.appendChild( _container );

      _media.listen( "trackeventremoved", function( e ){
        var trackEvent = e.data;
        trackEvent.view.unlisten( "trackeventdragstarted", onTrackEventDragStarted );
        trackEvent.view.unlisten( "trackeventmouseup", onTrackEventMouseUp );
        trackEvent.view.unlisten( "trackeventmousedown", onTrackEventMouseDown );
        if( _trackEventHighlight === "hover" ){
          trackEvent.view.unlisten( "trackeventmouseover", onTrackEventMouseOver );
          trackEvent.view.unlisten( "trackeventmouseout", onTrackEventMouseOut );
        } //if
      });

      function onTrackEventAdded( e ){
        var trackEvent = e.data;
        trackEvent.view.listen( "trackeventdragstarted", onTrackEventDragStarted );
        trackEvent.view.listen( "trackeventmouseup", onTrackEventMouseUp );
        trackEvent.view.listen( "trackeventmousedown", onTrackEventMouseDown );
        if( _trackEventHighlight === "hover" ){
          trackEvent.view.listen( "trackeventmouseover", onTrackEventMouseOver );
          trackEvent.view.listen( "trackeventmouseout", onTrackEventMouseOut );
        }
      }

      function onTrackAdded( e ){
        var track = e.data;
        track.view.listen( "plugindropped", onPluginDropped );
        track.view.listen( "trackeventdropped", onTrackEventDropped );
        track.view.listen( "trackeventmousedown", onTrackEventMouseDown );
        if( _trackEventHighlight === "hover" ){
          track.view.listen( "trackeventmouseover", onTrackEventMouseOver );
          track.view.listen( "trackeventmouseout", onTrackEventMouseOut );
        }

        var existingEvents = track.trackEvents;
        for( var i=0; i<existingEvents.length; ++i ){
          onTrackEventAdded({
            data: existingEvents[ i ]
          });
        }

      }

      var existingTracks = _media.tracks;
      for( var i=0; i<existingTracks.length; ++i ){
        onTrackAdded({
          data: existingTracks[ i ]
        });
      }

      _media.listen( "trackadded", onTrackAdded );
      _media.listen( "trackeventadded", onTrackEventAdded );

      _media.listen( "trackremoved", function( e ){
        var track = e.data;
        track.view.unlisten( "plugindropped", onPluginDropped );
        track.view.unlisten( "trackeventdropped", onTrackEventDropped );
        track.view.listen( "trackeventmousedown", onTrackEventMouseDown );
        if( _trackEventHighlight === "hover" ){
          track.view.listen( "trackeventmouseover", onTrackEventMouseOver );
          track.view.listen( "trackeventmouseout", onTrackEventMouseOut );
        } //if
      });

      onMediaReady();
    }

    _media.listen( "mediaready", onMediaReadyFirst );

    function onPluginDropped( e ){

      var type = e.data.type,
          track = e.data.track,
          start = e.data.start;

      if( start + 1 > _media.duration ){
          start = _media.duration - 1;
      } //if

      var defaultTarget = butter.defaultTarget;
      if( !defaultTarget && butter.targets.length > 0 ){
        defaultTarget = butter.targets[ 0 ];
      } //if

      track.addTrackEvent({
        popcornOptions: {
          start: start,
          end: start + 1,
          target: defaultTarget.elementID
        },
        type: type
      });

      if( defaultTarget ){
        defaultTarget.view.blink();
      } //if

    } //onPluginDropped

    function onTrackEventDropped( e ){
      var search = _media.findTrackWithTrackEventId( e.data.trackEvent ),
          trackEvent = search.trackEvent,
          corn = trackEvent.popcornOptions;

      search.track.removeTrackEvent( trackEvent );

      var duration = corn.end- corn.start;
      corn.start = e.data.start;
      corn.end = corn.start + duration;

      trackEvent.update( corn );

      e.data.track.addTrackEvent( trackEvent );
    } //onTrackEventDropped


    this.destroy = function() {
      _rootElement.parentNode.removeChild( _rootElement );
      if( _mediaStatusContainer.parentNode ){
        butter.ui.areas.statusbar.element.removeChild( _mediaStatusContainer );
      }
      _timebar.destroy();
    }; //destroy

    this.hide = function() {
      _rootElement.style.display = "none";
    }; //hide

    this.show = function() {
      _rootElement.style.display = "block";
    }; //show

    function updateUI() {
      if( _media.duration ){
        _tracksContainer.update();
        _timebar.update( _zoom );
        _hScrollBar.update();
        _vScrollBar.update();
        _zoombar.update();
        _trackHandles.update();
      } //if
    } //updateUI

    butter.listen( "ready", function(){
      updateUI();
    });

    _tracksContainer.zoom = _zoom;

    Object.defineProperties( this, {
      zoom: {
        enumerable: true,
        get: function(){
          return _zoom;
        },
        set: function( val ){
          _zoom = val;
          updateUI();
        }
      },
      element: {
        enumerable: true,
        configurable: false,
        get: function(){
          return _rootElement;
        }
      },
      media: {
        enumerable: true,
        configurable: false,
        get: function(){
          return _media;
        }
      },
      shrunken: {
        enumerable: true,
        configurable: false,
        get: function(){
          return _shrunken;
        },
        set: function( val ){
          if( val !== _shrunken ){
            _shrunken = val;

          } //if
        }
      }
    });

  } //MediaInstance

  return MediaInstance;

});


/* This Source Code Form is subject to the terms of the MIT license
 * If a copy of the MIT license was not distributed with this file, you can
 * obtain one at http://www.mozillapopcorn.org/butter-license.txt */

define('timeline/module',[
          "core/logger",
          "./media"
        ],
        function(
          Logger,
          Media
        ){

  var Timeline = function( butter, options ){

    var _media = {},
        _currentMedia,
        _parentElement = document.createElement( "div" );

    _parentElement.id = "butter-timeline";

    _parentElement.classList.add( "fadable" );

    this._start = function( onModuleReady ){
      butter.ui.areas.work.addComponent( _parentElement, {
        states: [ "timeline" ],
        transitionIn: function(){
          _parentElement.style.visibility = "visible";
          setTimeout(function(){
            _parentElement.style.opacity = "1";
          }, 0);
        },
        transitionInComplete: function(){

        },
        transitionOut: function(){
          _parentElement.style.opacity = "0";
        },
        transitionOutComplete: function(){
          _parentElement.style.visibility = "hidden";
        }
      });

      butter.ui.registerStateToggleFunctions( "timeline", {
        transitionIn: function(){
          _parentElement.removeAttribute( "data-butter-disabled" );
        },
        transitionOut: function(){
          _parentElement.setAttribute( "data-butter-disabled", true );
        }
      });

      butter.ui.pushContentState( "timeline" );
      onModuleReady();
    };

    if( butter.ui ){
      butter.ui.listen( "uivisibilitychanged", function( e ){
        for( var m in _media ){
          if( _media.hasOwnProperty( m ) ){
            _media[ m ].shrunken = !e.data;
          } //if
        } //for
      });
    } //if

    this.findAbsolutePosition = function( obj ){
      var curleft = 0,
          curtop = 0;

      if( obj.offsetParent ) {
        do {
          curleft += obj.offsetLeft;
          curtop += obj.offsetTop;
        } while ( ( obj = obj.offsetParent ) );
      }
      //returns an array
      return [ curleft, curtop ];
    }; //findAbsolutePosition

    butter.listen( "mediaadded", function( event ){
      var mediaObject = event.data,
          media = new Media( butter, mediaObject );

      _media[ mediaObject.id ] = media;
      _parentElement.appendChild( media.element );

      function mediaChanged( event ){
        if ( _currentMedia !== _media[ event.data.id ] ){
          if ( _currentMedia ) {
            _currentMedia.hide();
          }
          _currentMedia = _media[ event.data.id ];
          if ( _currentMedia ) {
            _currentMedia.show();
          }
          butter.dispatch( "timelineready" );
        }
      }

      function mediaRemoved( event ){
        var mediaObject = event.data;
        if( _media[ mediaObject.id ] ){
          _media[ mediaObject.id ].destroy();
        }
        delete _media[ mediaObject.id ];
        if( _currentMedia && ( mediaObject.id === _currentMedia.media.id ) ){
          _currentMedia = undefined;
        }
        butter.unlisten( "mediachanged", mediaChanged );
        butter.unlisten( "mediaremoved", mediaRemoved );
      } //mediaRemoved

      butter.listen( "mediachanged", mediaChanged );
      butter.listen( "mediaremoved", mediaRemoved );
    });

    Object.defineProperties( this, {
      zoom: {
        get: function(){
          return _currentMedia.zoom;
        },
        set: function( val ){
          _currentMedia.zoom = val;
        }
      }
    });

  }; //Timeline

  Timeline.__moduleName = "timeline";

  return Timeline;
}); //define
;
/* This Source Code Form is subject to the terms of the MIT license
 * If a copy of the MIT license was not distributed with this file, you can
 * obtain one at http://www.mozillapopcorn.org/butter-license.txt */

define('plugin/plugin',[ "util/dragndrop", "util/lang" ], function( DragNDrop, LangUtils ){

  var PLUGIN_ELEMENT_PREFIX = "butter-plugin-";

  return function( id, pluginOptions ){
    pluginOptions = pluginOptions || {};

    var _id = "plugin" + id,
        _this = this,
        _name = pluginOptions.type,
        _path = pluginOptions.path,
        _manifest = {},
        _type = pluginOptions.type,
        _helper = document.getElementById( _this.type + "-icon" ) ||
                  document.getElementById( "default-icon" );

    // before we try and add the plugins script, make sure we have a path to it and we haven't already included it
    if( _path && !Popcorn.manifest[ _type ] ) {
      var head = document.getElementsByTagName( "HEAD" )[ 0 ],
          script = document.createElement( "script" );

      script.src = _path;
      head.appendChild( script );
    } //if

    Object.defineProperties( this, {
      id: {
        enumerable: true,
        get: function() {
          return _id;
        }
      },
      name: {
        enumerable: true,
        get: function() {
          return _name;
        }
      },
      path: {
        enumerable: true,
        get: function() {
          return _path;
        }
      },
      manifest: {
        enumerable: true,
        get: function() {
          return _manifest;
        },
        set: function( manifest ) {
          _manifest = manifest;
        }
      },
      type: {
        enumerable: true,
        get: function() {
          return _type;
        }
      },
      helper: {
        enumerable: true,
        get: function(){
          return _helper;
        }
      }
    });

    _helper = document.getElementById( _this.type + "-icon" ) || document.getElementById( "default-icon" );
    if( _helper ) { _helper = _helper.cloneNode( false ); }

    this.createElement = function ( butter, pattern ) {
      var pluginElement;
      if ( !pattern ) {
        pluginElement = document.createElement( "span" );
        pluginElement.innerHTML = _this.type + " ";
      }
      else {
        var patternInstance = pattern.replace( /\$type/g, _this.type );
        pluginElement = LangUtils.domFragment( patternInstance );
      }
      pluginElement.id = PLUGIN_ELEMENT_PREFIX + _this.type;
      pluginElement.setAttribute( "data-butter-plugin-type", _this.type );
      pluginElement.setAttribute( "data-butter-draggable-type", "plugin" );
      DragNDrop.helper( pluginElement, {
        image: _helper,
        start: function(){
          var targets = butter.targets,
              media = butter.currentMedia;
          media.view.blink();
          for( var i=0, l=targets.length; i<l; ++i ){
            targets[ i ].view.blink();
          }
        },
        stop: function(){
        }
      });
      this.element = pluginElement;
      return pluginElement;
    }; //createElement

  };
});

/* This Source Code Form is subject to the terms of the MIT license
 * If a copy of the MIT license was not distributed with this file, you can
 * obtain one at http://www.mozillapopcorn.org/butter-license.txt */

(function() {

  define('plugin/module',[ "core/logger",
            "util/dragndrop",
            "util/scrollbars",
            "./plugin-list",
            "./plugin"
          ],
          function(
            Logger,
            DragNDrop,
            Scrollbars,
            PluginList,
            Plugin
          ) {

    var __trackEventCSSRules = {},
        __cssRuleProperty = "data-butter-trackevent-type",
        __cssRulePrefix = "#butter-timeline .butter-track-event",
        __newStyleSheet = document.createElement( "style" );

    __newStyleSheet.type = "text/css";
    __newStyleSheet.media = "screen";
    __newStyleSheet.setAttribute( "data-butter-exclude", "true" );

    function colourHashFromType( type ){
      var hue = 0, saturation = 0, lightness = 0, srcString = type;

      // very simple hashing function
      while( srcString.length < 9 ){
        srcString += type;
      } //while
      hue = ( srcString.charCodeAt( 0 ) + srcString.charCodeAt( 3 ) + srcString.charCodeAt( 6 ) ) % ( ( srcString.charCodeAt( 8) * 5 ) % 360 );
      saturation = ( ( srcString.charCodeAt( 0 ) + srcString.charCodeAt( 2 ) + srcString.charCodeAt( 4 ) + srcString.charCodeAt( 6 ) ) % 100 ) * 0.05 + 95;
      lightness = ( ( srcString.charCodeAt( 1 ) + srcString.charCodeAt( 3 ) + srcString.charCodeAt( 5 ) + srcString.charCodeAt( 7 ) ) % 100 ) * 0.20 + 40;

      // bump up reds because they're hard to see
      if( hue < 20 || hue > 340 ){
        lightness += 10;
      } //if

      // dial back blue/greens a bit
      if( hue > 160 && hue < 200 ){
        lightness -= 10;
      } //if

      return {
        h: hue,
        s: saturation,
        l: lightness
      };
    } //colourHashFromType

    function createStyleForType( type ){
      var styleContent = "",
          hash = colourHashFromType( type );
      styleContent +=__cssRulePrefix + "[" + __cssRuleProperty + "=\"" + type + "\"]{";
      styleContent += "background: hsl( " + hash.h + ", " + hash.s + "%, " + hash.l + "% );";
      styleContent += "}";
      __newStyleSheet.innerHTML = __newStyleSheet.innerHTML + styleContent;
    } //createStyleForType

    var PluginManager = function( butter, moduleOptions ) {

      var _plugins = [],
          _container = document.createElement( "div" ),
          _listWrapper = document.createElement( "div" ),
          _listContainer = document.createElement( "div" ),
          _this = this,
          _pattern = '<div class="list-item $type_tool">$type</div>';

      _container.id = "butter-plugin";
      _listContainer.className = "list";
      _listWrapper.className = "list-wrapper";

      var title = document.createElement( "div" );
      title.className = "title";
      title.innerHTML = "<span>My Events</span>";
      _container.appendChild( title );
      _listWrapper.appendChild( _listContainer );
      _container.appendChild( _listWrapper );

      var _scrollbar = new Scrollbars.Vertical( _listWrapper, _listContainer );
      _container.appendChild( _scrollbar.element );

      this._start = function( onModuleReady ){
        if( butter.ui ){
          document.head.appendChild( __newStyleSheet );
          butter.ui.areas.tools.addComponent( _container );
          PluginList( butter );
        }
        if( moduleOptions && moduleOptions.plugins ){
          _this.add( moduleOptions.plugins, onModuleReady );
        }
        else{
          onModuleReady();
        }
      }; //start

      this.add = function( plugin, cb ) {

        if( plugin instanceof Array ) {
          var counter = 0,
              i = 0,
              l = 0,
              check = function() {
                if ( ++counter === plugin.length && cb ) {
                  cb();
                }
              };

          for( i = 0, l = plugin.length; i < l; i++ ) {
            _this.add( plugin[ i ], check );
          }
        } else {
          if( !__trackEventCSSRules[ plugin.type ] ){
            createStyleForType( plugin.type );
          }

          plugin = new Plugin( _plugins.length, plugin );

          var interval = setInterval(function( e ) {
            if( !Popcorn.manifest[ plugin.type ]) {
              return;
            }
            plugin.manifest = Popcorn.manifest[ plugin.type ];
            clearInterval( interval );
            if( cb ){
              cb();
            }
          }, 100);

          _plugins.push( plugin );
          if( moduleOptions.defaults && moduleOptions.defaults.indexOf( plugin.type ) > -1 ){
            _listContainer.appendChild( plugin.createElement( butter, _pattern ) );
          }
          butter.dispatch( "pluginadded", plugin );
        }

        _scrollbar.update();

        return plugin;
      }; //add

      this.remove = function( plugin ) {

        if( typeof plugin === "string" ) {
          plugin = this.get( plugin );
          if( !plugin ) {
            return;
          }
        }

        var i, l;

        for ( i = 0, l = _plugins.length; i < l; i++ ) {
          if( _plugins[ i ].name === plugin.name ) {
            var tracks = butter.tracks;
            for ( i = 0, l = tracks.length; i < l; i++ ) {
              var trackEvents = tracks[ i ].trackEvents;
              for( var k = 0, ln = trackEvents.length - 1; ln >= k; ln-- ) {
                if( trackEvents[ ln ].type === plugin.name ) {
                  tracks[ i ].removeTrackEvent( trackEvents[ ln ] );
                } //if
              } //for
            } //for

            _plugins.splice( i, 1 );
            l--;
            _listContainer.removeChild( plugin.element );

            var head = document.getElementsByTagName( "HEAD" )[ 0 ];
            for ( i = 0, l = head.children.length; i < l; i++ ) {
              if( head.children[ i ].getAttribute( "src" ) === plugin.path ) {
                head.removeChild( head.children[ i ] );
              }
            }

            butter.dispatch( "pluginremoved", plugin );
          }
        }

        _scrollbar.update();
      };

      this.clear = function () {
        while ( _plugins.length > 0 ) {
          var plugin = _plugins.pop();
          _listContainer.removeChild( plugin.element );
          butter.dispatch( "pluginremoved", plugin );
        }
      }; //clear

      this.get = function( name ) {
        for ( var i=0, l=_plugins.length; i<l; ++i ) {
          if ( _plugins[ i ].name === name ) {
            return _plugins[ i ];
          } //if
        } //for
      }; //get

      DragNDrop.droppable( _container, {
        drop: function( element ){
          if( element.getAttribute( "data-butter-draggable-type" ) === "plugin" ){
            var pluginType = element.getAttribute( "data-butter-plugin-type" ),
                plugin = _this.get( pluginType );
            if( plugin ){
              for( var i=0; i<_listContainer.childNodes.length; ++i ){
                if( _listContainer.childNodes[ i ].getAttribute( "data-butter-plugin-type" ) === pluginType ){
                  return;
                }
              }
              _listContainer.appendChild( plugin.createElement( butter, _pattern ) );
            }
          }
        }
      });
    }; //PluginManager

    PluginManager.__moduleName = "plugin";

    return PluginManager;

  }); //define
}());

/* This Source Code Form is subject to the terms of the MIT license
 * If a copy of the MIT license was not distributed with this file, you can
 * obtain one at http://www.mozillapopcorn.org/butter-license.txt */

define('modules',[
    "editor/module",
    "timeline/module",
    "cornfield/module",
    "plugin/module"
  ],
  function(){

  var moduleList = Array.prototype.slice.apply( arguments );

  return function( butter, config, onReady ){

    var modules = [],
        loadedModules = 0,
        readyModules = 0;

    for( var i=0; i<moduleList.length; ++i ){
      var name = moduleList[ i ].__moduleName;
      butter[ name ] = new moduleList[ i ]( butter, config.value( name ) );
      modules.push( butter[ name ] );
    } //for

    return {
      load: function( onLoaded ){
        function onModuleLoaded(){
          loadedModules++;
          if( loadedModules === modules.length ){
            onLoaded();
          }
        }

        for( var i=0; i<modules.length; ++i ){
          if( modules[ i ]._load ){
            modules[ i ]._load( onModuleLoaded );
          }
          else{
            loadedModules++;
          } //if
        } //for

        if( loadedModules === modules.length ){
          onLoaded();
        }
      },
      ready: function( onReady ){
        function onModuleReady(){
          readyModules++;
          if( readyModules === modules.length ){
            onReady();
          }
        }

        for( var i=0; i<modules.length; ++i ){
          if( modules[ i ]._start ){
            modules[ i ]._start( onModuleReady );
          }
          else{
            readyModules++;
          } //if
        } //for
      }
    };

  };

});

/*
 RequireJS text 1.0.8 Copyright (c) 2010-2011, The Dojo Foundation All Rights Reserved.
 Available via the MIT or new BSD license.
 see: http://github.com/jrburke/requirejs for details
*/
(function(){var k=["Msxml2.XMLHTTP","Microsoft.XMLHTTP","Msxml2.XMLHTTP.4.0"],m=/^\s*<\?xml(\s)+version=[\'\"](\d)*.(\d)*[\'\"](\s)*\?>/im,n=/<body[^>]*>\s*([\s\S]+)\s*<\/body>/im,i=typeof location!=="undefined"&&location.href,o=i&&location.protocol&&location.protocol.replace(/\:/,""),p=i&&location.hostname,q=i&&(location.port||void 0),j=[];define('text',[],function(){var e,l;e={version:"1.0.8",strip:function(a){if(a){var a=a.replace(m,""),c=a.match(n);c&&(a=c[1])}else a="";return a},jsEscape:function(a){return a.replace(/(['\\])/g,
"\\$1").replace(/[\f]/g,"\\f").replace(/[\b]/g,"\\b").replace(/[\n]/g,"\\n").replace(/[\t]/g,"\\t").replace(/[\r]/g,"\\r")},createXhr:function(){var a,c,b;if(typeof XMLHttpRequest!=="undefined")return new XMLHttpRequest;else if(typeof ActiveXObject!=="undefined")for(c=0;c<3;c++){b=k[c];try{a=new ActiveXObject(b)}catch(f){}if(a){k=[b];break}}return a},parseName:function(a){var c=!1,b=a.indexOf("."),f=a.substring(0,b),a=a.substring(b+1,a.length),b=a.indexOf("!");b!==-1&&(c=a.substring(b+1,a.length),
c=c==="strip",a=a.substring(0,b));return{moduleName:f,ext:a,strip:c}},xdRegExp:/^((\w+)\:)?\/\/([^\/\\]+)/,useXhr:function(a,c,b,f){var d=e.xdRegExp.exec(a),g;if(!d)return!0;a=d[2];d=d[3];d=d.split(":");g=d[1];d=d[0];return(!a||a===c)&&(!d||d===b)&&(!g&&!d||g===f)},finishLoad:function(a,c,b,f,d){b=c?e.strip(b):b;d.isBuild&&(j[a]=b);f(b)},load:function(a,c,b,f){if(f.isBuild&&!f.inlineText)b();else{var d=e.parseName(a),g=d.moduleName+"."+d.ext,h=c.toUrl(g),r=f&&f.text&&f.text.useXhr||e.useXhr;!i||r(h,
o,p,q)?e.get(h,function(c){e.finishLoad(a,d.strip,c,b,f)}):c([g],function(a){e.finishLoad(d.moduleName+"."+d.ext,d.strip,a,b,f)})}},write:function(a,c,b){if(j.hasOwnProperty(c)){var f=e.jsEscape(j[c]);b.asModule(a+"!"+c,"define(function () { return '"+f+"';});\n")}},writeFile:function(a,c,b,f,d){var c=e.parseName(c),g=c.moduleName+"."+c.ext,h=b.toUrl(c.moduleName+"."+c.ext)+".js";e.load(g,b,function(){var b=function(a){return f(h,a)};b.asModule=function(a,b){return f.asModule(a,h,b)};e.write(a,g,
b,d)},d)}};if(e.createXhr())e.get=function(a,c){var b=e.createXhr();b.open("GET",a,!0);b.onreadystatechange=function(){b.readyState===4&&c(b.responseText)};b.send(null)};else if(typeof process!=="undefined"&&process.versions&&process.versions.node)l=require.nodeRequire("fs"),e.get=function(a,c){var b=l.readFileSync(a,"utf8");b.indexOf("\ufeff")===0&&(b=b.substring(1));c(b)};else if(typeof Packages!=="undefined")e.get=function(a,c){var b=new java.io.File(a),f=java.lang.System.getProperty("line.separator"),
b=new java.io.BufferedReader(new java.io.InputStreamReader(new java.io.FileInputStream(b),"utf-8")),d,e,h="";try{d=new java.lang.StringBuffer;(e=b.readLine())&&e.length()&&e.charAt(0)===65279&&(e=e.substring(1));for(d.append(e);(e=b.readLine())!==null;)d.append(f),d.append(e);h=String(d.toString())}finally{b.close()}c(h)};return e})})();

define('text!default-config.json',[],function () { return '{\n  "name": "default-config",\n  "baseDir": "../",\n  "snapshotHTMLOnReady": true,\n  "scrapePage": true,\n  "editor": {\n    "default": "{{baseDir}}editors/default-editor.html",\n    "googlemap": "{{baseDir}}editors/googlemap-editor.html"\n  },\n  "ui": {\n    "enabled": true,\n    "trackEventHighlight": "click",\n    "title": "Popcorn Maker"\n  },\n  "mediaDefaults": {\n    "frameAnimation": true\n  },\n  "plugin": {\n    "plugins": [\n      {\n        "type": "attribution",\n        "path": "{{baseDir}}external/popcorn-js/plugins/attribution/popcorn.attribution.js"\n      },\n      {\n        "type": "flickr",\n        "path": "{{baseDir}}external/popcorn-js/plugins/flickr/popcorn.flickr.js"\n      },\n      {\n        "type": "webpage",\n        "path": "{{baseDir}}external/popcorn-js/plugins/webpage/popcorn.webpage.js"\n      },\n      {\n        "type": "text",\n        "path": "{{baseDir}}external/popcorn-js/plugins/text/popcorn.text.js"\n      },\n      {\n        "type": "googlemap",\n        "path": "{{baseDir}}external/popcorn-js/plugins/googlemap/popcorn.googlemap.js"\n      },\n      {\n        "type": "image",\n        "path": "{{baseDir}}external/popcorn-js/plugins/image/popcorn.image.js"\n      },\n      {\n        "type": "twitter",\n        "path": "{{baseDir}}external/popcorn-js/plugins/twitter/popcorn.twitter.js"\n      },\n      {\n        "type": "wikipedia",\n        "path": "{{baseDir}}external/popcorn-js/plugins/wikipedia/popcorn.wikipedia.js"\n      },\n      {\n        "type": "mediaspawner",\n        "path": "{{baseDir}}external/popcorn-js/plugins/mediaspawner/popcorn.mediaspawner.js"\n      }\n    ],\n    "defaults": [\n      "text",\n      "image",\n      "googlemap"\n    ]\n  },\n  "player": {\n    "players": [\n      {\n        "type": "youtube",\n        "path": "{{baseDir}}external/popcorn-js/players/youtube/popcorn.youtube.js"\n      },\n      {\n        "type": "soundcloud",\n        "path": "{{baseDir}}external/popcorn-js/players/soundcloud/popcorn.soundcloud.js"\n      },\n      {\n        "type": "vimeo",\n        "path": "{{baseDir}}external/popcorn-js/players/vimeo/popcorn.vimeo.js"\n      }\n    ],\n    "defaults": [\n      "youtube",\n      "soundcloud",\n      "vimeo"\n    ]\n  },\n  "dirs": {\n    "popcorn-js": "{{baseDir}}external/popcorn-js/",\n    "css": "{{baseDir}}css/",\n    "dialogs": "{{baseDir}}dialogs/",\n    "resources": "{{baseDir}}resources/"\n  },\n  "icons": {\n    "default": "popcorn-icon.png",\n    "image": "image-icon.png"\n  }\n}\n';});

define('text!layouts/ua-warning.html',[],function () { return '<div class="butter-ua-warning" data-butter-exclude>Your web browser may lack some functionality expected by Butter to function properly. Please upgrade your browser or <a href="https://webmademovies.lighthouseapp.com/projects/65733-popcorn-maker">file a bug</a> to find out why your browser isn\'t fully supported. Click <a href="#" class="close-button">here</a> to remove this warning.</div>';});

define('text!layouts/media-view.html',[],function () { return '<div class="butter-media-properties" data-butter-exclude="true">\n  <p class="edit-message">Edit source...</p>\n  <div class="container">\n    <div class="inner-container">\n      <h3>Video/Audio URL</h3>\n      <div class="url-group">\n        <div class="url fade-in"><input type="text" /><button class="remove">-</button></div>\n      </div>\n      <p class="form-field-notes"></p>\n      <button class="save">Save</button><button class="add-url">Add Alternate URL</button>\n      <div class="loading-container"></div>\n    </div>\n  </div>\n</div>';});

define('core/views/media-view',[ "ui/page-element", "ui/logo-spinner", "util/lang", "ui/widget/textbox", "text!layouts/media-view.html" ],
  function( PageElement, LogoSpinner, LangUtils, TextboxWrapper, HTML_TEMPLATE ){

  var DEFAULT_SUBTITLE = "Supports HTML5 video and YouTube",
      MOUSE_OUT_DURATION = 300,
      MAX_URLS = 4;

  return function( media, options ){
    var _media = media,
        _pageElement,
        _onDropped = options.onDropped || function(){},
        _closeSignal = false,
        _logoSpinner;

    var _propertiesElement = LangUtils.domFragment( HTML_TEMPLATE ),
        _container = _propertiesElement.querySelector( "div.container" ),
        _urlContainer = _propertiesElement.querySelector( "div.url" ),
        _urlTextbox = _propertiesElement.querySelector( "input[type='text']" ),
        _subtitle = _propertiesElement.querySelector( ".form-field-notes" ),
        _changeButton = _propertiesElement.querySelector( "button.save" ),
        _addUrlButton = _propertiesElement.querySelector( "button.add-url" ),
        _urlList = _propertiesElement.querySelector( "div.url-group" ),
        _loadingContainer = _propertiesElement.querySelector( ".loading-container" );

    var _containerDims;

    function setDimensions( state ){
      if( state ){
        _closeSignal = false;
        _propertiesElement.style.width = _containerDims.width + "px";
        _propertiesElement.style.height = _containerDims.height + "px";
      }
      else {
        _propertiesElement.style.width = "";
        _propertiesElement.style.height = "";
      }
    }

    function prepareTextbox( textbox ){
      TextboxWrapper( textbox );
    }

    function addUrl() {
      var newContainer = _urlContainer.cloneNode( true );
      newContainer.classList.remove( "fade-in" );
      _urlList.appendChild( newContainer );

      // force the browser to wait a tick before applying this class
      // so fade-in effect occurs
      setTimeout(function(){
        newContainer.classList.add( "fade-in" );
      }, 0);

      _containerDims.width = _container.clientWidth;
      _containerDims.height = _container.clientHeight;
      setDimensions( true );

      newContainer.querySelector( "button.remove" ).addEventListener( "click", function ( e ) {
        removeUrl( newContainer );
      }, false );

      prepareTextbox( newContainer.querySelector( "input[type='text']" ) );

      if ( _urlList.querySelectorAll( "input[type='text']" ).length >= MAX_URLS ) {
        _addUrlButton.style.visibility = "hidden";
      }
    }

    function removeUrl( container ){
      _urlList.removeChild( container );
      _containerDims.width = _container.clientWidth;
      _containerDims.height = _container.clientHeight;
      setDimensions( true );
      if ( _urlList.querySelectorAll( "input[type='text']" ).length < MAX_URLS ) {
        _addUrlButton.style.visibility = "visible";
      }
    }

    _addUrlButton.addEventListener( "click", function( e ) {
      addUrl();
    }, false );

    prepareTextbox( _urlTextbox );

    _propertiesElement.addEventListener( "mouseover", function( e ) {
      e.stopPropagation();
      _propertiesElement.classList.add( "open" );
      // silly hack to stop jittering of width/height
      if ( !_containerDims ) {
        _containerDims = {
          width: _container.clientWidth,
          height: _container.clientHeight
        };
      }
      setDimensions( true );
    }, true );

    _propertiesElement.addEventListener( "mouseout", function( e ) {
      setTimeout(function(){
        if ( _closeSignal ) {
          setDimensions( false );
          _propertiesElement.classList.remove( "open" );
        }
      }, MOUSE_OUT_DURATION );
      _closeSignal = true;
    }, false );

    _logoSpinner = LogoSpinner( _loadingContainer );

    _subtitle.innerHTML = DEFAULT_SUBTITLE;

    function showError( state, message ){
      if( state ){
        _subtitle.innerHTML = message;
      }
      else{
        _subtitle.innerHTML = DEFAULT_SUBTITLE;
      }
    }

    function changeUrl(){
      var validTextboxes = [],
          textboxes = _container.querySelectorAll( "input[type='text']" ),
          errorTextboxes = [];

      _subtitle.classList.add( "form-ok" );
      _subtitle.classList.remove( "form-error" );

      for ( var i = 0, len = textboxes.length; i < len; i++ ) {
        textboxes[ i ].classList.add( "form-ok" );
        textboxes[ i ].classList.remove( "form-error" );
        if ( testUrl( textboxes[ i ].value ) ) {
          validTextboxes.push( textboxes[ i ].value );
        }
        else {
          _subtitle.classList.remove( "form-ok" );
          _subtitle.classList.add( "form-error" );
          errorTextboxes.push( textboxes[ i ] );
          textboxes[ i ].classList.remove( "form-ok" );
          textboxes[ i ].classList.add( "form-error" );
        }
      }

      if ( errorTextboxes.length ) {
        showError( true, "URL(s) not valid. Please use http://..." );
      }
      else if ( validTextboxes.length ) {
        _subtitle.innerHTML = "URL changed.";
        media.url = validTextboxes;
      }

    }

    function testUrl(url) {
      var test = /(http|https):\/\/(\w+:{0,1}\w*@)?(\S+)(:[0-9]+)?(\/|\/([\w#!:.?+=&%@!\-\/]))?/;
      return url.match(test);
    }

    _urlTextbox.addEventListener( "keypress", function( e ){
      if( e.which === 13 ){
        changeUrl();
      }
    }, false );
    _changeButton.addEventListener( "click", changeUrl, false );

    _logoSpinner.start();
    _changeButton.setAttribute( "disabled", true );

    function updateURLS(){
      if( typeof( media.url ) === "string" ) {
        _urlTextbox.value = media.url;
      }
      else if ( media.url.length ) {
        var urls = media.url,
            currentUrls = _urlList.querySelectorAll( "input[type='text']" );
        while ( currentUrls.length < urls.length ) {
          addUrl();
          currentUrls = _urlList.querySelectorAll( "input[type='text']" );
        }
        while ( currentUrls.length > urls.length ) {
          removeUrl( currentUrls[ currentUrls.length - 1 ] );
          currentUrls = _urlList.querySelectorAll( "input[type='text']" );
        }
        for ( var i = 0; i < urls.length; ++i ) {
          currentUrls[ i ].value = urls[ i ];
        }
      }
      else {
        throw "Media url is expected value (not string or array): " + media.url;
      }
    }

    media.listen( "mediacontentchanged", function( e ){
      updateURLS();
      showError( false );
      _changeButton.setAttribute( "disabled", true );
      _logoSpinner.start();
    });

    media.listen( "mediafailed", function( e ){
      showError( true, "Media failed to load. Check your URL." );
      _changeButton.removeAttribute( "disabled" );
      _urlTextbox.className += " form-error";
      _subtitle.className += " form-error";
      _logoSpinner.stop();
    });

    media.listen( "mediaready", function( e ){
      showError( false );
      _changeButton.removeAttribute( "disabled" );
      _logoSpinner.stop();
    });

    this.blink = function(){
      _pageElement.blink();
    };

    this.destroy = function() {
      _pageElement.destroy();
      _pageElement = null;
    };

    function pageElementMoved( e ){
      var rect = e ? e.data : _pageElement.element.getBoundingClientRect();
      _propertiesElement.style.left = rect.left + "px";
      _propertiesElement.style.top = rect.top + "px";
    }

    this.update = function(){
      updateURLS();

      var targetElement = document.getElementById( _media.target );

      if( _pageElement ){
        _pageElement.destroy();
      } //if
      _pageElement = new PageElement( _media.target, {
        drop: function( element ){
          _onDropped( element );
        }
      },
      {
        highlightClass: "butter-media-highlight"
      });

      if( targetElement ){
        if( !_propertiesElement.parentNode ){
          document.body.appendChild( _propertiesElement );
        }
        _pageElement.listen( "moved", pageElementMoved );
      }
    };

  };

});

/* This Source Code Form is subject to the terms of the MIT license
 * If a copy of the MIT license was not distributed with this file, you can
 * obtain one at http://www.mozillapopcorn.org/butter-license.txt */

(function() {
  define('core/media',[
            "core/logger",
            "core/eventmanager",
            "core/track",
            "core/popcorn-wrapper",
            "core/views/media-view"
          ],
          function( Logger, EventManagerWrapper, Track, PopcornWrapper, MediaView ){

    var MEDIA_ELEMENT_SAFETY_POLL_INTERVAL = 500,
        MEDIA_ELEMENT_SAFETY_POLL_ATTEMPTS = 10;

    var __guid = 0;

    var Media = function ( mediaOptions ) {
      mediaOptions = mediaOptions || {};

      EventManagerWrapper( this );

      var _tracks = [],
          _id = "Media" + __guid++,
          _logger = new Logger( _id ),
          _name = mediaOptions.name || _id,
          _url = mediaOptions.url,
          _ready = false,
          _target = mediaOptions.target,
          _registry,
          _currentTime = 0,
          _duration = 0,
          _popcornOptions = mediaOptions.popcornOptions,
          _mediaUpdateInterval,
          _view,
          _this = this,
          _popcornWrapper = new PopcornWrapper( _id, {
            popcornEvents: {
              muted: function(){
                _this.dispatch( "mediamuted", _this );
              },
              unmuted: function(){
                _this.dispatch( "mediaunmuted", _this );
              },
              volumechange: function(){
                _this.dispatch( "mediavolumechange", _popcornWrapper.volume );
              },
              timeupdate: function(){
                _currentTime = _popcornWrapper.currentTime;
                _this.dispatch( "mediatimeupdate", _this );
              },
              pause: function(){
                clearInterval( _mediaUpdateInterval );
                _this.dispatch( "mediapause" );
              },
              playing: function(){
                _mediaUpdateInterval = setInterval( function(){
                  _currentTime = _popcornWrapper.currentTime;
                }, 10 );
                _this.dispatch( "mediaplaying" );
              },
              ended: function(){
                _this.dispatch( "mediaended" );
              }
            },
            prepare: function(){
              _this.duration = _popcornWrapper.duration;
              _ready = true;
              for( var i = 0, l = _tracks.length; i < l; i++ ) {
                var te = _tracks[ i ].trackEvents;
                for( var j = 0, k = te.length; j < k; j++ ) {
                  _popcornWrapper.updateEvent( te[ j ] );
                }
              }
              if( _view ){
                _view.update();
              }
              _this.dispatch( "mediaready" );
            },
            constructing: function(){
              if( _view ){
                _view.update();
              }
            },
            timeout: function(){
              _this.dispatch( "mediatimeout" );
              _this.dispatch( "mediafailed", "timeout" );
            },
            fail: function( e ){
              _this.dispatch( "mediafailed", "error" );
            },
            playerTypeRequired: function( type ){
              _this.dispatch( "mediaplayertyperequired", type );
            },
            setup: {
              target: _target,
              url: _url
            }
          });

      this.popcornCallbacks = null;
      this.popcornScripts = null;

      this.createView = function(){
        if ( !_view ) {
          _view = new MediaView( this, {
            onDropped: onDroppedOnView
          });
        }
      };

      this.destroy = function(){
        _popcornWrapper.unbind();
        if ( _view ) {
          _view.destroy();
        }
      };

      this.clear = function(){
        while( _tracks.length > 0 ){
          _this.removeTrack( _tracks[ 0 ] );
        }
      };

      function onDroppedOnView( e ){
        _this.dispatch( "trackeventrequested", e );
      }

      function onTrackEventAdded( e ){
        _popcornWrapper.updateEvent( e.data );
      } //onTrackEventAdded

      function onTrackEventUpdated( e ){
        _popcornWrapper.updateEvent( e.target );
      } //onTrackEventUpdated

      function onTrackEventRemoved( e ){
        _popcornWrapper.destroyEvent( e.data );
      } //onTrackEventRemoved

      this.addTrack = function ( track ) {
        if ( !( track instanceof Track ) ) {
          track = new Track( track );
        } //if
        track.order = _tracks.length;
        track._media = _this;
        _tracks.push( track );
        _this.chain( track, [
          "tracktargetchanged",
          "trackeventadded",
          "trackeventremoved",
          "trackeventupdated",
          "trackeventselected",
          "trackeventdeselected",
          "trackeventeditrequested"
        ]);
        track.popcorn = _popcornWrapper;
        track.listen( "trackeventadded", onTrackEventAdded );
        track.listen( "trackeventupdated", onTrackEventUpdated );
        track.listen( "trackeventremoved", onTrackEventRemoved );
        _this.dispatch( "trackadded", track );
        var trackEvents = track.trackEvents;
        if ( trackEvents.length > 0 ) {
          for ( var i=0, l=trackEvents.length; i<l; ++i ) {
            track.dispatch( "trackeventadded", trackEvents[ i ] );
          } //for
        } //if
        return track;
      }; //addTrack

      this.getTrackById = function( id ){
        for( var i=0, l=_tracks.length; i<l; ++i ){
          if( _tracks[ i ].id === id ){
            return _tracks[ i ];
          } //if
        } //for
      }; //getTrackById

      this.removeTrack = function ( track ) {
        var idx = _tracks.indexOf( track );
        if ( idx > -1 ) {
          _tracks.splice( idx, 1 );
          var events = track.trackEvents;
          for ( var i=0, l=events.length; i<l; ++i ) {
            events[ i ].selected = false;
            track.dispatch( "trackeventremoved", events[ i ] );
          } //for
          _this.unchain( track, [
            "tracktargetchanged",
            "trackeventadded",
            "trackeventremoved",
            "trackeventupdated",
            "trackeventselected",
            "trackeventdeselected",
            "trackeventeditrequested"
          ]);
          track.unlisten( "trackeventadded", onTrackEventAdded );
          track.unlisten( "trackeventupdated", onTrackEventUpdated );
          track.unlisten( "trackeventremoved", onTrackEventRemoved );
          _this.dispatch( "trackremoved", track );
          track._media = null;
          return track;
        } //if
      }; //removeTrack

      this.findTrackWithTrackEventId = function( id ){
        for( var i=0, l=_tracks.length; i<l; ++i ){
          var te = _tracks[ i ].getTrackEventById( id );
          if( te ){
            return {
              track: _tracks[ i ],
              trackEvent: te
            };
          }
        } //for
      }; //findTrackWithTrackEventId

      this.getManifest = function( name ) {
        return _registry[ name ];
      }; //getManifest

      function setupContent(){
        if( _url && _target ){
          _popcornWrapper.prepare( _url, _target, _popcornOptions, _this.popcornCallbacks, _this.popcornScripts );
        } //if
        if( _view ){
          _view.update();
        }
      }

      this.setupContent = setupContent;

      this.onReady = function( callback ){
        function onReady( e ){
          callback( e );
          _this.unlisten( "mediaready", onReady );
        }
        if( _ready ){
          callback();
        }
        else{
          _this.listen( "mediaready", onReady );
        }
      };

      this.pause = function(){
        _popcornWrapper.pause();
      }; //pause

      this.play = function(){
        _popcornWrapper.play();
      };

      this.generatePopcornString = function( callbacks, scripts ){
        var popcornOptions = _popcornOptions || {};

        callbacks = callbacks || _this.popcornCallbacks;
        scripts = scripts || _this.popcornScripts;

        var collectedEvents = [];
        for ( var i = 0, l = _tracks.length; i < l; ++i ) {
          collectedEvents = collectedEvents.concat( _tracks[ i ].trackEvents );
        }

        /* TODO: determine if we need to turn on frameAnimation or not before calling generatePopcornString
         * for now we default to off when exporting by setting frameAnimation to false. This should be handled in #1370.
         */
        popcornOptions.frameAnimation = false;
        return _popcornWrapper.generatePopcornString( popcornOptions, _url, _target, null, callbacks, scripts, collectedEvents );
      };

      Object.defineProperties( this, {
        ended: {
          enumerable: true,
          get: function(){
            if( _popcornWrapper.popcorn ){
              return _popcornWrapper.popcorn.ended();
            }
            return false;
          }
        },
        url: {
          enumerable: true,
          get: function() {
            return _url;
          },
          set: function( val ) {
            if ( _url !== val ) {
              _url = val;
              _popcornWrapper.clear( _target );
              setupContent();
              _this.dispatch( "mediacontentchanged", _this );
            }
          }
        },
        target: {
          get: function() {
            return _target;
          },
          set: function( val ) {
            if ( _target !== val ) {
              _popcornWrapper.clear( _target );
              _target = val;
              setupContent();
              _this.dispatch( "mediatargetchanged", _this );
            }
          },
          enumerable: true
        },
        muted: {
          enumerable: true,
          get: function(){
            return _popcornWrapper.muted;
          },
          set: function( val ){
            _popcornWrapper.muted = val;
          }
        },
        ready:{
          enumerable: true,
          get: function(){
            return _ready;
          }
        },
        name: {
          get: function(){
            return _name;
          },
          enumerable: true
        },
        id: {
          get: function(){
            return _id;
          },
          enumerable: true
        },
        tracks: {
          get: function(){
            return _tracks;
          },
          enumerable: true
        },
        currentTime: {
          get: function(){
            return _currentTime;
          },
          set: function( time ){
            if( time !== undefined ){
              _currentTime = time;
              if( _currentTime < 0 ){
                _currentTime = 0;
              }
              if( _currentTime > _duration ){
                _currentTime = _duration;
              } //if
              _popcornWrapper.currentTime = _currentTime;
              _this.dispatch( "mediatimeupdate", _this );
            } //if
          },
          enumerable: true
        },
        duration: {
          get: function(){
            return _duration;
          },
          set: function( time ){
            if( time ){
              _duration = time;
              _logger.log( "duration changed to " + _duration );
              _this.dispatch( "mediadurationchanged", _this );
            }
          },
          enumerable: true
        },
        json: {
          get: function(){
            var exportJSONTracks = [];
            for( var i=0, l=_tracks.length; i<l; ++i ){
              exportJSONTracks.push( _tracks[ i ].json );
            }
            return {
              id: _id,
              name: _name,
              url: _url,
              target: _target,
              duration: _duration,
              tracks: exportJSONTracks
            };
          },
          set: function( importData ){
            if( importData.name ) {
              _name = importData.name;
            }
            if( importData.target ){
              _this.target = importData.target;
            }
            if( importData.url ){
              _this.url = importData.url;
            }
            if( importData.tracks ){
              var importTracks = importData.tracks;
              for( var i=0, l=importTracks.length; i<l; ++i ){
                var newTrack = new Track();
                newTrack.json = importTracks[ i ];
                _this.addTrack( newTrack );
              }
            }
          },
          enumerable: true
        },
        registry: {
          get: function(){
            return _registry;
          },
          set: function( val ){
            _registry = val;
          },
          enumerable: true
        },
        popcorn: {
          enumerable: true,
          get: function(){
            return _popcornWrapper;
          }
        },
        paused: {
          enumerable: true,
          get: function(){
            return _popcornWrapper.paused;
          },
          set: function( val ){
            _popcornWrapper.paused = val;
          }
        },
        volume: {
          enumerable: true,
          get: function(){
            return _popcornWrapper.volume;
          },
          set: function( val ){
            _popcornWrapper.volume = val;
          }
        },
        view: {
          enumerable: true,
          get: function(){
            return _view;
          }
        },
        popcornOptions: {
          enumerable: true,
          get: function(){
            return _popcornOptions;
          },
          set: function( val ){
            _popcornOptions = val;
            _this.dispatch( "mediapopcornsettingschanged", _this );
            setupContent();
          }
        }
      });

      // There is an edge-case where currentSrc isn't set yet, but everything else about the video is valid.
      // So, here, we wait for it to be set.
      var targetElement = document.getElementById( _target );
      if( targetElement && [ "VIDEO", "AUDIO" ].indexOf( targetElement.nodeName ) > -1 ) {
        if( !targetElement.currentSrc && targetElement.getAttribute( "src" ) || targetElement.childNodes.length > 0 ){
          var attempts = 0,
              safetyInterval = setInterval(function(){
            if( targetElement.currentSrc ){
              _url = targetElement.currentSrc;
              setupContent();
              clearInterval( safetyInterval );
            }
            else if( attempts++ === MEDIA_ELEMENT_SAFETY_POLL_ATTEMPTS ){
              clearInterval( safetyInterval );
            }
          }, MEDIA_ELEMENT_SAFETY_POLL_INTERVAL );
        }
      }

    }; //Media

    return Media;

  });
}());

define('text!layouts/header.html',[],function () { return '<div class="logo-drop"></div>\n<h1 class="name"></h1>\n<div class="editor-actions">\n  <button id="butter-header-projects" class="butter-header-brown">Projects</button>\n  <button id="butter-header-save" class="butter-header-brown">Save</button>\n  <button id="butter-header-share">Publish</button>\n  <button id="butter-header-auth"></button>\n  <button id="butter-header-auth-out">Logout</button>\n</div>\n';});

define('ui/header',[
  "dialog/iframe-dialog",
  "text!layouts/header.html"
], function(
  IFrameDialog,
  HEADER_TEMPLATE
) {

  var DEFAULT_AUTH_BUTTON_TEXT = "Login / Sign Up",
      DEFAULT_AUTH_BUTTON_TITLE = "Login using BrowserID authentication";

  return function( butter, options ){

    options = options || {};

    var _rootElement = document.createElement( "div" ),
        _title,
        _projectsButton,
        _saveButton,
        _shareButton,
        _loginButton,
        _logoutButton;

    _rootElement.innerHTML = HEADER_TEMPLATE;
    _title = _rootElement.querySelector(".name");
    _title.innerHTML = options.value( "title" ) || "Butter";

    _rootElement.setAttribute( "data-butter-exclude", true );
    _rootElement.id = "butter-header";

    document.body.insertBefore( _rootElement, document.body.firstChild );

    _projectsButton = document.getElementById( "butter-header-projects" );
    _saveButton = document.getElementById( "butter-header-save" );
    _shareButton = document.getElementById( "butter-header-share" );
    _loginButton = document.getElementById( "butter-header-auth" );
    _logoutButton = document.getElementById( "butter-header-auth-out" );

    _saveButton.title = "Save your project";
    _shareButton.title = "Generate a link to share this project with the world";
    _logoutButton.title = "Logout";
    _loginButton.title = DEFAULT_AUTH_BUTTON_TITLE;

    document.body.classList.add( "butter-header-spacing" );

    var _oldDisplayProperty = _logoutButton.style.display;
    _logoutButton.style.display = "none";

    function authenticationRequired( successCallback, errorCallback ){
      if ( butter.cornfield.authenticated() && successCallback && typeof successCallback === "function" ) {
        successCallback();
        return;
      }

      butter.cornfield.login(function( response ){
        if ( !response.error ) {
          butter.cornfield.list(function( listResponse ) {
            loginDisplay();
            if ( successCallback && typeof successCallback === "function" ) {
              successCallback();
            }
          });
        }
        else{
          showErrorDialog( "There was an error logging in. Please try again." );
          if( errorCallback ){
            errorCallback();
          }
        }
      });
    }

    _loginButton.addEventListener( "click", authenticationRequired, false );

    _logoutButton.addEventListener( "click", function( e ){
      butter.cornfield.logout( logoutDisplay );
    });

    function showErrorDialog( message, callback ){
      var dialog = new IFrameDialog({
        type: "iframe",
        modal: true,
        url: butter.ui.dialogDir + "error-message.html",
        events: {
          open: function( e ){
            dialog.send( "message", message );
          },
          cancel: function( e ){
            dialog.close();
            if( callback ){
              callback();
            }
          }
        }
      });
      dialog.open();
    }

    _projectsButton.addEventListener( "click", function() {
      window.location = "/dashboard";
    });

    _shareButton.addEventListener( "click", function( e ){
      function publish(){
        butter.cornfield.publish( butter.project.id, function( e ){
          if( e.error !== "okay" ){
            showErrorDialog( "There was a problem saving your project. Please try again." );
            return;
          }
          else{
            var url = e.url;
            var dialog = new IFrameDialog({
              type: "iframe",
              modal: true,
              url: butter.ui.dialogDir + "share.html",
              events: {
                open: function( e ){
                  dialog.send( "url", url );
                },
                cancel: function( e ){
                  dialog.close();
                }
              }
            });
            dialog.open();
          }
        });
      }

      function prepare(){
        if( butter.project.id ){
          publish();
        }
        else{
          doSave( publish );
        }
      }

      authenticationRequired( prepare );
    }, false );

    function doSave( callback ){

      function execute(){
        butter.project.html = butter.getHTML();
        butter.project.data = butter.exportProject();
        var saveString = JSON.stringify( butter.project, null, 4 );
        butter.ui.loadIndicator.start();
        butter.cornfield.save( butter.project.id, saveString, function( e ){
          butter.ui.loadIndicator.stop();
          if( e.error !== "okay" || !e.project || !e.project._id ){
            showErrorDialog( "There was a problem saving your project. Please try again." );
            return;
          }
          butter.project.id = e.project._id;
          if( callback ){
            callback();
          }
        });
      }

      if( !butter.project.name ){
        var dialog = new IFrameDialog({
          type: "iframe",
          modal: true,
          url: butter.ui.dialogDir + "save-as.html",
          events: {
            open: function( e ){
              dialog.send( "name", null );
            },
            submit: function( e ){
              butter.project.name = e.data;
              dialog.close();
              execute();
            },
            cancel: function( e ){
              dialog.close();
            }
          }
        });
        dialog.open();
      }
      else{
        execute();
      }
    }

    _saveButton.addEventListener( "click", function( e ){
      authenticationRequired( doSave );
    }, false );

    function loginDisplay() {
      _loginButton.innerHTML = butter.cornfield.email();
      _loginButton.title = "This is you!";
      _loginButton.disabled = true;
      _logoutButton.style.display = _oldDisplayProperty;
    }

    function logoutDisplay() {
      _logoutButton.style.display = "none";
      _loginButton.innerHTML = DEFAULT_AUTH_BUTTON_TEXT;
      _loginButton.disabled = false;
      _loginButton.title = DEFAULT_AUTH_BUTTON_TITLE;
    }

    if ( butter.cornfield.authenticated() ) {
      loginDisplay();
    } else {
      logoutDisplay();
      butter.listen( "autologinsucceeded", function onAutoLoginSucceeded( e ) {
        butter.unlisten( "autologinsucceeded", onAutoLoginSucceeded );
        loginDisplay();
      });
    }

    function setup(){
      _rootElement.style.width = window.innerWidth + "px";
    }

    window.addEventListener( "resize", setup, false );
    setup();

  };

});

/* This Source Code Form is subject to the terms of the MIT license
 * If a copy of the MIT license was not distributed with this file, you can
 * obtain one at http://www.mozillapopcorn.org/butter-license.txt */

define('ui/ui',[ "core/eventmanager", "./toggler", "./logo-spinner", "./context-button", "./header" ],
        function( EventManagerWrapper, Toggler, LogoSpinner, ContextButton, Header ){

  var TRANSITION_DURATION = 500,
      BUTTER_CSS_FILE = "{css}/butter.ui.css";

  function Area( id, element ){
    var _element,
        _components = [],
        _this = this;

    EventManagerWrapper( _this );

    this.element = _element = element || document.createElement( "div" );
    _element.id = id;
    this.items = {};

    this.addComponent = function( element, options ){
      var component = new Component( element, options );
      _components.push( component );
      _element.appendChild( component.element );
    };

    this.setContentState = function( state ){
      for( var i=0, l=_components.length; i<l; ++i ){
        _components[ i ].setState( state );
      }
    };
  }

  function Component( element, options ){
    options = options || {};
    var _onTransitionIn = options.transitionIn || function(){},
        _onTransitionInComplete = options.transitionInComplete || function(){},
        _onTransitionOut = options.transitionOut || function(){},
        _onTransitionOutComplete = options.transitionOutComplete || function(){},
        _validStates = options.states || [],
        _enabled = false;

    this.element = element;

    this.setState = function( state ){
      if( ( !_validStates || _validStates.indexOf( state ) > -1 ) && !_enabled ){
        _enabled = true;
        _onTransitionIn();
        setTimeout( _onTransitionInComplete, TRANSITION_DURATION );
      }
      else if( _enabled ){
        _onTransitionOut();
        setTimeout( _onTransitionOutComplete, TRANSITION_DURATION );
        _enabled = false;
      }
    };
  }

  function loadIcons( icons, resourcesDir ){
    var icon, img, div;

    for( icon in icons ){
      if( icons.hasOwnProperty( icon ) ){
        img = new Image();
        img.id = icon + "-icon";
        img.src = resourcesDir + icons[ icon ];

        // We can't use "display: none", since that makes it
        // invisible, and thus not load.  Opera also requires
        // the image be in the DOM before it will load.
        div = document.createElement( "div" );
        div.setAttribute( "data-butter-exclude", "true" );
        div.className = "butter-image-preload";

        div.appendChild( img );
        document.body.appendChild( div );
      }
    }
  }

  var __unwantedKeyPressElements = [
    "TEXTAREA",
    "INPUT",
    "VIDEO",
    "AUDIO"
  ];

  var NUDGE_INCREMENT_SMALL = 0.25,
      NUDGE_INCREMENT_LARGE = 1;

  function UI( butter ){

    var _areas = {},
        _contentState = [],
        _state = true,
        _logoSpinner,
        uiConfig = butter.config,
        _this = this;

    EventManagerWrapper( _this );

    _areas.main = new Area( "butter-tray" );

    this.contentStateLocked = false;

    var _element = _areas.main.element,
        _toggler = new Toggler( butter, _element );

    _element.setAttribute( "data-butter-exclude", "true" );
    _element.className = "butter-tray";

    _areas.work = new Area( "work" );
    _areas.statusbar = new Area( "status-bar" );
    _areas.tools = new Area( "tools" );

    var logoContainer = document.createElement( "div" );
    logoContainer.id = "butter-loading-container";
    _logoSpinner = LogoSpinner( logoContainer );
    _element.appendChild( logoContainer );

    _element.appendChild( _areas.statusbar.element );
    _element.appendChild( _areas.work.element );
    _element.appendChild( _areas.tools.element );

    if( uiConfig.value( "ui" ).enabled !== false ){
      document.body.classList.add( "butter-header-spacing" );
      document.body.classList.add( "butter-tray-spacing" );
      document.body.appendChild( _element );
      butter.listen( "mediaadded", function( e ){
        e.data.createView();
      });
    }

    this.load = function( onReady ){
      if( uiConfig.value( "ui" ).enabled !== false ){
        butter.loader.load(
          [
            {
              type: "css",
              url: BUTTER_CSS_FILE
            }
          ],
          function(){
            // icon preloading needs css to be loaded first
            loadIcons( uiConfig.value( "icons" ), uiConfig.value( "dirs" ).resources || "" );
            onReady();
          }
        );
      }
      else{
        onReady();
      }
    };

    this.registerStateToggleFunctions = function( state, events ){
      _this.listen( "contentstatechanged", function( e ){
        if( e.data.oldState === state ){
          events.transitionOut( e );
        }
        if( e.data.newState === state ){
          events.transitionIn( e );
        }
      });
    };

    this.pushContentState = function( state ){
      if( _this.contentStateLocked ){
        return;
      }
      var oldState = _this.contentState;
      _contentState.push( state );
      _element.setAttribute( "data-butter-content-state", _this.contentState );
      for( var a in _areas ){
        if( _areas.hasOwnProperty( a ) ){
          _areas[ a ].setContentState( state );
        }
      }
      _this.dispatch( "contentstatechanged", {
        oldState: oldState,
        newState: _this.contentState
      });
    };

    this.popContentState = function(){
      if( _this.contentStateLocked ){
        return;
      }
      var oldState = _contentState.pop(),
          newState = _this.contentState;
      _element.setAttribute( "data-butter-content-state", newState );
      for( var a in _areas ){
        if( _areas.hasOwnProperty( a ) ){
          _areas[ a ].setContentState( newState );
        }
      }
      _this.dispatch( "contentstatechanged", {
        oldState: oldState,
        newState: newState
      });
      return oldState;
    };

    this.setContentState = function( newState ){
      var oldState = _contentState.pop();
      _contentState = [ newState ];
      _element.setAttribute( "data-butter-content-state", newState );
      for( var a in _areas ){
        if( _areas.hasOwnProperty( a ) ){
          _areas[ a ].setContentState( newState );
        }
      }
      _this.dispatch( "contentstatechanged", {
        oldState: oldState,
        newState: newState
      });
      return oldState;
    };

    Object.defineProperties( this, {
      contentState: {
        configurable: false,
        enumerable: true,
        get: function(){
          if( _contentState.length > 0 ){
            return _contentState[ _contentState.length - 1 ];
          }
          return null;
        }
      },
      element: {
        configurable: false,
        enumerable: true,
        get: function(){
          return _element;
        }
      },
      areas: {
        configurable: false,
        enumerable: true,
        get: function(){
          return _areas;
        }
      },
      visible: {
        enumerable: true,
        get: function(){
          return _state;
        },
        set: function( val ){
          if( _state !== val ){
            _state = val;
            if( _state ){
              document.body.classList.remove( "minimized" );
              _element.setAttribute( "ui-state", "visible" );
              _this.dispatch( "uivisibilitychanged", true );
            }
            else {
              document.body.classList.add( "minimized" );
              _element.setAttribute( "ui-state", "hidden" );
              _this.dispatch( "uivisibilitychanged", false );
            } //if
          } //if
        }
      }
    });

    var orderedTrackEvents = butter.orderedTrackEvents = [],
        sortTrackEvents = function( a, b ) {
          return a.popcornOptions.start > b .popcornOptions.start;
        };

    butter.listen( "trackeventadded", function( e ) {
      orderedTrackEvents.push( e.data );
      orderedTrackEvents.sort( sortTrackEvents );
    }); // listen

    butter.listen( "trackeventremoved", function( e ) {
      var index = orderedTrackEvents.indexOf( e.data );
      if( index > -1 ){
        orderedTrackEvents.splice( index, 1 );
      } // if
    }); // listen

    butter.listen( "trackeventupdated", function( e ) {
      orderedTrackEvents.sort( sortTrackEvents );
    }); // listen

    var orderedTracks = butter.orderedTracks = [],
        sortTracks = function( a, b ) {
          return a.order > b.order;
        };

    butter.listen( "trackadded", function( e ) {
      e.data.listen( "trackorderchanged", function( e ) {
        orderedTracks.sort( sortTracks );
      }); // listen
      orderedTracks.push( e.data );
      orderedTracks.sort( sortTracks );
    }); // listen

    butter.listen( "trackremoved", function( e ) {
      var index = orderedTracks.indexOf( e.data );
      if( index > -1 ){
        orderedTracks.splice( index, 1 );
      } // if
    }); // listen

    var processKey = {
      32: function( e ) { // space key
        e.preventDefault();

        if( butter.currentMedia.ended ){
          butter.currentMedia.paused = false;
        }
        else{
          butter.currentMedia.paused = !butter.currentMedia.paused;
        }
      }, // space key
      37: function( e ) { // left key
        var inc = e.shiftKey ? NUDGE_INCREMENT_LARGE : NUDGE_INCREMENT_SMALL;
        if( butter.selectedEvents.length ) {
          e.preventDefault();
          for( var i = 0, seLength = butter.selectedEvents.length; i < seLength; i++ ) {
            butter.selectedEvents[ i ].moveFrameLeft( inc, e.ctrlKey || e.metaKey );
          } // for
        } else {
          butter.currentTime -= inc;
        } // if
      }, // left key
      38: function( e ) { // up key
        var track,
            trackEvent,
            nextTrack;

        if ( butter.selectedEvents.length ) {
          e.preventDefault();
        }

        for( var i = 0, seLength = butter.selectedEvents.length; i < seLength; i++ ) {
          trackEvent = butter.selectedEvents[ i ];
          track = trackEvent.track;
          nextTrack = orderedTracks[ orderedTracks.indexOf( track ) - 1 ];
          if( nextTrack ) {
            track.removeTrackEvent( trackEvent );
            nextTrack.addTrackEvent( trackEvent );
          } // if
        } // for
      }, // up key
      39: function( e ) { // right key
        e.preventDefault();
        var inc = e.shiftKey ? NUDGE_INCREMENT_LARGE : NUDGE_INCREMENT_SMALL;
        if( butter.selectedEvents.length ) {
          for( var i = 0, seLength = butter.selectedEvents.length; i < seLength; i++ ) {
            butter.selectedEvents[ i ].moveFrameRight( inc, e.ctrlKey || e.metaKey );
          } // for
        } else {
          butter.currentTime += inc;
        } // if
      }, // right key
      40: function( e ) { // down key
        var track,
            trackEvent,
            nextTrack;

        if ( butter.selectedEvents.length ) {
          e.preventDefault();
        }

        for( var i = 0, seLength = butter.selectedEvents.length; i < seLength; i++ ) {
          trackEvent = butter.selectedEvents[ i ];
          track = trackEvent.track;
          nextTrack = orderedTracks[ orderedTracks.indexOf( track ) + 1 ];
          if( nextTrack ) {
            track.removeTrackEvent( trackEvent );
            nextTrack.addTrackEvent( trackEvent );
          } // if
        } // for
      }, // down key
      27: function( e ) { // esc key
        for( var i = 0; i < butter.selectedEvents.length; i++ ) {
          butter.selectedEvents[ i ].selected = false;
        } // for
        butter.selectedEvents = [];
      }, // esc key
      8: function( e ) { // del key
        if( butter.selectedEvents.length ) {
          e.preventDefault();
          for( var i = 0; i < butter.selectedEvents.length; i++ ) {
            butter.selectedEvents[ i ].track.removeTrackEvent( butter.selectedEvents[ i ] );
          } // for
          butter.selectedEvents = [];
        } // if
      }, // del key
      9: function( e ) { // tab key
        if( orderedTrackEvents.length && butter.selectedEvents.length <= 1 ){
          e.preventDefault();
          var index = 0,
              direction = e.shiftKey ? -1 : 1;
          if( orderedTrackEvents.indexOf( butter.selectedEvents[ 0 ] ) > -1 ){
            index = orderedTrackEvents.indexOf( butter.selectedEvents[ 0 ] );
            if( orderedTrackEvents[ index+direction ] ){
              index+=direction;
            } else if( !e.shiftKey ){
              index = 0;
            } else {
              index = orderedTrackEvents.length - 1;
            } // if
          } // if
          for( var i = 0; i < butter.selectedEvents.length; i++ ) {
            butter.selectedEvents[ i ].selected = false;
          } // for
          butter.selectedEvents = [];
          orderedTrackEvents[ index ].selected = true;
          butter.selectedEvents.push( orderedTrackEvents[ index ] );
        } // if
      } // tab key
    };

    window.addEventListener( "keydown", function( e ){
      var key = e.which || e.keyCode;
      // this allows backspace and del to do the same thing on windows and mac keyboards
      key = key === 46 ? 8 : key;
      if( processKey[ key ] && __unwantedKeyPressElements.indexOf( e.target.nodeName ) === -1 ){
        processKey[ key ]( e );
      } // if
    }, false );

    this.TRANSITION_DURATION = TRANSITION_DURATION;

    _toggler.visible = false;
    _this.visible = false;

    this.loadIndicator = {
      start: function(){
        _logoSpinner.start();
        logoContainer.style.display = "block";
      },
      stop: function(){
        _logoSpinner.stop(function(){
          logoContainer.style.display = "none";
        });
      }
    };

    _this.loadIndicator.start();

    butter.listen( "ready", function(){
      _this.loadIndicator.stop();
      _this.visible = true;
      _toggler.visible = true;
      ContextButton( butter );
      if( uiConfig.value( "ui" ).enabled !== false ){
        Header( butter, uiConfig );
      }
    });

    _this.dialogDir = butter.config.value( "dirs" ).dialogs || "";

   } //UI

  UI.__moduleName = "ui";

  return UI;

});

/* This Source Code Form is subject to the terms of the MIT license
 * If a copy of the MIT license was not distributed with this file, you can
 * obtain one at http://www.mozillapopcorn.org/butter-license.txt */

(function () {

  var DEFAULT_TRACKEVENT_DURATION = 1,
      DEFAULT_TRACKEVENT_OFFSET = 0.01;

  var ACCEPTED_UA_LIST = {
    "Chrome": 17,
    "Firefox": 10
  };

  define('main',[
            "core/eventmanager",
            "core/logger",
            "core/config",
            "core/target",
            "core/media",
            "core/page",
            "./modules",
            "./dependencies",
            "ui/ui",
            "util/xhr",
            "util/lang",
            "text!default-config.json",
            "text!layouts/ua-warning.html"
          ],
          function(
            EventManagerWrapper,
            Logger,
            Config,
            Target,
            Media,
            Page,
            Modules,
            Dependencies,
            UI,
            XHR,
            Lang,
            DefaultConfigJSON,
            UAWarningLayout
          ){

    var __guid = 0,
        __instances = [];

    var Butter = function( options ){
      return new ButterInit( options );
    }; //Butter

    Butter.showUAWarning = function() {
      var uaWarningDiv = Lang.domFragment( UAWarningLayout );
      document.body.appendChild( uaWarningDiv );
      uaWarningDiv.classList.add( "slide-out" );
      uaWarningDiv.getElementsByClassName( "close-button" )[0].onclick = function () {
        document.body.removeChild( uaWarningDiv );
      };
    };

    function ButterInit( butterOptions ){

      var ua = navigator.userAgent,
          acceptedUA;
      for ( var uaName in ACCEPTED_UA_LIST ) {
        if( ACCEPTED_UA_LIST.hasOwnProperty( uaName ) ) {
          var uaRegex = new RegExp( uaName + "/([0-9]+)\\.", "g" ),
              match = uaRegex.exec( ua );
          if ( match && match.length === 2 && Number( match[ 1 ] ) >= ACCEPTED_UA_LIST[ uaName ] ) {
            acceptedUA = uaName + "/" + match[ 1 ];
          }
        }
      }

      if ( !acceptedUA ) {
        Butter.showUAWarning();
      }

      butterOptions = butterOptions || {};

      var _media = [],
          _currentMedia,
          _targets = [],
          _id = "Butter" + __guid++,
          _logger = new Logger( _id ),
          _page,
          _config,
          _defaultConfig,
          _defaultTarget,
          _this = this,
          _selectedEvents = [],
          _defaultPopcornScripts = {},
          _defaultPopcornCallbacks = {};

      // We use the default configuration in src/default-config.json as
      // a base, and override whatever the user provides in the
      // butterOptions.config file.
      try {
        _defaultConfig = Config.parse( DefaultConfigJSON );
      } catch ( e) {
        throw "Butter Error: unable to find or parse default-config.json";
      }

      if ( butterOptions.debug !== undefined ) {
        Logger.enabled( butterOptions.debug );
      }

      EventManagerWrapper( _this );

      this.project = {
        id: null,
        name: null,
        data: null,
        html: null,
        template: null
      };

      function checkMedia() {
        if ( !_currentMedia ) {
          throw new Error("No media object is selected");
        } //if
      } //checkMedia

      this.getManifest = function ( name ) {
        checkMedia();
        return _currentMedia.getManifest( name );
      }; //getManifest

      this.getHTML = function(){
        var media = [];
        for( var i=0; i<_media.length; ++i ){
          media.push( _media[ i ].generatePopcornString() );
        } //for
        return _page.getHTML( media );
      }; //getHTML

      function trackEventRequested( element, media, target ){
        var track,
            type = element.getAttribute( "data-butter-plugin-type" ),
            start = media.currentTime,
            end;

        if( start > media.duration ){
          start = media.duration - DEFAULT_TRACKEVENT_DURATION;
        }

        if( start < 0 ){
          start = 0;
        }

        end = start + DEFAULT_TRACKEVENT_DURATION;

        if( end > media.duration ){
          end = media.duration;
        }

        if( !type ){
          _logger.log( "Invalid trackevent type requested." );
          return;
        } //if

        if( media.tracks.length === 0 ){
          media.addTrack();
        } //if
        track = media.tracks[ 0 ];
        var trackEvent = track.addTrackEvent({
          type: type,
          popcornOptions: {
            start: start,
            end: end,
            target: target
          }
        });

        if( media.currentTime < media.duration - DEFAULT_TRACKEVENT_OFFSET ){
          media.currentTime += DEFAULT_TRACKEVENT_OFFSET;
        }

        return trackEvent;
      }

      function targetTrackEventRequested( e ){
        if( _currentMedia ){
          var trackEvent = trackEventRequested( e.data.element, _currentMedia, e.target.elementID );
          _this.dispatch( "trackeventcreated", {
            trackEvent: trackEvent,
            by: "target"
          });
        }
        else {
          _logger.log( "Warning: No media to add dropped trackevent." );
        } //if
      } //targetTrackEventRequested

      function mediaPlayerTypeRequired( e ){
        _page.addPlayerType( e.data );
      }

      function mediaTrackEventRequested( e ){
        var trackEvent = trackEventRequested( e.data, e.target, "Media Element" );
        _this.dispatch( "trackeventcreated", {
          trackEvent: trackEvent,
          by: "media"
        });
      }

       /****************************************************************
       * Target methods
       ****************************************************************/
      //addTarget - add a target object
      this.addTarget = function ( target ) {
        if ( !(target instanceof Target ) ) {
          target = new Target( target );
        } //if
        _targets.push( target );
        target.listen( "trackeventrequested", targetTrackEventRequested );
        _logger.log( "Target added: " + target.name );
        _this.dispatch( "targetadded", target );
        if( target.isDefault ){
          _defaultTarget = target;
        } //if
        return target;
      }; //addTarget

      //removeTarget - remove a target object
      this.removeTarget = function ( target ) {
        if ( typeof(target) === "string" ) {
          target = _this.getTargetByType( "id", target );
        } //if
        var idx = _targets.indexOf( target );
        if ( idx > -1 ) {
          target.unlisten( "trackeventrequested", targetTrackEventRequested );
          _targets.splice( idx, 1 );
          delete _targets[ target.name ];
          _this.dispatch( "targetremoved", target );
          if( _defaultTarget === target ){
            _defaultTarget = undefined;
          } //if
          return target;
        } //if
        return undefined;
      }; //removeTarget

      //serializeTargets - get a list of targets objects
      this.serializeTargets = function () {
        var sTargets = [];
        for ( var i=0, l=_targets.length; i<l; ++i ) {
          sTargets.push( _targets[ i ].json );
        }
        return sTargets;
      }; //serializeTargets

      //getTargetByType - get the target's information based on a valid type
      // if type is invalid, return undefined
      this.getTargetByType = function( type, val ) {
        for( var i = 0, l = _targets.length; i < l; i++ ) {
          if ( _targets[ i ][ type ] === val ) {
            return _targets[ i ];
          }
        }
        return undefined;
      }; //getTargetByType

      /****************************************************************
       * Project methods
       ****************************************************************/
      //importProject - Import project data
      this.importProject = function ( projectData ) {
        var i,
            l;

        if ( projectData.targets ) {
          for ( i = 0, l = projectData.targets.length; i < l; ++i ) {

            var t, targets = _this.targets, targetData = projectData.targets[ i ];
            for ( var k=0, j=targets.length; k<j; ++k ) {
              if ( targets[ k ].name === targetData.name ) {
                t = targets[ k ];
                break;
              }
            }

            if ( !t ) {
              _this.addTarget( targetData );
            }
            else {
              t.json = targetData;
            }
          }
        }
        if ( projectData.media ) {
          for ( i = 0, l = projectData.media.length; i < l; ++i ) {

            var mediaData = projectData.media[ i ],
                m = _this.getMediaByType( "target", mediaData.target );

            if ( !m ) {
              m = new Media();
              m.json = mediaData;
              _this.addMedia( m );
            }
            else {
              m.json = mediaData;
            }

          } //for
        } //if projectData.media
      }; //importProject

      //exportProject - Export project data
      this.exportProject = function () {
        var exportJSONMedia = [];
        for ( var m=0, lm=_media.length; m<lm; ++m ) {
          exportJSONMedia.push( _media[ m ].json );
        }
        var projectData = {
          targets: _this.serializeTargets(),
          media: exportJSONMedia
        };
        return projectData;
      };

      this.clearProject = function(){
        var allTrackEvents = this.orderedTrackEvents;

        while( allTrackEvents.length > 0 ) {
          allTrackEvents[ 0 ].track.removeTrackEvent( allTrackEvents[ 0 ] );
        }
        while( _targets.length > 0 ){
          _targets[ 0 ].destroy();
          _this.removeTarget( _targets[ 0 ] );
        }
        while( _media.length > 0 ){
          _media[ 0 ].destroy();
          _this.removeMedia( _media[ 0 ] );
        }
      };

      /****************************************************************
       * Media methods
       ****************************************************************/
      //getMediaByType - get the media's information based on a valid type
      // if type is invalid, return undefined
      this.getMediaByType = function ( type, val ) {
       for( var i = 0, l = _media.length; i < l; i++ ) {
          if ( _media[ i ][ type ] === val ) {
            return _media[ i ];
          }
        }
        return undefined;
      }; //getMediaByType

      //addMedia - add a media object
      this.addMedia = function ( media ) {
        if ( !( media instanceof Media ) ) {
          media = new Media( media );
        } //if

        media.popcornCallbacks = _defaultPopcornCallbacks;
        media.popcornScripts = _defaultPopcornScripts;

        _media.push( media );

        _this.chain( media, [
          "mediacontentchanged",
          "mediadurationchanged",
          "mediatargetchanged",
          "mediatimeupdate",
          "mediaready",
          "trackadded",
          "trackremoved",
          "tracktargetchanged",
          "trackeventadded",
          "trackeventremoved",
          "trackeventupdated",
          "trackeventeditrequested"
        ]);

        var trackEvents;
        if ( media.tracks.length > 0 ) {
          for ( var ti=0, tl=media.tracks.length; ti<tl; ++ti ) {
            var track = media.tracks[ ti ];
                trackEvents = track.trackEvents;
                media.dispatch( "trackadded", track );
            if ( trackEvents.length > 0 ) {
              for ( var i=0, l=trackEvents.length; i<l; ++i ) {
                track.dispatch( "trackeventadded", trackEvents[ i ] );
              } //for
            } //if
          } //for
        } //if

        media.listen( "trackeventrequested", mediaTrackEventRequested );
        media.listen( "mediaplayertyperequired", mediaPlayerTypeRequired );

        _this.dispatch( "mediaadded", media );
        if ( !_currentMedia ) {
          _this.currentMedia = media;
        } //if
        media.setupContent();
        return media;
      }; //addMedia

      //removeMedia - forget a media object
      this.removeMedia = function ( media ) {

        var idx = _media.indexOf( media );
        if ( idx > -1 ) {
          _media.splice( idx, 1 );
          _this.unchain( media, [
            "mediacontentchanged",
            "mediadurationchanged",
            "mediatargetchanged",
            "mediatimeupdate",
            "mediaready",
            "trackadded",
            "trackremoved",
            "tracktargetchanged",
            "trackeventadded",
            "trackeventremoved",
            "trackeventupdated",
            "trackeventeditrequested"
          ]);
          var tracks = media.tracks;
          for ( var i=0, l=tracks.length; i<l; ++i ) {
            _this.dispatch( "trackremoved", tracks[ i ] );
          } //for
          if ( media === _currentMedia ) {
            _currentMedia = undefined;
          } //if

          media.unlisten( "trackeventrequested", mediaTrackEventRequested );
          media.unlisten( "mediaplayertyperequired", mediaPlayerTypeRequired );

          _this.dispatch( "mediaremoved", media );
          return media;
        } //if
        return undefined;
      }; //removeMedia

      this.extend = function(){
        Butter.extend( _this, [].slice.call( arguments, 1 ) );
      };

      /****************************************************************
       * Properties
       ****************************************************************/
      Object.defineProperties( _this, {
        defaultTarget: {
          enumerable: true,
          get: function(){
            return _defaultTarget;
          }
        },
        config: {
          enumerable: true,
          get: function(){
            return _config;
          }
        },
        id: {
          get: function(){ return _id; },
          enumerable: true
        },
        tracks: {
          get: function() {
            return _currentMedia.tracks;
          },
          enumerable: true
        },
        targets: {
          get: function() {
            return _targets;
          },
          enumerable: true
        },
        currentTime: {
          get: function() {
            checkMedia();
            return _currentMedia.currentTime;
          },
          set: function( time ) {
            checkMedia();
            _currentMedia.currentTime = time;
          },
          enumerable: true
        },
        duration: {
          get: function() {
            checkMedia();
            return _currentMedia.duration;
          },
          set: function( time ) {
            checkMedia();
            _currentMedia.duration = time;
          },
          enumerable: true
        },
        media: {
          get: function() {
            return _media;
          },
          enumerable: true
        },
        currentMedia: {
          get: function() {
            return _currentMedia;
          },
          set: function( media ) {
            if ( typeof( media ) === "string" ) {
              media = _this.getMediaByType( "id", media.id );
            } //if

            if ( media && _media.indexOf( media ) > -1 ) {
              _currentMedia = media;
              _logger.log( "Media Changed: " + media.name );
              _this.dispatch( "mediachanged", media );
              return _currentMedia;
            } //if
          },
          enumerable: true
        },
        selectedEvents: {
          get: function() {
            return _selectedEvents;
          },
          set: function(selectedEvents) {
            _selectedEvents = selectedEvents;
          },
          enumerable: true
        },
        debug: {
          get: function() {
            return Logger.enabled();
          },
          set: function( value ) {
            Logger.enabled( value );
          },
          enumerable: true
        }
      });

      var preparePage = this.preparePage = function( callback ){
        var scrapedObject = _page.scrape(),
            targets = scrapedObject.target,
            medias = scrapedObject.media;

        _page.prepare(function() {
          if ( !!_config.value( "scrapePage" ) ) {
            var i, j, il, jl, url, oldTarget, oldMedia, mediaPopcornOptions, mediaObj;
            for( i = 0, il = targets.length; i < il; ++i ) {
              oldTarget = null;
              if( _targets.length > 0 ){
                for( j = 0, jl = _targets.length; j < jl; ++j ){
                  // don't add the same target twice
                  if( _targets[ j ].id === targets[ i ].id ){
                    oldTarget = _targets[ j ];
                    break;
                  } //if
                } //for j
              }

              if( !oldTarget ){
                _this.addTarget({ element: targets[ i ].id });
              }
            }

            for( i = 0, il = medias.length; i < il; i++ ) {
              oldMedia = null;
              mediaPopcornOptions = null;
              url = "";
              mediaObj = medias[ i ];

              if( mediaObj.getAttribute( "data-butter-source" ) ){
                url = mediaObj.getAttribute( "data-butter-source" );
              }
              else if( [ "VIDEO", "AUDIO" ].indexOf( mediaObj.nodeName ) > -1 ) {
                url = mediaObj.currentSrc;
              }

              if( _media.length > 0 ){
                for( j = 0, jl = _media.length; j < jl; ++j ){
                  if( _media[ j ].id !== medias[ i ].id && _media[ j ].url !== url ){
                    oldMedia = _media[ j ];
                    break;
                  } //if
                } //for
              }
              else{
                if( _config.value( "mediaDefaults" ) ){
                  mediaPopcornOptions = _config.value( "mediaDefaults" );
                }
              } //if

              if( !oldMedia ){
                _this.addMedia({ target: medias[ i ].id, url: url, popcornOptions: mediaPopcornOptions });
              }
            } //for
          }

          if( callback ){
            callback();
          } //if

          _this.dispatch( "pageready" );
        });
      }; //preparePage

      __instances.push( this );

      if( butterOptions.ready ){
        _this.listen( "ready", function( e ){
          butterOptions.ready( e.data );
        });
      } //if

      var preparePopcornScriptsAndCallbacks = this.preparePopcornScriptsAndCallbacks = function( readyCallback ){
        var popcornConfig = _config.value( "popcorn" ) || {},
            callbacks = popcornConfig.callbacks,
            scripts = popcornConfig.scripts,
            toLoad = [],
            loaded = 0;

        // wrap the load function to remember the script
        function genLoadFunction( script ){
          return function( e ){
            // this = XMLHttpRequest object
            if( this.readyState === 4 ){

              // if the server sent back a bad response, record empty string and log error
              if( this.status !== 200 ){
                _defaultPopcornScripts[ script ] = "";
                _logger.log( "WARNING: Trouble loading Popcorn script: " + this.response );
              }
              else{
                // otherwise, store the response as text
                _defaultPopcornScripts[ script ] = this.response;
              }

              // see if we can call the readyCallback yet
              ++loaded;
              if( loaded === toLoad.length && readyCallback ){
                readyCallback();
              }

            }
          };
        }

        _defaultPopcornCallbacks = callbacks;

        for( var script in scripts ){
          if( scripts.hasOwnProperty( script ) ){
            var url = scripts[ script ],
                probableElement = document.getElementById( url.substring( 1 ) );
            // check to see if an element on the page contains the script we want
            if( url.indexOf( "#" ) === 0 ){
              if( probableElement ){
                _defaultPopcornScripts[ script ] = probableElement.innerHTML;
              }
            }
            else{
              // if not, treat it as a url and try to load it
              toLoad.push({
                url: url,
                onLoad: genLoadFunction( script )
              });
            }
          }
        }

        // if there are scripts to load, load them
        if( toLoad.length > 0 ){
          for( var i = 0; i < toLoad.length; ++i ){
            XHR.get( toLoad[ i ].url, toLoad[ i ].onLoad );
          }
        }
        else{
          // otherwise, call the ready callback right away
          readyCallback();
        }
      };

      function attemptDataLoad( finishedCallback ){
        if ( _config.value( "savedDataUrl" ) ) {

          var xhr = new XMLHttpRequest(),
              savedDataUrl = _config.value( "savedDataUrl" ) + "?noCache=" + Date.now(),
              savedData;

          xhr.open( "GET", savedDataUrl, false );

          if( xhr.overrideMimeType ){
            // Firefox generates a misleading "syntax" error if we don't have this line.
            xhr.overrideMimeType( "application/json" );
          }

          // Deal with caching
          xhr.setRequestHeader( "If-Modified-Since", "Fri, 01 Jan 1960 00:00:00 GMT" );
          xhr.send( null );

          if( xhr.status === 200 ){
            try{
              savedData = JSON.parse( xhr.responseText );
            }
            catch( e ){
              _this.dispatch( "loaddataerror", "Saved data not formatted properly." );
            }
            _this.project.id = savedData.projectID;
            _this.project.name = savedData.name;
            _this.importProject( savedData );
          }
          else {
            _logger.log( "Butter saved data not found: " + savedDataUrl );
          }
        }

        finishedCallback();
      }

      function readConfig( userConfig ){
        // Overwrite default config options with user settings (if any).
        if( userConfig ){
          _defaultConfig.merge( userConfig );
        }

        _config = _defaultConfig;

        _this.project.template = _config.value( "name" );

        //prepare modules first
        var moduleCollection = Modules( _this, _config ),
            loader = Dependencies( _config );

        _this.loader = loader;

        _page = new Page( loader, _config );

        _this.ui = new UI( _this  );

        _this.ui.load(function(){
          //prepare the page next
          preparePopcornScriptsAndCallbacks(function(){
            preparePage(function(){
              moduleCollection.ready(function(){
                if( _config.value( "snapshotHTMLOnReady" ) ){
                  _page.snapshotHTML();
                }
                attemptDataLoad(function(){
                  //fire the ready event
                  _this.dispatch( "ready", _this );
                });
              });
            });
          });
        });

      } //readConfig

      if( butterOptions.config && typeof( butterOptions.config ) === "string" ){
        var xhr = new XMLHttpRequest(),
          userConfig,
          url = butterOptions.config + "?noCache=" + Date.now();

        xhr.open( "GET", url, false );
        if( xhr.overrideMimeType ){
          // Firefox generates a misleading "syntax" error if we don't have this line.
          xhr.overrideMimeType( "application/json" );
        }
        // Deal with caching
        xhr.setRequestHeader( "If-Modified-Since", "Fri, 01 Jan 1960 00:00:00 GMT" );
        xhr.send( null );

        if( xhr.status === 200 || xhr.status === 0 ){
          try{
            userConfig = Config.parse( xhr.responseText );
          }
          catch( e ){
            throw new Error( "Butter config file not formatted properly." );
          }
          readConfig( userConfig );
        }
        else{
          _this.dispatch( "configerror", _this );
        } //if
      }
      else {
        readConfig( butterOptions.config );
      } //if

      this.page = _page;

    }

    Butter.instances = __instances;

    // Butter will report a version, which is the git commit sha
    // of the version we ship.  This happens in make.js's build target.
    Butter.version = "0.5";

    if ( window.Butter.__waiting ) {
      for ( var i=0, l=window.Butter.__waiting.length; i<l; ++i ) {
        Butter.apply( {}, window.Butter.__waiting[ i ] );
      }
      delete Butter._waiting;
    } //if
    window.Butter = Butter;
    return Butter;
  });

}());


}());
