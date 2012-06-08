from django import forms
from django.conf import settings
from django.forms.widgets import CheckboxSelectMultiple
from django.template.defaultfilters import slugify

from tower import ugettext_lazy as _
from .models import Project, Template, ProjectCategory, ProjectCategoryMembership
from .fields import PopcornJSONField
from .templates import prepare_project_stream


class ProjectForm(forms.Form):
    """Form used to validate the data sent through the API."""
    name = forms.CharField()
    data = PopcornJSONField()
    html = forms.CharField()
    template = forms.ModelChoiceField(queryset=Template.live.all(),
                                      empty_label=None,
                                      to_field_name='slug')

    def clean(self):
        template = self.cleaned_data.get('template')
        html = self.cleaned_data.get('html')
        metadata = self.cleaned_data.get('metadata', {})
        if template and html:
            base_url = '%s%s/%s' % (settings.TEMPLATE_MEDIA_URL,
                                    template.author.username, template.slug)
            self.cleaned_data['html'] = prepare_project_stream(html, base_url, metadata)
        return self.cleaned_data


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
        if not self.cleaned_data.get('template_zip'):
            return None
        try:
            filename = self.cleaned_data['template_zip'].name.split('.')[-2]
        except IndexError:
            raise forms.ValidationError('File must be a zip file')
        self.slug = slugify(filename)
        try:
            template = Template.objects.get(slug=self.slug)
        except Template.DoesNotExist:
            return self.cleaned_data['template_zip']
        raise forms.ValidationError('Template with this slug already exists')
