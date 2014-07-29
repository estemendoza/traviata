import random
import string
import json

class Traviata(object):
    #This two class attributes should be overriden
    _framework = "Undefined"
    _root_object = "undefined"

    def _handler_function_closure(self, name):
        raise NotImplementedError("This method must be overriden in '%s'"  
            % self.__class__.__name__)

    @classmethod
    def get_framework(cls):
        return cls._framework

    @classmethod
    def _generate_id(cls):
        return "".join(random.choice(string.ascii_uppercase)
            for _ in xrange(10)) + "_trv"

    @classmethod
    def _get_root_object(cls):
        return cls._root_object

    @classmethod
    def get_instance(cls, framework, *args, **kwargs):
        if framework == ExtJsTraviata.get_framework():
            return ExtJsTraviata(ExtJsTraviata._get_root_object(), *args, **kwargs)
        
        raise ValueError("Framework '%s' not supported" % framework)

    def __getattr__(self, name):
        return self._handler_function_closure(name)


class ExtJsTraviata(Traviata):
    _framework = "ExtJs"
    _root_object = "Ext"

    def __init__(self, cmp_id, driver, content={}):
        self._cmp_id = cmp_id
        self._driver = driver

        if cmp_id == self._get_root_object():
            self.set_stringify()
            unicode_obj = self._driver.execute_script('return JSON.prune(%s)' % cmp_id)
            content = json.loads(unicode_obj)
            
        #Configure elements to be python objects
        for name, value in content.iteritems():
            setattr(self, name, self._wrap(value))

    def _wrap(self, value):
        if isinstance(value, (tuple, list, set, frozenset)): 
            return type(value)([self._wrap(v) for v in value])

        elif isinstance(value, dict):
            return ExtJsTraviata(self._generate_id(), self._driver, value)
        else:
            return value

    def _handler_function_closure(self, name):

        def handler_function(*args, **kwargs):

            def quote(value):
                if isinstance(value, int):
                    return str(value)
                return '"%s"' % value

            trv_id = self._generate_id()

            temp_args = ', '.join(quote(item) for item in args)

            _call = trv_id + ' = ' + self._cmp_id + '.' + name + '(' + temp_args + ')'

            self._driver.execute_script(_call)
            
            stringify = '\
            if ('+trv_id+'){\
                return JSON.prune('+trv_id+', {inheritedProperties:false, depthDecr:3})\
            }else{\
                return false;\
            }'

            result = self._driver.execute_script(stringify)
            if result:
                cmp = json.loads(result)
            
                if isinstance(cmp, (tuple, list, set, frozenset)):
                    return cmp

                return ExtJsTraviata(trv_id, self._driver, cmp)

            raise NameError("Not found: %s" % name)


        return handler_function

    #Method to include the code for JSON.prune
    #which is the responsible to convert javascript objects to json
    #and send it to python
    def set_stringify(self):
        self._driver.execute_script("var s=document.createElement('script');\
                                    s.setAttribute('type', 'text/javascript');\
                                    s.innerHTML='"+self._get_JSON_parser()+"';\
                                    document.head.appendChild(s);")

    def _get_JSON_parser(self):
        '''
        // JSON.prune : a function to stringify any object without overflow
        // two additional optional parameters :
        //   - the maximal depth (default : 6)
        //   - the maximal length of arrays (default : 50)
        // You can also pass an "options" object.
        // examples :
        //   var json = JSON.prune(window)
        //   var arr = Array.apply(0,Array(1000)); var json = JSON.prune(arr, 4, 20)
        //   var json = JSON.prune(window.location, {inheritedProperties:true})
        // Web site : http://dystroy.org/JSON.prune/
        // JSON.prune on github : https://github.com/Canop/JSON.prune
        // This was discussed here : http://stackoverflow.com/q/13861254/263525
        // The code is based on Douglas Crockford's code : https://github.com/douglascrockford/JSON-js/blob/master/json2.js
        // No effort was done to support old browsers. JSON.prune will fail on IE8.
        '''

        t = r'''
        var cx = /[\u0000\u00ad\u0600-\u0604\u070f\u17b4\u17b5\u200c-\u200f\u2028-\u202f\u2060-\u206f\ufeff\ufff0-\uffff]/g,
            escapable = /[\\\"\x00-\x1f\x7f-\x9f\u00ad\u0600-\u0604\u070f\u17b4\u17b5\u200c-\u200f\u2028-\u202f\u2060-\u206f\ufeff\ufff0-\uffff]/g,
            meta = { 
                '\b': '\\b',
                '\t': '\\t',
                '\n': '\\n',
                '\f': '\\f',
                '\r': '\\r',
                '"' : '\\"',
                '\\': '\\\\'
            };
        '''

        parser = '''(function () {
            'use strict';
            var DEFAULT_MAX_DEPTH = 6;
            var DEFAULT_ARRAY_MAX_LENGTH = 50;
            var seen; 
            var iterator;
            
            var forEachEnumerableOwnProperty = function(obj, callback) {
                for (var k in obj) {
                    if (Object.prototype.hasOwnProperty.call(obj, k)) callback(k);
                }
            };

            var forEachEnumerableProperty = function(obj, callback) {
                for (var k in obj) callback(k);
            };

            var forEachProperty = function(obj, callback, excluded) {
                if (obj==null) return;
                excluded = excluded || {};
                Object.getOwnPropertyNames(obj).forEach(function(k){
                    if (!excluded[k]) {
                        callback(k);
                        excluded[k] = true;
                    }
                });
                forEachProperty(Object.getPrototypeOf(obj), callback, excluded);
            };

            Date.prototype.toPrunedJSON = Date.prototype.toJSON;
            String.prototype.toPrunedJSON = String.prototype.toJSON;

            '''+t.replace("\\","\\\\")+'''

            function quote(string) {
                escapable.lastIndex = 0;
                return escapable.test(string) ? '\"' + string.replace(escapable, function (a) {
                    var c = meta[a];
                    return typeof c === 'string'
                        ? c
                        : '\\\\\\\\u' + ('0000' + a.charCodeAt(0).toString(16)).slice(-4);
                }) + '\"' : '\"' + string + '\"';
            }

            function str(key, holder, depthDecr, arrayMaxLength) {
                var i, k, v, length, partial, value = holder[key];
                if (value && typeof value === 'object' && typeof value.toPrunedJSON === 'function') {
                    value = value.toPrunedJSON(key);
                }

                switch (typeof value) {
                case 'string':
                    return quote(value);
                case 'number':
                    return isFinite(value) ? String(value) : 'null';
                case 'boolean':
                case 'null':
                    return String(value);
                case 'object':
                    if (!value) {
                        return 'null';
                    }
                    if (depthDecr<=0 || seen.indexOf(value)!==-1) {
                        return '"-pruned-"';
                    }
                    seen.push(value);
                    partial = [];
                    if (Object.prototype.toString.apply(value) === '[object Array]') {
                        length = Math.min(value.length, arrayMaxLength);
                        for (i = 0; i < length; i += 1) {
                            partial[i] = str(i, value, depthDecr-1, arrayMaxLength) || 'null';
                        }
                        return  '[' + partial.join(',') + ']';
                    }
                    iterator(value, function(k) {
                        try {
                            v = str(k, value, depthDecr-1, arrayMaxLength);
                            if (v) partial.push(quote(k) + ':' + v);
                        } catch (e) { 
                            
                        }               
                    });
                    return '{' + partial.join(',') + '}';
                }
            }

            JSON.prune = function (value, depthDecr, arrayMaxLength) {
                if (typeof depthDecr == "object") {
                    var options = depthDecr;
                    depthDecr = options.depthDecr;
                    arrayMaxLength = options.arrayMaxLength;
                    iterator = options.iterator || forEachEnumerableOwnProperty;
                    if (options.allProperties) iterator = forEachProperty;
                    else if (options.inheritedProperties) iterator = forEachEnumerableProperty
                } else {
                    iterator = forEachEnumerableOwnProperty;
                }
                seen = [];
                depthDecr = depthDecr || DEFAULT_MAX_DEPTH;
                arrayMaxLength = arrayMaxLength || DEFAULT_ARRAY_MAX_LENGTH;
                return str('', {'': value}, depthDecr, arrayMaxLength);
            };
        }());
        '''
        return parser.replace("\n","").replace("'","\\'")
