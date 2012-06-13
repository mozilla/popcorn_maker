import re

from django import forms
from django.conf import settings
from django.contrib.auth.models import User

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
    username = forms.CharField(max_length=30, error_messages={
        'required': _l(u'A username is required.')
        })
    agreement = forms.BooleanField(required=True, error_messages={
        'required': _l(u'You must agree to the privacy policy to register.')
        })

    class Meta(ProfileForm.Meta):
        fields = ('name', 'username', 'website', 'bio')

    def clean_username(self):
        """Check that the ``username`` hasn't been taken or is invalid"""
        error_message = _l('This username is not available')
        username = self.cleaned_data.get('username')
        if re.match('^[-\w]+$', username) is None:
            raise forms.ValidationError('Make sure you enter an alphanumeric'
                                        ' username')
        if not username:
            return username
        # black list of usernames
        if username in settings.INVALID_USERNAMES:
            raise forms.ValidationError(error_message)
        # user kept his username
        if self.instance.user.username == username:
            return username
        try:
            User.objects.get(username=username)
            raise forms.ValidationError(error_message)
        except User.DoesNotExist:
            pass
        return username
