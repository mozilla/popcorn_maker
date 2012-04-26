from django.contrib.auth.models import User
from tastypie import fields
from tastypie.authorization import Authorization
from tastypie.resources import ModelResource
from .models import Project, Template
from .auth import OwnerAuthorization, InternalApiKeyAuthentication
from .forms import ProjectAPIForm, CustomFormValidation


class UserResource(ModelResource):
    """Helper to map the ForeignKey. This Resource is not mapped since
    we don't want to expose our users"""

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
    uuid = fields.CharField(readonly=True)
    created = fields.DateTimeField(readonly=True)
    modified = fields.DateTimeField(readonly=True)

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
        validation = CustomFormValidation(form_class=ProjectAPIForm)
