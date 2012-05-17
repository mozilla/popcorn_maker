import json

from django import forms
from django.forms.widgets import CheckboxSelectMultiple

from .models import Project, Template, ProjectCategory, ProjectCategoryMembership


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

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super(ProjectEditForm, self).__init__(*args, **kwargs)
        queryset = (ProjectCategory.objects
                    .filter(projectcategorymembership__user=user,
                            projectcategorymembership__status=ProjectCategoryMembership.APPROVED))
        self.has_categories = True if queryset else False
        self.fields.update({
            'categories': forms.ModelMultipleChoiceField(queryset=queryset,
                                                         required=False,
                                                         widget=CheckboxSelectMultiple)
                                                         })

    class Meta:
        fields = ('name', 'description', 'is_shared', 'is_forkable', 'status',
                  'categories')
        model = Project

