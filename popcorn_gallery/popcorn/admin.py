from django.contrib import admin
from .models import Project, Template, Category


admin.site.register([Project, Template, Category])
