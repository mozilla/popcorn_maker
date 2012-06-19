from django import forms
from django.forms.models import BaseInlineFormSet
from django.contrib import admin

from .models import Asset


class AssetInlineFormSet(BaseInlineFormSet):
    def clean(self):
        asset_list = []
        for form in self.forms:
            asset_type = form.cleaned_data.get('asset_type')
            if asset_type and asset_type in asset_list:
                name = dict(form.fields['asset_type'].choices)[asset_type]
                raise forms.ValidationError('Only can be one %s' % name)
            if asset_type:
                asset_list.append(asset_type)
        return


class AssetInline(admin.TabularInline):
    formset = AssetInlineFormSet
    model = Asset
