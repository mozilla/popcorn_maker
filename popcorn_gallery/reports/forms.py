import urlparse

from django import forms
from django.conf import settings

from .models import Report


class ReportForm(forms.ModelForm):

    def clean_url(self):
        if 'url' in self.cleaned_data:
            site_url = urlparse.urlparse(settings.SITE_URL)
            parsed = urlparse.urlparse(self.cleaned_data['url'])
            if site_url.netloc == parsed.netloc:
                return self.cleaned_data['url']
        raise forms.ValidationError('This is an invalid URL')

    class Meta:
        model = Report
        fields = ('url', 'description')
