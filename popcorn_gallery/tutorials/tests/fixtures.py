from ..models import Tutorial
from ...users.tests.fixtures import create_user


def create_tutorial(**kwargs):
    defaults = {
        'title': 'How you can do X with Popcornjs',
        'body': 'This is amazing!'
        }
    if kwargs:
        defaults.update(kwargs)
    return Tutorial.objects.create(**defaults)
