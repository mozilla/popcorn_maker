from django.test import TestCase

from nose.tools import ok_, eq_
from ..templates import (prepare_template_stream, get_absolute_url,
                         remove_default_values)


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
        url = get_absolute_url(self.base, 'relative/path/')
        eq_(url, '/static/relative/path/')

    def test_absolute_url(self):
        url = get_absolute_url(self.base, '/absolute/path/')
        eq_(url, '/absolute/path/')

    def test_domain_url(self):
        url = get_absolute_url(self.base, 'http://mozilla.org/static/')
        eq_(url, 'http://mozilla.org/static/')


class TestGetAbsoluteURLOtherDomain(TestCase):

    base = 'http://base.mozilla.org/static/'

    def test_relative_url(self):
        url = get_absolute_url(self.base, 'relative/path/')
        eq_(url, 'http://base.mozilla.org/static/relative/path/')

    def test_absolute_url(self):
        url = get_absolute_url(self.base, '/absolute/path/')
        eq_(url, 'http://base.mozilla.org/absolute/path/')

    def test_domain_url(self):
        url = get_absolute_url(self.base, 'http://mozilla.org/static/')
        eq_(url, 'http://mozilla.org/static/')


class TestRemoveDefaultValues(TestCase):

    def test_remove_defalut_values(self):
        data = '{"baseDir": "", "name": "", "savedDataUrl": ""}'
        result = remove_default_values(data)
        eq_(result, "{}")
