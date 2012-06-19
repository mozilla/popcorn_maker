from django import forms

from tower import ugettext_lazy as _


class SearchForm(forms.Form):
    q = forms.CharField(required=False, label=_(u'Search'))
