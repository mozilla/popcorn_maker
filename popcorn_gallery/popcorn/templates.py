import html5lib

from urlparse import urlparse, urljoin


from django.conf import settings
from django.template.loader import render_to_string
from django.utils.encoding import force_unicode
from django.utils.html import strip_tags

from django_extensions.db.fields import json
from html5lib import treebuilders
from html5lib.serializer import htmlserializer
from lxml.html import tostring

from .constants import POPCORN_JS_ASSETS, BUTTER_ASSETS
from .sanitize import clean


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


def prepare_project_stream(stream, base_url, metadata):
    """ Sanitizes a butter HTML export
     - Picks the plug-in required from the stream.
    """
    stream = force_unicode(stream) if stream else u''
    tree = treebuilders.getTreeBuilder('lxml')
    parser = html5lib.HTMLParser(tree=tree, namespaceHTMLElements=False)
    document_tree = parser.parse(stream)
    # plugins are relative
    scripts = document_tree.xpath('//script[@src]')
    plugins = [s.get('src') for s in scripts if not urlparse(s.get('src')).netloc]
    # styles are relative
    styles = document_tree.xpath('//link[@href]')
    css = [s.get('href') for s in styles if not urlparse(s.get('href')).netloc]
    # inline css
    inline_css = []
    for inline in document_tree.xpath('//style'):
        inline_css.append(strip_tags(inline.text))
        inline.getparent().remove(inline)
    # remove script tags
    for inline in document_tree.xpath('//script'):
        inline.getparent().remove(inline)
    body = [clean(tostring(b)) for b in document_tree.xpath('//body')]
    context = {
        'styles': css,
        'scripts': plugins,
        'inline_css': inline_css,
        'body': body,
        }
    return render_to_string('project/skeleton.html', context)
