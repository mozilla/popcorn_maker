import functools

from django.http import HttpResponseBadRequest, HttpResponseForbidden
from django.core.serializers.json import simplejson as json


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
        if request.is_ajax and not request.user.is_authenticated():
            return HttpResponseForbidden()
        return func(request, *args, **kwargs)
    return wrapper
