import random

from django.test import TestCase
from django import forms

from nose.tools import eq_, ok_
from ..forms import PopcornJSONField


VALID_KEYWORDS = ['id', 'name', 'track', 'type', 'popcornOptions', 'end',
                  'src', 'text', 'url', 'duration', 'target', 'valid_key']

VALID_VALUES = [1.2, 'undefined', 'TrackEvent', 'http://mozillapopcorn.org/',
                "http://www.youtube.com/watch?v=cfOa1a8hYP8"]


DICTIONARY = 1
LIST = 2
PLAIN = 3

def get_data_fixtures(depth=3):
    """"Generates a random valid JSON structure, with an specified depth"""
    data = {}
    depth = depth - 1
    for key in random.sample(VALID_KEYWORDS, 4):
        if depth:
            choice = random.choice([DICTIONARY, LIST, PLAIN])
            if choice == DICTIONARY:
                data[key] = get_data_fixtures(depth)
            elif choice == LIST:
                data[key] = [get_data_fixtures(depth) for i in range(3)]
            else:
                data[key] = random.choice(VALID_VALUES)
        else:
            data[key] = random.choice(VALID_VALUES)
    return data


class MockForm(forms.Form):
    data = PopcornJSONField()


class PopcornJSONFieldTests(TestCase):

    def test_empty_json(self):
        form = MockForm({'data': {}})
        self.assertFalse(form.is_valid())

    def test_valid_json(self):
        data = get_data_fixtures()
        form = MockForm({'data': data})
        ok_(form.is_valid())

    def test_invalid_url(self):
        data = get_data_fixtures()
        data['url'] = {'url': 'http://invalid.mozillapopcorn.org'}
        form = MockForm({'data': data})
        self.assertFalse(form.is_valid())

    def test_invalid_schemaless_url(self):
        data = get_data_fixtures()
        data['url'] = {'field': '//invalid.mozillapopcorn.org'}
        form = MockForm({'data': data})
        self.assertFalse(form.is_valid())

    def test_sanitized_body_html(self):
        evil_js = 'an <script>evil()</script> example'
        data = {'html': evil_js}
        form = MockForm({'data': data})
        ok_(form.is_valid())
        self.assertFalse('<script>' in form.cleaned_data['data'])
        eq_(form.cleaned_data['data'],
            '{"html": "an &lt;script&gt;evil()&lt;/script&gt; example"}')

    def test_sanitized_key_html(self):
        evil_js = '<script>alert()</script>'
        data = {evil_js: 'foo'}
        form = MockForm({'data': data})
        ok_(form.is_valid())
        self.assertFalse('<script>' in form.cleaned_data['data'])
        eq_(form.cleaned_data['data'],
            '{"&lt;script&gt;alert()&lt;/script&gt;": "foo"}')
