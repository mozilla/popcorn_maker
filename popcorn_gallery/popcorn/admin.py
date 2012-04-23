from django.contrib import admin
from .models import Project, Template


admin.site.register([Project, Template])
