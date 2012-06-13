from django import forms
from django.conf import settings
from django.forms.widgets import CheckboxSelectMultiple
from django.template.defaultfilters import slugify

from tower import ugettext_lazy as _
from .models import Project, Template, ProjectCategory, ProjectCategoryMembership
from .fields import PopcornJSONField


class ProjectForm(forms.Form):
    """Form used to validate the data sent through the API."""
    name = forms.CharField()
    data = PopcornJSONField()
    template = forms.ModelChoiceField(queryset=Template.live.all(),
                                      empty_label=None,
                                      to_field_name='slug')


class ProjectEditForm(forms.ModelForm):
    STATUS_CHOICES = (
        (Project.LIVE, _('Published')),
        (Project.HIDDEN, _('Unpublished')),
        )
    status = forms.ChoiceField(choices=STATUS_CHOICES)

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
        model = Project
        fields = ('name', 'description', 'thumbnail','is_shared', 'is_forkable',
                  'status', 'categories')


class ExternalProjectEditForm(ProjectEditForm):
    class Meta:
        model = Project
        fields = ('name', 'description', 'is_shared', 'status', 'categories')


class ProjectSubmissionForm(forms.ModelForm):
    name = forms.CharField()
    url = forms.URLField()
    thumbnail = forms.ImageField(required=False)

    class Meta:
        model = Project
        fields = ('name', 'description', 'url', 'thumbnail')


class OrderingForm(forms.Form):
    ORDERING_CHOICES = (
        ('default', _('Featured')),
        ('views', _('Most views')),
        ('created', _('Most recent')),
        ('votes', _('Most voted')),
        )
    order = forms.ChoiceField(choices=ORDERING_CHOICES)


class UploadTemplateAdminForm(forms.Form):
    template_zip = forms.FileField()

    def clean_template_zip(self):
        """Validates that the template filename slug doesn't exist"""
        template_zip = self.cleaned_data.get('template_zip')
        if not template_zip:
            return None
        file_bits = template_zip.name.split('.')
        try:
            # make sure filename exists and looks like a zip file
            if len(file_bits) > 1 and file_bits[-1] == 'zip':
                return template_zip
        except IndexError:
            pass
        raise forms.ValidationError('File must be a zip file')
