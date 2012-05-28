from django import forms


class SearchForm(forms.Form):
    q = forms.CharField(min_length=3, max_length=50)
