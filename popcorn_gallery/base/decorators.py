import functools

from django.http import HttpResponseBadRequest
from django.core.serializers.json import simplejson as json


def json_handler(func):
    """Decorator for deserializing requests with ``application/json``
    ``CONTENT_TYPE``.
    Transforms the ``POST`` request into a python object.
    """
    @functools.wraps(func)
    def wrapper(request, *args, **kwargs):
        request.JSON = {}
        content_type = request.META.get('CONTENT_TYPE')
        request.is_json = True if 'application/json' in content_type else False
        if (request.method == 'POST' and request.is_json):
            try:
                data = json.loads(request.raw_post_data)
            except ValueError:
                return HttpResponseBadRequest()
            request.JSON = data
        return func(request, *args, **kwargs)
    return wrapper

