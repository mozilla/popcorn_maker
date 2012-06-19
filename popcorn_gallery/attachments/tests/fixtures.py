from django.core.files import File
from django.core.files.base import ContentFile

from ..models import Asset
from ...popcorn.tests.fixtures import create_template


def create_asset(asset_content='<DOCTYPE !html5>', asset_name='index.html', **kwargs):
    asset_file = ContentFile(asset_content)
    asset_file.name = asset_name
    defaults = {
        'asset': asset_file,
        }
    if kwargs:
        defaults.update(kwargs)
    if not 'template' in kwargs:
        defaults['template'] = create_template()
    return Asset.objects.create(**defaults)
