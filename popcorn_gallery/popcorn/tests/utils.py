import mock

from django.test.client import Client
from django.utils import simplejson as json


class CustomClient(Client):
    """Wrapper around the default Django ``Client`` adds the extra headers"""

    def get_auth(self, user):
        return 'ApiKey %s:%s' % (user.username, user.api_key.key)

    def get(self, path, data={}, user=None, **extra):
        if user:
            extra.update({'HTTP_AUTHORIZATION': self.get_auth(user)})
        return super(CustomClient, self).get(path, data=data, **extra)

    def patch(self, path, data={}, user=None, content_type='application/json',
              **extra):
        defaults = {'REQUEST_METHOD': 'PATCH'}
        if user:
            defaults.update({'HTTP_AUTHORIZATION': self.get_auth(user)})
        if extra:
            defaults.update(extra)
        data = json.dumps(data)
        return super(CustomClient, self).post(path, data=data,
                                              content_type=content_type,
                                              **defaults)

    def put(self, path, data={}, user=None, content_type='application/json',
              **extra):
        defaults = {'REQUEST_METHOD': 'PUT'}
        if user:
            defaults.update({'HTTP_AUTHORIZATION': self.get_auth(user)})
        if extra:
            defaults.update(extra)
        data = json.dumps(data)
        return super(CustomClient, self).post(path, data=data,
                                              content_type=content_type,
                                              **defaults)

    def post(self, path, data={}, user=None, content_type='application/json',
             **extra):
        if user:
            extra.update({'HTTP_AUTHORIZATION': self.get_auth(user)})
        data = json.dumps(data)
        return super(CustomClient, self).post(path, data=data,
                                              content_type=content_type, **extra)

