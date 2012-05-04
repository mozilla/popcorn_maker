from django.contrib import admin

from tower import ugettext_lazy as _

from .models import Profile


username = lambda u: u.user.username
username.short_description = _('Username')


class ProfileAdmin(admin.ModelAdmin):
    list_display = (username, 'name')
    search_fields = ('name',)

admin.site.register(Profile, ProfileAdmin)
