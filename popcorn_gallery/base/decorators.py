import functools
import hashlib

from django.core.serializers.json import simplejson as json
from django.http import HttpResponseBadRequest, HttpResponseForbidden
from django.core.cache import cache


def json_handler(func):
    """Decorator for deserializing requests with ``application/json``
    ``CONTENT_TYPE``.
    Transforms the ``POST`` request into a python object.
    """
    @functools.wraps(func)
    def wrapper(request, *args, **kwargs):
        request.JSON = {}
        content_type = request.META.get('CONTENT_TYPE', 'text/plain')
        request.is_json = True if 'application/json' in content_type else False
        if (request.method == 'POST' and request.is_json):
            try:
                data = json.loads(request.raw_post_data)
            except ValueError:
                return HttpResponseBadRequest()
            request.JSON = data
        return func(request, *args, **kwargs)
    return wrapper


def login_required_ajax(func):
    """Checks if the request is preformed via ajax by an authenticated user"""

    @functools.wraps(func)
    def wrapper(request, *args, **kwargs):
        if request.is_ajax() and request.user.is_authenticated():
            return func(request, *args, **kwargs)
        return HttpResponseForbidden()
    return wrapper


class _Missing(object):

    def __repr__(self):
        return 'no value'

    def __reduce__(self):
        return '_missing'

_missing = _Missing()


class cached_property(object):
    """A decorator that converts a function into a lazy property.  The
    function wrapped is called the first time to retrieve the result
    and then that calculated result is used the next time you access
    the value::

        class Foo(object):

            @cached_property
            def foo(self):
                # calculate something important here
                return 42

    The class has to have a `__dict__` in order for this property to
    work.

    .. versionchanged:: 0.6
       the `writeable` attribute and parameter was deprecated.  If a
       cached property is writeable or not has to be documented now.
       For performance reasons the implementation does not honor the
       writeable setting and will always make the property writeable.

    :copyright: (c) 2011 by the Werkzeug Team, see AUTHORS for more details.
    :license: BSD, see LICENSE for more details.
    """

    # implementation detail: this property is implemented as non-data
    # descriptor.  non-data descriptors are only invoked if there is
    # no entry with the same name in the instance's __dict__.
    # this allows us to completely get rid of the access function call
    # overhead.  If one choses to invoke __get__ by hand the property
    # will still work as expected because the lookup logic is replicated
    # in __get__ for manual invocation.

    def __init__(self, func, name=None, doc=None, writeable=False):
        if writeable:
            from warnings import warn
            warn(DeprecationWarning('the writeable argument to the '
                                    'cached property is a noop since 0.6 '
                                    'because the property is writeable '
                                    'by default for performance reasons'))

        self.__name__ = name or func.__name__
        self.__module__ = func.__module__
        self.__doc__ = doc or func.__doc__
        self.func = func

    def __get__(self, obj, type=None):
        if obj is None:
            return self
        value = obj.__dict__.get(self.__name__, _missing)
        if value is _missing:
            value = self.func(obj)
            obj.__dict__[self.__name__] = value
        return value


def throttle_view(func, methods=None, duration=15):
    def inner(request, *args, **kwargs):
        throttled_methods = methods if methods else ['POST', 'GET']
        if request.method in throttled_methods:
            remote_addr = request.META.get('HTTP_X_FORWARDED_FOR') or \
                          request.META.get('REMOTE_ADDR')
            m = hashlib.md5()
            m.update('%s.%s' % (remote_addr, request.path_info))
            key = m.hexdigest()
            if cache.get(key):
                return HttpResponseForbidden('Please try again later.')
            else:
                cache.set(key, True, duration)
        return func(request, *args, **kwargs)
    return inner
