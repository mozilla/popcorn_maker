from django.contrib.auth.models import User
from ..models import Template, TemplateCategory, Project, ProjectCategory


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
        'template': 'butter/default-butter/base.html',
        'config': 'butter/default-butter/config.cfg',
        }
    if kwargs:
        defaults.update(kwargs)
    return Template.objects.create(**defaults)


def create_project(**kwargs):
    defaults = {
        "name": 'Popcorn Project',
        "metadata": "{\"data\": \"foo\"}",
        "html": "<!DOCTYPE html5>",
        }
    if kwargs:
        defaults.update(kwargs)
    if not 'author' in kwargs:
        defaults['author'] = create_user('bob')
    if not 'template' in kwargs:
        defaults['template'] = create_template()
    return Project.objects.create(**defaults)


def create_external_project(**kwargs):
    defaults = {
        "name": 'Popcorn Project',
        "url": 'http://mozillapopcorn.org',
        }
    if not 'author' in kwargs:
        defaults['author'] = create_user('bob')
    if kwargs:
        defaults.update(kwargs)
    return Project.objects.create(**defaults)



def create_template_category(**kwargs):
    defaults = {'name': 'Special'}
    if kwargs:
        defaults.update(kwargs)
    return TemplateCategory.objects.create(**defaults)


def create_project_category(**kwargs):
    defaults = {'name': 'Special'}
    if kwargs:
        defaults.update(kwargs)
    return ProjectCategory.objects.create(**defaults)
