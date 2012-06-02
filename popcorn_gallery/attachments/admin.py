from django.contrib import admin

from .models import Asset


class AssetInline(admin.TabularInline):
    model = Asset
