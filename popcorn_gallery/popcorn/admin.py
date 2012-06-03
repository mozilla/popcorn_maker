import zipfile

from django.contrib import admin
from django.conf.urls.defaults import patterns, url
from django.shortcuts import render, redirect

from .forms import UploadTemplateAdminForm
from .models import (Project, Template, TemplateCategory, ProjectCategory,
                     ProjectCategoryMembership)
from .utils import import_zipped_template
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

    def get_urls(self):
        urls = super(TemplateAdmin, self).get_urls()
        custom_urls = patterns(
            '',
            (url('^import/$', self.admin_site.admin_view(self.import_template),
                 name='import_template'))
            )
        return custom_urls + urls

    def import_template(self, request):
        """Imports a Template bundled in a zip file.
         - A template can be bulk uploaded with a zip file, the files must be
           contained in a folder with the template name.
         - The slugified name of the zip file will be used as the name of the
           template.
         - Any other asset will be listed and added to the build.
        """
        if request.method == 'POST':
            form = UploadTemplateAdminForm(request.POST, request.FILES)
            if form.is_valid():
                user_path = '%s/%s/' % (request.user.username, form.slug)
                zipped_template = request.FILES['template_zip']
                try:
                    imported_files = import_zipped_template(zipped_template,
                                                            user_path)
                except zipfile.BadZipfile:
                    self.message_user(request, 'Invalid Zip file')
                if not imported_files:
                    self.message_user(request, 'No files to import')
                template_data = {
                    'name': form.slug,
                    'slug': form.slug,
                    'author': request.user,
                    'status': Template.HIDDEN,
                    }
                template = Template.objects.create(**template_data)
                for imported_file in imported_files:
                    template.asset_set.create(asset=imported_file)
                return redirect('admin:popcorn_template_change', template.pk)
        else:
            form = UploadTemplateAdminForm()
        context = {
            'form': form,
            'app_label': 'popcorn',
            'opts': self.model._meta,
            }
        return render(request, 'admin/template/import.html', context)


admin.site.register(Template, TemplateAdmin)
admin.site.register(ProjectCategory, ProjectCategoryAdmin)
admin.site.register([Project, TemplateCategory])
