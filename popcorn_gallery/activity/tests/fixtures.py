from django.contrib.auth.models import User

from ..models import Activity


def create_user(handle, with_profile=False):
    """Helper to create Users"""
    email = '%s@%s.com' % (handle, handle)
    user = User.objects.create_user(handle, email, handle)
    if with_profile:
        profile = user.get_profile()
        profile.name = handle.title()
        profile.save()
    return user


def create_activity(**kwargs):
    defaults = {'body': 'has performed an action'}
    if not 'user' in kwargs:
        defaults['user'] = create_user('bob')
    if kwargs:
        defaults.update(kwargs)
    return Activity.objects.create(**defaults)
