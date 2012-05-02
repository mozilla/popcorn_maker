import json

from django import forms

class JSONField(forms.CharField):
    """JSON field makes sure the value is dumped by JSON."""

    def clean(self, value):
        try:
            value = json.dumps(value)
        except ValueError:
            raise forms.ValidationError('Invalid JSON value')
        return super(JSONField, self).clean(value)


class ProjectForm(forms.Form):
    """Form used to validate the data sent through the API."""
    name = forms.CharField()
    data = JSONField()
    template = forms.CharField()
