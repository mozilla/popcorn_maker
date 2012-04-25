from django.contrib.auth.models import User
from tastypie.resources import Resource
from tastypie import fields
from tastypie.authorization import Authorization
from django_browserid.auth import BrowserIDBackend


class AccountContainer(object):
    def __init__(self, initial=None):
        self.__dict__['_data'] = {}

        if hasattr(initial, 'items'):
            self.__dict__['_data'] = initial

    def __getattr__(self, name):
        return self._data.get(name, None)

    def __setattr__(self, name, value):
        self.__dict__['_data'][name] = value

    def to_dict(self):
        return self._data


class AccountResource(Resource):
    """End point for creating new accounts only accepts ``POST`` requests
    and returns a ``username`` an ``apikey`` and the ``email`` for the user
    """
    email = fields.CharField(attribute='email')

    class Meta:
        resource_name = 'account'
        object_class = AccountContainer
        list_allowed_methods = ['post']
        detail_allowed_methods = []
        always_return_data = True
        authorization = Authorization()

    def obj_create(self, bundle, request=None, **kwargs):
        """Create or return the account details for this email"""
        bundle = self.full_hydrate(bundle)
        browserid = BrowserIDBackend()
        try:
            user = User.objects.get(email=bundle.data['email'])
        except User.DoesNotExist:
            user = browserid.create_user(bundle.data['email'])
        bundle.data['username'] = user.username
        bundle.data['apikey'] = user.api_key.key
        return bundle

    def get_resource_uri(self, bundle_or_obj):
        """Don't expose the account information over the API"""
        return u''
