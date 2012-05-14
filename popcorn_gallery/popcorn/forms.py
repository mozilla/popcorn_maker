import json

from django import forms

from .models import Project, Template


class JSONField(forms.CharField):
    """JSON field makes sure the value is dumped by JSON."""

    def clean(self, value):
        try:
            value = json.dumps(value) if value else None
        except TypeError:
            raise forms.ValidationError('Invalid JSON value')
        return super(JSONField, self).clean(value)


class ProjectForm(forms.Form):
    """Form used to validate the data sent through the API."""
    name = forms.CharField()
    data = JSONField()
    template = forms.ModelChoiceField(queryset=Template.live.all(),
                                      empty_label=None,
                                      to_field_name='slug')


class ProjectEditForm(forms.ModelForm):

    class Meta:
        fields = ('name', 'description', 'is_shared', 'is_forkable', 'status')
        model = Project

