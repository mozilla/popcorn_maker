from django.contrib import admin

from tower import ugettext_lazy as _

from .models import Profile
from ..popcorn.admin import ProjectCategoryMembershipInline


username = lambda u: u.user.username
username.short_description = _('Username')


class ProfileAdmin(admin.ModelAdmin):
    list_display = (username, 'name')
    search_fields = ('name',)
    inlines = [ProjectCategoryMembershipInline]

admin.site.register(Profile, ProfileAdmin)
