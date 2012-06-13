import re

from django.test import TestCase

from django_extensions.db.fields import json
from nose.tools import ok_, eq_
from .fixtures import (HTML_EXPORT, POPCORN_CONFIG,
                       POPCORN_METADATA)
from ..templates import (prepare_template_stream, _absolutify_url,
                         _remove_default_values, _get_document_tree,
                         _serialize_stream, _remove_scripts,
                         _add_popcorn_plugins, _add_popcorn_metadata,
                         prepare_popcorn_string_from_project_data,
                         _make_links_absolute)


class PrepareTemplateTest(TestCase):

    def test_prepare_template_stream_relative(self):
        stream = '<a href="relative/path/">Relative path</a>'
        result = prepare_template_stream(stream, '/static/')
        ok_('href="/static/relative/path/"' in result)

    def test_prepare_template_stream_absolute(self):
        stream = '<a href="/absolute/path/">Absolute path</a>'
        result = prepare_template_stream(stream, '/static/')
        ok_('href="/absolute/path/"' in result)

    def test_prepare_template_stream_url(self):
        stream = '<a href="http://mozillapopcorn.org/path/">Mozilla Popcorn</a>'
        result = prepare_template_stream(stream, '/static/')
        ok_('href="http://mozillapopcorn.org/path/"' in result)


class TestGetAbsoluteURLSameDomain(TestCase):

    base = '/static/'

    def test_relative_url(self):
        url = _absolutify_url(self.base, 'relative/path/')
        eq_(url, '/static/relative/path/')

    def test_absolute_url(self):
        url = _absolutify_url(self.base, '/absolute/path/')
        eq_(url, '/absolute/path/')

    def test_domain_url(self):
        url = _absolutify_url(self.base, 'http://mozilla.org/static/')
        eq_(url, 'http://mozilla.org/static/')


class TestGetAbsoluteURLOtherDomain(TestCase):

    base = 'http://base.mozilla.org/static/'

    def test_relative_url(self):
        url = _absolutify_url(self.base, 'relative/path/')
        eq_(url, 'http://base.mozilla.org/static/relative/path/')

    def test_absolute_url(self):
        url = _absolutify_url(self.base, '/absolute/path/')
        eq_(url, 'http://base.mozilla.org/absolute/path/')

    def test_domain_url(self):
        url = _absolutify_url(self.base, 'http://mozilla.org/static/')
        eq_(url, 'http://mozilla.org/static/')


class TestRemoveDefaultValues(TestCase):

    def test_remove_default_values(self):
        data = {"baseDir": "", "name": "", "savedDataUrl": ""}
        result = _remove_default_values(data)
        eq_(result, {})


class ExportProjectHTML(TestCase):

    base_url = '/static/'

    def test_remove_scripts_inline(self):
        stream = '<script>alert()</script>'
        document_tree = _get_document_tree(stream)
        eq_(len(document_tree.xpath('//script')), 1)
        _remove_scripts(document_tree)
        eq_(len(document_tree.xpath('//script')), 0)

    def test_remove_scripts(self):
        stream = '<script type="text/javascript" src="javscript.js"></script>'
        document_tree = _get_document_tree(stream)
        eq_(len(document_tree.xpath('//script')), 1)
        _remove_scripts(document_tree)
        eq_(len(document_tree.xpath('//script')), 0)

    def test_add_popcorn_plugins(self):
        config = json.loads(POPCORN_CONFIG)
        document_tree = _get_document_tree('<html><head></head></html>')
        _add_popcorn_plugins(document_tree, config)
        eq_(len(document_tree.xpath('//script[@src]')), 4)

    def test_add_popcorn_metadata(self):
        document_tree = _get_document_tree('<html><body></body></html>')
        _add_popcorn_metadata(document_tree, POPCORN_METADATA)
        eq_(len(document_tree.xpath('//script')), 1)
        result = _serialize_stream(document_tree)
        spaceless_result = re.sub(r'\s', '', result)
        ok_('<script>(function(){varpopcorn=Popcorn(' not in spaceless_result)


    def test_prepare_popcorn_string(self):
        metadata = json.loads(POPCORN_METADATA)
        result = prepare_popcorn_string_from_project_data(metadata)
        spaceless_result = re.sub(r'\s', '', result)
        ok_('(function(){varpopcorn=Popcorn.smart("#' + metadata['media'][0]['target'] + '","' + metadata['media'][0]['url'] + '"' in spaceless_result)


class TestMakeLinksAbsolute(TestCase):

    def test_update_relative_links(self):
        text = '<html><body><script src="relative.js"></body></html>'
        document_tree = _get_document_tree(text)
        _make_links_absolute(document_tree, '/static/username/slug/')
        script = document_tree.xpath('//script')[0]
        eq_(script.get('src'), '/static/username/slug/relative.js')

    def test_update_absolute_links(self):
        text = '<html><body><script src="http://mozillapopcorn.org/relative.js"></body></html>'
        document_tree = _get_document_tree(text)
        _make_links_absolute(document_tree, '/static/username/slug/')
        script = document_tree.xpath('//script')[0]
        eq_(script.get('src'), 'http://mozillapopcorn.org/relative.js')
