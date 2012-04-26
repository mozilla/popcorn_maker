from django.test.client import Client
from django.utils import simplejson as json

# from django.conf import settings
# settings.DEBUG=True


class CustomClient(Client):
    """Wrapper around the default Django ``Client`` adds the extra headers"""

    def get_auth(self, user):
        return 'ApiKey %s:%s' % (user.username, user.api_key.key)

    def get(self, path, data={}, user=None, **extra):
        if user:
            extra.update({'HTTP_AUTHORIZATION': self.get_auth(user)})
        return super(CustomClient, self).get(self, path, data=data, **extra)

    def patch(self, path, data={}, user=None, content_type='application/json',
              **extra):
        default = {'REQUEST_METHOD': 'PATCH'}
        if user:
            default.update({'HTTP_AUTHORIZATION': self.get_auth(user)})
        if extra:
            default.update(extra)
        data = json.dumps(data)
        return super(CustomClient, self).post(path, data=data,
                                              content_type=content_type, **extra)

    def post(self, path, data={}, user=None, content_type='application/json',
             **extra):
        if user:
            extra.update({'HTTP_AUTHORIZATION': self.get_auth(user)})
        data = json.dumps(data)
        return super(CustomClient, self).post(path, data=data,
                                              content_type=content_type, **extra)
