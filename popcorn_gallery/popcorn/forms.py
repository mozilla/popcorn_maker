from django import forms
from django.core.exceptions import ImproperlyConfigured
from django.forms.models import model_to_dict
from django.utils import simplejson
from tastypie.validation import Validation


class CustomFormValidation(Validation):
    """
    A validation class that uses a Django ``Form`` to validate the data.

    This class **DOES NOT** alter the data sent, only verifies it. If you
    want to alter the data, please use the ``CleanedDataFormValidation`` class
    instead.

    This class requires a ``form_class`` argument, which should be a Django
    ``Form`` (or ``ModelForm``, though ``save`` will never be called) class.
    This form will be used to validate the data in ``bundle.data``.
    """

    def __init__(self, **kwargs):
        if not 'form_class' in kwargs:
            raise ImproperlyConfigured("You must provide a 'form_class'"
                                       " to 'FormValidation' classes.")

        self.form_class = kwargs.pop('form_class')
        super(CustomFormValidation, self).__init__(**kwargs)

    def form_args(self, bundle):
        data = bundle.data
        # Ensure we get a bound Form, regardless of the state of the bundle.
        if data is None:
            data = {}
        kwargs = {'data': {}}
        if hasattr(bundle.obj, 'pk'):
            kwargs['data'] = model_to_dict(bundle.obj)
        kwargs['data'].update(data)
        return kwargs

    def is_valid(self, bundle, request=None):
        """
        Performs a check on ``bundle.data``to ensure it is valid.

        If the form is valid, an empty list (all valid) will be returned. If
        not, a list of errors will be returned.
        """
        form = self.form_class(**self.form_args(bundle))
        if form.is_valid():
            return {}
        # The data is invalid. Let's collect all the error messages & return
        # them.
        return form.errors


class ProjectAPIForm(forms.Form):
    """Form used to validate the data sent through the API"""
    name = forms.CharField(required=False)
    metadata = forms.CharField(required=False)
    html = forms.CharField(required=False)

    def clean_metadata(self):
        """Make sure the metadata is valid JSON"""
        if not 'metadata' in self.cleaned_data or not self.cleaned_data['metadata']:
            return self.cleaned_data
        try:
            simplejson.loads(self.cleaned_data['metadata'])
        except ValueError, e:
            raise forms.ValidationError('Invalid metadata')
        return self.cleaned_data
