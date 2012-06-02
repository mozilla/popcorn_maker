from django.contrib import admin

from .models import (Project, Template, TemplateCategory, ProjectCategory,
                     ProjectCategoryMembership)
from ..attachments.admin import AssetInline


class ProjectCategoryMembershipInline(admin.TabularInline):
    readonly_fields = ['created', 'modified']
    model = ProjectCategoryMembership
    extra = 1


class ProjectCategoryAdmin(admin.ModelAdmin):
    inlines = [ProjectCategoryMembershipInline]


class TemplateAdmin(admin.ModelAdmin):
    model = Template
    readonly_fields = ['views_count', 'votes_count']
    inlines = [AssetInline]


admin.site.register(Template, TemplateAdmin)
admin.site.register(ProjectCategory, ProjectCategoryAdmin)
admin.site.register([Project, TemplateCategory])
