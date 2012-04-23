from django.contrib.auth.models import User
from ...popcorn.models import Template, Project


def create_user(handle):
    """Helper to create Users"""
    email = '%s@%s.com' % (handle, handle)
    return User.objects.create_user(handle, email, handle)


def create_template(**kwargs):
    defaults = {'name': 'basic'}
    if kwargs:
        defaults.update(kwargs)
    return Template.objects.create(**defaults)


def create_project(**kwargs):
    defaults = {
        'name': 'Popcorn Project',
        'user': create_user('bob'),
        'template': create_template(),
        }
    if kwargs:
        defaults.update(kwargs)
    return Project.objects.create(**defaults)
