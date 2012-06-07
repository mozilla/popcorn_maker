import html5lib

from urlparse import urlparse, urljoin

from django.conf import settings
from django.utils.encoding import force_unicode

from django_extensions.db.fields import json
from html5lib import treebuilders
from html5lib.serializer import htmlserializer

from .constants import POPCORN_JS_ASSETS, BUTTER_ASSETS


def get_popcorn_plugins(template):
    """Determines from a template which popcorn plugins are required"""
    pass


def get_library_path(src, asset_list):
    """Determines if the element linked is a valid ``butter`` library"""
    if not src:
        return None
    # Is it already a valid URL?
    url = urlparse(src)
    if url.netloc:
        return src
    # Is this part of butter?
    for asset in asset_list:
        # Asset is part of butter
        if asset in src:
            return settings.STATIC_URL + asset
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
    update_butter_links(document_tree)
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

def update_butter_links(document_tree):
    script_elements = document_tree.xpath('//script[@src]')
    asset_list = POPCORN_JS_ASSETS + BUTTER_ASSETS
    for script in script_elements:
        src = script.get('src')
        # Determine if the asset is part of Butter or Popcorn
        asset_path = get_library_path(src, asset_list)
        if asset_path:
            script.set('src', asset_path)
    return document_tree

def get_absolute_url(base_url, path):
    url = urlparse(path)
    if url.netloc:
        return path
    return urljoin(base_url, path)


def remove_invalid_links(document_tree, base_url):
    """Removes any link that is not part of the base url or whitelisted domains"""
    pass


def prepare_project_stream(stream, base_url):
    """ Sanitizes a butter HTML export by:
     - Strip any malicious tag and all JS.
     - Allow only internal and whitelisted URLs
    """
    stream = force_unicode(stream) if stream else u''
    tree = treebuilders.getTreeBuilder('lxml')
    parser = html5lib.HTMLParser(tree=tree, namespaceHTMLElements=False)
    document_tree = parser.parse(stream)
    return _serialize_stream(document_tree)
