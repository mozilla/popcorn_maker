from ..models import Notice


def create_notice(**kwargs):
    defaults = {
        'title': 'Hello!',
        'body': 'World!',
        }
    if kwargs:
        defaults.update(kwargs)
    return Notice.objects.create(**defaults)
