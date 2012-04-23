from django.contrib.auth.models import User
from tastypie import fields
from tastypie.resources import ModelResource, ALL_WITH_RELATIONS
from .models import Project


class UserResource(ModelResource):
    class Meta:
        queryset = User.objects.all()
        resource_name = 'user'
        fields = ['username', 'first_name', 'last_name', 'last_login']


class ProjectResource(ModelResource):
    user = fields.ForeignKey(UserResource, 'user', full=True)
    class Meta:
        queryset = Project.objects.all()
        resource_name = 'project'
        filtering = {
            'user': ALL_WITH_RELATIONS,
        }
