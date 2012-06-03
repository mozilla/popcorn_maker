from urlparse import urlparse

from django.conf import settings
from lxml import html

from django_extensions.db.fields import json


BUTTER_ASSETS = {
    'butter.js': 'src/',
    'butter.ui.css': 'css/',
    }


def get_butter_library(src):
    """Determines if the element linked is a valid ``butter`` library"""
    if not src:
        return None
    # is it already a valid URL?
    url = urlparse(src)
    if url.netloc:
        return None
    # Is whitelisted as part of butter
    filename = src.split('/')[-1]
    if filename in BUTTER_ASSETS:
        return settings.STATIC_URL + BUTTER_ASSETS[filename] + filename
    return None


def prepare_template_stream(stream, base_url):
    """Prepares the stream to be stored in the DB"""
    document_tree = html.fromstring(stream, base_url=base_url)
    script_elements = document_tree.xpath('//script[@src]')
    for script in script_elements:
        src = script.get('src')
        butter_library = get_butter_library(src)
        if butter_library:
            script.set('src', butter_library)
    document_tree.make_links_absolute()
    return html.tostring(document_tree, pretty_print=True)


def remove_default_values(stream, base_url):
    data = json.loads(stream)
    for attr in ['baseDir', 'name', 'savedDataUrl']:
        if attr in data:
            del data[attr]
    return json.dumps(data)
