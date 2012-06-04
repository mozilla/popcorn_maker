import html5lib

from urlparse import urlparse, urljoin

from django.conf import settings
from django.utils.encoding import force_unicode

from django_extensions.db.fields import json
from html5lib import treebuilders
from html5lib.serializer import htmlserializer


BUTTER_ASSETS = {
    'butter.js': 'src/',
    'butter.ui.css': 'css/',
    }


def get_butter_library(src):
    """Determines if the element linked is a valid ``butter`` library"""
    if not src:
        return None
    # Is it already a valid URL?
    url = urlparse(src)
    if url.netloc:
        return None
    # Is this part of butter?
    filename = src.split('/')[-1]
    if filename in BUTTER_ASSETS:
        return settings.STATIC_URL + BUTTER_ASSETS[filename] + filename
    return None


def _serialize_stream(document_tree):
    walker = html5lib.treewalkers.getTreeWalker('lxml')
    stream = walker(document_tree)
    serializer = htmlserializer.HTMLSerializer(omit_optional_tags=False,
                                               quote_attr_values=True)
    return unicode(serializer.render(stream))


def prepare_template_stream(stream, base_url):
    """Prepares the stream to be stored in the DB"""
    stream = force_unicode(stream) if stream else u''
    tree = treebuilders.getTreeBuilder('lxml')
    parser = html5lib.HTMLParser(tree=tree, namespaceHTMLElements=False)
    document_tree = parser.parse(stream)
    script_elements = document_tree.xpath('//script[@src]')
    for script in script_elements:
        src = script.get('src')
        butter_library = get_butter_library(src)
        if butter_library:
            script.set('src', butter_library)
    make_links_absolute(document_tree, base_url)
    return _serialize_stream(document_tree)


def remove_default_values(stream, base_url=None):
    data = json.loads(stream)
    for attr in ['baseDir', 'name', 'savedDataUrl']:
        if attr in data:
            del data[attr]
    return json.dumps(data)


URL_ATTRIBUTES = [
    ('a', 'href'),
    ('applet', 'codebase'),
    ('area', 'href'),
    ('blockquote', 'cite'),
    ('body', 'background'),
    ('del', 'cite'),
    ('form', 'action'),
    ('frame', 'longdesc'),
    ('frame', 'src'),
    ('iframe', 'longdesc'),
    ('iframe', 'src'),
    ('head', 'profile'),
    ('img', 'longdesc'),
    ('img', 'src'),
    ('img', 'usemap'),
    ('input', 'src'),
    ('input', 'usemap'),
    ('ins', 'cite'),
    ('link', 'href'),
    ('object', 'classid'),
    ('object', 'codebase'),
    ('object', 'data'),
    ('object', 'usemap'),
    ('q', 'cite'),
    ('script', 'src'),
    ('video', 'src'),
    ]


def make_links_absolute(document_tree, base_url):
    for tag, attr in URL_ATTRIBUTES:
        xpath = '//%s[@%s]' % (tag, attr)
        element_list = document_tree.xpath(xpath)
        for element in element_list:
            url = get_absolute_url(base_url, element.get(attr))
            element.set(attr, url)
    return document_tree


def get_absolute_url(base_url, path):
    url = urlparse(path)
    if url.netloc:
        return path
    return urljoin(base_url, path)
