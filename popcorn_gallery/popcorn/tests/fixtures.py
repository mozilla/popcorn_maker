from django.contrib.auth.models import User
from ..models import Template, Project, Category


def create_user(handle, with_profile=False):
    """Helper to create Users"""
    email = '%s@%s.com' % (handle, handle)
    user = User.objects.create_user(handle, email, handle)
    if with_profile:
        profile = user.get_profile()
        profile.name = handle.title()
        profile.save()
    return user


def create_template(**kwargs):
    defaults = {
        'name': 'basic',
        'slug': 'basic',
        'template': 'popcorn/templates/test/base.html',
        'config': 'popcorn/templates/test/config.cfg',
        }
    if kwargs:
        defaults.update(kwargs)
    return Template.objects.create(**defaults)


def create_project(**kwargs):
    defaults = {
        "name": 'Popcorn Project',
        "metadata": "{\"data\": \"foo\"}",
        "template": "base-template",
        "html": "<!DOCTYPE html5>",
        }
    if kwargs:
        defaults.update(kwargs)
    if not 'author' in kwargs:
        defaults['author'] = create_user('bob')
    if not 'template' in kwargs:
        defaults['template'] = create_template()
    return Project.objects.create(**defaults)


def create_category(**kwargs):
    defaults = {'name': 'Special'}
    if kwargs:
        defaults.update(kwargs)
    return Category.objects.create(**defaults)
