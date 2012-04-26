from django.conf import settings
from tastypie.authentication import ApiKeyAuthentication
from tastypie.authorization import Authorization


class InternalApiKeyAuthentication(ApiKeyAuthentication):

    def is_authenticated(self, request, **kwargs):
        """API can only be accessed from ``INTERNAL_IPS`` or when
        ``DEBUG`` is on"""
        ip = request.META.get('HTTP_X_REAL_IP',
                              request.META.get('REMOTE_ADDR'))
        if not (settings.DEBUG or ip in settings.INTERNAL_IPS):
            return self._unauthorized()
        return (super(InternalApiKeyAuthentication, self)
                .is_authenticated(request, **kwargs))


class OwnerAuthorization(Authorization):

    def apply_limits(self, request, object_list):
        return object_list.filter(user=request.user)

