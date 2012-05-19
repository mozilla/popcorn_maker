import re
import bleach
import urlparse

from django import forms
from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder
from django.utils import simplejson as json


def is_valid_url(value):
    """If the ``value`` is a URL makes sure the ``netloc`` is whitelisted"""
    url = urlparse.urlparse(value)
    if url.netloc:
        if url.netloc.lower() in settings.POPCORN_VALID_DOMAINS:
            return value
        raise forms.ValidationError('Domain %s is invalid' % url.netloc)
    return value


def is_valid_string(value):
    """Sanitize the value from any prohibited data"""
    cleaned = bleach.clean(value)
    return cleaned


def validate_value(value):
    """Takes the value and runs it trough the defined validators"""
    if isinstance(value, basestring):
        string_validators = [is_valid_url, is_valid_string]
        for validator in string_validators:
            value = validator(value)
    return value


def validate_metadata(data):
    """Search the dictionary for any non valid key or value.
    We don't care about the structure we care about the values passed in.
    Sanitize every value and key
    """
    if isinstance(data, (list, tuple)):
        new_data = []
        for item in data:
            new_data.append(validate_metadata(item))
    elif isinstance(data, dict):
        new_data = {}
        for key, value in data.items():
            key = validate_value(key)
            new_data[key] = validate_metadata(value)
    else:
        new_data = validate_value(data)
    return new_data


class PopcornJSONField(forms.CharField):
    """JSON field makes sure the value is dumped by JSON."""

    def clean(self, value):
        if value:
            value = validate_metadata(value)
            try:
                value = json.dumps(value, cls=DjangoJSONEncoder)
            except TypeError:
                raise forms.ValidationError('Invalid JSON value')
        return super(PopcornJSONField, self).clean(value)
