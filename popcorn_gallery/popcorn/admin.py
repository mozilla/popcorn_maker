from django.contrib import admin
from .models import (Project, Template, TemplateCategory, ProjectCategory,
                     ProjectCategoryMembership)


class ProjectCategoryMembershipInline(admin.TabularInline):
    readonly_fields = ['created', 'modified']
    model = ProjectCategoryMembership
    extra = 1


class ProjectCategoryAdmin(admin.ModelAdmin):
    inlines = [ProjectCategoryMembershipInline]


admin.site.register(ProjectCategory, ProjectCategoryAdmin)
admin.site.register([Project, Template, TemplateCategory])
