from django import forms

from tower import ugettext_lazy as _l

from .models import Profile


class ProfileForm(forms.ModelForm):
    name = forms.CharField(error_messages={
        'required': _l(u'A Display Name is required.')
        })

    class Meta:
        model = Profile
        fields = ('name', 'website', 'bio')


class ProfileCreateForm(ProfileForm):
    agreement = forms.BooleanField(required=True, error_messages={
        'required': _l(u'You must agree to the privacy policy to register.')
        })
