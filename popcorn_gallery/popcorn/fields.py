import json

from django import forms


class PopcornJSONField(forms.CharField):
    """JSON field makes sure the value is dumped by JSON."""

    def clean(self, value):
        try:
            value = json.dumps(value) if value else None
        except TypeError:
            raise forms.ValidationError('Invalid JSON value')
        return super(PopcornJSONField, self).clean(value)
