import html5lib

from urlparse import urlparse, urljoin

from django.conf import settings
from django.utils.encoding import force_unicode

from django_extensions.db.fields import json
from html5lib import treebuilders
from html5lib.serializer import htmlserializer
from lxml.html import builder as E

from .constants import POPCORN_JS_ASSETS, BUTTER_ASSETS, URL_ATTRIBUTES


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


def _get_document_tree(stream):
    stream = force_unicode(stream) if stream else u''
    tree = treebuilders.getTreeBuilder('lxml')
    parser = html5lib.HTMLParser(tree=tree, namespaceHTMLElements=False)
    return parser.parse(stream)


def _absolutify_url(base_url, path):
    url = urlparse(path)
    if url.netloc:
        return path
    return urljoin(base_url, path)


def _remove_scripts(document_tree):
    """Removes any script tag from the tree"""
    script_elements = document_tree.xpath('//script')
    for script in script_elements:
        script.getparent().remove(script)
    return document_tree


def _make_links_absolute(document_tree, base_url):
    for tag, attr in URL_ATTRIBUTES:
        xpath = '//%s[@%s]' % (tag, attr)
        element_list = document_tree.xpath(xpath)
        for element in element_list:
            element.set(attr, _absolutify_url(base_url, element.get(attr)))
    return document_tree


def prepare_popcorn_string_from_project_data(project_data):
    """ Prepares a script tag representing a Popcorn instance
        corresponding to given project data
    """
    popcorn_string = ''
    try:
        media_list = project_data['media']
        for media in media_list:
            track_list = media['tracks']

            popcorn_string += '\n(function(){'
            popcorn_string += '\nvar popcorn = Popcorn.smart( "#' + \
                media['target'] + '", "' + \
                media['url'] + '", {"frameAnimation":true} );'

            for track in track_list:
                track_event_list = track['trackEvents']
                for track_event in track_event_list:
                    popcorn_string += '\npopcorn.' + track_event['type'] + '({'
                    options = track_event['popcornOptions']
                    for prop in options:
                        popcorn_string += '\n\t"' + prop + '": "' + str(options[prop]) + '",'
                    if popcorn_string[-1:] == ',':
                        popcorn_string = popcorn_string[:-1]
                    popcorn_string += '\n});'

            popcorn_string += '\n}());\n'
    except KeyError:
        #TODO something should occur when invalid trackevent data is passed in perhaps
        pass

    return popcorn_string


def _add_popcorn_metadata(document_tree, metadata):
    """Transform the metadata into Popcorn instructions"""
    if not metadata:
        return document_tree
    data = json.loads(metadata)
    popcorn = prepare_popcorn_string_from_project_data(data)
    body = document_tree.xpath('//body')[0]
    script = E.SCRIPT(popcorn, type="text/javascript")
    body.append(script)
    return document_tree


def _add_popcorn_plugins(document_tree, config):
    """Adds the popcorn plugins from the template config"""
    if not config:
        return document_tree
    static_tag = "{{baseDir}}"
    script_text = '<script type="text/javascript" src="%s"></script>'
    fix_url = lambda x: x.replace(' ','').replace(static_tag,
                                                  settings.STATIC_URL)
    head = document_tree.xpath('//head')[0]
    popcorn = E.SCRIPT(src=settings.STATIC_URL+'dist/buttered-popcorn.min.js',
                       type="text/javascript")
    head.append(popcorn)
    for plugin in config['plugin']['plugins']:
        src = fix_url(plugin['path'])
        script_tag = E.SCRIPT(type="text/javascript", src=src)
        head.append(script_tag)
    return document_tree


def prepare_template_stream(stream, base_url):
    """Prepares the stream to be stored in the DB"""
    document_tree = _get_document_tree(stream)
    _make_links_absolute(document_tree, base_url)
    return _serialize_stream(document_tree)


def export_template(template, metadata, base_url):
    """Generates a Project export from the ``Template`` and ``metadata``
    - Gets the skeleton from the template HTML
    - Removes any Butter reference
    - Imports the plugin from the template config file
    - Adds popcorn functionality from the metadata.
    """
    document_tree = _get_document_tree(template.template_content)
    _remove_scripts(document_tree)
    _add_popcorn_plugins(document_tree, template.config)
    _add_popcorn_metadata(document_tree, metadata)
    return _serialize_stream(document_tree)


def _remove_default_values(data):
    for attr in ['baseDir', 'name', 'savedDataUrl']:
        if attr in data:
            del data[attr]
    return data


def prepare_config_stream(stream, base_url):
    """Prepares the config to be stored in the database"""
    data = json.loads(stream)
    data = _remove_default_values(data)
    return json.dumps(data)
