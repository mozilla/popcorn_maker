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
        if (request.method == 'POST' and \
            'application/json' in request.META.get('CONTENT_TYPE')):
            try:
                data = json.loads(request.raw_post_data)
            except ValueError:
                return HttpResponseBadRequest()
            request.JSON = data
        return func(request, *args, **kwargs)
    return wrapper
