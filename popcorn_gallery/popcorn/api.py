from django.contrib.auth.models import User
from tastypie import fields
from tastypie.authorization import Authorization
from tastypie.resources import ModelResource
from .models import Project, Template
from .auth import OwnerAuthorization, InternalApiKeyAuthentication


class UserResource(ModelResource):

    class Meta:
        queryset = User.objects.all()
        resource_name = 'user'
        fields = ['username', 'first_name', 'last_name', 'last_login']


class TemplateResource(ModelResource):

    class Meta:
        queryset = Template.objects.all()
        resource_name = 'template'
        fields = ['name', ]
        allowed_methods = ['get', ]
        authentication = InternalApiKeyAuthentication()
        authorization = Authorization()


class ProjectResource(ModelResource):
    user = fields.ForeignKey(UserResource, 'user', full=True)
    template = fields.ForeignKey(TemplateResource, 'template', full=True)

    def get_object_list(self, request):
        """List only ``User`` owned templates"""
        if not hasattr(request, 'user'):
            return Project.objects.none()
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
        list_allowed_methods = ['get', 'post']
        detail_allowed_methods = ['get', 'patch']
        authentication = InternalApiKeyAuthentication()
        authorization = OwnerAuthorization()
