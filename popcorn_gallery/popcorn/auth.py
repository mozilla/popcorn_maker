from tastypie.authentication import ApiKeyAuthentication
from tastypie.authorization import Authorization


class InternalApiKeyAuthentication(ApiKeyAuthentication):
    pass


class OwnerAuthorization(Authorization):

    def apply_limits(self, request, object_list):
        return object_list.filter(user=request.user)

