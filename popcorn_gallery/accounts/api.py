from django.contrib.auth.models import User
from tastypie.resources import Resource
from tastypie import fields
from tastypie.authorization import Authorization
from django_browserid.auth import BrowserIDBackend
from .forms import AccountAPIForm, NonORMFormValidation


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
        validation = NonORMFormValidation(form_class=AccountAPIForm)

    def obj_create(self, bundle, request=None, **kwargs):
        """Create or return the account details for this email"""
        bundle.obj = self._meta.object_class()
        for key, value in kwargs.items():
            setattr(bundle.obj, key, value)
        bundle = self.full_hydrate(bundle)
        # determine if the data sent is valid using tastypie's mechanics
        self.is_valid(bundle, request)
        if bundle.errors:
            self.error_response(bundle.errors, request)
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
