from django import forms
from django.core.exceptions import ImproperlyConfigured
from tastypie.validation import Validation


class NonORMFormValidation(Validation):
    """A validation class that uses a Django ``Form`` to validate the data,
    for non-ORM sources."""

    def __init__(self, **kwargs):
        if not 'form_class' in kwargs:
            raise ImproperlyConfigured("You must provide a 'form_class'"
                                       " to 'FormValidation' classes.")
        self.form_class = kwargs.pop('form_class')
        super(NonORMFormValidation, self).__init__(**kwargs)

    def form_kwargs(self, bundle):
        """Returns the ``kwargs`` suitable for a Django ``Form``"""
        return {'data': bundle.data}

    def is_valid(self, bundle, request=None):
        """
        Performs a check on ``bundle.data``to ensure it is valid.

        If the form is valid, an empty list (all valid) will be returned. If
        not, a list of errors will be returned.
        """
        form = self.form_class(**self.form_kwargs(bundle))
        if form.is_valid():
            # We're different here & relying on having a reference to the same
            # bundle the rest of the process is using.
            bundle.data = form.cleaned_data
            return {}
        # The data is invalid. Let's collect all the error messages & return
        # them.
        return form.errors


class AccountAPIForm(forms.Form):
    email = forms.EmailField(max_length=75)
