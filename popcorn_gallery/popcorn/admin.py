from django.contrib import admin
from .models import Project, Template, TemplateCategory, ProjectCategory


admin.site.register([Project, Template, TemplateCategory, ProjectCategory])
