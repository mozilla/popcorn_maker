from django.contrib.auth.models import User
from tastypie import fields
from tastypie.authentication import (Authentication, ApiKeyAuthentication,
                                     MultiAuthentication)
from tastypie.authorization import Authorization
from tastypie.resources import ModelResource
from .models import Project, Template


class SuperuserAuthentication(Authentication):
    """Super users authenticated can access the API"""

    def is_authenticated(self, request, **kwargs):
        return request.user.is_superuser

    def get_identifier(self, request):
        return request.user.username


class OwnerAuthorization(Authorization):

    def apply_limits(self, request, object_list):
        return object_list.filter(user=request.user)


class UserResource(ModelResource):

    class Meta:
        queryset = User.objects.all()
        resource_name = 'user'
        fields = ['username', 'first_name', 'last_name', 'last_login', 'email']


class TemplateResource(ModelResource):

    class Meta:
        queryset = Template.objects.all()
        resource_name = 'template'
        fields = ['name', ]
        list_allowed_methods = ['get', ]
        authentication = MultiAuthentication(SuperuserAuthentication(),
                                             ApiKeyAuthentication())
        authorization = Authorization()


class ProjectResource(ModelResource):
    user = fields.ForeignKey(UserResource, 'user', full=True)
    template = fields.ForeignKey(TemplateResource, 'template', full=True)

    def get_object_list(self, request):
        """List only ``User`` owned templates"""
        return (super(ProjectResource, self).get_object_list(request)
                .filter(user=request.user))

    def hydrate_user(self, bundle):
        bundle.data['user'] = bundle.request.user
        return bundle

    class Meta:
        queryset = Project.objects.filter(status=Project.LIVE)
        resource_name = 'project'
        fields = ['uuid', 'name', 'metadata', 'html', 'created', 'modified',
                  'user', 'template']
        authentication = MultiAuthentication(SuperuserAuthentication(),
                                             ApiKeyAuthentication())
        authorization = OwnerAuthorization()
